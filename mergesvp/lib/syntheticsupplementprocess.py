""" Code for filling the time gaps between SVP profiles with synthetic 
data.
"""

from datetime import datetime, timedelta
from tkinter import FLAT
import click
import os
import math
from pathlib import Path
from typing import List, TextIO, Tuple

from mergesvp.lib.svpprofile import SvpProfile
from mergesvp.lib.parsers import CarisSvpParser
from mergesvp.lib.utils import sort_svp_list, timedelta_to_hours

def load_svps(path: Path, fail_on_error: bool) -> List[SvpProfile]:
    """ Loads multiple SVPs from each of the paths provided, returns them all
    in a single list. Must be paths to CARIS formatted SVP files.
    """

    svp_parser = CarisSvpParser()
    svp_parser.fail_on_error = fail_on_error

    svps = svp_parser.read_many(path)
    return svps


def find_gaps(
        svps: List[SvpProfile],
        time_threshold: float) -> List[Tuple[SvpProfile, SvpProfile, float]]:
    """
    Finds the gaps in the list of SVPs whereby the time between two SVPs
    exceeds the time_threshold.

    Args:
        svps: List of SVPs sorted by timestamp
        time_threshold: only gaps larger than this time (in hours) will
            be returned by this function
    
    Returns:
        A list of tuples, each tuple includes the SVP at the beginning of
        the gap, the SVP at the end of the gap, and the total duration of
        the gap (in hours)
    """
    gaps = []

    prev_svp = None
    for svp in svps:
        if prev_svp is not None:
            dt = svp.timestamp - prev_svp.timestamp
            dt_hours = timedelta_to_hours(dt)
            if dt_hours > time_threshold:
                gap = (prev_svp, svp, dt_hours)
                gaps.append(gap)
        
        prev_svp = svp
    
    return gaps


def get_synthetic_svp(
        time: datetime,
        latitude: float,
        longitude: float) -> SvpProfile:
    """ Generates a synthetic SVP for the given time and location
    """
    synthetic_svp = SvpProfile()
    synthetic_svp.timestamp = datetime

    return synthetic_svp


def get_supplement_coords(
        svp_start: SvpProfile,
        svp_end: SvpProfile,
        interval: float) -> List[Tuple[datetime, float, float]]:
    """
    Gets the coordination (lat, long, time) for the SVPs that need to be
    created to fill in the gaps.

    Args:
        svp_start: the last real SVP (non-synthetic) before the gap
        svp_end: the last real SVP after the gap
        interval: time (in hours) between each SVP created to fill the gap
    
    Returns:
        List of tuples, each tuple contains the timestamp (datetime) and
        latitude/longitude
    """
    coords_list = []

    dt = timedelta(hours=interval)
    current_time = svp_start.timestamp + dt
    
    while current_time < svp_end.timestamp:
        # TODO: get actual spatial coord
        latitude = 2.0
        longitude = 2.0
        coord = (current_time, latitude, longitude)
        coords_list.append(coord)

        current_time += dt

    return coords_list


def calc_interval(
        svp_start: SvpProfile,
        svp_end: SvpProfile,
        time_threshold) -> float:
    """
    Calculates an optimal interval over a gap period so that supplemental
    SVPs will be evenly distributed
    """
    dt = svp_end.timestamp - svp_start.timestamp
    dt_hours = timedelta_to_hours(dt)
    steps = dt_hours / time_threshold
    return math.ceil(steps)


def synthetic_supplement_svp_process(
        input: Path,
        output: TextIO,
        fail_on_error: bool,
        time_threshold: float = 4) -> None:
    """
    Main entry point for the synthetic supplement process whereby synthetic
    SVP profiles are generate to fill in the gaps between recorded SVPs. Only
    gaps greater than the time_threshold are filled in.

    Args:
        input: Path to input CARIS formatted SVP file
        output: CARIS SVP output with supplemented synthetic SVPs
        fail_on_error: escalates any warnings that occur to exceptions
        time_threshold: only periods larger than this time (in hours) will
            be supplemented with synthetic SVPs

    Returns:
        None

    Raises:
        Exception: Raises an exception.

    """
    svps = load_svps(input)
    # sort the list of SVPs by timestamp. In most cases this will already be
    # done, but users may include unsorted files that haven't been generated
    # by merge svp
    svps = sort_svp_list(svps)


