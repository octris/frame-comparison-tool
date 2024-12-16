from typing import Final

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel


class SpinningCircle(QLabel):
    """
    A ``QLabel`` subclass that displays an animated loading indicator.
    """

    _CIRCLE_STATES: Final[list[str]] = ["◒", "◐", "◓", "◑"]
    _ANIMATION_INTERVAL: Final[int] = 150  # milliseconds
    _FIXED_HEIGHT: Final[int] = 30

    def __init__(self) -> None:
        """
        Initialize the spinning circle loading indicator.
        """

        super().__init__()

        self.setFixedHeight(self._FIXED_HEIGHT)

        self.angle: int = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self._rotate)

    def _set_text(self, text: str) -> None:
        """
        Update the label text.

        :param text: Label text to be shown.
        """

        self.setText(text)

    def _rotate(self) -> None:
        """
        Update the animation state to the next frame.
        """

        self.angle = (self.angle + 1) % len(self._CIRCLE_STATES)
        self._set_text(text=f"Loading {self._CIRCLE_STATES[self.angle]}")

    def start(self) -> None:
        """
        Start the loading animation.
        """

        self.timer.start(self._ANIMATION_INTERVAL)

    def stop(self) -> None:
        """
        Stop the loading animation.
        """

        self.timer.stop()
        self._set_text(text='')
        self.angle = 0
