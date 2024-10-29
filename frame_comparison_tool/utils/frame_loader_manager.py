from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

import numpy as np
import random

from frame_comparison_tool.utils import FrameLoader, FrameType


class FrameLoaderManager:
    def __init__(self, files: Optional[List[str]], n_samples: int, seed: int,
                 frame_type: FrameType):
        self.sources: OrderedDict[str, FrameLoader] = OrderedDict({})
        """Dictionary mapping file path to ``FrameLoader`` object."""
        self.n_samples: int = n_samples
        """Number of frame samples."""
        self.seed: int = seed
        """Random seed."""
        self.frame_positions: List[int] = []
        """List of frame indices, range (0, `total_frames - 1`)."""
        self.frame_type: FrameType = frame_type
        """Current frame type."""

        if files:
            for file in files:
                self.add_source(file)

    @property
    def source_count(self) -> int:
        return len(self.sources)

    def add_source(self, file_path: str) -> bool:
        if file_path in self.sources:
            return False
        else:
            frame_loader = FrameLoader(Path(file_path))
            self.sources[file_path] = frame_loader
            self._sample_frames(frame_loader=frame_loader)
            return True

    def delete_source(self, file_path: str) -> int:
        src_idx = list(self.sources.keys()).index(file_path)
        del self.sources[file_path]

        return src_idx

    def get_source(self, src_idx: int) -> FrameLoader:
        return list(self.sources.values())[src_idx]

    def get_frame(self, src_idx: int, frame_idx: int) -> np.ndarray:
        return self.get_source(src_idx).frames[frame_idx]

    def offset_frame(self, direction: int, src_idx: int, frame_idx: int) -> None:
        source = self.get_source(src_idx=src_idx)
        frame_pos, frame = source.offset(
            frame_pos=self.frame_positions[frame_idx],
            direction=direction,
            frame_type=self.frame_type
        )
        self.frame_positions[frame_idx] = frame_pos
        source.frames[frame_idx] = frame

    def resample_frames(self) -> None:
        if self.sources:
            self._clear_frames()
            self._generate_sample_positions()
            for source in self.sources.values():
                self._sample_frames(source)

    def _generate_sample_positions(self):
        random.seed(self.seed)
        min_total_frames = min([source.total_frames for source in self.sources.values()])
        self.frame_positions = sorted([random.randint(0, min_total_frames) for _ in range(self.n_samples)])

    def _sample_frames(self, frame_loader: FrameLoader) -> None:
        if len(self.frame_positions) == 0:
            self._generate_sample_positions()

        frame_loader.sample_frames(frame_positions=self.frame_positions, frame_type=self.frame_type)

    def _clear_frames(self) -> None:
        for source in self.sources.values():
            source.delete_frames()
