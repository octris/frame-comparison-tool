import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from frame_comparison_tool.utils import put_bordered_text, Align, FrameType


class NoMatchingFrameTypeError(Exception):
    """Raised when no matching frame type is found."""
    pass


class FrameLoader:
    def __init__(self, file_path: Path):
        self._file_path: Path = file_path
        self._video_capture: cv2.VideoCapture = cv2.VideoCapture(str(self._file_path.absolute()))
        self.frames: List[np.ndarray] = []
        self._total_frames = int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def file_name(self) -> str:
        return self._file_path.name

    @property
    def total_frames(self) -> int:
        return int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def delete_frames(self) -> None:
        if len(self.frames) > 0:
            self.frames.clear()

    def _get_frame(self) -> Optional[cv2.typing.MatLike]:
        if self._video_capture.isOpened():
            success, image = self._video_capture.read()
            if success:
                return image
            else:
                raise RuntimeError(f'Could not read image.')
        else:
            raise RuntimeError(f'Video capture not opened.')

    def _set_frame_idx(self, frame_idx: int) -> None:
        if self._video_capture.isOpened():
            self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        else:
            raise RuntimeError(f'Could not set frame index.')

    def _get_frame_type(self) -> FrameType:
        frame_type = int(self._video_capture.get(cv2.CAP_PROP_FRAME_TYPE))
        return FrameType(frame_type)

    def _get_composited_image(self, frame_idx: int, image: np.ndarray, frame_type: FrameType) -> np.ndarray:
        source = self.file_name

        frame = put_bordered_text(img=image, text=f'SOURCE: {source}', origin=(0, 0))
        frame = put_bordered_text(img=frame,
                                  text=f'FRAME TYPE: {frame_type.name}\nFRAME: {frame_idx}/{self.total_frames}',
                                  origin=(frame.shape[1], 0), align=Align.RIGHT)
        return frame

    def _find_closest_frame(self, frame_idx: int, frame_type: FrameType) -> Tuple[int, np.ndarray]:
        self._set_frame_idx(frame_idx)

        while frame_idx < self.total_frames:
            curr_frame_type = self._get_frame_type()
            curr_frame = self._get_frame()

            if curr_frame_type == frame_type:
                return frame_idx, curr_frame
            else:
                frame_idx += 1

        raise NoMatchingFrameTypeError(f'No {frame_type.value} frame found.')

    # TODO
    def offset(self, frame_position: int, direction: int, frame_type: FrameType) -> Tuple[int, Optional[np.ndarray]]:
        frame_position += direction
        frame: Optional[np.ndarray] = None

        if direction > 0:
            frame_position, image = self._find_closest_frame(frame_position, frame_type)
            frame = self._get_composited_image(frame_position, image, frame_type)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif direction < 0:
            pass
        else:
            raise ValueError(f'Invalid offset value.')

        return frame_position, frame

    def sample_frames(self, frame_ids: List[int], frame_type: FrameType) -> None:
        if len(self.frames) > 0:
            self.frames.clear()

        for idx in frame_ids:
            idx, image = self._find_closest_frame(idx, frame_type)
            frame = self._get_composited_image(idx, image, frame_type)
            self.frames.append((cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
