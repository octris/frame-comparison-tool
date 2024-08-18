from typing import Optional
import numpy as np

from frame_comparison_tool.utils import DisplayMode


class ViewData:
    def __init__(self, frame: Optional[np.ndarray], mode: DisplayMode):
        self.frame: Optional[np.ndarray] = frame
        self.mode: DisplayMode = mode
