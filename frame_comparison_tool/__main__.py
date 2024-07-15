from pathlib import Path
from typing import List

import cv2
import random
import argparse


def display_random_frame(files: List[Path]) -> None:
    vidcaps = [cv2.VideoCapture(str(file.absolute())) for file in files]

    min_total_frames = min([int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) for vidcap in vidcaps])

    random_frame_idx = random.randint(0, min_total_frames)

    for i, vidcap in enumerate(vidcaps):
        if vidcap.isOpened():
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_idx)
            success, image = vidcap.read()
            
            if success:
                cv2.imshow(f'Random frame in video {i + 1}', image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', type=Path, nargs='+')
    args = parser.parse_args()

    display_random_frame(args.files)


if __name__ == '__main__':
    main()
