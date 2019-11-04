"""
.. module:: Katna.image_filters.text_detector
    :platform: OS X
    :synopsis: This module is implementation of text detector filter
"""

import os
import cv2
import numpy as np
import time
import requests
import random
from imutils.object_detection import non_max_suppression
from Katna.image_filters.filter import Filter
import Katna.config as config


class TextDetector(Filter):
    """TextDetector Class: Class for implementation of text detector filter, inherit from Filter class
    """

    def __init__(self, weight=1.0):
        """Constructor for this class does following tasks, if not already downloaded\
        , it first downloads text detector dnn weights file from public URL\
        ands save it at USER_HOME/.katna directory, or /tmp/.katna directory.\
        After this initializer code initializes internal parameter: \
        min_confidence (for text detection)
        """
        super().__init__(weight)
        self.min_confidence = config.TextDetector.min_confidence
        self.merge_threshold = config.TextDetector.merge_threshold
        self.layerNames = config.TextDetector.layerNames
        self.frozen_weights = config.TextDetector.frozen_weights
        self.cache_subdir = config.TextDetector.cache_subdir

        try:
            self.network_folder_path = os.path.join(os.path.expanduser("~"), ".katna")
            if not os.access(self.network_folder_path, os.W_OK):
                self.network_folder_path = os.path.join("/tmp", ".katna")
            self.datadir = os.path.join(self.network_folder_path, self.cache_subdir)
            if not os.path.exists(self.datadir):
                os.makedirs(self.datadir)

            self.network_file_path = os.path.join(self.datadir, self.frozen_weights)
            if not os.path.exists(self.network_file_path):
                self.download_data()

            self.net = cv2.dnn.readNet(self.network_file_path)

        except Exception:
            raise FileNotFoundError(
                self.frozen_weights
                + " seems to be missing.\
                 Download the file and specify the full path\
                      while initializing TextDetector class"
            )

    def download_data(self):
        """Public function for downloading the network weight from the URL link, to be used for
        text detection functionality. 
        Troubleshooting tip: If you get FileNotFound error during text detector initialization,
        initialize the text detector and call this function directly to download the model file from public URL link.
        """
        # create response object
        link = config.TextDetector.model_download_link
        r = requests.get(link, stream=True)
        # download started
        print("Downloading model file...")
        # if not os.path.isfile(self.network_file_path) or not os.path.exists(self.network_file_path):
        with open(os.path.join(self.datadir, self.frozen_weights), "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        print("Model file downloaded.")

    def __decode_predictions(self, scores, geometry):
        """Internal Function for getting bounding box and confidence values 
        from text detector dnn network output (scores, geometry)
        function takes the number of rows and columns from the scores volume, then
        initializes set of bounding box rectangles and corresponding confidence scores
        """
        (numRows, numCols) = scores.shape[2:4]
        rects = []
        confidences = []

        # loop over the number of rows
        for y in range(0, numRows):
            # extract the scores (probabilities), followed by the
            # geometrical data used to derive potential bounding box
            # coordinates that surround text
            scoresData = scores[0, 0, y]
            xData0 = geometry[0, 0, y]
            xData1 = geometry[0, 1, y]
            xData2 = geometry[0, 2, y]
            xData3 = geometry[0, 3, y]
            anglesData = geometry[0, 4, y]

            # loop over the number of columns
            for x in range(0, numCols):
                # if our score does not have sufficient probability,
                # ignore it
                if scoresData[x] < self.min_confidence:
                    continue

                # compute the offset factor as our resulting feature
                # maps will be 4x smaller than the input image
                (offsetX, offsetY) = (x * 4.0, y * 4.0)

                # extract the rotation angle for the prediction and
                # then compute the sin and cosine
                angle = anglesData[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                # use the geometry volume to derive the width and height
                # of the bounding box
                h = xData0[x] + xData2[x]
                w = xData1[x] + xData3[x]

                # compute both the starting and ending (x, y)-coordinates
                # for the text prediction bounding box
                endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                startX = int(endX - w)
                startY = int(endY - h)

                # add the bounding box coordinates and probability score
                # to our respective lists
                rects.append((startX, startY, endX, endY))
                confidences.append(scoresData[x])

        # return a tuple of the bounding boxes and associated confidences
        return (rects, confidences)

    def __merge_boxes(self, rects):
        """main function to detect text boxes from image

        :param rects: list of 
        :type rects: numpy array
        :param rectsUsed: image file in numpy array/opencv format
        :type rectsUsed: numpy array

        :return: output image with the list of text boxes
        :rtype: file, list
        """

        def grouper(iterable, interval=2):
            prev = None
            group = []
            for item in iterable:
                if not prev or abs(item[1] - prev[1]) <= interval:
                    group.append(item)
                else:
                    yield group
                    group = [item]
                prev = item
            if group:
                yield group

        rects_used = []
        heights = list()
        for bbox in rects:
            heights.append(bbox[3] - bbox[1])
        heights = sorted(heights)  # Sort heights
        median_height = heights[len(heights) // 2] / 2  # Find half of the median height

        bboxes_list = sorted(
            rects, key=lambda k: k[1]
        )  # Sort the bounding boxes based on y1 coordinate ( y of the left-top coordinate )
        combined_bboxes = grouper(
            bboxes_list, median_height
        )  # Group the bounding boxes
        for group in combined_bboxes:
            x_min = min(group, key=lambda k: k[0])[0]  # Find min of x1
            x_max = max(group, key=lambda k: k[2])[2]  # Find max of x2
            y_min = min(group, key=lambda k: k[1])[1]  # Find min of y1
            y_max = max(group, key=lambda k: k[3])[3]  # Find max of y2
            rects_used.append([x_min, y_min, x_max, y_max])
        return rects_used

    def __detect_text(self):
        """Internal function to detect text bounding boxes from input image.
        Returns list of bounding boxes of each detected text field in input image.

        :param image: image file in numpy array/opencv format
        :type image: numpy array
        :param output_image: image file in numpy array/opencv format
        :type output_image: numpy array

        :return: output image with the list of text boxes
        :rtype: file, list
        """
        (H, W) = self.image.shape[:2]
        rW = W / 320
        rH = H / 320
        image = cv2.resize(self.image, (320, 320))
        (H, W) = image.shape[:2]

        # construct a blob from the image and then perform a forward pass of
        # the model to obtain the two output layer sets
        blob = cv2.dnn.blobFromImage(
            self.image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False
        )

        self.net.setInput(blob)
        (scores, geometry) = self.net.forward(self.layerNames)

        rects, confidences = self.__decode_predictions(scores, geometry)
        # apply non-maxima suppression to suppress weak, overlapping bounding
        # boxes
        boxes = non_max_suppression(np.array(rects), probs=confidences)
        text_rects = []
        # loop over the bounding boxes
        for (startX, startY, endX, endY) in boxes:
            # scale the bounding box coordinates based on the respective
            # ratios

            startX = int(startX * rW)
            startY = int(startY * rH)
            endX = int(endX * rW)
            endY = int(endY * rH)
            cv2.rectangle(self.image, (startX, startY), (endX, endY), (0, 0, 255), 3)
            text_rects.append([startX, startY, endX, endY])

        text_rects = sorted(text_rects, key=lambda item: item[0])
        final_rects = text_rects
        if len(text_rects) > 0:
            final_rects = self.__merge_boxes(text_rects)

        return final_rects

    def set_image(self, image):
        """Public set_image function, This will detect all text boxes in input image and
        will saves them as internal list of text_rect to be used in get_filter_result

        :param image: input image from which needs to be cropped
        :type image: numpy array(opencv)
        """
        if image is None:
            return None
        self.image = image
        self.text_rects = self.__detect_text()

    def get_filter_result(self, crop):
        """Main public function of TextDetector filter class,
        this filter Returns false if crop contains no text, additionally
        checks for overlap between input crop rectangle and the detected
        text bounding box, returns True if No overlap (Filter will not discard input crop)
        otherwise returns False (signal for discarding input crop).
        
        :param crop: input crop rectangle to test
        :type crop: crop_rect
        :return: True if No overlap (Filter will not discard input crop) otherwise returns False 
        :rtype: bool
        """
        # rect: xs,ys,xe,ye
        # crop: x,y,w,h
        if self.text_rects is None or len(self.text_rects) == 0:
            return True

        for rect in self.text_rects:
            if not (
                (rect[2]) <= (crop.x + crop.w)
                and (rect[0]) >= (crop.x)
                and (rect[1]) >= (crop.y)
                and (rect[3]) <= (crop.y + crop.h)
            ):
                return False
            else:
                return True

        return True
