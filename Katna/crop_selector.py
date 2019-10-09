"""
.. module:: Katna.crop_selecter
    :platform: OS X
    :synopsis: This module has functions related to crop selection
"""

from __future__ import print_function

import os
import cv2
import numpy as np
import Katna.config as config

class CropSelector(object):
    """Class for selection of top n crop rectangles from input list of crop rectangles
    ,It also implements filtering functionality, currently following filtering
    method are implemented: Text Detector filter

    :param object: base class inheritance
    :type object: class:`Object`
    """

    def __init__(self):
        pass

    def _sort(self, filtered_crop_list):
        """ Function to sort the filtered crop list

            :param filtered_crop_list: Required number of crop
            :type filtered_crop_list: list of crop rect objects
            :return: Returns list of filtered crop rect
            :rtype: list of crop rect objects
        """
        # reverse = None (Sorts in Ascending order)
        # key is set to sort using second element of
        # sublist lambda has been used

        # print("\n\nUN SORTED LIST\n\n")
        # for f in filtered_crop_list:
        #    print(f, f.score)
        sorted_list = sorted(
            filtered_crop_list, key=lambda x: float(x.score), reverse=True
        )

        # print("\n\nSORTED LIST\n\n")
        # for f in sorted_list:
        #    print(f, f.score)

        return sorted_list

    def select_candidate_crops(
        self,
        input_image,
        num_of_crops,
        input_crop_list,
        defined_filters,
        filters=[],
    ):
        """Public Function for CropSelector class: takes list of
        crop retangles and number of required crops as input and returns list
        of filtered crop retangles as output. Also takes list of filters to be used for filtering out unwanted crop rectangles 
        as optional input.

        :param object: base class inheritance
        :type object: class:`Object`
        :param input_image: input image
        :type input_image: Opencv Numpy Image
        :param input_crop_list: list of input crop in list of crop_rect format
        :type input_crop_list: python list crop_rect data structure
        :param number_of_crop: Required number of crop
        :type: int

        :return: Returns list of filtered crop_rect
        :rtype: python list of crop_rect data structure
        """

        filtered_crop_list = []
        # print(len(input_key_frames))
        if (defined_filters is not None or len(defined_filters) > 0
            or filters != [] or len(filters) > 0):
            for defFilter in defined_filters:
                if type(defFilter).__name__ in filters:
                    defFilter.set_image(input_image)
                    for i in range(len(input_crop_list) - 1, -1, -1):
                        # print(defFilter.get_filter_result(input_crop_list[i]))
                        if (
                            defFilter.get_filter_result(input_crop_list[i])
                            is False
                        ):
                            #pass
                            input_crop_list.remove(input_crop_list[i])

        filtered_crop_list = self._sort(input_crop_list)

        if config.DEBUG is True:
            return filtered_crop_list[:num_of_crops] + filtered_crop_list[-num_of_crops:], input_image
        else:
            return filtered_crop_list[:num_of_crops]
