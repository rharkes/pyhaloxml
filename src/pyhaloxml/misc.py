"""
File with some basic classes and functions
"""
import enum
import logging

import shapely.geometry as sg
import shapely.affinity as sa
from lxml.etree import _Element


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


def getvertices(element: _Element) -> list[tuple]:
    vertices = []
    for e in element.getchildren():
        if e.tag == "Vertices":
            for v in e.getchildren():
                vertices.append((float(v.attrib["X"]), float(v.attrib["Y"])))
    return vertices


def getvertex(element: _Element) -> tuple:
    for e in element.getchildren():
        if e.tag == "Vertices":
            for v in e.getchildren():
                return float(v.attrib["X"]), float(v.attrib["Y"])


def closepolygon(vertices: list[tuple], warn: bool = True) -> list[tuple]:
    if vertices[0] != vertices[-1]:
        if warn:
            logging.warning(
                "HaloXML:Region 'Polygon does not close. Will close it now.'"
            )
        vertices.append(vertices[0])
    return vertices


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
