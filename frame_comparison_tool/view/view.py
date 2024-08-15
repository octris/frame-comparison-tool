from enum import Enum
from typing import override, List, Optional, Tuple

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QPushButton, QHBoxLayout, QComboBox, \
    QLabel, QFileDialog, QScrollArea
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage, QKeyEvent, QResizeEvent
from frame_comparison_tool.utils import FrameType


class DisplayMode(Enum):
    CROPPED = 'Cropped'
    SCALED = 'Scaled'


class ViewData:
    def __init__(self, frame: Optional[np.ndarray], mode: DisplayMode):
        self.frame: Optional[np.ndarray] = frame
        self.mode: DisplayMode = mode


class View(QMainWindow):
    add_source_requested = Signal(str)
    delete_source_requested = Signal(str)
    mode_changed = Signal(DisplayMode)
    frame_changed = Signal(int)
    source_changed = Signal(int)
    resize_requested = Signal(tuple)
    frame_type_changed = Signal(FrameType)

    def __init__(self):
        super().__init__()
        self.presenter: Optional['Presenter'] = None
        self._init_ui()

    def _init_ui(self) -> None:
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle(f'Frame Comparison Tool')
        self.setMinimumSize(1, 1)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)

        self.frame_widget = QLabel()
        self.frame_widget.setStyleSheet('background-color: white')
        self.frame_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumSize(1, 1)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.frame_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.central_layout.addWidget(self.scroll_area, stretch=4)

        self.config_widget = QWidget()
        self.config_widget.setStyleSheet('background-color: #F8F8F8')
        self.config_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.central_layout.addWidget(self.config_widget, stretch=1)

        self.config_layout = QHBoxLayout(self.config_widget)

        self.add_source_button = QPushButton('Add Source', self.config_widget)
        self.add_source_button.clicked.connect(self._on_add_source_clicked)
        self.add_source_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.config_layout.addWidget(self.add_source_button)

        self.mode_dropdown = QComboBox(self.config_widget)
        self.mode_dropdown.addItems([mode.value for mode in DisplayMode])
        self.mode_dropdown.currentTextChanged.connect(self._on_mode_changed)
        self.mode_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.config_layout.addWidget(self.mode_dropdown)

        self.frame_type_dropdown = QComboBox(self.config_widget)
        # noinspection PyTypeChecker
        self.frame_type_dropdown.addItems([
            frame_type.value
            for frame_type
            in FrameType
            if frame_type != FrameType.UNKNOWN
        ])
        self.frame_type_dropdown.currentTextChanged.connect(self._on_frame_type_changed)
        self.frame_type_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.config_layout.addWidget(self.frame_type_dropdown)

        self.added_sources_widgets: List[QWidget] = []

        self.setLayout(self.central_layout)
        self.setFocus()
        self.show()

    def set_presenter(self, presenter: 'Presenter') -> None:
        self.presenter = presenter

    @override
    def resizeEvent(self, event: QResizeEvent):
        self.resize_requested.emit(self.get_max_frame_size())
        return super().resizeEvent(event)

    @override
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Left:
            self.frame_changed.emit(-1)
        elif event.key() == Qt.Key.Key_Right:
            self.frame_changed.emit(1)
        elif event.key() == Qt.Key.Key_Down:
            self.source_changed.emit(-1)
        elif event.key() == Qt.Key.Key_Up:
            self.source_changed.emit(1)

        return super().keyPressEvent(event)

    def _on_add_source_clicked(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self)
        if file_path:
            self.add_source_requested.emit(file_path)

    def on_add_source(self, file_path: str) -> None:
        main_widget = QWidget()
        widget_layout = QHBoxLayout(main_widget)
        source_label = QLabel(file_path)
        delete_button = QPushButton('Delete')
        delete_button.clicked.connect(lambda: self._on_delete_clicked(file_path))

        main_widget.setLayout(widget_layout)
        widget_layout.addWidget(source_label)
        widget_layout.addWidget(delete_button)

        self.central_layout.addWidget(main_widget)
        self.added_sources_widgets.append(main_widget)

        self.central_layout.update()
        self.update()

    def on_delete_source(self, idx) -> None:
        widget_to_remove = self.added_sources_widgets.pop(idx)
        widget_to_remove.setParent(None)
        widget_to_remove.deleteLater()

        self.central_layout.update()
        self.update()

    def _on_delete_clicked(self, file_path: str) -> None:
        self.delete_source_requested.emit(file_path)

    def _on_mode_changed(self) -> None:
        mode = DisplayMode(self.mode_dropdown.currentText())
        self.mode_changed.emit(mode)

    def _on_frame_type_changed(self) -> None:
        frame_type = FrameType(self.frame_type_dropdown.currentText())
        self.frame_type_changed.emit(frame_type)

    def update_display(self, view_data: ViewData) -> None:
        if view_data.frame is None:
            self.frame_widget.clear()
        else:
            height, width, channels = view_data.frame.shape
            bytes_per_line = 3 * width
            image = QImage(view_data.frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)

            self.frame_widget.setPixmap(pixmap)
            self.frame_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setFocus()

    def get_max_frame_size(self) -> Tuple[int, int]:
        width = self.scroll_area.size().width()
        height = self.scroll_area.size().height()

        return width, height
