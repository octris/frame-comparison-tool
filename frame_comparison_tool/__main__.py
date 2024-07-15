import cv2
import random
import argparse


def display_random_frame(file: str) -> None:
    vidcap = cv2.VideoCapture(file)

    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    random_frame_idx = random.randint(0, total_frames)

    vidcap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_idx)

    if vidcap.isOpened():
        success, image = vidcap.read()

        if success:
            cv2.imshow(f'Random frame', image)
            cv2.waitKey(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'))
    args = parser.parse_args()

    display_random_frame(args.file.name)


if __name__ == '__main__':
    main()
