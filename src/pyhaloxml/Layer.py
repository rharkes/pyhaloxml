"""
Layer.py
"""

import json
import logging
from typing import List
from uuid import uuid4
import geojson as gs
from lxml.etree import _Attrib
from .Region import Region
from .misc import Color, points_in_polygons


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

    def contains_negative(self) -> bool:
        """
        Are there any negative regions in the layer
        """
        return any([x.isnegative for x in self.regions])

    def fromattrib(self, annotationattribs: _Attrib) -> None:
        """
        Populate the layer with information from an lxml attribute.

        :param annotationattribs: lxml attribute with information about the layer
        """
        self.linecolor.setlinecolor(str(annotationattribs["LineColor"]))
        self.name = str(annotationattribs["Name"])
        self.visible = str(annotationattribs["Visible"])

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

    def as_geojson(self, matchnegative: bool = True) -> List[gs.Feature]:
        """
        A geojson representation of all regions in this layer
        """
        if self.contains_negative() & matchnegative:
            self.log.warning(
                "Layer contains negative regions! Please match before converting to geojson, or set matchnegative to False"
            )
            self.match_negative()
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

    def match_negative(self) -> None:
        neg_points = []
        pos_map = []  # type: list[int]  # index to original
        neg_map = []  # type: list[int]
        for idx, region in enumerate(self.regions):
            if region.isnegative:
                neg_points.append(region.getpointinregion())
                neg_map.append(idx)
            else:
                pos_map.append(idx)
        if neg_points:
            pos_polygons = [
                region.getvertices() for region in self.regions if not region.isnegative
            ]
            pos_idxs = points_in_polygons(
                neg_points, pos_polygons
            )  # locate the positive polygon that belongs to each negative polygon
            for neg_idx, pos_idx in enumerate(
                pos_idxs
            ):  # add the negative as hole to the apropriate positive
                if pos_idx == -1:
                    self.log.warning(
                        f"Did not find a matching positive region for region {neg_map[neg_idx]} in layer {self.name}"
                    )
                else:
                    self.regions[pos_map[pos_idx]].add_hole(
                        self.regions[neg_map[neg_idx]]
                    )
        # remove all negative regions
        self.regions = [x for x in self.regions if not x.isnegative]
