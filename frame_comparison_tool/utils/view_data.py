from dataclasses import dataclass
from typing import Optional
import numpy as np

from frame_comparison_tool.utils import DisplayMode


@dataclass(frozen=True)
class ViewData:
    """
    Class containing data needed for displaying a frame.

    Encapsulates the frame data and the display mode, which is necessary for rendering the frame in the application.
    """

    frame: Optional[np.ndarray]
    mode: DisplayMode
