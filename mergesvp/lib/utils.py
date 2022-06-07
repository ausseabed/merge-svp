from functools import reduce
import math
from sys import flags
from typing import List, Tuple
from datetime import timedelta

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


def _get_all_dives(
        depth_vs_speed: List[Tuple[float, float]]
        ) -> List[List[Tuple[float, float]]]:
    """ makes a list of all the dive segments in this series"""
    # list of all the dives
    all_dives = []
    # list of the current dives depth vs speed data
    current_dive = []
    all_dives.append(current_dive)

    last_depth = None
    for (depth, speed) in depth_vs_speed:
        if last_depth is None:
            pass
        elif depth >= last_depth:
            # then probe is going down, so still the same dive
            pass
        else:
            # then probe has moved up, so it will be a new dive
            # from this point on
            current_dive = []
            all_dives.append(current_dive)

        last_depth = depth
        current_dive.append((depth, speed))

    return all_dives


def trim_to_longest_dive(
        depth_vs_speed: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """ returns a new array of the same information that only includes the
    longest dive"""
    all_dives = _get_all_dives(depth_vs_speed)

    # compares two array lengths and returns the longest
    def red_fn(a,b):
        if len(a) > len(b):
            return a
        else:
            return b
    # get the longest array in the all_dives array
    longest_dive = reduce(red_fn, all_dives,[])

    return longest_dive


def format_timedelta(dt: timedelta) -> str:
    total_seconds = dt.total_seconds()

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{int(hours):02}h {int(minutes):02}m {int(seconds):02}s'
