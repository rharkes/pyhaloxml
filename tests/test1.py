"""
Open simple .annotation with a single layer and single region.
"""
import pytest as pytest
from pathlib import Path
import geojson as gs
from pyhaloxml import HaloXML


@pytest.fixture
def file():
    return Path(Path.cwd(), 'testdata', 'test1.annotations')


@pytest.fixture
def wkt():
    return 'MULTIPOLYGON (((10627 68377, 10749 68354, 10870 68317, 10988 68267, 11106 68200, 11220 68116, 10627 68377)))'


@pytest.fixture
def geojson():
    return '{"features": [{"geometry": {"coordinates": [[[10627.0, 68377.0], [10749.0, 68354.0], [10870.0, 68317.0], [10988.0, 68267.0], [11106.0, 68200.0], [11220.0, 68116.0], [10627.0, 68377.0]]], "type": "Polygon"}, "properties": {"classification": {"colorRGB": [255, 247, 85], "name": "Layer 1"}, "isLocked": false, "object_type": "annotation"}, "type": "Feature"}], "type": "FeatureCollection"}'

def test_nr_layers(file):
    hx = HaloXML()
    hx.load(file)
    assert len(hx.layers) == 1


def test_nr_regions(file):
    hx = HaloXML()
    hx.load(file)
    assert len(hx.layers[0].regions) == 1


def test_shapely_wkt(file, wkt):
    hx = HaloXML()
    hx.load(file)
    assert hx.layers[0].as_shapely().wkt == wkt


def test_geojson(file, geojson):
    hx = HaloXML()
    hx.load(file)
    assert gs.dumps(hx.as_geojson(), sort_keys=True) == geojson
