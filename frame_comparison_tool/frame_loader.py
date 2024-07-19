from pathlib import Path
from typing import List, Optional
from cv2_utilities import put_bordered_text, Align
from frame_type import FrameType
import cv2
from PIL import Image, ImageTk


class FrameLoader:
    def __init__(self, file_path: Path):
        self._file_path: Path = file_path
        self._video_capture: cv2.VideoCapture = cv2.VideoCapture(str(self._file_path.absolute()))
        self._curr_frame_idx: int = 0
        self.frames: List[Image] = []

    @property
    def file_name(self) -> str:
        return self._file_path.name

    @property
    def total_frames(self) -> int:
        return int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def _set_frame(self, frame_idx) -> None:
        if self._video_capture.isOpened():
            self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            self._curr_frame_idx = frame_idx

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

    def _get_composited_image(self) -> Image:
        frame = self._get_frame()
        frame_type = self._get_frame_type()
        source = self.file_name

        frame = put_bordered_text(img=frame, text=f'SOURCE: {source}', origin=(0, 0))
        frame = put_bordered_text(img=frame,
                                  text=f'FRAME TYPE: {frame_type}\nFRAME: {self._curr_frame_idx}/{self.total_frames}',
                                  origin=(frame.shape[1], 0), align=Align.RIGHT)
        return frame

    def sample_frames(self, frame_ids: List[int]) -> None:
        if len(self.frames) > 0:
            self.frames.clear()

        for idx in frame_ids:
            self._set_frame(idx)
            frame = self._get_composited_image()
            self.frames.append(ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))))
