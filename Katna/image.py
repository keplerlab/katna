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
    """Enum class for filters"""

    text = "TextDetector"


class Image(object):
    """Class for all image cropping operations

    :param object: base class inheritance
    :type object: class:`Object`
    """

    def __init__(self, disable_text=True):
        """Constructor for image files"""
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
        """Internal function to create the crop specs for a given aspect ratio

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

        # print("hr, wr",hr, wr)
        # Check if height is smaller than the width.If yes, interchange height and width.
        if not is_height_small:
            image_height, image_width = image_width, image_height
            hr, wr = wr, hr
        crop_height, crop_width = image_height, hr * ratio_width

        # Decreasing the height and width for crops while checking it don't get small by 1/(min) of image height/width
        while True:
            if not (
                (crop_height >= (image_height // config.Image.min_image_to_crop_factor))
                and (
                    crop_width >= (image_width // config.Image.min_image_to_crop_factor)
                )
            ):
                break

            crop_height, crop_width = (
                int(crop_height),
                int((ratio_width / ratio_height) * crop_height),
            )

            crop_list_tuple.append((crop_height, crop_width))

            crop_height /= multiply_by

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

    def _extract_crop_for_files_iterator(
        self, 
        list_of_files,
        crop_width,
        crop_height,
        num_of_crops,
        filters,
        down_sample_factor,
    ):
        """Generator which yields crop data / error for filepaths in a list

        :param list_of_files: list of files to process for crop
        :type list_of_files: list, required
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
        :yield: dict containing error (if any), data ,and filepath of image processed
        :rtype: dict
        """

        for filepath in list_of_files:
            print("Running for : ", filepath)
            try:
                crop_list = self._crop_image(
                    filepath,
                    crop_width,
                    crop_height,
                    num_of_crops,
                    filters,
                    down_sample_factor,
                )
                yield {"crops": crop_list, "error": None,"filepath": filepath}
            except Exception as e:
                yield {"crops": crop_list, "error": e,"filepath": filepath}

    @FileDecorators.validate_dir_path
    def crop_image_from_dir(
        self,
        dir_path,
        crop_width,
        crop_height,
        num_of_crops,
        writer,
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
        :param writer: number of crops required
        :type writer: int
        :param filters: filters to be applied for cropping(checks if image contains english text and the crop rectangle doesn't cut the text)
        :type filters: list (eg. ['text'])
        :param down_sample_factor: number by which you want to reduce image height & width (use it if image is large or to fasten the process)
        :type down_sample_factor: int [default=8]
        :return: crop dict with key as filepath and crop list for the file
        :rtype: dict
        """

        valid_files = []
        all_crops = {}
        for path, subdirs, files in os.walk(dir_path):
            for filename in files:
                filepath = os.path.join(path, filename)
                if self._check_if_valid_image(filepath):
                    valid_files.append(filepath)
        
        if len(valid_files) > 0:
            generator = self._extract_crop_for_files_iterator(
                valid_files,
                crop_width,
                crop_height,
                num_of_crops,
                filters,
                down_sample_factor
            )

            for data in generator:
                file_path = data["filepath"]
                file_crops = data["crops"]
                error = data["error"]

                if error is None:
                    writer.write(file_path, file_crops) 
                    print("Completed processing for : ", file_path)
                else:
                    print("Error processing file : ", file_path)
                    print(error)
        else:
            print("All the files in directory %s are invalid video files" % dir_path)

    def _crop_image(
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
    def crop_image(
        self,
        file_path,
        crop_width,
        crop_height,
        num_of_crops,
        writer,
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
        :param writer: writer object to process data
        :type writer: Writer, required
        :param filters: filters to be applied for cropping(checks if image contains english text and the crop rectangle doesn't cut the text)
        :type filters: list (eg. ['text'])
        :param down_sample_factor: number by which you want to reduce image height & width (use it if image is large or to fasten the process)
        :type down_sample_factor: int [default=8]
        :return: crop list
        :rtype: list of structure crop_rect
        """

        crop_list = self._crop_image(
            file_path,
            crop_width,
            crop_height,
            num_of_crops,
            filters=[],
            down_sample_factor=config.Image.down_sample_factor
        )
        writer.write(file_path, crop_list)

    @FileDecorators.validate_file_path
    def crop_image_with_aspect(
        self,
        file_path,
        crop_aspect_ratio,
        num_of_crops,
        writer,
        filters=[],
        down_sample_factor=8
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
        :param writer: writer to process the image
        :type num_of_crops: Writer, required
        :return: crop list
        :rtype: list of structure crop_rect
        """

        imgFile = cv2.imread(file_path)
        image_height, image_width, _ = imgFile.shape
        ratio_width, ratio_height = map(int, crop_aspect_ratio.split(":"))
        crop_list = self._generate_crop_options_given_for_given_aspect_ratio(
            imgFile,
            image_width,
            image_height,
            ratio_width,
            ratio_height,
            num_of_crops=num_of_crops,
            filters=filters,
            down_sample_factor=down_sample_factor,
        )

        sorted_list = sorted(crop_list, key=lambda x: float(x.score), reverse=True)
        crop_list = sorted_list[:num_of_crops]
        writer.write(file_path, crop_list)

    # 
    @FileDecorators.validate_file_path
    def save_crop_to_disk(self, crop_rect, frame, file_path, file_name, file_ext, rescale=False):
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

    @FileDecorators.validate_file_path
    def resize_image(
        self,
        file_path,
        target_width,
        target_height,
        down_sample_factor=config.Image.down_sample_factor,
    ):
        """smartly resizes the image based on the specification - width and height

        :param file_path: Input file path
        :type file_path: str, required
        :param target_width: output image width
        :type target_width: int
        :param target_height: output image height
        :type target_height: int
        :param down_sample_factor: number by which you want to reduce image height & width (use it if image is large or to fasten the process)
        :type down_sample_factor: int [default=8]
        :return: resized image
        :rtype: cv_image
        """
        if not self._check_if_valid_image(file_path):
            print("Error: Invalid Image, check image path: ", file_path)
            return
        imgFile = cv2.imread(file_path)
        input_image_height, input_image_width, _ = imgFile.shape

        target_image_aspect_ratio = target_width / target_height
        input_image_aspect_ratio = input_image_width / input_image_height

        if input_image_aspect_ratio == target_image_aspect_ratio:
            target_image = cv2.resize(imgFile, (target_width, target_height))
            return target_image
        else:
            crop_list = self._generate_crop_options_given_for_given_aspect_ratio(
                imgFile,
                input_image_width,
                input_image_height,
                target_width,
                target_height,
                num_of_crops=1,
                filters=[],
                down_sample_factor=down_sample_factor,
            )
            # From list of crop options sort and get best crop using crop score variables in each
            # crop option
            sorted_list = sorted(crop_list, key=lambda x: float(x.score), reverse=True)
            # Get top crop image
            resized_image = sorted_list[0].get_image_crop(imgFile)
            target_image = cv2.resize(resized_image, (target_width, target_height))
            return target_image

    def _generate_crop_options_given_for_given_aspect_ratio(
        self,
        imgFile,
        input_image_width,
        input_image_height,
        target_width,
        target_height,
        num_of_crops,
        filters,
        down_sample_factor,
    ):
        """ Internal function to which for given aspect ratio (target_width/target_height)
        Generates ,scores and returns list of image crops 

        :param imgFile: Input image
        :type imgFile: opencv image
        :param input_image_width: input image width
        :type input_image_width: int
        :param input_image_height: input image height
        :type input_image_height: int
        :param target_width: target aspect ratio width
        :type target_width: int
        :param target_height: target aspect ratio height
        :type target_height: int
        :param num_of_crops: number of crop needed in the end
        :type num_of_crops: int
        :param filters: filters
        :type filters: list of filters
        :param down_sample_factor: image down sample factor for optimizing processing time
        :type down_sample_factor: int
        :return: list of candidate crop rectangles as per input aspect ratio
        :rtype: list of CropRect
        """
        crop_list_tuple, crop_list = [], []
        # Calculate height ratio and width ratio of input and target image
        height_ratio, width_ratio = (
            input_image_height / target_height,
            input_image_width / target_width,
        )

        # Generate candidate crops, _get_crop_spec function changes it's behavior based
        # on whether height_ratio is greater or smaller than width ratio.
        if height_ratio <= width_ratio:
            crop_list_tuple += self._get_crop_specs(
                input_image_height,
                input_image_width,
                target_height,
                target_width,
                is_height_small=True,
            )
        else:  # elif width_ratio < height_ratio:
            crop_list_tuple += self._get_crop_specs(
                input_image_height,
                input_image_width,
                target_height,
                target_width,
                is_height_small=False,
            )

        # For each of crop_specifications generated by _get_crop_spec() function
        # generate actual crop as well as give score to each of these crop 
        for crop_height, crop_width in crop_list_tuple:
            crop_list += self.crop_image_from_cvimage(
                input_image=imgFile,
                crop_width=crop_width,
                crop_height=crop_height,
                num_of_crops=num_of_crops,
                filters=filters,
                down_sample_factor=down_sample_factor,
            )
        return crop_list

    @FileDecorators.validate_dir_path
    def resize_image_from_dir(
        self,
        dir_path,
        target_width,
        target_height,
        down_sample_factor=config.Image.down_sample_factor,
    ):
        """smartly resizes all the images (inside a directory) based on the specification - width and height

        :param dir_path: Input Directory path
        :type dir_path: str, required
        :param target_width: output width
        :type target_width: int
        :param target_height: output height
        :type target_height: int
        :param down_sample_factor: number by which you want to reduce image height & width (use it if image is large or to fasten the process)
        :type down_sample_factor: int [default=8]
        :return: dict with key as filepath and resized image as in opencv format as value
        :rtype: dict
        """

        all_resized_images = {}
        for path, subdirs, files in os.walk(dir_path):
            for filename in files:
                filepath = os.path.join(path, filename)
                image_file_path = os.path.join(path, filename)
                if self._check_if_valid_image(image_file_path):
                    resized_image = self.resize_image(
                        image_file_path, target_width, target_height, down_sample_factor
                    )
                    all_resized_images[filepath] = resized_image
                else:
                    print("Error: Not a valid image file:", image_file_path)

        return all_resized_images

    @FileDecorators.validate_file_path
    def save_image_to_disk(self, image, file_path, file_name, file_ext):
        """saves an in-memory image obtained from image resize on drive.

        :param image: In-memory input image.
        :type image: numpy.ndarray, required
        :param file_name: name of the image.
        :type file_name: str, required
        :param file_path: Folder location where files needs to be saved
        :type file_path: str, required
        :param file_ext: File extension indicating the file type for example - '.jpg'
        :type file_ext: str, required
        :return: None
        """
        file_full_path = os.path.join(file_path, file_name + file_ext)
        cv2.imwrite(file_full_path, image)

    @FileDecorators.validate_file_path
    def _check_if_valid_image(self, file_path):
        """Function to check if given image file is a valid image compatible with
        opencv

        :param file_path: image filename
        :type file_path: str
        :return: Return True if valid image file else False
        :rtype: bool
        """
        try:
            frame = cv2.imread(file_path)
            # Making sure video frame is not empty
            if frame is not None:
                return True
            else:
                return False
        except cv2.error as e:
            print("cv2.error:", e)
            return False
        except Exception as e:
            print("Exception:", e)
            return False
