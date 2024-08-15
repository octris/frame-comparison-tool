import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional
from frame_comparison_tool.utils import put_bordered_text, Align, FrameType


class NoMatchingFrameTypeError(Exception):
    """Raised when no matching frame type is found."""
    pass


class FrameLoader:
    def __init__(self, file_path: Path):
        self._file_path: Path = file_path
        self._video_capture: cv2.VideoCapture = cv2.VideoCapture(str(self._file_path.absolute()))
        self._frames: List[np.ndarray] = []

    @property
    def file_name(self) -> str:
        return self._file_path.name

    @property
    def total_frames(self) -> int:
        return int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def frames(self) -> List[np.ndarray]:
        return self._frames

    def delete_frames(self) -> None:
        if len(self._frames) > 0:
            self._frames.clear()

    def _get_frame(self) -> Optional[cv2.typing.MatLike]:
        if self._video_capture.isOpened():
            success, image = self._video_capture.read()
            if success:
                return image
            else:
                raise RuntimeError(f'Could not read image.')
        else:
            raise RuntimeError(f'Video capture not opened.')

    def _set_frame_idx(self, frame_idx: int) -> bool:
        if self._video_capture.isOpened():
            self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            return True
        else:
            return False

    def _get_frame_by_idx(self, frame_idx: int) -> Optional[cv2.typing.MatLike]:
        if self._set_frame_idx(frame_idx):
            return self._get_frame()

    def _get_frame_type(self) -> FrameType:
        frame_type = int(self._video_capture.get(cv2.CAP_PROP_FRAME_TYPE))
        return FrameType(frame_type)

    def _get_frame_type_by_idx(self, frame_idx: int) -> Optional[FrameType]:
        if self._set_frame_idx(frame_idx):
            return self._get_frame_type()
        else:
            raise RuntimeError('Could not get frame type.')

    def _get_composited_image(self, frame_idx: int) -> np.ndarray:
        frame = self._get_frame_by_idx(frame_idx)
        frame_type = self._get_frame_type_by_idx(frame_idx)
        source = self.file_name

        frame = put_bordered_text(img=frame, text=f'SOURCE: {source}', origin=(0, 0))
        frame = put_bordered_text(img=frame,
                                  text=f'FRAME TYPE: {frame_type.name}\nFRAME: {frame_idx}/{self.total_frames}',
                                  origin=(frame.shape[1], 0), align=Align.RIGHT)
        return frame

    def _find_closest_idx(self, frame_idx: int, frame_type: FrameType) -> int:
        if self._get_frame_type_by_idx(frame_idx) == frame_type:
            return frame_idx

        total_frames = self.total_frames
        l_ptr, r_ptr = frame_idx - 1, frame_idx + 1

        while l_ptr >= 0 and r_ptr < total_frames:
            if l_ptr >= 0 and self._get_frame_type_by_idx(l_ptr) == frame_type:
                return l_ptr

            if r_ptr < total_frames and self._get_frame_type_by_idx(r_ptr) == frame_type:
                return r_ptr

            l_ptr -= 1
            r_ptr += 1

        raise NoMatchingFrameTypeError(f'No {frame_type.value} frame found.')

    def sample_frames(self, frame_ids: List[int], frame_type: FrameType) -> None:
        if len(self._frames) > 0:
            self._frames.clear()

        for idx in frame_ids:
            idx = self._find_closest_idx(idx, frame_type)
            frame = self._get_composited_image(idx)
            self._frames.append((cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
