Understanding katna
======================

As mentioned in intro section katna consists of two modules,
Video and Image, In this section we will go into details about 
each modules working. 

Katna.video Module:
--------------------

Video module handles the task(s) for key frame(s) extraction.
This module has two primary public functions for keyframe extraction,
which are extract_video_keyframes and extract_keyframes_from_videos_dir,
extract_video_keyframes is the primary function which given a video file
extracts most important keyframe from a video. extract_keyframes_from_videos_dir
actually runs extract_video_frames function for all video files in a directory
recursively. 
Katna.video first takes a video and divides a big video in smaller chunks of 
videos, it runs video frame extraction and frame selector tasks on these chunked
videos in parallel. For each chunked video actual frame extraction is done in
Katna by following two separate modules.

Katna.frame_extractor module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In frame extractor module given a input video all the video frames that
are sufficiently different from previous ones using absolute differences
in LUV colorspace are returned.

Katna.frame_selector module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Katna.frame_selector module given list of frames
returned from frame_extractor module following checks are performed: 

1. Brightness score filtering of extracted frames.
2. Entropy/contrast score filtering of extracted frames.

Each of these properties are filtered based on threshold which you can check
and edit in Katna.config.ImageSelector properties. 

After frame filtering based on number of required frames N, N clusters are 
formed using K-Means clustering where K=N, clustering is done using
image histogram based approach. 
After K-Means clustering, for each cluster selection of best frame from
cluster is done using variance of laplacian sorting. In image processing world 
variance of laplacian method is often used for image blur detection. 
This sorting and selection ensures that least blurred image is selected
from cluster.


Katna.image Module:
---------------------

This module handles the task(s) for smart cropping.
The Smart crop feature tries to automatically identify important image
areas where the user will focus more and tries to retain it while cropping.
For a given input cropping dimension/final output image size, Katna.image works
by first extracting all possible image crop given crop specification using 
katna.crop_extractor module, Katna.crop_selector module then uses various filtering
and selection criteria to select best crops from list of image crops.
Let's read more about these two modules in details. 

Katna.crop_extractor module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Katna.crop_extractor module works by given a crop specification using a sliding
window approach it first calculates all possible crop see
**_get_all_possible_crops()** function inside Katna.crop_extractor module.
Additionally it applies rule of third and crop rectangle distance from edge score.
Configurations related to these scoring rules could be edited in
Katna.config.CropScorer module. 


Katna.crop_selector module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
After returning candidate crops from crop_extractor module Katna.crop_selector
module first does further filtering using Katna.image_filters filters.
At the moment only text filter is supported. Text filter ensures that
if cropped rectangle contains text, texts present is not abruptly cropped.

After performing crop_filtering crop selection is done by first calculating 
additional crop scoring is done based on following criteria: Saliency,
edge features and Face features.
This score is then combined with rule of third and crop distance from edge feature
calculated in crop_extractor module.
Configurations related to these scoring rules could be edited in
Katna.config.CropScorer, Katna.config.EdgeFeature, Katna.config.FaceFeature modules.
