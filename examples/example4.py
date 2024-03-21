"""
Not recommended in any way! Going from GeoJSON to .annotation is a step in the wrong direction.
"""

from pathlib import Path
from pyhaloxml.Region import region_from_coordinates
from pyhaloxml import Layer, HaloXML
import geojson as gs

pth = Path(Path.cwd(), "exampledata", "qupath_test.geojson")

with open(pth, "r") as f:
    geo_data = gs.load(f)

hx = HaloXML()
for feature in geo_data["features"]:
    layer = Layer()
    if feature["geometry"]["type"] == "MultiPolygon":
        print("multi")
        layer.name = feature["properties"]["classification"]["name"]
        layer.linecolor.setrgb(*feature["properties"]["classification"]["color"])
        for coordinates in feature["geometry"]["coordinates"]:
            reg = region_from_coordinates(coordinates)
            layer.addregion(reg)
    else:
        print("single")
        layer.name = feature["properties"]["classification"]["name"]
        layer.linecolor.setrgb(*feature["properties"]["classification"]["color"])
        coordinates = feature["geometry"]["coordinates"]
        reg = region_from_coordinates(coordinates)
        layer.addregion(reg)
    hx.layers.append(layer)
hx.save(Path(pth.parent, "qupath_test"))
# --- to create the .geojson file --- #
hx = HaloXML()
hx.load(Path(pth.parent, "qupath_test.annotations"))
hx.matchnegative()
hx.to_geojson(Path(pth.parent, "qupath_test"))
