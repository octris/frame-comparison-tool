from queue import Queue
from typing import override, Optional, Any, Dict

from PySide6.QtCore import QThread, Signal

from frame_comparison_tool.utils.exceptions import InvalidTaskError, MultipleSourcesImageReadError, \
    NoMatchingFrameTypeError
from frame_comparison_tool.utils.frame_loader_manager import FrameLoaderManager
from frame_comparison_tool.utils.task import Task


class Worker(QThread):
    """A worker thread that manages frame loading tasks in a queue.

    This class handles asynchronous frame loading tasks including resampling,
    sampling, and frame offset. It emits signals to notify task status.

    Signals:
        on_frames_ready: Emitted when frames have been loaded successfully
        on_task_started: Emitted when a task begins processing
        on_task_finished: Emitted when a task completes
        on_task_failed: Emitted when a task fails, includes the problematic file path
    """

    on_frames_ready: Signal = Signal()
    on_task_started: Signal = Signal()
    on_task_finished: Signal = Signal()
    on_task_failed: Signal = Signal(str)
    on_task_failed_invalid_sources: Signal = Signal(list)

    def __init__(self, frame_loader_manager: FrameLoaderManager):
        """
        Initialize the worker thread.

        :param frame_loader_manager: ``FrameLoaderManager`` instance handling frame loading.
        """

        super().__init__()
        self.queue: Queue[tuple[Optional[Task], Dict[str, Any]]] = Queue()
        """Queue containing tuples that consist of a task and additional arguments (if needed)."""
        self.frame_loader_manager: FrameLoaderManager = frame_loader_manager
        """Instance of ``FrameLoaderManager``."""
        self._running = True
        """Flag indicating if the thread is running."""

    def stop(self) -> None:
        """
        Stop the worker thread.
        """

        self._running = False
        self.queue.put((None, {}))
        self.wait()

    def add_task(self, task: Task, **kwargs) -> None:
        """
        Add a new task to the queue.

        :param task: ``Task`` enum specifying the type of task that needs to be done.
        :param kwargs: Additional arguments required for a specific task.
        For the ``OFFSET`` task, expected kwargs are `direction`, `src_idx`, and `frame_idx`.
        """

        self.queue.put((task, kwargs))

    @override
    def run(self) -> None:
        """
        Thread execution loop processing tasks from the queue.

        This method continuously processes tasks from the queue until stopped.
        It handles three types of tasks:
        - RESAMPLE: Clears frame positions and samples all frames
        - SAMPLE: Samples all frames without clearing positions
        - OFFSET: Adjusts frame offset

        Emits appropriate signals for task status and handles errors that may occur.

        :raises ``InvalidTaskError``: If an unsupported task is encountered.
        """

        while True:
            task, kwargs = self.queue.get()

            if not self._running:
                break

            self.on_task_started.emit()

            if task == Task.RESAMPLE:
                self.frame_loader_manager.clear_frame_positions()
                try:
                    self.frame_loader_manager.sample_all_frames()
                except MultipleSourcesImageReadError as e:
                    self.on_task_failed_invalid_sources.emit(e.sources)
                except NoMatchingFrameTypeError as e:
                    self.on_task_failed.emit(e.message)

            elif task == Task.SAMPLE:
                try:
                    self.frame_loader_manager.sample_all_frames()
                except MultipleSourcesImageReadError as e:
                    self.on_task_failed_invalid_sources.emit(e.sources)
                except NoMatchingFrameTypeError as e:
                    self.on_task_failed.emit(e.message)

            elif task == Task.OFFSET:
                self.frame_loader_manager.offset_frame(direction=kwargs.get("direction"),
                                                       src_idx=kwargs.get("src_idx"),
                                                       frame_idx=kwargs.get("frame_idx"))
            elif task == Task.OFFSET_ALL:
                self.frame_loader_manager.offset_all_frames(direction=kwargs.get("direction"),
                                                            src_idx=kwargs.get("src_idx"))

            else:
                raise InvalidTaskError(task)

            self.on_frames_ready.emit()
            self.on_task_finished.emit()
