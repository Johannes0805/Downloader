import yt_dlp
from mutagen.id3 import ID3, error, TIT2, TRCK, APIC, TALB, TPE1, TDRC, TCON, ID3NoHeaderError, TextFrame, UrlFrame, \
    COMM, USLT
from PIL import Image
import os
import requests

def get_options(url, filetype, filepath, cookies=None):
    yt = yt_dlp.YoutubeDL()
    info = yt.extract_info(url, download=False)

    postprocessors = []
    if filetype == "audio":
        postprocessors.append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"})
    elif filetype == "video":
        postprocessors.append({
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mkv"
        })
    postprocessors.append({"key": "EmbedThumbnail"})
    postprocessors.append({"key": "FFmpegMetadata"})

    if filetype == "audio":
        dlformat = get_best_stream(info, filetype)
        #dlformat = "bestvideo+bestaudio/best"
    elif filetype == "video":
        dlformat = f"{get_best_stream(info, filetype)}+{get_best_stream(info, 'audio')}"
    else:
        raise ValueError(f"Can only give options for video or audio download; Given: {filetype}")

    return {
        "format": dlformat,
        "cookiefile": "/Users/johannes/Downloads/www.youtube.com_cookies.txt",
        "outtmpl": filepath + "%(title)s.%(ext)s",
        "noplaylist": True,
        "writethumbnail": True,
        "extractor_args": {"youtube": {"player_client": ["default", "-tv_simply"]}},
        "postprocessors": postprocessors
    }

def get_best_stream(info, filetype):
    def video_sort_helper(x):
        if x.get("vbr"):
            return x.get("vbr")
        else:
            return 0
    def audio_sort_helper(x):
        if x.get("abr"):
            return x.get("abr")
        else:
            return 0

    if filetype == "audio":
        audio_streams = [f for f in info["formats"] if f["acodec"] != "none" ] #and str(f.get("format_note", "")).find("original")+1
        audio_streams.sort(key=audio_sort_helper, reverse=True)
        return audio_streams[0].get("format_id")
    elif filetype == "video":
        video_streams = [f for f in info["formats"]if f["vcodec"] != "none"]
        video_streams.sort(key=video_sort_helper, reverse=True)
        return video_streams[0].get("format_id")
    else:
        raise ValueError(f"Can only extract best video or audio streams; Given: {filetype}")

def download_single(url, filetype, filepath, cookies=None):
    ydl = yt_dlp.YoutubeDL(get_options(url, filetype, filepath, cookies))
    max_retries = 10
    retries = 0
    while retries < max_retries:
        try:
            ydl.download(url)
            break
        except Exception as e:
            print(f"An error accured while downloading {retries +1} / {max_retries}")
            print(e)
            retries += 1
    if retries == max_retries:
        exit(1)
    return filepath + str(ydl.extract_info(url, download=False).get("title"))+ (".mp3" if filetype == "audio" else "")

def edit_metadata(filepath, artist=None, album=None, date=None, genre=None, title=None, playlist_index=None, thumbnail_path=None):
    try:
        media = ID3(filepath)
    except error:
        media = ID3()

    if artist and artist != "":
        media.add(TPE1(encoding=3, text=artist))
    if album and album != "":
        media.add(TALB(encoding=3, text=album))
    if date and date != "":
        media.add(TDRC(encoding=3, text=date))
    if genre and genre != "":
        media.add(TCON(encoding=3, text=genre))
    if title and title != "":
        media.add(TIT2(encoding=3, text=title))
    if playlist_index and playlist_index != "":
        media.add(TRCK(encoding=3, text=str(playlist_index)))
    else:
        media.add(TRCK(encoding=3, text="1"))

    if thumbnail_path:
        with open(thumbnail_path, "rb") as img:
            media.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime="image/jpeg",  # falls PNG, entsprechend anpassen
                    type=3,  # Cover (front)
                    desc="Cover",
                    data=img.read()
                )
            )

    media.save(filepath)
def get_playlist(url):
    """
    :return: list of links to every video in the playlist
    """
    yt = yt_dlp.YoutubeDL()
    info = yt.extract_info(url, download=False)
    entries = [f.get("original_url") for f in info["entries"]]
    return entries

def crop_to_square(filepath, output_path=None, scale:str=None):
    with Image.open(filepath) as img:
        width, height = img.size

        new_edge = min(width, height)

        left = (width - new_edge) // 2
        top = (height - new_edge) // 2
        right = left + new_edge
        bottom = top + new_edge

        img_cropped = img.crop((left, top, right, bottom))

        if scale:
            x, y = scale.split("x")
        else:
            x,y = (1000,1000)

        img_resized = img_cropped.resize((x, y))

        if output_path:
            img_resized.save(output_path, "JPEG")
        else:
            img_resized.save(filepath, "JPEG")

def download_thumbnail(url):
    yt = yt_dlp.YoutubeDL()
    info = yt.extract_info(url, download=False)
    # getting the thumbnail url
    thumb_url = info.get("thumbnail")

    thumbnail_path =  str(info.get("title")) + ".jpg"

    # downloading and writing the thumbnail
    r = requests.get(thumb_url)
    with open(thumbnail_path, "wb") as f:
        f.write(r.content)

    return thumbnail_path

def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        raise FileNotFoundError

def get_meta(filepath):
    try:
        tags = ID3(filepath)
    except ID3NoHeaderError:
        return {}  # keine ID3-Tags vorhanden

    out = {}

    # tags.items() liefert (key, frame) z.B. ("TIT2", TIT2(...)) oder ("APIC:Cover", APIC(...))
    for key, frame in tags.items():
        frame_id = frame.FrameID  # z.B. "TIT2", "APIC", "COMM"

        def push(value) -> None:
            out.setdefault(frame_id, [])
            out[frame_id].append(value)

        # Text Frames (T***)
        if isinstance(frame, TextFrame):
            # frame.text ist meist eine Liste von Strings
            push(list(frame.text))

        # URL Frames (W***)
        elif isinstance(frame, UrlFrame):
            # frame.url ist ein String
            push(frame.url)

        # Comments
        elif isinstance(frame, COMM):
            push({
                "lang": frame.lang,
                "desc": frame.desc,
                "text": list(frame.text),
            })

        # Lyrics
        elif isinstance(frame, USLT):
            push({
                "lang": frame.lang,
                "desc": frame.desc,
                "text": frame.text,
            })

        # Attached Picture (Cover)
        elif isinstance(frame, APIC):
            data = frame.data or b""
            push({
                "mime": frame.mime,
                "type": int(frame.type),  # 3 = front cover
                "desc": frame.desc,
                "size": len(data),  # Bytes
            })

        # Alles andere: fallback (gut für seltene Frames)
        else:
            # frame.pprint() ist lesbar, aber string-basiert
            push(frame.pprint())

    return out