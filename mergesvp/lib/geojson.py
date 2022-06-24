""" Small module to support constructing geojson files without needing
an external dependency.
"""

from typing import Dict


class GeojsonFeature:
    """ Base class for all GeoJSON feature types
    """

    def __init__(self) -> None:
        # this properties dictionary is included as the properties
        # of the GeoJSON feature
        self.properties = {}


class GeojsonPointFeature(GeojsonFeature):

    def __init__(self) -> None:
        super().__init__()
        # list of lists. Each inner list is a longitude/latitude coordinate.
        self.point = []

    def to_geojson(self) -> Dict:
        return {
            "type": "Feature",
            "properties": self.properties,
            "geometry": {
                "type": "Point",
                "coordinates": self.point
            }
        }


class GeojsonLineStringFeature(GeojsonFeature):

    def __init__(self) -> None:
        super().__init__()
        # list of lists. Each inner list is a longitude/latitude coordinate.
        self.points = []
    
    def to_geojson(self) -> Dict:
        return {
            "type": "Feature",
            "properties": self.properties,
            "geometry": {
                "type": "LineString",
                "coordinates": self.points
            }
        }


class GeojsonFeatureCollection:

    def __init__(self) -> None:
        self.features = []


    def add_feature(self, feature: GeojsonFeature) -> None:
        self.features.append(feature)


    def to_geojson(self) -> Dict:
        features = [
            feature.to_geojson()
            for feature in self.features
        ]
        return {
            "type": "FeatureCollection",
            "features": features
        }


class GeojsonRoot:

    def __init__(self) -> None:
        self.feature_collection = GeojsonFeatureCollection()

    def to_geojson(self) -> Dict:
        return self.feature_collection.to_geojson()
