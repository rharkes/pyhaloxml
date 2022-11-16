"""
This example opens a datafile and prints the wkt representation of the shapely polygon
"""
from pathlib import Path
from haloxml import HaloXML

pth = Path(Path.cwd(), "exampledata", "multiple_holes.annotations")
hx = HaloXML()
hx.load(pth)
sl, n = hx.as_shapely()
for i in range(len(sl)):
    print(f"{n[i]} ; {sl[i].wkt}")
