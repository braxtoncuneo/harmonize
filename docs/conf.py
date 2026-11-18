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
]

exclude_patterns = ["_build", "README.md"]

# -- Markdown (MyST) -----------------------------------------------------------
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

# -- HTML ----------------------------------------------------------------------
html_theme = "furo"
html_title = "Harmonize"
html_theme_options = {
    "source_repository": "https://github.com/harmonize-software/harmonize",
    "source_branch": "main",
    "source_directory": "docs/",
}
