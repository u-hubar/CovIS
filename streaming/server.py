import logging
import sys
from datetime import datetime

import cv2
import imagezmq
import imutils
import numpy as np

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
        confidence=0.1
    ):
        self.model = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.conf_threshold = confidence
        self.image_hub = imagezmq.ImageHub()
        self.frame_dict = {}
        self.last_active = {}
        self.last_active_check = datetime.now()

    def stream(self):
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

        self.model.setInput(blob)
        detections = self.model.forward()

        for i in range(len(detections)):
            confidence = detections[0, 0, i, 2]
            if confidence > self.conf_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (start_x, start_y, end_x, end_y) = box.astype("int")
                cv2.rectangle(
                    frame,
                    (start_x, start_y),
                    (end_x, end_y),
                    (255, 0, 0),
                    2,
                )

        cv2.putText(
            frame,
            cam_name,
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )

        self.frame_dict[cam_name] = frame

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

    def _cleanup(self):
        cv2.destroyAllWindows()
