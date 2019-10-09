"""
.. module:: Katna.feature_list
    :platform: OS X
    :synopsis: This module creates list of features for image module
"""

import os
import cv2
import pathlib
import numpy as np


class FeatureList:
    """Adapter class for features
    """

    def __init__(self):
        self.features = []
        for each_feature in os.listdir(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "image_features"
            )
        ):
            if (
                each_feature.endswith(".py")
                and len(each_feature.split("_")) == 2
            ):
                splitted_name = each_feature.split(".")
                exec(
                    str(
                        "from Katna.image_features."
                        + splitted_name[0]
                        + " import "
                        + "".join(
                            [_.title() for _ in splitted_name[0].split("_")]
                        )
                    )
                )
                dummy_obj = eval(
                    "".join([_.title() for _ in splitted_name[0].split("_")])
                    + "()"
                )
                self.features.append(dummy_obj)

    def get_features(self):
        """ Function to get list of all the builtin features

            :return: Returns list of features
            :rtype: python list of features objects
        """
        return self.features
