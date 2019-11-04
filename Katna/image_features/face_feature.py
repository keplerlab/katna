"""
.. module:: Katana.image_features.face_feature
    :platform: OS X
    :synopsis: This module is for for getting Face detection feature Map from input image
"""

import os
import cv2
import math
import numpy as np
import time
import requests
import imutils
import random


from Katna.image_features.feature import Feature
import Katna.config as config


class FaceFeature(Feature):
    """Class for calculating Face detection feature map from input image \n
    Internal Parameters\n
    model_file : Path for downloading model for face detection\n
    prototxt_file : Path for downloading model description prototxt file\n
    confidence : Face detection confidence threshold value
    """

    def __init__(self, weight=1.0):
        """Constructor for this class does following tasks, if not already downloaded\
        , it first downloads face detector model file and prototxt file from public URL\
        ands save it at USER_HOME/.katna directory, or /tmp/.katna directory.\
        After this initializer code initializes internal parameter: \
        min_confidence (for face detection)
        """
        super().__init__(weight)

        self.model_file = config.FaceFeature.model_file
        self.prototxt_file = config.FaceFeature.prototxt_file
        self.cache_subdir = config.FaceFeature.cache_subdir
        self.confidence = config.FaceFeature.confidence

        try:
            self.network_folder_path = os.path.join(os.path.expanduser("~"), ".katna")
            if not os.access(self.network_folder_path, os.W_OK):
                self.network_folder_path = os.path.join("/tmp", ".katna")
            self.datadir = os.path.join(self.network_folder_path, self.cache_subdir)
            if not os.path.exists(self.datadir):
                os.makedirs(self.datadir)

            self.network_model_file_path = os.path.join(self.datadir, self.model_file)

            self.network_prototxt_file_path = os.path.join(
                self.datadir, self.prototxt_file
            )

            if not os.path.exists(self.network_model_file_path):
                self.download_model()

            if not os.path.exists(self.network_prototxt_file_path):
                self.download_proto()

            # print("model file..." + self.network_prototxt_file_path + " Model file " +  self.network_model_file_path)

            self.net = cv2.dnn.readNetFromCaffe(
                self.network_prototxt_file_path, self.network_model_file_path
            )

        except Exception:
            raise FileNotFoundError(
                self.model_file
                + " or "
                + self.prototxt_file
                + " seems to be missing.\
                 Download the file and specify the full path\
                      while initializing FaceFeature class"
            )

    def download_proto(self):
        """Public function for downloading the network weight from the URL link, to be used for
        face detection functionality. 
        Troubleshooting tip: If you get FileNotFound error during face detector initialization,
        initialize the face detector and call this function directly to download the model file from public URL link.
        """
        # create response object
        link = config.FaceFeature.prototxt_download_link
        r = requests.get(link, stream=True)
        # download started
        print("Downloading model file...")
        # if not os.path.isfile(self.network_file_path) or not os.path.exists(self.network_file_path):
        with open(os.path.join(self.datadir, self.prototxt_file), "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        print("Prototext file downloaded.")

    def download_model(self):
        """Public function for downloading the network weight from the URL link, to be used for
        face detection functionality. 
        Troubleshooting tip: If you get FileNotFound error during face detector initialization,
        initialize the face detector and call this function directly to download the model file from public URL link.
        """
        # create response object
        link = config.FaceFeature.modelfile_download_link
        r = requests.get(link, stream=True)
        # download started
        print("Downloading model file...")
        # if not os.path.isfile(self.network_file_path) or not os.path.exists(self.network_file_path):
        with open(os.path.join(self.datadir, self.model_file), "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        print("Caffe Model file downloaded.")

    def get_feature_map(self, image):
        """Public function for getting Feature map image from Face detection in input Image

        :param image: input image
        :type image: `numpy array`
        :return: single channel opencv numpy image with feature map from Face detection
        :rtype: numpy array
        """

        # frame = imutils.resize(image, width=400)
        # grab the frame dimensions and convert it to a blob
        frame = image.copy()
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )
        # pass the blob through the network and obtain the detections and
        # predictions
        self.net.setInput(blob)
        detections = self.net.forward()
        gray = np.zeros((h, w), dtype=np.uint8)

        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence < self.confidence:
                continue

            # compute the (x, y)-coordinates of the bounding box for the
            # object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # draw the bounding box of the face along with the associated
            # probability
            text = "{:.2f}%".format(confidence * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(gray, (startX, startY), (endX, endY), (120), -1)
            # cv2.putText(gray, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (127), 2)

        return gray
