import customtkinter as ct
import main
import threading

class Window(ct.CTk):
    def __init__(self):
        super().__init__()

        self.title("Downloader")
        self.geometry("450x400")

        self.columnconfigure(0, weight=1)

        self.startscreen()

        #self.to_gui_queue = Queue()
        #self.to_worker_queue = Queue()

        #self.check_queue()

    def startscreen(self):
        self.startframe = ct.CTkFrame(self)

        self.mpcheckbox = Mpcheckbox(self)
        self.mpcheckbox.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="nswe")

        # Fragt ob Playlist oder Single
        self.type = Typecheckbox(self)
        self.type.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nswe")

        # Eingabefeld für den Link
        self.entry = Linkentry(self)
        self.entry.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nswe")

    def delete_frame(self, frame):
        frame.grid_forget()

    def start_download(self):
        pass


class Mpcheckbox(ct.CTkFrame):
    # This class displays a checkbox allowing the user to select between audio and video
    # Input can be returned using gettype()
    def __init__(self, master):
        super().__init__(master)

        self.description = ct.CTkLabel(self, text="Welchen Ausgabetyp hättest du gerne?")
        self.description.grid(row=0, column=0, padx=10, pady=(10, 10))

        self.mp3 = ct.CTkCheckBox(self, text="mp3")
        self.mp3.grid(row=1, column=0, padx=10, pady=(10, 0))

        self.mp4 = ct.CTkCheckBox(self, text="mp4")
        self.mp4.grid(row=1, column=2, padx=10, pady=(10, 0))

    def gettype(self):
        """retruns the type of file that should be downloaded"""
        # TODO: option for selecting both and handling the exception
        mp3 = self.mp3.get()
        mp4 = self.mp4.get()
        if mp3:
            return "mp3"
        elif mp4:
            return "mp4"
        else:
            ct.CTkMessagebox(title="Fehler", message="Bitte alle Felder ausfüllen.")
            return

class Typecheckbox(ct.CTkFrame):
    # This class displays a checkbox allowing the user to select between playlists and single videos
    # Input can be returned using gettype()
    def __init__(self, master):
        super().__init__(master)

        self.description = ct.CTkLabel(self, text="Willst du eine Playlist oder ein einzelnes Video?")
        self.description.grid(row=0, column=0, padx=10, pady=(10,10))

        self.single = ct.CTkCheckBox(self, text="Einzelnes Video")
        self.single.grid(row=1, column=0, padx=10,pady=(10,0))

        self.playlist = ct.CTkCheckBox(self, text="Playlist")
        self.playlist.grid(row=1, column=2, padx=10, pady=(10, 0))

    def gettype(self):
        """retruns wether a single video or a playlist should be downloaded"""
        #TODO: handling the exception
        single = self.single.get()
        playlist = self.playlist.get()
        if single:
            return "S"
        elif playlist:
            return "P"
        else:
            raise Exception

class Linkentry(ct.CTkFrame):
    # This class displays a field to enter the link of the resource
    # When "enter" is pressed it automatically submits the content
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.entry = ct.CTkEntry(self, placeholder_text="www.gibhierdeinlink.ein")
        self.entry.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nswe")
        self.entry.bind("<Return>", lambda e: self.master.start_download())

    #def on_submit(self):
     #   pass

    def getentry(self):
        return self.entry.get()

w1 = Window()
w1.mainloop()