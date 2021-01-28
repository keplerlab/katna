import os.path
from Katna.image import Image
import os
import ntpath


def main():

    img_module = Image()

    # folder to save resized images
    output_folder_resized_image = "resizedimages"

    if not os.path.isdir(os.path.join(".", output_folder_resized_image)):
        os.mkdir(os.path.join(".", output_folder_resized_image))

    # resized image dimensions
    resize_width = 500
    resize_height = 600

    # Input folder file path
    input_folder_path = os.path.join(".", "tests", "data")
    print(f"input_folder_path = {input_folder_path}")

    resized_images = img_module.resize_image_from_dir(
        dir_path=input_folder_path,
        target_width=resize_width,
        target_height=resize_height,
        down_sample_factor=8,
    )

    for filepath, resized_image in resized_images.items():
        # name of the image file
        filename = ntpath.basename(filepath)
        name = filename.split(".")[0]
        # folder path where the images will be stored
        img_module.save_image_to_disk(
            resized_image, output_folder_resized_image, name + "_resized" + "_", ".jpeg"
        )


main()
