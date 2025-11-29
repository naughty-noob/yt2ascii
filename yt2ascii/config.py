import os
import sys
import shutil
import json
import argparse
from typing import Any, Dict

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
DEFAULT_CONFIG = {
    "target_width": 120,
    "fps_cap": 24,
    "invert": False,
    "aspect_corr": 0.45,
    "use_colors": True,
    "charset": "detailed",
    "enable_audio": True,
    "frame_cache_size": 100,
    "adaptive_quality": True,
    "auto_detect_terminal": True
}


class Config:
    # configuration manager with file and CLI support
    
    def __init__(self, args: argparse.Namespace):
        self.config = DEFAULT_CONFIG.copy()
        
        # load config file if specified
        if args.config:
            self.load_config_file(args.config)
        
        # override with CLI arguments
        if args.width is not None:
            self.config["target_width"] = args.width
        if args.fps is not None:
            self.config["fps_cap"] = args.fps
        if args.invert:  # only override if explicitly set to True
            self.config["invert"] = True
        if args.no_color:
            self.config["use_colors"] = False
        if args.charset:
            self.config["charset"] = args.charset
        if args.no_audio:
            self.config["enable_audio"] = False
        if args.no_cache:
            self.config["frame_cache_size"] = 0
        if args.no_adaptive:
            self.config["adaptive_quality"] = False
        
        # auto-detect terminal capabilities
        if self.config["auto_detect_terminal"]:
            self.auto_detect_terminal()
    
    def load_config_file(self, path: str):
        # load configuration from YAML or JSON file
        try:
            with open(path, 'r') as f:
                if path.endswith('.yaml') or path.endswith('.yml'):
                    if not YAML_AVAILABLE:
                        print(f"Warning: PyYAML is required for YAML config files. Install with: pip install PyYAML", file=sys.stderr)
                        return
                    file_config = yaml.safe_load(f)
                else:
                    file_config = json.load(f)
                if file_config:
                    self.config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file {path}: {e}", file=sys.stderr)
    
    def auto_detect_terminal(self):
        # auto-detect terminal capabilities
        # check color support
        if not sys.stdout.isatty():
            self.config["use_colors"] = False
        else:
            # check if terminal supports colors
            term = os.environ.get("TERM", "")
            if term in ("dumb", "unknown"):
                self.config["use_colors"] = False
        
        # auto-detect aspect ratio from terminal
        try:
            # try to get terminal font info (heuristic)
            term_width, term_height = shutil.get_terminal_size()
            # estimate aspect ratio (most terminals are ~2:1 character aspect)
            if term_width > 0 and term_height > 0:
                # adjust aspect correction based on terminal size
                self.config["aspect_corr"] = 0.45  # keep default, could be improved
        except Exception:
            pass
    
    def get(self, key: str, default: Any = None):
        # get configuration value
        return self.config.get(key, default)

