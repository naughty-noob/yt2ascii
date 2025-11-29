import os
import shutil
import sys
import time
from collections import deque
from typing import Optional

import cv2
import numpy as np

from .ascii_converter import frame_to_ascii
from .audio_player import AudioPlayer
from .charsets import CHARSETS
from .config import Config
from .frame_cache import FrameCache
from .keyboard import KeyboardInput
from .utils import clear_screen, format_time


class VideoPlayer:
    def __init__(self, config: Config):
        self.config = config
        self.charset_str = CHARSETS.get(config.get("charset", "detailed"), CHARSETS["detailed"])
        self.charset = np.array(list(self.charset_str))
        self.frame_cache = FrameCache(config.get("frame_cache_size", 100))
        self.audio_player = AudioPlayer(config.get("enable_audio", True))
        self.paused = False
        self.quit = False
        self.speed = 1.0
        self.current_frame = 0
        self.total_frames = 0
        self.video_path = None
        self.temp_dir = None
        self.cap = None
        self.width = None
        self.fps = None
        self.frame_delay = None
        self.start_time = None
        self.last_frame_time = None
        self.frame_times = deque(maxlen=30)  # For adaptive quality
        self.fullscreen = False
    
    def setup_video(self, video_path: str):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")
        
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.fps = min(video_fps, self.config.get("fps_cap", 24))
        self.frame_delay = 1.0 / self.fps
        
        # setup width
        term_width = shutil.get_terminal_size((self.config.get("target_width", 120), 40)).columns
        self.width = min(self.config.get("target_width", 120), max(40, term_width))
        
        # load audio
        if self.config.get("enable_audio", True):
            self.audio_player.load_audio(video_path)
    
    def handle_input(self, key: Optional[str]):
        if not key:
            return
        
        if key == 'SPACE':
            self.paused = not self.paused
            if self.paused:
                self.audio_player.stop()
            else:
                self.audio_player.play()
        elif key == 'Q' or key == 'q':
            self.quit = True
        elif key == 'LEFT':
            # seek backward 5 seconds
            if self.cap:
                current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
                new_pos = max(0, current_pos - 5 * fps)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
                self.frame_cache.clear()
        elif key == 'RIGHT':
            # seek forward 5 seconds
            if self.cap:
                current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
                new_pos = min(self.total_frames, current_pos + 5 * fps)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
                self.frame_cache.clear()
        elif key == 'PLUS' or key == '=':
            self.speed = min(3.0, self.speed + 0.25)
        elif key == 'MINUS' or key == '-':
            self.speed = max(0.25, self.speed - 0.25)
        elif key == 'F' or key == 'f':
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                term_width = shutil.get_terminal_size().columns
                self.width = term_width
            else:
                term_width = shutil.get_terminal_size().columns
                self.width = min(self.config.get("target_width", 120), max(40, term_width))
            self.frame_cache.clear()
        elif key == 'ENTER':
            # frame-by-frame mode toggle (step one frame)
            if self.paused and self.cap:
                ok, _ = self.cap.read()
                if ok:
                    self.current_frame += 1
    
    def get_frame_ascii(self, frame_num: int) -> str:
        cached = self.frame_cache.get(frame_num)
        if cached:
            return cached
        
        # convert frame
        if not self.cap:
            return ""
        
        # save current position
        saved_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ok, frame = self.cap.read()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, saved_pos)
        
        if not ok:
            return ""
        
        ascii_frame = frame_to_ascii(
            frame,
            self.width,
            self.charset,
            self.config.get("invert", False),
            self.config.get("aspect_corr", 0.45),
            self.config.get("use_colors", True)
        )
        
        self.frame_cache.put(frame_num, ascii_frame)
        return ascii_frame
    
    def play(self):
        clear_screen()
        
        if self.config.get("enable_audio", True):
            self.audio_player.play()
        
        self.start_time = time.time()
        self.last_frame_time = time.time()
        
        with KeyboardInput() as kb:
            try:
                while not self.quit:
                    # handle input
                    key = kb.get_key()
                    self.handle_input(key)
                    
                    if self.quit:
                        break
                    
                    if self.paused:
                        time.sleep(0.1)
                        continue
                    
                    # read frame
                    ok, frame = self.cap.read()
                    if not ok:
                        break
                    
                    self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                    
                    # convert to ASCII
                    frame_start = time.time()
                    ascii_art = frame_to_ascii(
                        frame,
                        self.width,
                        self.charset,
                        self.config.get("invert", False),
                        self.config.get("aspect_corr", 0.45),
                        self.config.get("use_colors", True)
                    )
                    frame_time = time.time() - frame_start
                    self.frame_times.append(frame_time)
                    
                    # adaptive quality
                    if self.config.get("adaptive_quality", True) and len(self.frame_times) > 10:
                        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                        if avg_frame_time > self.frame_delay * 0.8:
                            # slow down if we're taking too long
                            self.fps = max(10, self.fps - 1)
                            self.frame_delay = 1.0 / self.fps
                    
                    # display
                    current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    total_time = (self.total_frames / (self.cap.get(cv2.CAP_PROP_FPS) or 30.0))
                    progress = f"{format_time(current_time)} / {format_time(total_time)}"
                    speed_indicator = f"Speed: {self.speed:.2f}x" if self.speed != 1.0 else ""
                    status = f"{progress} {speed_indicator}".strip()
                    
                    sys.stdout.write("\x1b[H")  # move cursor to top
                    sys.stdout.write(ascii_art)
                    sys.stdout.write(f"\n{status}\n")
                    sys.stdout.flush()
                    
                    # frame timing
                    now = time.time()
                    sleep_for = (self.frame_delay / self.speed) - (now - self.last_frame_time)
                    if sleep_for > 0:
                        time.sleep(sleep_for)
                    self.last_frame_time = time.time()
                    
            except KeyboardInterrupt:
                pass
            finally:
                self.audio_player.stop()
                if self.cap:
                    self.cap.release()
                print("\nDone.")
    
    def cleanup(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Warning: Could not remove temp directory: {e}", file=sys.stderr)

