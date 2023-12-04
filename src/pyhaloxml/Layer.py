"""
Layer.py
"""
import json
import logging
from typing import List
from uuid import uuid4
import geojson as gs
from lxml.etree import _Attrib
from pyhaloxml.Region import Region
from pyhaloxml.misc import Color, RegionType


class Layer:
    """
    Halo annotations are grouped in layers. They have a LineColor, Name and Visibility
    """

    def __init__(self) -> None:
        self.linecolor = Color()  # type:Color
        self.name = ""  # type:str
        self.visible = "True"  # type:str
        self.regions = []  # type:list[Region]
        self.log = logging.getLogger("HaloXML-Layer")

    def __str__(self) -> str:
        return self.tojson()

    def fromattrib(self, annotationattribs: _Attrib) -> None:
        """
        Populate the layer with information from an lxml attribute.

        :param annotationattribs: lxml attribute with information about the layer
        """
        self.linecolor.setlinecolor(annotationattribs["LineColor"])
        self.name = annotationattribs["Name"]
        self.visible = annotationattribs["Visible"]

    def fromdict(self, dinfo: dict[str, str]) -> None:
        """
        Populate the layer with information from a dictionary

        :param dinfo: dictionary with LineColor, Name and Visibility
        """
        self.linecolor.setlinecolor(dinfo["LineColor"])
        self.name = dinfo["Name"]
        self.visible = dinfo["Visible"]

    def tojson(self) -> str:
        """
        JSON representation of the layer

        :return: A jsonstring representation of this layer
        """
        return json.dumps(self.todict(), sort_keys=True)

    def todict(self) -> dict[str, str]:
        """
        Dictonary representation of the layer.
        :return:
        """
        return {
            "LineColor": self.linecolor.getlinecolor(),
            "Name": self.name,
            "Visible": self.visible,
        }

    def as_geojson(self) -> List[gs.Feature]:
        """
        A geojson representation of all regions in this layer
        """
        props = {
            "objectType": "annotation",
            "name": self.name,
            "classification": {
                "name": self.name,
                "color": self.linecolor.getrgb(),
            },
            "isLocked": False,
        }
        features = []
        for region in self.regions:
            features.append(
                gs.Feature(
                    geometry=region.as_geojson(), properties=props, id=str(uuid4())
                )
            )
        return features

    def addregion(self, region: Region) -> None:
        """
        Add a region to this layer

        :param region:
        """
        self.regions.append(region)
