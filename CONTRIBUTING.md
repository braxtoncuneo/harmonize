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
