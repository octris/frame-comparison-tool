from collections import OrderedDict
from pathlib import Path
from typing import List
from frame_loader import FrameLoader
import random
import tkinter as tk
from tkinter import filedialog
from PIL import Image


class Controller:
    def __init__(self, n_samples=5):
        self.sources: OrderedDict[str, FrameLoader] = OrderedDict()
        self.n_samples = n_samples
        self.curr_src_idx = 0
        self.curr_frame_idx = 0
        self._frame_ids: List[int] = []

    def add_source(self, file_path: Path) -> bool:
        file_path_str = str(file_path.absolute())

        if file_path_str in self.sources:
            return False
        else:
            frame_loader = FrameLoader(Path(file_path))
            self.sources[file_path_str] = frame_loader
            self._sample_frame_ids()
            return True

    def _sample_frame_ids(self) -> None:
        random.seed(42)
        min_total_frames = min([source.total_frames for source in self.sources.values()])
        self._frame_ids = sorted([random.randint(0, min_total_frames) for _ in range(self.n_samples)])

        for source in self.sources.values():
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
        self.frame_sources.grid(row=1, column=0, sticky=tk.EW)

        self.button = tk.Button(self.frame_sources, text='Add Source', command=self._add_source, width=8)
        self.button.grid(sticky=tk.E)

        self.bind('<Left>', self._display_next_frame)
        self.bind('<Right>', self._display_next_frame)

        self.bind('<Up>', self._change_displayed_source)
        self.bind('<Down>', self._change_displayed_source)

    def _change_displayed_source(self, event) -> None:
        if event.keysym == 'Down' and self.controller.curr_src_idx > 0:
            self.controller.curr_src_idx -= 1
        elif event.keysym == 'Up' and self.controller.curr_src_idx < len(self.controller.sources) - 1:
            self.controller.curr_src_idx += 1

        frame = list(self.controller.sources.values())[self.controller.curr_src_idx].frames[
            self.controller.curr_frame_idx]
        self._display_frame(frame)

    def _display_next_frame(self, event) -> None:
        if event.keysym == 'Left' and self.controller.curr_frame_idx > 0:
            self.controller.curr_frame_idx -= 1

        elif event.keysym == 'Right' and self.controller.curr_frame_idx < self.controller.n_samples - 1:
            self.controller.curr_frame_idx += 1

        frame = list(self.controller.sources.values())[self.controller.curr_src_idx].frames[
            self.controller.curr_frame_idx]
        self._display_frame(frame)

    def _display_frame(self, frame: Image) -> None:
        self.image_label.configure(image=frame)

    def _add_source(self) -> None:
        file_path = filedialog.askopenfilename()

        if len(file_path) == 0 or not self.controller.add_source(Path(file_path)):
            return

        self.button.destroy()

        frame = tk.Frame(self.frame_sources)
        frame.grid(sticky=tk.EW)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.columnconfigure(2, weight=0)

        source_label = tk.Label(frame, text=f'Source: {file_path}')
        source_label.grid(row=0, column=0)

        def del_command():
            if file_path in self.controller.sources:
                self.controller.sources.pop(file_path)

            if self.controller.curr_src_idx > 0 and self.controller.curr_src_idx >= len(self.controller.sources):
                self.controller.curr_src_idx -= 1

            if len(self.controller.sources) > 0:
                self._display_frame(list(self.controller.sources.values())[self.controller.curr_src_idx].
                                    frames[self.controller.curr_frame_idx])

            frame.destroy()

        delete_btn = tk.Button(frame, text='Delete', width=8, command=del_command)
        delete_btn.grid(row=0, column=1)

        self.button = tk.Button(self.frame_sources, text='Add Source', command=self._add_source, width=8)
        self.button.grid(sticky=tk.E)

        self._display_frame(
            list(self.controller.sources.values())[self.controller.curr_src_idx].frames[self.controller.curr_frame_idx])


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
