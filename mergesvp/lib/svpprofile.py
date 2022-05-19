from datetime import datetime
from enum import Enum


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
        longitude: float = None
    ) -> None:
        self.filename = filename
        # in general timestamp, lat and long should be taken from the SvpSource
        # object and not from here. No technical reason for this, this is the
        # precedence used in the current manual process.
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        # array with each element being a tuple of (depth, sound speed)
        self.depth_speed = []
        # list of warning messages generated when parsing file
        self.warnings = []

    def has_warning(self) -> bool:
        return len(self.warnings) != 0

        
