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
import Katna.config as config
import subprocess
import re
import ffmpy
from imageio_ffmpeg import get_ffmpeg_exe
from multiprocessing import Pool, Process, cpu_count
class Video(object):
    """Class for all video frames operations

    :param object: base class inheritance
    :type object: class:`Object`
    """

    def __init__(self):
        # Find out location of ffmpeg binary on system
        self._set_ffmpeg_binary_path()
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

    @FileDecorators.validate_dir_path
    def extract_keyframes_from_videos_dir(self, no_of_frames, dir_path):
        """Returns best key images/frames from the videos in the given directory.
        you need to mention number of keyframes as well as directory path 
        containing videos. Function returns python dictionary with key as filepath
        each dictionary element contains list of python numpy image objects as 
        keyframes. 

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

                if self._check_if_valid_video(filename):
                    video_file_path = os.path.join(path, filename)
                    video_top_frames = self.extract_video_keyframes(
                        no_of_frames, video_file_path
                    )
                    all_videos_top_frames[filepath] = video_top_frames

        return all_videos_top_frames

    @FileDecorators.validate_file_path
    def _check_if_valid_video(self, file_path):
        """Function to check if given video file is a valid video compatible with
        ffmpeg/opencv

        :param file_path: video filename
        :type file_path: str
        :return: Return True if valid video file else False
        :rtype: bool
        """
        try:
            vid = cv2.VideoCapture(file_path)
            if vid.isOpened():
                # Making sure we can read at least two frames from video
                ret, frame = vid.read()
                ret, frame = vid.read()
                # Making sure video frame is not empty
                if frame is not None:
                    return True
                else:
                    return False
            else:
                return False
        except cv2.error as e:
            print("cv2.error:", e)
            return False
        except Exception as e:
            print("Exception:", e)
            return False

    @FileDecorators.validate_file_path
    def extract_video_keyframes(self, no_of_frames, file_path):
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
        if not self._check_if_valid_video(file_path):
            raise Exception("Invalid or corrupted video: "+ file_path)

        chunked_videos = self._split(file_path)

        frame_extractor = FrameExtractor()

        # Passing all the clipped videos for  the frame extraction using map function of the
        # multiprocessing pool
        extracted_candidate_frames = self.pool_extractor.map(
            frame_extractor.extract_candidate_frames, chunked_videos
        )
        # Converting the nested list of extracted frames into 1D list
        extracted_candidate_frames = [
            frame for frames in extracted_candidate_frames for frame in frames
        ]

        self._remove_clips(chunked_videos)

        image_selector = ImageSelector(self.pool_selector)
        top_frames = image_selector.select_best_frames(
            extracted_candidate_frames, no_of_frames
        )

        return top_frames

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

    @FileDecorators.validate_file_path
    def _split(self, file_path):
        """Function to split the videos and persist the chunks

        :param file_path: path of video file
        :type file_path: str, required
        :return: List of path of splitted video clips
        :rtype: list
        """
        clipped_files = []
        duration = self._get_video_duration_with_ffmpeg(file_path)
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
                self._write_videofile(file_path, clip_start, clip_end)
            )

            clip_start = clip_end
        return clipped_files

    def _write_videofile(self, video_file_path, start, end):
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

        self._ffmpeg_extract_subclip(
            video_file_path, start, end, targetname=_clipped_file_path
        )
        return _clipped_file_path

    def _ffmpeg_extract_subclip(self, filename, t1, t2, targetname=None):
        """chops a new video clip from video file ``filename`` between
            the times ``t1`` and ``t2``, Uses ffmpy wrapper on top of ffmpeg
            library
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

        timeParamter = "-ss " + "%0.2f" % t1 + " -t " + "%0.2f" % (t2 - t1)

        # Uses ffmpeg binary for video clipping using ffmpy wrapper
        FFMPEG_BINARY = os.getenv("FFMPEG_BINARY")
        ff = ffmpy.FFmpeg(
            executable=FFMPEG_BINARY,
            inputs={filename: "-y -hide_banner -loglevel panic "},
            outputs={targetname: timeParamter + " -vcodec copy -acodec copy"},
        )
        ff.run()


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
        ff = ffmpy.FFmpeg(executable=FFMPEG_BINARY, inputs={file_path: ""}, outputs={None: "-f null -"})
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
            video_duration = self._convert_to_seconds(match)
        except Exception:
            raise IOError(
                f"error: failed to read the duration of file {file_path}.\n"
                f"Here are the file infos returned by ffmpeg:\n\n{infos}"
            )
        return video_duration

    def _convert_to_seconds(self, time):
        """ Will convert any time into seconds.
        If the type of `time` is not valid,
        it's returned as is.
        Here are the accepted formats::
        >>> convert_to_seconds(15.4)   # seconds
        15.4
        >>> convert_to_seconds((1, 21.5))   # (min,sec)
        81.5
        >>> convert_to_seconds((1, 1, 2))   # (hr, min, sec)
        3662
        >>> convert_to_seconds('01:01:33.045')
        3693.045
        >>> convert_to_seconds('01:01:33,5')    # coma works too
        3693.5
        >>> convert_to_seconds('1:33,5')    # only minutes and secs
        99.5
        >>> convert_to_seconds('33.5')      # only secs
        33.5

        :param time: time_string
        :type time: string
        :return: time in seconds
        :rtype: float
        """        

        factors = (1, 60, 3600)

        if isinstance(time, str):
            time = [float(part.replace(",", ".")) for part in time.split(":")]

        if not isinstance(time, (tuple, list)):
            return time

        return sum(mult * part for mult, part in zip(factors, reversed(time)))

    def _set_ffmpeg_binary_path(self):
        """ Function for getting path to ffmpeg binary on your system to be
        used by ffmpy
        # Derived from ffmpeg detection code borrowed from moviepy 
        # https://github.com/Zulko/moviepy/moviepy/config.py
        # The MIT License (MIT)
        # Copyright (c) 2015 Zulko
        #
        :raises IOError: [description]
        """
        FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")

        if FFMPEG_BINARY == "ffmpeg-imageio":
            FFMPEG_BINARY = get_ffmpeg_exe()
        else:
            success, err = self._try_cmd([FFMPEG_BINARY])
            if not success:
                raise IOError(
                    f"{err} - The path specified for the ffmpeg binary might be wrong"
                )
        os.environ["FFMPEG_BINARY"] = FFMPEG_BINARY


    def _try_cmd(self, cmd):
        """
        # Derived from ffmpeg detection code borrowed from moviepy 
        # https://github.com/Zulko/moviepy/moviepy/config.py
        # The MIT License (MIT)
        # Copyright (c) 2015 Zulko
        #
        :param cmd: command to execute
        :type cmd: string
        :return: True/False with error
        :rtype: Bool, Error
        """
        try:
            popen_params = self._cross_platform_popen_params(
                {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "stdin": subprocess.DEVNULL}
            )
            proc = subprocess.Popen(cmd, **popen_params)
            proc.communicate()
        except Exception as err:
            return False, err
        else:
            return True, None


    def _cross_platform_popen_params(self, popen_params):
        """ 
        # Derived from ffmpeg detection code borrowed from moviepy 
        # https://github.com/Zulko/moviepy/moviepy/config.py
        # The MIT License (MIT)
        # Copyright (c) 2015 Zulko
        #
        Wrap with this function a dictionary of ``subprocess.Popen`` kwargs and
        will be ready to work without unexpected behaviours in any platform.
        Currently, the implementation will add to them:
        - ``creationflags=0x08000000``: no extra unwanted window opens on Windows
        when the child process is created. Only added on Windows.

        :param popen_params: original popen_parameters
        :type popen_params: dict
        :return: modified popen_parameters
        :rtype: dict
        """
        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000
        return popen_params
