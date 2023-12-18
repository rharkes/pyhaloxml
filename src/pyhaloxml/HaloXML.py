"""
HaloXML Class to import the xml files that are outputted by Halo.
"""
import io
import logging
import os
from contextlib import AbstractContextManager
from pathlib import Path
from types import TracebackType
from typing import Union, Any, BinaryIO, Type, Optional, List

from lxml import etree
from lxml.etree import _ElementTree
import geojson as gs

from .Layer import Layer
from .Region import Region
from .misc import RegionType, points_in_polygons


class HaloXMLFile(AbstractContextManager[Any]):
    """
    Context manager for handeling .annotation files
    """

    def __init__(self, pth: Union[str, os.PathLike[Any]], mode: str = "r") -> None:
        if mode not in ["r", "w"]:
            raise KeyError(f"Invalid mode: {mode}")
        pth = Path(pth)
        if mode == "r" and (not pth.exists() or not pth.is_file()):
            raise FileNotFoundError(pth)
        self.pth = pth
        self.mode = mode

    def __enter__(self) -> "HaloXML":
        self.hx = HaloXML()
        if self.mode == "r":
            self.file = io.FileIO(self.pth, "r")
            self.hx.loadstream(self.file)
        return self.hx

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.mode == "w":
            self.hx.save(self.pth)
        else:
            self.file.close()


class HaloXML:
    """
    The class to hold annotation data.
    """

    def __init__(self) -> None:
        self.tree = etree.Element("root")  # type:_ElementTree
        self.layers = []  # type: list[Layer]
        self.valid = False  # type: bool
        self.log = logging.getLogger(__name__)

    def __bool__(self) -> bool:
        return self.valid

    def loadstream(self, fp: BinaryIO) -> None:
        """

        :param fp:
        :return:
        """
        self.tree = etree.parse(fp)
        annotations = self.tree.getroot().getchildren()
        for annotation in annotations:  # go over each layer in the file
            layer = Layer()
            layer.fromattrib(annotation.attrib)
            regions = annotation.getchildren()[0]
            for region in regions:  # sort regions for positive ore negative
                layer.addregion(Region(region))
        self.valid = True

    def matchnegative(self) -> None:
        for layeridx, layer in enumerate(self.layers):
            neg_points = []
            pos_map = []  # type: list[int]  # index to original
            neg_map = []  # type: list[int]
            for idx, region in enumerate(layer.regions):
                if region.isnegative:
                    neg_points.append(region.getpointinregion())
                    neg_map.append(idx)
                else:
                    pos_map.append(idx)
            if neg_points:
                pos_polygons = [
                    region.getvertices()
                    for region in layer.regions
                    if not region.isnegative
                ]
                pos_idxs = points_in_polygons(
                    neg_points, pos_polygons
                )  # locate the positive polygon that belongs to each negative polygon
                for neg_idx, pos_idx in enumerate(
                    pos_idxs
                ):  # add the negative as hole to the apropriate positive
                    if pos_idx == -1:
                        self.log.warning(
                            f"Did not find a matching positive region for region {neg_map[neg_idx]} in layer {layeridx}"
                        )
                    else:
                        layer.regions[pos_map[pos_idx]].add_hole(
                            layer.regions[neg_map[neg_idx]]
                        )
            # remove all negative regions
            layer.regions = [x for x in layer.regions if not x.isnegative]

    def load(self, pth: Union[str, os.PathLike[Any]]) -> None:
        """
        Load .annotations file

        :param pth: path to the .annotations file
        """
        pth = Path(pth)
        if not pth.exists() or not pth.is_file():
            raise FileNotFoundError(pth)
        with open(pth, "rb") as fp:
            self.loadstream(fp)
        logging.info(f"Finished loading {pth.stem}")

    def save(self, pth: Union[str, os.PathLike[Any]]) -> None:
        """
        Save the data as .annotation file.

        :param pth: Location to save the annotations to
        """
        pth = Path(pth)
        if not pth.suffix:
            pth = Path(pth.parent, pth.name + ".annotations")
        with open(pth, "wb") as f:
            f.write(self.as_raw())

    def as_raw(self) -> bytes:
        """
        Return the bytes that can be written to a .annotations files.

        :return: bytes represention of the data in this HaloXML.
        """
        new_root = etree.Element("Annotations")
        for layer in self.layers:
            anno = etree.Element("Annotation", layer.todict())
            regions = etree.Element("Regions")
            for region in layer.regions:
                regions.append(region.region)
                for n in region.holes:
                    regions.append(n.region)
            anno.append(regions)
            new_root.append(anno)
        return bytes(etree.tostring(new_root))

    def as_geojson(self) -> gs.FeatureCollection:
        """
        Returns the annotations as geojson.FeatureCollection

        :return: A geojson featurecollection with all the annotations.
        """
        features = []  # type: List[gs.Feature]
        for layer in self.layers:
            fts = layer.as_geojson()
            for ft in fts:
                features.append(ft)

        return gs.FeatureCollection(features)

    def to_geojson(self, pth: Union[str, os.PathLike[Any]]) -> None:
        """
        Save regions as geojson. This file can be loaded in QuPath.

        :param pth: Location to save the .geojson to.
        """
        pth = Path(pth)
        if not pth.suffix:
            pth = Path(pth.parent, pth.name + ".geojson")
        with open(pth, "wt") as f:
            f.write(gs.dumps(self.as_geojson(), sort_keys=True))
