import os.path
import cv2
from Katna.image import Image

import cProfile


def main():

    # Extract specific number of key frames from video
    img_module = Image()

    # folder to save extracted images
    output_folder_cropped_image = "selectedcrops"

    if not os.path.isdir(os.path.join(".", output_folder_cropped_image)):
        os.mkdir(os.path.join(".", output_folder_cropped_image))

    # number of images to be returned
    no_of_crops_to_returned = 3

    # crop dimentions
    crop_width = 1100
    crop_height = 600
    crop_aspect_ratio = "4:3"

    # Filters
    filters = ["text"]
    # Image file path
    image_file_path = os.path.join(".", "tests", "data", "bird_img_for_crop.jpg")
    print(f"image_file_path = {image_file_path}")

    # crop_image_with_aspect(
    #     self, file_path, crop_aspect_ratio, num_of_crops, filters=[], down_sample_factor=8
    # )

    crop_list = img_module.crop_image_with_aspect(
        file_path=image_file_path,
        crop_aspect_ratio=crop_aspect_ratio,
        num_of_crops=no_of_crops_to_returned,
        filters=filters,
        down_sample_factor=8
    )
    # im = cv2.imread(image_file_path)
    # print(im.shape)
    # crop_list = img_module.crop_image(
    #     file_path=image_file_path,
    #     crop_width=crop_width,
    #     crop_height=crop_height,
    #     num_of_crops=no_of_crops_to_returned,
    #     filters=filters,
    #     down_sample_factor=8
    # )
    # print(crop_list)
    if len(crop_list) > 0:
        img = cv2.imread(image_file_path)
        for counter, crop in enumerate(crop_list):                        
            img_module.save_crop_to_disk(crop, img, \
                file_path=output_folder_cropped_image,
                file_name="cropped_image_" + str(counter), 
                file_ext=".jpeg",
            )
        # print("Top Crop Corrected", top_crop, top_crop.score)
        
    else:
        print(
            "No Perfect crop found for {0}x{1} with for Image {2}".format(
                        crop_width, crop_height ,image_file_path
            )
        )



main()
