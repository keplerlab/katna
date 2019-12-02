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
        self.debug_image = None

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
        self, input_image, num_of_crops, input_crop_list, defined_filters, filters=[]
    ):
        """Public Function for CropSelector class: takes list of
        crop rectangles and number of required crops as input and returns list
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

        # Has the user applied any filters
        if self.__are_filters_defined(filters) is False:
            filtered_crop_list = self._sort(input_crop_list)
            return self.__topk(filtered_crop_list, num_of_crops)

        # Are user added filters valid
        if self.__are_filters_valid(defined_filters, filters) is False:
            raise TypeError("Added filters do not match predefined filters")

        # Apply the filter to all the crops. This is like scanning the crops with filters
        for defFilter in defined_filters:

            defFilter.set_image(input_image)
            input_crop_list = self.__remove_crops_from_list(defFilter, input_crop_list)

        self.debug_image = input_image

        filtered_crop_list = self._sort(input_crop_list)

        return self.__topk(filtered_crop_list, num_of_crops)

    def __remove_crops_from_list(self, user_filter, input_crop_list):
        """ Private function to remove crops not matching the user added filter.
        
        :param user_filter: filter added by user
        :type user_filter: custom object of type filter

        :param input_crop_list: list of input crop in list of crop_rect format
        :type input_crop_list: python list crop_rect data structure
        
        :return: Returns updated crop list
        :rtype: python list of crop_rect data structure
        """
        # Iterate from last item to first item of python list input_crop_list 
        for i in range(len(input_crop_list) - 1, -1, -1):
            # Remove item from list if filter response is false 
            # please note iterating list from last to first item ensures 
            # you do not remove items are removed in right order
            if user_filter.get_filter_result(input_crop_list[i]) is False:
                input_crop_list.remove(input_crop_list[i])

        return input_crop_list

    def __are_filters_defined(self, filters):
        """Private Function to check if any filters have been added.

        :param filters: User provided filter list. 
        :type defined_filters: list of filter 

        :return: True if filters are added by user
        :rtype: boolean
        """
        # Check filters which are defined actually are present
        if filters != [] or len(filters) > 0:
            return True
        else:
            return False

    def __are_filters_valid(self, defined_filters, filters):
        """Private Function to check if user added filters are valid.

        :param defined_filters: Master List of filters. 
        :type defined_filters: list of filter 
        :param filters: User provided filter list. 
        :type defined_filters: list of filter 

        :return: True if valid filters
        :rtype: boolean
        """

        if defined_filters is not None or len(defined_filters) > 0:
            for defFilter in defined_filters:
                # Check if user asked filters **filters** are in library implemented filters **defFilter**
                if not (type(defFilter).__name__ in filters):
                    return False
        # if reached here then added filters are valid
        return True

    def __topk(self, crops_list, k):
        """Private Function to return top k items from the crops list.

        :param crops_list: crops left after applying all the filters. 
        :type crops_list: list of crops 
        :param K: number of crops to return. 
        :type K: int 

        :return: crops
        :rtype: list of crops
        """
        return crops_list[:k]
