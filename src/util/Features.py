from enum import Enum, unique


@unique
class Invested(Enum):
    LONG = 'LONG'
    SHORT = 'SHORT'


@unique
class Features(Enum):
    VOLUME = "VOLUME"
    HIGH = 'HIGH'
    CLOSE = 'CLOSE'
    LOW = 'LOW'
    OPEN = 'OPEN'