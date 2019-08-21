"""
.. module:: Katna.image_selecter
    :platform: OS X
    :synopsis: This module has functions related to key frame extraction 
"""

from __future__ import print_function

import os
from glob import glob
import tempfile
import cv2
import numpy as np
from sklearn.cluster import KMeans
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage import img_as_float


class Image_Selector(object):
    """Class for selection of best top N images from input list of images, Currently following selection method are implemented:
    brightness filtering, contrast/entropy filtering, clustering of frames and variance of laplacian for non blurred images 
    selection

    :param object: base class inheritance
    :type object: class:`Object`
    """

    def __init__(self):

        # Setting for optimum Brightness values
        self.min_brightness_value = 10.0
        self.max_brightness_value = 90.0

        # Setting for optimum Contrast/Entropy values
        self.min_entropy_value = 1.0
        self.max_entropy_value = 10.0

    def __get_brighness_score__(self, image):
        """Internal function to compute the brightness of input image , returns brightness score between 0 to 100.0 , 
 
        :param object: base class inheritance
        :type object: class:`Object`
        :param image: input image
        :type image: Opencv Numpy Image   
        :return: result of Brighness measurment 
        :rtype: float value between 0.0 to 100.0    
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        _, _, v = cv2.split(hsv)
        sum = np.sum(v, dtype=np.float32)
        num_of_pixels = v.shape[0] * v.shape[1]
        brightness_score = (sum * 100.0) / (num_of_pixels * 255.0)
        return brightness_score

    def __get_entropy_score__(self, image):
        """Internal function to compute the entropy/contrast of input image , returns entropy score between 0 to 10 , 
 
        :param object: base class inheritance
        :type object: class:`Object`
        :param image: input image
        :type image: Opencv Numpy Image   
        :return: result of Entropy measurment 
        :rtype: float value between 0.0 to 10.0    
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        entr_img = entropy(gray, disk(5))
        all_sum = np.sum(entr_img)
        num_of_pixels = entr_img.shape[0] * entr_img.shape[1]
        entropy_score = (all_sum) / (num_of_pixels)

        return entropy_score

    def __variance_of_laplacian__(self, image):
        """Internal function to compute the laplacian of the image and then return the focus
        measure, which is simply the variance of the laplacian , 
 
        :param object: base class inheritance
        :type object: class:`Object`
        :param image: input image
        :type image: Opencv Numpy Image   
        :return: result of cv2.Laplacian
        :rtype: opencv image of type CV_64F    
        """

        return cv2.Laplacian(image, cv2.CV_64F).var()

    def __filter_optimum_brightness_and_contrast_images__(self, input_img_files):
        """ Internal function for selection of given input images with following parameters :optimum brightness and contrast range ,
        returns array of image files which are in optimum brigtness and contrast/entropy range.
 
        :param object: base class inheritance
        :type object: class:`Object`
        :param files: list of input image files 
        :type files: python list of images
        :return: Returns list of filtered images  
        :rtype: python list of images 
        """

        output_images = []

        for img_file in input_img_files:
            brightness_ok = False
            contrast_ok = False
            brightness_score = self.__get_brighness_score__(img_file)
            entropy_score = self.__get_entropy_score__(img_file)
            if (
                brightness_score > self.min_brightness_value
                and brightness_score < self.max_brightness_value
            ):
                brightness_ok = True
            if (
                entropy_score > self.min_entropy_value
                and entropy_score < self.max_entropy_value
            ):
                contrast_ok = True

            if brightness_ok and contrast_ok:
                output_images.append(img_file)

        return output_images

    def __prepare_cluster_sets__(self, files):
        """ Internal function for clustering input image files, returns array of indexs of each input file
        (which determines which cluster a given file belongs)
 
        :param object: base class inheritance
        :type object: class:`Object`
        :param files: list of input image files 
        :type files: python list of opencv numpy images
        :return: Returns array containing index for each file for cluster belongingness 
        :rtype: np.array   
        """

        all_hists = []
        for img_file in files:
            img = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            hist = hist.reshape((256))
            all_hists.append(hist)

        kmeans = KMeans(n_clusters=self.nb_clusters, random_state=0).fit(all_hists)
        labels = kmeans.labels_

        files_clusters_index_array = []
        for i in np.arange(self.nb_clusters):
            index_array = np.where(labels == i)
            files_clusters_index_array.append(index_array)

        files_clusters_index_array = np.array(files_clusters_index_array)
        return files_clusters_index_array

    def __get_best_images_index_from_each_cluster__(
        self, files, files_clusters_index_array
    ):
        """ Internal function returns index of one best image from each cluster

        :param object: base class inheritance
        :type object: class:`Object`
        :param files: list of input filenames 
        :type files: python list of string
        :param files_clusters_index_array: Input is array containing index for each file for cluster belongingness 
        :type: np.array   
        :return: Returns list of filtered files which are best candidate from each cluster
        :rtype: python list 
        """
        filtered_items = []
        # orb = cv2.ORB_create()
        for i in np.arange(len(files_clusters_index_array)):
            curr_row = files_clusters_index_array[i][0]
            # kp_lengths = []
            variance_laplacians = []

            for j in np.arange(len(curr_row)):
                img_file = files[curr_row[j]]
                img = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
                variance_laplacian = self.__variance_of_laplacian__(img)
                variance_laplacians.append(variance_laplacian)
            selected_frame_of_current_cluster = curr_row[np.argmax(variance_laplacians)]
            filtered_items.append(selected_frame_of_current_cluster)

        return filtered_items

    def select_best_frames(self, input_key_frames, number_of_frames):
        """[summary] Public function for Image selector class: takes list of key-frames images and number of required
        frames as input, returns list of filtered keyframes

        :param object: base class inheritance
        :type object: class:`Object`
        :param input_key_frames: list of input keyframes in list of opencv image format 
        :type input_key_frames: python list opencv images
        :param number_of_frames: Required number of images 
        :type: int   
        :return: Returns list of filtered image files 
        :rtype: python list of images
        """

        self.nb_clusters = number_of_frames

        filtered_images_list = []
        # print(len(input_key_frames))
        input_key_frames = self.__filter_optimum_brightness_and_contrast_images__(
            input_key_frames
        )

        if len(input_key_frames) >= self.nb_clusters:
            files_clusters_index_array = self.__prepare_cluster_sets__(input_key_frames)
            selected_images_index = self.__get_best_images_index_from_each_cluster__(
                input_key_frames, files_clusters_index_array
            )

            for index in selected_images_index:
                img = input_key_frames[index]
                filtered_images_list.append(img)
        else:
            # if number of required files are less than requested key-frames return all the files
            for img in input_key_frames:
                filtered_images_list.append(img)
        return filtered_images_list
