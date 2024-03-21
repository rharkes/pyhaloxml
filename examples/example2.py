"""
This example opens a datafile and saves it as a geojson.
One of the polygons does not close. This happens with Halo .annotations files for some reason.
The polygon is closed automatically and a warning is given.
"""

from pathlib import Path
from pyhaloxml import HaloXML

pth = Path(Path.cwd(), "exampledata", "multiple_holes.annotations")
# pth = Path(Path.cwd(), "exampledata", "example_holes.annotations")
hx = HaloXML()
hx.load(pth)
hx.matchnegative()
for layer in hx.layers:
    for i, region in enumerate(layer.regions):
        if len(region.holes) == 1:
            print(f"Region {i} in annotation {layer.name} has 1 hole.")
        else:
            print(
                f"Region {i} in annotation {layer.name} has {len(region.holes)} holes."
            )
hx.to_geojson(Path(pth.parent, pth.stem + "_new"))
