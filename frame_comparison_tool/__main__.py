from pathlib import Path
from typing import List
from video_loader import VideoLoader
import cv2
import random
import argparse
import tkinter as tk
from tkinter import filedialog


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self._file_paths = []

        self.title('Frame Comparison Tool')
        self.geometry('500x500')

        self.rowconfigure(0, minsize=400, weight=4)
        self.rowconfigure(1, minsize=100, weight=1)
        self.columnconfigure(0, minsize=500)

        self.frame_image = tk.Frame(self, bg='white')
        self.frame_image.grid(row=0, column=0, sticky="nsew")

        self.frame_button = tk.Frame(self)
        self.frame_button.grid(row=1, column=0, sticky="nsew")

        self.button = tk.Button(self.frame_button, text='Add source', command=self._open_file)
        self.button.pack()

    def _open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self._file_paths.append(Path(file_path))
            display_random_frame(self._file_paths)


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

    # display_random_frame(file_paths=args.file_paths)

    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
