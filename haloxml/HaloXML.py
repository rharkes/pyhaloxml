import copy
import json
import logging
import os
from pathlib import Path
import geojson as gs
from lxml import etree
from lxml.etree import _Element, _Attrib, _ElementTree
from shapely import geometry


class HaloXML:
    """
    Class around the halo .annotations files.
    """

    def __init__(self) -> None:
        self.pth = Path()  # type: Path
        self.tree = etree.Element("root")  # type:_ElementTree
        self.regions = []  # type:[Region]
        self.valid = False  # type:bool
        self.log = logging.getLogger("HaloXML")

    def __bool__(self) -> bool:
        return self.valid

    def load(self, pth: os.PathLike | str) -> None:
        """
        Load .annotations file
        :param pth:
        :return:
        """
        self.pth = Path(pth)
        self.tree = etree.parse(pth)
        annotations = self.tree.getroot().getchildren()
        for annotation in annotations:
            regions = annotation.getchildren()[0]
            neg = []  # type: [_Element]
            pos = []  # type: [_Element]
            for region in regions:
                if region.attrib["NegativeROA"] == "1":
                    neg.append(region)
                else:
                    pos.append(region)
            # It is not clear what 'parent' a negative ROIs belongs to. Have to find it out ourselves...
            if neg:
                # Take the first point of the negative ROIs
                points = [geometry.Point(_getvertices(n, False)[0]) for n in neg]
                for r in pos:
                    self.regions.append(Region(r, annotation.attrib))
                    polygon = geometry.Polygon(_getvertices(r, False))
                    for i, point in enumerate(points):
                        if polygon.contains(point):
                            self.regions[-1].add_hole(neg[i])
            else:
                for r in pos:
                    self.regions.append(Region(r, annotation.attrib))
        self.valid = True

    def getannotationattributes(self) -> list:
        """
        Get all unique annotation attributes
        :return: dictionary with unique annotation attributes
        """
        unique_attrs = set([json.dumps(d.annatr, sort_keys=True) for d in self.regions])
        return [json.loads(x) for x in unique_attrs]

    def groupregions(self) -> dict:
        """
        group regions based on annotation attributes
        :return: a dictionary where the key is the unique attributes
        """
        grouped_regions = {}
        for r in self.regions:
            attr = json.dumps(r.annatr, sort_keys=True)
            if attr in grouped_regions.keys():
                grouped_regions[attr].append(r)
            else:
                grouped_regions[attr] = [r]
        return grouped_regions

    def save(self, pth: os.PathLike | str) -> None:
        """
        Group regions based on annotation attributes
        :param pth: path to save the annotations to
        :return:
        """
        annotations = self.groupregions()
        new_root = etree.Element("Annotations")
        for annotation in annotations:
            anno = etree.Element("Annotation", json.loads(annotation))
            for region in annotations[annotation]:
                anno.append(region.region)
                for n in region.holes:
                    anno.append(n)
            new_root.append(anno)
        pth = Path(pth)
        if not pth.suffix:
            pth = Path(pth.parent, pth.name + ".annotations")
        with open(pth, "wb") as f:
            f.write(etree.tostring(new_root))

    def as_geojson(self) -> gs.FeatureCollection:
        """
        Returns the annotations as geojson.FeatureCollection
        :return:
        """
        annotations = self.groupregions()
        features = []
        for annotation in annotations:
            ann_info = json.loads(annotation)
            props = {
                "object_type": "annotation",
                "classification": {"name": ann_info["Name"], "colorRGB": -65536},
                "isLocked": False,
            }
            for region in annotations[annotation]:
                features.append(
                    gs.Feature(geometry=region.as_geojson(), properties=props)
                )
        return gs.FeatureCollection(features)

    def to_geojson(self, pth: os.PathLike | str) -> None:
        """
        Save regions as geojson
        :param pth:
        :return:
        """
        pth = Path(pth)
        if not pth.suffix:
            pth = Path(pth.parent, pth.name + ".geojson")
        with open(pth, "wt") as f:
            f.write(gs.dumps(self.as_geojson(), sort_keys=True))


def _getvertices(element: _Element, warn: bool = True) -> list[tuple]:
    vertices = []
    for e in element.getchildren():
        if e.tag == "Vertices":
            for v in e.getchildren():
                vertices.append((float(v.attrib["X"]), float(v.attrib["Y"])))
    if vertices[0] != vertices[-1]:
        if warn:
            logging.warning(
                "HaloXML:Region 'Polygon does not close. Will close it now.'"
            )
        vertices.append(vertices[0])
    return vertices


class Region:
    """
    Halo region
    """

    def __init__(self, region: _Element, annotationattribs: _Attrib) -> None:
        self.region = region  # type: _Element
        self.holes = []  # type: [_Element]
        self.annatr = copy.deepcopy(annotationattribs)  # type: _Attrib
        self.log = logging.getLogger("HaloXML:Region")

    def add_hole(self, n_element: _Element) -> None:
        """
        Halo regions can have holes
        :param n_element:
        """
        self.holes.append(n_element)

    def getvertices(self) -> list[tuple]:
        """
        Get the vertices of the region
        :return: the vertices element
        """
        return _getvertices(self.region)

    def as_geojson(self) -> gs.Polygon:
        """
        Return the region as geojson.Polygon
        :return:
        """
        vertices = [self.getvertices()]
        for v in self.holes:
            vertices.append(_getvertices(v))
        polygon = gs.Polygon(vertices)
        if not polygon.is_valid:
            self.log.warning("HaloXML:Region 'Polygon is not valid!'")
        return polygon
