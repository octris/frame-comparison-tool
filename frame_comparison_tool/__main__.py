from pathlib import Path
from typing import List, Optional
from cv2_utilities import put_bordered_text, Align
from frame_type import FrameType
import cv2
import random
import argparse


class VideoLoader:
    def __init__(self, file_path: Path) -> None:
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


def display_random_frame(file_paths: List[Path]) -> None:
    video_loaders = [VideoLoader(file_path) for file_path in file_paths]

    min_total_frames = min([video_loader.total_frames for video_loader in video_loaders])
    random_frame_idx = random.randint(0, min_total_frames)

    for video_loader_idx, video_loader in enumerate(video_loaders):
        video_loader.set_frame(random_frame_idx)
        frame = video_loader.get_composited_image()
        cv2.imshow(f'Random frame in video {video_loader_idx + 1}', frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file_paths', type=Path, nargs='+')
    args = parser.parse_args()

    display_random_frame(file_paths=args.file_paths)


if __name__ == '__main__':
    main()
