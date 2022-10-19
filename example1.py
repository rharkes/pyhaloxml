"""
This example opens a datafile and moves all the regions with 5 vertices to Layer 1 and puts the rest in Layer 2.
In this file this moves the rectangles to Layer 1 and the circles to Layer 2.
"""
from pathlib import Path
from haloxml import HaloXML

pth = Path(Path.cwd(), "exampledata", "example.annotations")
hx = HaloXML()
hx.load(pth)
for r in hx.regions:
    if len(r.getvertices()) == 5:
        r.annatr["Name"] = "Layer 1"
    else:
        r.annatr["Name"] = "Layer 2"
hx.save(Path(pth.parent, pth.stem + "_new"))
