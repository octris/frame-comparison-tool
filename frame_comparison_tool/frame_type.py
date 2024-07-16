from enum import Enum


class FrameType(Enum):
    UNKNOWN = 63
    B_TYPE = 66
    I_TYPE = 73
    P_TYPE = 80

    def __str__(self):
        return self.name
