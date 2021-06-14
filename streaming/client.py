import logging
import sys
import time

import imagezmq
from imutils.video import VideoStream

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("CovIS")


class StreamClient:
    def __init__(self, server_ip, camera_ip):
        self.sender = imagezmq.ImageSender(connect_to=f"tcp://{server_ip}:5555")
        self.camera_ip = camera_ip
        self.sending = False
        self.vs = self._start(camera_ip)

    def stream(self):
        self.sending = True

        try:
            while self.sending:
                frame = self.vs.read()
                self.sender.send_image(self.camera_ip, frame)
        except Exception as err:
            logger.error(err)
            pass

    def stop(self):
        self.sending = False

    def close(self):
        self.vs.stop()
        self.sender.close()

    def _start(self, camera_ip):
        vs = VideoStream(f"rtsp://{camera_ip}:554")
        vs.start()
        time.sleep(2.0)
        return vs
