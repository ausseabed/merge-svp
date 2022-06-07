""" Code for reading multiple CARIS SVP files, stripping out duplicates, and
outputting a single CARIS SVP file along with some summary information.
"""
import click
import os
from pathlib import Path
from typing import List, TextIO, Tuple

from mergesvp.lib.svpprofile import SvpProfile
from mergesvp.lib.parsers import CarisSvpParser
from mergesvp.lib.utils import format_timedelta

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


def write_grouping_summary_data(
    svp_groups: List[List[SvpProfile]], output: TextIO) -> None:
    """ Writes grouping and filename information to a CSV file. Includes all
    file names, and what group they belong to
    """
    output.write("Group number, SVP filename\n")
    for (i, svp_group) in enumerate(svp_groups):
        for svp in svp_group:
            txt = f"{i}, {svp.filename}\n"
            output.write(txt)


def write_dt_summary_data(
        svps: List[SvpProfile], output: TextIO) -> None:
    """ Writes CSV file containing the filename (with timestamp suffix) and
    the time stamp of each SVP
    """
    output.write("Timestamp, delta time, SVP filename and timestamp\n")
    last_svp = None
    for svp in svps:

        fn_ts = svp.timestamp.strftime('%Y%m%d_%H%M%S')
        svp_fn_ts = f'{svp.filename}_{fn_ts}'

        dt = "n/a"
        if last_svp is not None:
            delta_time = svp.timestamp - last_svp.timestamp
            dt = format_timedelta(delta_time)

        ts = svp.timestamp.strftime('%Y/%m/%d %H:%M:%S')

        txt = f"{ts}, {dt}, {svp_fn_ts}\n"
        output.write(txt)

        last_svp = svp


def _sort_svp_list(svps: List[SvpProfile]) -> List[SvpProfile]:
    return sorted(svps, key=lambda x: x.timestamp, reverse=False)


def merge_caris_svp_process(
        path: Path,
        output: TextIO,
        fail_on_error: bool) -> None:
    
    svp_paths = find_svp_files(path)
    svps = load_svps(svp_paths, fail_on_error)

    svps_sorted = _sort_svp_list(svps)

    # group all the svps that have the same depth vs speed data
    svp_groups = group_by_depth_speed(svps_sorted)

    # we can include only one of each SVP is we get the first SVP from each
    # group of SVPs. Each group of SVPs share the same depth vs speed data, but
    # may have a different time/location/filename
    svp_no_dups = [svp_group[0] for svp_group in svp_groups]

    # now write output file
    writer = CarisSvpParser()
    writer.show_progress = True
    output_path = Path(os.path.realpath(output.name))
    writer.write_many(output_path, svp_no_dups)

    summary_group_file = output.name + '_group_summary.csv'
    with open(summary_group_file, 'w') as summary_group_output:
        write_grouping_summary_data(svp_groups, summary_group_output)

    summary_dt_file = output.name + '_time_summary.csv'
    with open(summary_dt_file, 'w') as summary_group_output:
        write_dt_summary_data(svp_no_dups, summary_group_output)

    # print some summary info to StdOut
    click.echo(f"{len(svp_paths)} SVP files were found in folder structure")
    click.echo(f"{len(svps)} SVPs were read from these files")
    click.echo(f"{len(svp_no_dups)} Unique profiles were found")


