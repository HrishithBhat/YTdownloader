from yt_dlp import YoutubeDL
import os

# Set downloads outside the project directory
DOWNLOAD_DIR = os.path.expanduser("~/YTDownloads")

def download_video(url, progress_hook=None):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook] if progress_hook else [],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
