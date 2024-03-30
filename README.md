# Terminal Jukebox

Terminal Jukebox is a compact, terminal-based media player that integrates the power of MPV and yt-dlp for a seamless audio and video playback experience. It allows users to play media from specified directories, stream radio, search YouTube for content not available locally, and download it directly to a designated directory for easy management.

## Features

- Play audio and video files from local directories.
- Stream radio directly from predefined URLs.
- Search for and play content from YouTube when not available locally.
- Download media from YouTube and save it to specific directories.

## Getting Started

### Prerequisites

Ensure you have Python installed on your system. Terminal Jukebox requires Python 3.x.

You will also need MPV and yt-dlp installed:
- **MPV**: [Installation Guide](https://mpv.io/installation/)
- **yt-dlp**: Install using pip with `pip install yt-dlp`

### Installation

1. Clone this repository to your local machine.
    ```bash
    git clone https://github.com/BrianKellyCS/Jukebox.git
    cd Jukebox
    ```
2. Install required Python packages:
    ```bash
    pip install colorama
    ```

## Usage

To start the Terminal Jukebox, navigate to the cloned directory and run:

```bash
python jukebox.py
```


### Commands

- `help`: Displays help menu with commands and MPV controls.
- `q`: Quits the Terminal Jukebox application.
- `r`: Plays streaming radio (default: Heart80s).
- `{search query} -a`: Searches for and plays audio from YouTube.
- `{search query} -v`: Searches for and plays video from YouTube.
- To save media from YouTube to the specified directory, respond `y` when prompted after playback.

### MPV Controls

While MPV is focused, you can use the following controls:
- `SPACE`: Play/Pause
- `q`: Stop playback & quit MPV
- `>` (Shift + .): Next in playlist
- `<` (Shift + ,): Previous in playlist
- Arrow keys: Volume and seek control
- `m`: Mute
- `f`: Toggle fullscreen
- `9`/`0`: Decrease/Increase volume

## Customization

You can customize the directories for music and videos by editing the `music_path` and `video_path` attributes in the `Jukebox` class.


