"""Test script for video class
"""
import sys
import os.path
import pytest
import cv2 as cv2
import numpy as np
import scipy
import skimage.transform
import multiprocessing

LIBDIR = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(os.path.split(LIBDIR)[0], "Katna")
test_path = os.path.join(os.path.split(LIBDIR)[0], "tests")
sys.path.append(modules_path)
sys.path.append(test_path)


@pytest.fixture(scope="module")
def video_object():
    """fixture for video object
    
    Returns:
        Video -- an instantiated video object
    """
    from video import Video

    if __name__ == "__main__":
        multiprocessing.set_start_method("spawn")

    return Video()


@pytest.fixture
def image_similarity_object():
    """fixture for video object
    
    Returns:
        Image_Similarity -- an instantiated Image_Similarity object
    """
    from image_similarity import ImageSimilarity

    return ImageSimilarity()


def test_validate_video_exception():
    """
        Test case for no file exception.
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    video_file_path = os.path.join(".", "data", "pos_video1.mp4")

    from decorators import FileDecorators

    @FileDecorators.validate_file_path
    def dummy(file_path):  # Dummy function because we only want to test the decorator
        return True

    with pytest.raises(FileNotFoundError):
        assert FileDecorators.validate_file_path(dummy(file_path=video_file_path))


def test_extracted_frame_numbers(video_object):
    """
        Test case for extracted frame numbers.
        Must return 10 images
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    video_file_path = os.path.join("tests", "data", "pos_video.mp4")
    expected_number_of_images = 10

    imgs = video_object.extract_frames_as_images(
        expected_number_of_images, video_file_path
    )

    assert len(imgs) == expected_number_of_images


def test_extracted_frame_quality(video_object, image_similarity_object):
    """
        Test case for extracted frame numbers.
        Must return similar 12 images as stored in test data 
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    video_file_path = os.path.join("tests", "data", "pos_video.mp4")
    expected_number_of_images = 12

    imgs = video_object.extract_frames_as_images(
        expected_number_of_images, video_file_path
    )

    print("Testing if extracted images are same as stored images inside data folder")

    for count in range(expected_number_of_images):
        test_img_path = os.path.join(
            "tests", "data", "extracted_img_" + str(count) + ".jpeg"
        )
        test_img = cv2.imread(test_img_path)

        image_found = False
        for img in imgs:
            cv2.imwrite("temp.jpeg", img)
            similairty = image_similarity_object.pixel_sim(test_img_path, "temp.jpeg")
            if abs(similairty - 0.0) < 0.01:
                image_found = True
                break

        os.remove("temp.jpeg")
        assert image_found == True


def test_video_splitting(video_object):
    """Test case for splitting logic for videos.. Used tide ad video because of edge case
    """
    large_video_file_path = os.path.join("tests", "data", "Tidead.mp4")
    small_video_file_path = os.path.join("tests", "data", "pos_video.mp4")
    n_clips_large = video_object._split(large_video_file_path)
    n_clips_small = video_object._split(small_video_file_path)
    video_object._remove_clips(n_clips_large)
    video_object._remove_clips(n_clips_small)
    # print(len(n_clips))
    if multiprocessing.cpu_count() > 1:
        assert len(n_clips_large) > 1
    assert len(n_clips_small) == 1


@pytest.mark.skip(reason="no way of currently testing this")
def test_extracted_frame_as_png(video_object):
    """
        Test case for png extraction.
        All returned files must be png.
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    video_file_path = os.path.join(".", "data", "pos_video.mp4")
    expected_number_of_images = 10
    file_type = "png"

    imgs = video_object.extract_frames_as_images(
        expected_number_of_images, video_file_path, file_type
    )

    # All the images must have png extension

    assert False


@pytest.mark.skip(reason="no way of currently testing this")
def test_extracted_frame_as_jpg(video_object):
    """
        Test case for jpg extraction.
        All returned files must be jpg.
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    video_file_path = os.path.join(".", "data", "pos_video.mp4")
    expected_number_of_images = 10

    imgs = video_object.extract_frames_as_images(
        expected_number_of_images, video_file_path
    )

    # All the images must have jpg extension

    assert False


@pytest.mark.skip(reason="no way of currently testing this")
def test_extract_frames_as_numpy(video_object):
    """
        Test case for frame extraction as image.
        Must return 10 images
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    video_file_path = os.path.join(".", "data", "pos_video.mp4")
    expected_number_of_images = 10
    imgs = video_object.extract_frames_as_numpy(
        expected_number_of_images, video_file_path
    )

    # Check that returned images are numpy array

    assert False


def test_save_frame_to_disk_exception(video_object, tmpdir):
    """Test case for exception test while saving extracted image
    
    :param video_object: Video class object
    :type video_object: Video
    """

    img = "Str"  # None numpy array
    folder = tmpdir.mkdir("katna_test_dir")
    with pytest.raises(TypeError):
        assert video_object.save_frame_to_disk(
            img, file_path=folder, file_name="test", file_ext=".jpeg"
        )


def test_save_frame_to_disk(video_object, tmpdir):
    """Test case for saving image extracted frame on disk
    
    :param video_object: Video class object
    :type video_object: Video
    """

    # Save the file to a temporary location
    test_file_name = "save_frame_to_disk_1.jpeg"
    test_file_location = os.path.join(".", "data", test_file_name)
    img = cv2.imread(test_file_location, cv2.IMREAD_UNCHANGED)

    # tempdir is pytest provided fixture for temporary folders
    copy_location = tmpdir.mkdir("katna_test_dir")

    video_object.save_frame_to_disk(
        img, file_path=copy_location, file_name="test", file_ext=".jpeg"
    )

    assert os.path.isfile(os.path.join(copy_location, "test.jpeg")) == True
