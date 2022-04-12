# merge-svp
Command line utility for merging Sound Velocity Profiles into single file format supported by Teledyne CARIS

## Dependencies
Merge SVP was written for Python 3.8, earlier versions may work but have not been tested.

## Installation
Clone the repository

    git clone https://github.com/ausseabed/merge-svp.git
    cd merge-svp

Install Python dependencies

    pip install -r requirements.txt

Install merge-svp (omit `-e` for non-developer install)

    pip install -e .

## Running
Once installed the inputs to the command line tool can be shown with

    mergesvp --help

## Testing
Unit tests are included in `./tests` these use the [pytest](https://docs.pytest.org/) framework and can be run using the following command.

    pytest
