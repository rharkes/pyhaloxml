from .. import Region, Layer
from ..misc import RegionType

try:
    import shapely.geometry as sg
except ImportError as e:
    raise ImportError(
        "Shapely is not installed. Cannot use the shapely converters of haloxml."
    )


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
