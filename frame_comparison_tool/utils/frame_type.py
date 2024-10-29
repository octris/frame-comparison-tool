from aenum import MultiValueEnum


class FrameType(MultiValueEnum):
    """
    Enumeration representing video frame types.
    """

    B_TYPE = 'B-Type', 66
    """B-frame"""
    I_TYPE = 'I-Type', 73
    """I-frame"""
    P_TYPE = 'P-Type', 80
    """P-frame"""
    UNKNOWN = 'Unknown', 63
    """Unknown frame type."""
