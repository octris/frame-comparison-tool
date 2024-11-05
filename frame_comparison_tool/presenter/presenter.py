from typing import Tuple

import numpy as np

from frame_comparison_tool.model import Model
from frame_comparison_tool.utils.exceptions import ZeroDimensionError
from frame_comparison_tool.view import View
from frame_comparison_tool.utils import DisplayMode, ViewData
from frame_comparison_tool.utils import FrameType
from PIL import Image


class Presenter:
    """
    The presenter class. Manages interactions between the ``View`` and ``Model`` objects.
    """

    def __init__(self, model: Model, view: View):
        """
        Initializes the ``Presenter`` with ``Model`` and ``View`` instances.

        :param model: ``Model`` object.
        :param view: ``View`` object.
        """
        self.model: Model = model
        """``Model`` instance."""
        self.model.set_on_frame_sample_callback(self.update_display)

        self.view: View = view
        """``View`` instance."""

        self.view.set_presenter(self)
        self.view.set_init_values(files=model.sources.keys(), seed=self.model.seed,
                                  frame_type=self.model.frame_type,
                                  display_mode=model.curr_mode)
        self._connect_signals()

    def _connect_signals(self) -> None:
        """
        Connect ``View`` signals to corresponding ``Presenter`` methods.
        """
        self.view.add_source_requested.connect(self.add_source)
        self.view.delete_source_requested.connect(self.delete_source)
        self.view.mode_changed.connect(self.change_mode)
        self.view.frame_changed.connect(self.change_frame)
        self.view.source_changed.connect(self.change_source)
        self.view.resize_requested.connect(self.resize_frame)
        self.view.frame_type_changed.connect(self.change_frame_type)
        self.view.offset_changed.connect(self.offset_frame_position)
        self.view.seed_changed.connect(self.change_seed)
        self.view.shown.connect(self.resize_frame)

    def add_source(self, file_path: str) -> None:
        """
        Adds source and updates display.

        :param file_path: Path to video source.
        """
        if self.model.add_source(file_path=file_path):
            self.view.on_add_source(file_path=file_path)
            self.update_display()

    def delete_source(self, file_path: str) -> None:
        """
        Deletes source and updates display.

        :param file_path: Path to video source.
        """
        src_idx = self.model.delete_source(file_path)
        self.view.on_delete_source(src_idx)
        self.update_display()

    def change_seed(self, seed: int):
        """
        Changes random seed and updates display with resampled frames.

        :param seed: New seed.
        """
        self.model.set_seed(seed)
        self.model.resample_frames()
        self.update_display()

    def offset_frame_position(self, direction: int) -> None:
        """
        Offsets the current frame and updates the display.

        :param direction: The direction of the frame offset.
        """
        self.model.offset_frame(direction)
        self.update_display()

    def change_frame_type(self, frame_type: FrameType) -> None:
        """
        Changes the current frame type to the ``Model`` object, resamples frames, and updates the current display.

        :param frame_type: New frame type.
        """
        if self.model.frame_type != frame_type:
            self.model.set_frame_type(frame_type=frame_type)
            self.model.resample_frames()
            self.update_display()

    def change_frame(self, direction: int) -> None:
        """
        Changes the current frame to the ``Model`` object and updates the current display.

        :param direction: The direction of frame change.
        """
        self.model.curr_frame_idx += direction
        self.model.curr_frame_idx = max(0, min(self.model.curr_frame_idx, len(self.model.frame_positions) - 1))
        self.update_display()

    def change_source(self, direction: int) -> None:
        """
        Changes the current source to the ``Model`` object.

        :param direction: The direction of source change.
        """

        self.model.curr_src_idx += direction
        self.model.curr_src_idx = max(0, min(self.model.curr_src_idx, len(self.model.sources) - 1))
        self.update_display()

    def change_mode(self, mode: DisplayMode) -> None:
        """
        Changes the display mode to the ``Model`` object and updates the current display.

        :param mode: New display mode.
        """
        if mode != self.model.curr_mode:
            self.model.curr_mode = mode
            self.update_display()

    def resize_frame(self, frame_size: Tuple[int, int]) -> None:
        """
        Resizes frame to a certain frame size and updates the current display.

        :param frame_size: A tuple containing the desired frame width and height.
        """
        if frame_size != self.model.max_frame_size:
            self.model.max_frame_size = frame_size
            self.update_display()

    def update_display(self) -> None:
        """
        Updates the display with the current frame and selected display mode.
        Applies necessary transformations to the frame.
        """
        mode: DisplayMode = self.model.curr_mode
        view_data: ViewData

        if self.model.source_count == 0:
            view_data = ViewData(frame=None, mode=mode)
        else:
            frame = self.model.get_current_frame()

            if mode == DisplayMode.SCALED:
                frame = self._resize_frame_to_fit(frame)

            view_data = ViewData(frame=frame, mode=mode)

        self.view.update_display(view_data)

    def _resize_frame_to_fit(self, frame: np.ndarray) -> np.ndarray:
        """
        Resizes frame to fit into the scroll area.

        :param frame: Frame to be fitted.
        :return: Resized frame.
        :raises ``ZeroDimensionError``: If either width or height of the scroll area is zero.
        """
        max_frame_size: Tuple[int, int] = self.model.max_frame_size

        if max_frame_size[0] == 0 or max_frame_size[1] == 0:
            raise ZeroDimensionError()

        image = Image.fromarray(frame)
        image.thumbnail(max_frame_size)
        return np.array(image)
