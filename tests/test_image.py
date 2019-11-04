import sys
import os.path
import pytest
import cv2
import numpy as np
import inspect

LIBDIR = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(os.path.split(LIBDIR)[0], "Katna")
test_path = os.path.join(os.path.split(LIBDIR)[0], "tests")
sys.path.append(modules_path)
sys.path.append(test_path)


def process_images(path, temp_dir, feature, which):

    test_img_ext = ["jpg", "jpeg"]
    i = 0
    method_list = inspect.getmembers(eval("which"))
    for f in os.listdir(path):
        if f.endswith(test_img_ext[0]) or f.endswith(test_img_ext[1]):
            img = cv2.imread(os.path.join(path, f))
            smap = eval("feature." + method_list[-2][0] + "(img)")
            cv2.imwrite(os.path.join(temp_dir, f), smap)
            i += 1
    return i


@pytest.fixture(scope="module")
def image_similarity_object():
    """fixture for image similarity object
    
    Returns:
        Image_Similarity -- an instantiated Image_Similarity object
    """
    from image_similarity import ImageSimilarity

    return ImageSimilarity()


@pytest.fixture(scope="module")
def image_object():
    """fixture for image object
    
    Returns:
        Image -- an instantiated Image object
    """
    from Katna.image import Image

    return Image()


@pytest.fixture(scope="module")
def text_detector_object():
    """fixture for text detection object
    
    Returns:
        TextDetector -- an instantiated Text Detector object
    """
    from Katna.image_filters.text_detector import TextDetector

    return TextDetector()


def test_saliency(tmpdir_factory):
    from Katna.image_features.saliency_feature import SaliencyFeature

    sd = SaliencyFeature()
    path = os.path.join("tests", "data")
    save_path = "saliency_result_images"
    temp_dir = tmpdir_factory.mktemp(save_path)
    no_img_processed = process_images(path, temp_dir, sd, SaliencyFeature)
    assert len(temp_dir.listdir()) == no_img_processed


def test_edge(tmpdir_factory):
    from Katna.image_features.edge_feature import EdgeFeature

    ed = EdgeFeature()
    path = os.path.join("tests", "data")
    save_path = "edge_result_images"
    temp_dir = tmpdir_factory.mktemp(save_path)
    no_img_processed = process_images(path, temp_dir, ed, EdgeFeature)
    assert len(temp_dir.listdir()) == no_img_processed


def test_face(tmpdir_factory):
    from Katna.image_features.face_feature import FaceFeature

    sf = FaceFeature()
    path = os.path.join("tests", "data")
    save_path = "face_result_images"
    temp_dir = tmpdir_factory.mktemp(save_path)
    no_img_processed = process_images(path, temp_dir, sf, FaceFeature)
    assert len(temp_dir.listdir()) == no_img_processed


def test_features_list():
    from Katna.feature_list import FeatureList

    fl = FeatureList()
    assert len(fl.get_features()) == 3


def test_filters_list():
    from Katna.filter_list import FilterList

    fl = FilterList()
    assert len(fl.get_filters()) == 1


def test_text_detector(tmpdir_factory, text_detector_object):

    from Katna.crop_rect import CropRect

    crop1 = CropRect(0, 0, 100, 100)
    crop2 = CropRect(0, 0, 200, 200)
    crop3 = CropRect(0, 0, 1000, 600)
    path = os.path.join("tests", "data")
    save_path = "text_result_image"
    temp_dir = tmpdir_factory.mktemp(save_path)
    text_detector_object.set_image(cv2.imread(os.path.join(path, "image_for_text.png")))
    assert text_detector_object.get_filter_result(crop1) == False
    assert text_detector_object.get_filter_result(crop2) == False
    assert text_detector_object.get_filter_result(crop3) == True


def test_image(image_object):
    import os.path
    import cv2

    # number of images to be returned
    no_of_crops_to_returned = 3

    # crop dimensions
    crop_width = 800
    crop_height = 600

    crop_width1 = 200
    crop_height1 = 200
    # Filters
    filters = ["text"]
    # Image file path
    path = os.path.join("tests", "data")
    image_file_path = os.path.join(path, "test_image_for_text.jpeg")
    print(f"image_file_path = {image_file_path}")

    img = cv2.imread(image_file_path)
    crop_list = image_object.crop_image_from_cvimage(
        input_image=img,
        crop_width=crop_width,
        crop_height=crop_height,
        num_of_crops=no_of_crops_to_returned,
        filters=filters,
    )
    crop_list1 = image_object.crop_image_from_cvimage(
        input_image=img,
        crop_width=crop_width1,
        crop_height=crop_height1,
        num_of_crops=no_of_crops_to_returned,
        filters=filters,
    )
    print(len(crop_list1), len(crop_list))
    assert len(crop_list) == no_of_crops_to_returned
    assert len(crop_list1) == 0


def test_crop_quality(tmpdir_factory, image_object, image_similarity_object):
    import os.path
    import cv2

    # number of images to be returned
    no_of_crops_to_returned = 3

    # crop dimentions
    crop_width = 500
    crop_height = 500

    # Image file path
    path = os.path.join("tests", "data")
    save_path = "result_image_crop"
    temp_dir = tmpdir_factory.mktemp(save_path)
    image_file_path = os.path.join(path, "23018877.jpg")
    print(f"image_file_path = {image_file_path}")

    img = cv2.imread(image_file_path)
    crop_list = image_object.crop_image(
        file_path=image_file_path,
        crop_width=crop_width,
        crop_height=crop_height,
        num_of_crops=no_of_crops_to_returned,
    )
    print(crop_list)
    image_object.save_crop_to_disk(crop_list[0], img, temp_dir, "crop_img", ".jpg")
    similairty = image_similarity_object.pixel_sim(
        os.path.join(path, "23018877_crop.jpg"), os.path.join(temp_dir, "crop_img.jpg")
    )
    print("Similarity: ", similairty)
    assert round(similairty, 1) <= 0.3


def test_validate_image_exception():
    """
        Test case for no file exception.
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    image_file_path = os.path.join(".", "data", "image_1.jpg")

    from decorators import FileDecorators

    @FileDecorators.validate_file_path
    def dummy(file_path):  # Dummy function because we only want to test the decorator
        return True

    with pytest.raises(FileNotFoundError):
        assert FileDecorators.validate_file_path(dummy(file_path=image_file_path))


def test_aspect_ratio(tmpdir_factory, image_object):
    import os.path
    import cv2

    # number of images to be returned
    no_of_crops_to_returned = 3

    # crop aspect ratio
    crop_aspect_ratio = "4:3"
    aspect_ratio = list(map(int, crop_aspect_ratio.split(":")))
    # Filters
    filters = []
    # Image file path
    path = os.path.join("tests", "data")
    save_path = "result_image_crop"
    temp_dir = tmpdir_factory.mktemp(save_path)
    image_file_path = os.path.join(path, "bird_img_for_crop.jpg")
    print(f"image_file_path = {image_file_path}")

    img = cv2.imread(image_file_path)
    crop_list = image_object.crop_image_with_aspect(
        file_path=image_file_path,
        crop_aspect_ratio=crop_aspect_ratio,
        num_of_crops=no_of_crops_to_returned,
        filters=filters,
    )
    ratio = str(aspect_ratio[0] / aspect_ratio[1])
    for crop in crop_list:
        cv2.imwrite(
            os.path.join(temp_dir, "cropped.jpeg"),
            img[crop.y : crop.y + crop.h, crop.x : crop.x + crop.w],
        )
        crop_img = cv2.imread(os.path.join(temp_dir, "cropped.jpeg"))
        value = str(crop_img.shape[1] / crop_img.shape[0])
        print(value[:4], ratio[:4])
        if value[:3] != ratio[:3]:
            assert False
    assert True
