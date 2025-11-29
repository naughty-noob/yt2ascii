from typing import Optional, Dict
from collections import deque


class FrameCache:
    def __init__(self, max_size: int = 100):
        self.cache: Dict[int, str] = {}
        self.max_size = max_size
        self.access_order = deque()
    
    def get(self, frame_num: int) -> Optional[str]:
        if frame_num in self.cache:
            # update access order
            if frame_num in self.access_order:
                self.access_order.remove(frame_num)
            self.access_order.append(frame_num)
            return self.cache[frame_num]
        return None
    
    def put(self, frame_num: int, ascii_frame: str):
        if self.max_size <= 0:
            return
        
        if len(self.cache) >= self.max_size:
            # remove least recently used
            oldest = self.access_order.popleft()
            del self.cache[oldest]
        
        self.cache[frame_num] = ascii_frame
        self.access_order.append(frame_num)
    
    def clear(self):
        self.cache.clear()
        self.access_order.clear()

