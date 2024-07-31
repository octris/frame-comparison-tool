from PySide6.QtWidgets import QApplication

from frame_comparison_tool.model import Model
from frame_comparison_tool.presenter import Presenter
from frame_comparison_tool.view import View


def main():
    app = QApplication([])
    model = Model()
    view = View()
    presenter = Presenter(model, view)
    view.show()
    app.exec()


if __name__ == '__main__':
    main()
