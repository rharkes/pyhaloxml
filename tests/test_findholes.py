import pytest as pytest
from pathlib import Path
from pyhaloxml import HaloXML, RegionType


@pytest.fixture
def file():
    return Path(Path.cwd(), "tests", "testdata", "test_findholes.annotations")


@pytest.fixture
def jsonfile():
    return Path(Path.cwd(), "tests", "testdata", "test_findholes.json")


def test_findholes(file):
    hx = HaloXML()
    hx.load(file)
    assert len(hx.layers[0].regions) == 10
    hx.matchnegative()
    assert len(hx.layers[0].regions) == 4
    for region in hx.layers[0].regions:
        if region.type == RegionType.Rectangle:
            assert region.holes[0].type == RegionType.Rectangle
        if region.type == RegionType.Ellipse:
            assert region.holes[0].type == RegionType.Ellipse
        if region.type == RegionType.Polygon:
            if len(region.holes) == 1:
                assert region.holes[0].type == RegionType.Ellipse
            else:
                assert len(region.holes) == 3
                assert all([x.type == RegionType.Polygon for x in region.holes])


def test_geojson(file):
    hx = HaloXML()
    hx.load(file)
    hx.matchnegative()
    geores = hx.as_geojson()
    assert len(geores["features"]) == 4
    for feature in geores["features"]:
        geometry = feature["geometry"]
        assert geometry.is_valid


def test_shapely(file):
    from pyhaloxml.shapely import layer_to_shapely

    hx = HaloXML()
    hx.load(file)
    hx.matchnegative()
    shapely_res = layer_to_shapely(hx.layers[0])
    assert len(shapely_res.geoms) == 4
    for geometry in shapely_res.geoms:
        print(geometry.area)
        assert geometry.is_valid
