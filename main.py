import logging
import math
import sys

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets

from streaming.client import StreamClient
from streaming.server import StreamServer
from utils import config

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("CovIS")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(QtWidgets.QMainWindow, self).__init__()
        self.win_width = config.WIDTH
        self.win_height = config.HEIGHT
        self.cameras = config.CAMERAS
        self.cameras_in_row = config.CAMERAS_IN_ROW
        self.setup_ui()

        self.client_workers = {}

        self.worker_server = WorkerServer()
        self.worker_server.start()
        self.worker_server.frame_dict_update.connect(self.image_update_slot)

    def setup_ui(self):
        self.setObjectName("MainWindow")
        self.resize(self.win_width, self.win_height)
        self.setMinimumSize(QtCore.QSize(800, 600))

        self.central_widget = QtWidgets.QWidget(self)
        self.vertical_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)
        self.tab = QtWidgets.QWidget()
        self.tab_2 = QtWidgets.QWidget()
        self.tab_3 = QtWidgets.QWidget()
        self.grid_layout_widget = QtWidgets.QWidget(self.tab)
        self.grid_layout = QtWidgets.QGridLayout(self.grid_layout_widget)

        self.setCentralWidget(self.central_widget)
        self.grid_layout_widget.setGeometry(
            QtCore.QRect(10, 13, self.win_width, self.win_height)
        )
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.setWindowTitle("MainWindow")
        self.tab_widget.addTab(self.tab, "Cameras")
        self.tab_widget.addTab(self.tab_2, "Settings")
        self.tab_widget.addTab(self.tab_3, "Statistics")
        self.tab_widget.setCurrentIndex(0)
        self.vertical_layout.addWidget(self.tab_widget)

        self.status_bar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.cameras_ui = {
            "grid_layout": {},
            "camera": {},
            "push_button": {},
            "label": {},
        }

        for i, (camera_name, camera_info) in enumerate(self.cameras.items()):
            grid_layout = QtWidgets.QGridLayout()

            camera = QtWidgets.QLabel(self.grid_layout_widget)
            camera.setText(camera_name)
            grid_layout.addWidget(camera, 0, 0, 1, 1)
            self.cameras_ui["camera"][camera_name] = camera

            push_button = QtWidgets.QPushButton(self.grid_layout_widget)
            push_button.setObjectName(camera_name)
            push_button.setText("Connect")
            push_button.setStyleSheet("background-color : purple")
            push_button.clicked.connect(self.connect_camera)
            grid_layout.addWidget(push_button, 0, 1, 1, 1)
            self.cameras_ui["push_button"][camera_name] = push_button

            row = (i // self.cameras_in_row) * 2
            col = i - self.cameras_in_row * (
                i // self.cameras_in_row
            )

            label = QtWidgets.QLabel(self.grid_layout_widget)
            label.setLayoutDirection(QtCore.Qt.LeftToRight)
            label.setFrameShape(QtWidgets.QFrame.Box)
            label.setFixedSize(
                int(self.win_width / self.cameras_in_row) - 10,
                int(
                    self.win_height
                    / math.ceil(len(self.cameras) / self.cameras_in_row)
                )
                - 50,
            )
            self.grid_layout.addWidget(label, row + 1, col, 1, 1)
            self.cameras_ui["label"][camera_name] = label

            self.grid_layout.addLayout(grid_layout, row, col, 1, 1)
            self.cameras_ui["grid_layout"][camera_name] = grid_layout

    def connect_camera(self):
        clicked_button = self.sender()
        camera_name = clicked_button.objectName()

        client_worker = WorkerClient(
            "localhost", self.cameras[camera_name]["IP"]
        )
        self.client_workers[camera_name] = client_worker
        self.client_workers[camera_name].start()

    def image_update_slot(self, frame_dict):
        for cam_name, frame in frame_dict.items():
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convert_to_qt_format = QtGui.QImage(
                image.data,
                image.shape[1],
                image.shape[0],
                QtGui.QImage.Format_RGB888,
            )
            image = convert_to_qt_format.scaled(
                self.cameras_ui["label"][cam_name].size()
            )
            self.cameras_ui["label"][cam_name].setPixmap(
                QtGui.QPixmap.fromImage(image)
            )


class WorkerServer(QtCore.QThread):
    frame_dict_update = QtCore.pyqtSignal(dict)

    def __init__(
        self,
        prototxt=config.FACE_DETECTION_PROTOTXT,
        model=config.FACE_DETECTION_MODEL,
    ):
        super(QtCore.QThread, self).__init__()
        self.prototxt = prototxt
        self.model = model
        self.thread_active = False
        self.server = StreamServer(self.prototxt, self.model)

    def run(self):
        self.thread_active = True

        while self.thread_active:
            self.server.stream()
            self.frame_dict_update.emit(self.server.frame_dict)

    def stop(self):
        self.thread_active = False
        self.quit()


class WorkerClient(QtCore.QThread):
    def __init__(self, server_ip, camera_ip):
        super(QtCore.QThread, self).__init__()
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
        self.main = MainWindow()
        self.setStyle("Fusion")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
        palette.setColor(
            QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53)
        )
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(
            QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter()
        )
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.setPalette(palette)
        self.main.show()


def main(args):
    # ip_address_file = open("ip_addr.txt")
    # ip_address_list = ip_address_file.read().splitlines()

    # print("Cameras connected:\n")
    # print(ip_address_list)

    # worker_client_list = []

    # for i in range(len(ip_address_list)):
    #     worker_client_list.append(WorkerClient("localhost", ip_address_list[i]))
    #     worker_client_list[i].start()

    app = App(args)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
