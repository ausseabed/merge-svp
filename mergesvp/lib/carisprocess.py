""" Code for reading multiple CARIS SVP files, stripping out duplicates, and
outputting a single CARIS SVP file along with some summary information.
"""
import click
import os
from pathlib import Path
from typing import List, TextIO, Tuple

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


def depth_speed_compare(
        a: List[Tuple[float, float]],
        b: List[Tuple[float, float]]) -> bool:
    """ Compares the values in the two tuple lists (a and b), will return
    true only if all the values are the same. Used to check if two sound
    velocity profiles are duplicates."""
    if len(a) != len(b):
        return False

    for i in range(0, len(a)):
        a_depth, a_speed = a[i]
        b_depth, b_speed = b[i]

        if a_depth != b_depth or a_speed != b_speed:
            return False

    return True


def group_by_depth_speed(svps: List[SvpProfile]) -> List[List[SvpProfile]]:
    """ Groups all SVPs into a list of lists based on common depth vs speed
    profiles. This doesn't strip duplicates, it groups them all together.
    """
    svp_groups = []
    
    with click.progressbar(svps, label="Finding duplicate SVPs") as input_svps:
        for svp in input_svps:
            matched_group = None
            
            for svp_group in svp_groups:
                # all groups of SVPs will have at least one entry
                first_group_svp = svp_group[0]
                if depth_speed_compare(svp.depth_speed, first_group_svp.depth_speed):
                    matched_group = svp_group
                    break
                
            if matched_group is not None:
                matched_group.append(svp)
            else:
                new_group = [svp]
                svp_groups.append(new_group)
    
    return svp_groups


def merge_caris_svp_process(
        path: Path,
        output: TextIO,
        fail_on_error: bool) -> None:
    
    svp_paths = find_svp_files(path)
    svps = load_svps(svp_paths, fail_on_error)
    # group all the svps that have the same depth vs speed data
    svp_groups = group_by_depth_speed(svps)

    # we can include only one of each SVP is we get the first SVP from each
    # group of SVPs. Each group of SVPs share the same depth vs speed data, but
    # may have a different time/location/filename
    svp_no_dups = [svp_group[0] for svp_group in svp_groups]

    # now write output file
    writer = CarisSvpParser()
    writer.show_progress = True
    output_path = Path(os.path.realpath(output.name))
    writer.write_many(output_path, svp_no_dups)

    # print some summary info to StdOut
    click.echo(f"{len(svp_paths)} SVP files were found in folder structure")
    click.echo(f"{len(svps)} SVPs were read from these files")
    click.echo(f"{len(svp_no_dups)} Unique profiles were found")


