from pathlib import Path
from queue import Queue
from typing import override, Optional, Any, Dict, Callable

from PySide6.QtCore import QThread, Signal

from frame_comparison_tool.utils.exceptions import InvalidOperationError, MultipleSourcesImageReadError
from frame_comparison_tool.utils.frame_loader_manager import FrameLoaderManager
from frame_comparison_tool.utils.operation import Operation


class Worker(QThread):
    on_frames_ready: Signal = Signal()
    on_task_started: Signal = Signal()
    on_task_finished: Signal = Signal()
    on_task_failed: Signal = Signal(Path)

    def __init__(self, frame_loader_manager: FrameLoaderManager):
        super().__init__()
        self.queue: Queue[tuple[Optional[Operation], Dict[str, Any]]] = Queue()
        self.frame_loader_manager: FrameLoaderManager = frame_loader_manager
        self.on_frame_sample: Optional[Callable] = None
        self._running = True

    def stop(self):
        self._running = False
        self.queue.put((None, {}))
        self.wait()

    def add_task(self, operation: Operation, **kwargs) -> None:
        self.queue.put((operation, kwargs))

    @override
    def run(self) -> None:
        while True:
            operation, kwargs = self.queue.get()

            if not self._running:
                break

            self.on_task_started.emit()

            if operation == Operation.RESAMPLE:
                self.frame_loader_manager.clear_frame_positions()
                try:
                    self.frame_loader_manager.sample_all_frames()
                except MultipleSourcesImageReadError as e:
                    self.on_task_failed.emit(e.sources)
            elif operation == Operation.SAMPLE:
                try:
                    self.frame_loader_manager.sample_all_frames()
                except MultipleSourcesImageReadError as e:
                    self.on_task_failed.emit(e.sources)
            elif operation == Operation.OFFSET:
                self.frame_loader_manager.offset_frame(direction=kwargs.get("direction"),
                                                       src_idx=kwargs.get("src_idx"),
                                                       frame_idx=kwargs.get("frame_idx"))
            else:
                raise InvalidOperationError(operation)

            self.on_frames_ready.emit()
            self.on_task_finished.emit()
