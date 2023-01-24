"""
Gateway to cython function
"""
from array import array
from pyhaloxml.cython.c_inpoly import c_pointinpoly

def point_in_poly(point: (float, float), polygon: list[(float, float)]) -> bool:
    apoint = array("f", point)
    apolygon = array("f", [xy for coord in polygon for xy in coord])
    return c_pointinpoly(apoint, apolygon)
