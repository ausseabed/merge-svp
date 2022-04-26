import click
import logging

from mergesvp.lib.process import merge_svp_process

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
@click.option(
    '-e', '--fail-on-error',
    is_flag=True,
    help=(
        "Should parsing errors be treated as warnings and continue, "
        "or fail and exit the application"
    )
)
def merge_svp(input, output, fail_on_error):
    merge_svp_process(input, output, fail_on_error)


def configure_logger():
    logging.basicConfig(level="DEBUG")


configure_logger()


if __name__ == '__main__':
    merge_svp()
