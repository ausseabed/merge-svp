# merge-svp
Command line utility for merging Sound Velocity Profiles into single file format supported by Teledyne CARIS

[![Test](https://github.com/ausseabed/merge-svp/actions/workflows/merge-svp-app.yml/badge.svg)](https://github.com/ausseabed/merge-svp/actions/workflows/merge-svp-app.yml)

## Dependencies
Merge SVP was written for Python 3.8, earlier versions may work but have not been tested.

## Installation

**Note:** More detailed instructions for end users of Merge SVP are provided [here](./docs/installation.md). The following steps on this page are intended more for developers.

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
