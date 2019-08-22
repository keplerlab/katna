.. Katna documentation master file, created by
   sphinx-quickstart on Sat Jun 15 08:16:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Katna documentation
===============================
Katna automates the boring, error prone task of videos key/best frames extraction.
Key-frames are defined as the representative frames of a video stream, the frames that provide the most accurate and compact summary of the video content.


**Supported Video file formats**

All the major video formats like .mp4,.mov,.avi etc are supported. 

**Frame extraction and selection criteria**

1. Frame that are sufficiently different from previous ones using absolute differences in LUV colorspace
2. Brightness score filtering of extracted frames
3. Entropy/contrast score filtering of extracted frames
4. K-Means Clustering of frames using image histogram
5. Selection of best frame from clusters based on and variance of laplacian (image blur detection)

More selection features are in developement pipeline

.. toctree::
   :maxdepth: 1
   :hidden:

   Installation <installation>
   Quickstart <tutorials>
   API reference <modules>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
