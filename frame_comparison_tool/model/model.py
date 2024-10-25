import random
from pathlib import Path

import numpy as np
from collections import OrderedDict
from typing import List, Tuple, Optional

from frame_comparison_tool.utils import FrameLoader, FrameType
from frame_comparison_tool.utils import DisplayMode


class Model:
    """
    The model class, responsible for backend logic regarding storing and manipulating data.
    """

    def __init__(self, files: Optional[List[str]], n_samples: int, seed: int,
                 frame_type: FrameType):
        """
        Initializes a ``Model`` instance.
        """
        self.sources = OrderedDict({})
        """Dictionary mapping file path to ``FrameLoader`` object."""
        self.n_samples: int = n_samples
        """Number of frame samples."""
        self.curr_src_idx: int = 0
        """Index of current video source."""
        self.curr_frame_idx: int = 0
        """Range (0, `n_samples - 1`), denotes the frame index inside the `frame_position` list."""
        self.frame_positions: List[int] = []
        """List of frame indices, range (0, `total_frames - 1`)."""
        self.curr_mode = DisplayMode.SCALED
        """Current display mode."""
        self.max_frame_size: Optional[Tuple[int, int]] = None
        """Maximum frame width and height."""
        self.curr_frame_type: FrameType = frame_type
        """Current frame type."""
        self.seed: int = seed
        """Random seed."""

        [self.add_source(file) for file in files] if files else None

    def offset(self, direction: int) -> None:
        """
        Replaces current frame with the closest frame of the same type in specified direction (backward or forward).

        :param direction: -1 for backward, 1 for forward.
        """
        frame_position, frame = self.get_current_source().offset(self.frame_positions[self.curr_frame_idx],
                                                                 direction,
                                                                 self.curr_frame_type)
        self.frame_positions[self.curr_frame_idx] = frame_position
        self.get_current_source().frames[self.curr_frame_idx] = frame

    def _delete_sampled_frames(self) -> None:
        """
        Deletes sampled frames from the model.
        """
        for source in self.sources.values():
            source.delete_frames()

    def _sample_frames(self) -> None:
        """
        Randomly samples video frames and adds them to the model.
        """
        random.seed(self.seed)
        min_total_frames = min([source.total_frames for source in self.sources.values()])
        self.frame_positions = sorted([random.randint(0, min_total_frames) for _ in range(self.n_samples)])

        for source in self.sources.values():
            source.sample_frames(self.frame_positions, self.curr_frame_type)

    def resample_frames(self) -> None:
        """
        Deletes current video frames and samples new ones.
        """
        if len(self.sources) > 0:
            self._delete_sampled_frames()
            self._sample_frames()

    def add_source(self, file_path: str) -> bool:
        """
        Adds video source to the model.

        :param file_path: Video source string.
        :return: ``True`` if source was successfully added, ``False`` if source already exists.
        """
        if file_path in self.sources:
            return False
        else:
            frame_loader = FrameLoader(Path(file_path))
            self.sources[file_path] = frame_loader
            self._sample_frames()
            return True

    def delete_source(self, file_path: str) -> int:
        """
        Deletes video source from the model.

        :param file_path: Path of the video source to delete.
        :return: Index of deleted source.
        """
        src_idx = list(self.sources.keys()).index(file_path)

        if self.curr_src_idx == len(self.sources) - 1 and self.curr_src_idx > 0:
            self.curr_src_idx -= 1

        del self.sources[file_path]

        if len(self.sources) == 0:
            self.curr_frame_idx = 0

        return src_idx

    def get_current_source(self) -> FrameLoader:
        """
        Retrieves current video source.

        :return: ``FrameLoader`` object representing current source.
        """
        return list(self.sources.values())[self.curr_src_idx]

    def get_current_frame(self) -> np.ndarray:
        """
        Retrieves current frame of current video source.

        :return: Current frame.
        """
        return self.get_current_source().frames[self.curr_frame_idx]
