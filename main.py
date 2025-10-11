import yt_dlp


def get_option(url, filetype, cookies):
    yt = yt_dlp.YoutubeDL()

def get_best_stream(info, filetype):
    if filetype == "mp3":
        audio_streams = [f for f in info["formats"] if f["vcodec"] == "none"]
        audio_streams.sort(key= lambda x: x.get("abr", 0), reverse=True)
        return audio_streams[0].get("format_id")
    else:
        video_streams = []

def download_single():
    pass

def edit_metadata():
    pass

def get_playlist():
    pass

def crop_to_square():
    pass