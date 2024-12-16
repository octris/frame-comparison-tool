from pathlib import Path

from frame_comparison_tool.utils.video_formats import VideoFormats

"""
Utilities for validating video file paths.
"""


def _is_valid_extension(file_path: Path) -> bool:
    """
    Check if file has a supported video extension.

    :param file_path: Path to check.
    :return: ``True`` if extension is supported, ``False`` otherwise.
    """

    return VideoFormats.is_supported_extension(file_path.suffix)


def check_path(file_path: Path) -> bool:
    """
    Validate that a path exists, is a file, and has a supported video extension.

    :param file_path: Path to validate.
    :return: ``True`` if all checks pass, ``False`` otherwise.
    """

    return file_path.exists() and file_path.is_file() and _is_valid_extension(file_path)
