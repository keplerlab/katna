"""
.. module:: Katna.frame_extractor
    :platform: OS X
    :synopsis: This module has functions related to key frame extraction 
"""
import os
import cv2
import operator
import numpy as np
from scipy.signal import argrelextrema

import tempfile
import Katna.config as config

from Katna.decorators import VideoDecorators
from Katna.decorators import FileDecorators
import Katna.helper_functions as helper
import ffmpy
from icecream import ic

class VideoCompressor(object):
    """Class for extraction of key frames from video : based on sum of absolute differences in LUV colorspace from given video 
    """

    def __init__(self):
        # Find out location of ffmpeg binary on system
        helper._set_ffmpeg_binary_path()


    @FileDecorators.validate_file_path
    def compress_video(self, file_path, dir_path):
        """Returns a list of best key images/frames from a single video.

        :param no_of_frames: Number of key frames to be extracted
        :type no_of_frames: int, required
        :param file_path: video file location
        :type file_path: str, required
        :return: List of numpy.2darray Image objects
        :rtype: list
        """

        # Split the input video into chunks. Each split(video) will be stored
        # in a temp 
        if not helper._check_if_valid_video(file_path):
            raise Exception("Invalid or corrupted video: "+ file_path)

        status = self._compress_video_using_ffmpeg(file_path)
        return status


    def _compress_video_using_ffmpeg(self, filename, targetname=None):
        """Internal function to compress a input file with ffmpeg using x265 codec
        :param filename: path of video file
        :type filename: str, required
        :param targetname: path where clipped file to be stored
        :type targetname: str, optional
        :return: None
        """
        name, _ = os.path.splitext(filename)
        # Use mp4 extension for target regardless of input extension
        ext = "mp4"
        #  ffmpeg -i input.mp4 -vcodec libx265 -crf 28 output.mp4
        if not targetname:
            targetname = "{0}_compressed.{1}".format(name, ext)

        ic(targetname)
        # Uses ffmpeg binary for video clipping using ffmpy wrapper
        FFMPEG_BINARY = os.getenv("FFMPEG_BINARY")
        ff = ffmpy.FFmpeg(
            executable=FFMPEG_BINARY,
            inputs={filename: "-y -hide_banner -nostats -loglevel panic"},
            outputs={targetname: "-vcodec libx264 -crf 28"},
        )
        ff.run()
