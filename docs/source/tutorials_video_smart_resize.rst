.. _tutorials_video_smart_resize:

Smart video resize using katna  
=================================


Please note that is it necessary to first install and initialize
Google mediapipe autoflip solution before using Katna video 
resize (experimental) feature.

Install Google Mediapipe library and Autoflip solution. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install Mediapipe by following these instructions : https://google.github.io/mediapipe/getting_started/install
   
2. Build Autoflip c++ solution by following these instructions: https://google.github.io/mediapipe/solutions/autoflip



Resize a single video using Katna (Using Experimental Mediapipe Autoflip bridge)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Call the **resize_video** method.
The method accepts four parameters and returns a status whether video resize is
performed successfully or not. 
Refer to API reference for further details. Below are the four parameters required by the method

1. **abs_path_to_autoflip_build**: Number of key frames to be extracted

2. **file_path**: Video file path.

3. **abs_file_path_output**: absolute path for saving final output file.

4. **output_aspect_ratio**: required aspect ratio for output video. e.g. "4:3"


.. code-block:: python

     status = vd.resize_video(abs_path_to_autoflip_build ,file_path ,abs_file_path_output, output_aspect_ratio)


Code below is a complete example for a single video file.

.. code-block:: python
   :emphasize-lines: 1,8,11,19-20,22-25
   :linenos:

   from Katna.video import Video
   import os
   
   # For windows, the below if condition is must.
   if __name__ == "__main__":

     #instantiate the video class
     vd = Video()

    # folder to save resized video
    output_folder_resized_video = "resized_video"
    out_dir_path = os.path.join(".", output_folder_resized_video)

    if not os.path.isdir(out_dir_path):
        os.mkdir(out_dir_path)

    # number of images to be returned
    # VIdeo file path
    video_file_path = os.path.join(".", "tests", "data", "pos_video.mp4")
    print(f"Input video file path = {video_file_path}")

    vd.resize_video(abs_path_to_autoflip_build,
                     file_path,
                     abs_file_path_output,
                     output_aspect_ratio)

    print(f"output resized video file path = {abs_file_path_output}")


Resize a multiple videos in a directory using Katna (Using Experimental Mediapipe Autoflip bridge)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Call the **resize_video_from_dir** method.
The method accepts four parameters and returns a status whether video resize is
performed successfully or not. 
Refer to API reference for further details. Below are the four parameters required by the method

1. **abs_path_to_autoflip_build**: Number of key frames to be extracted

2. **file_path**: Video file path.

3. **abs_file_path_output**: absolute path for saving final output file.

4. **output_aspect_ratio**: required aspect ratio for output video. e.g. "4:3"


.. code-block:: python

     status = vd.resize_video_from_dir(abs_path_to_autoflip_build ,file_path ,abs_file_path_output, output_aspect_ratio)


Code below is a complete example for a folder full of video file.

.. code-block:: python
   :emphasize-lines: 1,8,11,18-19,21-24
   :linenos:

   from Katna.video import Video
   import os
   
   # For windows, the below if condition is must.
   if __name__ == "__main__":

     #instantiate the video class
     vd = Video()

    # folder to save resized video
    output_folder_resized_video = "resized_videos"
    out_dir_path = os.path.join(".", output_folder_resized_video)

    if not os.path.isdir(out_dir_path):
        os.mkdir(out_dir_path)

     # Video file path
     video_folder_path = os.path.join(".", "tests", "data")
     print(f"Input video folder path = {video_folder_path}")

    vd.resize_video_from_dir(abs_path_to_autoflip_build,
                     video_folder_path,
                     out_dir_path,
                     output_aspect_ratio)

    print(f"output resized videos folder path = {out_dir_path}")
