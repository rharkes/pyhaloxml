"""
HaloXML Class to import the xml files that are outputted by Halo.
"""
import enum
import json
import logging
import os
from pathlib import Path
from lxml import etree
from lxml.etree import _Element, _Attrib, _ElementTree
from shapely import geometry as sg
from shapely import affinity as sa
import geojson as gs

from haloxml.ellipse import ellipse2polygon


class HaloXML:
    """
    Class around the halo .annotations files.
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
        :param pth:
        :return:
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
            if neg:
                # Take the first point of the negative ROIs
                points = [sg.Point(n.getpointinregion()) for n in neg]
                for r in pos:
                    polygon = sg.Polygon(r.getvertices())
                    for i, point in enumerate(points):
                        if polygon.contains(point):
                            r.add_hole(neg[i])
                    layer.addregion(r)
            else:
                for r in pos:
                    layer.addregion(r)

            self.layers.append(layer)
        self.valid = True

    def save(self, pth: os.PathLike | str) -> None:
        """
        Save the data as .annotation file.
        :param pth: path to save the annotations to
        :return:
        """
        new_root = etree.Element("Annotations")
        for layer in self.layers:
            anno = etree.Element("Annotation", layer.todict())
            for region in layer.regions:
                anno.append(region.region)
                for n in region.holes:
                    anno.append(n.region)
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
        features = []
        for layer in self.layers:
            props = {
                "object_type": "annotation",
                "classification": {
                    "name": layer.name,
                    "colorRGB": int(layer.linecolor),
                },
                "isLocked": False,
            }
            for region in layer.regions:
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


def _getvertices(element: _Element) -> list[tuple]:
    vertices = []
    for e in element.getchildren():
        if e.tag == "Vertices":
            for v in e.getchildren():
                vertices.append((float(v.attrib["X"]), float(v.attrib["Y"])))
    return vertices


def _closepolygon(vertices: list[tuple], warn: bool = True) -> list[tuple]:
    if vertices[0] != vertices[-1]:
        if warn:
            logging.warning(
                "HaloXML:Region 'Polygon does not close. Will close it now.'"
            )
        vertices.append(vertices[0])
    return vertices


class Layer:
    """
    Halo annotations are grouped in layers. They have a LineColor, Name and Visibility
    """

    def __init__(self) -> None:
        self.linecolor = ""  # type:str
        self.name = ""  # type:str
        self.visible = ""  # type:str
        self.regions = []  # type:[Region]

    def __str__(self):
        return self.tojson()

    def fromattrib(self, annotationattribs: _Attrib):
        self.linecolor = annotationattribs["LineColor"]
        self.name = annotationattribs["Name"]
        self.visible = annotationattribs["Visible"]

    def fromdict(self, dinfo: dict):
        self.linecolor = dinfo["LineColor"]
        self.name = dinfo["Name"]
        self.visible = dinfo["Visible"]

    def tojson(self) -> str:
        """
        JSON representation of the layer
        :return:
        """
        return json.dumps(self.todict(), sort_keys=True)

    def todict(self) -> dict:
        """
        Dictonary representation of the layer.
        :return:
        """
        return {"LineColor": self.linecolor, "Name": self.name, "Visible": self.visible}

    def addregion(self, region) -> None:
        self.regions.append(region)

    def as_shapely(self) -> sg.MultiPolygon:
        polygons = [x.as_shapely() for x in self.regions]
        return sg.MultiPolygon(polygons)


class Region:
    """
    Halo region.
    Can contian negative Regions with the same layer.
    Has a variable called region that contains the original element from the haloxml.
    """

    def __init__(self, region: _Element) -> None:
        self.region = region  # type: _Element
        self.holes = []  # type: [Region]
        self.type = RegionType.Polygon  # type: RegionType
        if region.attrib["Type"] == "Rectangle":
            self.type = RegionType.Rectangle
        if region.attrib["Type"] == "Ruler":
            self.type = RegionType.Ruler
        if region.attrib["Type"] == "Ellipse":
            self.type = RegionType.Ellipse
        self.hasendcaps = region.attrib["HasEndcaps"] == "1"  # type: bool
        self.log = logging.getLogger("HaloXML:Region")  # type: logging.Logger

    def __str__(self):
        return str(self.region.attrib)

    def add_hole(self, negative_region) -> None:
        """
        Halo regions can have holes
        :param negative_region: element of type Region
        """
        self.holes.append(negative_region)

    def getvertices(self) -> list[tuple]:
        """
        Get the vertices of the region
        :return: the vertices element
        """
        vertices = [(None, None)]
        if self.type == RegionType.Polygon:
            if self.hasendcaps:
                vertices = _getvertices(self.region)
            else:
                vertices = _closepolygon(_getvertices(self.region), warn=True)
        if self.type == RegionType.Rectangle:
            pts = _getvertices(self.region)  # corners of the rectangle
            vertices = [
                pts[0],
                (pts[0][0], pts[1][1]),
                pts[1],
                (pts[1][0], pts[0][1]),
                pts[0],
            ]
        if self.type == RegionType.Ruler:
            vertices = _getvertices(self.region)
        if self.type == RegionType.Ellipse:
            pts = _getvertices(self.region)
            center = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
            a = (pts[0][0] - pts[1][0]) / 2
            b = (pts[0][1] - pts[1][1]) / 2
            e = ellipse2polygon(a, b)
            vertices = [(x + center[0], y + center[1]) for (x, y) in e]
        return vertices

    def getpointinregion(self) -> tuple:
        """
        Returns a point in the region or on the edge of the region
        :return:
        """
        pointinregion = (None, None)
        if self.type in [RegionType.Polygon, RegionType.Rectangle]:
            pointinregion = self.getvertices()[0]
        if self.type == RegionType.Ellipse:
            pts = _getvertices(
                self.region
            )  # corners of the rectangle, return the centerpoint
            pointinregion = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
        return pointinregion

    def as_geojson(self) -> gs.Polygon:
        """
        Return the region as geojson.Polygon
        :return:
        """
        vertices = [self.getvertices()]
        if self.type == RegionType.Ruler:
            polygon = gs.LineString(vertices)
        else:
            for v in self.holes:
                vertices.append(v.getvertices())
            polygon = gs.Polygon(vertices)
            if not polygon.is_valid:
                self.log.warning("HaloXML:Region 'Polygon is not valid!'")
        return polygon

    def as_shapely(self) -> sg.Polygon:
        """
        Return the region as a shapeply polygon
        :return:
        """
        if self.type == RegionType.Ruler:
            polygon = sg.LineString(self.getvertices())
        else:
            polygon = sg.Polygon(
                self.getvertices(), [x.getvertices() for x in self.holes]
            )
        return polygon


class RegionType(enum.IntEnum):
    """
    Region, can be of type:
    * Rectangle  (x1, y1, x2, y2)  corners
    * Ellipse  (x1, y1, x2, y2) corners of enclosing rectangle
    * Ruler (x1, y1, x2, y2)  start->end
    * Polygon (vertex elements)
    """

    Rectangle = 0
    Ellipse = 1
    Ruler = 2
    Polygon = 3


def shapelyellipse(
    a: float, b: float, r: float = 0.0, c: (float, float) = (0.0, 0.0)
) -> sg.Polygon:
    """
    Generate a rotated ellipse with major axis a and minor axis b and centered around c
    from ; https://gis.stackexchange.com/questions/243459/drawing-ellipse-with-shapely
    :param c: center
    :param a: major axis
    :param b: minor axis
    :param r: angle
    :return:
    """
    circ = sg.Point(c).buffer(1.0)  # circle
    ell = sa.scale(circ, a, b)
    return sa.rotate(ell, r)
