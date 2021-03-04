"""
.. module:: Katna.crop_rect
    :platform: OS X
    :synopsis: This module defines crop spec
"""
import os
import cv2
import numpy as np
import Katna.config as config
import math

class CropRect(object):
    """Data structure class for storing image crop rectangles

    :param object: base class inheritance
    :type object: class:`Object`
    """

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.target_crop_width = None
        self.target_crop_height = None
        self.score = 0.0
        self.debug_image = 0

    def __str__(self):
        """Print crop rectangle

        :param object: base class inheritance
        :type object: class:`Object`
        """
        rep = (
            " x_pos: "
            + str(self.x)
            + " y_pos: "
            + str(self.y)
            + " width: "
            + str(self.w)
            + " height: "
            + str(self.h)
            + " target_crop_width: "
            + str(self.target_crop_width)
            + " target_crop_height: "
            + str(self.target_crop_height)
        )
        return rep

    def get_image_crop(self, input_image):
        """public functions which for given input image and current crop rectangle object returns image cropped to 
        crop rectangle specifications. 

        :param object: base class inheritance
        :type object: class:`Object`
        :param image: input image
        :type image: Opencv Numpy Image
        :return: cropped image according to given spec
        :rtype: Opencv Numpy Image
        """
        crop_img = input_image[self.y : self.y + self.h, self.x : self.x + self.w]
        # In case of image crop by specification to ensure cropped images are always 
        # up to specification resize images to target crop specification before return
        # of cropped image
        if self.target_crop_height is None or self.target_crop_width is None:
            return crop_img
        else:
            resized_crop_img = cv2.resize(crop_img, (self.target_crop_width, self.target_crop_height))
            return resized_crop_img
