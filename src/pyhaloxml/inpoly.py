from array import array
from pyhaloxml.cython.c_inpoly import pointinpoly


def points_in_polygons(
    points: list[(float, float)], polygons: list[list[(float, float)]]
) -> list[int]:
    result = [-1] * len(points)
    for i, point in enumerate(points):
        apoint = array("f", point)
        for j, polygon in enumerate(polygons):
            apolygon = array("f", [xy for coord in polygon for xy in coord])
            if pointinpoly(apoint, apolygon):
                result[i] = j
                continue
    return result
