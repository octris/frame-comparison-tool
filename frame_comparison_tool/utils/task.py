from enum import Enum


class Task(Enum):
    """
    Enumeration representing possible ``Worker`` tasks.
    """

    SAMPLE = 'Sample'
    """
    Sample frames.
    """
    RESAMPLE = 'Resample'
    """
    Resample frames.
    """
    OFFSET = 'Offset'
    """
    Offset frame.
    """
    OFFSET_ALL = "Offset all"
    """
    Offset all frames.
    """
