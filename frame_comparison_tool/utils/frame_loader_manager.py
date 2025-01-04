import random
from bisect import bisect_right
from collections import OrderedDict
from pathlib import Path
from sys import maxsize
from typing import Optional

import numpy as np
from PIL import Image

from frame_comparison_tool.utils import FrameLoader, FrameType, Direction
from frame_comparison_tool.utils.exceptions import ImageReadError, MultipleSourcesImageReadError, VideoCaptureFailed


class FrameLoaderManager:
    """
    Manages multiple ``FrameLoader`` instances and coordinates frame sampling operations.

    This class handles the synchronization and management of multiple video sources,
    including frame sampling, position tracking, and error handling across all sources.
    """

    def __init__(self, n_samples: int, seed: int, frame_type: FrameType):
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

    def save_frames(self, formatted_date: str) -> None:
        """
        Iterates through all sources and saves frames to the current working directory.

        :param formatted_date: Formatted date to be used as directory name.
        """

        if self.sources:
            current_dir = Path.cwd()
            frames_dir = current_dir / formatted_date
            frames_dir.mkdir(exist_ok=True)

            for src_idx, frame_loader in enumerate(self.sources.values()):
                for frame_idx, frame in enumerate(f.frame for f in frame_loader.frame_data):
                    image_path = frames_dir / f"{src_idx + 1}_{frame_idx + 1}.png"
                    image = Image.fromarray(frame)
                    image.save(image_path)

    def update_n_samples(self, n_samples: int) -> None:
        """
        Updates number of samples.

        :param n_samples: New number of samples.
        """
        self.n_samples = n_samples

    def update_seed(self, seed: int) -> None:
        """
        Updates seed.

        :param seed: New seed.
        """
        self.seed = seed

    def add_source(self, file_paths: list[Path]) -> list[tuple[Path, bool]]:
        """
        Adds new video source.

        :param file_paths: List of video file paths to be added.
        :return: List of tuples containing a video file path and its success status.
        """

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
        """
        Removes a video file.

        :param file_path: Path of the video to be deleted.
        :return: Index of removed source.
        """
        src_idx = list(self.sources.keys()).index(file_path)
        del self.sources[file_path]

        return src_idx

    def get_source(self, src_idx: int) -> FrameLoader:
        """
        Gets a frame loader by its index.

        :param src_idx: Index of the source.
        :return: ``FrameLoader`` instance at the specified index.
        """
        return list(self.sources.values())[src_idx]

    def get_frame(self, src_idx: int, frame_idx: int) -> Optional[np.ndarray]:
        """
        Retrieves a specific frame from a specific source.

        :param src_idx: Index of the source.
        :param frame_idx: Index of the frame.
        :return: Frame from desired source at desired index or ``None`` if indices are invalid.
        """
        if 0 <= src_idx < len(self.sources):
            source = self.get_source(src_idx)

            if 0 <= frame_idx < len(source.frame_data):
                return source.frame_data[frame_idx].frame
            else:
                return None
        else:
            return None

    def expand_frames(self, n_samples: int) -> None:
        """
        Expand the number of sampled frames while maintaining existing frame positions.

        :param n_samples: New number of sampled frames.
        """

        if n_samples > self.n_samples and self.frame_positions:
            self._generate_random_frame_positions(min_frame_pos=min(self.frame_positions),
                                                  max_frame_pos=max(self.frame_positions),
                                                  n_samples=n_samples)

    def offset_frame(self, direction: Direction, src_idx: int, frame_idx: int) -> None:
        """
        Offset a frame in a specified direction.

        :param direction: Direction to move the frame.
        :param src_idx: Index of the source video.
        :param frame_idx: Index of the frame to offset.
        """

        source = self.get_source(src_idx=src_idx)
        source.offset(frame_idx=frame_idx, direction=direction)

    def clear_frame_positions(self) -> None:
        """
        Clear all stored frame positions.
        """
        if self.frame_positions:
            self.frame_positions.clear()

    def sample_all_frames(self) -> None:
        """
        Sample frames from all sources.
        """
        if self.sources:
            self._sample_frames(list(self.sources.values()))

    def _generate_random_frame_positions(self, min_frame_pos: int, max_frame_pos: int, n_samples: int) -> list[int]:
        """
        Generate sorted random frame positions within a range.

        :param min_frame_pos: Minimum frame position (inclusive).
        :param max_frame_pos: Maximum frame position (inclusive).
        :param n_samples: Number of positions to generate.
        :return: Sorted list of randomly generated frame positions.
        """
        random.seed(self.seed)
        frame_positions = sorted([random.randint(min_frame_pos, max_frame_pos) for _ in range(n_samples)])

        return frame_positions

    def _sample_frames(self, frame_loaders: list[FrameLoader]) -> None:
        """
        Adjusts frame positions based on the minimum total frames across all loaders
        and samples frames of the specified type from each loader.

        :param frame_loaders: List of frame loaders.
        :raises ``MultipleSourcesImageReadError``:  If frame reading fails for any loader.
        """
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

        errors: list[ImageReadError or VideoCaptureFailed] = []

        for frame_loader in frame_loaders:
            try:
                frame_loader.sample_frames(
                    frame_positions=self.frame_positions,
                    frame_type=self.frame_type
                )
            except (ImageReadError, VideoCaptureFailed) as e:
                errors.append(e)

        if errors:
            raise MultipleSourcesImageReadError(errors=errors)
