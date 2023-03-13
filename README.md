[![mypy](https://github.com/rharkes/pyhaloxml/actions/workflows/mypy.yml/badge.svg)](https://github.com/rharkes/pyhaloxml/actions/workflows/mypy.yml)
[![Black](https://github.com/rharkes/pyhaloxml/actions/workflows/black.yml/badge.svg)](https://github.com/rharkes/pyhaloxml/actions/workflows/black.yml)
[![Black](https://github.com/rharkes/pyhaloxml/actions/workflows/pytest.yml/badge.svg)](https://github.com/rharkes/pyhaloxml/actions/workflows/pytest.yml)

# PyHaloXML
Python code to read/write .annotation files from Halo. Can export as .geojson for further analysis.

# Examples
[Example 1](https://github.com/rharkes/pyhaloxml/blob/main/examples/example1.py) : Move rectangles to a different layer and save as `.annotation`.

[Example 2](https://github.com/rharkes/pyhaloxml/blob/main/examples/example2.py) : Check if annotations have holes in them and save as `.geojson`.

[Example 3](https://github.com/rharkes/pyhaloxml/blob/main/examples/example3.py) : Show the wkt representation of the shapely polygon.

[Example 4](https://github.com/rharkes/pyhaloxml/blob/main/examples/example4.py) : Create a .annotation file from coordinates.

# Installation
`pip install pyhaloxml`

# Loading speed
Rust is used to match the negative regions to positive regions, thanks to [Wim Pomp](github.com/wimpomp/)!

It takes 41 seconds to load a 30.9MB file with 856454 vertices in 5769 regions with 731 holes.
