import os
import subprocess
import tempfile
import sys

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class AudioPlayer:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and PYGAME_AVAILABLE
        self.sound = None
        self.channel = None
        if self.enabled:
            try:
                pygame.mixer.init()
                self.channel = pygame.mixer.Channel(0)
            except Exception as e:
                print(f"Warning: Could not initialize audio: {e}", file=sys.stderr)
                self.enabled = False
    
    def load_audio(self, video_path: str) -> bool:
        if not self.enabled:
            return False
        
        try:
            # extract audio using ffmpeg
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_audio.close()
            
            cmd = [
                'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
                '-ar', '44100', '-ac', '2', '-y', temp_audio.name
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            self.sound = pygame.mixer.Sound(temp_audio.name)
            os.unlink(temp_audio.name)  # clean up temp file
            return True
        except Exception as e:
            print(f"Warning: Could not load audio: {e}", file=sys.stderr)
            return False
    
    def play(self, loops: int = 0):
        # play audio
        if self.enabled and self.sound:
            self.channel.play(self.sound, loops=loops)
    
    def stop(self):
        # stop audio
        if self.enabled and self.channel:
            self.channel.stop()
    
    def set_volume(self, volume: float):
        # set volume (0.0 to 1.0)
        if self.enabled and self.sound:
            self.sound.set_volume(volume)

