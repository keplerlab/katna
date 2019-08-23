
## **Katna**: Tool for automating video keyframe extraction 

### Resources 
* Homepage and Reference: <https://keplervaani.com/katna/>

### Description
Katna automates the boring, error prone task of videos key/best frames extraction.
Key-frames are defined as the representative frames of a video stream, the frames that provide the most accurate and compact summary of the video content.


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
    conda create --name katna python=3
    source activate katna
    ```

7) Run the setup:
    ``` 
    python setup.py install 
    ```    
 
 
### How to use Library

1) Refer to quickstart section in Katna Reference 
   from https://keplervaani.com/katna/tutorials.html

### Attributions
1) We have used the SAD (Sum of absolute difference) code from https://github.com/amanwalia92/KeyFramesExtraction  
