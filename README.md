
## **Katna**: Tool for automating video keyframe extraction 

### Resources 
* Homepage and Reference: <https://keplervaani.com/katna/>

### Description
Katna is a tool that automates video key/best frames extraction. Key-frames are defined as the representative frames of a video stream, the frames that provide the most accurate and compact summary of the video content.

Video module takes following frame extraction and selection method into consideration:

1) Frame extraction from a input video which are sufficiently different using absolute differences in LUV colorspace 
2) Brightness score filtering of extracted frames
3) Entropy/contrast score filtering of extracted frames
4) K-Means clustering of frames using image histogram
5) Selection of best frame from each cluster based on variance of laplacian feature (image blur detection)

More selection features are in developement pipeline

###  How to install

#### Using pypi
1) Install Python 3 
2) pip install --extra-index-url https://testpypi.python.org/pypi katna

#### Install from source

1) Install git
2) Install Anaconda or Miniconda Python
3) Open terminal 
4) Clone repo from here https://github.com/keplerlab/Katna.git 
5) Change the directory to the directory where you have cloned your repo 
    ```
    $cd path_to_the_folder_repo_cloned
    ```

6) If running katna for the first time, run the following commands in the below
   mentioned order:
    ```
    conda create --name katna python=3
    source activate katna 
    python setup.py install 
    ```
   Above is one-time command which has to be executed only when you want to install library 
   for the first time. 
 
 
### How to use Library

1) Refer to quickstart section in Katna Reference 
   from https://keplervaani.com/katna/tutorials.html 
