import os.path
import cv2
from Katna.video import Video


def main():

    # Extract specific number of key frames from video
    vd = Video()

    # folder to save extracted images
    output_folder_video_image = "selectedframes"

    if not os.path.isdir(os.path.join(".", output_folder_video_image)):
        os.mkdir(os.path.join(".", output_folder_video_image))
    # number of images to be returned
    no_of_frames_to_returned = 12
    # VIdeo file path
    video_file_path = os.path.join(".", "tests", "data", "pos_video.mp4")
    print(f"video_file_path = {video_file_path}")

    imgs = vd.extract_frames_as_images(
        no_of_frames=no_of_frames_to_returned, file_path=video_file_path
    )

    # Save it to disk
    for counter, img in enumerate(imgs):
        vd.save_frame_to_disk(
            img,
            file_path=output_folder_video_image,
            file_name="test_" + str(counter),
            file_ext=".jpeg",
        )


main()
