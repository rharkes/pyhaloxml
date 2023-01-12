"""
Not recommended in any way! Going from GeoJSON to .annotation is a step in the wrong direction.
"""

from pathlib import Path
from pyhaloxml.Region import region_from_coordinates
from pyhaloxml import Layer, HaloXML
import geojson as gs

pth = Path(Path.cwd(), "exampledata", "multiple_holes_new.geojson")

with open(pth, 'r') as f:
    geo_data = gs.load(f)

# we want to have a geojson.geometry.Polygon:
coordinates = geo_data['features'][0]['geometry']['coordinates']
reg = region_from_coordinates(coordinates)
layer = Layer()
layer.addregion(reg)
hx = HaloXML()
hx.layers = [layer]
hx.save(Path(pth.parent, "geojson_to_annotation"))
