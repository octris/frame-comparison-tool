import random
from bisect import bisect_right
from collections import OrderedDict
from pathlib import Path
from sys import maxsize
from typing import Optional

import numpy as np

from frame_comparison_tool.utils import FrameLoader, FrameType, Direction
from frame_comparison_tool.utils.exceptions import ImageReadError, MultipleSourcesImageReadError


class FrameLoaderManager:
    def __init__(self, files: Optional[list[Path]], n_samples: int, seed: int, frame_type: FrameType):
        self.sources: OrderedDict[Path, FrameLoader] = OrderedDict({})
        """Dictionary mapping file path to ``FrameLoader`` object."""
        self.n_samples: int = n_samples
        """Number of frame samples."""
        self.seed: int = seed
        """Random seed."""
        self.frame_positions: list[int] = []
        """List of frame indices, range (0, `total_frames - 1`)."""
        self.frame_type: FrameType = frame_type
        """Current frame type."""

    def update_n_samples(self, n_samples: int) -> None:
        self.n_samples = n_samples

    def update_seed(self, seed: int) -> None:
        self.seed = seed

    def add_source(self, file_paths: list[Path]) -> list[tuple[Path, bool]]:
        added_file_paths: list[tuple[Path, bool]] = []

        if file_paths:
            for file_path in file_paths:
                if file_path not in self.sources.keys():
                    status = True
                    frame_loader = FrameLoader(file_path=Path(file_path))

                    if frame_loader.total_frames == 0:
                        status = False
                    else:
                        self.sources[file_path] = frame_loader

                    added_file_paths.append((file_path, status))

        return added_file_paths

    def delete_source(self, file_path: Path) -> int:
        src_idx = list(self.sources.keys()).index(file_path)
        del self.sources[file_path]

        return src_idx

    def get_source(self, src_idx: int) -> FrameLoader:
        return list(self.sources.values())[src_idx]

    def get_frame(self, src_idx: int, frame_idx: int) -> Optional[np.ndarray]:
        if src_idx < len(self.sources):
            source = self.get_source(src_idx)

            if frame_idx < len(source.frame_data):
                return source.frame_data[frame_idx].frame
            else:
                return None
        else:
            return None

    def expand_frames(self, n_samples: int):
        if n_samples > self.n_samples and self.frame_positions:
            self._generate_random_frame_positions(min_frame_pos=min(self.frame_positions),
                                                  max_frame_pos=max(self.frame_positions),
                                                  n_samples=n_samples)

    def offset_frame(self, direction: Direction, src_idx: int, frame_idx: int) -> None:
        source = self.get_source(src_idx=src_idx)
        source.offset(frame_idx=frame_idx, direction=direction)

    def clear_frame_positions(self) -> None:
        if self.frame_positions:
            self.frame_positions.clear()

    def sample_all_frames(self) -> None:
        if self.sources:
            self._sample_frames(list(self.sources.values()))

    def _generate_random_frame_positions(self, min_frame_pos: int, max_frame_pos: int, n_samples: int) -> list[int]:
        random.seed(self.seed)
        frame_positions = sorted([random.randint(min_frame_pos, max_frame_pos) for _ in range(n_samples)])

        return frame_positions

    def _sample_frames(self, frame_loaders: list[FrameLoader]) -> None:
        if (min_total_frames := min([frame_loader.total_frames for frame_loader in frame_loaders])) < max(
                self.frame_positions, default=maxsize):
            idx = bisect_right(self.frame_positions, min_total_frames)
            new_frame_positions = self._generate_random_frame_positions(
                min_frame_pos=(
                        self.frame_positions[idx - 1 if idx > 0 else idx] + 1
                ) if self.frame_positions else 0,
                max_frame_pos=min_total_frames,
                n_samples=self.n_samples - idx
            )
            self.frame_positions = self.frame_positions[:idx]
            self.frame_positions.extend(new_frame_positions)

        errors: list[ImageReadError] = []

        for frame_loader in frame_loaders:
            try:
                frame_loader.sample_frames(
                    frame_positions=self.frame_positions,
                    frame_type=self.frame_type
                )
            except ImageReadError as e:
                errors.append(e)

        if errors:
            raise MultipleSourcesImageReadError(errors=errors)
