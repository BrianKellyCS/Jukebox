# Jukebox

Jukebox is a project for managing local media and playing music/yt-videos/movies without having to open up the browser. It is terminal-based media player that integrates the power of MPV and yt-dlp for a seamless audio and video playback experience. It allows users to play media from specified directories, stream radio, search YouTube for content not available locally, and download it directly to a designated directory for easy management. It also supports searching for and playing movies using `mov-cli`.

## Features

- Play audio and video files from local directories.
- Stream radio directly from predefined URLs.
- Search for and play content from YouTube when not available locally.
- Download media from YouTube and save it to specific directories.
- Search for movies using the `mov-cli` tool when installed.

## Getting Started

### Prerequisites

Ensure you have Python installed on your system. Terminal Jukebox requires Python 3.x.

You will also need MPV and yt-dlp installed:
- **MPV**: [Installation Guide](https://mpv.io/installation/)
- **yt-dlp**: Install using pip with `pip install yt-dlp`
- **mov-cli** (optional): Install using pip with `pip install mov-cli` [Installation Guide](https://github.com/mov-cli/mov-cli/wiki/Installation)

### Installation

1. Clone this repository to your local machine.
    ```bash
    git clone https://github.com/BrianKellyCS/Jukebox.git
    cd Jukebox
    ```

## Usage

To start the Terminal Jukebox, navigate to the cloned directory and run:

```bash
python3 app.py
```


### Commands

The video commands will get improved as I keep working on this. But for now, this is what I use.

- `help`: Displays help menu with commands and usage details.
- `q`: Quits the Terminal Jukebox application.
- `r`: Plays streaming radio (default: Heart80s).
- `{search query} -a`: Searches for and plays audio from YouTube.
- `{search query} -a -p`: Searches for and plays audio playlists from YouTube.
- `{search query} -v`: Searches for and plays video from YouTube by default.
- `{search query} -v -yt`: Explicitly searches for and plays video from YouTube.
- `{search query} -v -m`: Searches for movies locally, and if not found -> uses the `mov-cli` tool.
- `{search query} -v -m -d`: Searches for and optionally downloads movies using the `mov-cli` tool.

To save media from YouTube to the specified directory, respond `y` when prompted after playback.

### MPV Controls

While MPV is focused, you can use the following controls:
- `SPACE`: Play/Pause
- `q`: Stop playback & quit MPV
- `>` (Shift + .): Next in playlist
- `<` (Shift + ,): Previous in playlist
- Arrow keys: Seek backward/forward and adjust volume
- `m`: Mute
- `f`: Toggle fullscreen
- `9`/`0`: Decrease/Increase volume

### Advanced Usage

#### Downloading Media

When you play media from YouTube or use the `mov-cli` for movies, you can choose to download the content. After playback, if you opted to download the media, you will be prompted to save it to a specific directory. Confirm with `y` to proceed with the download.

#### Movie Searches

With `mov-cli` installed, use the `-m` option after `-v` to search for movies. The `-d` option can be used to directly download movies after searching. Ensure you have enough storage space and appropriate permissions set on your machine to save downloads.

## Customization

You can customize the directories for music and videos by editing the `music_path` and `video_path` attributes in the `Jukebox` class.

### Customizing Streaming Radio

To change streaming radio station, you can modify the `self.Radio` attribute in the `Jukebox` class. Find the streaming URL by visiting `https://media-ice.musicradio.com` and selecting the desired radio station. Replace the `self.Radio` value with the direct streaming URL of your choice.


