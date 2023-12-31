# Imports
import argparse  # Parses command line arguments
import music_tag  # Reads/Sets ID3 Tags
import requests  # Sends API Requests
import os  # Gets paths for all files
from tqdm import tqdm
from datetime import datetime
import os, subprocess, re
from subprocess import call
import re
from threading import Thread

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

# Uses ffprobe to get audio information from file
def probe_file(filename):
    def format_sample_rate(sample_rate):
        return f"{sample_rate} Hz"

    def format_bit_rate(bit_rate):
        return f"{int(round(bit_rate / 1000))} kbps"

    cmnd = ["ffprobe", "-v", "error", "-show_entries", "stream=sample_rate,channels,bit_rate", "-of", "default=noprint_wrappers=1:nokey=1", filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    sample_rate = format_sample_rate(out.decode("utf-8").split("\n")[0])
    channels = out.decode("utf-8").split("\n")[1]
    bit_rate = format_bit_rate(float(out.decode("utf-8").split("\n")[2]))

    return {"bitrate": bit_rate, "channels": channels, "sample_rate": sample_rate}


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
        return ""  # Return empty string if lyrics fetching failed or response format is invalid


# Sets lyrics for all files in directory
# Input: ['./music/drake.m4a', './music/Pain 1993 (Explicit).mp3'...]
def set(paths):
    progress_bar = tqdm(total=len(paths), desc="Processing", unit="file(s)")
    missed_songs = []
    missed_songs_count = 0

    for path in paths:
        # Load song's ID3 tags and probe file for audio information
        f = music_tag.load_file(path)
        probe = probe_file(path)
        
        if "lyrics" in f:
            if len(str(f["lyrics"])) > 10:
                print("Lyrics already exist for " + path)
                progress_bar.update(1)
                continue
        
        # Prepare argument for API call
        artist = str(f["artist"])
        artist_match = re.search(r"(.*?)\s(?:feat(?:\.|uring)?|&|with|,|and|ft\.|w\.)", artist, re.IGNORECASE)
        if artist_match:
            artist = artist_match.group(1).strip()
        
        # Title and Artist
        lyrics = fetch(str(f["title"]) + " " + artist)
        if lyrics == "":
            # Track the missed song
            missed_songs.append(path)
            
            # Save empty tag
            f["lyrics"] = ""
            f.save()
            continue
        else:
            # Add additional information to lyrics
            additional_info = "\n\nBitrate: {bitrate}\nChannels: {channels}\nSample Rate: {samplerate}".format(
                bitrate=probe["bitrate"],
                channels=probe["channels"],
                samplerate=probe["sample_rate"],
            )

            f["lyrics"] = lyrics + additional_info
            f.save()
            
        progress_bar.update(1)

    progress_bar.close()
    return missed_songs, missed_songs_count


# Concurrently sets lyrics for all files in directory
# Issues: MP3_TAG is not thread safe
def set_concurrent(paths):
    # Split list of file paths into 
    path_1, path_2 = paths[: len(paths) // 2], paths[len(paths) // 2 :]
    
    # Run operation in two threads
    Thread(target=set, args=(path_1,)).start()
    Thread(target=set, args=(path_2,)).start()
    

# Remove lyrics from Directory
def remove_lyrics_from_files(paths):
    for path in paths:
        # Load song's ID3 tags
        f = music_tag.load_file(path)
        f["lyrics"] = ""
        f.save()
        print(path)
    
    
def main(directory, concurrent, dry_run, fetch_manual, remove_lyrics):
    # Get file paths
    file_paths = get_m4a_files_in_directory(directory)
    
    # Remove lyrics from files
    if remove_lyrics:
        remove_lyrics_from_files(file_paths)
        return
    
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
        missed_songs, missed_songs_count = set(file_paths)
        for line in missed_songs:
            print(line)
        print("Missed Songs Total: ", missed_songs_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set lyrics for music files.")
    parser.add_argument("-directory", type=str, default="./", help="Directory containing the music files")
    parser.add_argument("-concurrent", action="store_true", help="Enable concurrent processing (default: False)")
    parser.add_argument("-dry_run", action="store_true", help="Only print the files that will be processed (default: False)")
    parser.add_argument("-fetch_manual", type=str, default="", help="Fetch lyrics for a single song (insert song title)")
    parser.add_argument("-remove_lyrics", action="store_true", help="Remove lyrics for entire directory")
    args = parser.parse_args()
    main(args.directory, args.concurrent, args.dry_run, args.fetch_manual, args.remove_lyrics)
