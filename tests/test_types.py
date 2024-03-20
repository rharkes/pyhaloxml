import pytest as pytest
from pathlib import Path
from pyhaloxml import HaloXML, RegionType


@pytest.fixture
def file():
    return Path(Path.cwd(), "tests", "testdata", "test_types.annotations")


def test_types(file):
    hx = HaloXML()
    hx.load(file)
    regiontypes={}
    for region in hx.layers[0].regions:
        if str(region.type) in regiontypes.keys():
            regiontypes[str(region.type)] += 1
        else:
            regiontypes[str(region.type)] = 1

    assert regiontypes == {'Ellipse': 2, 'Pin': 1, 'Polygon': 3, 'Rectangle': 2, 'Ruler': 2}
