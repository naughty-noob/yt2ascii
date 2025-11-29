import os
import shutil
import subprocess
import sys
import tempfile
from typing import Tuple, Optional


def download_video(url: str, progress_callback: Optional[callable] = None) -> Tuple[str, str]:
    tdir = tempfile.mkdtemp(prefix="ascii_vid_")
    print(f"↓ Downloading to {tdir} ...")
    
    # try multiple format options as fallback
    format_options = [
        "bestvideo[height<=360][fps<=30]+bestaudio/best/best",
        "best[height<=360]/best",
        "best"
    ]
    
    stderr_output = []
    
    for fmt in format_options:
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "-f", fmt,
            "-o", "%(title)s.%(ext)s",
            url
        ]
        
        try:
            # try to show progress
            process = subprocess.Popen(
                cmd,
                cwd=tdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            stderr_lines = []
            for line in process.stderr:
                stderr_lines.append(line)
                if progress_callback and "%" in line:
                    # extract progress if possible
                    progress_callback(line)
                sys.stdout.write(f"\r{line[:80]}")
                sys.stdout.flush()
            
            process.wait()
            stderr_output = stderr_lines
            
            if process.returncode == 0:
                # success! find the downloaded file
                for fn in os.listdir(tdir):
                    if fn.lower().endswith((".mp4", ".mkv", ".webm", ".mov")):
                        return os.path.join(tdir, fn), tdir
                raise RuntimeError("No video file found after download.")
            
            # if we get here, download failed - try next format
            if fmt != format_options[-1]:  # not the last format
                continue
            else:
                # last format failed, raise error with helpful message
                error_msg = "\n".join(stderr_lines[-5:])  # last 5 lines of error
                if "403" in error_msg or "Forbidden" in error_msg:
                    raise RuntimeError(
                        f"Download failed: YouTube blocked the request (403 Forbidden).\n"
                        f"Try:\n"
                        f"  1. Update yt-dlp: pip install --upgrade yt-dlp\n"
                        f"  2. Use a local video file instead\n"
                        f"  3. Check if the video is available\n"
                        f"\nError details: {error_msg}"
                    )
                else:
                    raise subprocess.CalledProcessError(process.returncode, cmd, stderr=error_msg)
                    
        except subprocess.CalledProcessError as e:
            # if it's the last format, re-raise with better message
            if fmt == format_options[-1]:
                error_msg = "\n".join(stderr_output[-5:]) if stderr_output else str(e)
                if "403" in error_msg or "Forbidden" in error_msg:
                    raise RuntimeError(
                        f"Download failed: YouTube blocked the request (403 Forbidden).\n"
                        f"Try:\n"
                        f"  1. Update yt-dlp: pip install --upgrade yt-dlp\n"
                        f"  2. Use a local video file instead\n"
                        f"  3. Check if the video is available\n"
                        f"\nError details: {error_msg}"
                    )
                raise RuntimeError(f"Download failed: {error_msg}")
            continue
        except Exception as e:
            # cleanup on error
            try:
                shutil.rmtree(tdir)
            except:
                pass
            raise
    
    # should never reach here, but just in case
    raise RuntimeError("Download failed with all format options.")

