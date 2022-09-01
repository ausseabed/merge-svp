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
            fail_on_error: bool = False) -> None:
        self.tracklines_input = tracklines_input
        self.output = output
        self.time_gap = time_gap
        # should the process generate some spatial summary files that
        # show what SVPs were generated
        self.generate_summary = generate_summary
        self.fail_on_error = fail_on_error

        # list of SvpProfiles
        self.svps = []
        # merged version of all tracklines loaded from the tracklines_input 
        self.trackline = []
        # list of warning messages (str)
        self.warnings = []


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

            if trackline is None:
                self.warnings.append(
                    f"Could not identify trackline that covers time {current_time} "
                    "this SVP was skipped"
                )
                current_time += dt
                continue

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
        fail_on_error: bool = False) -> None:
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
        fail_on_error=fail_on_error
    )
    processor.process()
