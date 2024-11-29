MIME_TYPES: list[str] = [
    "video/x-matroska",
    "video/mp4",
    "video/quicktime"
    "video/x-msvideo",
    "video/x-ms-wmv",
    "video/x-flv",
    "video/mpeg",
    "video/x-m4v",
    "video/3gpp",
    "video/mp2t",
    "video/webm",
]

VIDEO_EXTENSIONS: list[str] = [
    ".mkv",
    ".mp4",
    ".mp4v",
    ".mpg4",
    ".mov",
    ".qt",
    ".avi",
    ".wmv",
    ".flv",
    ".mpeg",
    ".m1v",
    ".m2v",
    ".mpa",
    ".mpe",
    ".mpg",
    ".m4v",
    ".3gp",
    ".ts",
    ".webm"
]

FILTERS = [
    f"All Video Files (*{' *'.join(VIDEO_EXTENSIONS)})",
    *[f"{ext[1:].upper()} (*{ext})" for ext in VIDEO_EXTENSIONS]
]
