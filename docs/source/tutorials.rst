How to use
==========

Video
------

You can run the smart key-frame extraction funtionality by using the code snippet below.

.. code-block:: python
   :emphasize-lines: 4,13-15
   :linenos:

   from Katna.video import Video
   import os

   #instantiate the video class
   vd = Video()

   #number of key-frame images to be extracted
   no_of_frames_to_returned = 12

   #Input Video file path
   video_file_path = os.path.join(".", "tests","data", "pos_video.mp4")

   #Call the public key-frame extraction method
   imgs = vd.extract_frames_as_images(no_of_frames = no_of_frames_to_returned, \
        file_path= video_file_path)

   # Make folder for saving frames
   output_folder_video_image = 'selectedframes'
   if not os.path.isdir(os.path.join(".", output_folder_video_image)):
        os.mkdir(os.path.join(".", output_folder_video_image))

   # Save all frames to disk
   for counter,img in enumerate(imgs):
        vd.save_frame_to_disk(img, file_path=output_folder_video_image, \
            file_name="test_"+str(counter), file_ext=".jpeg")
