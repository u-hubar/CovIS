import sys

import cv2
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from mainWindow import Ui_MainWindow
from addCameraWindow import Ui_Dialog
from streaming.client import StreamClient
from streaming.server import StreamServer

from my_utils import config


class MainWindow(QMainWindow):
    def __init__(self, camera_ip_addr_list):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.connect_buttons_list = [
            self.ui.pushButton_1, self.ui.pushButton_2, self.ui.pushButton_3,
            self.ui.pushButton_4, self.ui.pushButton_5, self.ui.pushButton_6,
            self.ui.pushButton_7, self.ui.pushButton_8, self.ui.pushButton_9,
        ]

        for connect_button in self.connect_buttons_list:
            connect_button.clicked.connect(self.connect_button_clicked)

        self.worker_server = WorkerServer()
        self.worker_server.start()
        self.worker_server.frame_dict_update.connect(self.image_update_slot)

        self.worker_client_dict = {}
        self.camera_ip_addr_list = camera_ip_addr_list

        if self.camera_ip_addr_list:
            for cammera_ip_addr in camera_ip_addr_list:
                self.worker_client_dict[cammera_ip_addr] = WorkerClient("localhost", cammera_ip_addr)
                self.worker_client_dict[cammera_ip_addr].start()

    def connect_button_clicked(self):
        dialog = AddCameraDialog()
        dialog.exec_()
        dialog.show()
        print(dialog.camera_ip)
        self.camera_ip_addr_list.append(dialog.camera_ip)
        self.worker_client_dict[dialog.camera_ip] = WorkerClient("localhost", dialog.camera_ip)
        self.worker_client_dict[dialog.camera_ip].start()

    def image_update_slot(self, frame_dict):
        frame_dict_list = list(frame_dict.values())
        image_list = []

        for frame in frame_dict_list:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convert_to_qt_format = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
            image = convert_to_qt_format.scaled(640, 480)
            image_list.append(image)

        label_list = [self.ui.label_1, self.ui.label_2, self.ui.label_3,
                      self.ui.label_4, self.ui.label_5, self.ui.label_6,
                      self.ui.label_7, self.ui.label_8, self.ui.label_9]

        for j in range(len(image_list)):
            label_list[j].setPixmap(QPixmap.fromImage(image_list[j]))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        ip_addr_file = open("ip_addr_saved.txt", "w")

        for cammera_ip_addr in self.camera_ip_addr_list[:-1]:
            ip_addr_file.write(cammera_ip_addr + "\n")

        ip_addr_file.write(self.camera_ip_addr_list[-1])


class AddCameraDialog(QDialog):
    def __init__(self):
        super(AddCameraDialog, self).__init__()
        self.camera_ip = ""
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.okPushButton.clicked.connect(self.ok_push_button_clicked)

    def ok_push_button_clicked(self):
        self.camera_ip = self.ui.ipLineEdit.text()
        self.close()


class WorkerServer(QThread):
    frame_dict_update = pyqtSignal(dict)

    def __init__(self, prototxt=config.FACE_DETECTION_PROTOTXT, model=config.FACE_DETECTION_MODEL):
        super(WorkerServer, self).__init__()
        self.prototxt = prototxt
        self.model = model
        self.thread_active = False
        self.server = StreamServer(self.prototxt, self.model)

    def run(self):
        self.thread_active = True

        while self.thread_active:
            while True:
                self.server.stream()
                self.frame_dict_update.emit(self.server.frame_dict)

    def stop(self):
        self.thread_active = False
        self.quit()


class WorkerClient(QThread):
    def __init__(self, server_ip, camera_ip):
        super(WorkerClient, self).__init__()
        self.thread_active = False
        self.stream_client = StreamClient(server_ip, camera_ip)

    def run(self):
        self.thread_active = True

        while self.thread_active:
            self.stream_client.stream()

    def stop(self):
        self.thread_active = False
        self.quit()


class App(QtWidgets.QApplication):
    def __init__(self, *args):
        QtWidgets.QApplication.__init__(self, *args)

        ip_address_file = open("ip_addr_saved.txt")
        ip_address_list = ip_address_file.read().splitlines()

        self.main = MainWindow(ip_address_list)
        self.main.show()

        # self.worker_client_dict = {}
        # self.camera_ip_addr_list = ip_address_list
        #
        # if self.camera_ip_addr_list:
        #     for cammera_ip_addr in ip_address_list:
        #         self.worker_client_dict[cammera_ip_addr] = WorkerClient("localhost", cammera_ip_addr)
        #         self.worker_client_dict[cammera_ip_addr].start()


def main(args):
    # app = QApplication(args)
    # window = MainWindow(ip_address_list)
    # window.show()
    # sys.exit(app.exec_())

    app = App(args)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
