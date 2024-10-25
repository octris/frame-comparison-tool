from PySide6.QtWidgets import QApplication

from frame_comparison_tool.model import Model
from frame_comparison_tool.presenter import Presenter
from frame_comparison_tool.view import View
from frame_comparison_tool.utils.argument_parser import parse_arguments


def main():
    app = QApplication([])
    args = parse_arguments()
    model = Model(args.files, args.n_samples, args.seed, args.frame_type)
    view = View()
    presenter = Presenter(model, view)
    view.show()
    app.exec()


if __name__ == '__main__':
    main()
