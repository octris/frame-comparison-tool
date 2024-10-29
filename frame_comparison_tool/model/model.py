import numpy as np
from typing import List, Tuple, Optional, OrderedDict

from frame_comparison_tool.utils import FrameLoader, FrameType
from frame_comparison_tool.utils import DisplayMode
from frame_comparison_tool.utils.frame_loader_manager import FrameLoaderManager


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

    @property
    def frame_positions(self) -> List[int]:
        return self.frame_loader_manager.frame_positions

    @property
    def sources(self) -> OrderedDict[str, FrameLoader]:
        return self.frame_loader_manager.sources

    @property
    def source_count(self) -> int:
        return self.frame_loader_manager.source_count

    @property
    def seed(self) -> int:
        return self.frame_loader_manager.seed

    @property
    def frame_type(self) -> FrameType:
        return self.frame_loader_manager.frame_type

    def set_seed(self, seed: int) -> None:
        self.frame_loader_manager.seed = seed

    def set_frame_type(self, frame_type: FrameType) -> None:
        self.frame_loader_manager.frame_type = frame_type

    def get_current_source(self) -> FrameLoader:
        """
        Retrieves current video source.

        :return: ``FrameLoader`` object representing current source.
        """
        return self.frame_loader_manager.get_source(self.curr_src_idx)

    def get_current_frame(self) -> np.ndarray:
        """
        Retrieves current frame of current video source.

        :return: Current frame.
        """
        return self.get_current_source().frames[self.curr_frame_idx]

    def add_source(self, file_path: str) -> bool:
        """
        Adds video source to the model.

        :param file_path: Video source string.
        :return: ``True`` if source was successfully added, ``False`` if source already exists.
        """
        return self.frame_loader_manager.add_source(file_path)

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
        self.frame_loader_manager.resample_frames()

    def offset_frame(self, direction: int) -> None:
        """
        Replaces current frame with the closest frame of the same type in specified direction (backward or forward).

        :param direction: -1 for backward, 1 for forward.
        """
        self.frame_loader_manager.offset_frame(direction=direction, src_idx=self.curr_src_idx,
                                               frame_idx=self.curr_frame_idx)
