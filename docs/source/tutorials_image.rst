.. _tutorials_image:

How to Use
==========

Image
------
**Step 1**

Import the image module.

.. code-block:: python

   from Katna.image import Image

**Step 2**

Instantiate the image class.

.. code-block:: python

     img_module = Image()
   
**Step 3**

Call the **crop_image** method. This method accepts following parameters and returns a list of crop rectangles (in crop_rect data structure).
Refer to API reference for further details. Below are the six parameters of the function

**file_path**: image file path from which crop has to be extracted

**crop_width**: width of crop to extract

**crop_height**: height of crop to extract

**no_of_crops_to_returned**: number of crops rectangles to be extracted

**filters**: You can use this **optional** parameter to filter out unwanted crop rectangles according to some filtering criteria.
At the moment only "text" detection filter is implemented and more filters will be added in future 
will be added in future. Passing on "text" detection filter ensures crop rectangle contains text, additionally it checks 
that detected "text" inside an image is not abruptly cropped by any crop_rectangle.
By default, filters are not applied.

**down_sample_factor**: You can use this **optional** feature to specify the down sampling factor. For large images
consider increasing this parameter for faster image cropping.  By default input images are downsampled by factor of 
**8** before processing. 

.. code-block:: python

     image_file_path = <Path where the image is stored>

     crop_list = img_module.crop_image(
        file_path=image_file_path,
        crop_width=<crop_width>,
        crop_height=<crop_height>,
        num_of_crops=<no_of_crops_to_returned>,
        filters=<filters>,
        down_sample_factor=<number_by_which_image_to_downsample>
     )

Or 

You can use **crop_image_from_cvimage** function in case you want to crop in-memory images. This method accepts opencv image as
image source. Rest of the parameters are same as **crop_images** method. This function helps in connecting smart image
cropping to any existing workflow.

.. code-block:: python

    img = cv2.imread(image_file_path)

    crop_list = img_module.crop_image_from_cvimage(
    input_image=img,
    #Other parameters
    )

If you want to get the crops by a specified aspect ratio. You can use **crop_image_with_aspect** function. This method accepts
**crop_aspect_ratio** as parameter instead of height & width and returns a list of crop rectangles wrt to each crop dimension it finds with the specified aspect ratio.

**crop_aspect_ratio**: use this parameter to specify the aspect ratio by which crops need to be extracted.The parameter
expects you to specify the aspect ratio in string format eg. '4:3' or '16:9'.

.. code-block:: python

     image_file_path = <Path where the image is stored>
     crop_aspect_ratio = '4:3'

     crop_list = img_module.crop_image_with_aspect(
        file_path=image_file_path,
        crop_aspect_ratio=<crop_aspect_ratio>,
        num_of_crops=<no_of_crops_to_returned>,
        filters=<filters>,
        down_sample_factor=<number_by_which_image_to_downsample>
     )

**Step 4**

To save the extracted crop rectangles call **save_crop_to_disk** method.
The method accepts following parameters and doesn't returns anything. 
Refer to API reference for further details.

1. **crop_rect**: crop rect object from the extracted crops

2. **frame**: input image from which crops are extracted

3. **file_path**: Folder location where files needs to be saved

4. **file_name**:  File name for the crop image to be saved.

5. **file_ext**: File extension indicating the file type for example - ‘.jpg’


.. code-block:: python

     img_module.save_crop_to_disk(crop_rect=<crop_rect>, frame=<image>, file_path=<output_folder_cropped_image>,
            file_name=<file_name>, 
            file_ext=<file_ext>,
        )

Code below is a complete example.

.. code-block:: python
   :emphasize-lines: 3,5,16-18,20-21,27-34,43-44
   :linenos:

    import os.path
    import cv2
    from Katna.image import Image

    img_module = Image()

    # folder to save extracted images
    output_folder_cropped_image = "selectedcrops"

    if not os.path.isdir(os.path.join(".", \
                output_folder_cropped_image)):
        
        os.mkdir(os.path.join(".",\
            output_folder_cropped_image))

    # number of images to be returned
    no_of_crops_to_returned = 3

    # crop dimentions
    crop_width = 1000
    crop_height = 600

    # Filters
    filters = ["text"]

    # Image file path
    image_file_path = os.path.join(".", "tests", "data",\
                                "image_for_text.png")

    crop_list = img_module.crop_image(
        file_path=image_file_path,
        crop_width=crop_width,
        crop_height=crop_height,
        num_of_crops=no_of_crops_to_returned,
        filters= filters,
        down_sample_factor=8
    )

    if len(crop_list) > 0:
        top_crop = crop_list[0]
        print("Top Crop", top_crop, " Score", top_crop.score)

        img = cv2.imread(image_file_path)
        img_module.save_crop_to_disk(top_crop, img, 
            file_path=output_folder_cropped_image,
            file_name="cropped_image", 
            file_ext=".jpeg",
        )

        
    else:
        print(
            "No Perfect crop found for {0}x{1} with for Image {2}".format(
                        crop_width, crop_height ,image_file_path
            )
        )
