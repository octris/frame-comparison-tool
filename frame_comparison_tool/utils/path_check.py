from pathlib import Path


def check_path(file_path_str: str) -> bool:
    try:
        Path(file_path_str).resolve(strict=True)
        return True
    except (RuntimeError, FileNotFoundError):
        return False
