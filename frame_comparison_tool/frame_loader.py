from pathlib import Path
from typing import List, Optional

import numpy

from cv2_utilities import put_bordered_text, Align
from frame_type import FrameType
import cv2
import numpy as np


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

    def _get_frame(self) -> Optional[cv2.typing.MatLike]:
        if self._video_capture.isOpened():
            success, image = self._video_capture.read()
            if success:
                return image
            else:
                raise RuntimeError(f'Could not read image.')
        else:
            raise RuntimeError(f'Video capture not opened.')

    def _get_frame_type(self) -> FrameType:
        frame_type = int(self._video_capture.get(cv2.CAP_PROP_FRAME_TYPE))
        return FrameType(frame_type)

    def _get_composited_image(self, frame_idx) -> numpy.ndarray:
        if self._video_capture.isOpened():
            self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

        frame = self._get_frame()
        frame_type = self._get_frame_type()
        source = self.file_name

        frame = put_bordered_text(img=frame, text=f'SOURCE: {source}', origin=(0, 0))
        frame = put_bordered_text(img=frame,
                                  text=f'FRAME TYPE: {frame_type}\nFRAME: {frame_idx}/{self.total_frames}',
                                  origin=(frame.shape[1], 0), align=Align.RIGHT)
        return frame

    def sample_frames(self, frame_ids: List[int]) -> None:
        if len(self._frames) > 0:
            self._frames.clear()

        for idx in frame_ids:
            frame = self._get_composited_image(idx)
            self._frames.append((cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
