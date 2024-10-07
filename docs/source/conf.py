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
]
intersphinx_mapping = {
'python': ('https://docs.python.org/3', None),
'numpydoc': ('https://numpydoc.readthedocs.io/en/latest', None),
}

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"
