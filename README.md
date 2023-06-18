# Lyrics Fetcher and Embedder

This repository contains a project that fetches lyrics for a list of music files in m4a format and embeds them. The goal of this project is to provide a convenient way to add lyrics to your music collection.

## Features

- Fetch lyrics for music files in m4a format.
- Embed the lyrics into the metadata of the music files.
- Support for batch processing of multiple files.
- Customizable options for fetching and embedding lyrics.

## Installation

1. Clone the repository to your local machine:

   ```shell
   git clone https://github.com/smurtazahasan/get-lyrics-bulk.git
   ```

2. Navigate to the project directory:

   ```shell
   cd lyrics-fetcher
   ```

3. Install the dependencies:

   ```shell
   pip install -r requirements.txt
   ```

## Usage

1. Ensure your music files are in the m4a format and are located in a directory accessible to the script.

2. Open the `fetcher.py` file and customize the following options:

   - `LYRICS_API`: Choose the API you want to use for fetching lyrics. (Refer to the API documentation for the required setup and credentials.)
   - `MUSIC_DIR`: Specify the path to the directory containing your music files.
   - (Optional) Adjust any additional options, such as language preferences or filtering criteria.

3. Run the `fetcher.py` script:

   ```shell
   python fetcher.py
   ```

   The script will fetch the lyrics for each music file and embed them into the metadata. Progress and any errors will be displayed in the console.

4. Check the music files in the specified directory. The lyrics should now be embedded in the metadata.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
