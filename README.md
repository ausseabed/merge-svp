# merge-svp
Command line utility for merging Sound Velocity Profiles (SVP) into single file format supported by Teledyne CARIS

[![Test](https://github.com/ausseabed/merge-svp/actions/workflows/merge-svp-app.yml/badge.svg)](https://github.com/ausseabed/merge-svp/actions/workflows/merge-svp-app.yml)

## Dependencies
Merge SVP was written for Python 3.8, earlier versions may work but have not been tested.

## Installation

**Note:** The process outlined below will provide a Python environment suitable to only part of the Merge SVP capability. Generation of synthetic SVPs requires Sound Speed Manager and all its dependencies be installed. Detailed instructions outlining this process are provided [here](./docs/installation.md).

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

The complete user guide for Merge SVP can be found here [docs/user-guide.md](./docs/user-guide.md).

## Testing
Unit tests are included in `./tests` these use the [pytest](https://docs.pytest.org/) framework and can be run using the following command.

    pytest
