# Music Lyrics Setter

This repository contains a Python script that allows you to set lyrics for your music files. It utilizes an API to fetch lyrics based on the song title and embeds them into the corresponding music files. The script supports both sequential and concurrent processing to accommodate different performance requirements.

## Features

- Fetches lyrics using an API based on song titles.
- Embeds fetched lyrics into music files using ID3 tags.
- Supports sequential and concurrent processing for setting lyrics.
- Provides a progress bar to track the processing status.

## Requirements

- Python 3.6+
- `music_tag` library (install using `pip install music-tag`)
- `requests` library (install using `pip install requests`)
- `tqdm` library (install using `pip install tqdm`)

## Usage

1. Clone the repository:

   ```
   git clone https://github.com/smurtazahasan/get-lyrics-bulk.git
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Place your music files in the desired directory.

4. Open the terminal and navigate to the directory where the script is located.

5. Run the script with the desired options:

- To set lyrics sequentially (default):

  ```
  python main.py -directory ./music
  ```

- To set lyrics concurrently:

  ```
  python main.py -directory ./music -concurrent True
  ```

- To perform a dry run and see the list of files that will be processed:

  ```
  python main.py -directory ./music -dry_run True
  ```

- To fetch lyrics for a single song:

  ```
  python main.py -directory ./music -fetch_manual "Song Title"
  ```

**Note:** Replace `./music` with the path to your music directory and `"Song Title"` with the title of the song for manual fetching.

   The script will fetch the lyrics for each music file and embed them into the files using ID3 tags. Progress will be displayed using a progress bar.

## Performance Optimization

The script offers two processing methods to optimize performance:

- Sequential Processing:
  - Suitable for a smaller number of music files.
  - Processes the files one by one in a sequential manner.
  - Enabled by default in the script.

- Concurrent Processing (BETA!!):
  - Recommended for a larger number of music files.
  - Utilizes parallel processing to speed up execution time.
  - To enable concurrent processing, follow the instructions in the "Usage" section.
  - **Note** that concurrent processing requires the `music_tag` library to work correctly in a concurrent/threaded environment which I'm working on but this will remain in experimental state until then.

Choose the appropriate processing method based on your requirements and the number of music files you have.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- [music_tag](https://github.com/KristoforMaynard/music-tag) library for ID3 tag handling.
- [Some Random API](https://some-random-api.com/) for lyrics retrieval.

Feel free to contribute to the project and make it even better! If you encounter any issues or have any suggestions, please open an issue on the repository.
