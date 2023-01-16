"""
HaloXML Class to import the xml files that are outputted by Halo.
"""
import logging
import os
from pathlib import Path
import numpy as np
from lxml import etree
from lxml.etree import _ElementTree
import geojson as gs

from .Layer import Layer
from .Region import Region
from .inpoly import parallelpointinpolygon
from .misc import RegionType


class HaloXML:
    """
    The main class around the halo .annotations files.
    """

    def __init__(self) -> None:
        self.tree = etree.Element("root")  # type:_ElementTree
        self.layers = []  # type:[Layer]
        self.valid = False  # type:bool
        self.log = logging.getLogger("HaloXML")

    def __bool__(self) -> bool:
        return self.valid

    def load(self, pth: os.PathLike | str) -> None:
        """
        Load .annotations file

        :param pth: path to the .annotations file
        """
        pth = Path(pth)
        if not pth.exists() or not pth.is_file():
            raise FileNotFoundError(pth)
        self.tree = etree.parse(pth)
        annotations = self.tree.getroot().getchildren()
        for annotation in annotations:  # go over each layer in the file
            layer = Layer()
            layer.fromattrib(annotation.attrib)
            regions = annotation.getchildren()[0]
            neg = []  # type: [Region]
            pos = []  # type: [Region]
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
                nppoints = np.array([n.getpointinregion() for n in neg])
                for pos_region in pos:
                    nppolygon = np.array(pos_region.getvertices())
                    point_in_poly = np.flatnonzero(
                        parallelpointinpolygon(nppoints, nppolygon)
                    )
                    for i in range(point_in_poly.size):
                        pos_region.add_hole(neg[point_in_poly[i]])
                    layer.addregion(pos_region)
            else:
                for r in pos:
                    layer.addregion(r)

            self.layers.append(layer)
        self.valid = True
        logging.info(f"Finished loading {pth.stem}")

    def save(self, pth: os.PathLike | str) -> None:
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
        return etree.tostring(new_root)

    def as_geojson(self) -> gs.FeatureCollection:
        """
        Returns the annotations as geojson.FeatureCollection

        :return: A geojson featurecollection with all the annotations.
        """
        features = []
        for layer in self.layers:
            props = {
                "object_type": "annotation",
                "classification": {
                    "name": layer.name,
                    "colorRGB": layer.linecolor.getrgb(),
                },
                "isLocked": False,
            }
            if len(layer.regions) == 1:
                geometry = layer.regions[0].as_geojson()
                features.append(
                    gs.Feature(geometry=geometry, properties=props)
                )
            else:  # try to put them in a MultiPolygon
                if any([x.type == RegionType.Ruler for x in layer.regions]):
                    for region in layer.regions:
                        features.append(
                            gs.Feature(geometry=region.as_geojson(), properties=props)
                        )
                else:
                    geometry = gs.MultiPolygon([x.as_geojson()["coordinates"] for x in layer.regions])
                    features.append(
                        gs.Feature(geometry=geometry, properties=props)
                    )

        return gs.FeatureCollection(features)

    def to_geojson(self, pth: os.PathLike | str) -> None:
        """
        Save regions as geojson. This file can be loaded in QuPath.

        :param pth: Location to save the .geojson to.
        """
        pth = Path(pth)
        if not pth.suffix:
            pth = Path(pth.parent, pth.name + ".geojson")
        with open(pth, "wt") as f:
            f.write(gs.dumps(self.as_geojson(), sort_keys=True))
