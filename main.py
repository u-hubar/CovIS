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
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # self.connect_buttons_list = [
        #     self.ui.pushButton_1, self.ui.pushButton_2, self.ui.pushButton_3,
        #     self.ui.pushButton_4, self.ui.pushButton_5, self.ui.pushButton_6,
        #     self.ui.pushButton_7, self.ui.pushButton_8, self.ui.pushButton_9,
        # ]

        # self.label_dict = {
        #     1: self.ui.label_1, 2: self.ui.label_2, 3: self.ui.label_3,
        #     4: self.ui.label_4, 5: self.ui.label_5, 6: self.ui.label_6,
        #     7: self.ui.label_7, 8: self.ui.label_8, 9: self.ui.label_9,
        # }

        self.connect_buttons_dict = {
            1: self.ui.pushButton_1, 2: self.ui.pushButton_2, 3: self.ui.pushButton_3,
            4: self.ui.pushButton_4, 5: self.ui.pushButton_5, 6: self.ui.pushButton_6,
            7: self.ui.pushButton_7, 8: self.ui.pushButton_8, 9: self.ui.pushButton_9,
        }

        # self.disconnect_buttons_list = [
        #     self.ui.disconnect_pushButton_1, self.ui.disconnect_pushButton_2,
        #     self.ui.disconnect_pushButton_3, self.ui.disconnect_pushButton_4,
        #     self.ui.disconnect_pushButton_5, self.ui.disconnect_pushButton_6,
        #     self.ui.disconnect_pushButton_7, self.ui.disconnect_pushButton_8,
        #     self.ui.disconnect_pushButton_9
        # ]

        self.disconnect_buttons_dict = {
            1: self.ui.disconnect_pushButton_1, 2: self.ui.disconnect_pushButton_2,
            3: self.ui.disconnect_pushButton_3, 4: self.ui.disconnect_pushButton_4,
            5: self.ui.disconnect_pushButton_5, 6: self.ui.disconnect_pushButton_6,
            7: self.ui.disconnect_pushButton_7, 8: self.ui.disconnect_pushButton_8,
            9: self.ui.disconnect_pushButton_9
        }

        self.connect_buttons_dict[1].clicked.connect(lambda: self.connect_button_clicked(1))
        self.connect_buttons_dict[2].clicked.connect(lambda: self.connect_button_clicked(2))
        self.connect_buttons_dict[3].clicked.connect(lambda: self.connect_button_clicked(3))
        self.connect_buttons_dict[4].clicked.connect(lambda: self.connect_button_clicked(4))
        self.connect_buttons_dict[5].clicked.connect(lambda: self.connect_button_clicked(5))
        self.connect_buttons_dict[6].clicked.connect(lambda: self.connect_button_clicked(6))
        self.connect_buttons_dict[7].clicked.connect(lambda: self.connect_button_clicked(7))
        self.connect_buttons_dict[8].clicked.connect(lambda: self.connect_button_clicked(8))
        self.connect_buttons_dict[9].clicked.connect(lambda: self.connect_button_clicked(9))

        self.disconnect_buttons_dict[1].clicked.connect(lambda: self.disconnect_button_clicked(1))
        self.disconnect_buttons_dict[2].clicked.connect(lambda: self.disconnect_button_clicked(2))
        self.disconnect_buttons_dict[3].clicked.connect(lambda: self.disconnect_button_clicked(3))
        self.disconnect_buttons_dict[4].clicked.connect(lambda: self.disconnect_button_clicked(4))
        self.disconnect_buttons_dict[5].clicked.connect(lambda: self.disconnect_button_clicked(5))
        self.disconnect_buttons_dict[6].clicked.connect(lambda: self.disconnect_button_clicked(6))
        self.disconnect_buttons_dict[7].clicked.connect(lambda: self.disconnect_button_clicked(7))
        self.disconnect_buttons_dict[8].clicked.connect(lambda: self.disconnect_button_clicked(8))
        self.disconnect_buttons_dict[9].clicked.connect(lambda: self.disconnect_button_clicked(9))

        self.worker_server = WorkerServer()
        self.worker_server.start()
        self.worker_server.frame_dict_update.connect(self.image_update_slot)

        self.worker_client_dict = {}

        ip_address_file = open("ip_addr_saved.txt")
        ip_address_list = ip_address_file.read().splitlines()
        self.ip_address_dict = {}
        i = 1

        for ip_address in ip_address_list:
            self.ip_address_dict[i] = ip_address
            i += 1

        print(self.ip_address_dict)

        if self.ip_address_dict:
            for key, ip_address in self.ip_address_dict.items():
                self.worker_client_dict[key] = \
                    WorkerClient("localhost", self.ip_address_dict[key])
                self.worker_client_dict[key].start()

    def connect_button_clicked(self, button_id):
        print(button_id)
        dialog = AddCameraDialog()
        dialog.exec_()
        dialog.show()

        if dialog.camera_ip:
            print(dialog.camera_ip)
            self.ip_address_dict[button_id] = dialog.camera_ip
            self.worker_client_dict[button_id] = \
                WorkerClient("localhost", self.ip_address_dict[button_id])
            self.worker_client_dict[button_id].start()

    def disconnect_button_clicked(self, button_id):
        if button_id in self.worker_client_dict:
            self.worker_client_dict[button_id].stop()
            del self.worker_client_dict[button_id]
            del self.ip_address_dict[button_id]

            # label_list = [self.ui.label_1, self.ui.label_2, self.ui.label_3,
            #               self.ui.label_4, self.ui.label_5, self.ui.label_6,
            #               self.ui.label_7, self.ui.label_8, self.ui.label_9]
            #
            # for label in label_list:
            #     label.clear()

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
        ip_addr_list = [ip_addr for key, ip_addr in self.ip_address_dict.items()]

        for ip_addr in ip_addr_list:
            ip_addr_file.write(ip_addr + "\n")


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
        self.camera_ip = camera_ip
        self.thread_active = False
        self.stream_client = StreamClient(server_ip, camera_ip)

    def run(self):
        self.thread_active = True

        while self.thread_active:
            ret = self.stream_client.stream()

            if ret == 1:
                print(f"Połączenie z {self.camera_ip} zostało zerwane")
                self.thread_active = False

    def stop(self):
        self.thread_active = False
        self.stream_client.stop_streaming()
        self.quit()


class App(QtWidgets.QApplication):
    def __init__(self, *args):
        QtWidgets.QApplication.__init__(self, *args)

        # ip_address_file = open("ip_addr_saved.txt")
        # ip_address_list = ip_address_file.read().splitlines()

        self.main = MainWindow()

        self.setStyle("Fusion")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.setPalette(palette)

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
