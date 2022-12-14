"""
Layer.py
"""
import json
from lxml.etree import _Attrib
from shapely import geometry as sg
from pyhaloxml.Region import Region


class Layer:
    """
    Halo annotations are grouped in layers. They have a LineColor, Name and Visibility
    """

    def __init__(self) -> None:
        self.linecolor = ""  # type:str
        self.name = ""  # type:str
        self.visible = ""  # type:str
        self.regions = []  # type:[Region]

    def __str__(self) -> str:
        return self.tojson()

    def fromattrib(self, annotationattribs: _Attrib) -> None:
        """
        Populate the layer with information from an lxml attribute.

        :param annotationattribs: lxml attribute with information about the layer
        """
        self.linecolor = annotationattribs["LineColor"]
        self.name = annotationattribs["Name"]
        self.visible = annotationattribs["Visible"]

    def fromdict(self, dinfo: dict) -> None:
        """
        Populate the layer with information from a dictionary

        :param dinfo: dictionary with LineColor, Name and Visibility
        """
        self.linecolor = dinfo["LineColor"]
        self.name = dinfo["Name"]
        self.visible = dinfo["Visible"]

    def tojson(self) -> str:
        """
        JSON representation of the layer

        :return: A jsonstring representation of this layer
        """
        return json.dumps(self.todict(), sort_keys=True)

    def todict(self) -> dict:
        """
        Dictonary representation of the layer.
        :return:
        """
        return {"LineColor": self.linecolor, "Name": self.name, "Visible": self.visible}

    def addregion(self, region: Region) -> None:
        """
        Add a region to this layer

        :param region:
        """
        self.regions.append(region)

    def as_shapely(self) -> sg.MultiPolygon:
        """
        Return the layer as shaply multipolygon

        :return: A shapely multipolygon contain all the regions in this layer.
        """
        polygons = [x.as_shapely() for x in self.regions]
        return sg.MultiPolygon(polygons)
