""" Code for reading multiple CARIS SVP files, stripping out duplicates, and
outputting a single CARIS SVP file along with some summary information.
"""
from pathlib import Path
from typing import List, TextIO


def find_svp_files(current_path: Path) -> List[Path]:
    svp_paths = current_path.glob("**/svp")
    return svp_paths


def merge_caris_svp_process(
        path: Path,
        output: TextIO,
        fail_on_error: bool) -> None:
    
    svp_paths = find_svp_files(path)

    for p in svp_paths:
        print(p)

