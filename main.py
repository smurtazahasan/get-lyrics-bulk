# Imports
import music_tag  # Reads/Sets ID3 Tags
import requests  # Sends API Requests
import urllib.parse  # Parses Music Titles for API Query
import os  # Gets paths for all files
from tqdm import tqdm
import concurrent.futures
import time


# Get paths for files in directory
# Input: './music'
# Result: ['./music/drake.m4a', './music/Pain 1993 (Explicit).mp3'...]
def get_files_in_directory(directory):
  file_paths = []
  for root, _, files in os.walk(directory):
    for file in files:
      file_path = os.path.join(root, file)
      file_paths.append(file_path)
  return file_paths

# Build API request for song
# Input: "Deep Pockets"
# Results: {"title": Deep Pockets, "lyrics": ''...}
def fetch(title):
  URL = "https://some-random-api.com/lyrics?title="
  parsed_title = urllib.parse.quote_plus(title)

  resp = requests.get(URL + parsed_title)
  if 300 > resp.status_code >= 200: content = resp.json()
  else: content = {"lyrics": ""}
  return content['lyrics']


def set(paths):
  total_files = len(paths)
  progress_bar = tqdm(total=total_files, desc="Processing", unit="file(s)")
  for path in paths:
     f = music_tag.load_file(path)
     f['lyrics'] = fetch(str(f['title']))
     f.save()
     print("Done: " + path)
     progress_bar.update(1)
  progress_bar.close()



def set_concurrent(paths):
    total_files = len(paths)
    progress_bar = tqdm(total=total_files, desc="Processing", unit="file(s)")

    def process_file(path):
        file = music_tag.load_file(path)
        if len(file['lyrics']) < 20:
            file['lyrics'] = fetch(str(file['title']))
        file.save()
        progress_bar.update(1)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_file, paths)

    progress_bar.close()



def check(paths):
  for i in paths:
    # Get song title + reference
    f = music_tag.load_file(i)
    print(str(f['title']) + ": " + str(f['lyrics']))


def remove_lyrics(paths):
  for i in paths:
    #print(i)
    f = music_tag.load_file(i)
    if 'lyrics' in f:
        f['lyrics'] = ""
        f.save()

def filter_m4a_paths(file_paths):
    m4a_paths = [path for path in file_paths if os.path.splitext(path)[1] == ".m4a"]
    return m4a_paths

paths = get_files_in_directory("./")
paths = filter_m4a_paths(paths)
set(paths)