from aenum import MultiValueEnum


class FrameType(MultiValueEnum):
    UNKNOWN = 'Unknown', 63
    B_TYPE = 'B-Type', 66
    I_TYPE = 'I-Type', 73
    P_TYPE = 'P-Type', 80
