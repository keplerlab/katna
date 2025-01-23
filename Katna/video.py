"""
.. module:: Katna.video
    :platform: OS X
    :synopsis: This module has functions related to key frame extraction
"""
import os.path
import os
import psutil
import sys
import math
import numpy as np
import cv2
import errno
import ntpath
from Katna.decorators import VideoDecorators
from Katna.decorators import FileDecorators

from Katna.frame_extractor import FrameExtractor
from Katna.image_selector import ImageSelector
from Katna.mediapipe import MediaPipeAutoFlip
import Katna.config as config
from Katna.video_compressor import VideoCompressor
import Katna.helper_functions as helper

import Katna.config as config
import subprocess
import re
import ffmpy
from imageio_ffmpeg import get_ffmpeg_exe
from multiprocessing import Pool, Process, cpu_count
import functools
import operator

class Video(object):
    """Class for all video frames operations

    :param object: base class inheritance
    :type object: class:`Object`
    """

    def __init__(self, autoflip_build_path=None, autoflip_model_path=None):
        # Find out location of ffmpeg binary on system
        helper._set_ffmpeg_binary_path()
        # If the duration of the clipped video is less than **min_video_duration**
        # then, the clip will be added with the previous clipped
        self._min_video_duration = config.Video.min_video_duration

        # Calculating optimum number of processes for multiprocessing
        self.n_processes = cpu_count() // 2 - 1
        if self.n_processes < 1:
            self.n_processes = None

        if autoflip_build_path is not None and autoflip_model_path is not None:
            self.mediapipe_autoflip = MediaPipeAutoFlip(
                autoflip_build_path, autoflip_model_path
            )
        else:
            self.mediapipe_autoflip = None

        # Folder to save the videos after clipping
        self.temp_folder = os.path.abspath(os.path.join("clipped"))
        if not os.path.isdir(self.temp_folder):
            os.mkdir(self.temp_folder)

    def _remove_clips(self, video_clips):
        """Remove video clips from the temp directory given list of video clips

        :param video_clips: [description]
        :type video_clips: [type]
        """
        for clip in video_clips:
            try:
                os.remove(clip)
            except OSError:
                print("Error in removing clip: " + clip)
            # print(clip, " removed!")

    @FileDecorators.validate_file_path
    def resize_video(self, file_path, abs_file_path_output, aspect_ratio):
        """Resize a single video file

        :param file_path: file path of the video to be resized
        :type file_path: str
        :param abs_file_path_output: absolute path to output video file
        :type abs_file_path_output: str
        :param aspect_ratio: aspect ratio of the final video
        :type aspect_ratio: [type]
        :raises Exception: [description]
        """

        if self.mediapipe_autoflip is not None:
            self.mediapipe_autoflip.prepare_pipeline()
            self.mediapipe_autoflip.run(file_path, abs_file_path_output, aspect_ratio)
            self.mediapipe_autoflip.exit_clean()
        else:
            raise Exception("Mediapipe build path not found.")

    @FileDecorators.validate_dir_path
    def resize_video_from_dir(self, dir_path, abs_dir_path_output, aspect_ratio):
        """Resize all videos inside the directory

        :param dir_path: Directory path where videos are located
        :type dir_path: str
        :param abs_dir_path_output: Absolute path to directory where output videos should to be dumped
        :type abs_dir_path_output: str
        :param aspect_ratio: desirable aspect ratio for the videos
        :type aspect_ratio: [type]
        :raises Exception: [description]
        """
        if self.mediapipe_autoflip is None:
            raise Exception("Mediapipe build path not found.")

        # prepare the mediapipe autoflip pipeline
        self.mediapipe_autoflip.prepare_pipeline()

        # make the output dir if it doesn't exist
        if not os.path.isdir(abs_dir_path_output):
            os.mkdir(abs_dir_path_output)

        list_of_videos_to_process = []
        # Collect all the valid video files inside folder
        for path, _, files in os.walk(dir_path):
            for filename in files:
                video_file_path = os.path.join(path, filename)
                if helper._check_if_valid_video(video_file_path):
                    list_of_videos_to_process.append(video_file_path)

        # autoflip = self.mediapipe_autoflip

        # generates a pool based on cores
        pool = Pool(processes=self.n_processes)
        print("This might take a while ... ")

        try:
            results = pool.starmap(
                self.mediapipe_autoflip.run,
                [
                    (
                        input_file_path,
                        os.path.join(abs_dir_path_output, ntpath.basename(input_file_path)),
                        aspect_ratio,
                    )
                    for input_file_path in list_of_videos_to_process
                ],
            )

            pool.close()
            pool.join()
        except Exception as e:
            self.mediapipe_autoflip.exit_clean()
            raise e

        self.mediapipe_autoflip.exit_clean()

        print("Finished processing for files")

    def _extract_keyframes_from_video(self, no_of_frames, file_path):
        """Core method to extract keyframe for a video

        :param no_of_frames: number of keyframes to extract
        :type no_of_frames: int
        :param file_path: path to video file
        :type file_path: str
        :return: list of keyframes
        :rtype: list
        """
        self.pool_extractor = Pool(processes=self.n_processes)
        
        if not helper._check_if_valid_video(file_path):
            raise Exception("Invalid or corrupted video: " + file_path)

        chunked_videos = self._split(file_path)
        frame_extractor = FrameExtractor()

        extracted_candidate_frames = []
        with self.pool_extractor:
            results = self.pool_extractor.map(frame_extractor.extract_candidate_frames, chunked_videos)
            extracted_candidate_frames.extend(results)

        extracted_candidate_frames = functools.reduce(operator.iconcat, extracted_candidate_frames, [])

        self._remove_clips(chunked_videos)
        image_selector = ImageSelector(self.n_processes)

        top_frames = image_selector.select_best_frames(
            extracted_candidate_frames, no_of_frames
        )

        del extracted_candidate_frames
        return top_frames

    def _extract_keyframes_from_video_with_time(self, no_of_frames, file_path, chunk_timing):
        """Core method to extract keyframe for a video with timestamps

        :param no_of_frames: number of keyframes to extract
        :type no_of_frames: int
        :param file_path: path to video file
        :type file_path: str
        :param chunk_timing: tuple of (start_time, clip_start, clip_end)
        :type chunk_timing: tuple(float, float, float)
        :return: tuple of (list of keyframes, list of timestamps)
        :rtype: tuple(list, list)
        """
        self.pool_extractor = Pool(processes=self.n_processes)
        
        if not helper._check_if_valid_video(file_path):
            raise Exception("Invalid or corrupted video: " + file_path)

        chunked_videos, chunk_info = self._split_with_time(file_path, chunk_timing)
        video_chunks_with_info = list(zip(chunked_videos, chunk_info))

        frame_extractor = FrameExtractor()

        extracted_candidate_frames = []
        extracted_timestamps = []

        with self.pool_extractor:
            results = self.pool_extractor.map(frame_extractor.extract_candidate_frames_with_time, video_chunks_with_info)
            extracted_candidate_frames.extend([result[0] for result in results])
            extracted_timestamps.extend([result[1] for result in results])

        extracted_candidate_frames = functools.reduce(operator.iconcat, extracted_candidate_frames, [])
        extracted_timestamps = functools.reduce(operator.iconcat, extracted_timestamps, [])

        self._remove_clips(chunked_videos)
        image_selector = ImageSelector(self.n_processes)

        top_frames, top_timestamps = image_selector.select_best_frames_with_time(
            extracted_candidate_frames, no_of_frames, extracted_timestamps
        )

        del extracted_candidate_frames
        del extracted_timestamps

        return top_frames, top_timestamps

    def _extract_keyframes_for_files_iterator(self, no_of_frames, list_of_filepaths):
        """Extract desirable number of keyframes for files in the list of filepaths.

        :param no_of_frames: [description]
        :type no_of_frames: [type]
        :param list_of_filepaths: [description]
        :type list_of_filepaths: [type]
        :raises Exception: [description]
        :return: [description]
        :rtype: [type]
        """
        for filepath in list_of_filepaths:
            print("Running for : ", filepath)
            try:
                keyframes = self._extract_keyframes_from_video(no_of_frames, filepath)
                yield {"keyframes": keyframes, "error": None,"filepath": filepath}
            except Exception as e:
                yield {"keyframes": [],"error": e,"filepath": filepath}

    @FileDecorators.validate_dir_path
    def extract_keyframes_from_videos_dir(self, no_of_frames, dir_path, writer):
        """Returns best key images/frames from the videos in the given directory.
        you need to mention number of keyframes as well as directory path
        containing videos. Function returns python dictionary with key as filepath
        each dictionary element contains list of python numpy image objects as
        keyframes.

        :param no_of_frames: Number of key frames to be extracted
        :type no_of_frames: int, required
        :param dir_path: Directory location with videos
        :type dir_path: str, required
        :param writer: Writer class obj to process keyframes
        :type writer: Writer, required
        :return: Dictionary with key as filepath and numpy.2darray Image objects
        :rtype: dict
        """

        valid_files = []

        for path, subdirs, files in os.walk(dir_path):
            for filename in files:
                filepath = os.path.join(path, filename)
                if helper._check_if_valid_video(filepath):
                    valid_files.append(filepath)

        if len(valid_files) > 0:
            generator = self._extract_keyframes_for_files_iterator(no_of_frames, valid_files)

            for data in generator:

                file_path = data["filepath"]
                file_keyframes = data["keyframes"]
                error = data["error"]

                if error is None:
                    writer.write(file_path, file_keyframes)
                    print("Completed processing for : ", file_path)
                else:
                    print("Error processing file : ", file_path)
                    print(error)
        else:
            print("All the files in directory %s are invalid video files" % dir_path)

    def extract_video_keyframes(self, no_of_frames, file_path, writer):
        """Returns a list of best key images/frames from a single video.

        :param no_of_frames: Number of key frames to be extracted
        :type no_of_frames: int, required
        :param file_path: video file location
        :type file_path: str, required
        :param writer: Writer object to process keyframe data
        :type writer: Writer, required
        :return: List of numpy.2darray Image objects
        :rtype: list
        """
        # get the video duration
        video_duration = self._get_video_duration_with_cv(file_path)

        # duration is in seconds
        if video_duration > (config.Video.video_split_threshold_in_minutes * 60):
            print("Large Video (duration = %s min), will split into smaller videos " % round(video_duration / 60))
            top_frames = self.extract_video_keyframes_big_video(no_of_frames, file_path)
        else:
            top_frames = self._extract_keyframes_from_video(no_of_frames, file_path)

        writer.write(file_path, top_frames)
        print("Completed processing for : ", file_path)
        
        return top_frames

    def extract_video_keyframes_with_time(self, no_of_frames, file_path, writer):
        """Returns a list of best key images/frames from a single video with their timestamps.

        :param no_of_frames: Number of key frames to be extracted
        :type no_of_frames: int, required
        :param file_path: video file location
        :type file_path: str, required
        :param writer: Writer object to process keyframe data
        :type writer: Writer, required
        :return: Tuple of (List of numpy.2darray Image objects, List of timestamps)
        :rtype: tuple(list, list)
        """
        # get the video duration
        video_duration = self._get_video_duration_with_cv(file_path)

        # duration is in seconds
        if video_duration > (config.Video.video_split_threshold_in_minutes * 60):
            print("Large Video (duration = %s min), will split into smaller videos " % round(video_duration / 60))
            top_frames, top_timestamps = self.extract_video_keyframes_big_video_with_time(no_of_frames, file_path)
        else:
            top_frames, top_timestamps = self._extract_keyframes_from_video_with_time(no_of_frames, file_path)

        writer.write(file_path, top_frames)
        print("Completed processing for : ", file_path)
        
        return top_frames, top_timestamps

    def extract_video_keyframes_big_video(self, no_of_frames, file_path):
        """Extract keyframes from a large video by splitting it into chunks

        :param no_of_frames: number of frames to extract
        :type no_of_frames: int
        :param file_path: path to video file
        :type file_path: str
        :return: list of keyframes
        :rtype: list
        """
        # split the videos with break point at 20 min
        video_splits = self._split_large_video(file_path)
        print("Video split complete.")

        all_top_frames_split = []

        # call _extract_keyframes_from_video
        for split_video_file_path in video_splits:
            print("Processing split video: ", split_video_file_path)
            top_frames_split = self._extract_keyframes_from_video(no_of_frames, split_video_file_path)
            all_top_frames_split.append(top_frames_split)

        # collect and merge keyframes to get no_of_frames
        self._remove_clips(video_splits)
        image_selector = ImageSelector(self.n_processes)

        # list of list to 1d list
        extracted_candidate_frames = functools.reduce(operator.iconcat, all_top_frames_split, [])

        # top frames
        top_frames = image_selector.select_best_frames(
            extracted_candidate_frames, no_of_frames
        )

        return top_frames
    
    def extract_video_keyframes_big_video_with_time(self, no_of_frames, file_path):
        """Extract keyframes from a large video by splitting it into chunks, with timestamps

        :param no_of_frames: number of frames to extract
        :type no_of_frames: int
        :param file_path: path to video file
        :type file_path: str
        :return: tuple of (list of keyframes, list of timestamps)
        :rtype: tuple(list, list)
        """
        # split the videos with break point at 20 min
        video_splits, chunk_info = self._split_large_video_with_time(file_path)
        print("Video split complete.")

        all_top_frames_split = []
        all_timestamps_split = []

        # call _extract_keyframes_from_video_with_time
        for split_video_file_path, chunk_timing in zip(video_splits, chunk_info):
            top_frames_split, timestamps_split = self._extract_keyframes_from_video_with_time(
                no_of_frames, split_video_file_path, chunk_timing
            )
            all_top_frames_split.append(top_frames_split)
            all_timestamps_split.append(timestamps_split)

        # collect and merge keyframes to get no_of_frames
        self._remove_clips(video_splits)
        image_selector = ImageSelector(self.n_processes)

        # list of list to 1d list
        extracted_candidate_frames = functools.reduce(operator.iconcat, all_top_frames_split, [])
        extracted_timestamps = functools.reduce(operator.iconcat, all_timestamps_split, [])

        # top frames
        top_frames, top_timestamps = image_selector.select_best_frames_with_time(
            extracted_candidate_frames, no_of_frames, extracted_timestamps
        )

        return top_frames, top_timestamps

    @FileDecorators.validate_file_path
    def extract_video_keyframes(self, no_of_frames, file_path, writer):
        """Returns a list of best key images/frames from a single video.

        :param no_of_frames: Number of key frames to be extracted
        :type no_of_frames: int, required
        :param file_path: video file location
        :type file_path: str, required
        :param writer: Writer object to process keyframe data
        :type writer: Writer, required
        :return: List of numpy.2darray Image objects
        :rtype: list
        """

        # get the video duration
        video_duration = self._get_video_duration_with_cv(file_path)

        # duration is in seconds
        if video_duration > (config.Video.video_split_threshold_in_minutes * 60):
            print("Large Video (duration = %s min), will split into smaller videos " % round(video_duration / 60))
            top_frames = self.extract_video_keyframes_big_video(no_of_frames, file_path)
        else:
            top_frames = self._extract_keyframes_from_video(no_of_frames, file_path)

        writer.write(file_path, top_frames)
        print("Completed processing for : ", file_path)
        
        # returning top frames for processing by caller
        return top_frames

    def _split(self, file_path):
        chunked_videos = self._split_with_ffmpeg(file_path)
        corruption_in_chunked_videos = False
        for chunked_video in chunked_videos:
            if not helper._check_if_valid_video(chunked_video):
                corruption_in_chunked_videos = True

        if corruption_in_chunked_videos:
            chunked_videos = self._split_with_ffmpeg(file_path, override_video_codec=True)
            for chunked_video in chunked_videos:
                if not helper._check_if_valid_video(chunked_video):
                    raise Exception(
                        "Error in splitting videos in multiple chunks, corrupted video chunk: "
                        + chunked_video
                    )

        return chunked_videos

    def _split_with_time(self, file_path, chunk_timing):
        chunked_videos, chunk_info = self._split_with_ffmpeg_with_time(file_path, chunk_timing)
        corruption_in_chunked_videos = False
        for chunked_video in chunked_videos:
            if not helper._check_if_valid_video(chunked_video):
                corruption_in_chunked_videos = True

        if corruption_in_chunked_videos:
            chunked_videos, _ = self._split_with_ffmpeg_with_time(file_path, override_video_codec=True, chunk_timing=chunk_timing)
            for chunked_video in chunked_videos:
                if not helper._check_if_valid_video(chunked_video):
                    raise Exception(
                        "Error in splitting videos in multiple chunks, corrupted video chunk: "
                        + chunked_video
                    )

        return chunked_videos, chunk_info

    def _split_large_video(self, file_path):
        break_duration_in_sec = self._calculate_break_duration(file_path)
        video_splits = self._split_with_ffmpeg(file_path, break_point_duration_in_sec=break_duration_in_sec)
        corruption_in_chunked_videos = False
        for chunked_video in video_splits:
            if not helper._check_if_valid_video(chunked_video):
                corruption_in_chunked_videos = True

        if corruption_in_chunked_videos:
            video_splits = self._split_with_ffmpeg(file_path, override_video_codec=True, break_point_duration_in_sec=break_duration_in_sec)
            for chunked_video in video_splits:
                if not helper._check_if_valid_video(chunked_video):
                    raise Exception(
                        "Error in splitting videos in multiple chunks, corrupted video chunk: "
                        + chunked_video
                    )

        return video_splits

    def _split_large_video_with_time(self, file_path):
        break_duration_in_sec = self._calculate_break_duration(file_path)
        video_splits, chunk_info = self._split_with_ffmpeg_with_time(
            file_path, 
            break_point_duration_in_sec=break_duration_in_sec, 
            chunk_timing=("", 0, 0)
        )
        corruption_in_chunked_videos = False
        for chunked_video in video_splits:
            if not helper._check_if_valid_video(chunked_video):
                corruption_in_chunked_videos = True

        if corruption_in_chunked_videos:
            video_splits, chunk_info = self._split_with_ffmpeg_with_time(
                file_path, 
                override_video_codec=True, 
                break_point_duration_in_sec=break_duration_in_sec,
                chunk_timing=("", 0, 0)
            )
            for chunked_video in video_splits:
                if not helper._check_if_valid_video(chunked_video):
                    raise Exception(
                        "Error in splitting videos in multiple chunks, corrupted video chunk: "
                        + chunked_video
                    )

        return video_splits, chunk_info

    def _split_with_ffmpeg(self, file_path, override_video_codec=False, break_point_duration_in_sec=None):
        """Function to split the videos and persist the chunks

        :param file_path: path of video file
        :type file_path: str, required
        :param override_video_codec: If true overrides input video codec to ffmpeg default codec else copy input video codec, defaults to False
        :type override_video_codec: bool, optional
        :param break_point_duration_in_sec: duration in sec for break point
        :type break_point_duration_in_sec: int, optional
        :return: List of video clip paths
        :rtype: list
        """
        clipped_files = []
        duration = self._get_video_duration_with_cv(file_path)
        
        # Calculate break points
        if break_point_duration_in_sec is None:
            clip_start, break_point = (
                0,
                duration // cpu_count() if duration // cpu_count() > 15 else 25,
            )
        else:
            clip_start, break_point = (
                0,
                break_point_duration_in_sec,
            )

        # Loop over the video duration to get the clip stating point and end point to split the video
        while clip_start < duration:
            clip_end = clip_start + break_point

            # Setting the end position of the particular clip equals to the end time of original clip,
            # if end position or end position added with the **min_video_duration** is greater than
            # the end time of original video
            if clip_end > duration or (clip_end + self._min_video_duration) > duration:
                clip_end = duration

            filepath = self._write_videofile(file_path, clip_start, clip_end, override_video_codec)
            clipped_files.append(filepath)
            clip_start = clip_end

        return clipped_files

    def _split_with_ffmpeg_with_time(self, file_path, chunk_timing, override_video_codec=False, break_point_duration_in_sec=None):
        """Function to split the videos and persist the chunks, returning timing information

        :param file_path: path of video file
        :type file_path: str, required
        :param override_video_codec: If true overrides input video codec to ffmpeg default codec else copy input video codec, defaults to False
        :type override_video_codec: bool, optional
        :param break_point_duration_in_sec: duration in sec for break point
        :type break_point_duration_in_sec: int, optional
        :return: Tuple of (list of video paths, list of chunk timing info)
        :rtype: tuple(list, list)
        """
        clipped_files = []
        chunk_info = []  # List to store (filepath, start_time, end_time) tuples
        duration = self._get_video_duration_with_cv(file_path)
        
        # Calculate break points
        if break_point_duration_in_sec is None:
            clip_start, break_point = (
                0,
                duration // cpu_count() if duration // cpu_count() > 15 else 25,
            )
        else:
            clip_start, break_point = (
                0,
                break_point_duration_in_sec,
            )

        # Loop over the video duration to get the clip stating point and end point to split the video
        while clip_start < duration:
            clip_end = clip_start + break_point

            # Setting the end position of the particular clip equals to the end time of original clip,
            # if end position or end position added with the **min_video_duration** is greater than
            # the end time of original video
            if clip_end > duration or (clip_end + self._min_video_duration) > duration:
                clip_end = duration

            filepath = self._write_videofile(file_path, clip_start, clip_end, override_video_codec)
            clipped_files.append(filepath)
            chunk_info.append((filepath, chunk_timing[1] + clip_start, chunk_timing[1] + clip_end))  # Store filepath with start and end times
            clip_start = clip_end

        return clipped_files, chunk_info

    def _write_videofile(self, video_file_path, start, end, override_video_codec=False):
        """Function to clip the video for given start and end points and save the video

        :param video_file_path: path of video file
        :type video_file_path: str, required
        :param start: start time for clipping
        :type start: float, required
        :param end: end time for clipping
        :type end: float, required
        :param override_video_codec: If true overrides input video codec to ffmpeg default codec else copy input video codec, defaults to False
        :type override_video_codec: bool, optional
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

        self._ffmpeg_extract_subclip(
            video_file_path,
            start,
            end,
            targetname=_clipped_file_path,
            override_video_codec=override_video_codec,
        )
        return _clipped_file_path

    def _ffmpeg_extract_subclip(
        self, filename, t1, t2, targetname=None, override_video_codec=False
    ):
        """chops a new video clip from video file ``filename`` between
            the times ``t1`` and ``t2``, Uses ffmpy wrapper on top of ffmpeg
            library
        :param filename: path of video file
        :type filename: str, required
        :param t1: time from where video to clip
        :type t1: float, required
        :param t2: time to which video to clip
        :type t2: float, required
        :param override_video_codec: If true overrides input video codec to ffmpeg default codec else copy input video codec, defaults to False
        :type override_video_codec: bool, optional
        :param targetname: path where clipped file to be stored
        :type targetname: str, optional
        :return: None
        """
        name, ext = os.path.splitext(filename)

        if not targetname:
            T1, T2 = [int(1000 * t) for t in [t1, t2]]
            targetname = name + "{0}SUB{1}_{2}.{3}".format(name, T1, T2, ext)

        #timeParamter = "-ss " + "%0.2f" % t1 + " -t " + "%0.2f" % (t2 - t1)

        ssParameter = "-ss " + "%0.2f" % t1
        timeParamter = " -t " + "%0.2f" % (t2 - t1)
        hideBannerParameter = " -y -hide_banner -loglevel panic  "
        if override_video_codec:
            codecParameter = " -vcodec libx264 -max_muxing_queue_size 9999"
        else:
            codecParameter = " -vcodec copy -avoid_negative_ts 1 -max_muxing_queue_size 9999"

        # Uses ffmpeg binary for video clipping using ffmpy wrapper
        FFMPEG_BINARY = os.getenv("FFMPEG_BINARY")
        ff = ffmpy.FFmpeg(
            executable=FFMPEG_BINARY,
            inputs={filename: ssParameter + hideBannerParameter},
            outputs={targetname: timeParamter + codecParameter},
        )
        # Uncomment next line for watching ffmpeg command line being executed
        # print("ff.cmd", ff.cmd)
        ff.run()

    @FileDecorators.validate_file_path
    def _get_video_duration_with_cv(self, file_path):
        """
        Computes video duration by getting frames count and fps info (using opencv)
        :param file_path:
        :type file_path:
        :return:
        :rtype:
        """
        video_info = helper.get_video_info(file_path)
        video_frame_size = video_info[0]
        video_fps = video_info[1]
        video_frames = video_info[2]
        video_duration = round((video_frames / video_fps), 2)
        return video_duration

    @FileDecorators.validate_file_path
    def _get_video_duration_with_ffmpeg(self, file_path):
        """Get video duration using ffmpeg binary.
        Based on function ffmpeg_parse_infos inside repo
        https://github.com/Zulko/moviepy/moviepy/video/io/ffmpeg_reader.py
        The MIT License (MIT)
        Copyright (c) 2015 Zulko
        Returns a video duration in second

        :param file_path: video file path
        :type file_path: string
        :raises IOError:
        :return: duration of video clip in seconds
        :rtype: float
        """
        FFMPEG_BINARY = os.getenv("FFMPEG_BINARY")
        # Open the file in a pipe, read output
        ff = ffmpy.FFmpeg(
            executable=FFMPEG_BINARY,
            inputs={file_path: ""},
            outputs={None: "-max_muxing_queue_size 9999 -f null -"},
        )
        _, error = ff.run(
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        infos = error.decode("utf8", errors="ignore")
        lines = infos.splitlines()
        if "No such file or directory" in lines[-1]:
            raise IOError(
                (
                    "Error: the file %s could not be found!\n"
                    "Please check that you entered the correct "
                    "path."
                )
                % file_path
            )

        # get duration (in seconds) by parsing ffmpeg file info returned by
        # ffmpeg binary
        video_duration = None
        decode_file = False
        try:
            if decode_file:
                line = [line for line in lines if "time=" in line][-1]
            else:
                line = [line for line in lines if "Duration:" in line][-1]
            match = re.findall("([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])", line)[0]
            video_duration = helper._convert_to_seconds(match)
        except Exception:
            raise IOError(
                f"error: failed to read the duration of file {file_path}.\n"
                f"Here are the file infos returned by ffmpeg:\n\n{infos}"
            )
        return video_duration

    def _calculate_break_duration(self, file_path):
        """Calculate appropriate break duration for video splitting
        
        :param file_path: path of video file
        :type file_path: str, required
        :return: Break duration in seconds
        :rtype: float
        """
        break_duration_in_sec = config.Video.video_split_threshold_in_minutes * 60

        video_info = helper.get_video_info(file_path)
        frame_size_in_bytes = video_info[0]
        fps = video_info[1]

        free_space_in_bytes = psutil.virtual_memory().available
        available_memory = config.Video.memory_consumption_threshold * free_space_in_bytes

        no_of_sec_to_reach_threshold = (available_memory / (fps * frame_size_in_bytes)) * config.Video.assumed_no_of_frames_per_candidate_frame

        if break_duration_in_sec > no_of_sec_to_reach_threshold:
            break_duration_in_sec = math.floor(no_of_sec_to_reach_threshold)

        return break_duration_in_sec

    @FileDecorators.validate_file_path
    def compress_video(
        self,
        file_path,
        force_overwrite=False,
        crf_parameter=config.Video.video_compression_crf_parameter,
        output_video_codec=config.Video.video_compression_codec,
        out_dir_path="",
        out_file_name="",
    ):
        """Function to compress given input file

        :param file_path: Input file path
        :type file_path: str
        :param force_overwrite: optional parameter if True then if there is \
        already a file in output file location function will overwrite it, defaults to False
        :type force_overwrite: bool, optional
        :param crf_parameter: Constant Rate Factor Parameter for controlling \
        amount of video compression to be applied, The range of the quantizer scale is 0-51:\
        where 0 is lossless, 23 is default, and 51 is worst possible.\
        It is recommend to keep this value between 20 to 30 \
        A lower value is a higher quality, you can change default value by changing \
        config.Video.video_compression_crf_parameter
        :type crf_parameter: int, optional
        :param output_video_codec: Type of video codec to choose, \
        Currently supported options are libx264 and libx265, libx264 is default option.\
        libx264 is more widely supported on different operating systems and platforms, \
        libx265 uses more advanced x265 codec and results in better compression and even less \
        output video sizes with same or better quality. Right now libx265 is not as widely compatible \
        on older versions of MacOS and Widows by default. If wider video compatibility is your goal \
        you should use libx264., you can change default value by changing \
        Katna.config.Video.video_compression_codec
        :type output_video_codec: str, optional
        :param out_dir_path: output folder path where you want output video to be saved, defaults to ""
        :type out_dir_path: str, optional
        :param out_file_name: output filename, if not mentioned it will be same as input filename, defaults to ""
        :type out_file_name: str, optional
        :raises Exception: raises FileNotFoundError Exception if input video file not found, also exception is raised in case output video file path already exist and force_overwrite is not set to True.
        :return: Status code Returns True if video compression was successfull else False
        :rtype: bool
        """
        # TODO add docstring for exeception
        # Add details where libx265 will make sense

        if not helper._check_if_valid_video(file_path):
            raise Exception("Invalid or corrupted video: " + file_path)
        # Intialize video compression class
        video_compressor = VideoCompressor()
        # Run video compression
        status = video_compressor.compress_video(
            file_path,
            force_overwrite,
            crf_parameter,
            output_video_codec,
            out_dir_path,
            out_file_name,
        )
        return status

    @FileDecorators.validate_dir_path
    def compress_videos_from_dir(
        self,
        dir_path,
        force_overwrite=False,
        crf_parameter=config.Video.video_compression_crf_parameter,
        output_video_codec=config.Video.video_compression_codec,
        out_dir_path="",
        out_file_name="",
    ):
        """Function to compress input video files in a folder

        :param dir_path: Input folder path
        :type dir_path: str
        :param force_overwrite: optional parameter if True then if there is \
        already a file in output file location function will overwrite it, defaults to False
        :type force_overwrite: bool, optional
        :param crf_parameter: Constant Rate Factor Parameter for controlling \
        amount of video compression to be applied, The range of the quantizer scale is 0-51:\
        where 0 is lossless, 23 is default, and 51 is worst possible.\
        It is recommend to keep this value between 20 to 30 \
        A lower value is a higher quality, you can change default value by changing \
        config.Video.video_compression_crf_parameter
        :type crf_parameter: int, optional
        :param output_video_codec: Type of video codec to choose, \
        Currently supported options are libx264 and libx265, libx264 is default option.\
        libx264 is more widely supported on different operating systems and platforms, \
        libx265 uses more advanced x265 codec and results in better compression and even less \
        output video sizes with same or better quality. Right now libx265 is not as widely compatible \
        on older versions of MacOS and Widows by default. If wider video compatibility is your goal \
        you should use libx264., you can change default value by changing Katna.config.Video.video_compression_codec
        :type output_video_codec: str, optional
        :param out_dir_path: output folder path where you want output video to be saved, defaults to ""
        :type out_dir_path: str, optional
        :raises Exception: raises FileNotFoundError Exception if input video file not found, also exception is raised in case output video file path already exist and force_overwrite is not set to True.
        :return: Status code Returns True if video compression was successfull else False
        :rtype: bool
        """
        status = True
        list_of_videos_to_process = []
        # Collect all the valid video files inside folder
        for path, _, files in os.walk(dir_path):
            for filename in files:
                video_file_path = os.path.join(path, filename)
                if helper._check_if_valid_video(video_file_path):
                    list_of_videos_to_process.append(video_file_path)

        # Need to run in two sepearte loops to prevent recursion
        for video_file_path in list_of_videos_to_process:
            statusI = self.compress_video(
                video_file_path,
                force_overwrite=force_overwrite,
                crf_parameter=crf_parameter,
                output_video_codec=output_video_codec,
                out_dir_path=out_dir_path,
            )
            status = bool(status and statusI)
        return status

    @FileDecorators.validate_file_path
    def save_frame_to_disk(self, frame, file_path, file_name, file_ext):
        """saves an in-memory numpy image array on drive.

        :param frame: In-memory image. This would have been generated by extract_video_keyframes method
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
