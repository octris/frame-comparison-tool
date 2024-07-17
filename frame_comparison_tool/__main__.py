from pathlib import Path
from typing import List
from video_loader import VideoLoader
import cv2
import random
import argparse
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


# TODO: Load frames from multiple videos
# TODO: Add args to Controller

class Controller:
    def __init__(self):
        self.sources: List[Path] = []
        self.frames: List[ImageTk.PhotoImage] = []
        self.video_loaders: List[VideoLoader] = []
        self.curr_idx = 0

    def add_source(self, file_path: Path) -> None:
        self.sources.append(file_path)
        self.video_loaders.append(VideoLoader(file_path=file_path))
        self.load_frames()

    def load_frames(self, n: int = 5) -> None:
        if len(self.video_loaders) > 0:
            curr_video_loader = self.video_loaders[-1]
            total_frames = curr_video_loader.total_frames

            random_frame_ids = [random.randint(0, total_frames) for _ in range(n)]

            for idx in random_frame_ids:
                curr_video_loader.set_frame(idx)
                frame = curr_video_loader.get_composited_image()
                self.frames.append(ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))))


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

        self.image_label = tk.Label(master=self.frame_images, bg='white')
        self.image_label.pack()

        self.frame_sources = tk.Frame(self)
        self.frame_sources.grid(row=1, column=0, sticky=tk.NE)

        self.button = tk.Button(self.frame_sources, text='Add source', command=self._open_file)
        self.button.pack()

        self.bind("<Left>", self._display_next_frame)
        self.bind("<Right>", self._display_next_frame)

    def _display_next_frame(self, event) -> None:
        if event.keysym == "Left" and self.controller.curr_idx > 0:
            self.controller.curr_idx -= 1
        elif event.keysym == "Right" and self.controller.curr_idx < len(self.controller.frames) - 1:
            self.controller.curr_idx += 1

        frame = self.controller.frames[self.controller.curr_idx]
        self._display_frame(frame)

    def _display_frame(self, frame: Image) -> None:
        self.image_label.configure(image=frame)

    def _open_file(self) -> None:
        file_path = filedialog.askopenfilename()
        self.controller.add_source(Path(file_path))
        self._display_frame(self.controller.frames[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_paths', type=Path, nargs='*')
    args = parser.parse_args()

    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
