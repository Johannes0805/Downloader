from PyQt6.QtCore import QThread, QObject, pyqtSignal
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
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    ready = pyqtSignal(bool)

    def __init__(self, linklist, filetype, folderpath, cookies, returnlist, playlist):

        super().__init__()

        self.linklist = linklist
        self.filetype = filetype
        self.folderpath = folderpath
        self.cookies = cookies
        self.returnlist = returnlist
        #self.playlist = playlist



    def run(self):
        # Updating the status bar with fake values
        self.progress.emit(0)

        #if self.playlist:
         #   self.linklist = get_playlist(self.link)
          #  counter = 0
           # for l in self.linklist:
            #    counter += 1
             #   self.returnlist.append(download_single(l, self.filetype, self.folderpath, self.cookies))
              #  self.progress.emit((counter/len(self.returnlist)) * 100)
               # print(self.returnlist)
        #else:
            # Starting download and saving the filepath in returnlist
         #   self.returnlist.append(download_single(self.link, self.filetype, self.folderpath, self.cookies))
        counter = 0
        for l in self.linklist:
            counter += 1
            self.returnlist.append(download_single(l, self.filetype, self.folderpath, self.cookies))
            self.progress.emit(int((counter/len(self.linklist)) * 100))
            print(int((counter/len(self.linklist)) * 100))
            print(self.returnlist)

        # Emit signal to set the status bar to finished, close the thread and worker and enable buttons
        self.progress.emit(100)
        self.finished.emit()
        self.ready.emit(True)

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

    # Function to ensure that the filepath passed has a proper format
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


class EditView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.apply_push = None
        uic.loadUi("editmeta_widget.ui", self)

class BulkEditView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("bulk_edit_widget.ui", self)

class MainWindow(QtWidgets.QMainWindow):
    thumbnail_ready = pyqtSignal(str)
    thumbnail_loaded = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        # Necessary to save the return of threads
        self.link_list = []
        self.filepath_list = []
        self.thumbpath_list = []
        self.playlist_index = 0

        self.thumbnail_ready.connect(self.show_image_playlist)


        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initiating all the Views
        self.start_view = StartView()
        self.progress_view = ProgressView()
        self.edit_view = EditView()
        self.bulk_edit_view = BulkEditView()

        # Adding the views to the stack
        self.start_view_index = self.stack.addWidget(self.start_view)
        self.progress_view_index = self.stack.addWidget(self.progress_view)
        self.edit_view_index = self.stack.addWidget(self.edit_view)
        self.bulk_edit_view_index = self.stack.addWidget(self.bulk_edit_view)

        # Connecting buttons and setting properties
        self.start_view.start_download.clicked.connect(self.download_v)

        self.progress_view.editmeta_push.setEnabled(False)
        self.progress_view.quit_push.setEnabled(False)
        self.progress_view.repeat_push.setEnabled(False)

        self.progress_view.quit_push.clicked.connect(self.save_q)


        self.progress_view.editmeta_push.clicked.connect(self.edit_v)

        self.progress_view.repeat_push.clicked.connect(self.repeat_d)


        self.edit_view.apply_push.clicked.connect(self.edit_save)
        self.edit_view.repeat_push.clicked.connect(self.repeat_d)
        self.edit_view.scene = QtWidgets.QGraphicsScene(self)
        self.edit_view.graphicsView.setScene(self.edit_view.scene)


        self.bulk_edit_view.scene = QtWidgets.QGraphicsScene(self)
        self.bulk_edit_view.cover_view.setScene(self.bulk_edit_view.scene)
        self.bulk_edit_view.previous_push.clicked.connect(self.edit_prev)
        self.bulk_edit_view.next_push.clicked.connect(self.edit_next)
        self.bulk_edit_view.save_push.clicked.connect(self.bulk_save_quit)

        self.thumbnail_loaded.connect(self.update_bulk_edit_buttons)
        #self.thumbnail_loaded.connect(self.bulk_edit_view.previous_push.setEnabled)
    # Function to show the cover
    def show_image(self, filepath):
        pixmap = QtGui.QPixmap(filepath)
        self.edit_view.scene.clear()
        self.edit_view.pixmap_item = self.edit_view.scene.addPixmap(pixmap)
        self.edit_view.graphicsView.fitInView(self.edit_view.pixmap_item, QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def show_image_playlist(self, filepath):
        pixmap = QtGui.QPixmap(filepath)
        self.bulk_edit_view.scene.clear()
        self.bulk_edit_view.pixmap_item = self.bulk_edit_view.scene.addPixmap(pixmap)
        self.bulk_edit_view.cover_view.fitInView(self.bulk_edit_view.pixmap_item, QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def download_v(self):

        self.stack.setCurrentIndex(self.progress_view_index)

        # Gathering all information from the ui
        #url = self.start_view.link_input.text()
        playlist = self.start_view.playlist_radio.isChecked()
        filetype = "audio" if self.start_view.audio_checkbox.isChecked() else "video"

        folderpath = self.start_view.get_cleaned_dir()
        cookies = None  # TODO

        if playlist:
            self.linklist = get_playlist(self.start_view.link_input.text())
            self.bulk_edit_view.previous_push.setEnabled(False)
        else:
            self.linklist = [self.start_view.link_input.text()]

        # Downloading using main.py

        self.dworker = DownloadWorker(self.linklist, filetype, folderpath, cookies, self.filepath_list, playlist)

        self.dthread = QThread()
        self.dthread.setObjectName("test")


        self.dworker.moveToThread(self.dthread)

        self.dthread.started.connect(self.dworker.run)

        self.dworker.finished.connect(self.dthread.quit)

        self.dworker.finished.connect(self.dworker.deleteLater)
        self.dthread.finished.connect(self.dthread.deleteLater)
        self.dworker.progress.connect(lambda x: self.progress_view.progressBar.setValue(x))
        self.dworker.ready.connect(lambda x: self.progress_view.editmeta_push.setEnabled(x))
        self.dworker.ready.connect(lambda x: self.progress_view.quit_push.setEnabled(x))
        self.dworker.ready.connect(lambda x: self.progress_view.repeat_push.setEnabled(x))

        self.dthread.start()

    def threaded_download_thumbnail(self, linklist, return_list, playlist):
        self.thumbnail_loaded.emit(False)
        print(linklist)
        print(self.playlist_index)
        temp = download_thumbnail(linklist[self.playlist_index])
        crop_to_square(temp)
        return_list.append(temp)

        print(f"Bild liegt hier:{return_list[self.playlist_index]}")
        if playlist:
            self.thumbnail_ready.emit(return_list[self.playlist_index])
            self.thumbnail_loaded.emit(True)
        else:
            self.show_image(return_list[self.playlist_index])

        self.update_bulk_edit_buttons(True)

    def edit_v(self):

        self.setGeometry(starting_x-100,starting_y-75,standard_width + 200,standard_hight + 150)

        playlist = self.start_view.playlist_radio.isChecked()

        if playlist:

            self.stack.setCurrentIndex(self.bulk_edit_view_index)

            print(self.filepath_list[0])
            meta = get_meta(self.filepath_list[0])

            release_date = str(meta["TDRC"][0][0])
            self.bulk_edit_view.rday_input.setText(release_date[6:8])
            self.bulk_edit_view.rmonth_input.setText(release_date[4:6])
            self.bulk_edit_view.ryear_input.setText(release_date[0:4])
            self.bulk_edit_view.songtitle_input.setText(meta["TIT2"][0][0])
            self.bulk_edit_view.artist_input.setText(meta["TPE1"][0][0])
            self.bulk_edit_view.song_indicator.setText(f"Song: {self.playlist_index + 1}/{len(self.linklist)}")

            #thumbpath = None

            d = threading.Thread(target=self.threaded_download_thumbnail, args=(self.linklist, self.thumbpath_list, playlist))
            d.start()
            self.update_bulk_edit_buttons(True)
        else:
            self.stack.setCurrentIndex(self.edit_view_index)

            thumbpath = None

            d = threading.Thread(target=self.threaded_download_thumbnail, args=(self.linklist, self.thumbpath_list, playlist))
            d.start()

            print(self.filepath_list[0])
            meta = get_meta(self.filepath_list[0])
            print(meta)
            release_date = str(meta["TDRC"][0][0])

            self.edit_view.artist_input.setText(meta["TPE1"][0][0])
            self.edit_view.rday_input.setText(release_date[6:8])
            self.edit_view.rmonth_input.setText(release_date[4:6])
            self.edit_view.ryear_input.setText(release_date[0:4])
            self.edit_view.title_input.setText(meta["TIT2"][0][0])
            self.update_bulk_edit_buttons(True)

    def update_bulk_edit_buttons(self, unlocked):
        if not unlocked:
            self.bulk_edit_view.next_push.setEnabled(False)
            self.bulk_edit_view.previous_push.setEnabled(False)
        else:
            if self.playlist_index >= len(self.linklist) - 1:
                self.bulk_edit_view.next_push.setEnabled(False)
            else:
                self.bulk_edit_view.next_push.setEnabled(True)

            if self.playlist_index <= 0:
                self.bulk_edit_view.previous_push.setEnabled(False)
            else:
                self.bulk_edit_view.previous_push.setEnabled(True)

    def edit_next(self):
        def save(save_index):
            date = self.bulk_edit_view.ryear_input.text() + self.bulk_edit_view.rmonth_input.text() + self.bulk_edit_view.rday_input.text()

            artist = self.bulk_edit_view.artist_input.text()
            album = self.bulk_edit_view.albumtitle_input.text()
            genre = self.bulk_edit_view.genre_input.text()
            title = self.bulk_edit_view.songtitle_input.text()

            self.bulk_save(save_index, date, artist, genre, title, album)

        save_index = self.playlist_index
        save(save_index)

        self.playlist_index += 1

        print(f"linklist: {self.linklist}")
        print(f"Länge Linklist:{len(self.linklist)}")
        print("save_index:" + str(save_index))

        self.update_bulk_edit_buttons(True)

        self.bulk_edit_view.song_indicator.setText(f"Song: {self.playlist_index + 1}/{len(self.linklist)}")
        print(self.filepath_list[self.playlist_index])
        meta = get_meta(self.filepath_list[self.playlist_index])

        self.bulk_edit_view.songtitle_input.setText(meta["TIT2"][0][0])

        d = threading.Thread(target=self.threaded_download_thumbnail, args=(self.linklist, self.thumbpath_list, True))
        d.start()



    def edit_prev(self):

        def save(save_index):
            date = self.bulk_edit_view.ryear_input.text() + self.bulk_edit_view.rmonth_input.text() + self.bulk_edit_view.rday_input.text()

            artist = self.bulk_edit_view.artist_input.text()
            album = self.bulk_edit_view.albumtitle_input.text()
            genre = self.bulk_edit_view.genre_input.text()
            title = self.bulk_edit_view.songtitle_input.text()

            self.bulk_save(save_index, date, artist, genre, title, album)

        save_index = self.playlist_index
        save(save_index)
        self.playlist_index -= 1

        self.update_bulk_edit_buttons(True)

        self.bulk_edit_view.song_indicator.setText(f"Song: {self.playlist_index + 1}/{len(self.linklist)}")
        print(self.filepath_list[self.playlist_index])
        meta = get_meta(self.filepath_list[self.playlist_index])

        self.bulk_edit_view.songtitle_input.setText(meta["TIT2"][0][0])

        d = threading.Thread(target=self.threaded_download_thumbnail, args=(self.linklist, self.thumbpath_list, True))
        d.start()


    def bulk_save(self, save_index, date, artist, genre, title, album):
        filepath = self.filepath_list[save_index]
        thumbpath = self.thumbpath_list[save_index]

        edit_metadata(filepath, artist, album, date, genre, title, save_index + 1, thumbpath)

        delete_file(thumbpath)

    def bulk_save_quit(self):
        date = self.bulk_edit_view.ryear_input.text() + self.bulk_edit_view.rmonth_input.text() + self.bulk_edit_view.rday_input.text()

        artist = self.bulk_edit_view.artist_input.text()
        album = self.bulk_edit_view.albumtitle_input.text()
        genre = self.bulk_edit_view.genre_input.text()
        title = self.bulk_edit_view.songtitle_input.text()
        filepath = self.filepath_list[self.playlist_index]
        thumbpath = self.thumbpath_list[self.playlist_index]

        edit_metadata(filepath, artist, album, date, genre, title, self.playlist_index + 1, thumbpath)

        delete_file(thumbpath)
        exit(0)

    # Function called to save the changes made in edit_view
    def edit_save(self):

        date = self.edit_view.ryear_input.text() + self.edit_view.rmonth_input.text() + self.edit_view.rday_input.text()

        artist = self.edit_view.artist_input.text()
        album = self.edit_view.album_input.text()
        genre = self.edit_view.genre_input.text()
        title = self.edit_view.title_input.text()
        filepath = self.filepath_list[0]
        thumbpath = self.thumbpath_list[0]

        edit_metadata(filepath,artist,album,date,genre,title,0,thumbpath)

        delete_file(thumbpath)
        exit(0)

    def repeat_d(self):
        # Reset all buttons and lists for the next run
        def cleanup():
            self.start_view.single_radio.setChecked(False)
            self.start_view.playlist_radio.setChecked(False)
            self.start_view.audio_checkbox.setChecked(False)
            self.start_view.link_input.setText("")

            self.progress_view.editmeta_push.setEnabled(False)
            self.progress_view.quit_push.setEnabled(False)
            self.progress_view.repeat_push.setEnabled(False)

            self.filepath_list.clear()
            self.thumbpath_list.clear()

        #delete_file(self.thumbpath_list[0])

        cleanup()

        self.stack.setCurrentIndex(self.start_view_index)

    def save_q(self):
        # delete_file(self.thumbpath_list[0])
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