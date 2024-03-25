from ..Layer import Layer
from ..Region import Region
from ..misc import RegionType

try:
    import shapely.geometry as sg
except ImportError as e:
    raise ImportError(
        "Shapely is not installed. Cannot use the shapely converters of haloxml."
    )


def region_to_shapely(
    region: Region,
) -> sg.Polygon | sg.Point | sg.LineString:
    """
    Return the region as a shapeply polygon
    :return:
    """

    if region.type == RegionType.Ruler:
        geometry = sg.LineString(region.getvertices())
    elif region.type == RegionType.Pin:
        geometry = sg.Point(region.getvertices())
    else:
        geometry = sg.Polygon(
            region.getvertices(), [x.getvertices() for x in region.holes]
        )
        if not geometry.is_valid:
            geometry = sg.LineString(region.getvertices())
    return geometry


def layer_to_shapely(layer: Layer, fix_negative: bool = True) -> sg.MultiPolygon:
    """
    Return the layer as shaply multipolygon
    :return: A shapely multipolygon contain all the regions in this layer.
    """
    if layer.contains_negative() and fix_negative:
        layer.match_negative()
    geometries = []
    for x in layer.regions:
        geom = region_to_shapely(x)
        geometries.append(geom)
    return sg.GeometryCollection(geometries)
