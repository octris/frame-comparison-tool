from dataclasses import dataclass

import numpy as np

from frame_comparison_tool.utils import FrameType


@dataclass(frozen=True)
class FrameData:
    original_frame_position: int
    real_frame_position: int
    frame: np.ndarray
    frame_type: FrameType
