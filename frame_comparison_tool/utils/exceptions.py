from pathlib import Path

from frame_comparison_tool.utils.align import Align
from frame_comparison_tool.utils.direction import Direction
from frame_comparison_tool.utils.frame_type import FrameType
from frame_comparison_tool.utils.task import Task


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


class ImageReadError(Exception):
    """
    Raised when ``cv2.VideoCapture`` instance could not return image.
    """

    def __init__(self, source: Path, message="Could not read image") -> None:
        """
        Initialize an ``ImageReadError`` instance.

        :param message: Error message to display.
        """
        self.source = source
        self.message = message
        super().__init__(self.message)


class MultipleSourcesImageReadError(Exception):
    """
    Raised when ``ImageReadError`` occurs multiple times.
    """

    def __init__(self, errors: list[ImageReadError or VideoCaptureFailed]):
        """
        Initialize a ``MultipleSourcesImageReadError`` instance.

        :param errors: List of ``ImageReadError`` instances.
        """

        self.sources: list[Path] = [error.source for error in errors]
        self.message = f"Could not read image from one or multiple sources."
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


class FramePositionError(Exception):
    """
    Raised when an invalid frame position is supplied.
    """

    def __init__(self, pos: int) -> None:
        """
        Initialize a ``FramePositionError`` instance.

        :param pos: Position of frame in video, range (0, `total_frames - 1`)
        """
        self.message = f"Could not set frame at position {pos}"
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


class InvalidDirectionError(ValueError):
    """
    Raised when an invalid ``Direction`` option is supplied.
    """

    def __init__(self, direction: Direction) -> None:
        """
        Initialize an ``InvalidDirectionError`` instance.

        :param direction: Enum representing the direction of the offset.
        """
        self.message = f"Invalid offset value: {direction.value}"
        super().__init__(self.message)


class InvalidTaskError(ValueError):
    """
    Raised when an invalid ``Operation`` option is supplied.
    """

    def __init__(self, task: Task) -> None:
        self.message = f"Invalid task value supplied: {task}"
        super().__init__(self.message)
