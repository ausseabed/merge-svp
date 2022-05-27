""" Code for reading multiple CARIS SVP files, stripping out duplicates, and
outputting a single CARIS SVP file along with some summary information.
"""
import click
from pathlib import Path
from typing import List, TextIO

from mergesvp.lib.svpprofile import SvpProfile
from mergesvp.lib.parsers import CarisSvpParser


def find_svp_files(current_path: Path) -> List[Path]:
    svp_paths = current_path.glob("**/svp")
    # glob returns a generator, convert this to a list as it will allow
    # us to better display progress (we'll know its length)
    return list(svp_paths)


def load_svps(paths: List[Path], fail_on_error: bool) -> List[SvpProfile]:
    """ Loads multiple SVPs from each of the paths provided, returns them all
    in a single list. Must be paths to CARIS formatted SVP files.
    """

    svp_parser = CarisSvpParser()
    svp_parser.fail_on_error = fail_on_error

    svps = []
    with click.progressbar(paths, label="Reading SVP files") as svp_paths:
        for path in svp_paths:
            # there can be multiple SVPs in a single CARIS formatted SVP
            # file
            svp = svp_parser.read_many(path)
            svps.extend(svp)

    return svps


def merge_caris_svp_process(
        path: Path,
        output: TextIO,
        fail_on_error: bool) -> None:
    
    svp_paths = find_svp_files(path)
    svps = load_svps(svp_paths, fail_on_error)

    print(len(svp_paths))
    print(len(svps))

