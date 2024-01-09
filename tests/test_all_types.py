import pytest as pytest
from pathlib import Path
from pyhaloxml import HaloXML


@pytest.fixture
def file():
    return Path(Path.cwd(), "tests", "testdata", "HaloMultilayerTest.annotations")


def test_types(file):
    hx = HaloXML()
    hx.load(file)
    assert len(hx.layers) == 1
