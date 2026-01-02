from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtBoundSignal
from PyQt6 import QtWidgets, uic, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

from main import *

import threading

starting_x = 500
starting_y = 400

standard_width = 450
standard_hight = 200


class DownloadWorker(QObject):
    def __init__(self, link, filetype, folderpath, cookies, returnlist):

        super().__init__()
        self.finished = pyqtBoundSignal()
        self.progress = pyqtBoundSignal(int)

        self.link = link
        self.filetype = filetype
        self.folderpath = folderpath
        self.cookies = cookies
        self.returnlist = returnlist

    def run(self):
        self.progress.emit(10)
        self.returnlist.append(download_single(self.link, self.filetype, self.folderpath, self.cookies))
        self.progress.emit(100)
        self.finished.emit()
        #self.progress_view.editmeta_push.setEnabled(True)


class StartView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("start_widget.ui", self)

        self.open_dialog.clicked.connect(self.select_dir)

    # Opens the filewindow and saves the selection in the QTextEdit

    def select_dir(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Speicherordner auswählen"
        )
        self.filepath_input.setText(folder)

    def get_cleaned_dir(self):
        input = self.filepath_input.text()
        if input:
            if input[-1] == "/":
                return input
            else:
                return input + "/"
        return ""

class ProgressView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("progress_widget.ui", self)

    def edit(self):
        pass


class EditView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("editmeta_widget.ui", self)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.filepath_list = []
        self.thumbpath_list = []
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initiieren der verschiedenen Views
        self.start_view = StartView()
        self.progress_view = ProgressView()
        self.edit_view = EditView()

        # Einfügen der Views auf den Stack
        self.start_view_index = self.stack.addWidget(self.start_view)
        self.progress_view_index = self.stack.addWidget(self.progress_view)
        self.edit_view_index = self.stack.addWidget(self.edit_view)

        self.start_view.start_download.clicked.connect(self.download_v)
        self.progress_view.editmeta_push.setEnabled(False)
        self.progress_view.editmeta_push.clicked.connect(self.edit_v)
        self.edit_view.apply_push.clicked.connect(self.edit_s)
        self.edit_view.scene = QtWidgets.QGraphicsScene(self)
        self.edit_view.graphicsView.setScene(self.edit_view.scene)

    def show_image(self, filepath):
        pixmap = QtGui.QPixmap(filepath)
        self.edit_view.scene.clear()
        self.edit_view.pixmap_item = self.edit_view.scene.addPixmap(pixmap)
        self.edit_view.graphicsView.fitInView(self.edit_view.pixmap_item, QtCore.Qt.AspectRatioMode.KeepAspectRatio)


    def download_v(self):
        #def threaded_download_single(link, filetype, folderpath, cookies, returnlist):
         #   returnlist.append(download_single(link, filetype, folderpath, cookies))
          #  self.progress_view.editmeta_push.setEnabled(True)


        self.stack.setCurrentIndex(self.progress_view_index)

        # Gathering all information from the ui
        url = self.start_view.link_input.text()
        playlist = self.start_view.playlist_radio.isChecked()
        filetype = "audio" if self.start_view.audio_checkbox.isChecked() else "video"

        folderpath = self.start_view.get_cleaned_dir()
        cookies = None  # TODO


        # Downloading using main.py
        if not playlist:
            print("Downloading single")

            self.dworker = DownloadWorker(url, filetype, folderpath, cookies, self.filepath_list)

            self.dthread = QThread()

            self.dworker.moveToThread(self.dthread)
            self.dthread.started.connect(self.dworker.run)
            self.dworker.finished.connect(self.dthread.quit)
            self.dworker.finished.connect(self.dworker.deleteLater)
            self.dthread.finished.connect(self.dthread.deleteLater)
            self.dworker.progress.connect(lambda x: self.progress_view.progressBar.setValue(x))

            self.dthread.start()
            #t = threading.Thread(target=threaded_download_single, args=(url, filetype, folderpath, cookies, self.filepath_list))
            #t.start()

    def edit_v(self):
        def threaded_download_thumbnail(link, return_list):

            return_list.append(download_thumbnail(link))
            crop_to_square(return_list[0])
            #print(return_list[0])

            self.show_image(return_list[0])


        self.setGeometry(starting_x-100,starting_y-75,standard_width + 200,standard_hight + 150)
        self.stack.setCurrentIndex(self.edit_view_index)

        filetype = "audio" if self.start_view.audio_checkbox.isChecked() else "video"
        url = self.start_view.link_input.text()

        thumbpath = None
        if filetype == "audio":

            d = threading.Thread(target=threaded_download_thumbnail, args=(url, self.thumbpath_list))
            d.start()

            print(self.filepath_list[0])
            meta = get_meta(self.filepath_list[0])

            self.edit_view.artist_input.setText(meta["TPE1"][0][0])
            #self.edit_view.album_input.setText("")
            self.edit_view.rdate_input.setText(str(meta["TDRC"][0][0]))
            #self.edit_view.genre_input.setText(meta["TPE1"][0][0])
            self.edit_view.title_input.setText(meta["TIT2"][0][0])
            self.stack.setCurrentWidget(self.edit_view)

    def edit_s(self):
        artist = self.edit_view.artist_input.text()
        album = self.edit_view.album_input.text()
        date = self.edit_view.rdate_input.text()
        genre = self.edit_view.genre_input.text()
        title = self.edit_view.title_input.text()
        filepath = self.filepath_list[0]
        thumbpath = self.thumbpath_list[0]
        edit_metadata(filepath,artist,album,date,genre,title,0,thumbpath)
        delete_file(thumbpath)
        exit(0)

def run():
    app = QApplication(sys.argv)
    win = MainWindow()

    win.setGeometry(starting_x,starting_y,standard_width,standard_hight)
    win.setWindowTitle("Downloader")
    icon = QtGui.QIcon("icon_downloader.png")
    win.setWindowIcon(icon)

    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    run()