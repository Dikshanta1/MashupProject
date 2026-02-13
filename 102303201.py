import sys
import os
import shutil
from yt_dlp import YoutubeDL
from pydub import AudioSegment


def validate_inputs(args):
    if len(args) != 5:
        print("Usage: python 102303201.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer = args[1]

    try:
        num_videos = int(args[2])
        if num_videos <= 10:
            raise ValueError
    except ValueError:
        print("Error: NumberOfVideos must be an integer greater than 10.")
        sys.exit(1)

    try:
        duration = int(args[3])
        if duration <= 20:
            raise ValueError
    except ValueError:
        print("Error: AudioDuration must be an integer greater than 20 seconds.")
        sys.exit(1)

    output_file = args[4]

    if not output_file.endswith(".mp3"):
        print("Error: Output file must have .mp3 extension.")
        sys.exit(1)

    return singer, num_videos, duration, output_file


def download_videos(singer, num_videos, download_path):
    print(f"Downloading top {num_videos} videos of {singer}...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'default_search': f'ytsearch{num_videos}',
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"{singer} songs"])


def convert_and_trim(download_path, duration, trimmed_path):
    print("Converting and trimming audio files...")

    for file in os.listdir(download_path):
        if file.endswith((".webm", ".m4a", ".mp3")):
            full_path = os.path.join(download_path, file)
            try:
                audio = AudioSegment.from_file(full_path)
                trimmed_audio = audio[:duration * 1000]

                output_file = os.path.splitext(file)[0] + "_trimmed.mp3"
                trimmed_audio.export(os.path.join(trimmed_path, output_file), format="mp3")
            except Exception as e:
                print(f"Error processing {file}: {e}")


def merge_audios(trimmed_path, output_file):
    print("Merging audio files...")

    combined = AudioSegment.empty()

    for file in os.listdir(trimmed_path):
        if file.endswith("_trimmed.mp3"):
            audio = AudioSegment.from_mp3(os.path.join(trimmed_path, file))
            combined += audio

    combined.export(output_file, format="mp3")
    print(f"\nMashup created successfully: {output_file}")


def main():
    try:
        singer, num_videos, duration, output_file = validate_inputs(sys.argv)

        download_path = "downloads"
        trimmed_path = "trimmed"

        # Clean old folders if they exist
        if os.path.exists(download_path):
            shutil.rmtree(download_path)
        if os.path.exists(trimmed_path):
            shutil.rmtree(trimmed_path)

        os.makedirs(download_path)
        os.makedirs(trimmed_path)

        download_videos(singer, num_videos, download_path)
        convert_and_trim(download_path, duration, trimmed_path)
        merge_audios(trimmed_path, output_file)

    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
