class NoMatchingFrameTypeError(Exception):
    def __init__(self, frame_type):
        self.message = f"Could not find frame that matches type {frame_type}"
        super().__init__(self.message)


class ImageReadError(Exception):
    def __init__(self, message="Could not read image"):
        self.message = message
        super().__init__(self.message)


class VideoCaptureFailed(Exception):
    def __init__(self, message="Video capture not opened"):
        self.message = message
        super().__init__(self.message)


class FrameIndexError(Exception):
    def __init__(self, idx):
        self.message = f"Could not set frame at index {idx}"
        super().__init__(self.message)


class InvalidOffsetError(ValueError):
    def __init__(self, offset):
        self.message = f"Invalid offset value: {offset}"
        super().__init__(self.message)


class InvalidAlignmentError(ValueError):
    def __init__(self, align):
        self.message = f"Invalid align value supplied: {align}"
        super().__init__(self.message)


class ZeroDimensionError(ValueError):
    def __init__(self):
        self.message = f"Width or height cannot be zero"
        super().__init__(self.message)
