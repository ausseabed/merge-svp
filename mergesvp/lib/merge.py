# Functions for writing merged SVP file

from typing import TextIO, List
from pathlib import Path
from typing import BinaryIO, TextIO, List

from mergesvp.lib.svpprofile import SvpProfile
from mergesvp.lib.svplist import SvpSource
from mergesvp.lib.utils import decimal_to_dms


def write_merged_header(output: TextIO) -> None:
    """Writes the header information to output, in this case it is a single
    text line followed by the filename itself"""
    lines = [
        "[SVP_VERSION_2]\n",
        Path(output.name).name + "\n"
    ]
    output.writelines(lines)


def __formatted_dms(val: float) -> str:
    dms = decimal_to_dms(val)
    return f"{dms[0]}:{dms[1]}:{dms[2]}"


def _get_merged_svp_lines(src: SvpSource, svp: SvpProfile) -> List[str]:

    # example SVP section header line
    # Section 2015-148 23:49:31 -12:14:35.00 130:55:40.00
    date_str = src.timestamp.strftime('%Y-%j')
    lat_str = __formatted_dms(src.latitude)
    lng_str = __formatted_dms(src.longitude)
    header_line = f"Section {date_str} {lat_str} {lng_str}\n"

    svp_lines = [
        f"{depth:.6f} {speed:.6f}\n"
        for (depth, speed) in svp.depth_speed
    ]

    svp_lines.insert(0, header_line)
    return svp_lines


def write_merged_svp(output: TextIO, src: SvpSource, svp: SvpProfile) -> None:
    """Writes the SvpSource and SvpProfile objects to the output stream
    in the merged SVP format"""
    lines = _get_merged_svp_lines(src, svp)
    output.writelines(lines)

