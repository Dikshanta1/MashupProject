import os
import shutil
from yt_dlp import YoutubeDL
from pydub import AudioSegment

def create_mashup(singer, num_videos, duration):
    download_path = "downloads"
    trimmed_path = "trimmed"
    output_file = "final_mashup.mp3"

    # Clean old folders
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    if os.path.exists(trimmed_path):
        shutil.rmtree(trimmed_path)

    os.makedirs(download_path)
    os.makedirs(trimmed_path)

    # Download videos
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'default_search': f'ytsearch{num_videos}',
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"{singer} songs"])

    # Convert + Trim
    for file in os.listdir(download_path):
        if file.endswith((".webm", ".m4a", ".mp3")):
            full_path = os.path.join(download_path, file)
            audio = AudioSegment.from_file(full_path)
            trimmed_audio = audio[:duration * 1000]

            out_name = os.path.splitext(file)[0] + "_trimmed.mp3"
            trimmed_audio.export(os.path.join(trimmed_path, out_name), format="mp3")

    # Merge
    combined = AudioSegment.empty()
    for file in os.listdir(trimmed_path):
        if file.endswith("_trimmed.mp3"):
            audio = AudioSegment.from_mp3(os.path.join(trimmed_path, file))
            combined += audio

    combined.export(output_file, format="mp3")

    return output_file
