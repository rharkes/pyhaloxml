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
from lxml.etree import _ElementTree, _Element
import geojson as gs

from .Layer import Layer
from .Region import Region


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
        self.tree = etree.Element("root")  # type:_ElementTree | Any
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
        for (
            annotation
        ) in self.tree.getroot().iterchildren():  # go over each layer in the file
            layer = Layer()
            layer.fromattrib(annotation.attrib)
            regionslist = [x for x in annotation.iterchildren()]
            regions = regionslist[0]
            for region in regions:  # sort regions for positive ore negative
                layer.addregion(Region(region))
            self.layers.append(layer)
        self.valid = True

    def matchnegative(self) -> None:
        for layer in self.layers:
            layer.match_negative()

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
