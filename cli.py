import main
from main import download_single, crop_to_square


def download():
    playlist = input("Do you want to download a playlist or a single video (P/S): ").upper()

    url = input("Enter the link you want to download: ")

    filetype = input("Do you want the download to be a video or just audio (V/A): ").upper()
    if filetype == "V":
        filetype = "video"
    elif filetype == "A":
        filetype = "audio"
    else: print("Error")

    filepath = input("Where do you want to save the file? /Users/johannes/...")
    filepath = "/Users/johannes/" + filepath + "/"

    cookies = None

    if playlist == "P":
        linklist = main.get_playlist(url)
        artist = input("Artist: ")
        album = input("Album: ")
        date = input("Date: ")
        genre = input("Genre: ")
        playlist_indicator = 0
        for l in linklist:
            playlist_indicator += 1
            rpath = download_single(l, filetype, filepath, cookies)
            print(f"Download successfull: {rpath}")
            edit = input("Do you want to edit the meta data (Y/N)").upper()

            thumbpath = None
            if filetype == "audio":
                thumbpath = main.download_thumbnail(l)
                crop_to_square(thumbpath, thumbpath)

            if edit == "Y":
                title = input("Titel: ")
                main.edit_metadata(filepath, artist, album, date, genre, title, playlist_indicator, thumbnail_path=thumbpath)

            if filetype == "audio":
                main.delete_file(thumbpath)



    elif playlist == "S":
        filepath = download_single(url, filetype, filepath, cookies)
        print(f"Download successfull: {filepath}")
        edit = input("Do you want to edit the meta data (Y/N)").upper()

        thumbpath = None
        if filetype == "audio":
            thumbpath = main.download_thumbnail(url)
            crop_to_square(thumbpath, thumbpath)


        if edit == "Y":
            artist = input("Artist: ")
            album = input("Album: ")
            date = input("Date: ")
            genre = input("Genre: ")
            title = input("Titel: ")
            main.edit_metadata(filepath, artist, album, date, genre, title, 1, thumbnail_path=thumbpath)

        if filetype == "audio":
            main.delete_file(thumbpath)
download()
