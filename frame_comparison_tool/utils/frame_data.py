import numpy as np


# TODO: Add frame_type
class FrameData:
    def __init__(self, frame: np.ndarray, original_position: int, real_position: int):
        self._frame: np.ndarray = frame
        self._original_frame_position: int = original_position
        self._real_frame_position: int = real_position
        self._offset: int = 0

    @property
    def frame(self) -> np.ndarray:
        return self._frame

    @property
    def original_frame_position(self) -> int:
        return self._original_frame_position

    @property
    def real_frame_position(self) -> int:
        return self._real_frame_position

    def _update_real_position(self, real_frame_position: int):
        if real_frame_position > self._real_frame_position:
            self._offset += 1
        elif real_frame_position < self._real_frame_position:
            self._offset -= 1
        else:
            pass

        self._real_frame_position = real_frame_position

    def update_frame(self, frame: np.ndarray, frame_position: int):
        self._frame = frame
        self._update_real_position(real_frame_position=frame_position)
