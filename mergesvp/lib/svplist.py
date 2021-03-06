from datetime import datetime
from typing import List

from mergesvp.lib.errors import SvpMissingDataException, SvpParsingException

class SvpSource:
    """ Data model class for details read from source file listing individual
    SVP profiles, and their time and location """

    def __init__(
        self,
        filename: str,
        timestamp: datetime,
        latitude: float,
        longitude: float
    ) -> None:
        self.filename = filename
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self) -> str:
        return (
            f'SVP filename: {self.filename}\n'
            f' {self.timestamp.isoformat()}\n'
            f' {self.latitude}, {self.longitude}\n'
        )


def parse_svp_line(row: List[str], filename: str = None,
                   line_num: int = -1) -> SvpSource:
    """ Parses the CSV data from the source input file into a `SvpSource`
    object. Peforms error checking on input data and raises a
    `SvpParsingException` if validation fails.
    """
    if len(row) != 4:
        msg = (
            f'Unexpected formatting found in {filename} at line '
            f'{line_num}, expected 4 data columns'
        )
        raise SvpParsingException(msg)

    filename = row[0]
    try:
        # Format expected is 28/05/2015 23:49:31
        timestamp = datetime.strptime(row[1], r'%d/%m/%Y %H:%M:%S')
        latitude = float(row[2])
        longitude = float(row[3])
    except ValueError as e:
        msg = (
            f'Unable to parse data in {filename} at line '
            f'{line_num}, check date format and lat/long values.'
        )
        raise SvpParsingException(msg)

    svp = SvpSource(filename, timestamp, latitude, longitude)
    return svp
