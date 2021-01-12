"""
.. module:: Katna.image
    :platform: OS X
    :synopsis: This module has functions related to smart cropping
"""
import os
import cv2
import numpy as np
from Katna.decorators import FileDecorators
from Katna.feature_list import FeatureList
from Katna.filter_list import FilterList
from Katna.crop_extractor import CropExtractor
from Katna.crop_selector import CropSelector
import Katna.config as config

from Katna.decorators import DebugDecorators


class UserFiltersEnum:
    """ Enum class for filters
    """

    text = "TextDetector"


class Image(object):
    """Class for all image cropping operations

    :param object: base class inheritance
    :type object: class:`Object`
    """

    def __init__(self, disable_text=True):
        """Constructor for image files
        """
        featureList = FeatureList()
        filterList = FilterList()
        self.user_filters_enum = UserFiltersEnum()
        self.crop_extractor = CropExtractor()
        self.crop_selector = CropSelector()
        self.features = featureList.get_features()
        self.definedFilters = filterList.get_filters()


    def _get_crop_specs(
        self, image_height, image_width, ratio_height, ratio_width, is_height_small=True
    ):
        """Function to create the crop specs for a given aspect ratio

        :param image_height: height of image
        :type image_height: int, required
        :param image_width: width of image
        :type image_width: int, required
        :param ratio_height: aspect ratio height (eg. 3 from 4:3)
        :type ratio_height: int, required
        :param ratio_width: aspect ratio width (eg. 4 from 4:3)
        :type ratio_width: int, required
        :param is_height_small: parameter to check if crop dimension should be reduced wrt height[default=True]
        :type is_height_small: boolean, required
        :return: list of crop height and crop width
        :rtype:list of tuples
        """

        # multiplication factor by which height/width of crop should be decreased to get crop specs 
        multiply_by = 1
        crop_list_tuple = []

        # Calculating the height and width ratio wrt aspect ratio
        hr, wr = image_height / ratio_height, image_width / ratio_width

        #print("hr, wr",hr, wr)
        # Check if height is smaller than the width.If yes, interchange height and width.
        if not is_height_small:
            image_height, image_width = image_width, image_height
            hr, wr = wr, hr
        crop_height, crop_width = image_height, hr * ratio_width


        # Decreasing the height and width for crops while checking it don't get small by 1/(min) of image height/width
        while True:
            if not((crop_height >= (image_height // config.Image.min_image_to_crop_factor)) and (crop_width >= (image_width // config.Image.min_image_to_crop_factor))):
                break

            crop_height, crop_width = (
                                int(crop_height),
                                int((ratio_width / ratio_height) * crop_height),
                            )
            
            crop_list_tuple.append((crop_height, crop_width))

            crop_height /=  multiply_by

            crop_height, crop_width = (
                        int(crop_height),
                        int((ratio_width / ratio_height) * crop_height),
                    )
            
            multiply_by += config.Image.crop_height_reduction_factor_in_each_iteration

        return crop_list_tuple


    # Apply optional Debug mode decorator , If config=DEBUG is true this decorator 
    # will populate internal variables of Image module.debug_images with debug images
    # Which you can see by opencv Imshow to check if every feature is working as expected 
    @DebugDecorators.add_optional_debug_images_for_image_module
    def crop_image_from_cvimage(
        self,
        input_image,
        crop_width,
        crop_height,
        num_of_crops,
        filters=[],
        down_sample_factor=config.Image.down_sample_factor,
    ):
        """smartly crops the imaged based on the specification - width and height

        :param input_image: Input image
        :type input_image: numpy array, required
        :param crop_width: output crop width
        :type crop_width: int
        :param crop_height: output crop heigh
        :type crop_height: int
        :param num_of_crops: number of crops required
        :type num_of_crops: int
        :param filters: filters to be applied for cropping(only returns crops containing english text where the crop rectangle doesn't cut the text)
        :type filters: list (eg. ['text']) 
        :param down_sample_factor: number by which you want to reduce image height & width (use it if image is large or to fasten the process)
        :type down_sample_factor: int [default=8]
        :return: crop list 
        :rtype: list of structure crop_rect 
        """

        self.crop_extractor.down_sample_factor = down_sample_factor
        if (
            input_image.shape[0] + 5 <= crop_height
            or input_image.shape[1] + 5 <= crop_width
        ):
            # print(
            #     "Error: crop width or crop height larger than Image",
            #     "input_image.shape",
            #     input_image.shape,
            #     "crop_width",
            #     crop_width,
            #     "crop_height",
            #     crop_height,
            # )

            return []

        extracted_candidate_crops = self.crop_extractor.extract_candidate_crops(
            input_image, crop_width, crop_height, self.features
        )

        # print(extracted_candidate_crops)
        # text: TextDetector
        # dummy: DummyDetector
        self.filters = []
        for x in filters:
            try:
                self.filters.append(eval("self.user_filters_enum." + x))
            except AttributeError as e:
                print(str(e))
        # self.filters = [eval("user_filters_enum."+x) for x in filters]

        crops_list = self.crop_selector.select_candidate_crops(
            input_image,
            num_of_crops,
            extracted_candidate_crops,
            self.definedFilters,
            self.filters,
        )

        return crops_list

    @FileDecorators.validate_dir_path
    def crop_image_from_dir(
            self,
            dir_path,
            crop_width,
            crop_height,
            num_of_crops,
            filters=[],
            down_sample_factor=config.Image.down_sample_factor,
    ):
        """smartly crops all the images (inside a directory) based on the specification - width and height

        :param dir_path: Input Directory path
        :type dir_path: str, required
        :param crop_width: output crop width
        :type crop_width: int
        :param crop_height: output crop height
        :type crop_height: int
        :param num_of_crops: number of crops required
        :type num_of_crops: int
        :param filters: filters to be applied for cropping(checks if image contains english text and the crop rectangle doesn't cut the text)
        :type filters: list (eg. ['text'])
        :param down_sample_factor: number by which you want to reduce image height & width (use it if image is large or to fasten the process)
        :type down_sample_factor: int [default=8]
        :return: crop dict with key as filepath and crop list for the file
        :rtype: dict
        """

        all_crops = {}
        for path, subdirs, files in os.walk(dir_path):
            for filename in files:
                filepath = os.path.join(path, filename)
                if filename.lower().endswith(".jpeg") or filename.lower().endswith(".png") or \
                        filename.lower().endswith(".jpg"):
                    image_file_path = os.path.join(path, filename)
                    crop_list = self.crop_image(
                        image_file_path,
                        crop_width,
                        crop_height,
                        num_of_crops,
                        filters,
                        down_sample_factor)
                    all_crops[filepath] = crop_list

        return all_crops

    @FileDecorators.validate_file_path
    def crop_image(
        self,
        file_path,
        crop_width,
        crop_height,
        num_of_crops,
        filters=[],
        down_sample_factor=config.Image.down_sample_factor,
    ):
        """smartly crops the imaged based on the specification - width and height

        :param file_path: Input file path
        :type file_path: str, required
        :param crop_width: output crop width
        :type crop_width: int 
        :param crop_height: output crop heigh
        :type crop_height: int 
        :param num_of_crops: number of crops required
        :type num_of_crops: int 
        :param filters: filters to be applied for cropping(checks if image contains english text and the crop rectangle doesn't cut the text)
        :type filters: list (eg. ['text']) 
        :param down_sample_factor: number by which you want to reduce image height & width (use it if image is large or to fasten the process)
        :type down_sample_factor: int [default=8]
        :return: crop list 
        :rtype: list of structure crop_rect 
        """

        imgFile = cv2.imread(file_path)

        crop_list = self.crop_image_from_cvimage(
            input_image=imgFile,
            crop_width=crop_width,
            crop_height=crop_height,
            num_of_crops=num_of_crops,
            filters=filters,
            down_sample_factor=down_sample_factor,
        )
        return crop_list

    @FileDecorators.validate_file_path
    def crop_image_with_aspect(
        self,
        file_path,
        crop_aspect_ratio,
        num_of_crops,
        filters=[],
        down_sample_factor=8,
    ):
        """smartly crops the imaged based on the aspect ratio and returns number of specified crops for each crop spec found in the image with
        the specified aspect ratio

        :param file_path: Input file path
        :type file_path: str, required
        :param crop_aspect_ratio: output crop ratio
        :type crop_aspect_ratio: str (eg. '4:3') 
        :param num_of_crops: number of crops required
        :type num_of_crops: int 
        :param filters: filters to be applied for cropping(checks if image contains english text and the crop rectangle doesn't cut the text)
        :type filters: list (eg. ['text']) 
        :param down_sample_factor: number by which you want to reduce image height & width (use it if image is large or to fasten the process)
        :type down_sample_factor: int [default=8]
        :return: crop list 
        :rtype: list of structure crop_rect 
        """

        imgFile = cv2.imread(file_path)
        image_height, image_width, _ = imgFile.shape
        ratio_width, ratio_height = map(int, crop_aspect_ratio.split(":"))
        hr, wr = image_height / ratio_height, image_width / ratio_width
        crop_list_tuple, crop_list = [], []
        if hr <= wr:
            crop_list_tuple += self._get_crop_specs(
                image_height, image_width, ratio_height, ratio_width, is_height_small=True
            )
        elif wr < hr:
            crop_list_tuple += self._get_crop_specs(
                image_height,
                image_width,
                ratio_height,
                ratio_width,
                is_height_small=False,
            )

        for crop_height, crop_width in crop_list_tuple:
            crop_list += self.crop_image_from_cvimage(
                input_image=imgFile,
                crop_width=crop_width,
                crop_height=crop_height,
                num_of_crops=num_of_crops,
                filters=filters,
                down_sample_factor=down_sample_factor,
            )

        sorted_list = sorted(crop_list, key=lambda x: float(x.score), reverse=True)
        return sorted_list[:num_of_crops]

    @FileDecorators.validate_file_path
    def save_crop_to_disk(self, crop_rect, frame, file_path, file_name, file_ext):
        """saves an in-memory crop on drive.

        :param crop_rect: In-memory crop_rect. 
        :type crop_rect: crop_rect, required
        :param frame: In-memory input image. 
        :type frame: numpy.ndarray, required
        :param file_name: name of the image.
        :type file_name: str, required
        :param file_path: Folder location where files needs to be saved
        :type file_path: str, required
        :param file_ext: File extension indicating the file type for example - '.jpg'
        :type file_ext: str, required
        :return: None
        """
        cropped_img = crop_rect.get_image_crop(frame)
        file_full_path = os.path.join(file_path, file_name + file_ext)
        cv2.imwrite(file_full_path, cropped_img)
