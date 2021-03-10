"""
.. module:: Katna.config
    :platform: Platfrom Independent
    :synopsis: This module defines some helpful configuration variables
"""
import os

# # Configuration parameters for Image class
class Image:
    # default value by which image size to be reduces for processing
    down_sample_factor = 8
    # Debug flag
    DEBUG = False
    # Crop_height_reduction_factor_in_each_iterationnot found crop height
    # will be reduced by this multiplier/factor and search for candidate crops
    # is resumed.
    # Decreasing the height and width for crops while checking it don't get small by 1/(min_image_to_crop_factor) of image height/width
    min_image_to_crop_factor = 4
    crop_height_reduction_factor_in_each_iteration = 0.05


# # Configurations for Scoring crops for crop extractor
class CropScorer:
    detail_weight = 0.2  # default weight value for detail parameter
    edge_radius = 0.4  # default edge radius
    edge_weight = -20  # default edge weight
    outside_importance = (
        -0.5
    )  # default value to set if the pixel is outside crop rectangle
    rule_of_thirds = True  # boolean to set rule of third condition check
    saliency_bias = 0.2  # bias color value for saliency(+- error value)
    saliency_weight = 1.3  # default edge radius
    face_bias = 0.01  # bias color value for face(+- error value)
    face_weight = 3.4  # default weight value for face parameter
    rects_weight = 1  # default weight value for crop rectangles


# # Configurations for Text detection class
class TextDetector:
    # Min Confidence Threshold for Text detection model
    min_confidence = 0.9
    # Threshold for merging text detection boxes
    merge_threshold = 1
    # Name of Model files to be used for text detection
    frozen_weights = "frozen_east_text_detection.pb"
    # Location where model file will be downloaded
    cache_subdir = "models"
    # Layers Name for text detection
    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
    # Download Link for Text detection model
    model_download_link = "https://github.com/oyyd/frozen_east_text_detection.pb/raw/master/frozen_east_text_detection.pb"


# # Configurations for Edge Feature class
class EdgeFeature:
    # min edge threshold value
    min_val_threshold = 100
    # Max edge threshold value
    max_val_threshold = 200
    # aperture_size/size of Sobel kernel for canny edge detector
    ksize = 3


# # Configurations for Face detection Feature class
class FaceFeature:
    # Model file name to be used for face detection
    model_file = "res10_300x300_ssd_iter_140000_fp16.caffemodel"
    # Model definition file name to be used for face detetion
    prototxt_file = "deploy.prototxt"
    # Location where model file will be downloaded
    cache_subdir = "models"
    # Min Confidence Threshold for face detection model
    confidence = 0.5
    # Download Link for face detection model defintion file
    prototxt_download_link = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
    # Download Link for face detection model
    modelfile_download_link = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel"


# # Configuration parameters for Video class
class Video:
    # Debug flag
    DEBUG = False
    min_video_duration = 5.0

    # https://trac.ffmpeg.org/wiki/Encode/H.264

    # Keep this between 20 to 30 value
    video_compression_crf_parameter = 23
    video_compression_codec = "libx264"  # Currently "libx264 and  is supported"
    compression_output_file_extension = "mp4"
    
    # Supported/valid video extensions supported by ffmpeg
    # You can generate updated list by using following shell script on MacOSX or Linux
    # $ ffmpeg -demuxers -hide_banner | tail -n +5 | cut -d' ' -f4 | xargs -I{} ffmpeg -hide_banner -h demuxer={} | grep 'Common extensions' | cut -d' ' -f7 | tr ',' $'\n' | tr -d '.'
    
    video_extensions = [
        ".str",
        ".aa",
        ".aac",
        ".ac3",
        ".acm",
        ".adf",
        ".adp",
        ".dtk",
        ".ads",
        ".ss2",
        ".adx",
        ".aea",
        ".afc",
        ".aix",
        ".al",
        ".ape",
        ".apl",
        ".mac",
        ".aptx",
        ".aptxhd",
        ".aqt",
        ".ast",
        ".avi",
        ".avr",
        ".bfstm",
        ".bcstm",
        ".bit",
        ".bmv",
        ".brstm",
        ".cdg",
        ".cdxl",
        ".xl",
        ".c2",
        ".302",
        ".daud",
        ".str",
        ".dss",
        ".dts",
        ".dtshd",
        ".dv",
        ".dif",
        ".cdata",
        ".eac3",
        ".paf",
        ".fap",
        ".flm",
        ".flac",
        ".flv",
        ".fsb",
        ".g722",
        ".722",
        ".tco",
        ".rco",
        ".g723_1",
        ".g729",
        ".genh",
        ".gsm",
        ".h261",
        ".h26l",
        ".h264",
        ".264",
        ".avc",
        ".hevc",
        ".h265",
        ".265",
        ".idf",
        ".cgi",
        ".sf",
        ".ircam",
        ".ivr",
        ".flv",
        ".lvf",
        ".m4v",
        ".mkv",
        ".mk3d",
        ".mka",
        ".mks",
        ".mjpg",
        ".mjpeg",
        ".mpo",
        ".j2k",
        ".mlp",
        ".mov",
        ".mp4",
        ".m4a",
        ".3gp",
        ".3g2",
        ".mj2",
        ".mp2",
        ".mp3",
        ".m2a",
        ".mpa",
        ".mpc",
        ".mjpg",
        ".txt",
        ".mpl2",
        ".sub",
        ".msf",
        ".mtaf",
        ".ul",
        ".musx",
        ".mvi",
        ".mxg",
        ".v",
        ".nist",
        ".sph",
        ".nsp",
        ".nut",
        ".ogg",
        ".oma",
        ".omg",
        ".aa3",
        ".pjs",
        ".pvf",
        ".yuv",
        ".cif",
        ".qcif",
        ".rgb",
        ".rt",
        ".rsd",
        ".rsd",
        ".rso",
        ".sw",
        ".sb",
        ".smi",
        ".sami",
        ".sbc",
        ".msbc",
        ".sbg",
        ".scc",
        ".sdr2",
        ".sds",
        ".sdx",
        ".shn",
        ".vb",
        ".son",
        ".sln",
        ".mjpg",
        ".stl",
        ".sub",
        ".sub",
        ".sup",
        ".svag",
        ".tak",
        ".thd",
        ".tta",
        ".ans",
        ".art",
        ".asc",
        ".diz",
        ".ice",
        ".nfo",
        ".txt",
        ".vt",
        ".ty",
        ".ty+",
        ".uw",
        ".ub",
        ".v210",
        ".yuv10",
        ".vag",
        ".vc1",
        ".viv",
        ".idx",
        ".vpk",
        ".txt",
        ".vqf",
        ".vql",
        ".vqe",
        ".vtt",
        ".wsd",
        ".xmv",
        ".xvag",
        ".yop",
        ".y4m",
    ]


# Configuration parameters for mediapipe
class MediaPipe:
    class AutoFlip:

        # Rerun is required due to autoflip issue mentione here:
        # https://github.com/google/mediapipe/issues/497
        RERUN_LIMIT = 2

        # Models folder location
        MODELS_FOLDER_LOCATION = os.path.join(os.getcwd(), "mediapipe", "models")

        # pbtxt temp folder name
        TMP_PBTXT_FOLDER_NAME = "temp_pbtxt"
        TMP_PBTXT_FOLDER_PATH = os.path.join(os.getcwd(), TMP_PBTXT_FOLDER_NAME)

        # Default pbtxt and build cmd
        CONFIG_FILE_PBTXT = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "mediapipe_autoflip.pbtxt"
        )
        BUILD_CMD = "run_autoflip"

        # user friendly conf keys
        ENFORCE_FEATURES_KEYNAME = "ENFORCE_FEATURES"
        STABALIZATION_THRESHOLD_KEYNAME = "STABALIZATION_THRESHOLD"
        BLUR_AREA_OPACITY_KEYNAME = "BLUR_AREA_OPACITY"

        # DEFAULT VALUES IN PBTXT
        DEFAULT_BLUR_AREA_OPACITY = 0.6
        DEFAULT_MOTION_STABALIZATION_THRESHOLD = 0.5
        DEFAULT_FEATURE_SIGNAL_VALUE = "false"

        # ENFORCE_FEATURES Keys
        _FACE_CORE_LANDMARKS = "FACE_CORE_LANDMARKS"
        _FACE_FULL = "FACE_FULL"
        _FACE_ALL_LANDMARKS = "FACE_ALL_LANDMARKS"
        _HUMAN = "HUMAN"
        _PET = "PET"
        _CAR = "CAR"
        _OBJECT = "OBJECT"

        # the variables names below should match the keyname for set_conf to work
        # smoothly
        # ENFORCE_FEATURES list
        ENFORCE_FEATURES = {
            _FACE_CORE_LANDMARKS: False,
            _FACE_ALL_LANDMARKS: False,
            _FACE_FULL: False,
            _HUMAN: False,
            _PET: False,
            _CAR: False,
            _OBJECT: False,
        }

        # % AREA from center where most of the content is
        # usually applied when content is focused near center
        STABALIZATION_THRESHOLD = DEFAULT_MOTION_STABALIZATION_THRESHOLD

        # opacity of blur area
        BLUR_AREA_OPACITY = DEFAULT_BLUR_AREA_OPACITY

        @classmethod
        def get_pbtxt_mapping(cls):
            return {
                cls.ENFORCE_FEATURES_KEYNAME: "signal_settings",
                cls.STABALIZATION_THRESHOLD_KEYNAME: "motion_stabilization_threshold_percent",
                cls.BLUR_AREA_OPACITY_KEYNAME: "overlay_opacity",
            }

        @classmethod
        def get_conf(cls):
            """Gets the current config

            :return: dictionary containing the current config
            :rtype: dict
            """
            return {
                cls.ENFORCE_FEATURES_KEYNAME: cls.ENFORCE_FEATURES,
                cls.STABALIZATION_THRESHOLD_KEYNAME: cls.STABALIZATION_THRESHOLD,
                cls.BLUR_AREA_OPACITY_KEYNAME: cls.BLUR_AREA_OPACITY,
            }

        @classmethod
        def set_conf(cls, config):
            """Sets the config passed

            :param config: The configuration to set.
            :type config: dict
            """
            for attr in config.keys():
                current_conf = cls.get_conf()
                if attr in current_conf.keys():

                    if attr == cls.ENFORCE_FEATURES_KEYNAME:
                        updated_attr_dict = {**current_conf[attr], **config[attr]}
                        setattr(cls, attr, updated_attr_dict)
                    else:
                        setattr(cls, attr, config[attr])

                else:
                    raise Exception(
                        " Invalid configuration. Use get_conf method to see existing configuration or refer documentation."
                    )


class ImageSelector:
    # Setting for optimum Brightness values
    min_brightness_value = 10.0
    max_brightness_value = 90.0
    brightness_step = 2.0
    # Setting for optimum Contrast/Entropy values
    min_entropy_value = 1.0
    max_entropy_value = 10.0
    entropy_step = 0.5


class FrameExtractor:
    # Setting local maxima criteria
    USE_LOCAL_MAXIMA = True
    # Lenght of sliding window taking difference
    len_window = 20
    # Chunk size of Images to be processed at a time in memory
    max_frames_in_chunk = 2500
    # Type of smoothening window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman' flat window will produce a moving average smoothing.
    window_type = "hanning"
