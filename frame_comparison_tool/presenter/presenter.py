from pathlib import Path
from typing import Tuple

import numpy as np

from frame_comparison_tool.model import Model
from frame_comparison_tool.view import View, ViewData, DisplayMode
from PIL import Image


class Presenter:
    def __init__(self, model: Model, view: View):
        self.model: Model = model
        self.view: View = view
        self.view.set_presenter(self)

    def add_source(self, file_path: Path) -> bool:
        if self.model.add_source(file_path):
            self.update_display()
            return True
        else:
            return False

    def delete_source(self, file_path: str) -> int:
        idx = self.model.delete_source(file_path)
        self.update_display()
        return idx

    def change_frame(self, direction: int) -> None:
        self.model.curr_frame_idx += direction
        self.model.curr_frame_idx = max(0, min(self.model.curr_frame_idx, len(self.model.frame_ids) - 1))
        self.update_display()

    def change_source(self, direction: int) -> None:
        self.model.curr_src_idx += direction
        self.model.curr_src_idx = max(0, min(self.model.curr_src_idx, len(self.model.sources) - 1))
        self.update_display()

    def change_mode(self, mode: DisplayMode) -> None:
        if mode != self.model.curr_mode:
            self.model.curr_mode = mode
            self.update_display()

    def resize_frame(self, frame_size: Tuple[int, int]) -> None:
        if frame_size != self.model.max_frame_size:
            self.set_max_frame_size(max_frame_size=frame_size)
            self.update_display()

    def set_max_frame_size(self, max_frame_size: Tuple[int, int]) -> None:
        self.model.max_frame_size = max_frame_size

    def update_display(self) -> None:
        mode: DisplayMode = self.model.curr_mode
        view_data: ViewData

        if len(self.model.sources) == 0:
            view_data = ViewData(frame=None, mode=mode)
        else:
            frame = self.model.get_current_frame()

            if mode == DisplayMode.SCALED:
                frame = self._resize_frame_to_fit(frame)

            view_data = ViewData(frame=frame, mode=mode)

        self.view.update_display(view_data)

    def _resize_frame_to_fit(self, frame: np.ndarray) -> np.ndarray:
        max_frame_size: Tuple[int, int] = self.model.max_frame_size
        image = Image.fromarray(frame)
        image.thumbnail(max_frame_size)
        return np.array(image)
