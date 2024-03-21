"""
This example opens a datafile and prints the wkt representation of the shapely polygon
"""

from pathlib import Path
from pyhaloxml import HaloXML
from pyhaloxml.shapely import layer_to_shapely

pth = Path(Path.cwd(), "exampledata", "multiple_holes.annotations")
hx = HaloXML()
hx.load(pth)
hx.matchnegative()
sl = layer_to_shapely(hx.layers[0])
print(f"{sl.wkt}")
