"""
.. module:: Katna.crop_extractor
    :platform: OS X
    :synopsis: This module has functions related to crop extraction
"""

import cv2
import numpy as np
import sys
from Katna.crop_rect import CropRect
import math
import time
import Katna.config as config
from Katna.decorators import DebugDecorators


class CropExtractor(object):
    """Class for extraction and scoring of all possible crops from input image for input crop size.
    Currently features being used for scoring a given crop retangle are: Edge, saliency and face detection.
    Additionally crop scoring also takes following metrics into account: Distance of pixel in crop rectangle from crop boundary
    and rule of third.
    """

    def __init__(self):

        self.detail_weight = config.CropScorer.detail_weight
        self.edge_radius = config.CropScorer.edge_radius
        self.edge_weight = config.CropScorer.edge_weight
        self.outside_importance = config.CropScorer.outside_importance
        self.rule_of_thirds = config.CropScorer.rule_of_thirds
        self.saliency_bias = config.CropScorer.saliency_bias
        self.saliency_weight = config.CropScorer.saliency_weight
        self.down_sample_factor = config.Image.down_sample_factor
        self.face_bias = config.CropScorer.face_bias
        self.face_weight = config.CropScorer.face_weight
        self.rects_weight = config.CropScorer.rects_weight
        self.extracted_feature_maps = []

    def _get_all_possible_crops(
        self,
        image,
        crop_width,
        crop_height,
        max_scale=1,
        min_scale=0.9,
        scale_step=0.1,
        step=8,
    ):
        """Internal function for getting list of all possible Crop_rect for input image.

        :param object: base class inheritance
        :type object: class:`Object`
        :param image: image file
        :type image: OpenCV numpy Image file
        :param crop_width: width
        :type crop_width: int (pixels)
        :param crop_height: height
        :type crop_height: int (pixels)
        :param max_scale: maximum scale factor
        :type max_scale: int, default=1
        :param min_scale: minimum scale factor
        :type min_scale: int, default=0.9
        :param scale_step: scaling step
        :type scale_step: int, default=0.1
        :param step: step
        :type step: int, default=8
        :return: all_possible_crops_rect
        :rtype: list of CropRect
        """
        # This function takes a sliding window approach for getting all possible crop 
        # with given crop specification. 
        image_width, image_height = image.shape[1], image.shape[0]
        # print("Width,height", image_width, image_height)
        # get all possible crops using sliding window

        # Variable to collect all possible crops 
        all_possible_crops_rects = []

        # Start sliding window from from range 0 to max_scale
        for scale in (
            i / 100
            for i in range(
                int(max_scale * 100),
                int((min_scale - scale_step) * 100),
                -int(scale_step * 100),
            )
        ):
            for y in range(0, image_height, step):
                if not (y + crop_height * scale) <= image_height:
                    break
                for x in range(0, image_width, step):
                    if not (x + crop_width * scale) <= image_width:
                        break
                    all_possible_crops_rects.append(
                        CropRect(x, y, crop_width * scale, crop_height * scale)
                    )
        if not all_possible_crops_rects:
            raise ValueError(locals())
        return all_possible_crops_rects

    def _thirds(self, x):
        """Checks rule of third for particular x. Gets value in the range of [0, 1] where 0 is the center of the pictures
        returns weight of rule of thirds [0, 1]

        :param x: parameter x for which Rule of third needs to be checked
        :type x: int
        :return: weight of rule of thirds [0, 1]
        :rtype: int
        """
        # Rule 
        x = ((x + 2 / 3) % 2 * 0.5 - 0.5) * 16
        return np.maximum(1 - x * x, 0)

    def _importance(self, crop_rect, importance_map):
        """Function to Calculate importance_map of crop rectangle according to following criteria, Crop rectangle distance from edge
        and Rule of third

        :param object: base class inheritance
        :type object: class:`Object`
        :param crop: crop window
        :type crop_rect: crop_rect data structure
        :param importance_map: numpy array of size equal to input image and intialized with outside_importance parameter(default=-0.5)
        :type importance_map: numpy array
        :return: modified importance array
        :rtype: numpy array
        """
        # Select image around a grid size of crop width and crop height around 
        # crop center
        y, x = np.ogrid[
            int(crop_rect.y) : int(crop_rect.y + crop_rect.h),
            int(crop_rect.x) : int(crop_rect.x + crop_rect.w),
        ]

        # Subtract values in grid with Crop retangle center value so
        # Values far from center of grid would have hight amplitude
        x, y = (x - crop_rect.x) / crop_rect.w, (y - crop_rect.y) / crop_rect.h

        # Apply abs operation around center of grid 
        px, py = abs(0.5 - x) * 2, abs(0.5 - y) * 2
        px1 = px - 1 + self.edge_radius
        py1 = py - 1 + self.edge_radius
        dx = np.maximum(px1, np.zeros(px1.shape))
        dy = np.maximum(py1, np.zeros(py1.shape))

        # calculating edge distance
        d = (dx * dx + dy * dy) * self.edge_weight
        s = 1.41 - np.sqrt(px * px + py * py)

        # check for rule of thirds
        if self.rule_of_thirds:
            s = (np.maximum(0, s + d + 0.5) * 1.2) * (
                self._thirds(px) + self._thirds(py)
            )
        sdSum = s + d

        # Updating the value of importance matrix using rule of thirds and edge distance
        importance_map[
            int(crop_rect.y) : int(crop_rect.y + crop_rect.h),
            int(crop_rect.x) : int(crop_rect.x + crop_rect.w),
        ] = sdSum
        # should return wxh/hxw
        return importance_map

    def _score(self, feature_maps_image, crop_rect):
        """Internal function to get score for given crop rectangle - it calculates the importance of each pixel inside image
        for given crop_rect and calculates the score by combining all the image features with importance

        :param object: base class inheritance
        :type object: class:`Object`
        :param feature_maps_image: feature_maps image
        :type feature_maps_image: OpenCV image object
        :param crop_rect: Input crop rectangle for which score is calculated
        :type crop_rect: crop_rect
        :return: score
        :rtype: float
        """
        # setting the default scores for each crop rectangle
        rect_score_detail = 0.0
        rect_score_saliency = 0.0
        rect_score_face = 0.0
        rect_score_rects = 0.0
        rect_score_total = 0.0

        feature_maps_data = feature_maps_image
        feature_maps_width, feature_maps_height = (
            feature_maps_image.shape[1],
            feature_maps_image.shape[0],
        )
        # # Skin , Edge , Saliency are at index 0, 1, 2 respectively
        # dummy importance matrix to store base values which will be updated in _importance function
        importance_map = np.zeros((feature_maps_height, feature_maps_width))
        importance_map[:, :] = self.outside_importance
        # importance score matrix wrt rule of thirds and edge radius
        importance = self._importance(crop_rect, importance_map)

        if config.Image.DEBUG is True:
            crop_rect.debug_image = importance.copy()
            importance_max = np.max(crop_rect.debug_image)
            importance_min = np.min(crop_rect.debug_image)
            float_range = importance_max - importance_min
            crop_rect.debug_image = (
                crop_rect.debug_image - importance_min
            ) / float_range
            crop_rect.debug_image = 255 * crop_rect.debug_image
            crop_rect.debug_image = crop_rect.debug_image.astype(np.uint8)

        # print("Debug Image",crop_rect.debug_image)
        detail = np.array(feature_maps_data)[:, :, 2] / 255
        # detailT = detail.T
        rect_score_rects = np.sum(rect_score_rects * importance)
        # Skin score calculations
        a = (np.array(feature_maps_data)[:, :, 1] / 255) * (detail + self.face_bias)
        b = a * importance
        rect_score_face = np.sum(b)
        # edge score calculations
        rect_score_detail = detail * importance
        rect_score_detail = np.sum(rect_score_detail)
        # Saliency score calculations
        rect_score_saliency = np.sum(
            (np.array(feature_maps_data)[:, :, 0] / 255)
            * (detail + self.saliency_bias)
            * importance
        )

        # Scoring mechanism
        rect_score_total = (
            rect_score_detail * self.detail_weight
            + rect_score_face * self.face_weight
            + rect_score_rects * self.rects_weight
            + rect_score_saliency * self.saliency_weight
        ) / (crop_rect.w * crop_rect.h)

        return rect_score_total

    def _extract_and_score_crop_rects(
        self,
        image,
        extracted_feature_maps,
        feature_names,
        crop_width,
        crop_height,
        max_scale=1,
        min_scale=0.9,
        scale_step=0.1,
        step=8,
    ):
        """Internal function to get all crop rects and score each crop retangle given input feature maps for image

            :param object: base class inheritance
            :type object: class:`Object`
            :param image: image file
            :type image: OpenCV numpy Image file
            :param extracted_feature_maps: feature maps
            :type extracted_feature_maps: OpenCV numpy Image file
            :param feature_names: names of features used
            :type feature_names: list
            :param crop_width: width
            :type crop_width: int (pixels)
            :param crop_height: height
            :type crop_height: int (pixels)
            :param max_scale: maximum scale factor
            :type max_scale: int, default=1
            :param min_scale: minimum scale factor
            :type min_scale: int, default=0.9
            :param scale_step: scaling step
            :type scale_step: int, default=0.1
            :param step: step
            :type step: int, default=8
            :return: all_possible_crops_rect
            :rtype: list of CropRect
            """

        all_possible_crops_rects = self._get_all_possible_crops(
            image,
            crop_width,
            crop_height,
            max_scale=max_scale,
            min_scale=min_scale,
            scale_step=scale_step,
            step=step,
        )
        # Storing all feature maps in numpy stack
        feature_maps_image = np.dstack(extracted_feature_maps)
        start = time.time()
        for crop_rect in all_possible_crops_rects:
            crop_rect.score = self._score(feature_maps_image, crop_rect)

        end = time.time()
        # print("Time Spent in scoring Crop rectangles", end - start)
        self.extracted_feature_maps = extracted_feature_maps
        return all_possible_crops_rects

    def extract_candidate_crops(
        self, inputImage, crop_width, crop_height, feature_list
    ):
        """Public Function for crop_extractor module, Given input image and
        desired crop width and height: function returns list of all
        candidate crop rectangles scored taking into account input Image Feature list

        :param object: base class inheritance
        :type object: class:`Object`
        :param inputImage: input Image
        :type inputImage: opencv.Image
        :param crop_width: input crop width
        :type crop_width: Int
        :param crop_height: input crop height
        :type crop_height: Int
        :param feature_list: list of input feature maps to be used for scoring a crop rectangle
        :type feature_list: List of OpenCV numpy image type
        :return: List of extracted crop rectangle objects
        :rtype: list of crop_rect
        """
        extracted_candidate_crops = []
        extracted_feature_maps = []
        feature_names = []
        image = cv2.resize(
            inputImage,
            None,
            fx=1.0 / self.down_sample_factor,
            fy=1.0 / self.down_sample_factor,
        )

        for feature in feature_list:
            feature_names.append(type(feature).__name__)
            feature_map = feature.get_feature_map(image)
            extracted_feature_maps.append(feature_map)

        crop_width_small = int(crop_width / self.down_sample_factor)
        crop_height_small = int(crop_height / self.down_sample_factor)

        extracted_candidate_crops = self._extract_and_score_crop_rects(
            image,
            extracted_feature_maps,
            feature_names,
            crop_width_small,
            crop_height_small,
        )

        for crop_rect in extracted_candidate_crops:
            crop_rect.x = int(crop_rect.x * self.down_sample_factor)
            crop_rect.y = int(crop_rect.y * self.down_sample_factor)
            crop_rect.w = int(crop_rect.w * self.down_sample_factor)
            crop_rect.h = int(crop_rect.h * self.down_sample_factor)

        return extracted_candidate_crops
