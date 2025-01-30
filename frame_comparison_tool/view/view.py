from datetime import datetime
from pathlib import Path
from typing import override, Optional

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QImage, QKeyEvent, QResizeEvent, QMouseEvent, QCloseEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QPushButton, QHBoxLayout, QComboBox, \
    QLabel, QFileDialog, QSpinBox, QMessageBox

from frame_comparison_tool.utils import FrameType, DisplayMode, ViewData, Direction, check_path
from frame_comparison_tool.view.eliding_label import ElidingLabel
from frame_comparison_tool.view.pannable_scroll_area import PannableScrollArea
from frame_comparison_tool.view.spinning_circle import SpinningCircle
from frame_comparison_tool.utils.video_formats import VideoFormats


class View(QMainWindow):
    """
    A graphical user interface for the frame comparison tool.

    This class creates and manages the GUI components for video frame comparison.
    It communicates with the ``Presenter`` through signals to handle user interactions.

    Signals:
        - ``add_source_requested``: Emitted when user requests to add new video sources.
        - ``delete_source_requested``: Emitted when user requests to delete a video source.
        - ``mode_changed``: Emitted when display mode is changed.
        - ``frame_changed``: Emitted when user navigates between frames.
        - ``source_changed``: Emitted when user switches between video sources.
        - ``resize_requested``: Emitted when window is resized.
        - ``frame_type_changed``: Emitted when frame type changes.
        - ``offset_changed``: Emitted when user offsets a frame.
        - ``seed_changed``: Emitted when random seed value changes.
        - ``n_samples_changed``: Emitted when number of samples changes.
        - ``shown``: Emitted when window is first shown.
        - ``exit_app_requested``: Emitted when application exit is requested.
    """

    add_source_requested = Signal(list)
    delete_source_requested = Signal(Path)
    mode_changed = Signal(DisplayMode)
    frame_changed = Signal(Direction)
    source_changed = Signal(Direction)
    resize_requested = Signal(tuple)
    frame_type_changed = Signal(FrameType)
    offset_changed = Signal(Direction)
    seed_changed = Signal(int)
    n_samples_changed = Signal(int)
    shown = Signal(tuple)
    exit_app_requested = Signal()
    save_images_requested = Signal(str)
    offset_all_frames_requested = Signal(Direction)

    def __init__(self):
        """
        Initializes a ``View`` instance with all UI components.
        """
        super().__init__()

        self.presenter: Optional['Presenter'] = None
        """``Presenter`` instance."""

        self._init_ui()

    def _init_ui(self) -> None:
        """
        Initialize and configure all UI components.
        """
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle(f'Frame Comparison Tool')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setSpacing(10)
        self.central_layout.setContentsMargins(10, 10, 10, 10)
        self.central_layout.setSpacing(4)

        self.frame_widget = QLabel()
        self.frame_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.scroll_area = PannableScrollArea()
        self.scroll_area.setWidget(self.frame_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scroll_area.setMinimumHeight(300)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_layout.addWidget(self.scroll_area, stretch=6)

        self.loading_circle = SpinningCircle()
        self.central_layout.addWidget(self.loading_circle, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.config_widget = QWidget()
        self.config_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.central_layout.addWidget(self.config_widget, stretch=0)

        self.config_layout = QHBoxLayout(self.config_widget)
        self.config_layout.setSpacing(8)
        self.config_layout.setContentsMargins(10, 10, 10, 10)
        self.config_layout.addStretch()

        self._seed_timer = QTimer()
        self._seed_timer.setSingleShot(True)
        self._seed_timer.timeout.connect(self._emit_seed)

        self._n_samples_timer = QTimer()
        self._n_samples_timer.setSingleShot(True)
        self._n_samples_timer.timeout.connect(self._emit_n_samples)

        self.n_samples_container = QHBoxLayout()
        self.n_samples_label = QLabel("Number of frames:")
        self.spin_box_n_samples = QSpinBox()
        self.spin_box_n_samples.setValue(5)
        self.spin_box_n_samples.valueChanged.connect(self._on_n_samples_changed)
        self.spin_box_n_samples.setRange(1, 100)
        self.spin_box_n_samples.setFixedWidth(100)
        self.spin_box_n_samples.wheelEvent = lambda event: None
        self.n_samples_container.addWidget(self.n_samples_label)
        self.n_samples_container.addWidget(self.spin_box_n_samples)
        self.config_layout.addLayout(self.n_samples_container)
        self.config_layout.addStretch(1)

        self.seed_container = QHBoxLayout()
        self.seed_label = QLabel("Seed:")
        self.spin_box_seed = QSpinBox()
        self.spin_box_seed.setRange(0, 1000000)
        self.spin_box_seed.setValue(42)
        self.spin_box_seed.valueChanged.connect(self._on_seed_changed)
        self.spin_box_seed.setFixedWidth(100)
        self.spin_box_seed.wheelEvent = lambda event: None
        self.seed_container.addWidget(self.seed_label)
        self.seed_container.addWidget(self.spin_box_seed)
        self.config_layout.addLayout(self.seed_container)
        self.config_layout.addStretch(1)

        self.frame_type_container = QHBoxLayout()
        self.frame_type_label = QLabel("Frame type:")
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
        self.frame_type_dropdown.wheelEvent = lambda event: None
        self.frame_type_container.addWidget(self.frame_type_label)
        self.frame_type_container.addWidget(self.frame_type_dropdown)
        self.config_layout.addLayout(self.frame_type_container)
        self.config_layout.addStretch(1)

        self.display_mode_container = QHBoxLayout()
        self.display_mode_label = QLabel("Display mode:")
        self.mode_dropdown = QComboBox(self.config_widget)
        self.mode_dropdown.addItems([mode.value for mode in DisplayMode])
        self.mode_dropdown.currentTextChanged.connect(self._on_mode_changed)
        self.mode_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.mode_dropdown.wheelEvent = lambda event: None
        self.display_mode_container.addWidget(self.display_mode_label)
        self.display_mode_container.addWidget(self.mode_dropdown)
        self.config_layout.addLayout(self.display_mode_container)
        self.config_layout.addStretch(1)

        self.add_source_button = QPushButton('Add', self.config_widget)
        self.add_source_button.clicked.connect(self._on_add_source_clicked)
        self.add_source_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.add_source_button.setFixedWidth(70)
        self.config_layout.addWidget(self.add_source_button)
        self.added_sources_widgets: list[QWidget] = []

        self.setLayout(self.central_layout)
        self.setFocus()

    def set_init_values(self, files: Optional[list[Path]], n_samples: int, seed: int, frame_type: FrameType,
                        display_mode: DisplayMode) -> None:
        """
        Set initial values for all configurable parameters.

        :param files: Optional list of initial video file paths.
        :param n_samples: Initial number of frames to sample.
        :param seed: Initial random seed value.
        :param frame_type: Initial frame type.
        :param display_mode: Initial display mode.
        """

        self.spin_box_n_samples.setValue(n_samples)
        self.spin_box_seed.setValue(seed)
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
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event by requesting application exit.

        :param event: Close event object.
        """

        self.exit_app_requested.emit()
        super().closeEvent(event)

    @override
    def show(self) -> None:
        """
        Show main window and emit initial frame size.
        """

        super().show()
        self.shown.emit(self.get_max_frame_size())

    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Handle window resize by updating frame display size.

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
        - Ctrl + S: Save frames
        - Ctrl + Plus/Minus: Offset all frames of a certain source

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
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Plus:
            self.offset_all_frames_requested.emit(Direction(1))
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Minus:
            self.offset_all_frames_requested.emit(Direction(-1))
        elif event.key() == Qt.Key.Key_Plus:
            self.offset_changed.emit(Direction(1))
        elif event.key() == Qt.Key.Key_Minus:
            self.offset_changed.emit(Direction(-1))
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            formatted_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.save_images_requested.emit(formatted_date)

        return super().keyPressEvent(event)

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse clicks by setting window focus.

        :param event: Mouse press event object.
        """
        self.setFocus()
        super().mousePressEvent(event)

    def display_error_message(self, message: str, window_title: str = " ") -> None:
        """
        Display an error message dialog to the user.

        :param message: Error message to display.
        :param window_title: Title for error dialog window.
        """

        error_msg = QMessageBox(self)
        error_msg.setWindowTitle(window_title)
        error_msg.setText(message)
        error_msg.setIcon(QMessageBox.Icon.Warning)

        error_msg.exec()

    def _on_add_source_clicked(self) -> None:
        """
        Emits a signal when the user adds a new video source.
        """

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilters(VideoFormats.get_file_filters())

        if file_dialog.exec():
            files: set[Path] = set(map(Path, file_dialog.selectedFiles()))
            if files:
                valid_paths: set[Path] = set(filter(check_path, files))
                invalid_paths: set[Path] = files - valid_paths

                if valid_paths:
                    self.add_source_requested.emit(list(valid_paths))

                if invalid_paths:
                    invalid_paths_str = '\n'.join(str(invalid_path) for invalid_path in invalid_paths)
                    error_text = f"An error occurred with these files:\n{invalid_paths_str}"
                    self.display_error_message(message=error_text)

    def on_add_sources(self, file_paths: list[tuple[Path, bool]]) -> None:
        """
        Process multiple added video sources.

        :param file_paths: List of tuples containing a file path and their success status
        where the status indicates if the source was added.
        """

        added_paths = set(filter(lambda x: x[1], file_paths))
        discarded_paths = set(file_paths) - added_paths

        for file_path, status in added_paths:
            self.on_add_source(file_path=file_path)

        if discarded_paths:
            invalid_paths = '\n'.join(map(lambda path: str(path[0]), discarded_paths))
            error_text = f"An error occurred with these files:\n{invalid_paths}"
            self.display_error_message(message=error_text)

    def on_add_source(self, file_path: Path) -> None:
        """
        Add a new video source to the UI.

        :param file_path: Path to the video source.
        """

        main_widget = QWidget()
        main_widget.setFixedHeight(40)

        widget_layout = QHBoxLayout(main_widget)
        widget_layout.setContentsMargins(8, 2, 8, 2)
        widget_layout.setSpacing(4)

        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setText("📁")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget_layout.addWidget(icon_label)

        source_label = ElidingLabel(str(file_path))

        file_size = file_path.stat().st_size / (1024 * 1024)

        if file_size < 1024:
            file_size_str = f"{file_size:7.2f} MiB"
        else:
            file_size /= 1024
            file_size_str = f"{file_size:7.2f} GiB"

        file_size_label = QLabel(file_size_str)

        delete_button = QPushButton('Delete')
        delete_button.setFixedWidth(70)
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_button.clicked.connect(lambda: self._on_delete_clicked(file_path))

        main_widget.setLayout(widget_layout)
        widget_layout.addWidget(source_label, stretch=1)
        widget_layout.addWidget(file_size_label)
        widget_layout.addWidget(delete_button)

        self.central_layout.addWidget(main_widget)
        self.added_sources_widgets.append(main_widget)

        self.central_layout.update()
        self.update()

    def on_delete_source(self, src_idx: int) -> None:
        """
        Delete source from the UI.

        :param src_idx: Index of the deleted source.
        """

        widget_to_remove = self.added_sources_widgets.pop(src_idx)
        widget_to_remove.setParent(None)
        widget_to_remove.deleteLater()

        self.central_layout.update()
        self.update()

    def _emit_n_samples(self) -> None:
        """
        Emits a signal when the number of samples changes.
        """

        self.n_samples_changed.emit(self.spin_box_n_samples.value())

    def _on_n_samples_changed(self) -> None:
        """
        Starts debouncing timer when number of samples changes.
        """

        self._n_samples_timer.start(1000)

    def _emit_seed(self) -> None:
        """
        Emits a signal when the seed value changes.
        """

        self.seed_changed.emit(self.spin_box_seed.value())

    def _on_seed_changed(self) -> None:
        """
        Starts debouncing timer when seed value changes.
        """

        self._seed_timer.start(1000)

    def _on_delete_clicked(self, file_path: Path) -> None:
        """
        Emits a signal when the user deletes a source.

        :param file_path: Path to the video source.
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

            self.frame_widget.setMinimumSize(pixmap.size())
            self.frame_widget.setFixedSize(pixmap.size())
            self.frame_widget.setPixmap(pixmap)

            self.frame_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setFocus()

    def get_max_frame_size(self) -> tuple[int, int]:
        """
        Returns the maximal dimension the frame image can have.

        :return: Tuple containing the width and height of the scroll area.
        """

        viewport = self.scroll_area.viewport()
        width = viewport.width()
        height = viewport.height()

        return width, height
