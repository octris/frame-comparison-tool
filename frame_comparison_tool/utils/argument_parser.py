import argparse
from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import Optional

from frame_comparison_tool.utils import check_path
from frame_comparison_tool.utils.frame_type import FrameType


class CLIArgumentsParser:
    """
    Argument parser for the Frame Comparison Tool.

    Handles setup, parsing, and validation of command line arguments for frame comparison.
    """

    def __init__(self) -> None:
        self.parser: ArgumentParser = argparse.ArgumentParser(description="Frame Comparison Tool")
        """CLI argument parser."""

        self._setup_arguments()

    def _setup_arguments(self) -> None:
        """
        Set up command line arguments.

        Configures all available command line arguments with their types and defaults.
        """

        self.parser.add_argument(
            '--files',
            type=Path,
            nargs='*',
            required=False,
            help="Path(s) to video file(s)"
        )

        self.parser.add_argument(
            '--n-samples',
            type=int,
            required=False,
            default=5,
            help="Number of frames to sample (default: 5)"
        )

        self.parser.add_argument(
            '--seed',
            type=int,
            required=False,
            default=42,
            help="Random seed for reproducibility (default: 42)"
        )

        self.parser.add_argument(
            '--frame-type',
            type=FrameType,
            choices=list(FrameType),
            required=False,
            default="B-Type",
            help="Frame type (default: B-Type)"
        )

    def _validate_paths(self, paths: Optional[list[Path]]) -> list[str]:
        """
        Validate the provided file paths.

        :param paths: Optional list of paths to validate.
        :return: List of invalid path strings, empty if all paths are valid
        """

        if not paths:
            return []

        return [
            str(path) for path in paths
            if not check_path(file_path=path)
        ]

    def parse_arguments(self) -> Namespace:
        """
        Parse and validate command line arguments.

        :return: ``Namespace`` of parsed arguments.
        :raises ``SystemExit``: if any argument is invalid.
        """

        args = self.parser.parse_args()

        invalid_paths = self._validate_paths(args.files)

        if invalid_paths:
            invalid_paths_str = '\n'.join(path for path in invalid_paths)
            self.parser.error(f'The following files do not exist:\n{invalid_paths_str}')

        return args
