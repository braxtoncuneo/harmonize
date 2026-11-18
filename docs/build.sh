#!/usr/bin/env bash
# Build the documentation site into docs/_build/html.
#
#   1. Sphinx builds the guides (Markdown in docs/) and the Python API, read
#      from the installed harmonize package's docstrings.
#   2. Doxygen builds the C++ API from harmonize/cpp into the site's cpp/
#      directory.
#
# Needs doxygen, Harmonize installed (`pip install -e .`; no GPU needed), and
# the packages in docs/requirements.txt.
#
# Environment:
#   DOCS_BUILD_DIR  Build directory. Default: docs/_build.
#   SPHINXOPTS      Extra sphinx-build options. Default: treat warnings as
#                   errors (-W --keep-going).
set -euo pipefail

docs=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root=$(dirname "$docs")
build=${DOCS_BUILD_DIR:-$docs/_build}
html=$build/html

rm -rf "$build"
mkdir -p "$build"

echo "== Sphinx: guides and Python API"
# shellcheck disable=SC2086
sphinx-build --builder html ${SPHINXOPTS:--W --keep-going} "$docs" "$html"

echo "== Doxygen: C++ API"
export DOXYGEN_OUTPUT=$html
export DOXYGEN_WARN_LOG=$build/doxygen-warnings.log
HARMONIZE_VERSION=$(python -c 'from importlib.metadata import version; print(version("harmonize-python"))')
export HARMONIZE_VERSION
(cd "$root" && doxygen "$docs/doxygen/Doxyfile")
echo "$(grep -c . "$DOXYGEN_WARN_LOG" || true) Doxygen warnings (listed in $DOXYGEN_WARN_LOG)"

echo "Site written to $html"
