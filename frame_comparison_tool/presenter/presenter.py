from pathlib import Path

from frame_comparison_tool.model import Model
from frame_comparison_tool.view import View


class Presenter:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.view.set_presenter(self)

    def add_source(self, file_path: Path) -> bool:
        if self.model.add_source(file_path):
            self.update_display()
            return True
        else:
            return False

    # TODO: Check this
    def delete_source(self, file_path: str) -> int:
        return self.model.delete_source(file_path)

    def change_frame(self, direction: int) -> None:
        self.model.curr_frame_idx += direction
        self.model.curr_frame_idx = max(0, min(self.model.curr_frame_idx, len(self.model.frame_ids) - 1))
        self.update_display()

    def change_source(self, direction: int) -> None:
        self.model.curr_src_idx += direction
        self.model.curr_src_idx = max(0, min(self.model.curr_src_idx, len(self.model.sources) - 1))
        self.update_display()

    def update_display(self) -> None:
        mode = self.view.mode_dropdown.currentText()

        if len(self.model.sources) == 0:
            self.view.update_display(None, mode)
        else:
            frame = self.model.get_current_frame()
            self.view.update_display(frame, mode)
