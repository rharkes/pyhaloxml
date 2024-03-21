import pytest as pytest
from pathlib import Path
from pyhaloxml import HaloXML, RegionType


@pytest.fixture
def file():
    return Path(Path.cwd(), "tests", "testdata", "test_layers.annotations")


@pytest.fixture
def jsonfile():
    return Path(Path.cwd(), "tests", "testdata", "test_layers.json")


def test_layers(file):
    hx = HaloXML()
    hx.load(file)
    assert len(hx.layers) == 3
    for layer in hx.layers:
        if layer.name == "myfirstlayer":
            assert layer.linecolor.getrgb() == (255, 247, 85)
        elif layer.name == "secondlayer":
            assert layer.linecolor.getrgb() == (39, 231, 212)
        elif layer.name == "thishasafour":
            assert layer.linecolor.getrgb() == (151, 72, 6)
        else:
            assert False
