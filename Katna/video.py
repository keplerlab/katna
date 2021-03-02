"""
.. module:: Katna.video
    :platform: OS X
    :synopsis: This module has functions related to key frame extraction 
"""
import os.path
import os
import sys
import numpy as np
import cv2
import errno
from Katna.decorators import VideoDecorators
from Katna.decorators import FileDecorators

from Katna.frame_extractor import FrameExtractor
from Katna.image_selector import ImageSelector
from Katna.mediapipe import MediaPipeAutoFlip
import Katna.config as config

from multiprocessing import Pool, Process, cpu_count

from moviepy.editor import VideoFileClip

from moviepy.tools import subprocess_call
from moviepy.config import get_setting


class Video(object):
    """Class for all video frames operations

    :param object: base class inheritance
    :type object: class:`Object`
    """

    def __init__(self):
        # If the duration of the clipped video is less than **min_video_duration**
        # then, the clip will be added with the previous clipped
        self.min_video_duration = config.Video.min_video_duration
        # Creating the multiprocessing pool
        self.n_processes = cpu_count() // 2 - 1
        if self.n_processes < 1:
            self.n_processes = None
        self.pool_extractor = Pool(processes=self.n_processes)
        self.pool_selector = Pool(processes=self.n_processes)

        # Folder to save the videos after clipping
        self.temp_folder = os.path.abspath(os.path.join("clipped"))
        if not os.path.isdir(self.temp_folder):
            os.mkdir(self.temp_folder)

    def _remove_clips(self, video_clips):
        """Remove video clips from the temp directory
        """
        for clip in video_clips:
            os.remove(clip)
            # print(clip, " removed!")

    @VideoDecorators.is_mediapipe_installed
    @FileDecorators.validate_file_path
    def resize_video(self, abs_path_to_autoflip_build,
                     file_path,
                     abs_file_path_output,
                     output_aspect_ratio):
        """
        TODO: Call main method inside mediapipe.py for the file
        """
        autoflip = MediaPipeAutoFlip(abs_path_to_autoflip_build)
        autoflip.run(file_path, abs_file_path_output, output_aspect_ratio)


    @VideoDecorators.is_mediapipe_installed
    @FileDecorators.validate_dir_path
    def resize_video_from_dir(self, dir_path):
        """
        TODO: Call main method inside mediapipe.py for all the videos in the directory path
        """
        autoflip = MediaPipeAutoFlip()
        for file_path in dir_path:
            autoflip.run(file_path)
            pass

    @FileDecorators.validate_dir_path
    def extract_frames_as_images_from_dir(self, no_of_frames, dir_path):
        """Returns a dict of best key images/frames from the videos in the directory.

        :param no_of_frames: Number of key frames to be extracted
        :type no_of_frames: int, required
        :param dir_path: Directory location with videos
        :type dir_path: str, required
        :return: Dictionary with key as filepath and numpy.2darray Image objects
        :rtype: dict
        """

        all_videos_top_frames = {}
        for path, subdirs, files in os.walk(dir_path):
            for filename in files:
                filepath = os.path.join(path, filename)
                if filename.lower().endswith(".mp4") or filename.lower().endswith(".mov"):
                    video_file_path = os.path.join(path, filename)
                    video_top_frames = self.extract_frames_as_images(no_of_frames, video_file_path)
                    all_videos_top_frames[filepath] = video_top_frames

        return all_videos_top_frames

    @FileDecorators.validate_file_path
    def extract_frames_as_images(self, no_of_frames, file_path):
        """Returns a list of best key images/frames from the video.
        
        :param no_of_frames: Number of key frames to be extracted
        :type no_of_frames: int, required
        :param file_path: video file location
        :type file_path: str, required
        :return: List of numpy.2darray Image objects
        :rtype: list
        """

        # Split the videos into chunks. Each split(video) will be stored in a temp location
        videos = self._split(file_path)

        frame_extractor = FrameExtractor()

        # Passing all the clipped videos for  the frame extraction using map function of the
        # multiprocessing pool
        extracted_candidate_frames = self.pool_extractor.map(
            frame_extractor.extract_candidate_frames, videos
        )
        # Converting the nested list of extracted frames into 1D list
        extracted_candidate_frames = [
            frame for frames in extracted_candidate_frames for frame in frames
        ]

        self._remove_clips(videos)

        image_selecter = ImageSelector(self.pool_selector)
        top_frames = image_selecter.select_best_frames(
            extracted_candidate_frames, no_of_frames
        )

        return top_frames

    @FileDecorators.validate_file_path
    def save_frame_to_disk(self, frame, file_path, file_name, file_ext):
        """saves an in-memory numpy image array on drive.
        
        :param frame: In-memory image. This would have been generated by extract_frames_as_images method
        :type frame: numpy.ndarray, required
        :param file_name: name of the image.
        :type file_name: str, required
        :param file_path: Folder location where files needs to be saved
        :type file_path: str, required
        :param file_ext: File extension indicating the file type for example - '.jpg'
        :type file_ext: str, required         
        :return: None
        """

        file_full_path = os.path.join(file_path, file_name + file_ext)
        cv2.imwrite(file_full_path, frame)

    @FileDecorators.validate_file_path
    def _split(self, file_path):
        """Function to split the videos and persist the chunks

        :param file_path: path of video file
        :type file_path: str, required
        :return: List of path of splitted video clips
        :rtype: list
        """
        clipped_files = []
        duration = VideoFileClip(file_path, audio=False).duration
        # setting the start point to zero
        # Setting the breaking point for the clip to be 25 or if video is big
        # then relative to core available in the machine
        clip_start, break_point = (
            0,
            duration // cpu_count() if duration // cpu_count() > 15 else 25,
        )

        # Loop over the video duration to get the clip stating point and end point to split the video
        while clip_start < duration:

            clip_end = clip_start + break_point
            
            # Setting the end position of the particular clip equals to the end time of original clip,
            # if end position or end position added with the **min_video_duration** is greater than 
            # the end time of original video
            if clip_end > duration or (clip_end + self.min_video_duration) > duration:
                clip_end = duration

            clipped_files.append(
                self.__write_videofile(file_path, clip_start, clip_end)
            )

            clip_start = clip_end
        return clipped_files

    def __write_videofile(self, video_file_path, start, end):
        """Function to clip the video for given start and end points and save the video

        :param video_file_path: path of video file
        :type video_file_path: str, required
        :param start: start time for clipping
        :type start: float, required
        :param end: end time for clipping
        :type end: float, required
        :return: path of splitted video clip
        :rtype: str
        """

        name = os.path.split(video_file_path)[1]

        # creating a unique name for the clip video 
        # Naming Format: <video name>_<start position>_<end position>.mp4
        _clipped_file_path = os.path.join(
            self.temp_folder,
            "{0}_{1}_{2}.mp4".format(
                name.split(".")[0], int(1000 * start), int(1000 * end)
            ),
        )

        # Calling the ffmpeg to extract the clip with start & end position and
        # save it to the target location(temp dir)
        self._ffmpeg_extract_subclip(
            video_file_path, start, end, targetname=_clipped_file_path
        )
        return _clipped_file_path

    def _ffmpeg_extract_subclip(self, filename, t1, t2, targetname=None):
        """ makes a new video file playing video file ``filename`` between
            the times ``t1`` and ``t2``. 
        :param filename: path of video file
        :type filename: str, required
        :param t1: time from where video to clip
        :type t1: float, required
        :param t2: time to which video to clip
        :type t2: float, required
        :param targetname: path where clipped file to be stored
        :type targetname: str, optional
        :return: None
        """
        name, ext = os.path.splitext(filename)

        if not targetname:
            T1, T2 = [int(1000 * t) for t in [t1, t2]]
            targetname = name + "{0}SUB{1}_{2}.{3}".format(name, T1, T2, ext)

        cmd = [
            get_setting("FFMPEG_BINARY"),
            "-y",
            "-i",
            filename,
            "-ss",
            "%0.2f" % t1,
            "-t",
            "%0.2f" % (t2 - t1),
            "-vcodec",
            "copy",
            "-acodec",
            "copy",
            targetname,
        ]

        subprocess_call(cmd, logger=None, errorprint=True)
