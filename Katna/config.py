"""
.. module:: Katna.config
    :platform: Platfrom Independent
    :synopsis: This module defines some helpful configuration variables
"""


# # Configuration parameters for Image class
class Image:
    # default value by which image size to be reduces for processing
    down_sample_factor = 8
    # Debug flag
    DEBUG = False


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


class ImageSelector:
    # Setting for optimum Brightness values
    min_brightness_value = 10.0
    max_brightness_value = 90.0
    # Setting for optimum Contrast/Entropy values
    min_entropy_value = 1.0
    max_entropy_value = 10.0


class FrameExtractor:
    # Setting local maxima criteria
    USE_LOCAL_MAXIMA = True
    # Lenght of sliding window taking difference
    len_window = 20
    # Chunk size of Images to be processed at a time in memory
    max_frames_in_chunk = 2500
    # Type of smoothening window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman' flat window will produce a moving average smoothing.
    window_type = "hanning"
