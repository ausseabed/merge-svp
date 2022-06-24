from datetime import datetime
from enum import Enum
from typing import List, Tuple
from pathlib import Path
import json

from mergesvp.lib.geojson import GeojsonFeature, GeojsonPointFeature, GeojsonRoot


class SvpProfileFormat(Enum):
    L0 = 1
    L2 = 2
    CARIS = 3


class SvpProfile:
    """ SvpProfile contains the Sound Velocity Profile (SVP) data 
    (depth vs speed) for one location """

    def __init__(
        self,
        filename: str = None,
        timestamp: datetime = None,
        latitude: float = None,
        longitude: float = None,
        depth_speed: List[Tuple[float, float]] = None
    ) -> None:
        self.filename = filename
        # in general timestamp, lat and long should be taken from the SvpSource
        # object and not from here. No technical reason for this, this is the
        # precedence used in the current manual process.
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        # array with each element being a tuple of (depth, sound speed)
        if depth_speed is None:
            self.depth_speed = []
        else:
            self.depth_speed = depth_speed
        # list of warning messages generated when parsing file
        self.warnings = []

    def has_warning(self) -> bool:
        return len(self.warnings) != 0

    def to_geojson_object(self) -> GeojsonFeature:
        geojson_obj = GeojsonPointFeature()
        geojson_obj.point = [self.longitude, self.latitude]
        geojson_obj.properties = {
            'timestamp': str(self.timestamp)
        }
        return geojson_obj


def svps_to_geojson_file(
        svps: List[SvpProfile],
        output_file: Path) -> None:
    """ Writes a list of SVPs to a geojson file
    """
    geojson_object = GeojsonRoot()
    for svp in svps:
        geojson_object.feature_collection.add_feature(
            svp.to_geojson_object()
        )

    geojson = geojson_object.to_geojson()

    with output_file.open('w') as f:
        f.write(
            json.dumps(
                geojson,
                indent=2
            )
        )
