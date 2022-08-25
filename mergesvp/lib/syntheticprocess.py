""" Code for generating a complete set of synthetic SVP data based on trackline
data
"""

from pathlib import Path
from typing import TextIO

def synthetic_svp_process(
        tracklines: Path,
        output: TextIO,
        time_gap: float = 4,
        generate_summary: bool = False,
        fail_on_error: bool = False) -> None:
    """
    Main entry point for the synthetic process whereby synthetic SVP
    profiles are generated along the entire length of a tracklines dataset.
    Profiles are generated at a frequency based on the `time_gap` parameter

    Args:
        tracklines: Path to CSV file including trackline data
        output: CARIS SVP output with supplemented synthetic SVPs
        generate_summary: generate a summary geojson file that includes
            locations of synthetic SVN data
        fail_on_error: escalates any warnings that occur to exceptions
        time_gap: time between each synthetic SVP profile

    Returns:
        None

    Raises:
        Exception: Raises an exception.
    """
    pass