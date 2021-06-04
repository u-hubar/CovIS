import time

import imagezmq
from imutils.video import VideoStream


class StreamClient:
    def __init__(self, server_ip, camera_ip):
        self.sender = imagezmq.ImageSender(connect_to=f"tcp://{server_ip}:5555")
        self.camera_ip = camera_ip
        self.vs = self._start(camera_ip)

    def stream(self):
        while True:
            frame = self.vs.read()
            self.sender.send_image(self.camera_ip, frame)

    def _start(self, camera_ip):
        vs = VideoStream(f"rtsp://{camera_ip}:554").start()
        time.sleep(2.0)
        return vs
