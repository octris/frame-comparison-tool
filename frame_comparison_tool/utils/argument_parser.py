import argparse
from argparse import Namespace, ArgumentParser
from pathlib import Path

from frame_comparison_tool.utils import check_path
from frame_comparison_tool.utils.frame_type import FrameType


def parse_arguments() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('--files', type=Path, nargs='*', required=False)
    parser.add_argument('--n-samples', type=int, required=False, default=5)
    parser.add_argument('--seed', type=int, required=False, default=42)
    parser.add_argument('--frame-type', type=FrameType, choices=list(FrameType), required=False,
                        default="B-Type")

    args = parser.parse_args()

    invalid_paths: list[str] = []

    if args.files:
        for file_path in args.files:
            if not check_path(file_path=file_path):
                invalid_paths.append(str(file_path))

    if invalid_paths:
        invalid_paths_str = '\n'.join(path for path in invalid_paths)
        parser.error(f'The following files do not exist:\n{invalid_paths_str}')

    return args
