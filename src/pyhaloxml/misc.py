"""
File with some basic classes and functions
"""

import enum
import logging
import math
from datetime import datetime
import dateutil.parser
from lxml.etree import _Element, Element
from pyhaloxml.pyhaloxml_rs import point_in_polygon


def points_in_polygons(
    points: list[tuple[float, float]], polygons: list[list[tuple[float, float]]]
) -> list[int]:
    result = [-1] * len(points)
    for i, point in enumerate(points):
        for j, polygon in enumerate(polygons):
            if point_in_polygon(point, polygon):
                result[i] = j
                continue
    return result


class Comment:
    def __init__(self, author: str = "<no user>", body: str = "") -> None:
        self._author = author
        self._body = body
        self._createdtime = datetime.now()
        self._modifiedtime = datetime.now()

    def __str__(self) -> str:
        return self._body

    def setcomment(self, e: _Element) -> None:
        self._author = str(e.attrib["Author"])
        self._body = str(e.attrib["Body"])
        self._createdtime = dateutil.parser.isoparse(e.attrib["CreatedTime"])
        self._modifiedtime = dateutil.parser.isoparse(e.attrib["ModifiedTime"])

    def setbody(self, body: str) -> None:
        self._body = body
        self._modifiedtime = datetime.now()

    def getcomment(self) -> _Element:
        comment = Element(
            "Comment",
            {
                "Author": self._author,
                "Body": self._body,
                "CreatedTime": self.getcreated(),
                "ModifiedTime": self.getmodified(),
            },
        )
        return comment

    def getmodified(self) -> str:
        return self._modifiedtime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def getcreated(self) -> str:
        return self._createdtime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class Color:
    """
    Class for keeping color rgb information
    """

    def __init__(self) -> None:
        self.rgb = (0).to_bytes(length=3, byteorder="little")  # type:bytes
        self.log = logging.getLogger("HaloXML-Color")

    def __str__(self) -> str:
        return hex(int.from_bytes(self.rgb, byteorder="little"))

    def getrgb(self) -> tuple[int, int, int]:
        return int(self.rgb[0]), int(self.rgb[1]), int(self.rgb[2])

    def setrgb(self, r: int, g: int, b: int) -> None:
        if all([x <= 255 for x in [r, g, b]]):
            self.rgb = (r + g * 2**8 + b * 2**16).to_bytes(length=3, byteorder="little")
            return
        self.log.error("Color should be <255 for each color")

    def getlinecolor(self) -> str:
        return str(int.from_bytes(self.rgb, byteorder="little"))

    def setlinecolor(self, color: str) -> None:
        self.rgb = int(color).to_bytes(length=3, byteorder="little")


class RegionType(enum.IntEnum):
    """
    Region, can be of type:
    * Rectangle  (x1, y1, x2, y2)  corners
    * Ellipse  (x1, y1, x2, y2) corners of enclosing rectangle
    * Ruler (x1, y1, x2, y2)  start->end
    * Polygon (vertex elements)
    * Pin  (x1, y1)
    """

    Unknown = -1
    Rectangle = 0
    Ellipse = 1
    Ruler = 2
    Polygon = 3
    Pin = 4

    def __str__(self) -> str:
        return self.name


def getvertices(element: _Element) -> list[tuple[float, float]]:
    vertices = []
    for e in element.iterchildren():
        if e.tag == "Vertices":
            for v in e.iterchildren():
                vertices.append((float(v.attrib["X"]), float(v.attrib["Y"])))
    return vertices


def getvertex(element: _Element) -> tuple[float, float]:
    for e in element.iterchildren():
        if e.tag == "Vertices":
            for v in e.iterchildren():
                return float(v.attrib["X"]), float(v.attrib["Y"])
    return math.nan, math.nan


def closepolygon(
    vertices: list[tuple[float, float]], warn: bool = True
) -> list[tuple[float, float]]:
    if vertices[0] != vertices[-1]:
        if warn:
            logging.warning(
                "HaloXML:Region 'Polygon does not close. Will close it now.'"
            )
        vertices.append(vertices[0])
    return vertices
