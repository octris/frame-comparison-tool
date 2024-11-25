from typing import override

from PySide6.QtWidgets import QLabel, QStyleOptionFrame, QStyle
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt, QSize


class ElidingLabel(QLabel):
    def __init__(self, text: str, elide_mode: Qt.TextElideMode = Qt.TextElideMode.ElideLeft):
        super().__init__()
        self.setText(text)
        self._text = text
        self.elide_mode = elide_mode

    def setElideMode(self, mode: Qt.TextElideMode) -> None:
        if self.elide_mode != mode and mode != Qt.TextElideMode.ElideNone:
            self.elide_mode = mode
            self.updateGeometry()

    @override
    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    @override
    def sizeHint(self) -> QSize:
        hint = self.fontMetrics().boundingRect(self._text).size()
        margins = self.contentsMargins()
        margin = self.margin() * 2
        return QSize(
            min(100, hint.width()) + margins.left() + margins.right() + margin,
            min(self.fontMetrics().height(), hint.height()) + margins.top() + margins.bottom() + margin
        )

    @override
    def paintEvent(self, event) -> None:
        qp = QPainter(self)
        opt = QStyleOptionFrame()
        self.initStyleOption(opt)
        self.style().drawControl(QStyle.ControlElement.CE_ShapedFrame, opt, qp, self)
        margin = self.margin()
        m = self.fontMetrics().horizontalAdvance('x') / 2 - margin
        r = self.contentsRect().adjusted(int(margin + m), margin, -int(margin + m), -margin)
        qp.drawText(r, self.alignment(), self.fontMetrics().elidedText(self._text, self.elide_mode, r.width()))
