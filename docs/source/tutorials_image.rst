.. _tutorials_image:

Using Katna.image
========================

Crop a single image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Step 1**

Import the image module.

.. code-block:: python

   from Katna.image import Image

**Step 2**

Instantiate the image class.

.. code-block:: python

     img_module = Image()
   
**Step 3**

Call the **crop_image** method. This method accepts following parameters (Refer to API reference for further details):


**file_path**: image file path from which crop has to be extracted

**crop_width**: width of crop to extract

**crop_height**: height of crop to extract

**no_of_crops_to_return**: number of crops rectangles to be extracted

**writer**: Writer class instance to process image crop data for a file (use ImageCropDiskWriter from Katna.writer module to save data at a location).

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

    # diskwriter to save crop data
    diskwriter = ImageCropDiskWriter(location=<Path to save crops>)

    img_module.crop_image(
        file_path=image_file_path,
        crop_width=<crop_width>,
        crop_height=<crop_height>,
        num_of_crops=<no_of_crops_to_return>,
        writer=diskwriter,
        filters=<filters>,
        down_sample_factor=<number_by_which_image_to_downsample>
    )


Code below is a complete example for a single image.

.. code-block:: python
   :emphasize-lines: 1-3,6,9,12,15-17,20,22-23,26,29-37
   :linenos:

    import os.path
    import cv2
    from Katna.image import Image
    from Katna.writer import ImageCropDiskWriter

    # Extract specific number of key frames from video
    img_module = Image()

    # folder to save extracted images
    output_folder_cropped_image = "selectedcrops"

    # number of images to be returned
    no_of_crops_to_returned = 3

    # crop dimentions
    crop_width = 1100
    crop_height = 600

    # Filters
    filters = ["text"]
    # Image file path
    image_file_path = os.path.join(".", "tests", "data", "bird_img_for_crop.jpg")
    print(f"image_file_path = {image_file_path}")

    # diskwriter to save crop data
    diskwriter = ImageCropDiskWriter(location=output_folder_cropped_image)
    
    # crop the image and process data with diskwriter instance
    img_module.crop_image(
        file_path=image_file_path,
        crop_width=crop_width,
        crop_height=crop_height,
        num_of_crops=no_of_crops_to_returned,
        writer=diskwriter,
        filters=filters,
        down_sample_factor=8
    )


Crop all images in a directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run crop image for all images in a directory, call the **crop_image_from_dir**
method. This method accepts following parameters and returns a dictionary containing file path as key
and list of crop rectangles (in crop_rect data structure) as its values.
Below are the six parameters of the function

**dir_path**: directory path where images from which crop has to be extracted

**crop_width**: width of crop to extract

**crop_height**: height of crop to extract

**no_of_crops_to_return**: number of crops rectangles to be extracted

**writer**: Writer class instance to process image crop data for a file (use ImageCropDiskWriter from Katna.writer module to save data at a location).

**filters**: You can use this **optional** parameter to filter out unwanted crop rectangles according to some filtering criteria.
At the moment only "text" detection filter is implemented and more filters will be added in future
will be added in future. Passing on "text" detection filter ensures crop rectangle contains text, additionally it checks
that detected "text" inside an image is not abruptly cropped by any crop_rectangle.
By default, filters are not applied.

**down_sample_factor**: You can use this **optional** feature to specify the down sampling factor. For large images
consider increasing this parameter for faster image cropping.  By default input images are downsampled by factor of
**8** before processing.

.. code-block:: python

    input_dir_path = <Path to directory where images are stored>

    # diskwriter to save crop data
    diskwriter = ImageCropDiskWriter(location=<Path to save crops>)

    img_module.crop_image_from_dir(
        dir_path=input_dir_path,
        crop_width=<crop_width>,
        crop_height=<crop_height>,
        num_of_crops=<no_of_crops_to_return>,
        writer=diskwriter,
        filters=<filters>,
        down_sample_factor=<number_by_which_image_to_downsample>
     )


Code below is a complete example for a directory containing images.

.. code-block:: python
   :emphasize-lines: 1-4,6,9,12,15-16,19,22,25,27-35
   :linenos:

    import os.path
    import cv2
    import ntpath
    from Katna.image import Image
    from Katna.writer import ImageCropDiskWriter

    img_module = Image()

    # folder to save extracted images
    output_folder_cropped_image = "selectedcrops"

    # number of images to be returned
    no_of_crops_to_return = 3

    # crop dimensions
    crop_width = 300
    crop_height = 400

    # Filters
    filters = ["text"]

    # Directory containing images to be cropped
    input_dir_path = os.path.join(".", "tests", "data")

    # diskwriter to save crop data
    diskwriter = ImageCropDiskWriter(location=output_folder_cropped_image)

    img_module.crop_image_from_dir(
        dir_path=input_dir_path,
        crop_width=crop_width,
        crop_height=crop_height,
        num_of_crops=no_of_crops_to_return,
        writer=diskwriter,
        filters=filters,
        down_sample_factor=8
    )


**Note**: You can create custom writers to process the data in a different way. Check the :ref:`Katna.custom_writers` section for details.


Resize a single image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Step 1**

Import the image module.

.. code-block:: python

   from Katna.image import Image

**Step 2**

Instantiate the image class.

.. code-block:: python

     img_module = Image()
   
**Step 3**

Call the **resize_image** method. This method accepts following parameters and returns a in memory resized image in opencv format.
Refer to API reference for further details. Below are the four parameters of the function

**file_path**: image file path from which crop has to be extracted

**target_width**: width of target image

**target_height**: height of target image

**down_sample_factor**: You can use this **optional** feature to specify the down sampling factor. For large images
consider increasing this parameter for faster image resize and crop.  By default input images are downsampled by factor of 
**8** before processing. 

.. code-block:: python

     image_file_path = <Path where the image is stored>

     crop_list = img_module.resize_image(
        file_path=image_file_path,
        target_width=<target_width>,
        target_height=<target_height>,
        down_sample_factor=<number_by_which_image_to_downsample>
     )


**Step 4**

To save the extracted resized image call **save_image_to_disk** method.
The method accepts following parameters and doesn't returns anything. 
Refer to API reference for further details.

1. **image**: output image to be saved

2. **file_path**: Folder location where files needs to be saved

3. **file_name**:  File name for the crop image to be saved.

4. **file_ext**: File extension indicating the file type for example - ‘.jpg’


.. code-block:: python

     img_module.save_image_to_disk(image=<image>, file_path=<output_folder_cropped_image>,
            file_name=<file_name>, 
            file_ext=<file_ext>,
        )

Code below is a complete example for a single image.

.. code-block:: python
   :emphasize-lines: 1-3,8,17-18,21,24-29,33-38
   :linenos:

    import os.path
    import cv2
    from Katna.image import Image

    def main():

        # Extract specific number of key frames from video
        img_module = Image()

        # folder to save extracted images
        output_folder_cropped_image = "resizedimages"

        if not os.path.isdir(os.path.join(".", output_folder_cropped_image)):
            os.mkdir(os.path.join(".", output_folder_cropped_image))

        # crop dimentions
        resize_width = 500
        resize_height = 600

        # Image file path
        image_file_path = os.path.join(".", "tests", "data", "bird_img_for_crop.jpg")
        print(f"image_file_path = {image_file_path}")

        resized_image = img_module.resize_image(
            file_path=image_file_path,
            target_width=resize_width,
            target_height=resize_height,
            down_sample_factor=8,
        )
        # cv2.imshow("resizedImage", resized_image)
        # cv2.waitKey(0)

        img_module.save_image_to_disk(
            resized_image,
            file_path=output_folder_cropped_image,
            file_name="resized_image",
            file_ext=".jpeg",
        )

    main()


Resize all images in a directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run resize image for all images in a directory, call the **resize_image_from_dir**
method. This method accepts following parameters and returns a dictionary containing file path as key
and resized image (in opencv numpy format) as its values.
Below are the six parameters of the function

**dir_path**: directory path where images from which crop has to be extracted

**target_width**: width of output resized image

**target_height**: height of output resized image

**down_sample_factor**: You can use this **optional** feature to specify the down sampling factor. For large images
consider increasing this parameter for faster image cropping and resizing.  By default input images are downsampled by factor of
**8** before processing.

.. code-block:: python

     input_dir_path = <Path to directory where images are stored>

     crop_list = img_module.resize_image_from_dir(
        dir_path=input_dir_path,
        target_width=<target_width>,
        target_height=<target_height>,
        down_sample_factor=<number_by_which_image_to_downsample>
     )


Code below is a complete example for a directory containing images.

.. code-block:: python
   :emphasize-lines: 1-4,9,18-19,22,25-30,32-39
   :linenos:

    import os.path
    from Katna.image import Image
    import os
    import ntpath


    def main():

        img_module = Image()

        # folder to save resized images
        output_folder_resized_image = "resizedimages"

        if not os.path.isdir(os.path.join(".", output_folder_resized_image)):
            os.mkdir(os.path.join(".", output_folder_resized_image))

        # resized image dimensions
        resize_width = 500
        resize_height = 600

        # Input folder file path
        input_folder_path = os.path.join(".", "tests", "data")
        print(f"input_folder_path = {input_folder_path}")

        resized_images = img_module.resize_image_from_dir(
            dir_path=input_folder_path,
            target_width=resize_width,
            target_height=resize_height,
            down_sample_factor=8,
        )

        for filepath, resized_image in resized_images.items():
            # name of the image file
            filename = ntpath.basename(filepath)
            name = filename.split(".")[0]
            # folder path where the images will be stored
            img_module.save_image_to_disk(
                resized_image, output_folder_resized_image, name + "_resized" + "_", ".jpeg"
            )


    main()


In addition, image module also has some additional features:

1. Crop Image using cv: check :ref:`Katna.image_crop_cv`

2. Crop Image maintaining asepct ratio: check :ref:`Katna.image_crop_aspect_ratio`
