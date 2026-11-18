#!/usr/bin/env bash
# Build the documentation site into docs/_build/html.
#
# Sphinx builds the guides (Markdown in docs/).
#
# Needs the packages in docs/requirements.txt.
#
# Environment:
#   DOCS_BUILD_DIR  Build directory. Default: docs/_build.
#   SPHINXOPTS      Extra sphinx-build options. Default: treat warnings as
#                   errors (-W --keep-going).
set -euo pipefail

docs=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
build=${DOCS_BUILD_DIR:-$docs/_build}
html=$build/html

rm -rf "$build"
mkdir -p "$build"

# shellcheck disable=SC2086
sphinx-build --builder html ${SPHINXOPTS:--W --keep-going} "$docs" "$html"

echo "Site written to $html"
