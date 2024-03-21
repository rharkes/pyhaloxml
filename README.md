[![Mypy](https://github.com/rharkes/pyhaloxml/actions/workflows/mypy.yml/badge.svg)](https://github.com/rharkes/pyhaloxml/actions/workflows/mypy.yml)
[![Black](https://github.com/rharkes/pyhaloxml/actions/workflows/black.yml/badge.svg)](https://github.com/rharkes/pyhaloxml/actions/workflows/black.yml)
[![Pytest](https://github.com/rharkes/pyhaloxml/actions/workflows/pytest.yml/badge.svg)](https://github.com/rharkes/pyhaloxml/actions/workflows/pytest.yml)
[![Docs](https://readthedocs.org/projects/pyhaloxml/badge/?version=latest&style=flat)](https://readthedocs.org/projects/pyhaloxml)
# PyHaloXML
Python code to read/write .annotation files from Halo. Can export as .geojson for further analysis.

## Examples
[Example 1](https://github.com/rharkes/pyhaloxml/blob/main/examples/example1.py) : Move rectangles to a different layer and save as `.annotation`.

[Example 2](https://github.com/rharkes/pyhaloxml/blob/main/examples/example2.py) : Check if annotations have holes in them and save as `.geojson`.

[Example 3](https://github.com/rharkes/pyhaloxml/blob/main/examples/example3.py) : Show the wkt representation of the shapely polygon.

[Example 4](https://github.com/rharkes/pyhaloxml/blob/main/examples/example4.py) : Create a .annotation file from coordinates.

## Installation
`pip install pyhaloxml`

## Note on version 3
The matching of negative to positive regions now needs to be done by the user after loading the data. The examples have been updated. This needed to happen because negative regions can be unmatched in Halo. This would cause errors when loading. 

## Loading speed
Rust is used to match the negative regions to positive regions, thanks to [Wim Pomp](github.com/wimpomp/)!

It takes 41 seconds to load a 30.9MB file with 856454 vertices in 5769 regions with 731 holes.

## Development
* Install [Rust](https://rustup.rs/)
* Clone the repository
* `pip install -e .`

### Notes on development
* The xml is relatively simple. There are Annotations and an annotation contains regions.
* Regions can be either positive or negative. However regions in an annotation are not hierarchical. So there is no telling what negative region should go with what positive region.
* This package expects a negative region to be fully enclosed by one positive region. The matching is done by taking a single point that is inside or on the border of the negative region and checking if it is inside a positive region.
