import logging
from os import minor
import sys

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import math
from database.db import CovisDB
import datetime
from random import randrange
import numpy as np


import random
import matplotlib 
matplotlib.use('Qt5Agg')
  
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("CovIS")


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, width=1800, height=900, cameras_in_row=3):
        super(QtWidgets.QMainWindow, self).__init__()
        self.id = 0

        self.win_width = width
        self.win_height = height
        self.setup_ui(cameras_in_row)

    def setup_ui(self, cameras_in_row):
        self.setObjectName("MainWindow")
        self.resize(self.win_width, self.win_height)
        self.setMinimumSize(QtCore.QSize(800, 600))

        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tab = QtWidgets.QWidget()
        self.tab_2 = QtWidgets.QWidget()
        self.tab_3 = QtWidgets.QWidget()

        self.gridLayoutWidget = QtWidgets.QWidget(self.tab)
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)

        self.setCentralWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 13, self.win_width, self.win_height))
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.setWindowTitle("MainWindow")
        self.tabWidget.addTab(self.tab, "")
        self.tabWidget.addTab(self.tab_2, "")
        self.tabWidget.addTab(self.tab_3, "")

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "Cameras")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), "Settings")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), "Stats")

        self.tabWidget.setCurrentIndex(0)
        self.verticalLayout.addWidget(self.tabWidget)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

    #TAB 3 STATS

        self.gridLayoutWidget1 = QtWidgets.QWidget(self.tab_3)
        self.gridLayout1 = QtWidgets.QGridLayout(self.gridLayoutWidget1)

        print(self.win_height)

        self.myFig = MplCanvas(self, width=18, height=8, dpi=100)
        self.gridLayout1.addWidget(self.myFig)

        data = DataPlot()
        a = datetime.time(self.id,0,0)
        data.insert_persons(f"{self.id}",a)
        self.id = self.id+1


        self.update_plot()
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        
        self.timer.timeout.connect(self.insert_db)

        self.timer.timeout.connect(self.update_plot)

        self.timer.start()

    #####
        self.cameras_ui = {
            "grid_layout": {},
            "camera": {},
            "push_button": {},
            "label": {},
        }

    def insert_db(self):
        data = DataPlot()

        res = data.get_data()
        time = [el[1].strftime("%H:%M:%S") for el in res]
        count = [el[0] for el in res]
        time, count = zip(*sorted(zip(time, count)))

        count =list(count)

        i = randrange(2)
        value = randrange(3)
        
        if i == 1:
            for l in range(value):
                data.insert_persons(self.id+100+l, time[-1])
        
        append = data.get_data()
        max_time = max(append)[1]
        insert = max_time.strftime("%H:%M:%S").split(":")

        if int(insert[1])<45:
            insert_1 = datetime.time(int(insert[0]),int(insert[1])+10,int(insert[2]))
        else:
            insert_1 = datetime.time(int(insert[0])+1,0,0)

        self.id = self.id + 1

        data.insert_persons(self.id,insert_1)

    def update_plot(self):

        data = DataPlot()

        res = data.get_data()
        time = [el[1].strftime("%H:%M:%S") for el in res]
        count = [el[0] for el in res]
        time, count = zip(*sorted(zip(time, count)))

        count =list(count)

        self.xdata = time
        self.ydata = count

        self.myFig.axes.cla() 
        self.myFig.axes.plot(self.xdata, self.ydata, 'r')
        self.myFig.axes.set_xlabel('Time')
        self.myFig.axes.set_ylabel('Number of people')                
        rect_in = self.myFig.axes.patch
        rect_in.set_facecolor((0.1,0.1,0.1))
        self.myFig.axes.tick_params(axis='x', colors='white')
        self.myFig.axes.tick_params(axis='y', colors='white')
        self.myFig.axes.xaxis.label.set_color('white')
        self.myFig.axes.yaxis.label.set_color('white')

        self.myFig.axes.grid(True, linewidth=0.1, color='white', linestyle='-')
        # self.gridLayoutWidget1.move(int(self.win_width/10000), int(self.win_height/12))
        self.gridLayoutWidget1.move(0, int(self.win_height/12))

        self.myFig.draw()

class MplCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=10, height=10, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)
        self.axes.grid()
        rect = fig.patch
        rect.set_facecolor((0.30, 0.30, 0.30))

        super(MplCanvas, self).__init__(fig)

class DataPlot(CovisDB):

    def __init__(self):
        super().__init__()

    def get_data(self):

        res = self.get_num_entrances()
        return res


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

    app = App(args)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
