# Sphinx settings for the Harmonize documentation site.
#
# docs/build.sh runs Sphinx.
#
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from importlib import metadata

project = "Harmonize"
author = "The Harmonize developers"
copyright = "2025, The Harmonize developers"
try:
    release = metadata.version("harmonize-python")
except metadata.PackageNotFoundError:
    release = ""

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinxcontrib.mermaid",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

exclude_patterns = ["_build", "README.md"]

# -- Markdown (MyST) -----------------------------------------------------------
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

# -- Python API ----------------------------------------------------------------
# Docstrings use the NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
napoleon_google_docstring = False
napoleon_numpy_docstring = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "numba": ("https://numba.readthedocs.io/en/stable", None),
}

# -- HTML ----------------------------------------------------------------------
html_theme = "furo"
html_title = "Harmonize"
html_theme_options = {
    "source_repository": "https://github.com/harmonize-software/harmonize",
    "source_branch": "main",
    "source_directory": "docs/",
}
