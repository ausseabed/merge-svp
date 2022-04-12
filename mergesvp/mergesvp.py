import click

from mergesvp.lib.process import merge_svp_process

@click.command()
@click.option(
    '-i', '--input',
    required=True,
    type=click.File('r'),
    help="Path to CSV file including reference to SVP files, locations and timestamps."
)
@click.option(
    '-o', '--output',
    type=click.File('w'),
    help="Output location for merged SVP file."
)
def merge_svp(input, output):
    merge_svp_process(input, output)


if __name__ == '__main__':
    merge_svp()
