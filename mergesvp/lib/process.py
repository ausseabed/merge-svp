import click
import csv
import os
from email import header
from datetime import datetime
from typing import BinaryIO, TextIO, List
from pathlib import Path

from mergesvp.lib.errors import SvpMissingDataException, SvpParsingException
from mergesvp.lib.svpprofile import get_svp_profile_format, get_svp_read_function

class SvpSource:
    """ Data model class for details read from source file listing individual
    SVP profiles, and their time and location """
    def __init__(
        self,
        filename: str,
        timestamp: datetime,
        latitude: float,
        longitude:float
    ) -> None:
        self.filename = filename
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self) -> str:
        return (
            f'SVP filename: {self.filename}\n'
            f' {self.timestamp.isoformat()}\n'
            f' {self.latitude}, {self.longitude}\n'
        )


def parse_svp_line(row: List[str], filename:str = None, line_num: int = -1) -> SvpSource:
    """ Parses the CSV data from the source input file into a `SvpSource`
    object. Peforms error checking on input data and raises a 
    `SvpParsingException` if validation fails.
    """
    if len(row) != 4:
        msg = (
            f'Unexpected formatting found in {filename} at line '
            f'{line_num}, expected 4 data columns'
        )
        raise SvpParsingException(msg)

    filename = row[0]
    try:
        # Format expected is 28/05/2015 23:49:31
        timestamp = datetime.strptime(row[1], r'%d/%m/%Y %H:%M:%S')
        latitude = float(row[2])
        longitude = float(row[3])
    except ValueError as e:
        msg = (
            f'Unable to parse data in {filename} at line '
            f'{line_num}, check date format and lat/long values.'
        )
        raise SvpParsingException(msg)

    svp = SvpSource(filename, timestamp, latitude, longitude)
    return svp


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
    # first check the base folder, then L0, then L3
    if (base_folder / filename).exists():
        return base_folder / filename
    elif (base_folder / 'L0' / filename).exists():
        return base_folder / 'L0' / filename
    elif (base_folder / 'L1' / filename).exists():
        return base_folder / 'L1' / filename
    else:
        raise SvpMissingDataException(
            f'Could not find SVP profile file "{filename}" '
            f'under folder {base_folder}'
        )


def _get_svp(filename: Path) -> None:
    # find out what format this SVP profile uses
    svp_format = get_svp_profile_format(filename)
    # get a function to read this file
    svp_reader = get_svp_read_function(svp_format)
    # read the svp file into a SVP profile object
    svp = svp_reader(filename)

    return svp


def generate_merged_output(
        svp_source_list: List[SvpSource],
        base_folder: Path,
        output: TextIO) -> None:
    """Generates the merged SVP output file"""
    # iterate through each SvpSource object (effectivity each line of
    # the CSV file that gives us a SVP profile filename, date, and
    # location)
    with click.progressbar(svp_source_list) as svp_sources:
        for svp_source in svp_sources:
            svp_profile_fn = find_svp_profile_file(
                svp_source.filename,
                base_folder
            )
            svp = _get_svp(svp_profile_fn)





def merge_svp_process(input: TextIO, output: TextIO) -> None:
    svps = get_svp_list(input)
    
    # base folder is what we assume is root of all possible
    # locations for the SVP profile files. SVP profiles must be located
    # under this folder in the same dir, or L0, or L3
    # Assume the base folder is the folder that the 
    base_folder = Path(input.name).parent

    generate_merged_output(svps, base_folder, output)

    header = None
