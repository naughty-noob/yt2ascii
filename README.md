# ASCII Video Player

Convert videos to ASCII art and play them in your terminal.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### YouTube URL

```bash
python ascii_alnum_dark.py "https://www.youtube.com/watch?v=Q3_YxsWnjKg"
```

### Local video file

```bash
python ascii_alnum_dark.py path/to/your/video.mp4
```

## Features

- Downloads YouTube videos automatically using yt-dlp
- Converts video frames to ASCII art using alphanumeric characters
- Real-time playback in terminal
- Adjustable width and FPS settings
- Uses mostly letters and numbers with `# @ % &` for darkest tones

## Controls

- Press `Ctrl+C` to stop playback

## Configuration

You can modify these settings in the script:

- `TARGET_WIDTH`: Maximum width of ASCII output (default: 120)
- `FPS_CAP`: Maximum FPS for playback (default: 24)
- `INVERT`: Flip dark/light mapping (default: False)
- `ASPECT_CORR`: Vertical squish adjustment for terminal font (default: 0.45)
