import os
import os.path
import cv2
import sys, getopt
from Katna.video import Video
from Katna.writer import DiskWriterKeyFrame
import multiprocessing
import ntpath


class CustomDiskWriter(DiskWriterKeyFrame):
    """

    :param DiskWriterKeyFrame: Writer class to overwrite
    :type DiskWriterKeyFrame: Writer
    """

    def generate_output_filename(self, filepath, keyframe_number):
        """Custom output filename method

        :param filepath: [description]
        :type filepath: [type]
        """
        filename = super().generate_output_filename(filepath, keyframe_number)

        suffix = "keyframe"

        return "_".join([filename, suffix])
        

def main_dir():
    if len(sys.argv) ==1:
        dir_path = os.path.join(".", "tests", "data")
    else:
        dir_path = sys.argv[1]

    vd = Video()

    no_of_frames_to_returned = 12

    diskwriter = DiskWriterKeyFrame(location="selectedframes")

    vd.extract_keyframes_from_videos_dir(
        no_of_frames=no_of_frames_to_returned, dir_path=dir_path,
        writer=diskwriter
    )    


def main():

    # Extract specific number of key frames from video
    # if os.name == 'nt':
    #     multiprocessing.freeze_support()

    if len(sys.argv) ==1:
        video_file_path = os.path.join(".", "tests", "data", "pos_video.mp4")
    else:
        video_file_path = sys.argv[1]
       
    vd = Video()

    # folder to save extracted images
    output_folder_video_image = "selectedframes"
    out_dir_path = os.path.join(".", output_folder_video_image)

    if not os.path.isdir(out_dir_path):
        os.mkdir(out_dir_path)

    # number of images to be returned
    no_of_frames_to_returned = 12
    # VIdeo file path
    #video_file_path = os.path.join(".", "tests", "data", "pos_video.mp4")
    print(f"Input video file path = {video_file_path}")

    imgs = vd.extract_video_keyframes(
        no_of_frames=no_of_frames_to_returned, file_path=video_file_path
    )

    # Save it to disk
    for counter, img in enumerate(imgs):
        vd.save_frame_to_disk(
            img,
            file_path=out_dir_path,
            file_name="test_" + str(counter),
            file_ext=".jpeg",
        )
    print(f"Exracted key frames file path = {out_dir_path}")


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    # main()
    main_dir()
