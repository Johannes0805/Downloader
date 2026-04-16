# Downloader

![Badge: In Progress](https://img.shields.io/badge/Status-WIP-blue?style=flat-square)

This is just a simple downloader that can be used
to download YouTube videos in audio or video format.
Both single videos and playlists are supported.

## Installation

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

##  Running

###  IDE

To run the Script in an IDE just run main.py

###  App

####  Option 1: Use the already included .app file

=> The .app file can be found in /dist

####  Option 2: Generate the .app file on your own by using the following command:
```
pyinstaller --windowed --name "Downloader" --icon "assets/yt_downloader.icns" --add-binary "/opt/homebrew/bin/ffmpeg:ffstuff" --add-binary "/opt/homebrew/bin/ffprobe:ffstuff" main.py;
```
Important: the order ui has to be copied inside the .app file into /Frameworks otherwise the app will crash as it is not able to load the ui files

## Bugs

The different genres are not loaded in the app version currently