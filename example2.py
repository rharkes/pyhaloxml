"""
This example opens a datafile and saves it as a geojson.
One of the polygons does not close. This happens with Halo .annotations files for some reason.
The polygon is closed automatically and a warning is given.
"""
from pathlib import Path
from haloxml import HaloXML

pth = Path(Path.cwd(), 'exampledata', 'example_holes.annotations')
hx = HaloXML()
hx.load(pth)
for i, r in enumerate(hx.regions):
    if r.holes:
        if len(r.holes) == 1:
            print(f'Region {i} has 1 hole.')
        else:
            print(f'Region {i} has {len(r.holes)} holes.')
hx.to_geojson(Path(pth.parent, pth.stem+'_new'))
