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
