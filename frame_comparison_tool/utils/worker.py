from queue import Queue
from typing import override, Optional, Any, Tuple, Dict, Callable

from frame_comparison_tool.utils.frame_loader_manager import FrameLoaderManager
from frame_comparison_tool.utils.operation import Operation

from PySide6.QtCore import QThread, Signal


# TODO: Setter for callbacks
class Worker(QThread):
    on_frames_ready: Signal = Signal()
    on_offset_done: Signal = Signal()

    def __init__(self, frame_loader_manager: FrameLoaderManager):
        super().__init__()
        self.queue: Queue[Tuple[Optional[Operation], Dict[str, Any]]] = Queue()
        self.frame_loader_manager: FrameLoaderManager = frame_loader_manager
        self.on_frame_sample: Optional[Callable] = None

    def add_task(self, operation: Operation, **kwargs) -> None:
        self.queue.put((operation, kwargs))

    @override
    def run(self):
        while True:
            operation, kwargs = self.queue.get()

            if operation == Operation.SAMPLE:
                self.frame_loader_manager.resample_frames()
                self.on_frames_ready.emit()
            elif operation == Operation.OFFSET:
                self.frame_loader_manager.offset_frame(direction=kwargs.get("direction"), src_idx=kwargs.get("src_idx"),
                                                       frame_idx=kwargs.get("frame_idx"))
                self.on_offset_done.emit()
            else:
                # TODO: InvalidOperationError
                pass
