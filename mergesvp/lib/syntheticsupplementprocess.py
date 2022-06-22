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
from mergesvp.lib.tracklines import Trackline, TracklinesParser
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
    synthetic_svp.timestamp = time
    synthetic_svp.latitude = latitude
    synthetic_svp.longitude = longitude

    return synthetic_svp


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
    steps = math.ceil(dt_hours / time_threshold)
    return dt_hours / steps


class SyntheticSvpProcessor:
    """ Performs the several steps required to generate a set of SVP profiles
    that may include some synthetic data to fill gaps
    """

    def __init__(
            self,
            input: Path,
            tracklines_input: Path,
            output: TextIO,
            time_threshold: float = 4,
            generate_summary: bool = False,
            fail_on_error: bool = False) -> None:
        self.input = input
        self.tracklines_input = tracklines_input
        self.output = output
        self.time_threshold = time_threshold
        self.generate_summary = generate_summary
        self.fail_on_error = fail_on_error
        
        # list of SvpProfiles
        self.svps = []
        # list of Tracklines
        self.tracklines = []


    def _get_supplement_coords(
            self,
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
            trackline = Trackline.get_containing_trackline(
                self.tracklines,
                current_time
            )
            # get the interpolated location of this time based on the trackline
            # data
            lerp_point = trackline.get_lerp_point(current_time)

            coord = (current_time, lerp_point.latitude, lerp_point.longitude)
            coords_list.append(coord)

            current_time += dt

        return coords_list


    def _fill_gap(self, svp1: SvpProfile, svp2: SvpProfile, dt: float) -> None:
        """ Fills the gap between the two SVPs with synthetic data at
        locations determined by interpolating the trackline data. New
        SvpProfiles are inserted into this objects list of SVPs
        """
        # get the time between the new SVPs we will generate
        interval = calc_interval(svp1, svp2, self.time_threshold)
        # list of coords that we need to get synthetic SVPs for
        supp_coords = self._get_supplement_coords(svp1, svp2, interval)

        synthetic_svps = [
            get_synthetic_svp(timestamp, latitude, longitude)
            for (timestamp, latitude, longitude) in supp_coords
        ]

        # we need to insert these new synthetic SVPs into the existing list
        # of SVPs just after the first SVP of the gap
        insertion_index = self.svps.index(svp1) + 1

        # use slicing to insert into array
        self.svps[insertion_index:insertion_index] = synthetic_svps


    def _fill_gaps(self):
        gaps = find_gaps(self.svps, self.time_threshold)
        for (svp1, svp2, dt) in gaps:
            self._fill_gap(svp1, svp2, dt)


    def process(self):
        svps = load_svps(self.input)
        # sort the list of SVPs by timestamp. In most cases this will already be
        # done, but users may include unsorted files that haven't been generated
        # by merge svp
        self.svps = sort_svp_list(svps)

        # load the tracklines data. Location information is sourced exclusively
        # from this file. SVP files can store location data, but it is typically
        # not included.
        parser = TracklinesParser()
        self.tracklines = parser.read(self.tracklines_input)

        # no fill gaps in between the existing SVPs
        self._fill_gaps()


def synthetic_supplement_svp_process(
        input: Path,
        tracklines: Path,
        output: TextIO,
        time_threshold: float = 4,
        generate_summary: bool = False,
        fail_on_error: bool = False) -> None:
    """
    Main entry point for the synthetic supplement process whereby synthetic
    SVP profiles are generate to fill in the gaps between recorded SVPs. Only
    gaps greater than the time_threshold are filled in.

    Args:
        input: Path to input CARIS formatted SVP file
        tracklines: Path to CSV file including trackline data
        output: CARIS SVP output with supplemented synthetic SVPs
        generate_summary: generate a summary geojson file that includes
            locations of synthetic SVN data
        fail_on_error: escalates any warnings that occur to exceptions
        time_threshold: only periods larger than this time (in hours) will
            be supplemented with synthetic SVPs

    Returns:
        None

    Raises:
        Exception: Raises an exception.

    """
    processor = SyntheticSvpProcessor(
        input=input,
        tracklines_input=tracklines,
        output=output,
        time_threshold=time_threshold,
        generate_summary=generate_summary,
        fail_on_error=fail_on_error
    )
    processor.process()


