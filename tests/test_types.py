import pytest as pytest
from pathlib import Path
from pyhaloxml import HaloXML


@pytest.fixture
def file():
    return Path(Path.cwd(), "tests", "testdata", "test_types.annotations")


@pytest.fixture
def jsonfile():
    return Path(Path.cwd(), "tests", "testdata", "test_types.json")


def test_types(file):
    hx = HaloXML()
    hx.load(file)
    regiontypes = {}
    for region in hx.layers[0].regions:
        if str(region.type) in regiontypes.keys():
            regiontypes[str(region.type)] += 1
        else:
            regiontypes[str(region.type)] = 1

    assert regiontypes == {
        "Ellipse": 2,
        "Pin": 1,
        "Polygon": 3,
        "Rectangle": 2,
        "Ruler": 2,
    }


def test_geojson(file):
    hx = HaloXML()
    hx.load(file)
    geores = hx.as_geojson()
    regiontypes = {}
    for feature in geores["features"]:
        geometry = feature["geometry"]
        assert geometry.is_valid
        if geometry["type"] in regiontypes.keys():
            regiontypes[geometry["type"]] += 1
        else:
            regiontypes[geometry["type"]] = 1

    assert regiontypes == {"LineString": 2, "Point": 1, "Polygon": 7}


def test_shapely(file, jsonfile):
    from pyhaloxml.shapely import layer_to_shapely
    import json

    with open(jsonfile, "r") as fp:
        datainfo = json.load(fp)
    pixelsize = datainfo["micronsperpixel"]
    hx = HaloXML()
    hx.load(file)
    shapely_res = layer_to_shapely(hx.layers[0])
    regiontypes = {}
    for geometry in shapely_res.geoms:
        print(geometry.area)
        assert geometry.is_valid
        if geometry.geom_type in regiontypes.keys():
            regiontypes[geometry.geom_type] += 1
        else:
            regiontypes[geometry.geom_type] = 1
    assert regiontypes == {"LineString": 4, "Point": 1, "Polygon": 5}
