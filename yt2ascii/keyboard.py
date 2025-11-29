import sys
import select
from typing import Optional

if sys.platform != 'win32':
    import termios
    import tty
else:
    import msvcrt


class KeyboardInput:
    def __init__(self):
        self.old_settings = None
        if sys.platform != 'win32':
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def has_input(self) -> bool:
        if sys.platform == 'win32':
            return msvcrt.kbhit()
        else:
            return select.select([sys.stdin], [], [], 0)[0] != []
    
    def get_key(self) -> Optional[str]:
        if not self.has_input():
            return None
        
        if sys.platform == 'win32':
            key = msvcrt.getch()
            if key == b'\xe0':  # arrow key prefix
                key = msvcrt.getch()
                if key == b'K':
                    return 'LEFT'
                elif key == b'M':
                    return 'RIGHT'
                elif key == b'H':
                    return 'UP'
                elif key == b'P':
                    return 'DOWN'
            elif key == b' ':
                return 'SPACE'
            elif key == b'q' or key == b'Q':
                return 'Q'
            elif key == b'f' or key == b'F':
                return 'F'
            elif key == b'+' or key == b'=':
                return 'PLUS'
            elif key == b'-' or key == b'_':
                return 'MINUS'
            elif key == b'\r':
                return 'ENTER'
            elif key == b'\x1b':  # ESC
                return 'ESC'
            try:
                return key.decode('utf-8', errors='ignore')
            except:
                return None
        else:
            key = sys.stdin.read(1)
            if key == '\x1b':  # ESC sequence
                try:
                    key += sys.stdin.read(2)
                    if key == '\x1b[D':
                        return 'LEFT'
                    elif key == '\x1b[C':
                        return 'RIGHT'
                    elif key == '\x1b[A':
                        return 'UP'
                    elif key == '\x1b[B':
                        return 'DOWN'
                except:
                    return 'ESC'
            elif key == ' ':
                return 'SPACE'
            elif key == 'q' or key == 'Q':
                return 'Q'
            elif key == 'f' or key == 'F':
                return 'F'
            elif key == '+':
                return 'PLUS'
            elif key == '-':
                return 'MINUS'
            elif key == '\n':
                return 'ENTER'
            return key

