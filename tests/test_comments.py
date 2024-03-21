import pytest as pytest
from pathlib import Path
from pyhaloxml import HaloXML, RegionType


@pytest.fixture
def file():
    return Path(Path.cwd(), "tests", "testdata", "test_comments.annotations")


@pytest.fixture
def jsonfile():
    return Path(Path.cwd(), "tests", "testdata", "test_comments.json")


def test_layers(file):
    hx = HaloXML()
    hx.load(file)
    for region in hx.layers[0].regions:
        if region.type == RegionType.Rectangle:
            assert len(region.comments) == 2
        if region.type == RegionType.Ellipse:
            assert len(region.comments) == 2
        if region.type == RegionType.Polygon:
            assert len(region.comments) == 1
