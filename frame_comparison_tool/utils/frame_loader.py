from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from frame_comparison_tool.utils import put_bordered_text, Align, FrameType, Direction
from frame_comparison_tool.utils.exceptions import NoMatchingFrameTypeError, ImageReadError, VideoCaptureFailed, \
    FramePositionError, InvalidDirectionError
from frame_comparison_tool.utils.frame_data import FrameData


class FrameLoader:
    """
    A class for loading and managing video frames from a video file.

    This class provides functionality to:
    - Load frames from a video file
    - Navigate between frames
    - Sample frames of specific frame type
    - Add text (containing information about the frame) to each frame

    The loader maintains the internal state of loaded frames and their metadata.
    """

    def __init__(self, file_path: Path):
        """
        Initializes a ``FrameLoader`` instance with a video file.

        :param file_path: Path to the video file to be loaded.
        """
        self._file_path: Path = file_path
        self._video_capture: cv2.VideoCapture = cv2.VideoCapture(filename=str(self._file_path.absolute()))
        self.frame_data: list[FrameData] = []
        self._total_frames: int = int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

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
        return self._total_frames

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
                raise ImageReadError(source=self._file_path)
        else:
            raise VideoCaptureFailed()

    def _set_frame_pos(self, frame_position: int) -> None:
        """
        Sets the ``VideoCapture`` object to a specific frame position.

        :param frame_position: Position of the frame to be set.
        :raises ``FramePositionError``: If the frame position if invalid.
        """
        if self._video_capture.isOpened():
            self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
        else:
            raise FramePositionError(frame_position)

    def _get_frame_type(self) -> FrameType:
        """
        Retrieves the frame type. Should only be used after the frame position is set in the ``VideoCapture`` object.

        :return: Frame type of current video frame.
        """
        frame_type = int(self._video_capture.get(cv2.CAP_PROP_FRAME_TYPE))
        return FrameType(frame_type)

    def _get_composited_image(self, frame_position: int, image: np.ndarray, frame_type: FrameType) -> np.ndarray:
        """
        Gets the frame with added text information.

        :param frame_position: Position of current frame.
        :param image: Original frame image.
        :param frame_type: Type of the current frame.
        :return: New image with text overlay added.
        """
        source = self.file_name

        frame = put_bordered_text(img=image, text=f'SOURCE: {source}', origin=(0, 0))
        frame = put_bordered_text(img=frame,
                                  text=f'FRAME TYPE: {frame_type.name}\nFRAME: {frame_position}/{self.total_frames}',
                                  origin=(frame.shape[1], 0), align=Align.RIGHT)
        return frame

    def _find_closest_frame(self, frame_position: int, direction: Direction, frame_type: FrameType) \
            -> tuple[int, np.ndarray]:
        """
        Returns closest frame of specific frame type, starting from given position.

        :param frame_position: Starting frame position to search from.
        :param frame_type: Desired frame type.
        :return: Tuple containing the position of the found frame and the frame itself.
        :raises ``NoMatchingFrameTypeError``: If no frame of matching type was found.
        """
        self._set_frame_pos(frame_position)

        while 0 <= frame_position < self.total_frames:
            curr_frame_type = self._get_frame_type()
            curr_frame = self._get_frame()

            if curr_frame_type == frame_type:
                return frame_position, curr_frame
            else:
                frame_position += direction

            if direction == Direction.BACKWARD and frame_position >= 0:
                self._set_frame_pos(frame_position)

        raise NoMatchingFrameTypeError(frame_type.value)

    def offset(self, frame_idx: int, direction: Direction) -> None:
        """
        Retrieves a new frame based on the current frame position, direction, and desired frame type.

        :param frame_idx: Current frame index.
        :param direction: Enum representing the moving direction.
        :return: A tuple containing the new frame's position and the frame itself.
        :raises ``InvalidOffsetError``: If the passed direction is zero.
        """

        starting_position: int = self.frame_data[frame_idx].real_frame_position + direction
        frame_type: FrameType = self.frame_data[frame_idx].frame_type

        if direction == Direction.FORWARD or direction == Direction.BACKWARD:
            real_frame_position, frame = self._get_next_frame(frame_position=starting_position,
                                                              direction=direction,
                                                              frame_type=frame_type)
        else:
            raise InvalidDirectionError(direction)

        frame_data = FrameData(original_frame_position=starting_position,
                               real_frame_position=real_frame_position,
                               frame=frame,
                               frame_type=frame_type)

        self.frame_data[frame_idx] = frame_data

    def _get_next_frame(self, frame_position: int, direction: Direction, frame_type: FrameType) \
            -> tuple[int, np.ndarray]:
        """
        Retrieves the next frame in the specified search direction that matches the frame type.
        Adds information text to the found frame.

        :param frame_position: Starting frame position.
        :param direction: Indicates either forward or backward search.
        :param frame_type: Desired frame type.
        :return: Tuple containing the frame position of the new frame and the new frame itself.
        """

        new_frame_position, image = self._find_closest_frame(frame_position=frame_position,
                                                             direction=direction,
                                                             frame_type=frame_type)
        frame = self._get_composited_image(frame_position=new_frame_position, image=image, frame_type=frame_type)
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2RGB)

        return new_frame_position, frame

    def sample_frames(self, frame_positions: list[int], frame_type: FrameType) -> None:
        """
        Samples frames based on the given starting frame indices and desired frame type.

        :param frame_positions: List of starting frame positions.
        :param frame_type: Desired frame type.
        """
        buffer: list[tuple[int, FrameData]] = []

        for idx, original_frame_position in enumerate(frame_positions):
            if (self.frame_data
                    and idx < len(self.frame_data)
                    and self.frame_data[idx].original_frame_position == original_frame_position
                    and self.frame_data[idx].frame_type == frame_type):
                continue

            real_frame_position, frame = self._get_next_frame(frame_position=original_frame_position,
                                                              direction=Direction(1),
                                                              frame_type=frame_type)
            frame_data = FrameData(original_frame_position=original_frame_position,
                                   real_frame_position=real_frame_position,
                                   frame=frame,
                                   frame_type=frame_type)

            buffer.append((idx, frame_data))

        if self.frame_data:
            for idx, data in buffer:
                # noinspection PyTypeChecker
                if idx < len(self.frame_data):
                    self.frame_data[idx] = data  # type: ignore
                else:
                    self.frame_data.append(data)
        else:
            self.frame_data.extend(data[1] for data in buffer)
