from pathlib import Path

from frame_comparison_tool.utils.extension_filters import VIDEO_EXTENSIONS


def check_path(file_path: Path) -> bool:
    return file_path.exists() and file_path.is_file() and _is_valid_extension(file_path)


def _is_valid_extension(file_path: Path) -> bool:
    return file_path.suffix in VIDEO_EXTENSIONS
