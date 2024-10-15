import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from frame_comparison_tool.utils import put_bordered_text, Align, FrameType
from frame_comparison_tool.utils.exceptions import NoMatchingFrameTypeError, ImageReadError, VideoCaptureFailed, \
    FrameIndexError, InvalidOffsetError


class FrameLoader:
    """
    A class for loading and managing video frames.
    """

    def __init__(self, file_path: Path):
        """
        Initializes a ``FrameLoader`` instance with a video file.

        :param file_path: Path to the video file to be loaded.
        """
        self._file_path: Path = file_path
        self._video_capture: cv2.VideoCapture = cv2.VideoCapture(str(self._file_path.absolute()))
        self.frames: List[np.ndarray] = []
        self._total_frames = int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def file_name(self) -> str:
        """
        Gets the name of the loaded video file.

        :return: String representing the file name of the selected video.
        """
        return self._file_path.name

    @property
    def total_frames(self) -> int:
        """
        Gets the total number of frames in the loaded video.

        :return: Total number of frames in the selected video.
        """
        return int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def delete_frames(self) -> None:
        """
        Deletes all frames from memory.
        """
        if len(self.frames) > 0:
            self.frames.clear()

    def _get_frame(self) -> Optional[cv2.typing.MatLike]:
        """
        Reads the current frame from the ``VideoCapture`` object.

        :return: Video frame if available, ``None`` otherwise.
        :raises ``ImageReadError``: If frame reading fails.
        :raises ``VideoCaptureFailed``: If the ``VideoCapture`` object is not open.
        """
        if self._video_capture.isOpened():
            success, image = self._video_capture.read()
            if success:
                return image
            else:
                raise ImageReadError()
        else:
            raise VideoCaptureFailed()

    def _set_frame_idx(self, frame_idx: int) -> None:
        """
        Sets the ``VideoCapture`` object to a specific frame index.

        :param frame_idx: Index of the frame to be set.
        :raises ``FrameIndexError``: If the frame index if invalid.
        """
        if self._video_capture.isOpened():
            self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        else:
            raise FrameIndexError(frame_idx)

    def _get_frame_type(self) -> FrameType:
        """
        Retrieves the frame type.

        :return: Frame type of current video frame.
        """
        frame_type = int(self._video_capture.get(cv2.CAP_PROP_FRAME_TYPE))
        return FrameType(frame_type)

    def _get_composited_image(self, frame_idx: int, image: np.ndarray, frame_type: FrameType) -> np.ndarray:
        """
        Gets the frame with added text information.

        :param frame_idx: Index of current frame.
        :param image: Original frame image.
        :param frame_type: Type of the current frame.
        :return: New image with text overlay added.
        """
        source = self.file_name

        frame = put_bordered_text(img=image, text=f'SOURCE: {source}', origin=(0, 0))
        frame = put_bordered_text(img=frame,
                                  text=f'FRAME TYPE: {frame_type.name}\nFRAME: {frame_idx}/{self.total_frames}',
                                  origin=(frame.shape[1], 0), align=Align.RIGHT)
        return frame

    def _find_closest_frame(self, frame_idx: int, frame_type: FrameType) -> Tuple[int, np.ndarray]:
        """
        Returns closest frame of specific frame type, starting from given index.

        Searches for matching frame by increasing the given frame index.

        :param frame_idx: Starting frame index to search from.
        :param frame_type: Desired frame type.
        :return: Tuple containing the index of the found frame and the frame itself.
        :raises ``NoMatchingFrameTypeError``: If no frame of matching type was found.
        """
        self._set_frame_idx(frame_idx)

        while frame_idx < self.total_frames:
            curr_frame_type = self._get_frame_type()
            curr_frame = self._get_frame()

            if curr_frame_type == frame_type:
                return frame_idx, curr_frame
            else:
                frame_idx += 1

        raise NoMatchingFrameTypeError(frame_type.value)

    # TODO
    def offset(self, frame_position: int, direction: int, frame_type: FrameType) -> Tuple[int, Optional[np.ndarray]]:
        """
        Retrieves a new frame based on the current frame index (position), direction, and desired frame type.

        :param frame_position: Current frame position (index).
        :param direction: The moving direction (-1 for backward, 1 for forward).
        :param frame_type: Desired frame type.
        :return: A tuple containing the new frame index and the frame itself.
        :raises ``InvalidOffsetError``: If the passed direction is zero.
        """
        frame_position += direction
        frame: Optional[np.ndarray] = None

        if direction > 0:
            frame_position, image = self._find_closest_frame(frame_position, frame_type)
            frame = self._get_composited_image(frame_position, image, frame_type)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif direction < 0:
            pass
        else:
            raise InvalidOffsetError(direction)

        return frame_position, frame

    def sample_frames(self, frame_ids: List[int], frame_type: FrameType) -> None:
        """
        Samples frames based on the given starting frame indices and desired frame type.

        :param frame_ids: List of starting frame indices.
        :param frame_type: Desired frame type.
        """
        if len(self.frames) > 0:
            self.frames.clear()

        for idx in frame_ids:
            idx, image = self._find_closest_frame(idx, frame_type)
            frame = self._get_composited_image(idx, image, frame_type)
            self.frames.append((cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
