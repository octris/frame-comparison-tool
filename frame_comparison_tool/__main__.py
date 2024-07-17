from pathlib import Path
from typing import List
from video_loader import VideoLoader
import cv2
import random
import argparse
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class Controller:
    def __init__(self):
        self.sources: List[Path] = []
        self.frames: List[ImageTk.PhotoImage] = []
        self.video_loaders: List[VideoLoader] = []

    def add_source(self, file_path: Path) -> None:
        self.sources.append(file_path)
        self.video_loaders.append(VideoLoader(file_path=file_path))
        self.load_frame()

    def load_frame(self) -> None:
        if len(self.video_loaders) > 0:
            curr_video_loader = self.video_loaders[-1]
            total_frames = curr_video_loader.total_frames
            random_frame_idx = random.randint(0, total_frames)

            curr_video_loader.set_frame(random_frame_idx)
            frame = curr_video_loader.get_composited_image()

            self.frames.append(ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))))

    def get_frame(self) -> ImageTk:
        return self.frames[-1]


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.controller = Controller()

        self.title('Frame Comparison Tool')
        self.geometry('1000x600')

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=1)

        self.frame_images = tk.Frame(self, bg='white')
        self.frame_images.grid(row=0, column=0, sticky=tk.NSEW)

        self.frame_sources = tk.Frame(self)
        self.frame_sources.grid(row=1, column=0, sticky=tk.NE)

        self.button = tk.Button(self.frame_sources, text='Add source', command=self._open_file)
        self.button.pack()

    def _display_frame(self, frame: ImageTk) -> None:
        tk.Label(master=self.frame_images, image=frame).pack()

    def _open_file(self) -> None:
        file_path = filedialog.askopenfilename()
        self.controller.add_source(Path(file_path))
        frame = self.controller.get_frame()
        self._display_frame(frame)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_paths', type=Path, nargs='*')
    args = parser.parse_args()

    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
