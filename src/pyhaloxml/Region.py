"""
Region.py
"""
import logging
import math
from numbers import Real
from lxml.etree import _Element, Element
import geojson as gs
from pyhaloxml.ellipse import ellipse2polygon
from pyhaloxml.misc import RegionType, getvertices, closepolygon, getvertex


class Region:
    """
    Halo region.
    Can contian negative Regions with the same layer.
    Has a variable called region that contains the original element from the pyhaloxml.
    """

    def __init__(self, region: _Element) -> None:
        self.region = region  # type: _Element
        self.holes = []  # type: list[Region]
        self.vertices = [(math.nan, math.nan)]  # type: list[tuple[float, float]]
        self.type = RegionType.Unknown  # type: RegionType
        if region.attrib["Type"] == "Polygon":
            self.type = RegionType.Polygon
        elif region.attrib["Type"] == "Rectangle":
            self.type = RegionType.Rectangle
        elif region.attrib["Type"] == "Ruler":
            self.type = RegionType.Ruler
        elif region.attrib["Type"] == "Ellipse":
            self.type = RegionType.Ellipse
        elif region.attrib["Type"] == "Pin":
            self.type = RegionType.Pin

        self.hasendcaps = region.attrib["HasEndcaps"] == "1"  # type: bool
        self.log = logging.getLogger("HaloXML:Region")  # type: logging.Logger

    def __str__(self) -> str:
        return str(self.region.attrib)

    def has_area(self) -> bool:
        if self.type in [RegionType.Rectangle, RegionType.Ellipse]:
            return True
        if self.type == RegionType.Polygon:
            vertices = self.getvertices()
            if vertices[-1] != vertices[0]:
                return False  # it is a linestring, not a polygon
            else:
                return True
        return False

    def add_hole(self, negative_region: "Region") -> None:
        """
        Halo regions can have holes
        :param negative_region: element of type Region
        """
        if self.has_area():
            self.holes.append(negative_region)
        else:
            self.log.error("Cannot add a hole to a region without an area.")

    def getvertices(self) -> list[tuple[float, float]]:
        """
        Get the vertices of the region
        :return: the vertices element
        """
        if len(self.vertices) == 1:
            if self.vertices[0] == (math.nan, math.nan):
                self._getvertices()
        return self.vertices

    def _getvertices(self) -> None:
        """
        Get the vertices of the region and store in class
        """
        vertices = [(math.nan, math.nan)]
        if self.type == RegionType.Polygon:
            vertices = getvertices(self.region)
            if vertices[0] != vertices[1]:
                self.isclosed = False
        if self.type == RegionType.Rectangle:
            pts = getvertices(self.region)  # corners of the rectangle
            vertices = [
                pts[0],
                (pts[0][0], pts[1][1]),
                pts[1],
                (pts[1][0], pts[0][1]),
                pts[0],
            ]
        if self.type in [RegionType.Ruler, RegionType.Pin]:
            vertices = getvertices(self.region)
        if self.type == RegionType.Ellipse:
            pts = getvertices(self.region)
            center = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
            a = (pts[0][0] - pts[1][0]) / 2
            b = (pts[0][1] - pts[1][1]) / 2
            e = ellipse2polygon(a, b)
            vertices = [(x + center[0], y + center[1]) for (x, y) in e]
            vertices.append(vertices[0])  # close the polygon
        self.vertices = vertices

    def getpointinregion(self) -> tuple[float, float]:
        """
        Returns a point in the region or on the edge of the region or on the line of a linestring or the point.
        Do check if the region `.has_area()` if you need to.
        :return:
        """
        if self.type == RegionType.Ellipse:
            pts = getvertices(
                self.region
            )  # corners of the rectangle, return the centerpoint
            pointinregion = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
        else:
            pointinregion = getvertex(self.region)
        return pointinregion

    def as_geojson(self) -> gs.Polygon | gs.LineString | gs.Point:
        """
        Return the region as geojson.Polygon
        :return:
        """
        vertices = self.getvertices()
        if self.type == RegionType.Pin:
            geoj = gs.Point(vertices[0])
        elif self.has_area():
            polygon = [vertices]
            for v in self.holes:
                polygon.append(v.getvertices())
            geoj = gs.Polygon(polygon)
            if not geoj.is_valid:
                self.log.warning("Polygon is not valid!")
        elif self.type in [RegionType.Ruler, RegionType.Polygon]:
            geoj = gs.LineString(vertices)
        else:
            self.log.error(f"Cannot convert type {self.type} to polygon.")
        return geoj


def region_from_coordinates(coords: list[list[tuple[Real, Real]]]) -> Region:
    """
    Creates a HaloXML Region from coordinates. It must be a list of lists of coordinates.
    The first list is the outer polygon, the next lists are the polygonal holes and must be contained in the first polygon.
    :param coords:
    :return:
    """
    region = Element(
        "Region", {"Type": "Polygon", "HasEndcaps": "0", "NegativeROA": "0"}
    )
    vertices = Element("Vertices")
    for v in coords[0]:
        vertices.append(Element("V", {"X": str(int(v[0])), "Y": str(int(v[1]))}))
    region.append(vertices)
    reg = Region(region)
    for i in range(1, len(coords)):
        region = Element(
            "Region", {"Type": "Polygon", "HasEndcaps": "0", "NegativeROA": "1"}
        )
        vertices = Element("Vertices")
        for v in coords[i]:
            vertices.append(Element("V", {"X": str(int(v[0])), "Y": str(int(v[1]))}))
        region.append(vertices)
        reg.add_hole(Region(region))
    return reg
