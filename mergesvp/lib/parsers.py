from asyncore import read
from pathlib import Path
from typing import List, TextIO, Iterable
from datetime import datetime
import click

from mergesvp.lib.errors import ParserNotImplemeneted, SvpParsingException
from mergesvp.lib.svpprofile import SvpProfile, SvpProfileFormat
from mergesvp.lib.utils import dms_to_decimal, decimal_to_dms

class SvpParser:
    """ Base class for all parsers that read or write SvpProfiles
    """
    def __init__(self) -> None:
        # does this parser read multiple SVPs from a single file
        # should be set in all child classes
        self.supports_many_svps = False
        self.fail_on_error = True
        self.show_progress = False

    def read(self, path: Path) -> SvpProfile:
        return self.read_many(path)[0]

    def write(self, path: Path, svp: SvpProfile) -> None:
        self.write_many([svp])

    def read_many(self, path: Path) -> List[SvpProfile]:
        raise ParserNotImplemeneted(
            f"read_many function not implemented for {type(self).__name__}")

    def write_many(self, path: Path, svps: List[SvpProfile]) -> None:
        raise ParserNotImplemeneted(
            f"write_many function not implemented for {type(self).__name__}")


class L0SvpParser(SvpParser):
    """
    """
    def __init__(self) -> None:
        super().__init__()
        self.supports_many_svps = False

    def _validate_L0(self, svp: SvpProfile) -> None:
        """ Runs a few checks of the data included in the SvpProfile object,
        includes warnings if anything seems missing.
        """
        if svp.latitude is None:
            svp.warnings.append("Missing latitude, please check file header info")
        if svp.longitude is None:
            svp.warnings.append("Missing longitude, please check file header info")
        if svp.timestamp is None:
            svp.warnings.append("Missing date, please check file header info")

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
    def _parse_l0_header_line(self, line: str, svp: SvpProfile) -> None:
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


    def _is_l0_body_line(self, line: str) -> bool:
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
    def _parse_l0_body_line(self, line: str, svp: SvpProfile) -> None:
        line_vals = [float(line_bit) for line_bit in line.split()]
        depth_and_speed = (line_vals[0], line_vals[2])
        svp.depth_speed.append(depth_and_speed)

    def _parse_l0(
            self,
            lines: List[str],
            filename: Path = None) -> SvpProfile:
        """Parses the lines into an SVP object"""
        svp = SvpProfile()

        parsing_header = True
        for (i, line) in enumerate(lines):
            try:
                if parsing_header and not self._is_l0_body_line(line):
                    self._parse_l0_header_line(line, svp)
                else:
                    parsing_header = False
                    self._parse_l0_body_line(line, svp)

            except Exception as ex:
                svp.warnings.append(f"Failed to parse line number {i+1}")
                if self.fail_on_error:
                    msg = f"error parsing file {filename} at line {i+1}"
                    raise SvpParsingException(msg)

        self._validate_L0(svp)
        return svp

    def _read_l0(self, filename: Path) -> SvpProfile:
        """Reads a L0 formatted SVP file"""
        with filename.open('r') as file:
            lines = file.read().splitlines()
            return self._parse_l0(lines, filename)


    def read(self, path: Path) -> SvpProfile:
        svp = self._read_l0(path)
        svp.filename = path
        return svp


class L2SvpParser(SvpParser):
    """ Reads L2 formatted SVP data
    """

    def __init__(self) -> None:
        super().__init__()
        self.supports_many_svps = False

    ## example L2 header line
    # ( SoundVelocity  1.0 0 201505282349 -12.24305556 130.92777780 -1 0 0 SSM_2021.1.7 P 0088 )
    def _parse_l2_header_line(line: str, svp: SvpProfile) -> None:
        line_stripped = line.strip(['(', ')', ' '])
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
    def _parse_l2_body_line(self, line: str, svp: SvpProfile) -> None:
        line_vals = [float(line_bit) for line_bit in line.split()]
        depth_and_speed = (line_vals[0], line_vals[1])
        svp.depth_speed.append(depth_and_speed)


    def _read_l2(self, filename: Path) -> SvpProfile:
        """Reads a L2 formatted SVP file"""
        svp = SvpProfile()

        with filename.open('r') as file:
            lines = file.read().splitlines()
            for (i, line) in enumerate(lines):
                if i == 0:
                    # there is only a single header line in L2 data
                    self._parse_l2_header_line(line, svp)
                else:
                    self._parse_l2_body_line(line, svp)
        return svp


    def read(self, path: Path) -> SvpProfile:
        svp = self._read_l2(path)
        svp.filename = path
        return svp


class CarisSvpParser(SvpParser):
    """ Reads and writes CARIS formatted SVP files, these may contain multiple
    SVP profiles for different locations and times.
    """

    def __init__(self) -> None:
        super().__init__()
        self.supports_many_svps = True

        self._current_line_number = None
        self._current_filename = None

    def _write_header(self, output: TextIO) -> None:
        """Writes the header information to output, in this case it is a single
        text line followed by the filename itself"""
        lines = [
            "[SVP_VERSION_2]\n",
            Path(output.name).name + "\n"
        ]
        output.writelines(lines)


    def __formatted_dms(self, val: float) -> str:
        dms = decimal_to_dms(val)
        return f"{dms[0]}:{dms[1]}:{dms[2]}"


    def _get_caris_svp_lines(self, svp: SvpProfile) -> List[str]:

        # example SVP section header line
        # Section 2015-148 23:49:31 -12:14:35.00 130:55:40.00
        date_str = svp.timestamp.strftime('%Y-%j %H:%M:%S')
        lat_str = self.__formatted_dms(svp.latitude)
        lng_str = self.__formatted_dms(svp.longitude)
        header_line = f"Section {date_str} {lat_str} {lng_str}\n"

        svp_lines = [
            f"{depth:.6f} {speed:.6f}\n"
            for (depth, speed) in svp.depth_speed
        ]

        svp_lines.insert(0, header_line)
        return svp_lines


    def _write_all_svps(
            self,
            svps: Iterable[SvpProfile],
            output: TextIO) -> None:

        # loop through each of the SVPs we have and write them to the same
        # output
        for svp in svps:
            lines = self._get_caris_svp_lines(svp)
            output.writelines(lines)


    def write_many(self, path: Path, svps: List[SvpProfile]) -> None:
        with path.open(mode='w') as output:
            # write header to file
            self._write_header(output)
            if self.show_progress:
                with click.progressbar(svps, label="Writing merged SVP file") as svps_iter:
                    self._write_all_svps(svps_iter, output)
            else:
                self._write_all_svps(svps, output)


    def _read_section_header(
            self, svp: SvpProfile, line: str) -> None:
        """Populates svp with data read from the given header line"""
        linebits = line.split()
        if (len(linebits) < 5):
            msg = (
                "Error reading section header information from line number"
                f"{self._current_line_number} in file {self._current_filename}"
            )
            raise SvpParsingException(msg)
        line_date_time = linebits[1] + " " + linebits[2]
        line_lat = linebits[3]
        line_lng = linebits[4]

        svp.timestamp = datetime.strptime(line_date_time, '%Y-%j %H:%M:%S')

        lat_vals = [float(s) for s in line_lat.split(':')[0:3]]
        svp.latitude = dms_to_decimal(*lat_vals)
        lng_vals = [float(s) for s in line_lng.split(':')[0:3]]
        svp.longitude = dms_to_decimal(*lng_vals)

        # Note: some section headers include a "Datagram time:" this is not
        # currently extracted by the above code.


    def _parse_body_line(self, svp: SvpProfile, line: str) -> None:
        linebits = line.split()
        depth_speed = (float(linebits[0]), float(linebits[1]))
        svp.depth_speed.append((depth_speed))


    def _read_many(self, lines: List[str]) -> List[SvpProfile]:
        svps = []
        # the active SVP that data is being read into
        svp = None
        for (i, line) in enumerate(lines):
            self._current_line_number = i + 1  # first line number is 1
            if line.startswith('Section '):
                # then it's the beginning of a new sound velocity profile
                svp = SvpProfile()
                svp.filename = self._current_filename
                svps.append(svp)
                self._read_section_header(svp, line)
            elif svp is None:
                # then we haven't yet read a 'Section' from the SVP file, so skip
                # these lines till we do. There is a single '[SVP_VERSION_2]' file,
                # sometimes followed by 'CONVERT - ...' line.
                pass
            else:
                self._parse_body_line(svp, line)

        return svps


    def read_many(self, path: Path) -> List[SvpProfile]:
        self._current_filename = str(path)
        with path.open('r') as file:
            lines = file.read().splitlines()
            return self._read_many(lines)


def get_svp_parser(format: SvpProfileFormat) -> SvpParser:
    """Factory type function that returns a function that is able to
    read the SVP format given"""
    if format == SvpProfileFormat.L0:
        return L0SvpParser()
    elif format == SvpProfileFormat.L2:
        return L2SvpParser()
    elif format == SvpProfileFormat.CARIS:
        return CarisSvpParser()
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
        elif first_line.startswith('[SVP_VERSION_2]'):
            return SvpProfileFormat.CARIS
        else:
            raise SvpParsingException(
                f'Could not identify SVP file type of {filename}')
