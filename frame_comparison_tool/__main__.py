from pathlib import Path
from typing import List
from frame_loader import FrameLoader
import random
import argparse
import tkinter as tk
from tkinter import filedialog
from PIL import Image


# TODO: Add args to Controller


class Controller:
    def __init__(self, n_samples=5):
        self.sources: List[FrameLoader] = []
        self.n_samples = n_samples
        self.curr_src_idx = 0
        self.curr_frame_idx = 0
        self._frame_ids = []

    def add_source(self, file_path: Path) -> None:
        self.sources.append(FrameLoader(Path(file_path)))
        self._sample_frame_ids()

    def _sample_frame_ids(self) -> None:
        random.seed(42)
        min_total_frames = min([source.total_frames for source in self.sources])
        self._frame_ids = sorted([random.randint(0, min_total_frames) for _ in range(self.n_samples)])

        for source in self.sources:
            source.sample_frames(self._frame_ids)


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

        self.bind('<Left>', self._display_next_frame)
        self.bind('<Right>', self._display_next_frame)

        self.bind('<Up>', self._change_source)
        self.bind('<Down>', self._change_source)

    def _change_source(self, event) -> None:
        if event.keysym == 'Down' and self.controller.curr_src_idx > 0:
            self.controller.curr_src_idx -= 1
        elif event.keysym == 'Up' and self.controller.curr_src_idx < len(self.controller.sources) - 1:
            self.controller.curr_src_idx += 1

        frame = self.controller.sources[self.controller.curr_src_idx].frames[self.controller.curr_frame_idx]
        self._display_frame(frame)

    def _display_next_frame(self, event) -> None:
        if event.keysym == 'Left' and self.controller.curr_frame_idx > 0:
            self.controller.curr_frame_idx -= 1

        elif event.keysym == 'Right' and self.controller.curr_frame_idx < self.controller.n_samples - 1:
            self.controller.curr_frame_idx += 1

        frame = self.controller.sources[self.controller.curr_src_idx].frames[self.controller.curr_frame_idx]
        self._display_frame(frame)

    def _display_frame(self, frame: Image) -> None:
        self.image_label.configure(image=frame)

    def _open_file(self) -> None:
        file_path = filedialog.askopenfilename()
        self.controller.add_source(Path(file_path))
        self._display_frame(
            self.controller.sources[self.controller.curr_src_idx].frames[self.controller.curr_frame_idx])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_paths', type=Path, nargs='*')
    args = parser.parse_args()

    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
