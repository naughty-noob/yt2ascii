#!/usr/bin/env python3
import argparse
import os
import sys
import time

import cv2

from .ascii_converter import frame_to_ascii
from .charsets import CHARSETS
from .config import Config
from .exporter import export_to_gif, export_to_html, export_to_text
from .video_downloader import download_video
from .video_player import VideoPlayer


def main():
    parser = argparse.ArgumentParser(
        description="Convert videos to ASCII art and play them in your terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m yt2ascii "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m yt2ascii video.mp4 --width 80 --fps 15
  python -m yt2ascii video.mp4 --charset block --no-color
  python -m yt2ascii video1.mp4 video2.mp4 --export gif output.gif
        """
    )
    
    parser.add_argument("sources", nargs="+", help="YouTube URL(s) or local video file(s)")
    parser.add_argument("--width", type=int, help="Maximum width of ASCII output (default: 120)")
    parser.add_argument("--fps", type=float, help="Maximum FPS for playback (default: 24)")
    parser.add_argument("--invert", action="store_true", help="Flip dark/light mapping")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--charset", choices=list(CHARSETS.keys()), help="Character set preset")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio playback")
    parser.add_argument("--no-cache", action="store_true", help="Disable frame caching")
    parser.add_argument("--no-adaptive", action="store_true", help="Disable adaptive quality")
    parser.add_argument("--config", help="Path to YAML or JSON configuration file")
    parser.add_argument("--export", choices=["text", "gif", "html"], help="Export mode")
    parser.add_argument("--output", help="Output file path for export mode")
    parser.add_argument("--frame-by-frame", action="store_true", help="Start in frame-by-frame mode")
    
    args = parser.parse_args()
    
    config = Config(args)
    player = VideoPlayer(config)
    
    try:
        # handle export mode
        if args.export:
            if not args.output:
                print("Error: --output is required for export mode")
                sys.exit(1)
            
            frames = []
            for source in args.sources:
                if source.startswith("http"):
                    video_path, temp_dir = download_video(source)
                    player.temp_dir = temp_dir
                else:
                    video_path = source
                    if not os.path.exists(video_path):
                        print(f"Error: File not found: {video_path}")
                        sys.exit(1)
                
                player.setup_video(video_path)
                cap = cv2.VideoCapture(video_path)
                
                while True:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    ascii_frame = frame_to_ascii(
                        frame,
                        player.width,
                        player.charset,
                        config.get("invert", False),
                        config.get("aspect_corr", 0.45),
                        config.get("use_colors", True)
                    )
                    frames.append(ascii_frame)
                
                cap.release()
            
            if args.export == "text":
                export_to_text(frames, args.output)
            elif args.export == "gif":
                export_to_gif(frames, args.output, player.fps or 24)
            elif args.export == "html":
                export_to_html(frames, args.output, player.fps or 24)
            
            player.cleanup()
            return
        
        # playback mode
        for i, source in enumerate(args.sources):
            if i > 0:
                print(f"\n--- Playing {i+1}/{len(args.sources)}: {source} ---\n")
                time.sleep(1)
            
            try:
                if source.startswith("http"):
                    video_path, temp_dir = download_video(source)
                    player.temp_dir = temp_dir
                else:
                    video_path = source
                    if not os.path.exists(video_path):
                        print(f"Error: File not found: {video_path}")
                        continue
                
                player.setup_video(video_path)
                
                if args.frame_by_frame:
                    player.paused = True
                
                player.play()
                
            except Exception as e:
                print(f"Error playing {source}: {e}", file=sys.stderr)
                continue
            finally:
                player.cleanup()
                player.quit = False
                player.paused = False
                player.speed = 1.0
                player.frame_cache.clear()
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        player.cleanup()


if __name__ == "__main__":
    main()

