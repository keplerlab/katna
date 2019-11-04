Tips and Troubleshooting
------------------------

1) If input image is of very large size ( larger than 2000x2000 ) it might take a
long time to perform Automatic smart cropping.If you encounter this issue, consider changing down_sample_factor
from default 8 to larger values ( like 16 or 32 ). This will decrease processing time 
significantly. 

2) If you get "AttributeError: module 'cv2.cv2' has no attribute 'saliency'" error. then try  
re-installing opencv-contrib

.. code-block:: shell

    python -m pip uninstall opencv-contrib-python 
    python -m pip install opencv-contrib-python

3) If you get "FileNotFoundError: frozen_east_text_detection.pb file not found". Open python shell 
and follow the below commands.

.. code-block:: python

    from Katna.image_filters.text_detector import TextDetector
    td = TextDetector()
    td.download_data()

4) If you are running the code on windows, make sure to create the main file in the 
below format.

.. code-block:: python

    from Katna.video import Video

    def main():
        vd = Video()
        # your code...

    if __name__ == "__main__":
        main()

OR

.. code-block:: python

    from Katna.video import Video

    if __name__ == "__main__":
    
        vd = Video()
        # your code


5) On windows, ensure that anaconda has admin rights if installing with anaconda as it fails with
the write permission while installing some modules.

6) Python version 3.8 not supported due to the numpy and moviepy errors with this python 
version.

7) If you get "RuntimeError: No ffmpeg exe could be found. Install ffmpeg on your system, or 
set the IMAGEIO_FFMPEG_EXE environment variable". Go to the **imageio-ffmpeg-*.egg** folder inside your
**site-packages** folder, there's ffmpeg file inside binaries folder set it's path to environment variable.

   