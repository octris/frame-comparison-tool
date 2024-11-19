from typing import List

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QTimer


class SpinningCircle(QLabel):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(30)
        self.angle: int = 0
        self.chars: List[str] = ["◒", "◐", "◓", "◑"]

        self.timer = QTimer()
        self.timer.timeout.connect(self._rotate)

    def _set_text(self) -> None:
        self.setText(f'Loading {self.chars[self.angle]}')

    def _reset_text(self) -> None:
        self.setText('')

    def _rotate(self) -> None:
        self.angle = (self.angle + 1) % len(self.chars)
        self._set_text()

    def start(self) -> None:
        self.timer.start(150)

    def stop(self) -> None:
        self.timer.stop()
        self._reset_text()
        self.angle = 0
