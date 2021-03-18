.. _tutorials_video:

========================
Using Katna.video
========================

Extract keyframes for a video
----------------------------------------------------------------

**Step 1**

Import the video module 

.. code-block:: python

   from Katna.video import Video

**Step 2**

Instantiate the video class inside your main module (necessary for multiprocessing in windows)

.. code-block:: python

     if __name__ == "__main__":
          vd = Video()
   
**Step 3**

Call the **extract_video_keyframes** method.
The method accepts two parameters and returns a list of numpy 2D array which are images. 
Refer to API reference for further details. Below are the two parameters required by the method

1. **no_of_frames**: Number of key frames to be extracted

2. **file_path**: Video file path.

3. **writer**: Writer class instance to process keyframe data for a file (use KeyFrameDiskWriter from Katna.writer module to save data at a location).


.. code-block:: python

     # initialize diskwriter to save data at desired location
     diskwriter = KeyFrameDiskWriter(location="selectedframes")

     vd.extract_video_keyframes(
          no_of_frames=no_of_frames_to_returned, file_path=video_file_path,
          writer=diskwriter
     )

Code below is a complete example for a single video file.

.. code-block:: python
   :emphasize-lines: 1,8,11,14,17,22-24
   :linenos:

   from Katna.video import Video
   from Katna.writer import KeyFrameDiskWriter
   import os
   
   # For windows, the below if condition is must.
   if __name__ == "__main__":

     # initialize video module
     vd = Video()

     # number of images to be returned
     no_of_frames_to_returned = 12

     # initialize diskwriter to save data at desired location
     diskwriter = KeyFrameDiskWriter(location="selectedframes")

     # Video file path
     video_file_path = os.path.join(".", "tests", "data", "pos_video.mp4")

     print(f"Input video file path = {video_file_path}")

     # extract keyframes and process data with diskwriter
     vd.extract_video_keyframes(
          no_of_frames=no_of_frames_to_returned, file_path=video_file_path,
          writer=diskwriter
     )
     

Extract keyframes for all videos in a directory
----------------------------------------------------------------

Call the **extract_keyframes_from_videos_dir** method.
The method accepts three parameters and writes the data using a Writer class object. Katna comes with a default
writer named "KeyFrameDiskWriter".

1. **no_of_frames**: Number of key frames to be extracted

2. **dir_path**: Directory path which has all the videos.

3. **writer**: Writer class instance to process keyframe data for a file (use KeyFrameDiskWriter from Katna.writer module to save data at a location).

.. code-block:: python

     diskwriter = KeyFrameDiskWriter(location="/path/to/output/folder")
     
     vd.extract_keyframes_from_videos_dir(no_of_frames = no_of_frames_to_return, \
     dir_path= dir_path_containing_videos, writer=diskwriter)


Code below is a complete example for a directory containing videos.

.. code-block:: python
   :emphasize-lines: 1,2,10,13,17,19,21-23
   :linenos:

   from Katna.video import Video
   from Katna.writer import KeyFrameDiskWriter
   import os
   import ntpath

   # For windows, the below if condition is must.
   if __name__ == "__main__":

     #instantiate the video class
     vd = Video()

     #number of key-frame images to be extracted
     no_of_frames_to_return = 3

     #Input Video directory path
     #All .mp4 and .mov files inside this directory will be used for keyframe extraction)
     videos_dir_path = os.path.join(".", "tests","data")

     diskwriter = KeyFrameDiskWriter(location="selectedframes")

     vd.extract_keyframes_from_videos_dir(
          no_of_frames=no_of_frames_to_return, dir_path=videos_dir_path,
          writer=diskwriter
     )


**Note**: You can create custom writers to process the data in a different way. Check the :ref:`Katna.custom_writers` section for details.


.. _tutorials_video_smart_resize:

Smart video resize using katna
----------------------------------------------------------------


Please note that is it necessary to first install and initialize
Google mediapipe autoflip solution before using Katna video 
resize (experimental) feature.

Install Google Mediapipe library and Autoflip solution. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install Mediapipe by following these instructions `here <https://google.github.io/mediapipe/getting_started/install>`_.
     
2. Build Autoflip c++ solution by following these instructions `from here <https://google.github.io/mediapipe/solutions/autoflip>`_.



Resize a single video using Katna (Using Experimental Mediapipe Autoflip bridge)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Step 1**

Import the video module 

.. code-block:: python

     from Katna.video import Video

**Step 2**

Instantiate the video class inside your main module (necessary for multiprocessing in windows)

.. code-block:: python

     autoflip_build_path = "/absolute/path/to/autoflip/build/folder
     autoflip_model_path = "/absolute/path/to/autoflip/model/folder

     if __name__ == "__main__":
          vd = Video(autoflip_build_path, autoflip_model_path)

**Step 3 (Optional)**

Configure the mediapipe autoflip properties. To check the list of configurable options, check :ref:`Katna.video_resize`. 

.. code-block:: python

     import Katna.config as app_config

     # get the current configuration
     conf = app_config.MediaPipe.AutoFlip.get_conf()

     # set True for features which are required in output video
     conf["ENFORCE_FEATURES"] = {
          "FACE_CORE_LANDMARKS": False,
          "FACE_ALL_LANDMARKS": False,
          "FACE_FULL": False,
          "HUMAN": False,
          "PET": False,
          "CAR": False,
          "OBJECT": False
     }

     # % stabalization threshold
     conf["STABALIZATION_THRESHOLD"] = 0.5

     # opacity of blur area
     conf["BLUR_AREA_OPACITY"] = 0.6

     # update configuration
     app_config.MediaPipe.AutoFlip.set_conf(conf)

     
**Step 4**

Call the **resize_video** method.
The method accepts three parameters and returns a status whether video resize is
performed successfully or not. 
Refer to API reference for further details. Below are the four parameters required by the method


1. **file_path**: Video file path.

2. **abs_file_path_output**: absolute path for saving final output file.

3. **aspect_ratio**: required aspect ratio for output video. e.g. "4:3"


.. code-block:: python

     vd.resize_video(file_path = file_path, abs_file_path_output = abs_file_path_output, aspect_ratio = aspect_ratio)


Code below is a complete example for a single video file.

.. code-block:: python
     :emphasize-lines: 1,8,11,19-20,22-25
     :linenos:

     from Katna.video import Video
     import os
     
     # For windows, the below if condition is must.
     if __name__ == "__main__":

          # set the autoflip build and model path directory based on your installation
          # usually autoflip build is located here : /mediapipe/repo/bazel-build/mediapipe/examples/desktop/autoflip
          # usually mediapipe model is located here : /mediapipe/repo/mediapipe/models
          autoflip_build_path = "/absolute/path/to/autoflip/build/folder
          autoflip_model_path = "/absolute/path/to/autoflip/model/folder

          # desired aspect ratio (e.g potrait mode - 9:16)
          aspect_ratio = 9:16

          # input video file path
          file_path = os.path.join(".", "tests", "data", "pos_video.mp4")

          # output file to save resized video
          abs_file_path_output = os.path.join(".", "tests", "data", "pos_video_resize.mp4")

          #instantiate the video class
          vd = Video(autoflip_build_path, autoflip_model_path)
          
          print(f"Input video file path = {file_path}")

          vd.resize_video(file_path = file_path, abs_file_path_output = abs_file_path_output, aspect_ratio = aspect_ratio)

          print(f"output resized video file path = {abs_file_path_output}")


**NOTE : In case of subprocess.CalledProcessError, try running the resize_video method again.**


Resize multiple videos in a directory using Katna (Using Experimental Mediapipe Autoflip bridge)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Call the **resize_video_from_dir** method.
The method accepts three parameters and returns a status whether video resize is
performed successfully or not. 
Refer to API reference for further details. Below are the four parameters required by the method


1. **dir_path**: Directory path where videos are stored.

2. **abs_dir_path_output**: absolute path to directory where resized videos will be dumped.

3. **aspect_ratio**: required aspect ratio for output video. e.g. "4:3"


.. code-block:: python

     vd.resize_video_from_dir(dir_path = dir_path, abs_dir_path_output = abs_dir_path_output, aspect_ratio = aspect_ratio)


Code below is a complete example for a folder full of video file.

.. code-block:: python
     :emphasize-lines: 1,8,11,18
     :linenos:

     from Katna.video import Video
     import os
     
     # For windows, the below if condition is must.
     if __name__ == "__main__":

          # folder where videos are located
          dir_path = file_path = os.path.join(".", "tests", "data")

          # output folder to dump videos after resizing
          abs_dir_path_output = os.path.join(".", "tests", "data", "resize_results")

          # intialize video class
          vd = Video(autoflip_build_path, autoflip_model_path)

          # invoke resize for directory
          try:
               vd.resize_video_from_dir(dir_path = dir_path, abs_dir_path_output = abs_dir_path_output, aspect_ratio = aspect_ratio)
          except Exception as e:
               raise e
          
          print(f"output resized video dir path = {abs_dir_path_output}")

     
In addition, you can also compress videos using Katna video module. Refer the how to guide on
:ref:`Katna.compress_videos` for details.

