# Contributing to Harmonize

Thank you for helping. Bug reports, questions, documentation fixes, and code
are all welcome.

## Reporting a problem

Open an [issue](https://github.com/harmonize-software/harmonize/issues). For
problems building or running on a GPU, include the output of
`python -m harmonize info` and `python -m harmonize check`. To report a
security problem, follow [SECURITY.md](SECURITY.md) instead.

## Setting up

```sh
git clone https://github.com/harmonize-software/harmonize.git
cd harmonize
pip install -e ".[cuda13]" pytest   # or .[cuda12]; see the README for AMD
python -m harmonize check
```

## Making a change

- Branch from `main` and open a pull request against it.
- Prefer several small commits, each of which builds and passes the tests,
  over one large one. Describe in each commit message what changed and why.
- Run the tests (see [tests/README.md](tests/README.md)). CI runs those that
  need no GPU on every pull request. If you changed the runtime, the code
  generator, or the C++ headers, also run the GPU tests and say so in the pull
  request:
  ```sh
  pytest --require nvcc --require gpu tests
  ```
- New public Python names go in `harmonize/__init__.py`'s `__all__`, with
  NumPy-style docstrings, and in `docs/python-api.md`. See
  [docs/README.md](docs/README.md) for writing and building the documentation.

By contributing, you agree that your contributions are licensed under the
project's [BSD 3-Clause License](LICENSE). Everyone taking part is expected to
follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Making a release

For maintainers. The version is set in `pyproject.toml`; the tests check that
`CITATION.cff` and `CHANGELOG.md` match it.

1. In a pull request, set the new version in `pyproject.toml` and in
   `CITATION.cff` (with `date-released`), and rename the changelog's
   "Unreleased" section to the version and the release date. Merge it.
2. Optionally, do a dry run: Actions -> Release -> Run workflow uploads the
   build to [TestPyPI](https://test.pypi.org/p/harmonize-python).
3. Create a GitHub release with a new tag `vX.Y.Z` on `main`, matching the
   version, and the changelog section as its notes. Publishing it starts the
   Release workflow, which builds the package, checks that the tag matches the
   version and points to a commit on `main`, and uploads to PyPI.

### Release configuration

Publishing depends on settings outside this repository. If releases fail with
a publisher or environment error, or after moving or renaming the repository,
the workflow, or an environment, check that these still match:

- **PyPI and TestPyPI:** the `harmonize-python` project has a trusted publisher
  for owner `harmonize-software`, repository `harmonize`, workflow
  `release.yml`, and environment `pypi` (on pypi.org) or `testpypi` (on
  test.pypi.org). No token is stored anywhere.
- **Environments** (Settings -> Environments): `pypi` allows the tag pattern
  `v*`, since a release runs on its tag rather than a branch, and may require a
  reviewer's approval; `testpypi` allows only `main`.
- **Tag ruleset** (Settings -> Rules): only maintainers may create, move, or
  delete tags matching `v*`.
