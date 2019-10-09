"""
.. module:: Katna.image_features.saliency_feature
    :platform: Cross Platform
    :synopsis: This module is for for getting saliency feature Map from input image
"""

import os
import cv2
import numpy as np
from Katna.image_features.feature import Feature


class SaliencyFeature(Feature):
    """Class for calculating saliency feature map from Input image
    """

    def __init__(self, weight=0.0):
        # Initialize weight for feature in base class
        super().__init__(weight)
        self.saliency = cv2.saliency.StaticSaliencySpectralResidual_create()

    def get_feature_map(self, image):
        """Public function for getting Feature map image from Image saliency detection

        :param image: input image
        :type image: `numpy array`
        :return: single channel opencv numpy image with feature map from saliency detection
        :rtype: numpy array
        """
        _, saliency_map = self.saliency.computeSaliency(image)
        saliency_map = (saliency_map * 255).astype("uint8")

        return saliency_map
