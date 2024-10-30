from queue import Queue
from typing import override
from frame_comparison_tool.utils.operation import Operation

from PySide6.QtCore import QThread


class Worker(QThread):
    def __init__(self):
        super().__init__()
        queue = Queue()

    @override
    def run(self):
        while True:
            pass
