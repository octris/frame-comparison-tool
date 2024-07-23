from collections import OrderedDict
from pathlib import Path
from typing import List
from frame_loader import FrameLoader
import random
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QPushButton, QHBoxLayout, QComboBox, \
    QLabel, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QKeyEvent


class Controller:
    def __init__(self, n_samples=5):
        self.sources: OrderedDict[str, FrameLoader] = OrderedDict()
        self.n_samples = n_samples
        self.curr_src_idx = 0
        self.curr_frame_idx = 0
        self._frame_ids: List[int] = []

    @property
    def frame_ids(self) -> List[int]:
        return self._frame_ids

    def add_source(self, file_path: Path) -> bool:
        file_path_str = str(file_path.absolute())

        if file_path_str in self.sources:
            return False
        else:
            frame_loader = FrameLoader(Path(file_path))
            self.sources[file_path_str] = frame_loader
            self._sample_frame_ids()
            return True

    def _sample_frame_ids(self) -> None:
        random.seed(42)
        min_total_frames = min([source.total_frames for source in self.sources.values()])
        self._frame_ids = sorted([random.randint(0, min_total_frames) for _ in range(self.n_samples)])

        for source in self.sources.values():
            source.sample_frames(self._frame_ids)


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.controller = Controller()

        self.setGeometry(100, 100, 800, 500)
        self.setWindowTitle(f'Frame Comparison Tool')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)

        self.frame_widget = QLabel()
        self.frame_widget.setStyleSheet('background-color: white')
        self.central_layout.addWidget(self.frame_widget, stretch=4)

        self.config_widget = QWidget()
        self.config_widget.setStyleSheet('background-color: #F8F8F8')
        self.central_layout.addWidget(self.config_widget, stretch=1)

        self.config_layout = QHBoxLayout(self.config_widget)

        self.add_source_button = QPushButton('Add Source', self.config_widget)
        self.add_source_button.clicked.connect(self._add_source)
        self.config_layout.addWidget(self.add_source_button)

        self.mode_dropdown = QComboBox(self.config_widget)
        self.mode_dropdown.addItems(['Cropped', 'Scaled'])
        self.config_layout.addWidget(self.mode_dropdown)

        self.setLayout(self.central_layout)
        self.show()

        self.central_widget.setFocus()
        self.central_widget.keyPressEvent = self._key_press_event

    def _key_press_event(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self._display_next_frame(-1)
        elif event.key() == Qt.Key.Key_Right:
            self._display_next_frame(1)
        elif event.key() == Qt.Key.Key_Down:
            self._change_displayed_source(-1)
        elif event.key() == Qt.Key.Key_Right:
            self._change_displayed_source(1)

    def _add_source(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self)
        if file_path and self.controller.add_source(Path(file_path)):
            self._update_display()

    def _display_next_frame(self, direction: int) -> None:
        self.controller.curr_frame_idx += direction
        self.controller.curr_frame_idx = max(0, min(self.controller.curr_frame_idx,
                                                    len(self.controller.frame_ids) - 1))
        self._update_display()

    def _change_displayed_source(self, direction: int) -> None:
        self.controller.curr_src_idx += direction
        self.controller.curr_src_idx = max(0, min(self.controller.curr_src_idx,
                                                  len(self.controller.sources) - 1))
        self._update_display()

    def _update_display(self) -> None:
        if self.controller.sources:
            source = list(self.controller.sources.values())[self.controller.curr_src_idx]
            frame = source.frames[self.controller.curr_frame_idx]

            height, width, channels = frame.shape
            bytes_per_line = 3 * width
            image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

            self.frame_widget.setPixmap(QPixmap.fromImage(image))


def main():
    app = QApplication([])
    window = App()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
