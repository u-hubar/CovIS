import sys

import cv2
import imagezmq
import threading

from queue import Queue

# from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
# from PyQt5.QtGui import QImage, Qt, QPixmap
# from PyQt5.QtCore import *

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from imutils.video import VideoStream

from mainWindow import Ui_MainWindow

from streaming.server import StreamServer

# queue = Queue()
# FRAME_DICT = None


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.worker_server = WorkerServer()
        self.worker_server.start()
        self.worker_server.frame_dict_update.connect(self.image_update_slot)

        # self.worker = Worker()
        # self.worker.start()
        # self.worker.image_update.connect(self.image_update_slot)

        # queue = Queue()
        # self.thread1 = threading.Thread(target=WorkerServer, args=("Thread-1", queue))
        # self.thread2 = threading.Thread(target=QThread, args=("Thread-2", queue))
        # self.thread1.start()
        # self.thread2.start()
        # self.thread2.image_update.connect(self.image_update_slot)

    # def image_update_slot(self, image):

    def image_update_slot(self, frame_dict):
        # print(list(frame_dict.values())[0].shape)
        # print(type((frame_dict.values())[0]))
        print(frame_dict)
        print(type(frame_dict))

        # # print(image)
        # print('test_image_update_slot')
        # # print(frame_dict)
        # # print(class(frame_dict[0]))
        # frame_dict_0 = list(frame_dict.values())[0]
        # image = cv2.cvtColor(frame_dict_0, cv2.COLOR_BGR2RGB)
        # # flipped_image = cv2.flip(image, 1)
        # # convert_to_qt_format = QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0],
        # #                               QImage.Format_RGB888)
        # # image = convert_to_qt_format.scaled(640, 480)
        #
        # convert_to_qt_format = QImage(image.data, image.shape[1], image.shape[0],
        #                               QImage.Format_RGB888)
        # # image = convert_to_qt_format.scaled(640, 480)
        #
        print('test_image_update_slot_2')

        frame = list(frame_dict.values())[0]

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # flipped_image = cv2.flip(image, 1)
        convert_to_qt_format = QImage(image.data, image.shape[1], image.shape[0],
                                      QImage.Format_RGB888)
        image = convert_to_qt_format.scaled(640, 480)

        self.ui.label_1.setPixmap(QPixmap.fromImage(image))
        self.ui.label_2.setPixmap(QPixmap.fromImage(image))
        self.ui.label_3.setPixmap(QPixmap.fromImage(image))
        self.ui.label_4.setPixmap(QPixmap.fromImage(image))
        self.ui.label_5.setPixmap(QPixmap.fromImage(image))
        self.ui.label_6.setPixmap(QPixmap.fromImage(image))
        self.ui.label_7.setPixmap(QPixmap.fromImage(image))
        self.ui.label_8.setPixmap(QPixmap.fromImage(image))
        self.ui.label_9.setPixmap(QPixmap.fromImage(image))
        print('test_image_update_slot_3')


class WorkerServer(QThread):
    frame_dict_update = pyqtSignal(dict)

    def __init__(self):
        super(WorkerServer, self).__init__()
        # threading.Thread.__init__(self)
        self.prototxt = "models/deploy.prototxt"
        self.model = "models/res10_300x300_ssd_iter_140000.caffemodel"
        self.thread_active = False
        self.server = StreamServer(self.prototxt, self.model, 0.1, 2, 2)

    def run(self):
        self.thread_active = True

        while self.thread_active:
            while True:
                print('test')

                # server = StreamServer(self.prototxt, self.model, 0.1, 2, 2)
                print('test2')
                self.server.stream()
                print('test3')
                print(type(self.server.frame_dict))
                self.frame_dict_update.emit(self.server.frame_dict)
                print('test4')

                # FRAME_DICT = server.frame_dict
                # queue.put(server.frame_dict)

    def stop(self):
        self.thread_active = False
        self.quit()


class Worker(QThread):
    image_update = pyqtSignal(QImage)

    def __init__(self):
        super(Worker, self).__init__()
        # threading.Thread.__init__(self)
        self.thread_active = False

    def run(self):
        self.thread_active = True
        capture = cv2.VideoCapture(0)

        # server_ip = "localhost"
        # capture = cv2.VideoCapture(f"tcp://{server_ip}:5555")

        # server_ip = "localhost"
        # stream_client = StreamClient(server_ip)
        # stream_client.stream()
        # capture = stream_client.vs

        # capture = VideoStream().start()
        # global FRAME_DICT
        # print('test')

        while self.thread_active:
            while True:
                # frame_dict = queue.get()
                r, frame = capture.read()
                print(frame.shape)
                print("---")

                if r:
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    flipped_image = cv2.flip(image, 1)
                    convert_to_qt_format = QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0],
                                                  QImage.Format_RGB888)
                    picture = convert_to_qt_format.scaled(640, 480)
                    self.image_update.emit(picture)

    def stop(self):
        self.thread_active = False
        self.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(window)

    window.show()
    sys.exit(app.exec_())
