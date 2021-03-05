import os
import os.path
import cv2
from Katna.video import Video
import multiprocessing
import Katna.config as app_config


# change these paths
autoflip_build_path = "/Users/nitkatya/Kepler/mediapipe/autoflip"
autoflip_model_path = "/Users/nitkatya/Kepler/mediapipe/mediapipe/models"

# output aspect ratio
aspect_ratio = "9:16"

# get the current configuration
conf = app_config.MediaPipe.AutoFlip.get_conf()

# set True for features which are required in output
conf["ENFORCE_FEATURES"] = {
    "FACE_CORE_LANDMARKS": False,
    "FACE_ALL_LANDMARKS": False,
    "FACE_FULL": False,
    "HUMAN": False,
    "PET": False,
    "CAR": False,
    "OBJECT": False
}

# % stabalization threshold
conf["STABALIZATION_THRESHOLD"] = 0.5

# opacity of blur area
conf["BLUR_AREA_OPACITY"] = 0.6


def main_folder():
    dir_path = file_path = os.path.join(".", "tests", "data")

    # will create a resize_result dir inside data folder and dump videos there
    abs_dir_path_output = os.path.join(".", "tests", "data", "resize_results")

    vd = Video(autoflip_build_path, autoflip_model_path)

    # update configuration
    app_config.MediaPipe.AutoFlip.set_conf(conf)

    try:
        vd.resize_video_from_dir(dir_path = dir_path, abs_dir_path_output = abs_dir_path_output, aspect_ratio = aspect_ratio)
    except Exception as e:
        raise e
    
    print(f"output resized video dir path = {abs_dir_path_output}")


def main_single_video():

    # resize the pos_video.mp4 in same directory with na,e pos_video_resize.mp4
    abs_file_path_output = os.path.join(".", "tests", "data", "pos_video_resize.mp4")
    file_path = os.path.join(".", "tests", "data", "pos_video.mp4")

    vd = Video(autoflip_build_path, autoflip_model_path)

    # update configuration
    app_config.MediaPipe.AutoFlip.set_conf(conf)
    
    try:
        vd.resize_video(file_path = file_path, abs_file_path_output = abs_file_path_output, aspect_ratio = aspect_ratio)
    except Exception as e:
        raise e
    print(f"output resized video file path = {abs_file_path_output}")


if __name__ == "__main__":
    main_single_video()

    # uncomment this to run on a folder
    # main_folder()
