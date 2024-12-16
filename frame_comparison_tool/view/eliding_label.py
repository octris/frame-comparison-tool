from typing import override

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QLabel, QStyleOptionFrame, QStyle


class ElidingLabel(QLabel):
    """
    A ``QLabel`` subclass that automatically elides text that doesn't fit within its bounds.

    The label will show an ellipsis (...) to indicate truncated text. The position of the
    ellipsis is determined by the elide mode (start, middle, or end of text).
    """

    def __init__(self, text: str, elide_mode: Qt.TextElideMode = Qt.TextElideMode.ElideLeft):
        """
        Initialize the eliding label.

        :param text: The text to display in the label.
        :param elide_mode: Where to show the ellipsis when text is truncated.
        """

        super().__init__()
        self.setText(text)
        self._text = text
        self.elide_mode = elide_mode

    def setElideMode(self, mode: Qt.TextElideMode) -> None:
        """
        Set the elide mode for the label.

        :param mode: The new elide mode. Must not be ``ElideNone``.
        """

        if self.elide_mode != mode and mode != Qt.TextElideMode.ElideNone:
            self.elide_mode = mode
            self.updateGeometry()

    @override
    def minimumSizeHint(self) -> QSize:
        """
        Get the minimum size needed to display the elided text.

        :return: The minimum size for the label.
        """

        return self.sizeHint()

    @override
    def sizeHint(self) -> QSize:
        """
        Calculate the ideal size for the label.

        The width is limited to 100 pixels, and the height is limited to a single line.
        Margins are added to the calculated size.

        :return: The recommended size for the label.
        """

        hint = self.fontMetrics().boundingRect(self._text).size()
        margins = self.contentsMargins()
        margin = self.margin() * 2
        return QSize(
            min(100, hint.width()) + margins.left() + margins.right() + margin,
            min(self.fontMetrics().height(), hint.height()) + margins.top() + margins.bottom() + margin
        )

    @override
    def paintEvent(self, event) -> None:
        """
        Draw the label with elided text.

        :param event: An event (unused)
        """

        qp = QPainter(self)
        opt = QStyleOptionFrame()
        self.initStyleOption(opt)
        self.style().drawControl(QStyle.ControlElement.CE_ShapedFrame, opt, qp, self)
        margin = self.margin()
        m = self.fontMetrics().horizontalAdvance('x') / 2 - margin
        r = self.contentsRect().adjusted(int(margin + m), margin, -int(margin + m), -margin)
        qp.drawText(r, self.alignment(), self.fontMetrics().elidedText(self._text, self.elide_mode, r.width()))
