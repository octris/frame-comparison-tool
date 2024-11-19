import numpy as np
from typing import List, Tuple, Optional, OrderedDict, Callable

from frame_comparison_tool.utils import FrameLoader, FrameType, Operation, DisplayMode, Direction
from frame_comparison_tool.utils.frame_loader_manager import FrameLoaderManager
from frame_comparison_tool.utils.worker import Worker


class Model:
    """
    The model class, responsible for backend logic regarding storing and manipulating data.
    """

    def __init__(self, files: Optional[List[str]], n_samples: int, seed: int,
                 frame_type: FrameType):
        """
        Initializes a ``Model`` instance.
        """

        self.frame_loader_manager = FrameLoaderManager(files=files, n_samples=n_samples, seed=seed,
                                                       frame_type=frame_type)
        """Instance of ``FrameLoaderManager`` responsible for handling all video sources and frames."""
        self.curr_src_idx: int = 0
        """Index of current video source."""
        self.curr_frame_idx: int = 0
        """Range (0, `n_samples - 1`), denotes the frame index inside the `frame_positions` list."""
        self.curr_mode = DisplayMode.SCALED
        """Current display mode."""
        self.max_frame_size: Optional[Tuple[int, int]] = None
        """Maximum frame width and height."""

        self.worker = Worker(frame_loader_manager=self.frame_loader_manager)
        self.worker.start()

    def set_on_frame_sample_callback(self, on_frame_sample: Callable) -> None:
        self.worker.on_frames_ready.connect(on_frame_sample)

    def set_on_offset_frame_callback(self, on_offset_frame: Callable) -> None:
        self.worker.on_offset_done.connect(on_offset_frame)

    @property
    def n_samples(self) -> int:
        return self.frame_loader_manager.n_samples

    @property
    def frame_positions(self) -> List[int]:
        return self.frame_loader_manager.frame_positions

    @property
    def sources(self) -> OrderedDict[str, FrameLoader]:
        return self.frame_loader_manager.sources

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def seed(self) -> int:
        return self.frame_loader_manager.seed

    @property
    def frame_type(self) -> FrameType:
        return self.frame_loader_manager.frame_type

    def update_seed(self, seed: int) -> None:
        if seed != self.seed:
            self.frame_loader_manager.update_seed(seed)

    def set_frame_type(self, frame_type: FrameType) -> None:
        self.frame_loader_manager.frame_type = frame_type

    def get_current_frame(self) -> np.ndarray:
        """
        Retrieves current frame of current video source.

        :return: Current frame.
        """
        return self.frame_loader_manager.get_frame(src_idx=self.curr_src_idx, frame_idx=self.curr_frame_idx)

    def add_source(self, file_paths: List[str]) -> List[Optional[str]]:
        """
        Adds video source to the model.

        :param file_paths: Video source string.
        :return: ``True`` if source was successfully added, ``False`` if source already exists.
        """
        return self.frame_loader_manager.add_source(file_paths=file_paths)

    def delete_source(self, file_path: str) -> int:
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

    def resample_frames(self) -> None:
        self.worker.add_task(Operation.SAMPLE)

    def offset_frame(self, direction: Direction) -> None:
        """
        Replaces current frame with the closest frame of the same type in specified direction (backward or forward).

        :param direction: -1 for backward, 1 for forward.
        """
        self.worker.add_task(Operation.OFFSET,
                             direction=direction,
                             src_idx=self.curr_src_idx,
                             frame_idx=self.curr_frame_idx)
