"""
.. module:: Katna.video_compressor
    :platform: OS X
    :synopsis: This module has functions related to video compression 
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
import ntpath


class VideoCompressor(object):
    """Class for performing video compression task: based on ffmpeg library for doing video compression"""

    def __init__(self):
        # Find out location of ffmpeg binary on system
        helper._set_ffmpeg_binary_path()

    @FileDecorators.validate_file_path
    def compress_video(
        self,
        file_path,
        force_overwrite,
        crf_parameter,
        output_video_codec,
        out_dir_path,
        out_file_name,
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

        if not helper._check_if_valid_video(file_path):
            raise Exception("Invalid or corrupted video: " + file_path)

        output_full_file_name = self._generate_target_full_file_name(
            file_path, out_dir_path, out_file_name
        )

        if os.path.exists(output_full_file_name) is True and force_overwrite is False:
            exceptionMsg = (
                "Target video name already exist: "
                + output_full_file_name
                + "\nPass on parameter force_overwrite=True in video.compress_video() function to force overwrite"
            )
            raise Exception(exceptionMsg)

        status = self._compress_video_using_ffmpeg(
            file_path, crf_parameter, output_video_codec, output_full_file_name
        )
        return status

    def _generate_target_full_file_name(self, file_path, out_dir_path, out_file_name):
        """Internal function to generate output video file name given input video file_path, out_dir_path and out_file_name

        :param file_path: Input Video file path
        :type file_path: str
        :param out_dir_path: output folder path where you want output video to be saved, defaults to ""
        :type out_dir_path: str
        :param out_file_name: output filename, if not mentioned it will be same as input filename, defaults to ""
        :type out_file_name: str
        :return: Generated output video file path
        :rtype: str
        """
        # If output directory is not mentioned save compressed video in input dir
        if out_dir_path == "":
            out_dir_path = ntpath.dirname(file_path)
        if out_file_name != "":
            targetname = os.path.join(out_dir_path, out_file_name)
        else:
            # if output filename not mentioned make filename same as input file
            name, _ = os.path.splitext(ntpath.basename(file_path))
            targetname = os.path.join(out_dir_path, name)

        # Use mp4 extension for target regardless of input extension
        ext = config.Video.compression_output_file_extension
        target_full_file_name = "{0}.{1}".format(targetname, ext)

        # if target_file_name is same as input file name,
        # save it with extension "_compressed"
        if target_full_file_name == file_path:
            target_full_file_name = "{0}_compressed.{1}".format(targetname, ext)

        return target_full_file_name

    def _compress_video_using_ffmpeg(
        self, filename, crf_parameter, output_video_codec, targetname
    ):
        """Internal function to compress a input file with ffmpeg using given codec
        :param file_path: Input file path
        :type file_path: str
        :param crf_parameter: Constant Rate Factor Parameter for controlling amount of video compression to be applied, The range of the quantizer scale is 0-51: where 0 is lossless, 23 is default, and 51 is worst possible. A lower value is a higher quality, defaults to config.Video.video_compression_crf_parameter
        :type crf_parameter: int
        :param output_video_codec: Type of video codec to choose, Current Options: libx264 and libx265,libx264 is default and is more compatible to wide range of Operating system, libx265 gives better compression at expense of compatibility, defaults to config.Video.video_compression_codec
        :type output_video_codec: str
        :param targetname: path where output compressed video file to be stored
        :type targetname: str
        :return: Status code Returns True if video compression was successfull else False
        :rtype: bool
        """
        ffmpeg_output_parameters = (
            "-vcodec " + output_video_codec + " -crf " + str(crf_parameter)
        )
        # Uses ffmpeg binary for video clipping using ffmpy wrapper
        FFMPEG_BINARY = os.getenv("FFMPEG_BINARY")
        ff = ffmpy.FFmpeg(
            executable=FFMPEG_BINARY,
            inputs={filename: "-y -hide_banner -nostats -loglevel panic"},
            outputs={targetname: ffmpeg_output_parameters},
        )
        try:
            ff.run()
        except ffmpy.FFRuntimeError:
            return False
        return True
