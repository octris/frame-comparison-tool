from pathlib import Path
from typing import Optional, OrderedDict, Callable

import numpy as np

from frame_comparison_tool.utils import FrameLoader, FrameType, Task, DisplayMode, Direction
from frame_comparison_tool.utils.frame_loader_manager import FrameLoaderManager
from frame_comparison_tool.utils.worker import Worker
from loguru import logger


class Model:
    """
    The model class, responsible for backend logic regarding storing and manipulating data.
    """

    def __init__(self, files: Optional[list[Path]], n_samples: int, seed: int,
                 frame_type: FrameType):
        """
        Initializes a ``Model`` instance.
        """

        self.frame_loader_manager = FrameLoaderManager(n_samples=n_samples, seed=seed, frame_type=frame_type)
        """Instance of ``FrameLoaderManager`` responsible for handling all video sources and frames."""
        self.curr_src_idx: int = 0
        """Index of current video source."""
        self.curr_frame_idx: int = 0
        """Range (0, `n_samples - 1`), denotes the frame index inside the `frame_positions` list."""
        self.curr_mode = DisplayMode.SCALED
        """Current display mode."""
        self.max_frame_size: Optional[tuple[int, int]] = None
        """Maximum frame width and height."""

        self.worker = Worker(frame_loader_manager=self.frame_loader_manager)
        self.worker.start()

        if files:
            added_sources = self.add_sources(file_paths=files)
            discarded_sources = list(map(lambda data: str(data[0]), filter(lambda x: not x[1], added_sources)))

            if discarded_sources:
                logger.error(f"Could not add the following files:\n{'\n'.join(discarded_sources)}")

    def exit_app(self) -> None:
        """
        Signals to the worker to stop the running thread.
        """
        if self.worker:
            self.worker.stop()

    def set_on_frames_ready_callback(self, on_frames_ready: Callable) -> None:
        """
        Set callback for when frames are ready.

        :param on_frames_ready: Callback function to execute when frames are ready.
        """
        self.worker.on_frames_ready.connect(on_frames_ready)

    def set_on_task_started_callback(self, on_task_started: Callable) -> None:
        """
        Set callback for when a task starts.

        :param on_task_started: Callback function to execute when task begins.
        """

        self.worker.on_task_started.connect(on_task_started)

    def set_on_task_finished_callback(self, on_task_finished: Callable) -> None:
        """
        Set callback for when a task finishes.

        :param on_task_finished: Callback function to execute when task completes.
        """

        self.worker.on_task_finished.connect(on_task_finished)

    def set_on_task_failed_callback(self, on_task_failed: Callable) -> None:
        """
        Set callback for when a task fails.

        :param on_task_failed: Callback function to execute when task fails.
        """

        self.worker.on_task_failed.connect(on_task_failed)

    def set_on_task_failed_invalid_sources_callback(self, on_task_failed_invalid_sources: Callable) -> None:
        """
        Set callback for when a task fails due to invalid sources.

        :param on_task_failed_invalid_sources: Callback function to execute when task fails due to invalid sources.
        """

        self.worker.on_task_failed_invalid_sources.connect(on_task_failed_invalid_sources)

    @property
    def n_samples(self) -> int:
        """Get number of frames to sample."""
        return self.frame_loader_manager.n_samples

    @property
    def frame_positions(self) -> list[int]:
        """Get list of sampled frame positions."""
        return self.frame_loader_manager.frame_positions

    @property
    def sources(self) -> OrderedDict[Path, FrameLoader]:
        """Get dictionary mapping file paths to their frame loaders."""
        return self.frame_loader_manager.sources

    @property
    def source_count(self) -> int:
        """Get number of loaded video sources."""
        return len(self.sources)

    @property
    def seed(self) -> int:
        """Get current seed value."""
        return self.frame_loader_manager.seed

    @property
    def frame_type(self) -> FrameType:
        """Get current frame type."""
        return self.frame_loader_manager.frame_type

    def update_n_samples(self, n_samples: int) -> None:
        """
        Update number of frames to sample.

        :param n_samples: New number of frames to sample.
        """
        if n_samples != self.n_samples:
            self.frame_loader_manager.update_n_samples(n_samples)

    def update_seed(self, seed: int) -> None:
        """
        Update random seed value.

        :param seed: New random seed value.
        """
        if seed != self.seed:
            self.frame_loader_manager.update_seed(seed)

    def set_frame_type(self, frame_type: FrameType) -> None:
        """
        Set new frame type.

        :param frame_type: New frame type.
        """
        self.frame_loader_manager.frame_type = frame_type

    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        Retrieves current frame of current video source.

        :return: Current frame.
        """
        return self.frame_loader_manager.get_frame(src_idx=self.curr_src_idx, frame_idx=self.curr_frame_idx)

    def add_sources(self, file_paths: list[Path]) -> list[tuple[Path, bool]]:
        """
        Adds video source to the model.

        :param file_paths: Video source string.
        :return: ``True`` if source was successfully added, ``False`` if source already exists.
        """
        added_sources = self.frame_loader_manager.add_source(file_paths=file_paths)
        self.worker.add_task(Task.SAMPLE)
        return added_sources

    def delete_source(self, file_path: Path) -> int:
        """
        Deletes video source from the model.

        :param file_path: Path of the video source to delete.
        :return: Index of deleted source.
        """
        if self.curr_src_idx == len(self.frame_loader_manager.sources) - 1 and self.curr_src_idx > 0:
            self.curr_src_idx -= 1

        src_idx = self.frame_loader_manager.delete_source(file_path)

        if len(self.frame_loader_manager.sources) == 0:
            self.curr_frame_idx = 0

        return src_idx

    def expand_frames(self, n_samples: int) -> None:
        """
        Expands number of sampled frames.

        :param n_samples: New number of frames to sample.
        """

        self.frame_loader_manager.expand_frames(n_samples=n_samples)

    def resample_frames(self) -> None:
        """
        Resample frames from all sources
        """

        self.worker.add_task(Task.RESAMPLE)

    def offset_frame(self, direction: Direction) -> None:
        """
        Replaces current frame with the closest frame of the same frame type in
        a specified direction (backward or forward).

        :param direction: ``Direction`` enum.
        """
        self.worker.add_task(Task.OFFSET,
                             direction=direction,
                             src_idx=self.curr_src_idx,
                             frame_idx=self.curr_frame_idx)
