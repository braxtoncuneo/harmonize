"""The version is set once, in pyproject.toml; the other copies must match it."""

import os
import re
from importlib.metadata import version

import harmonize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(name):
    with open(os.path.join(ROOT, name)) as file:
        return file.read()


def test_version_attribute():
    assert harmonize.__version__ == version("harmonize-python")


def test_citation_version():
    match = re.search(r"^version:\s*['\"]?([^'\"\s]+)", read("CITATION.cff"), re.MULTILINE)
    assert match, "CITATION.cff has no version"
    assert match.group(1) == harmonize.__version__


def test_changelog_has_version():
    assert re.search(
        rf"^## {re.escape(harmonize.__version__)}\b", read("CHANGELOG.md"), re.MULTILINE
    ), f"CHANGELOG.md has no section for {harmonize.__version__}"
