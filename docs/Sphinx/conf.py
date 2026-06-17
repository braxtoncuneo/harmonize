# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Harmonize'
copyright = '2025, -'
author = '-'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",

    "breathe",
    "myst_parser",
    "autodoc2"

    # Formerly Utilized Extensions:
    # "sphinx.ext.autodoc",
    # "sphinx.ext.autosummary",
]

templates_path = ['_templates']
exclude_patterns = []

# 
# Breathe Configuration
# 
breathe_projects = {"Harmonize cpp": "./xml/"}
breathe_default_project = "Harmonize cpp"

# 
# Autodoc 2 Configuration
# 
autodoc2_sort_names = True
autodoc2_packages = [
    "../../python/harmonize/"
]

# Configure autodoc2 to interpret all docstrings as Markdown.
autodoc2_docstring_parser_regexes = [
    (r".*", "myst")
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']