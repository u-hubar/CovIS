from __future__ import absolute_import

import logging
import sys
from datetime import datetime

import cv2
import imagezmq
import imutils
import numpy as np
from utils_module import config
from face_recognizer.recognizer import FaceRecognizer
from mask_recognizer.recognizer import MaskRecognizer

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("CovIS")


class StreamServer:
    CAMERAS_NUM = 8
    ACTIVE_CHECK_PERIOD = 10
    ACTIVE_CHECK_SECONDS = CAMERAS_NUM * ACTIVE_CHECK_PERIOD

    def __init__(
        self,
        prototxt,
        model,
        confidence=0.6
    ):
        self.face_detector = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.conf_threshold = confidence
        self.face_recognizer = FaceRecognizer()
        self.mask_recognizer = MaskRecognizer(config.MASK_REC_MODEL)
        self.image_hub = imagezmq.ImageHub()
        self.frame_dict = {}
        self.last_active = {}
        self.last_active_check = datetime.now()

    def stream(self, face_recognition=False):
        (cam_name, frame) = self.image_hub.recv_image()
        self.image_hub.send_reply(b"OK")

        if cam_name not in self.last_active.keys():
            logger.info(f"Receiving data from {cam_name}...")
            self.last_active[cam_name] = datetime.now()

        frame = imutils.resize(frame, width=400)
        frame = cv2.flip(frame, 1)
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0),
        )

        self.face_detector.setInput(blob)
        detections = self.face_detector.forward()

        if cam_name not in self.frame_dict.keys():
            self.frame_dict[cam_name] = {}
        self.frame_dict[cam_name]["faces"] = []

        for i in range(len(detections)):
            confidence = detections[0, 0, i, 2]
            if confidence > self.conf_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (start_x, start_y, end_x, end_y) = box.astype("int")
                self.frame_dict[cam_name]["faces"].append(frame[start_y: end_y, start_x: end_x])

        cv2.putText(
            frame,
            cam_name,
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )

        self.frame_dict[cam_name]["frame"] = frame

        if (
            datetime.now() - self.last_active_check
        ).seconds > StreamServer.ACTIVE_CHECK_SECONDS:
            for (cam_name, ts) in list(self.last_active.items()):
                if (
                    datetime.now() - ts
                ).seconds > StreamServer.ACTIVE_CHECK_SECONDS:
                    logger.error(f"Lost connection to {cam_name}")
                    self.last_active.pop(cam_name)
                    self.frame_dict.pop(cam_name)

            self.last_active_check = datetime.now()

    def clean_frame(self, camera_ip):
        self.last_active.pop(camera_ip)
        self.frame_dict.pop(camera_ip)
