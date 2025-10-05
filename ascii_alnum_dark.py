import os
import sys
import time
import shutil
import subprocess
import tempfile
from typing import Tuple, Optional

import cv2
import numpy as np

# ======= CONFIGURATION =======
# light → dark, mostly letters/numbers, a few dark symbols at the end
ALPHANUM_DARK = " .`-_:;^~+iIl1tfrjJYCLUXVTwqpdbmgKO0QNBMAESZ23456789%&#@"
TARGET_WIDTH = 120
FPS_CAP = 24
INVERT = False        # flip dark/light mapping
ASPECT_CORR = 0.45    # adjust vertical squish for your terminal font
USE_COLORS = True     # enable ANSI colors
# =============================

CHARSET = np.array(list(ALPHANUM_DARK))

def rgb_to_ansi(r: int, g: int, b: int) -> int:
    if r == g == b:
        # grayscale
        if r < 8:
            return 16
        elif r > 248:
            return 231
        else:
            return 232 + int((r - 8) / 10)
    else:
        # color
        return 16 + (36 * int(r / 51)) + (6 * int(g / 51)) + int(b / 51)


def get_color_code(bgr_color: np.ndarray) -> str:
    if not USE_COLORS:
        return ""
    
    b, g, r = bgr_color
    ansi_code = rgb_to_ansi(r, g, b)
    return f"\033[38;5;{ansi_code}m"


def reset_color() -> str:
    return "\033[0m" if USE_COLORS else ""

def download(url: str) -> str:
    tdir = tempfile.mkdtemp(prefix="ascii_vid_")
    print(f"↓ Downloading to {tdir} ...")
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-f", "bestvideo[height<=360][fps<=30]+bestaudio/best/best",
        "-o", "%(title)s.%(ext)s",
        url
    ]
    subprocess.check_call(cmd, cwd=tdir)
    for fn in os.listdir(tdir):
        if fn.lower().endswith((".mp4", ".mkv", ".webm", ".mov")):
            return os.path.join(tdir, fn)
    raise RuntimeError("No video file found after download.")

def frame_to_ascii(frame: np.ndarray, width: int) -> str:
    h, w = frame.shape[:2]
    new_w = width
    new_h = max(1, int(h * (new_w / w) * ASPECT_CORR))
    
    # resize both color and grayscale versions
    small_color = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small_gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)

    norm = small_gray.astype(np.float32) / 255.0
    if INVERT:
        norm = 1.0 - norm
    idx = (norm * (len(CHARSET) - 1)).astype(np.int32)

    rows = []
    for y in range(new_h):
        row_chars = []
        for x in range(new_w):
            char = CHARSET[idx[y, x]]
            if USE_COLORS:
                color = small_color[y, x]
                color_code = get_color_code(color)
                row_chars.append(f"{color_code}{char}")
            else:
                row_chars.append(char)
        rows.append("".join(row_chars))
    
    result = "\n".join(rows)
    if USE_COLORS:
        result += reset_color()
    return result

def clear_screen() -> None:
    sys.stdout.write("\x1b[2J\x1b[H")
    sys.stdout.flush()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python ascii_alnum_dark.py <youtube-url-or-file>")
        sys.exit(1)

    src = sys.argv[1]
    if src.startswith("http"):
        path = download(src)
    else:
        path = src
        if not os.path.exists(path):
            print("File not found:", path)
            sys.exit(1)

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print("Failed to open video.")
        sys.exit(1)

    term_width = shutil.get_terminal_size((TARGET_WIDTH, 40)).columns
    width = min(TARGET_WIDTH, max(40, term_width))

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    fps = min(fps, FPS_CAP)
    frame_delay = 1.0 / fps

    clear_screen()
    last = time.time()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            art = frame_to_ascii(frame, width)
            sys.stdout.write("\x1b[H")
            sys.stdout.write(art + "\n")
            sys.stdout.flush()

            now = time.time()
            sleep_for = frame_delay - (now - last)
            if sleep_for > 0:
                time.sleep(sleep_for)
            last = time.time()
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        print("\nDone.")

if __name__ == "__main__":
    main()
