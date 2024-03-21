"""
This example opens a datafile and moves all the regions with 5 vertices to Layer 1 and puts the rest in Layer 2.
In this file this moves the rectangles to Layer 1 and the circles to Layer 2.
"""

from pathlib import Path
from pyhaloxml import HaloXML, Layer

pth = Path(Path.cwd(), "exampledata", "example.annotations")
hx = HaloXML()
hx.load(pth)
hx.matchnegative()
# create two empty layers, here with the same names/properties as the original layers
layer1 = Layer()
layer2 = Layer()
layer1.fromdict(hx.layers[0].todict())
layer2.fromdict(hx.layers[1].todict())
# add the regions to the appropriate layer
for layer in hx.layers:
    for region in layer.regions:
        if len(region.getvertices()) == 5:
            layer1.regions.append(region)
        else:
            layer2.regions.append(region)
hx.layers = []  # clear the original layers and add the new ones
hx.layers.append(layer1)
hx.layers.append(layer2)
hx.save(Path(pth.parent, pth.stem + "_new"))
