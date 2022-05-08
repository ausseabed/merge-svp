from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, List

from mergesvp.lib.errors import SvpParsingException
from mergesvp.lib.utils import dms_to_decimal

class SvpProfileFormat(Enum):
    L0 = 1
    L2 = 2

class SvpProfile:
    """ SvpProfile contains the Sound Velocity Profile (SVP) data 
    (depth vs speed) for one location """

    def __init__(
        self,
        filename: str = None,
        timestamp: datetime = None,
        latitude: float = None,
        longitude: float = None
    ) -> None:
        self.filename = filename
        # in general timestamp, lat and long should be taken from the SvpSource
        # object and not from here. No technical reason for this, this is the
        # precedence used in the current manual process.
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        # array with each element being a tuple of (depth, sound speed)
        self.depth_speed = []
        # list of warning messages generated when parsing file
        self.warnings = []

    def has_warning(self) -> bool:
        return len(self.warnings) != 0


## example L0 header lines
# Now: 28/05/2015 23:49:31
# Battery Level: 1.4V
# MiniSVP: S/N 34826
# Site info: DARWIN HARBOUR
# Calibrated: 10/01/2011
# Latitude: -12 14 35 S
# Longtitude: 130 55 40 E
# Mode: P2.000000e-1
# Tare: 10.0854
# Pressure units: dBar
def _parse_l0_header_line(line: str, svp: SvpProfile) -> None:
    if line.startswith("Now:"):
        date_str = line[5:]
        date_format = r'%d/%m/%Y %H:%M:%S'
        # parsing date string will fail if there are additional characters
        # so split the string at space chars, and rejoin only the first
        # two (date and time)
        date_str = ' '.join(date_str.split()[:2])
        svp.timestamp = datetime.strptime(
            date_str, date_format
        )
    elif line.startswith("Latitude:"):
        lat_str = line.split(':')[1].strip()
        lat_vals = [float(s) for s in lat_str.split()[0:3]]
        lat = dms_to_decimal(*lat_vals)
        svp.latitude = lat
    elif (
            line.startswith("Longtitude:") or 
            line.startswith("Longitude:") or 
            line.startswith("Long:")):
        lng_str = line.split(':')[1].strip()
        lng_vals = [float(s) for s in lng_str.split()[0:3]]
        lng = dms_to_decimal(*lng_vals)
        svp.longitude = lng

def _is_l0_body_line(line: str) -> bool:
    """ Checks if the line is a body line, used to determine
    if the parser should switch to reading body lines instead of the
    header"""
    line_parts = line.split()
    if len(line_parts) == 3:
        try:
            _ = [float(line_bit) for line_bit in line.split()]
            return True
        except ValueError as e:
            return False
    return False

## example L0 body lines
# 00.040	24.047	0000.000
# 00.202	26.599	1539.508
# 00.400	26.911	1539.485
def _parse_l0_body_line(line: str, svp: SvpProfile) -> None:
    line_vals = [float(line_bit) for line_bit in line.split()]
    depth_and_speed = (line_vals[0], line_vals[2])
    svp.depth_speed.append(depth_and_speed)


def _validate_L0(svp: SvpProfile) -> None:
    """ Runs a few checks of the data included in the SvpProfile object,
    includes warnings if anything seems missing.
    """
    if svp.latitude is None:
        svp.warnings.append("Missing latitude, please check file header info")
    if svp.longitude is None:
        svp.warnings.append("Missing longitude, please check file header info")
    if svp.timestamp is None:
        svp.warnings.append("Missing date, please check file header info")


def _parse_l0(
        lines: List[str],
        fail_on_error: bool,
        filename: Path = None) -> SvpProfile:
    """Parses the lines into an SVP object"""
    svp = SvpProfile()

    parsing_header = True
    for (i, line) in enumerate(lines):
        try:
            if parsing_header and not _is_l0_body_line(line):
                _parse_l0_header_line(line, svp)
            else:
                parsing_header = False
                _parse_l0_body_line(line, svp)

        except Exception as ex:
            svp.warnings.append(f"Failed to parse line number {i+1}")
            if fail_on_error:
                msg = f"error parsing file {filename} at line {i+1}"
                raise SvpParsingException(msg)

    _validate_L0(svp)
    return svp


def _read_l0(filename: Path, fail_on_error: bool = True) -> SvpProfile:
    """Reads a L0 formatted SVP file"""
    with filename.open('r') as file:
        lines = file.read().splitlines()
        return _parse_l0(lines, fail_on_error, filename)


## example L2 header line
# ( SoundVelocity  1.0 0 201505282349 -12.24305556 130.92777780 -1 0 0 SSM_2021.1.7 P 0088 )
def _parse_l2_header_line(line: str, svp: SvpProfile) -> None:
    line_stripped = line.strip(['(',')',' '])
    line_bits = line_stripped.split()
    svp.timestamp = datetime.strptime(
        line_bits[2], r'%Y%m%d%H%M'
    )
    svp.latitude = float(line_bits[3])
    svp.longitude = float(line_bits[4])


## example L2 body lines
# 0.00 1539.51
# 0.20 1539.51
# 0.40 1539.48
def _parse_l2_body_line(line: str, svp: SvpProfile) -> None:
    line_vals = [float(line_bit) for line_bit in line.split()]
    depth_and_speed = (line_vals[0], line_vals[1])
    svp.depth_speed.append(depth_and_speed)


def _read_l2(filename: Path, fail_on_error: bool = True) -> SvpProfile:
    """Reads a L2 formatted SVP file"""
    svp = SvpProfile()

    with filename.open('r') as file:
        lines = file.read().splitlines()
        for (i, line) in enumerate(lines):
            if i == 0:
                # there are 9 header/metadata lines
                _parse_l2_header_line(line, svp)
            else:
                _parse_l2_body_line(line, svp)
    return svp


def get_svp_read_function(format: SvpProfileFormat) -> Callable[[Path], SvpProfile]:
    """Factory type function that returns a function that is able to
    read the SVP format given"""
    if format == SvpProfileFormat.L0:
        return _read_l0
    elif format == SvpProfileFormat.L2:
        return _read_l2
    else:
        raise SvpParsingException(f'Format {format} is not supported')


def get_svp_profile_format(filename: Path) -> SvpProfileFormat:
    """ Attempts to get the type of SVP file from the given path"""
    with filename.open('r') as file:
        first_line = file.readline()

        if first_line.startswith('Now:'):
            # example first line
            # Now: 28/05/2015 23:49:31
            return SvpProfileFormat.L0
        elif first_line.startswith('( SoundVelocity'):
            # example first line
            # ( SoundVelocity  1.0 0 201505282349 -12.24305556 130.92777780 -1 0 0 SSM_2021.1.7 P 0088 )
            return SvpProfileFormat.L2
        else:
            raise SvpParsingException(
                f'Could not identify SVP file type of {filename}')

        
