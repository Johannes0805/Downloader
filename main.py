import sys
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtGui
from gui import MainWindow
from utils import resource_path

import sys
import traceback

def excepthook(type, value, tb):
    with open("/Users/johannes/Desktop/qt_crash_log.txt", "w") as f:
        traceback.print_exception(type, value, tb, file=f)

sys.excepthook = excepthook

starting_x = 500
starting_y = 400

standard_width = 450
standard_hight = 200

def main():

    app = QApplication(sys.argv)
    win = MainWindow()

    win.setGeometry(starting_x,starting_y,standard_width,standard_hight)
    win.setWindowTitle("Downloader")
    icon = QtGui.QIcon(resource_path("assets/yt_downloader.icns"))
    win.setWindowIcon(icon)

    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()