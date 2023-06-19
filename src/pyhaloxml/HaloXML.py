"""
HaloXML Class to import the xml files that are outputted by Halo.
"""
import io
import logging
import os
from contextlib import AbstractContextManager
from pathlib import Path
from types import TracebackType
from typing import Union, Any, BinaryIO, Type, Optional
from uuid import uuid4

from lxml import etree
from lxml.etree import _ElementTree
import geojson as gs

from .Layer import Layer
from .Region import Region
from .misc import RegionType, points_in_polygons


class HaloXMLFile(AbstractContextManager[Any]):
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
    The main class around the halo .annotations files.
    """

    def __init__(self) -> None:
        self.tree = etree.Element("root")  # type:_ElementTree
        self.layers = []  # type: list[Layer]
        self.valid = False  # type: bool
        self.log = logging.getLogger("HaloXML")

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
            neg = []  # type: list[Region]
            pos = []  # type: list[Region]
            for region in regions:  # sort regions for positive ore negative
                if region.attrib["NegativeROA"] == "1":
                    neg.append(Region(region))
                else:
                    pos.append(Region(region))
            # It is not clear what 'parent' a negative ROIs belongs to. Have to find it out ourselves...
            logging.info(
                f"Found {len(pos)} positive regions and {len(neg)} negative regions."
            )
            if neg:
                neg_points = [n.getpointinregion() for n in neg]
                pos_polygons = [p.getvertices() for p in pos]
                pos_idxs = points_in_polygons(
                    neg_points, pos_polygons
                )  # locate the positive polygon that belongs to each negative polygon
                for neg_idx, pos_idx in enumerate(
                    pos_idxs
                ):  # add the negative as hole to the apropriate positive
                    pos[pos_idx].add_hole(neg[neg_idx])
                for p in pos:
                    layer.addregion(p)
            else:
                for r in pos:
                    layer.addregion(r)

            self.layers.append(layer)
        self.valid = True

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
        features = []
        for layer in self.layers:
            props = {
                "objectType": "annotation",
                "name": layer.name,
                "classification": {
                    "name": layer.name,
                    "color": layer.linecolor.getrgb(),
                },
                "isLocked": False,
            }
            if len(layer.regions) == 1:
                geometry = layer.regions[0].as_geojson()
                features.append(
                    gs.Feature(geometry=geometry, properties=props, id=str(uuid4()))
                )
            else:  # try to put them in a MultiPolygon
                if any([x.type == RegionType.Ruler for x in layer.regions]):
                    for region in layer.regions:
                        features.append(
                            gs.Feature(
                                geometry=region.as_geojson(),
                                properties=props,
                                id=str(uuid4()),
                            )
                        )
                else:
                    geometry = gs.MultiPolygon(
                        [x.as_geojson()["coordinates"] for x in layer.regions]
                    )
                    features.append(
                        gs.Feature(geometry=geometry, properties=props, id=str(uuid4()))
                    )

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
