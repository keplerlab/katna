.. Katna documentation master file, created by
   sphinx-quickstart on Sat Jun 15 08:16:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Katna documentation
===============================
Katna automates the boring, error prone task of videos key/best frames extraction,
video compression and manual time consuming task of image cropping.
In summary you should consider using Katna library if you have following tasks which you 
want to automate:

#. You have video/videos from who you want to extract keyframe/keyframes. 
   Please note Key-frames are defined as the representative frames of a video stream,
   the frames that provide the most accurate and compact summary of the video content.
#. You have video/videos you want to compress down to smaller size.
#. You have image/images which you want to smartly resize to a target resolution.
   (e.g. 500x500, 1080p (1920x1080) etc.)
#. You have image/images from which you want to intelligently extract a crop with a target resolution.
   (e.g. Get a crop of size 500x500 from image of size 1920x1080)
#. You want to extract a crop of particular aspect ratio e.g. 4:3 from your input image/images.
   (e.g. Get a crop of aspect ratio 1:1 from image of resolution 1920x1080 (16:9 aspect ratio image))



Katna is divided into two modules namely video and image module.
In next sections we will learn more about them in more details.

Video Module:
-------------
This module handles the task(s) for key frame(s) extraction and video compression.

Key-frames are defined as the representative frames of a video stream,
the frames that provide the most accurate and compact summary of the video content.

**Frame extraction and selection criteria**

1. Frame that are sufficiently different from previous ones using absolute differences in LUV colorspace
2. Brightness score filtering of extracted frames
3. Entropy/contrast score filtering of extracted frames
4. K-Means Clustering of frames using image histogram
5. Selection of best frame from clusters based on and variance of laplacian (image blur detection)

Video compression is handled using ffmpeg library. Details about which could be 
read in :ref:`Katna.video_compressor` section.

Image Module:
-------------
This module handles the task(s) for smart cropping and smart image resizing.

The Smart crop feature tries to automatically identify important image areas
where the user will focus more and tries to retain it while cropping.
For a given input cropping dimension/final output image size,
following selection and filtering criteria are used.

**Crop selection and filtering criteria**

1. Edge, saliency and Face features.
2. Distance of crop from Image edge, Rule of third
3. Crop filters. At the moment only text filter is supported.
   Text filter ensures that cropped rectangle contains text, also it ensures
   that texts present is not abruptly cropped.  

Similar to Smart crop Katna image module supports **Smart image resizing** feature.
Given an input image and target image resolution it will perform simple image image resize
if if aspect ratio is same for input and target image. 
But in case of aspect ratio is different than smart image resize will extract a optimum crop
in target resolution and then resizes image to target resolution.
This ensures image resize without actually skewing output image.
**Please not that if aspect ratio of input and output image are not same katna image_resize can lead to some loss of image content**


**Supported Video and image file formats**
##########################################

All the major video formats like .mp4,.mov,.avi etc and image formats like .jpg, .png, .jpeg etc are supported.
Only constraint is that video should be readable by ffmpeg library and images should be readable
by opencv library.

.. toctree::
   :maxdepth: 1
   :hidden:

   Installation <installation>
   Quickstart video module <tutorials_video>
   Quickstart image module <tutorials_image>
   Understanding katna <understanding_katna>
   Troubleshooting <troubleshooting>
   API reference <modules>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
