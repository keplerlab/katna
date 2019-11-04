"""
.. module:: Katna.frame_extractor
    :platform: OS X
    :synopsis: This module has functions related to key frame extraction 
"""

import cv2
import operator
import numpy as np
from scipy.signal import argrelextrema

import tempfile
import Katna.config as config

# Class to hold information about each frame
class Frame:
    """Class for storing frame ref
    """

    def __init__(self, frame, sum_abs_diff):
        self.frame = frame
        self.sum_abs_diff = sum_abs_diff


class FrameExtractor(object):
    """Class for extraction of key frames from video : based on sum of absolute differences in LUV colorspace from given video 
    """

    def __init__(self):

        # Setting local maxima criteria
        self.USE_LOCAL_MAXIMA = config.FrameExtractor.USE_LOCAL_MAXIMA
        # Lenght of sliding window taking difference
        self.len_window = config.FrameExtractor.len_window
        # Chunk size of Images to be processed at a time in memory
        self.max_frames_in_chunk = config.FrameExtractor.max_frames_in_chunk

    def __calculate_frame_difference(self, frame, curr_frame, prev_frame):
        """Function to calculate the difference between current frame and previous frame

        :param frame: frame from the video
        :type frame: numpy array
        :param curr_frame: current frame from the video in LUV format
        :type curr_frame: numpy array
        :param prev_frame: previous frame from the video in LUV format
        :type prev_frame: numpy array
        :return: difference count and frame if None is empty or undefined else None
        :rtype: tuple
        """

        if curr_frame is not None and prev_frame is not None:
            # Calculating difference between current and previous frame
            diff = cv2.absdiff(curr_frame, prev_frame)
            count = np.sum(diff)
            frame = Frame(frame, count)

            return count, frame
        return None

    def __process_frame(self, frame, prev_frame, frame_diffs, frames):
        """Function to calculate the difference between current frame and previous frame

        :param frame: frame from the video
        :type frame: numpy array
        :param prev_frame: previous frame from the video in LUV format
        :type prev_frame: numpy array
        :param frame_diffs: list of frame differences
        :type frame_diffs: list of int
        :param frames: list of frames
        :type frames: list of numpy array
        :return: previous frame and current frame
        :rtype: tuple
        """

        luv = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
        curr_frame = luv
        # Calculating the frame difference for previous and current frame
        frame_diff = self.__calculate_frame_difference(frame, curr_frame, prev_frame)
        
        if frame_diff is not None:
            count, frame = frame_diff
            frame_diffs.append(count)
            frames.append(frame)
        prev_frame = curr_frame

        return prev_frame, curr_frame

    def __extract_all_frames_from_video__(self, videopath):
        """Generator function for extracting frames from a input video which are sufficiently different from each other, 
        and return result back as list of opencv images in memory

        :param videopath: inputvideo path
        :type videopath: `str`
        :return: Generator with extracted frames in max_process_frames chunks and difference between frames
        :rtype: generator object with content of type [numpy.ndarray, numpy.ndarray] 
        """
        cap = cv2.VideoCapture(str(videopath))

        ret, frame = cap.read()
        i = 1
        chunk_no = 0
        while ret:
            curr_frame = None
            prev_frame = None

            frame_diffs = []
            frames = []
            for _ in range(0, self.max_frames_in_chunk):
                if ret:
                    # Calling process frame function to calculate the frame difference and adding the difference 
                    # in **frame_diffs** list and frame to **frames** list
                    prev_frame, curr_frame = self.__process_frame(frame, prev_frame, frame_diffs, frames)
                    i = i + 1
                    ret, frame = cap.read()
                    # print(frame_count)
                else:
                    cap.release()
                    break
            chunk_no = chunk_no + 1
            yield frames, frame_diffs
        cap.release()

    def __get_frames_in_local_maxima__(self, frames, frame_diffs):
        """ Internal function for getting local maxima of key frames 
        This functions Returns one single image with strongest change from its vicinity of frames 
        ( vicinity defined using window length ) 

        :param object: base class inheritance
        :type object: class:`Object`
        :param frames: list of frames to do local maxima on
        :type frames: `list of images`
        :param frame_diffs: list of frame difference values 
        :type frame_diffs: `list of images`

        """
        extracted_key_frames = []
        diff_array = np.array(frame_diffs)
        # Normalizing the frame differences based on windows parameters
        sm_diff_array = self.__smooth__(diff_array, self.len_window)

        # Get the indexes of those frames which have maximum differences
        frame_indexes = np.asarray(argrelextrema(sm_diff_array, np.greater))[0]

        for frame_index in frame_indexes:
            extracted_key_frames.append(frames[frame_index - 1].frame)
        return extracted_key_frames

    def __smooth__(self, x, window_len, window=config.FrameExtractor.window_type):
        """smooth the data using a window with requested size.
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        example:
        import numpy as np
        t = np.linspace(-2,2,0.1)
        x = np.sin(t)+np.random.randn(len(t))*0.1
        y = smooth(x)
        see also:
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter
        
        :param x: the frame difference list
        :type x: numpy.ndarray
        :param window_len: the dimension of the smoothing window
        :type window_len: slidding window length
        :param window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman' flat window will produce a moving average smoothing.
        :type window: str
        :return: the smoothed signal
        :rtype: ndarray
        """
        # This function takes 
        if x.ndim != 1:
            raise (ValueError, "smooth only accepts 1 dimension arrays.")

        if x.size < window_len:
            raise (ValueError, "Input vector needs to be bigger than window size.")

        if window_len < 3:
            return x

        if not window in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
            raise (
                ValueError,
                "Smoothing Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'",
            )

        # Doing row-wise merging of frame differences wrt window length. frame difference
        # by factor of two and subtracting the frame differences from index == window length in reverse direction
        s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]

        if window == "flat":  # moving average
            w = np.ones(window_len, "d")
        else:
            w = getattr(np, window)(window_len)
        y = np.convolve(w / w.sum(), s, mode="same")
        return y[window_len - 1 : -window_len + 1]

    def extract_candidate_frames(self, videopath):
        """ Pubic function for this module , Given and input video path
        This functions Returns one list of all candidate key-frames  

        :param object: base class inheritance
        :type object: class:`Object`
        :param videopath: inputvideo path
        :type videopath: `str`
        :return: opencv.Image.Image objects
        :rtype: list
        """

        extracted_candidate_key_frames = []

        # Get all frames from video in chunks using python Generators
        frame_extractor_from_video_generator = self.__extract_all_frames_from_video__(
            videopath
        )

        # Loop over every frame in the frame extractor generator object and calculate the
        # local maxima of frames 
        for frames, frame_diffs in frame_extractor_from_video_generator:
            extracted_candidate_key_frames_chunk = []
            if self.USE_LOCAL_MAXIMA:

                # Getting the frame with maximum frame difference
                extracted_candidate_key_frames_chunk = self.__get_frames_in_local_maxima__(
                    frames, frame_diffs
                )
                extracted_candidate_key_frames.extend(
                    extracted_candidate_key_frames_chunk
                )

        return extracted_candidate_key_frames
