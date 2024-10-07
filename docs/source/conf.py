# Configuration file for the Sphinx documentation builder.

# -- Project information
project = "pyhaloxml"
copyright = "2024, R.Harkes"
author = "R.Harkes"

release = "3.1.2"
version = "3.1.2"

# -- General configuration
extensions = [
    'sphinx.ext.autodoc',
    'numpydoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
]
intersphinx_mapping = {
'python': ('https://docs.python.org/3', None),
'numpydoc': ('https://numpydoc.readthedocs.io/en/latest', None),
'geojson': ('https://geojson.readthedocs.io/en/latest/', None),
'lxml': ('https://lxml.readthedocs.io/en/latest/', None),
}

autosummary_generate = False
autosummary_imported_members = True

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"
