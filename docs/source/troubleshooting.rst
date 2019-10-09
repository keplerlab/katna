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
   