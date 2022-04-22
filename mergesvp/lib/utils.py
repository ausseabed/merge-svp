import math
from typing import Tuple

# collection of utility functions

def dms_to_decimal(
        degrees: float,
        minutes: float = 0,
        seconds: float = 0) -> float:
    """Converts lat or long provided as degrees, minutes, and seconds into
    decimal form"""
    abs_degrees = abs(degrees)
    abs_decimal = abs_degrees + minutes / 60 + seconds / 3600
    return math.copysign(abs_decimal, degrees)


def decimal_to_dms(val: float) -> Tuple[int, int, float]:
    """Converts lat or long provided as a decimal to degrees, minutes, and 
    seconds"""
    # int() will truncate
    abs_val = abs(val)
    d = int(abs_val)
    m = int((abs_val - d) * 60)
    s = (abs_val - d - m / 60) * 3600
    return (math.copysign(d, val), m, s)
