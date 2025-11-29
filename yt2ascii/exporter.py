import json
import re
import sys
from typing import List

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


def export_to_text(frames: List[str], output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, frame in enumerate(frames):
            f.write(f"=== Frame {i+1} ===\n")
            f.write(frame)
            f.write("\n\n")
    print(f"Exported {len(frames)} frames to {output_path}")


def export_to_gif(frames: List[str], output_path: str, fps: float = 10):
    if not PILLOW_AVAILABLE:
        print("Error: Pillow is required for GIF export. Install with: pip install Pillow")
        return
    
    images = []
    for frame in frames:
        lines = frame.split('\n')
        height = len(lines)
        width = max(len(line) for line in lines) if lines else 1
        
        # create image (using monospace font estimation)
        img = Image.new('RGB', (width * 8, height * 16), color='black')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 14)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
            except:
                font = ImageFont.load_default()
        
        y = 0
        for line in lines:
            # remove ANSI codes for rendering
            clean_line = line
            if '\033[' in clean_line:
                clean_line = re.sub(r'\033\[[0-9;]*m', '', clean_line)
            
            draw.text((0, y), clean_line, font=font, fill='white')
            y += 16
        
        images.append(img)
    
    if images:
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=int(1000 / fps),
            loop=0
        )
        print(f"Exported {len(images)} frames to {output_path}")


def export_to_html(frames: List[str], output_path: str, fps: float = 10):
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ASCII Video</title>
    <style>
        body {
            background: #000;
            color: #fff;
            font-family: 'Courier New', monospace;
            font-size: 8px;
            line-height: 1;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        #container {
            text-align: center;
        }
        #frame {
            white-space: pre;
            display: inline-block;
        }
        #controls {
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            margin: 5px;
            font-size: 14px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="container">
        <div id="frame"></div>
        <div id="controls">
            <button onclick="play()">Play</button>
            <button onclick="pause()">Pause</button>
            <button onclick="stop()">Stop</button>
        </div>
    </div>
    <script>
        const frames = """ + json.dumps(frames) + """;
        let currentFrame = 0;
        let interval = null;
        const fps = """ + str(fps) + """;
        
        function updateFrame() {
            document.getElementById('frame').innerHTML = frames[currentFrame];
        }
        
        function play() {
            if (interval) clearInterval(interval);
            interval = setInterval(() => {
                currentFrame = (currentFrame + 1) % frames.length;
                updateFrame();
            }, 1000 / fps);
            updateFrame();
        }
        
        function pause() {
            if (interval) clearInterval(interval);
        }
        
        function stop() {
            if (interval) clearInterval(interval);
            currentFrame = 0;
            updateFrame();
        }
        
        updateFrame();
    </script>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Exported {len(frames)} frames to {output_path}")

