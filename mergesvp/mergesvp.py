from email.policy import default
from pathlib import Path
import click
import logging

from mergesvp.lib.rawprocess import merge_raw_svp_process
from mergesvp.lib.carisprocess import merge_caris_svp_process
from mergesvp.lib.syntheticsupplementprocess import \
    synthetic_supplement_svp_process


def configure_logger():
    logging.basicConfig(level="DEBUG")


configure_logger()


@click.command()
@click.option(
    '-i', '--input',
    required=True,
    type=click.File('r'),
    help=(
        "Path to CSV file including reference to SVP files, locations "
        "and timestamps."
    )
)
@click.option(
    '-o', '--output',
    type=click.File('w'),
    help="Output location for merged SVP file."
)
@click.pass_context
def merge_raw_svp(ctx, input, output):
    """
    Merge multiple raw sound velocity profiles (SVP) as listed in a single
    CSV file into a single CARIS compatible SVP file. SVP files must be in a
    L0 or L2 format.
    """
    merge_raw_svp_process(input, output, ctx.obj['fail_on_error'])


@click.command()
@click.option(
    '-i', '--input',
    required=True,
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help=(
        "Path to root file containing multiple SVP files. This folder and "
        "all subfolders will be searched for files named 'svp' (no extension)."
    )
)
@click.option(
    '-o', '--output',
    type=click.File('w'),
    help="Output location for merged SVP file."
)
@click.option(
    '-ff', '--folder-filter',
    required=False,
    default=None,
    type=str,
    help=(
        "Restrict the folders that are searched for SVP files to ones that end "
        "in a suffix specified with this argument. This will not restrict top "
        "level folders, only immediate parents of folders containing SVP files."
    )
)
@click.pass_context
def merge_caris_svp(ctx, input, output, folder_filter):
    """ Merge multiple CARIS SVP files into a single CARIS SVP file.
    Note: duplicate profiles are removed during this process."""
    merge_caris_svp_process(
        Path(input),
        output,
        ctx.obj['fail_on_error'],
        folder_filter
    )


@click.command()
@click.option(
    '-i', '--input',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help=(
        "Path to single SVP file that includes multiple SVPs to be supplemented "
        "with synthetic SVP profiles"
    )
)
@click.option(
    '-t', '--tracklines',
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True),
    help=(
        "Path to CSV formatted tracklines file"
    )
)
@click.option(
    '-o', '--output',
    type=click.File('w'),
    help="Output location for supplemented SVP file."
)
@click.option(
    '-tt', '--time-threshold',
    required=False,
    default=4,
    type=float,
    help=(
        "The maximum time (hours) between SVPs that is allowed before synthetic "
        "SVPs are added"
    )
)
@click.option(
    '-ns', '--no-summary',
    is_flag=True,
    help=(
        "Disable generation of summary files including tracklines and "
        "locations of SVPs"
    )
)
@click.pass_context
def supplement_svp(ctx, input, tracklines, output, time_threshold, no_summary):
    """
    Fills the gaps in a series of SVPs where the time between two SVP
    profiles exceeds the given threshold
    """
    synthetic_supplement_svp_process(
        input=Path(input),
        tracklines=Path(tracklines),
        output=output,
        time_threshold=time_threshold,
        fail_on_error=ctx.obj['fail_on_error'],
        generate_summary= not no_summary
    )


@click.group()
@click.option(
    '-e', '--fail-on-error',
    is_flag=True,
    help=(
        "Should parsing errors be treated as warnings and continue, "
        "or fail and exit the application"
    )
)
@click.pass_context
def cli(ctx, fail_on_error):
    ctx.obj['fail_on_error'] = fail_on_error
    pass


cli.add_command(merge_raw_svp)
cli.add_command(merge_caris_svp)
cli.add_command(supplement_svp)


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
