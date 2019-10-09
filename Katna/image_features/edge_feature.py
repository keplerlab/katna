"""
.. module:: Katna.image_features.edge_feature
    :platform: OS X
    :synopsis: This module is for for getting Edge feature Map from input image
"""

import os
import cv2
import numpy as np
from Katna.image_features.feature import Feature


class EdgeFeature(Feature):
    """Class for getting edge detector Feature,
    Constructor Parameters:- feature weight \n 
    Internal Parameters:- \n 
    min_val_threshold : min edge threshold \n 
    max_val_threshold : max edge threshold \n 
    ksize: size of Sobel kernel used for finding image gradients
    """

    def __init__(self, weight=0.0):
        super().__init__(weight)
        # min edge threshold value
        self.min_val_threshold = 100

        # Max edge threshold value
        self.min_val_threshold = 200

        # aperture_size/size of Sobel kernel for canny edge detector
        self.ksize = 3

    def get_feature_map(self, image):
        """Public function for getting Feature map image from edges detection

        :param image: input image
        :type image: `numpy array`
        :return: single channel opencv numpy image with feature map from edge detection
        :rtype: numpy array
        """
        return cv2.Canny(image, self.min_val_threshold, self.min_val_threshold, self.ksize)
