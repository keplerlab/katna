import os.path
import cv2
from Katna.image import Image
from Katna.writer import ImageCropDiskWriter
import cProfile


def main_dir():
    
    img_module = Image()

    # folder to save extracted images
    output_folder_cropped_image = "selectedcrops"

    # number of images to be returned
    no_of_crops_to_return = 3

    # crop dimensions
    crop_width = 300
    crop_height = 400

    # Filters
    filters = ["text"]

    # Directory containing images to be cropped
    input_dir_path = os.path.join(".", "tests", "data")

    # diskwriter to save crop data
    diskwriter = ImageCropDiskWriter(location=output_folder_cropped_image)

    img_module.crop_image_from_dir(
        dir_path=input_dir_path,
        crop_width=crop_width,
        crop_height=crop_height,
        num_of_crops=no_of_crops_to_return,
        writer=diskwriter,
        filters=filters,
        down_sample_factor=8
    )


def main():

    # Extract specific number of key frames from video
    img_module = Image()

    # folder to save extracted images
    output_folder_cropped_image = "selectedcrops"

    # number of images to be returned
    no_of_crops_to_returned = 3

    # crop dimentions
    crop_width = 1100
    crop_height = 600
    crop_aspect_ratio = "9:16"

    # Filters
    filters = ["text"]
    # Image file path
    image_file_path = os.path.join(".", "tests", "data", "bird_img_for_crop.jpg")
    print(f"image_file_path = {image_file_path}")
    

    # diskwriter to save crop data
    diskwriter = ImageCropDiskWriter(location=output_folder_cropped_image)

    img_module.crop_image_with_aspect(
        file_path=image_file_path,
        crop_aspect_ratio=crop_aspect_ratio,
        num_of_crops=no_of_crops_to_returned,
        filters=filters,
        down_sample_factor=8,
        writer=diskwriter
    )
    
    # img_module.crop_image(
    #     file_path=image_file_path,
    #     crop_width=crop_width,
    #     crop_height=crop_height,
    #     num_of_crops=no_of_crops_to_returned,
    #     writer=diskwriter,
    #     filters=filters,
    #     down_sample_factor=8
    # )

if __name__ == "__main__":
    # main()
    main_dir()
