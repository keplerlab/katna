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


@pytest.fixture(scope="module")
def writer_object():
    """Writer for keyframe extraction

    :return: Writer instance
    :rtype: [type]
    """
    from writer import KeyFrameDiskWriter

    class TestWriterVideo(KeyFrameDiskWriter):

        def __init__(self, location, file_ext=".jpeg"):
            """[summary]

            :param location: [description]
            :type location: [type]
            """
            super().__init__(location, file_ext)

            # dict of formate { filepath: keyframes }
            self.data = {}

        def write(self, filepath, keyframes):
            """Saves keyframes in a dict rather than saving it to disk.

            :param filepath: [description]
            :type filepath: [type]
            :param keyframes: [description]
            :type keyframes: [type]
            :return: [description]
            :rtype: [type]
            """
            self.data = {
                filepath : keyframes
            }

        def get_data(self, filepath):
            """Retreives keyframe data for filepath

            :param filepath: [description]
            :type filepath: [type]
            :return: [description]
            :rtype: [type]
            """
            if filepath in self.data.keys():
                return self.data[filepath]
            else:
                raise Exception("File not found in writer data")
    
    return TestWriterVideo(location="selectedframes")


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


def test_extracted_frame_numbers(video_object, writer_object):
    """
        Test case for extracted frame numbers.
        Must return 10 images
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    video_file_path = os.path.join("tests", "data", "pos_video.mp4")
    expected_number_of_images = 10

    video_object.extract_video_keyframes(
        expected_number_of_images, video_file_path, writer_object
    )

    keyframes = writer_object.get_data(video_file_path)

    assert len(keyframes) == expected_number_of_images


def test_extracted_frame_quality(video_object, image_similarity_object, writer_object):
    """
        Test case for extracted frame numbers.
        Must return similar 12 images as stored in test data 
    """
    # Use following line to print anything from test function inside
    # with capsys.disabled():
    video_file_path = os.path.join("tests", "data", "pos_video.mp4")
    expected_number_of_images = 12

    video_object.extract_video_keyframes(
        expected_number_of_images, video_file_path, writer_object
    )

    print("Testing if extracted images are same as stored images inside data folder")

    imgs = writer_object.get_data(video_file_path)

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

def test_video_no_codec_video(video_object, writer_object):
    """Test case for splitting logic for videos.. Used tide ad video because of edge case
    """
    small_video_file_path = os.path.join("tests", "data", "codec_error_video.mp4")

    video_object.extract_video_keyframes(
        12, small_video_file_path, writer_object
    )

    imgs = writer_object.get_data(small_video_file_path)
    
    #print(len(n_clips_small))
    assert len(imgs) == 11


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

    imgs = video_object.extract_video_keyframes(
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

    imgs = video_object.extract_video_keyframes(
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
    test_file_name = "23018877.jpg"
    test_file_location = os.path.join("tests", "data", test_file_name)
    img = cv2.imread(test_file_location, cv2.IMREAD_UNCHANGED)
    # tempdir is pytest provided fixture for temporary folders
    copy_location = tmpdir.mkdir("katna_test_dir")

    video_object.save_frame_to_disk(
        img, file_path=copy_location, file_name="test", file_ext=".jpeg"
    )

    assert os.path.isfile(os.path.join(copy_location, "test.jpeg")) == True
