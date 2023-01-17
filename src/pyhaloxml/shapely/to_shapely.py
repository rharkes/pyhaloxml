from pyhaloxml import Region, Layer
from pyhaloxml.misc import RegionType
import shapely.geometry as sg


def region_to_shapely(region: Region) -> sg.Polygon:
    """
    Return the region as a shapeply polygon
    :return:
    """
    if region.type == RegionType.Ruler:
        polygon = sg.LineString(region.getvertices())
    else:
        polygon = sg.Polygon(
            region.getvertices(), [x.getvertices() for x in region.holes]
        )
    return polygon


def layer_to_shapely(layer: Layer) -> sg.MultiPolygon:
    """
    Return the layer as shaply multipolygon

    :return: A shapely multipolygon contain all the regions in this layer.
    """
    polygons = [region_to_shapely(x) for x in layer.regions]
    return sg.MultiPolygon(polygons)
