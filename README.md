
## **Katna**: Tool for automating common vide keyframe extraction and Image Autocrop and Smart image resize tasks

### Resources 
* Homepage and Reference: <https://katna.readthedocs.io/>

### Description
Katna automates the boring, error prone task of videos key/best frames extraction and manual time consuming task of image cropping.

Katna is divided into two modules namely video and image.

Video Module:
-------------
This module handles the task(s) related to key frame extraction.

Key-frames are defined as the representative frames of a video stream, the frames that provide the most accurate and compact summary of the video content.

**Frame extraction and selection criteria**

1. Frame that are sufficiently different from previous ones using absolute differences in LUV colorspace
2. Brightness score filtering of extracted frames
3. Entropy/contrast score filtering of extracted frames
4. K-Means Clustering of frames using image histogram
5. Selection of best frame from clusters based on and variance of laplacian (image blur detection)

Image Module:
-------------
This module handles the task(s) related to smart cropping and image resizing.

The Smart image cropping is happening in way that the module identifies the best part or the area where someone focus more
and interprets this information while cropping the image.

**Crop extraction and selection criteria**

1. Edge, saliency and Face detection features are detected in the input image
2. All the crops with specified dimensions are extracted with calculation of score for each crop wrt to extracted features
3. The crops will be passes through filters specified which will remove the crops which filter rejects

Similar to Smart crop Katna image module supports **Smart image resizing** feature. Given an input image it can resize image to target resolution with simple resizing if aspect ratio is same for input and target image. If aspect ratio is different than smart image resize will first crops biggest good quality crop in target resolution and then resizes image in target resolution. This ensures image resize without actually skewing input image. *Please not that if aspect ratio of input and output image are not same katna image_resize can lead to some loss of image content*

**Supported Video and image file formats**
##########################################

All the major video formats like .mp4,.mov,.avi etc and image formats like .jpg, .png, .jpeg etc are supported. 

More selection features are in developement pipeline

###  How to install

#### Using pypi
1) Install Python 3 
2) pip install katna

#### Install from source

1) Install git
2) Install Anaconda or Miniconda Python
3) Open terminal 
4) Clone repo from here https://github.com/keplerlab/Katna.git 
5) Change the directory to the directory where you have cloned your repo 
    ```
    $cd path_to_the_folder_repo_cloned
    ```
6) Create a new anaconda environment if you are using anaconda python distribution
    ```
    conda create --name katna python=3.7
    source activate katna
    ```

7) Run the setup:
    ``` 
    python setup.py install 
    ```    

#### Error handling and updates 
1) Since Katna version 0.4.0 Katna video module is optimized to use multiprocessing using python multiprocessing module. Due to restrictions of multiprocessing in windows, For safe importing of main module in windows system, make sure “entry point” of the program is wrapped in  __name__ == '__main__': as follows:
    ```
    from Katna.video import Video
    if __name__ == "__main__":
        vd = Video()
        # your code
    ```
    please refer to https://docs.python.org/2/library/multiprocessing.html#windows for more details.  

2) If input image is of very large size ( larger than 2000x2000 ) it might take a
long time to perform Automatic smart cropping.If you encounter this issue, consider changing down_sample_factor
from default 8 to larger values ( like 16 or 32 ). This will decrease processing time 
significantly. 

3) If you see "AttributeError: module 'cv2.cv2' has no attribute 'saliency'" error. Uninstall opencv-contrib
by running command "python -m pip uninstall opencv-contrib-python" and then again install it by running command 
    ```
    python -m pip install opencv-contrib-python
    ```

4) If you see "FileNotFoundError: frozen_east_text_detection.pb file not found". Open python shell and follow below commands.
    ```
    from Katna.image_filters.text_detector import TextDetector
    td = TextDetector()
    td.download()
    ```

5) On windows, ensure that anaconda has admin rights if installing with anaconda as it fails with 
the write permission while installing some modules.

6) If you get "RuntimeError: No ffmpeg exe could be found". Install ffmpeg on your system, and/or set the IMAGEIO_FFMPEG_EXE or FFMPEG_EXE environment variable to path of your ffmpeg binary.
Usually ffmpeg is installed using imageio-ffmpeg package, Check **imageio_ffmpeg-*.egg** folder inside your
**site-packages** folder, there should be a ffmpeg file inside binaries folder, check if this file has proper read/executable permission set and additionally set it's path to environment variable.

### How to use Library

1) Refer to quickstart section in Katna Reference 
   from https://katna.readthedocs.io/

### Update: katna version 0.5.0
In version 0.5.0 we have changed name of some of the public functions inside
for Katna.video module used for keyframe extraction,
1) extract_frames_as_images method is changed to extract_video_keyframes.
2) extract_frames_as_images_from_dir method is changed to extract_keyframes_from_videos_dir
### Attributions
1) We have used the SAD (Sum of absolute difference) code from https://github.com/amanwalia92/KeyFramesExtraction  
2) We have used project Smartcrop https://github.com/jwagner/smartcrop.js/ for Smart crop feature in Katna Image module
