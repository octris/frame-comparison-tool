from pathlib import Path
from typing import override

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QPushButton, QHBoxLayout, QComboBox, \
    QLabel, QFileDialog, QScrollArea, QErrorMessage
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QKeyEvent, QResizeEvent


class View(QMainWindow):
    def __init__(self):
        super().__init__()

        self.presenter = None
        self._init_ui()

    def _init_ui(self) -> None:
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle(f'Frame Comparison Tool')

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
        self.add_source_button.clicked.connect(self.on_add_source_clicked)
        self.add_source_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.config_layout.addWidget(self.add_source_button)

        self.mode_dropdown = QComboBox(self.config_widget)
        self.mode_dropdown.addItems(['Cropped', 'Scaled'])
        self.mode_dropdown.currentTextChanged.connect(
            lambda: self.presenter.update_display() if self.presenter is not None else None)
        self.mode_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.config_layout.addWidget(self.mode_dropdown)

        self.setLayout(self.central_layout)
        self.setFocus()
        self.show()

    def set_presenter(self, presenter: 'Presenter') -> None:
        self.presenter = presenter

    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.presenter:
            self.presenter.update_display()

        return super().resizeEvent(event)

    @override
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self.presenter.change_frame(-1)
        elif event.key() == Qt.Key.Key_Right:
            self.presenter.change_frame(1)
        elif event.key() == Qt.Key.Key_Down:
            self.presenter.change_source(-1)
        elif event.key() == Qt.Key.Key_Up:
            self.presenter.change_source(1)

        return super().keyPressEvent(event)

    def on_add_source_clicked(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self)
        if file_path and self.presenter.add_source(Path(file_path)):
            self.presenter.update_display()

    def update_display(self, frame, mode) -> None:
        height, width, channels = frame.shape
        image = QImage(frame.data, width, height, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        if mode == 'Scaled':
            pixmap = pixmap.scaled(self.scroll_area.viewport().size(), Qt.AspectRatioMode.KeepAspectRatio)
        elif mode == 'Cropped':
            pass
        else:
            raise ValueError("Invalid mode")

        self.frame_widget.setPixmap(pixmap)
        self.setFocus()
