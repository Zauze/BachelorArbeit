from enum import Enum

class DataLabel(Enum):
    """
    Provides enums for data attributes
    """
    DATE = 0,
    TIME = 1,
    TITLE = 2,
    LOCATION = 3,
    SHORT_DESC = 4,
    LONG_DESC = 5,
    LINK = 6,
    NOISE = 99,
    UNKNOWN = 100