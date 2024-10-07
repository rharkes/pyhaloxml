# Configuration file for the Sphinx documentation builder.

# -- Project information
project = "pyhaloxml"
copyright = "2023, R.Harkes"
author = "R.Harkes"

release = "3.1.2"
version = "3.1.2"

# -- General configuration
extensions = [
    "sphinx.ext.napoleon",
    "numpydoc",
]
napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"
