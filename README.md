# ASCII Video Player

Convert videos to ASCII art and play them in your terminal with full interactive controls, audio support, and export options.

## Installation

```bash
pip install -r requirements.txt
```

**Note:** For audio support, you'll also need `ffmpeg` installed on your system:
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg` (or your package manager)
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

### Basic Usage

**YouTube URL:**
```bash
python -m yt2ascii "https://www.youtube.com/watch?v=Q3_YxsWnjKg"
```

**Local video file:**
```bash
python -m yt2ascii path/to/your/video.mp4
```

**Multiple videos (playlist):**
```bash
python -m yt2ascii video1.mp4 video2.mp4 "https://youtube.com/watch?v=..."
```

### Command-Line Options

```bash
python -m yt2ascii [OPTIONS] SOURCE [SOURCE ...]

Options:
  --width WIDTH          Maximum width of ASCII output (default: 120)
  --fps FPS              Maximum FPS for playback (default: 24)
  --invert               Flip dark/light mapping
  --no-color             Disable ANSI colors
  --charset CHARSET      Character set preset: detailed, block, simple, alphanum
  --no-audio             Disable audio playback
  --no-cache             Disable frame caching
  --no-adaptive          Disable adaptive quality adjustment
  --config PATH          Path to YAML or JSON configuration file
  --export FORMAT        Export mode: text, gif, or html
  --output PATH          Output file path for export mode
  --frame-by-frame       Start in frame-by-frame mode
  --help                 Show help message
```

### Examples

**Custom width and FPS:**
```bash
python -m yt2ascii video.mp4 --width 80 --fps 15
```

**Block character set without colors:**
```bash
python -m yt2ascii video.mp4 --charset block --no-color
```

**Export to animated GIF:**
```bash
python -m yt2ascii video.mp4 --export gif --output output.gif
```

**Export to HTML:**
```bash
python -m yt2ascii video.mp4 --export html --output output.html
```

**Export to text file:**
```bash
python -m yt2ascii video.mp4 --export text --output frames.txt
```

**Using a configuration file:**
```bash
python -m yt2ascii video.mp4 --config config.yaml
```

## Interactive Controls

During playback, use these keyboard controls:

- **Space** - Pause/Resume playback
- **Left Arrow** - Seek backward 5 seconds
- **Right Arrow** - Seek forward 5 seconds
- **+ / =** - Increase playback speed (up to 3x)
- **-** - Decrease playback speed (down to 0.25x)
- **F** - Toggle fullscreen width
- **Q** - Quit playback
- **Enter** - Step one frame forward (when paused)
- **Ctrl+C** - Emergency quit

## Character Sets

Choose from multiple character set presets:

- **detailed** (default) - Alphanumeric characters with symbols: ` .`-_:;^~+iIl1tfrjJYCLUXVTwqpdbmgKO0QNBMAESZ23456789%&#@`
- **block** - Block characters: ` ░▒▓█`
- **simple** - Simple dots: ` .#`
- **alphanum** - Same as detailed

## Configuration File

Create a YAML or JSON configuration file to set default options:

**config.yaml:**
```yaml
target_width: 100
fps_cap: 20
invert: false
aspect_corr: 0.45
use_colors: true
charset: block
enable_audio: true
frame_cache_size: 100
adaptive_quality: true
auto_detect_terminal: true
```

**config.json:**
```json
{
  "target_width": 100,
  "fps_cap": 20,
  "invert": false,
  "aspect_corr": 0.45,
  "use_colors": true,
  "charset": "block",
  "enable_audio": true,
  "frame_cache_size": 100,
  "adaptive_quality": true,
  "auto_detect_terminal": true
}
```

Command-line arguments override configuration file settings.

## Requirements

- Python 3.7+
- OpenCV (`opencv-python`)
- NumPy
- yt-dlp (for YouTube downloads)
- pygame (for audio playback)
- Pillow (for GIF export)
- PyYAML (for YAML config files, optional)
- ffmpeg (system dependency, for audio extraction)

## Troubleshooting

**Audio not playing:**
- Make sure `ffmpeg` is installed and in your PATH
- Try `--no-audio` to disable audio if it's causing issues

**Keyboard controls not working:**
- On Windows, some terminals may have limited support
- Try using a different terminal (Windows Terminal, PowerShell, etc.)

**Slow playback:**
- Reduce `--fps` or `--width`
- Use `--no-cache` if memory is limited
- Try `--charset simple` for faster rendering

**Colors not showing:**
- Check if your terminal supports ANSI colors
- Use `--no-color` to disable if causing issues
- The script auto-detects terminal capabilities

## License

This project is open source. Feel free to use and modify as needed.
