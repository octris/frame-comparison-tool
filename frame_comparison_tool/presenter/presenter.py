from pathlib import Path

import numpy as np
from PIL import Image

from frame_comparison_tool.model import Model
from frame_comparison_tool.utils import DisplayMode, ViewData, FrameType, Direction
from frame_comparison_tool.utils.exceptions import ZeroDimensionError
from frame_comparison_tool.view import View


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
        self._set_init_callbacks()

        self.view: View = view
        """``View`` instance."""

        self.view.set_presenter(self)
        self.view.set_init_values(files=self.model.sources.keys(),
                                  n_samples=self.model.n_samples,
                                  seed=self.model.seed,
                                  frame_type=self.model.frame_type,
                                  display_mode=self.model.curr_mode)
        self._connect_signals()

    def _set_init_callbacks(self):
        self.model.set_on_frames_ready_callback(self.update_display)
        self.model.set_on_task_started_callback(self._start_loading)
        self.model.set_on_task_finished_callback(self._stop_loading)
        self.model.set_on_task_failed_callback(self._stop_task)

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
        self.view.n_samples_changed.connect(self.change_n_samples)
        self.view.shown.connect(self.resize_frame)
        self.view.exit_app_requested.connect(self._exit_app)

    def _exit_app(self) -> None:
        self.model.exit_app()

    def add_source(self, file_paths: list[Path]) -> None:
        """
        Adds source and updates display.

        :param file_paths: Paths to video source.
        """

        added_file_paths: list[tuple[Path, bool]] = self.model.add_sources(file_paths=file_paths)

        if added_file_paths:
            self.view.on_add_sources(file_paths=added_file_paths)
            self.update_display()

    def delete_source(self, file_path: Path) -> None:
        """
        Deletes source and updates display.

        :param file_path: Path to video source.
        """
        src_idx = self.model.delete_source(file_path)
        self.view.on_delete_source(src_idx)
        self.update_display()

    def change_n_samples(self, n_samples: int) -> None:
        self.model.update_n_samples(n_samples=n_samples)
        self.model.expand_frames(n_samples=n_samples)
        self.model.resample_frames()
        self.update_display()

    def change_seed(self, seed: int) -> None:
        """
        Changes random seed and updates display with resampled frames.

        :param seed: New seed.
        """
        self.model.update_seed(seed)
        self.model.resample_frames()
        self.update_display()

    def offset_frame_position(self, direction: Direction) -> None:
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

    def change_frame(self, direction: Direction) -> None:
        """
        Changes the current frame to the ``Model`` object and updates the current display.

        :param direction: The direction of frame change.
        """
        self.model.curr_frame_idx += direction
        self.model.curr_frame_idx %= self.model.n_samples
        self.update_display()

    def change_source(self, direction: Direction) -> None:
        """
        Changes the current source to the ``Model`` object.

        :param direction: The direction of source change.
        """

        self.model.curr_src_idx += direction
        self.model.curr_src_idx %= self.model.source_count
        self.update_display()

    def change_mode(self, mode: DisplayMode) -> None:
        """
        Changes the display mode to the ``Model`` object and updates the current display.

        :param mode: New display mode.
        """
        if mode != self.model.curr_mode:
            self.model.curr_mode = mode
            self.update_display()

    def resize_frame(self, frame_size: tuple[int, int]) -> None:
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

        frame = self.model.get_current_frame()

        if frame is not None and mode == DisplayMode.SCALED:
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
        max_frame_size: tuple[int, int] = self.model.max_frame_size

        if max_frame_size[0] == 0 or max_frame_size[1] == 0:
            raise ZeroDimensionError()

        image = Image.fromarray(frame)
        image.thumbnail(max_frame_size)
        return np.array(image)

    def _start_loading(self) -> None:
        self.view.loading_circle.start()

    def _stop_loading(self) -> None:
        self.view.loading_circle.stop()

    def _stop_task(self, sources: list[Path]) -> None:
        self._stop_loading()
        self.view.display_error_message(
            message=f"A problem occurred with the following video file(s):"
                    f"\n{'\n'.join(str(source) for source in sources)}\n"
                    f"These files WILL BE REMOVED!"
        )
        for source in sources:
            self.delete_source(file_path=source)
        self.update_display()
