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
        confidence,
        montage_width=4,
        montage_height=2,
    ):
        self.model = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.conf_threshold = confidence
        self.montage_width = montage_width
        self.montage_height = montage_height
        self.image_hub = imagezmq.ImageHub()
        self.frame_dict = {}
        self.last_active = {}
        self.last_active_check = datetime.now()

    def stream(self):
        while True:
            (cam_name, frame) = self.image_hub.recv_image()
            self.image_hub.send_reply(b"OK")

            if cam_name not in self.last_active.keys():
                logger.info(f"Receiving data from {cam_name}...")
                self.last_active[cam_name] = datetime.now()

            frame = imutils.resize(frame, width=400)
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5
            )

            self.model.setInput(blob)
            detections = self.model.forward()

            for i in range(len(detections)):
                confidence = detections[0, 0, i, 2]
                if confidence > self.conf_threshold:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    cv2.rectangle(
                        frame, (startX, startY), (endX, endY), (255, 0, 0), 2
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
            montages = imutils.build_montages(
                self.frame_dict.values(),
                (w, h),
                (self.montage_width, self.montage_height),
            )

            for i, montage in enumerate(montages):
                cv2.imshow(f"CovIS Camera ({i})", montage)

            key = cv2.waitKey(1) & 0xFF

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

            if key == ord("q"):
                break

    def _cleanup(self):
        cv2.destroyAllWindows()
