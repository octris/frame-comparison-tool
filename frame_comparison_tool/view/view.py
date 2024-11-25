from pathlib import Path
from typing import override, List, Optional, Tuple

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QPushButton, QHBoxLayout, QComboBox, \
    QLabel, QFileDialog, QSpinBox, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage, QKeyEvent, QResizeEvent, QMouseEvent
from frame_comparison_tool.utils import FrameType, DisplayMode, ViewData, Direction, check_path
from .pannable_scroll_area import PannableScrollArea
from .spinning_circle import SpinningCircle
from .styles import *
from ..utils.extension_filters import FILTERS


class View(QMainWindow):
    """
    This class creates the GUI for user interactions and communicates with the ``Presenter`` through signals.
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
        self.central_layout.setSpacing(10)
        self.central_layout.setContentsMargins(10, 10, 10, 10)
        self.central_layout.setSpacing(4)

        self.frame_widget = QLabel()
        self.frame_widget.setStyleSheet(FRAME_STYLE)
        self.frame_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.scroll_area = PannableScrollArea()
        self.scroll_area.setWidget(self.frame_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scroll_area.setMinimumHeight(300)
        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)
        self.central_layout.addWidget(self.scroll_area, stretch=6)

        self.loading_circle = SpinningCircle()
        self.central_layout.addWidget(self.loading_circle, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.config_widget = QWidget()
        self.config_widget.setStyleSheet(CONFIG_AREA_STYLE)
        self.config_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.central_layout.addWidget(self.config_widget, stretch=0)

        self.config_layout = QHBoxLayout(self.config_widget)
        self.config_layout.setSpacing(8)
        self.config_layout.setContentsMargins(10, 10, 10, 10)
        self.config_layout.addStretch()

        self.spin_box_n_samples = QSpinBox()
        self.spin_box_n_samples.setValue(5)
        self.spin_box_n_samples.valueChanged.connect(self._on_n_samples_changed)
        self.spin_box_n_samples.setFixedWidth(100)
        self.spin_box_n_samples.wheelEvent = lambda event: None
        self.config_layout.addWidget(self.spin_box_n_samples)

        self.spin_box_seed = QSpinBox()
        self.spin_box_seed.setRange(0, 10000)
        self.spin_box_seed.setValue(42)
        self.spin_box_seed.valueChanged.connect(self._on_seed_changed)
        self.spin_box_seed.setFixedWidth(100)
        # self.spin_box.setStyleSheet(SPIN_BOX_STYLE)
        self.spin_box_seed.wheelEvent = lambda event: None
        self.config_layout.addWidget(self.spin_box_seed)

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
        # self.frame_type_dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.frame_type_dropdown.wheelEvent = lambda event: None
        self.config_layout.addWidget(self.frame_type_dropdown)

        self.mode_dropdown = QComboBox(self.config_widget)
        self.mode_dropdown.addItems([mode.value for mode in DisplayMode])
        self.mode_dropdown.currentTextChanged.connect(self._on_mode_changed)
        self.mode_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # self.mode_dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.mode_dropdown.wheelEvent = lambda event: None
        self.config_layout.addWidget(self.mode_dropdown)

        self.add_source_button = QPushButton('Add', self.config_widget)
        self.add_source_button.clicked.connect(self._on_add_source_clicked)
        self.add_source_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.add_source_button.setFixedWidth(70)
        self.add_source_button.setStyleSheet(ADD_BUTTON_STYLE)
        self.config_layout.addWidget(self.add_source_button)

        self.added_sources_widgets: List[QWidget] = []

        self.setLayout(self.central_layout)
        self.setFocus()

    def set_init_values(self, files: Optional[List[Path]], seed: int, frame_type: FrameType, display_mode: DisplayMode):
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
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilters(FILTERS)

        if file_dialog.exec():
            files: List[str] = file_dialog.selectedFiles()

            if files:
                for file_path_str in files:
                    file_path = Path(file_path_str)

                    if check_path(file_path=file_path):
                        self.add_source_requested.emit([file_path])
                    else:
                        error_msg = QMessageBox(self)
                        error_msg.setWindowTitle(" ")
                        error_msg.setText("File does not exist.")
                        error_msg.setIcon(QMessageBox.Icon.Warning)
                        error_msg.exec()

    def on_add_source(self, file_path: Path) -> None:
        """
        Adds new source to the UI.

        :param file_path: String path to the video source.
        """
        main_widget = QWidget()
        main_widget.setFixedHeight(40)
        main_widget.setStyleSheet(SOURCE_WIDGET)

        widget_layout = QHBoxLayout(main_widget)
        widget_layout.setContentsMargins(8, 2, 8, 2)
        widget_layout.setSpacing(4)

        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setStyleSheet(FILE_ICON_LABEL_STYLE)
        icon_label.setText("📁")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget_layout.addWidget(icon_label)

        # TODO: Make as an Elided Label
        source_label = QLabel(str(file_path))
        source_label.setStyleSheet(SOURCE_LABEL_STYLE)

        delete_button = QPushButton('Delete')
        delete_button.setFixedWidth(70)  # Fixed width for consistency
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor on hover
        delete_button.setStyleSheet(DELETE_BUTTON_STYLE)
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

    def _on_n_samples_changed(self) -> None:
        self.n_samples_changed.emit(self.spin_box_n_samples.value())

    def _on_seed_changed(self) -> None:
        """
        Emits a signal when the user changes the random seed.
        """
        self.seed_changed.emit(self.spin_box_seed.value())

    def _on_delete_clicked(self, file_path: Path) -> None:
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

            self.frame_widget.setMinimumSize(pixmap.size())
            self.frame_widget.setFixedSize(pixmap.size())
            self.frame_widget.setPixmap(pixmap)

            self.frame_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setFocus()

    def get_max_frame_size(self) -> Tuple[int, int]:
        """
        Returns the maximal dimension the frame image can have.

        :return: Tuple containing the width and height of the scroll area.
        """

        viewport = self.scroll_area.viewport()
        width = viewport.width()
        height = viewport.height()

        return width, height
