import sys

import cv2
# from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
# from PyQt5.QtGui import QImage, Qt, QPixmap
# from PyQt5.QtCore import *

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from mainWindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.worker = Worker()
        self.worker.start()
        self.worker.image_update.connect(self.image_update_slot)

    def image_update_slot(self, image):
        self.ui.label_2.setPixmap(QPixmap.fromImage(image))
        self.ui.label_3.setPixmap(QPixmap.fromImage(image))
        self.ui.label_4.setPixmap(QPixmap.fromImage(image))
        self.ui.label_5.setPixmap(QPixmap.fromImage(image))
        self.ui.label_6.setPixmap(QPixmap.fromImage(image))
        self.ui.label_7.setPixmap(QPixmap.fromImage(image))
        self.ui.label_8.setPixmap(QPixmap.fromImage(image))
        self.ui.label_9.setPixmap(QPixmap.fromImage(image))
        self.ui.label_10.setPixmap(QPixmap.fromImage(image))


class Worker(QThread):
    image_update = pyqtSignal(QImage)

    def __init__(self):
        super(Worker, self).__init__()
        self.thread_active = False

    def run(self):
        self.thread_active = True
        capture = cv2.VideoCapture(0)

        while self.thread_active:
            r, frame = capture.read()

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
