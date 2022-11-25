""" Code for generating a complete set of synthetic SVP data based on trackline
data
"""

import click
import os
import time
from pathlib import Path
from typing import TextIO, List, Tuple
from datetime import datetime, timedelta

from mergesvp.lib.svpprofile import SvpProfile, svps_to_geojson_file
from mergesvp.lib.parsers import CarisSvpParser
from mergesvp.lib.tracklines import \
    Trackline, \
    TracklinesParser, \
    tracklines_to_geojson_file
from mergesvp.lib.ssminterface import get_ssm_synthetic_svp


def get_synthetic_svp(
        time: datetime,
        trackline: Trackline) -> SvpProfile:
    """ Generates a synthetic SVP for the given time based on the trackline
    data.
    """
    # get the interpolated location of this time based on the trackline
    # data
    lerp_point = trackline.get_lerp_point(time)

    synthetic_svp = SvpProfile()
    synthetic_svp.timestamp = time
    synthetic_svp.latitude = lerp_point.latitude
    synthetic_svp.longitude = lerp_point.longitude

    svp_data = get_ssm_synthetic_svp(
        latitude=lerp_point.latitude,
        longitude=lerp_point.longitude,
        timestamp=time
    )
    synthetic_svp.depth_speed = svp_data

    return synthetic_svp


class SyntheticSvpProcessor:
    """ Performs the several steps required to generate a complete set
    of SVP profiles that follow the provided tracklines data
    """

    def __init__(
            self,
            tracklines_input: Path,
            output: TextIO,
            time_gap: float = 4,
            generate_summary: bool = False,
            fail_on_error: bool = False,
            date_format: str = r'%d/%m/%y') -> None:
        self.tracklines_input = tracklines_input
        self.output = output
        self.time_gap = time_gap
        # should the process generate some spatial summary files that
        # show what SVPs were generated
        self.generate_summary = generate_summary
        self.fail_on_error = fail_on_error
        self.date_format = date_format

        # list of SvpProfiles
        self.svps = []
        # merged version of all tracklines loaded from the tracklines_input 
        self.trackline = []
        # list of warning messages (str)
        self.warnings = []


    def _validate_trackline(self):
        if len(self.trackline.points) < 2:
            raise RuntimeError("Trackline must include at least 2 points")

        last_time = None
        for pt in self.trackline.points:
            if last_time is not None:
                if last_time > pt.timestamp:
                    raise RuntimeError(
                        "Trackline points not in chronological order")
            last_time = pt.timestamp


    def _get_svp_times(self) -> List[datetime]:
        """ Gets a list of datetimes for when synthetic SVPs should be
        generated.
        """
        start = self.trackline.points[0].timestamp
        end = self.trackline.points[-1].timestamp
        current = start
        dt = timedelta(hours=self.time_gap)

        svp_times = [] 
        while current <= end:
            svp_times.append(current)
            current += dt

        return svp_times


    def process(self):
        # load the tracklines data. Location information for each synthetic SVP
        # is derived from this data
        parser = TracklinesParser()
        parser.date_format = self.date_format
        tracklines = parser.read(self.tracklines_input)
        if self.generate_summary:
            tl_geojson = Path(self.output.name + '_tracklines.geojson')
            tracklines_to_geojson_file(tracklines, tl_geojson)

        # merge all tracklines into a single trackline
        # makes processing easier and gives more reasonable results as
        # SVP location picking will not restart at the beginning of each arbitrary
        # trackline
        self.trackline = Trackline.merge_tracklines(tracklines)

        # remove points on the trackline that have the same date and time, this
        # breaks the interpolation process when calculating location.
        self.trackline = Trackline.filter_duplicate_points(self.trackline)

        # check trackline points are in the right order
        self._validate_trackline()

        svp_times = self._get_svp_times()

        with click.progressbar(svp_times, label="Generating synthetic SVPs") as svp_ts:
            self.svps = [
                get_synthetic_svp(svp_time, self.trackline)
                for svp_time in svp_ts
            ]

        if self.generate_summary:
            svp_synth_geojson = Path(self.output.name + '_synth_svps.geojson')
            svps_to_geojson_file(self.svps, svp_synth_geojson)

        # now write output file
        writer = CarisSvpParser()
        writer.show_progress = True
        output_path = Path(os.path.realpath(self.output.name))
        writer.write_many(output_path, self.svps)


def synthetic_svp_process(
        tracklines: Path,
        output: TextIO,
        time_gap: float = 4,
        generate_summary: bool = False,
        fail_on_error: bool = False,
        date_format: str = r'%d/%m/%y') -> None:
    """
    Main entry point for the synthetic process whereby synthetic SVP
    profiles are generated along the entire length of a tracklines dataset.
    Profiles are generated at a frequency based on the `time_gap` parameter

    Args:
        tracklines: Path to CSV file including trackline data
        output: CARIS SVP output with supplemented synthetic SVPs
        generate_summary: generate a summary geojson file that includes
            locations of synthetic SVP data
        fail_on_error: escalates any warnings that occur to exceptions
        time_gap: time between each synthetic SVP profile

    Returns:
        None

    Raises:
        Exception: Raises an exception.
    """
    processor = SyntheticSvpProcessor(
        tracklines_input=tracklines,
        output=output,
        time_gap=time_gap,
        generate_summary=generate_summary,
        fail_on_error=fail_on_error,
        date_format=date_format
    )
    processor.process()
