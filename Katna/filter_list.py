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
    # TODO #2
    def __init__(self):
        self.filters = []
        # Getting the absolute path for the directory in which all the filter modules are kept
        filters_modules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_filters")
        filters_modules_list = os.listdir(filters_modules_path)

        # Iterating over each filter module, importing it and adding it to filters list
        for each_filter in filters_modules_list:

            # Checking if the file is a python file and in format: <filter name>_detector.py
            if each_filter.endswith(".py") and len(each_filter.split("_")) == 2:
                splitted_name = each_filter.split(".")
                
                # Creating the import statement as string and converting it into import command command
                exec(
                    str(
                        "from Katna.image_filters."
                        + splitted_name[0]
                        + " import "
                        + "".join([_.title() for _ in splitted_name[0].split("_")])
                    )
                )

                # Creating a dummy object for the imported filter module class and adding it to the filters list
                dummy_obj = eval(
                    "".join([_.title() for _ in splitted_name[0].split("_")]) + "()"
                )
                self.filters.append(dummy_obj)

    def get_filters(self):
        """ Function to get list of all the builtin filters

            :return: Returns list of filters
            :rtype: python list of filter objects
        """
        return self.filters
