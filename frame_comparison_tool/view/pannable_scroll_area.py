from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea
from PySide6.QtCore import QPoint
from PySide6.QtGui import QMouseEvent


class PannableScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.panning: bool = False
        self.last_pan_point: QPoint = QPoint()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.last_pan_point = event.pos()
            self.panning = True

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
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
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.panning = False

        return super().mouseReleaseEvent(event)
