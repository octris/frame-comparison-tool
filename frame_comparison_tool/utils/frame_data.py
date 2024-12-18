from dataclasses import dataclass

import numpy as np

from frame_comparison_tool.utils import FrameType


@dataclass(frozen=True)
class FrameData:
    """
    Class containing frame information.
    """

    original_frame_position: int
    """
    Position that was randomly sampled.
    """
    real_frame_position: int
    """
    Real frame position. The first position from the `original_frame_position` that matched the `frame_type`.
    """
    frame: np.ndarray
    """
    Frame to be displayed.
    """
    frame_type: FrameType
    """
    Frame type.
    """
