from pathlib import Path
from typing import List, Optional
from cv2_utilities import put_bordered_text, Align
from frame_type import FrameType
import cv2
import random
import argparse


class VideoLoader:
    def __init__(self, file_path: Path):
        self._file_path = file_path
        self.video_capture = cv2.VideoCapture(str(self._file_path.absolute()))
        self._curr_frame_idx = 0

    @property
    def file_name(self) -> str:
        return self._file_path.name

    @property
    def total_frames(self) -> int:
        return int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def set_frame(self, frame_idx) -> None:
        if self.video_capture.isOpened():
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            self._curr_frame_idx = frame_idx

    def get_frame(self) -> Optional[cv2.typing.MatLike]:
        if self.video_capture.isOpened():
            success, image = self.video_capture.read()
            if success:
                return image
            else:
                raise RuntimeError(f'Could not read image.')
        else:
            raise RuntimeError(f'Video capture not opened.')

    def get_frame_type(self) -> FrameType:
        frame_type = int(self.video_capture.get(cv2.CAP_PROP_FRAME_TYPE))
        return FrameType(frame_type)

    def get_composited_image(self) -> cv2.typing.MatLike:
        frame = self.get_frame()
        frame_type = self.get_frame_type()
        source = self.file_name

        frame = put_bordered_text(img=frame, text=f'SOURCE: {source}', origin=(0, 0))
        frame = put_bordered_text(img=frame,
                                  text=f'FRAME TYPE: {frame_type}\nFRAME: {self._curr_frame_idx}/{self.total_frames}',
                                  origin=(frame.shape[1], 0), align=Align.RIGHT)
        return frame
