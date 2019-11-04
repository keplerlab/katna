"""
.. module:: tests.image_similarity
    :platform: OS X
    :synopsis: This module is used for comparsion of image 
"""

import warnings
from skimage.measure import compare_ssim
from skimage.transform import resize
from scipy.stats import wasserstein_distance
import scipy
import skimage
import numpy as np
import cv2
import imageio


class ImageSimilarity(object):
    """Class for performing Image similairty comparision between images

  :param object: None
  :type object:
  """

    def __init__(self):

        # specify resized image sizes
        self.height = 2 ** 7
        self.width = 2 ** 7

    def normalize_exposure(self, img):
        """
    Normalize the exposure of an image.
    param img: the input image
    type x: numpy.ndarray
    return: the normalized image
    rtype: numpy.ndarray
    """
        img = img.astype(int)
        hist = self.get_histogram(img)
        # get the sum of vals accumulated by each position in hist
        cdf = np.array([sum(hist[: i + 1]) for i in range(len(hist))])
        # determine the normalization values for each unit of the cdf
        sk = np.uint8(255 * cdf)
        # normalize each position in the output image
        height, width = img.shape
        normalized = np.zeros_like(img)
        for i in range(0, height):
            for j in range(0, width):
                normalized[i, j] = sk[img[i, j]]
        return normalized.astype(int)

    def get_histogram(self, img):
        """
    Get the histogram of an image. For an 8-bit, grayscale image, the
    histogram will be a 256 unit vector in which the nth value indicates
    the percent of the pixels in the image with the given darkness level.
    The histogram's values sum to 1.
    param img: the input image
    type x: numpy.ndarray
    return: the image histogram 
    rtype: numpy.ndarray
    """
        h, w = img.shape
        hist = [0.0] * 256
        for i in range(h):
            for j in range(w):
                hist[img[i, j]] += 1
        return np.array(hist) / (h * w)

    def get_img(self, path, norm_size=True, norm_exposure=False):
        """
    Prepare an image for image processing tasks
    param path: the input image path
    type x: str
    return: the image
    rtype: numpy.ndarray
    """
        # flatten returns a 2d grayscale array
        img = imageio.imread(path, as_gray=True).astype(int)
        # resizing returns float vals 0:255; convert to ints for downstream tasks
        if norm_size:
            img = skimage.transform.resize(
                img, (self.height, self.width), mode="constant", preserve_range=True
            )
        if norm_exposure:
            img = self.normalize_exposure(img)
        return img

    def pixel_sim(self, path_a, path_b):
        """
    Measure the pixel-level similarity between two images
    param path_a: the path to an image file
    type path_a: str
    param path_b: the path to an image file
    type path_b: str
    return: a float {-1:1} that measures structural similaritybetween the input images
    rtype: {float}
    """
        img_a = self.get_img(path_a, norm_exposure=True)
        img_b = self.get_img(path_b, norm_exposure=True)
        return np.sum(np.absolute(img_a - img_b)) / (self.height * self.width) / 255

    def earth_movers_distance(self, path_a, path_b):
        """
    Measure the Earth Mover's distance between two images
    type path_a: str
    param path_b: the path to an image file
    type path_b: str
    return: a float {-1:1} that measures structural similarity between the input images
    rtype: {float}
    """
        img_a = self.get_img(path_a, norm_exposure=True)
        img_b = self.get_img(path_b, norm_exposure=True)
        hist_a = self.get_histogram(img_a)
        hist_b = self.get_histogram(img_b)
        return wasserstein_distance(hist_a, hist_b)

    def structural_sim(self, path_a, path_b):
        """
    Measure the structural similarity between two images
    type path_a: str
    param path_b: the path to an image file
    type path_b: str
    return: a float {-1:1} that measures structural similarity between the input images
    rtype: {float}
    """
        img_a = self.get_img(path_a)
        img_b = self.get_img(path_b)
        sim, diff = compare_ssim(img_a, img_b, full=True)
        return sim

    def sift_sim(self, path_a, path_b):
        """
    Use SIFT features to measure image similarity
    type path_a: str
    param path_b: the path to an image file
    type path_b: str
    return: a float {-1:1} that measures  similarity between the input images
    rtype: {float}
    """
        # initialize the sift feature detector
        orb = cv2.ORB_create()

        # get the images
        img_a = cv2.imread(path_a)
        img_b = cv2.imread(path_b)

        # find the keypoints and descriptors with SIFT
        kp_a, desc_a = orb.detectAndCompute(img_a, None)
        kp_b, desc_b = orb.detectAndCompute(img_b, None)

        # initialize the bruteforce matcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # match.distance is a float between {0:100} - lower means more similar
        matches = bf.match(desc_a, desc_b)
        similar_regions = [i for i in matches if i.distance < 70]
        if len(matches) == 0:
            return 0
        return len(similar_regions) / len(matches)
