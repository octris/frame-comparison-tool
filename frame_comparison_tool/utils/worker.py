from queue import Queue
from typing import override, Optional, Any, Dict, Callable

from PySide6.QtCore import QThread, Signal

from frame_comparison_tool.utils.exceptions import InvalidOperationError
from frame_comparison_tool.utils.frame_loader_manager import FrameLoaderManager
from frame_comparison_tool.utils.operation import Operation


class Worker(QThread):
    on_frames_ready: Signal = Signal()
    on_task_started: Signal = Signal()
    on_task_finished: Signal = Signal()

    def __init__(self, frame_loader_manager: FrameLoaderManager):
        super().__init__()
        self.queue: Queue[tuple[Optional[Operation], Dict[str, Any]]] = Queue()
        self.frame_loader_manager: FrameLoaderManager = frame_loader_manager
        self.on_frame_sample: Optional[Callable] = None

    def add_task(self, operation: Operation, **kwargs) -> None:
        self.queue.put((operation, kwargs))

    @override
    def run(self) -> None:
        while True:
            operation, kwargs = self.queue.get()

            self.on_task_started.emit()

            if operation == Operation.RESAMPLE:
                self.frame_loader_manager.clear_frame_positions()
                self.frame_loader_manager.sample_all_frames()
            elif operation == Operation.SAMPLE:
                self.frame_loader_manager.sample_all_frames()
            elif operation == Operation.OFFSET:
                self.frame_loader_manager.offset_frame(direction=kwargs.get("direction"),
                                                       src_idx=kwargs.get("src_idx"),
                                                       frame_idx=kwargs.get("frame_idx"))
            else:
                raise InvalidOperationError(operation)

            self.on_frames_ready.emit()
            self.on_task_finished.emit()
