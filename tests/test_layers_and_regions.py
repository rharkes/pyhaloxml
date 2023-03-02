"""
Open simple .annotation with a single layer and single region.
"""
import pytest as pytest
from pathlib import Path
from pyhaloxml import HaloXML


@pytest.fixture
def file():
    return Path(Path.cwd(), "tests", "testdata", "test1.annotations")


def test_nr_layers(file):
    hx = HaloXML()
    hx.load(file)
    assert len(hx.layers) == 1


def test_nr_regions(file):
    hx = HaloXML()
    hx.load(file)
    assert len(hx.layers[0].regions) == 1
