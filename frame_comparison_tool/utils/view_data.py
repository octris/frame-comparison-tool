from typing import Optional
import numpy as np

from frame_comparison_tool.utils import DisplayMode


class ViewData:
    """
    Class containing data needed for displaying a frame.

    Encapsulates the frame data and the display mode, which is necessary for rendering the frame in the application.
    """

    def __init__(self, frame: Optional[np.ndarray], mode: DisplayMode) -> None:
        """
        Initialize a ``ViewData`` instance.

        :param frame: The frame data as a NumPy array. Can be ``None`` if no frame is provided.
        :param mode: The display mode for the frame. Determines how the frame should be rendered.
        """
        self.frame: Optional[np.ndarray] = frame
        self.mode: DisplayMode = mode
