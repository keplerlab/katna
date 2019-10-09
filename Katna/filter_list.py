"""
.. module:: Katna.filterlist
    :platform: OS X
    :synopsis: This module creates list of filters for image module
"""

import os
import cv2
import pathlib
import numpy as np


class FilterList:
    """Adapter class for filters
    """

    def __init__(self):
        self.filters = []
        for each_filter in os.listdir(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "image_filters"
            )
        ):
            if (
                each_filter.endswith(".py")
                and len(each_filter.split("_")) == 2
            ):
                splitted_name = each_filter.split(".")
                exec(
                    str(
                        "from Katna.image_filters."
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
                self.filters.append(dummy_obj)

    def get_filters(self):
        """ Function to get list of all the builtin filters

            :return: Returns list of filters
            :rtype: python list of filter objects
        """
        return self.filters
