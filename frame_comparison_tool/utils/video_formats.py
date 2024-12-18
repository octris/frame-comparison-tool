from typing import Final


class VideoFormats:
    """
    A class that defines supported video formats and provides utilities for file dialog filtering.
    """

    MIME_TYPES: Final[list[str]] = [
        "video/x-matroska",
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-ms-wmv",
        "video/x-flv",
        "video/mpeg",
        "video/x-m4v",
        "video/3gpp",
        "video/mp2t",
        "video/webm",
    ]
    """List of MIME types for supported video formats."""

    EXTENSIONS: Final[list[str]] = [
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
    """List of file extensions for supported video formats."""

    @classmethod
    def get_file_filters(cls) -> list[str]:
        """
        Returns file dialog filter strings for supported video formats.

        :return: List of supported video formats.
        """
        return [
            f"All Video Files (*{' *'.join(cls.EXTENSIONS)})",
            *(f"{ext[1:].upper()} (*{ext})" for ext in cls.EXTENSIONS)
        ]

    @classmethod
    def is_supported_mime_type(cls, mime_type: str) -> bool:
        """
        Checks if the given MIME type is supported.

        :param mime_type: The MIME type to check.
        :return: ``True`` if the MIME type is supported, ``False`` otherwise.
        """
        return mime_type in cls.MIME_TYPES

    @classmethod
    def is_supported_extension(cls, extension: str) -> bool:
        """
        Checks if the given file extension is supported.

        :param extension: The file extension to check (including the dot).
        :return: ``True`` if the extension is supported, ``False`` otherwise.
        """
        return extension.lower() in cls.EXTENSIONS
