"""The version is set once, in pyproject.toml; the other copies must match it."""

from importlib.metadata import version

import harmonize


def test_version_attribute():
    assert harmonize.__version__ == version("harmonize-python")
