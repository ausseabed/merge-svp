"""
Module includes functions/classes to support the parsing and processing
of trackline data (positions of the ship undertaking the survey).
"""
from __future__ import annotations
from datetime import datetime
from operator import le
from pathlib import Path
import json
from typing import List, Tuple
from mergesvp.lib.geojson import GeojsonFeature, GeojsonLineStringFeature, GeojsonRoot

from mergesvp.lib.utils import lerp, timedelta_to_hours


class TracklinePoint:
    """ Class represents a single point recorded on the trackline
    """

    def __init__(
            self,
            timestamp: datetime,
            latitude: float,
            longitude: float,
            depth: float) -> None:
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        self.depth = depth


    def lerp(self, other: TracklinePoint, timestamp: datetime) -> TracklinePoint:
        """ Uses linear interpolation to generate a new trackline point where
        the vessel would have been at the given timestamp between two existing
        TracklinePoints.
        """

        dt_start_end = timedelta_to_hours(other.timestamp - self.timestamp)
        dt_start_ts = timedelta_to_hours(timestamp - self.timestamp)
        t = dt_start_ts / dt_start_end

        new_lat = lerp(self.latitude, other.latitude, t)
        new_long = lerp(self.longitude, other.longitude, t)
        new_depth = lerp(self.depth, other.depth, t)

        return TracklinePoint(
            timestamp=timestamp,
            latitude=new_lat,
            longitude=new_long,
            depth=new_depth
        )


class Trackline:
    """ A Trackline is a collection of TracklinePoints that defines the path
    a vessel has taken
    """

    @staticmethod
    def get_containing_trackline(
            tracklines: List[Trackline],
            timestamp: datetime) -> Trackline:
        """ Gets the trackline that the timestamp falls in. If the timestamp
        falls outside of all tracklines then None is returned.
        """
        for trackline in tracklines:
            if trackline.is_in(timestamp):
                return trackline
        return None


    @staticmethod
    def merge_tracklines(tracklines: List[Trackline]) -> Trackline:
        """ Merges multiple tracklines into a single trackline
        """
        ids = [str(tl.line_id) for tl in tracklines]
        ids_str = ','.join(ids)
        merged_trackline = Trackline(line_id=ids_str, file=None)

        pts = []
        for tl in tracklines:
            pts.extend(tl.points)

        merged_trackline.points = pts

        return merged_trackline


    @staticmethod
    def filter_duplicate_points(trackline: Trackline) -> Trackline:
        """ Removes all duplicate points (points that have the same 
        timestamp) from the trackline. Operates on the given tracklines
        object.
        """
        filtered_points = []
        last_point = None
        for point in trackline.points:
            if last_point is None:
                # first point
                filtered_points.append(point)
            elif last_point.timestamp != point.timestamp:
                # not a duplicate if they dont have the same timestamp
                filtered_points.append(point)
            else:
                # the it's a duplicate point, so skip it
                pass
                # print(f"dup pt at {str(point.timestamp)}")
            last_point = point

        trackline.points = filtered_points

        return trackline


    def __init__(self, line_id: str, file: Path) -> None:
        """
        Args:
            line: the line id string of this trackline
            file: filename that this trackline was read from
        """
        self.line_id = line_id
        self.file = file

        # list of trackline points
        self.points = []


    def append(self, point: TracklinePoint) -> None:
        """
        Args:
            point: new TracklinePoint to append to this Trackline
        """
        self.points.append(point)


    def is_in(self, timestamp: datetime) -> bool:
        """ Returns true if the given timestamp is in between (or equal to)
        the start and end of this trackline.
        """
        first_pt = self.points[0].timestamp
        last_pt = self.points[-1].timestamp
        return timestamp >= first_pt and timestamp <= last_pt


    def get_lerp_point(self, timestamp: datetime) -> TracklinePoint:
        """ Calculates the location of the ship for the given timestamp by
        linear interpolation of the trackline points in this trackline.
        """
        if not self.is_in(timestamp):
            raise RuntimeError(
                f"Given timestamp ({timestamp}) is not within this trackline "
                f"based on the start ({self.points[0].timestamp}) and end "
                f"({self.points[-1].timestamp}) times."
            )
        
        prev_pt = None
        for pt in self.points:
            if prev_pt is None:
                prev_pt = pt
            elif prev_pt.timestamp <= timestamp and pt.timestamp > timestamp:
                # then we've found where this timestamp fits in
                break

        lerp_pt = prev_pt.lerp(pt, timestamp)
        return lerp_pt


    def to_geojson_object(self) -> GeojsonFeature:
        """ Generates a GeojsonFeature that represents this trackline
        """
        feature = GeojsonLineStringFeature()
        feature.properties['line_id'] = self.line_id
        geojson_points = [
            [tl_pt.longitude, tl_pt.latitude]
            for tl_pt in self.points
        ]

        feature.points = geojson_points
        return feature


class TracklinesParser:
    """ Reads CSV formatted tracklines data into Tracklines objects 
    """

    def __init__(self) -> None:
        self.file = None
        self.tracklines = []
        # each file may contain multiple tracklines, this variable is the 
        # trackline that is currently being parsed.
        self._current_trackline = None
        self.date_format = r'%d/%m/%y'


    def _process_line(self, line: str) -> Tuple[str, TracklinePoint]:
        """ Parses the text line into a trackline point object.

        Args:
            line: csv formatted line read from a tracklines file
        
        Returns:
            Tuple; first element is the track id, second is a TracklinePoint
                object containing the position data (location, timestamp)
        """
        line_bits = line.split(',')
        # merge date and time components so we can parse them together
        date_str = line_bits[0] + ' ' + line_bits[1]
        date_format = self.date_format + r' %H:%M:%S.%f'
        
        tl_id = line_bits[2]
        pt = TracklinePoint(
            timestamp=datetime.strptime(date_str, date_format),
            latitude=float(line_bits[4]),
            longitude=float(line_bits[3]),
            depth=float(line_bits[5])
        )

        return tl_id, pt


    def _process_lines(self, lines: List[str]) -> List[Trackline]:
        for line in lines:
            tl_id, tl_p = self._process_line(line)

            if (self._current_trackline is None) or (
                    self._current_trackline.line_id != tl_id):
                # then this is the first trackline being read from the file
                # OR
                # we've hit a new trackline, so make a new one and switch
                # the current trackline over to the new one.
                self._current_trackline = Trackline(
                    line_id=tl_id,
                    file=self.file
                )
                self.tracklines.append(self._current_trackline)

            self._current_trackline.append(tl_p)


    def read(self, file: Path) -> List[Trackline]:
        """ Reads a list of tracklines from a trackline file
        """
        self.file = file
        self.tracklines = []
        self._current_trackline = None

        with file.open('r') as f:
            # skip first line as it is just the header
            f.readline()
            lines = f.read().splitlines()
            self._process_lines(lines)

        return self.tracklines


def tracklines_to_geojson_file(
        tracklines: List[Trackline],
        output_file: Path) -> None:
    """ Writes a list of tracklines to a geojson file
    """
    geojson_object = GeojsonRoot()
    for trackline in tracklines:
        geojson_object.feature_collection.add_feature(
            trackline.to_geojson_object()
        )

    geojson = geojson_object.to_geojson()

    with output_file.open('w') as f:
        f.write(
            json.dumps(
                geojson,
                indent=2
            )
        )
