from dataclasses import dataclass
from frame_comparison_tool.utils import FrameType
import numpy as np


@dataclass(frozen=True)
class FrameData:
    original_frame_position: int
    real_frame_position: int
    frame: np.ndarray
    frame_type: FrameType
