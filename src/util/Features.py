from enum import Enum, unique
from copy import copy, deepcopy


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
    INTRADAY_VOL = "VOL"



@unique
class PositionType(Enum):
    SHORT = "SHORT"
    LONG = "LONG"
    NOT_INVESTED = "NOT_INVESTED"
