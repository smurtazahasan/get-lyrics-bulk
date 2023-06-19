# Imports
import argparse  # Parses command line arguments
import music_tag  # Reads/Sets ID3 Tags
import requests  # Sends API Requests
import urllib.parse  # Parses Music Titles for API Query
import os  # Gets paths for all files
from tqdm import tqdm
import concurrent.futures
import time
from datetime import datetime
import os, sys, subprocess, shlex, re
from subprocess import call

### Helper Functions ###


# Get paths for files in directory
# Input: './music'
# Result: ['./music/drake.m4a', './music/Pain 1993 (Explicit).mp3'...]
def get_m4a_files_in_directory(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.splitext(file_path)[1] in [".m4a", ".mp3", ".flac", ".wav"]:
                file_paths.append(file_path)
    return file_paths


# Formats sample rate
# Input: 44100
# Result: 44.1 kHz
def format_sample_rate(sample_rate):
    return f"{sample_rate} Hz"


# Formats bit rate
# Input: 320000
# Result: 320 kbps
def format_bit_rate(bit_rate):
    return f"{int(round(bit_rate / 1000))} kbps"


# Probes file for audio information
# Input: './music/drake.m4a'
# Result: {"bitrate": 320 kbps, "channels": 2, "sample_rate": 44.1 kHz}
def probe_file(filename):
    # Command = 'ffprobe -v error -show_entries stream=sample_rate,channels,bit_rate -of default=noprint_wrappers=1:nokey=1 {filename}'
    cmnd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=sample_rate,channels,bit_rate",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        filename,
    ]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    sample_rate = format_sample_rate(out.decode("utf-8").split("\n")[0])
    channels = out.decode("utf-8").split("\n")[1]
    bit_rate = format_bit_rate(float(out.decode("utf-8").split("\n")[2]))

    return {"bitrate": bit_rate, "channels": channels, "sample_rate": sample_rate}


# Gets audio information from file
# Input: './music/drake.m4a'
# Result: {"bitrate": 320 kbps, "codec": "aac", "channels": 2, "bits_per_sample": 0, "sample_rate": 44100}
def get_audio_info(file_path):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=bit_rate,codec_name,channels,bits_per_sample,sample_rate",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]

    output = (
        subprocess.check_output(command, universal_newlines=True).strip().split("\n")
    )
    return {
        "bitrate": int(output[0]),
        "codec": output[1],
        "channels": int(output[2]),
        "bits_per_sample": int(output[3]),
        "sample_rate": int(output[4]),
    }


# Fetches lyrics from API and formats them
# Input: 'Deep Pockets'
# Result: """Title: Deep Pockets, Author: Drake, Lyrics:..., Date: 01/01/2021 00:00:00"""
def fetch(title):
    url = "https://some-random-api.com/lyrics"
    params = {"title": title}
    resp = requests.get(url, params=params)

    if resp.status_code == 200:
        content = resp.json()
        if "title" in content and "author" in content and "lyrics" in content:
            return """Title: {title}\nAuthor: {author}\n\n{lyrics}\nRetrieved on: {dt_string}""".format(
                title=content["title"],
                author=content["author"],
                lyrics=content["lyrics"],
                dt_string=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            )
        else:
            print("Invalid response format from the API.")
    else:
        print("Error occurred while fetching lyrics. Status code:", resp.status_code)

    return ""  # Return empty string if lyrics fetching failed or response format is invalid


# Sets lyrics for all files in directory
# Input: ['./music/drake.m4a', './music/Pain 1993 (Explicit).mp3'...]
def set(paths):
    progress_bar = tqdm(total=len(paths), desc="Processing", unit="file(s)")

    for path in paths:
        # Load song's ID3 tags and probe file for audio information
        f = music_tag.load_file(path)
        probe = probe_file(path)

        lyrics = fetch(str(f["title"]))  # Fetch lyrics from API
        additional_info = "\n\nBitrate: {bitrate}\nChannels: {channels}\nSample Rate: {samplerate}".format(
            bitrate=probe["bitrate"],
            channels=probe["channels"],
            samplerate=probe["sample_rate"],
        )

        f["lyrics"] += additional_info
        f.save()
        progress_bar.update(1)

    progress_bar.close()


# Concurrently sets lyrics for all files in directory
# Issues: MP3_TAG is not thread safe
def set_concurrent(paths):
    progress_bar = tqdm(total=len(paths), desc="Processing", unit="file(s)")

    def process_file(path):
        file = music_tag.load_file(path)
        if len(file["lyrics"]) < 20:
            file["lyrics"] = fetch(str(file["title"]))
        file.save()
        progress_bar.update(1)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_file, paths)

    progress_bar.close()


def main(directory, concurrent, dry_run, fetch_manual):
    # Get file paths
    file_paths = get_m4a_files_in_directory(directory)

    if len(fetch_manual) > 0:
        print(fetch(fetch_manual))
        return

    if dry_run:
        print("Files that will be processed:")
        for path in file_paths:
            print(path)
        return

    if concurrent:
        set_concurrent(file_paths)
    else:
        set(file_paths)


if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Set lyrics for music files.")

    # Add arguments for directory and identifier
    parser.add_argument(
        "-directory",
        type=str,
        default="./",
        help="Directory containing the music files",
    )
    parser.add_argument(
        "-concurrent",
        type=bool,
        default=False,
        help="Enable concurrent processing (default: False)",
    )
    parser.add_argument(
        "-dry_run",
        type=bool,
        default=False,
        help="Only print the files that will be processed (default: False)",
    )
    parser.add_argument(
        "-fetch_manual",
        type=str,
        default="",
        help="Fetch lyrics for a single song (insert song title)",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the main function with the provided directory and identifier
    main(args.directory, args.concurrent, args.dry_run, args.fetch_manual)
