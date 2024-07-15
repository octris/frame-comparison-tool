from pathlib import Path
from typing import List, Optional
from cv2_utilities import put_bordered_text, Align
import cv2
import random
import argparse


class VideoLoader:
    def __init__(self, file: Path) -> None:
        self.path = file
        self.filename = file.name
        self.video_capture = cv2.VideoCapture(str(self.path.absolute()))
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.curr_frame_idx = 0

    def get_path(self) -> Path:
        return self.path

    def get_filename(self) -> str:
        return self.filename

    def get_total_frames(self) -> int:
        return self.total_frames

    def set_frame(self, frame_idx) -> None:
        if self.video_capture.isOpened():
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            self.curr_frame_idx = frame_idx

    def get_frame(self) -> Optional[cv2.typing.MatLike]:
        if self.video_capture.isOpened():
            success, image = self.video_capture.read()
            return image if success else None
        else:
            return None

    def get_frame_idx(self) -> int:
        return self.curr_frame_idx

    def get_frame_type(self) -> str:
        frame_type = int(self.video_capture.get(cv2.CAP_PROP_FRAME_TYPE))
        return chr(frame_type) if frame_type in (66, 73, 80) else 'UNKNOWN'

    def show_frame(self) -> None:
        pass


def display_random_frame(files: List[Path]) -> None:
    video_loaders = [VideoLoader(file) for file in files]

    min_total_frames = min([video_loader.get_total_frames() for video_loader in video_loaders])
    random_frame_idx = random.randint(0, min_total_frames)

    for video_loader_idx, video_loader in enumerate(video_loaders):
        video_loader.set_frame(random_frame_idx)

        frame = video_loader.get_frame()
        frame_type = video_loader.get_frame_type()
        source = video_loader.get_filename()

        frame = put_bordered_text(img=frame, text=f'SOURCE: {source}', org=(0, 0))
        frame = put_bordered_text(img=frame, text=f'FRAME TYPE: {frame_type}', org=(400, 0), align=Align.RIGHT)
        frame = put_bordered_text(img=frame,
                                  text=f'FRAME: {video_loader.curr_frame_idx}/{video_loader.total_frames}',
                                  org=(400, 40), align=Align.RIGHT)

        cv2.imshow(f'Random frame in video {video_loader_idx + 1}', frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', type=Path, nargs='+')
    args = parser.parse_args()

    display_random_frame(args.files)


if __name__ == '__main__':
    main()
