""" Code for merging multiple L0 and L2 SVP files into a single CARIS
formatted SVP file.
"""
import click
import csv
import os
import logging
import time
from email import header
from datetime import datetime
from typing import BinaryIO, TextIO, List, Tuple
from pathlib import Path

from mergesvp.lib.errors import SvpMissingDataException
from mergesvp.lib.svpprofile import SvpProfile
from mergesvp.lib.parsers import CarisSvpParser, get_svp_profile_format, get_svp_parser
from mergesvp.lib.svplist import SvpSource, parse_svp_line
from mergesvp.lib.utils import trim_to_longest_dive

logger = logging.getLogger(__name__)


def get_svp_list(input: TextIO) -> List[SvpSource]:
    """ Parses the input csv file into a list of SvpSource objects
    """
    csvreader = csv.reader(input)
    header = next(csvreader) # disregard header line

    svp_list = []
    for row in csvreader:
        src_fn = os.path.basename(input.name)
        svp = parse_svp_line(row, src_fn, csvreader.line_num)
        svp_list.append(svp)

    return svp_list


def find_svp_profile_file(filename: str, base_folder: Path) -> Path:
    """ Attempts to find the SVP profile file in one of the expected
    locations. Raises `SvpMissingDataException` if the SVP profile
    file listed in the SVP source CSV file cannot be found.
    """
    # first check the base folder, then L0, then L2
    if (base_folder / filename).exists():
        return base_folder / filename
    elif (base_folder / 'L0' / filename).exists():
        return base_folder / 'L0' / filename
    elif (base_folder / 'L2' / filename).exists():
        return base_folder / 'L2' / filename
    else:
        raise SvpMissingDataException(
            f'Could not find SVP profile file "{filename}" '
            f'under folder {base_folder}'
        )


def _get_svp(filename: Path, fail_on_error: bool) -> None:
    # find out what format this SVP profile uses
    svp_format = get_svp_profile_format(filename)
    # get a parser to read this file
    svp_parser = get_svp_parser(svp_format)
    svp_parser.fail_on_error = fail_on_error
    # read the svp file into a SVP profile object

    svp = svp_parser.read(filename)

    return svp


def patch_svp(src: SvpSource, svp: SvpProfile) -> None:
    # replace the entire depth vs speed profile with a trimmed version
    # that only includes the deepest dive part
    svp.depth_speed = trim_to_longest_dive(svp.depth_speed)

    # some attributes read from individual SVP files should be replaced
    # by what was included in the source list file (the CSV one)
    svp.latitude = src.latitude
    svp.longitude = src.longitude
    svp.timestamp = src.timestamp


def patch_svp_profiles(svps: List[Tuple[SvpSource, SvpProfile]]) -> None:
    """Performs some additional processing/modifying of the SVP profiles.
    This currently includes filtering out unnecessary parts of the depth vs
    sound profile.
    """
    for (svp_src, svp_profile) in svps:
        patch_svp(svp_src, svp_profile)


def generate_merged_output(
        svp_source_list: List[SvpSource],
        base_folder: Path,
        output: TextIO,
        fail_on_error: bool) -> None:
    """Generates the merged SVP output file"""
    # iterate through each SvpSource object (effectivity each line of
    # the CSV file that gives us a SVP profile filename, date, and
    # location)
    svps = []
    with click.progressbar(svp_source_list, label="Reading SVP files") as svp_sources:
        for svp_source in svp_sources:
            svp_profile_fn = find_svp_profile_file(
                svp_source.filename,
                base_folder
            )
            svp = _get_svp(svp_profile_fn, fail_on_error)
            # append both the source info and the SVP profile data
            # when writing the merged file we use the src data for lat/lng/date
            src_and_svp = (svp_source, svp)
            svps.append(src_and_svp)

    if not fail_on_error:
        # then no exceptions have been thrown, but there could be warning
        # messages so show these to the user.
        for (src, svp) in svps:
            if svp.has_warning():
                logger.warn(f"File {svp.filename} generated the following errors when parsing contents")
                for msg in svp.warnings:
                    logger.warn(f"    {msg}")

    # update details of the SvpProfiles
    patch_svp_profiles(svps)

    # svps was a list of tuples including a SvpSource, and SvpProfile
    # we only need to write the SvpProfile info now that it has been
    # patched
    svps_only = [svp for (_, svp) in svps]

    writer = CarisSvpParser()
    writer.show_progress = True
    output_path = Path(os.path.realpath(output.name))
    writer.write_many(output_path, svps_only)


def merge_raw_svp_process(input: TextIO, output: TextIO, fail_on_error: bool) -> None:
    svps = get_svp_list(input)
    
    # base folder is what we assume is root of all possible
    # locations for the SVP profile files. SVP profiles must be located
    # under this folder in the same dir, or L0, or L2
    # Assume the base folder is the folder that the 
    base_folder = Path(input.name).parent

    generate_merged_output(svps, base_folder, output, fail_on_error)

    header = None
