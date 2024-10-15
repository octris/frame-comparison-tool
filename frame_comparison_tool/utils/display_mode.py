from enum import Enum


class DisplayMode(Enum):
    """
    Enumeration representing how a certain frame will be displayed inside the application.
    """

    CROPPED = 'Cropped'
    """
    Displays part of the frame that fits inside the application.
    """
    SCALED = 'Scaled'
    """
    Scales down the frame to fit its longest side inside the application.
    """
