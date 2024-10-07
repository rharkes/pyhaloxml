"""Layer.py."""

import json
import logging
from typing import List
from uuid import uuid4

import geojson as gs
from lxml.etree import _Attrib

from .misc import Color, points_in_polygons
from .Region import Region


class Layer:
    """
    Halo annotations are grouped in layers.

    These layers are the first buildingblock of a halo annotation.
    They have properties like color and name and contain the regions.

    Attributes
    ----------
    linecolor : Color
        Color of the lines in this layer
    name : str
        Name of the layer
    visible : bool
        If the layer is visible
    regions: list[Region]
        a list of Regions
    log : logger
    """

    def __init__(self) -> None:  # numpydoc ignore=GL08
        self.linecolor = Color()  # type:Color
        self.name = ""  # type:str
        self.visible = "True"  # type:str
        self.regions = []  # type:list[Region]
        self.log = logging.getLogger("HaloXML-Layer")

    def __str__(self) -> str:  # numpydoc ignore=GL08
        return self.tojson()

    def contains_negative(self) -> bool:
        """
        Are there any negative regions in the layer.

        Returns
        -------
        bool
            Returns true if the layer contains any negative regions that are not matched to positive regions.

        See Also
        --------
        match_negative : Match the negative regions with a positive region.
        """
        return any([x.isnegative for x in self.regions])

    def fromattrib(self, annotationattribs: _Attrib) -> None:
        """
        Populate the layer with information from an lxml attribute.

        Parameters
        ----------
        annotationattribs : _Attrib
            Lxml attribute with information about the layer.
        """
        self.linecolor.setlinecolor(str(annotationattribs["LineColor"]))
        self.name = str(annotationattribs["Name"])
        self.visible = str(annotationattribs["Visible"])

    def fromdict(self, dinfo: dict[str, str]) -> None:
        """
        Populate the layer with information from a dictionary.

        Parameters
        ----------
        dinfo : dict[str, str]
            Dictionary with LineColor, Name and Visibility.
        """
        self.linecolor.setlinecolor(dinfo["LineColor"])
        self.name = dinfo["Name"]
        self.visible = dinfo["Visible"]

    def tojson(self) -> str:
        """
        JSON representation of the layer.

        Returns
        -------
        str
            A jsonstring representation of this layer.
        """
        return json.dumps(self.todict(), sort_keys=True)

    def todict(self) -> dict[str, str]:
        """
        Create a dictonary with the layer information.

        Returns
        -------
        dict[str, str]
            A dictonary with the layer information.
        """
        return {
            "LineColor": self.linecolor.getlinecolor(),
            "Name": self.name,
            "Visible": self.visible,
        }

    def as_geojson(self, matchnegative: bool = True) -> List[gs.Feature]:
        """
        A geojson representation of all regions in this layer.

        Parameters
        ----------
        matchnegative : bool
            True (default) - First matches negative regions before converting to GeoJSON.
            False - Will not match negative regions, but will raise a warning if negative regions are found.

        Returns
        -------
        List[gs.Feature]
            A list with geojson Feature objects for each Region.
        """
        if self.contains_negative() & matchnegative:
            self.match_negative()
        if self.contains_negative():
            self.log.warning(
                "Layer contains negative regions! Please match before converting to geojson, or set matchnegative to True."
            )
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
        Add a region to this layer.

        Parameters
        ----------
        region : Region
            Region to be added.
        """
        self.regions.append(region)

    def match_negative(self) -> None:
        """
        Match the negative regions in this layer to the positive region.

        If a region is not matched the there is a warning via the
        logging framework  and the negative region is removed.

        See Also
        --------
        contains_negative : Check if the layer contains negative regions.
        """
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
