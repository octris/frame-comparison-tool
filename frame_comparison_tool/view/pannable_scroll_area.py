from typing import Optional

from PySide6.QtCore import QPoint
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QScrollArea, QWidget


class PannableScrollArea(QScrollArea):
    """
    A ``QScrollArea`` subclass that enables the panning feature using mouse events.

    Allows the user to click and drag the frame within the scroll area.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initializes a ``PannableScrollArea`` instance.

        :param parent: Optional parent widget.
        """

        super().__init__(parent)

        self.panning: bool = False
        """
        Indicates whether the scroll area is currently being panned.
        """
        self.last_pan_point: QPoint = QPoint()
        """
        Stores the last recorded mouse position during panning.
        """

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handles the mouse press event to start panning.

        When clicking and holding the left mouse button:
        - The cursor changes to a closed hand
        - Panning mode is activated
        - The current mouse position is saved as the starting point

        :param event: Contains details about the mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.last_pan_point = event.pos()
            self.panning = True

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handles the mouse move event to perform panning.

         When dragging the mouse while in panning mode:
        - The distance moved is calculated
        - The view scrolls to follow mouse movement
        - The new mouse position is saved for the next move

        :param event: Contains details about the mouse press.
        """
        if self.panning:
            delta = event.pos() - self.last_pan_point
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self.last_pan_point = event.pos()

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handles the mouse release event to stop panning.

         When releasing the left mouse button:
        - The cursor changes back to the default arrow
        - Panning mode is turned off

        :param event: Contains details about the mouse press.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.panning = False

        return super().mouseReleaseEvent(event)
