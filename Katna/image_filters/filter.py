"""
.. module:: Katna.image_filters.filter
    :platform: Cross Platform
    :synopsis: image_Feature.Filter is an Base class for Image Filters\
         to be used for Katna Image crop Selection functionality all image filter \
        inherit from this base class
"""

import os
import cv2
import numpy as np


class Filter:
    """Base Class for Image filters
    """

    def __init__(self, weight):
        self.weight = weight

    def get_weight(self):
        """gets weight of particular filter

        :return: weight of the filter
        :rtype: float
        """
        return self.weight
