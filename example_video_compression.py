import os
import os.path
import cv2
from Katna.video import Video
from icecream import ic

def main():

    vd = Video()

    # folder to save extracted images
    output_folder_video_image = "compressed_folder"
    out_dir_path = os.path.join(".", output_folder_video_image)

    if not os.path.isdir(out_dir_path):
        os.mkdir(out_dir_path)

    # VIdeo file path
    video_file_path = os.path.join(".", "tests", "data", "pos_video.mp4")
    print(f"Input video file path = {video_file_path}")

    ic(video_file_path)
    status = vd.compress_video(
        file_path=video_file_path, dir_path=out_dir_path
    )
    ic(status)

if __name__ == "__main__":
    main()
