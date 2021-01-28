import os.path
import cv2
from Katna.image import Image

def main():

    # Extract specific number of key frames from video
    img_module = Image()

    # folder to save extracted images
    output_folder_cropped_image = "resizedimages"

    if not os.path.isdir(os.path.join(".", output_folder_cropped_image)):
        os.mkdir(os.path.join(".", output_folder_cropped_image))

    # crop dimentions
    resize_width = 500
    resize_height = 600

    # Image file path
    image_file_path = os.path.join(".", "tests", "data", "bird_img_for_crop.jpg")
    print(f"image_file_path = {image_file_path}")

    resized_image = img_module.resize_image(
        file_path=image_file_path,
        target_width=resize_width,
        target_height=resize_height,
        down_sample_factor=8,
    )
    # cv2.imshow("resizedImage", resized_image)
    # cv2.waitKey(0)

    img_module.save_image_to_disk(
        resized_image,
        file_path=output_folder_cropped_image,
        file_name="resized_image",
        file_ext=".jpeg",
    )

main()
