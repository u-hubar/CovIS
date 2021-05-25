from imutils.video import VideoStream
import imagezmq
import socket
import time


class StreamClient:
    def __init__(self, server_ip):
        self.sender = imagezmq.ImageSender(
            connect_to=f"tcp://{server_ip}:5555"
        )
        self.cam_name = socket.gethostname()
        self.vs = self._start()

    def stream(self):
        while True:
            frame = self.vs.read()
            self.sender.send_image(self.cam_name, frame)

    def _start(self):
        vs = VideoStream().start()
        time.sleep(2.0)
        return vs
