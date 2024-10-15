from frame_comparison_tool.utils.frame_type import FrameType
from frame_comparison_tool.utils.align import Align


class NoMatchingFrameTypeError(Exception):
    """
    Raised when frame of certain type could not be found.
    """

    def __init__(self, frame_type: FrameType) -> None:
        """
        Initialize a ``NoMatchingFrameTypeError`` instance.

        :param frame_type: Target frame type.
        """
        self.message = f"Could not find frame that matches type {frame_type}"
        super().__init__(self.message)


class ImageReadError(Exception):
    """
    Raised when ``cv2.VideoCapture`` instance could not return image.
    """

    def __init__(self, message="Could not read image") -> None:
        """
        Initialize an ``ImageReadError`` instance.

        :param message: Error message to display.
        """
        self.message = message
        super().__init__(self.message)


class VideoCaptureFailed(Exception):
    """
    Raised when ``cv2.VideoCapture`` instance could not be opened.
    """

    def __init__(self, message="Video capture not opened") -> None:
        """
        Initialize a ``VideoCaptureFailed`` instance.

        :param message: Error message to display.
        """
        self.message = message
        super().__init__(self.message)


class FrameIndexError(Exception):
    """
    Raised when an invalid frame index is supplied.
    """

    def __init__(self, idx: int) -> None:
        """
        Initialize a ``FrameIndexError`` instance.

        :param idx: Index of frame in video.
        """
        self.message = f"Could not set frame at index {idx}"
        super().__init__(self.message)


class InvalidOffsetError(ValueError):
    """
    Raised when offset direction is zero.
    """

    def __init__(self, direction: int) -> None:
        """
        Initialize an ``InvalidOffsetError`` instance.

        :param direction: Direction of offset.
        """
        self.message = f"Invalid offset value: {direction}"
        super().__init__(self.message)


class InvalidAlignmentError(ValueError):
    """
    Raised when an invalid ``Align`` option is supplied.
    """

    def __init__(self, align: Align) -> None:
        """
        Initialize an ``InvalidAlignmentError`` instance.

        :param align: Alignment option.
        """
        self.message = f"Invalid align value supplied: {align}"
        super().__init__(self.message)


class ZeroDimensionError(ValueError):
    """
    Raised when either image (frame) width or height is zero.
    """

    def __init__(self) -> None:
        """
        Initialize a ``ZeroDimensionError`` instance.
        """
        self.message = f"Width or height cannot be zero"
        super().__init__(self.message)
