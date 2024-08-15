import random
from pathlib import Path

import numpy as np
from collections import OrderedDict
from typing import List, Tuple, Optional

from frame_comparison_tool.utils import FrameLoader, FrameType
from frame_comparison_tool.view import DisplayMode


class Model:
    def __init__(self, n_samples: int = 5):
        self.sources: OrderedDict[str, FrameLoader] = OrderedDict()
        self.n_samples: int = n_samples
        self.curr_src_idx: int = 0
        self.curr_frame_idx: int = 0
        self._frame_ids: List[int] = []
        self.curr_mode = DisplayMode.CROPPED
        self.max_frame_size: Optional[Tuple[int, int]] = None
        self.curr_frame_type: FrameType = FrameType.B_TYPE

    @property
    def frame_ids(self) -> List[int]:
        return self._frame_ids

    def _delete_sampled_frames(self) -> None:
        for source in self.sources.values():
            source.delete_frames()

    def _sample_frames(self) -> None:
        random.seed(42)
        min_total_frames = min([source.total_frames for source in self.sources.values()])
        self._frame_ids = sorted([random.randint(0, min_total_frames) for _ in range(self.n_samples)])

        for source in self.sources.values():
            source.sample_frames(self._frame_ids, self.curr_frame_type)

    def resample_frames(self) -> None:
        if len(self.sources) > 0:
            self._delete_sampled_frames()
            self._sample_frames()

    def add_source(self, file_path: str) -> bool:
        if file_path in self.sources:
            return False
        else:
            frame_loader = FrameLoader(Path(file_path))
            self.sources[file_path] = frame_loader
            self._sample_frames()
            return True

    def delete_source(self, file_path: str) -> int:
        src_idx = list(self.sources.keys()).index(file_path)

        if self.curr_src_idx == len(self.sources) - 1 and self.curr_src_idx > 0:
            self.curr_src_idx -= 1

        del self.sources[file_path]

        if len(self.sources) == 0:
            self.curr_frame_idx = 0

        return src_idx

    def get_current_source(self) -> FrameLoader:
        return list(self.sources.values())[self.curr_src_idx]

    def get_current_frame(self) -> np.ndarray:
        return self.get_current_source().frames[self.curr_frame_idx]
