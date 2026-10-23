#!/usr/bin/env python3
"""
360p видео/плейлисты → настоящий MP4.
ffmpeg берётся из imageio-ffmpeg (PATH не нужен).
Никакого subprocess в нашем коде.
"""

import sys
from pathlib import Path

try:
    import yt_dlp
    import imageio_ffmpeg
except ImportError:
    sys.exit("Установи:  pip install yt-dlp imageio-ffmpeg")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
print(f"[i] ffmpeg: {FFMPEG}")

OUT = Path("downloads")
OUT.mkdir(exist_ok=True)

# Приоритет: H.264 + AAC (идеально совместимы с mp4),
# затем просто mp4-контейнер, затем любой 360p, затем что угодно.
FORMAT = (
    "bv*[height<=360][vcodec^=avc1]+ba[acodec^=mp4a]/"
    "bv*[height<=360][ext=mp4]+ba[ext=m4a]/"
    "b[height<=360][ext=mp4]/"
    "bv*[height<=360]+ba/"
    "b[height<=360]/b"
)


def hook(d):
    if d.get("status") == "downloading":
        p = d.get("_percent_str", "").strip()
        s = d.get("_speed_str", "").strip()
        print(f"\r{p}   {s}     ", end="", flush=True)
    elif d.get("status") == "finished":
        print(f"\n[+] {Path(d['filename']).name}")


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else input("Ссылка: ").strip()
    if not url:
        sys.exit("Пустая ссылка")

    opts = {
        "format": FORMAT,
        "outtmpl": str(OUT / "%(playlist_title,playlist_id|)s" / "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "ffmpeg_location": FFMPEG,         # ← встроенный ffmpeg, PATH не нужен
        "noplaylist": False,
        "ignoreerrors": True,
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "progress_hooks": [hook],
        "postprocessors": [
            # гарантированно кладёт результат в mp4-контейнер через ffmpeg
            {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"},
        ],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    print(f"\nГотово. Файлы: {OUT.resolve()}")


if __name__ == "__main__":
    main()