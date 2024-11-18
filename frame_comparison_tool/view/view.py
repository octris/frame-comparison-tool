from typing import override, List, Optional, Tuple

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QPushButton, QHBoxLayout, QComboBox, \
    QLabel, QFileDialog, QSpinBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage, QKeyEvent, QResizeEvent, QMouseEvent
from frame_comparison_tool.utils import FrameType, DisplayMode, ViewData, Direction
from .pannable_scroll_area import PannableScrollArea


class View(QMainWindow):
    """
    This class creates the GUI for user interactions and communicates with the ``Presenter`` through signals.
    """

    add_source_requested = Signal(list)
    delete_source_requested = Signal(str)
    mode_changed = Signal(DisplayMode)
    frame_changed = Signal(Direction)
    source_changed = Signal(Direction)
    resize_requested = Signal(tuple)
    frame_type_changed = Signal(FrameType)
    offset_changed = Signal(Direction)
    seed_changed = Signal(int)
    shown = Signal(tuple)

    def __init__(self):
        """
        Initializes a ``View`` instance.
        """
        super().__init__()

        self.presenter: Optional['Presenter'] = None
        """``Presenter`` instance."""

        self._init_ui()

    def _init_ui(self) -> None:
        """
        Initializes the user interface.
        """
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle(f'Frame Comparison Tool')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)

        self.frame_widget = QLabel()
        self.frame_widget.setStyleSheet('background-color: white')
        self.frame_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.scroll_area = PannableScrollArea()
        self.scroll_area.setWidget(self.frame_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.central_layout.addWidget(self.scroll_area, stretch=4)

        self.config_widget = QWidget()
        self.config_widget.setStyleSheet('background-color: #F8F8F8')
        self.config_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.central_layout.addWidget(self.config_widget, stretch=1)

        self.config_layout = QHBoxLayout(self.config_widget)

        self.spin_box = QSpinBox()
        self.spin_box.setRange(0, 10000)
        self.spin_box.valueChanged.connect(self._on_seed_changed)
        self.config_layout.addWidget(self.spin_box)

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

        self.mode_dropdown = QComboBox(self.config_widget)
        self.mode_dropdown.addItems([mode.value for mode in DisplayMode])
        self.mode_dropdown.currentTextChanged.connect(self._on_mode_changed)
        self.mode_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.config_layout.addWidget(self.mode_dropdown)

        self.add_source_button = QPushButton('Add Source', self.config_widget)
        self.add_source_button.clicked.connect(self._on_add_source_clicked)
        self.add_source_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.config_layout.addWidget(self.add_source_button)

        self.added_sources_widgets: List[QWidget] = []

        self.setLayout(self.central_layout)
        self.setFocus()

    def set_init_values(self, files: Optional[str], seed: int, frame_type: FrameType, display_mode: DisplayMode):
        self.spin_box.setValue(seed)
        self.frame_type_dropdown.setCurrentIndex(list(FrameType).index(frame_type))
        self.mode_dropdown.setCurrentIndex(list(DisplayMode).index(display_mode))

        if files:
            for file in files:
                self.on_add_source(file)

    def set_presenter(self, presenter: 'Presenter') -> None:
        """
        Set the ``Presenter`` object.

        :param presenter: ``Presenter`` instance.
        """
        self.presenter = presenter

    @override
    def show(self) -> None:
        """
        Shows the main window and emits a signal.
        """
        super().show()
        self.shown.emit(self.get_max_frame_size())

    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Handles window resize events.

        :param event: Resize event object.
        """
        self.resize_requested.emit(self.get_max_frame_size())
        return super().resizeEvent(event)

    @override
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events.

        Emits various signals based on the key pressed:
        - Left/Right arrows: Change frame
        - Up/Down arrows: Change source
        - Plus/Minus: Offset frame

        :param event: Key event object.
        """
        if event.key() == Qt.Key.Key_Left:
            self.frame_changed.emit(Direction(-1))
        elif event.key() == Qt.Key.Key_Right:
            self.frame_changed.emit(Direction(1))
        elif event.key() == Qt.Key.Key_Down:
            self.source_changed.emit(Direction(-1))
        elif event.key() == Qt.Key.Key_Up:
            self.source_changed.emit(Direction(1))
        elif event.key() == Qt.Key.Key_Plus:
            self.offset_changed.emit(Direction(1))
        elif event.key() == Qt.Key.Key_Minus:
            self.offset_changed.emit(Direction(-1))

        return super().keyPressEvent(event)

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handles mouse press events.

        :param event: Mouse press event object.
        """
        self.setFocus()
        super().mousePressEvent(event)

    def _on_add_source_clicked(self) -> None:
        """
        Emits a signal when the user adds a new video source.
        """
        file_path, _ = QFileDialog.getOpenFileName(self)
        if file_path:
            self.add_source_requested.emit([file_path])

    def on_add_source(self, file_path: str) -> None:
        """
        Adds new source to the UI.

        :param file_path: String path to the video source.
        """
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

    def on_delete_source(self, src_idx: int) -> None:
        """
        Deletes source from the UI.

        :param src_idx: Index of the deleted source.
        """
        widget_to_remove = self.added_sources_widgets.pop(src_idx)
        widget_to_remove.setParent(None)
        widget_to_remove.deleteLater()

        self.central_layout.update()
        self.update()

    def _on_seed_changed(self) -> None:
        """
        Emits a signal when the user changes the random seed.
        """
        self.seed_changed.emit(self.spin_box.value())

    def _on_delete_clicked(self, file_path: str) -> None:
        """
        Emits a signal when the user deletes a source.

        :param file_path: String path to the video source.
        """
        self.delete_source_requested.emit(file_path)

    def _on_mode_changed(self) -> None:
        """
        Emits a signal when the user changes the display mode.
        """
        mode = DisplayMode(self.mode_dropdown.currentText())
        self.mode_changed.emit(mode)

    def _on_frame_type_changed(self) -> None:
        """
        Emits a signal when the user changes the frame type.
        """
        frame_type = FrameType(self.frame_type_dropdown.currentText())
        self.frame_type_changed.emit(frame_type)

    def update_display(self, view_data: ViewData) -> None:
        """
        Updates the frame display with new data.

        :param view_data: Data needed to update the UI.
        """
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
        """
        Returns the maximal dimension the frame image can have.

        :return: Tuple containing the width and height of the scroll area.
        """
        width = self.scroll_area.size().width()
        height = self.scroll_area.size().height()

        return width, height
