import cv2
import numpy as np
from typing import Tuple


def rgb_to_ansi(r: int, g: int, b: int) -> int:
    # convert RGB to ANSI color code
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


def get_color_code(bgr_color: np.ndarray, use_colors: bool) -> str:
    # get ANSI color code for BGR color
    if not use_colors:
        return ""
    
    b, g, r = bgr_color
    ansi_code = rgb_to_ansi(int(r), int(g), int(b))
    return f"\033[38;5;{ansi_code}m"


def reset_color(use_colors: bool) -> str:
    return "\033[0m" if use_colors else ""


def frame_to_ascii(
    frame: np.ndarray,
    width: int,
    charset: np.ndarray,
    invert: bool,
    aspect_corr: float,
    use_colors: bool
) -> str:
    # convert video frame to ASCII art
    h, w = frame.shape[:2]
    new_w = width
    new_h = max(1, int(h * (new_w / w) * aspect_corr))
    
    # resize both color and grayscale versions
    small_color = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small_gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    norm = small_gray.astype(np.float32) / 255.0
    if invert:
        norm = 1.0 - norm
    idx = (norm * (len(charset) - 1)).astype(np.int32)
    
    rows = []
    for y in range(new_h):
        row_chars = []
        for x in range(new_w):
            char = charset[idx[y, x]]
            if use_colors:
                color = small_color[y, x]
                color_code = get_color_code(color, use_colors)
                row_chars.append(f"{color_code}{char}")
            else:
                row_chars.append(char)
        rows.append("".join(row_chars))
    
    result = "\n".join(rows)
    if use_colors:
        result += reset_color(use_colors)
    return result

