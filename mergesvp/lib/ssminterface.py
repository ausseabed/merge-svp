""" Utilities for interacting with the Sound Speed Manager code
for generation of synthetic sound velocity profiles based on 
World Ocean Atlas data.
https://github.com/hydroffice/hyo2_soundspeed
"""

import os
import logging
from datetime import datetime
from typing import List, Tuple

from mergesvp.lib.errors import SyntheticSvpGenerationException
from hyo2.soundspeed.atlas.abstract import AbstractAtlas
from hyo2.soundspeed.atlas.woa18 import Woa18, AbstractAtlas
from hyo2.abc.lib.progress.cli_progress import CliProgress


logging.basicConfig()


def get_data_folder() -> str:
    """ returns a folder path (str) where the World Ocean Atlas data
    files will be stored.
    """
    folder = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(folder, 'data\\woa18')
    return folder


class Proj:
    """ Mock SSM project class, some of the altas modules within SSM
    require a project object with a progress attribute.
    """
    def __init__(self) -> None:
        self.progress = CliProgress()


def get_ssm_atlas() -> AbstractAtlas:
    """ Returns an atlas object that can be used to generate synthetic
    velocity profiles.
    """
    atlas = Woa18(
        data_folder=get_data_folder(),
        prj=Proj()
    )

    if not atlas.is_present():
        logging.info("WOA data not found locally, download will commence")
        atlas.data_folder = os.path.join(atlas.data_folder, 'tmp')
        os.makedirs(atlas.data_folder)
        atlas.download_db()
        atlas.data_folder = get_data_folder()

    return atlas


def get_ssm_synthetic_svp(
        latitude: float,
        longitude: float,
        timestamp: datetime) -> List[Tuple[float, float]]:
    """ Generates a synthetic SVP based on the given location and time. Will
    raise a SyntheticSvpGenerationException if the process fails.
    """
    atlas = get_ssm_atlas()
    profiles = atlas.query(lat=latitude, lon=longitude, dtstamp=timestamp)

    if profiles is None or len(profiles.l) == 0:
        raise SyntheticSvpGenerationException(
            "Failed to generate synthetic SVP profiles"
        )

    # SSM returns a list of 3 profiles, use the first
    ssm_svp = profiles.l[0]

    if ssm_svp.data.num_samples == 0 or len(ssm_svp.data.depth) == 0:
        raise SyntheticSvpGenerationException(
            "Synthetic SVP profile is empty"
        )

    svp_data = []
    for count in range(ssm_svp.data.num_samples):
        depth = ssm_svp.data.depth[count]
        speed = ssm_svp.data.speed[count]
        svp_data.append( (depth, speed) )

    return svp_data
