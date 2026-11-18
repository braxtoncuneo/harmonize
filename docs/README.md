# Harmonize documentation

The documentation site has three parts, built by `docs/build.sh` and published
to GitHub Pages by `.github/workflows/docs.yml` from `main` (pull requests build
it without publishing):

| Part | Source | Built by |
|------|--------|----------|
| Guides | Markdown pages in `docs/` ([MyST](https://myst-parser.readthedocs.io/)) | [Sphinx](https://www.sphinx-doc.org/), [Furo](https://pradyunsg.me/furo/) theme |
| Python API | Docstrings in `harmonize/` (listed in `python-api.md`) | Sphinx autodoc |
| C++ API, at `cpp/` | `harmonize/cpp` | [Doxygen](https://www.doxygen.nl/) with [doxygen-awesome-css](https://jothepro.github.io/doxygen-awesome-css/) |

## Writing pages

Pages are Markdown with MyST extensions. Start each with a `#` title and list
it in a `toctree` in `index.md`. Cards, tabs, and grids come from
[sphinx-design](https://sphinx-design.readthedocs.io/); diagrams can use
` ```{mermaid} ` blocks. `index.md` and `installation.md` show examples.

## Docstrings

Python docstrings use the
[NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html):

```python
def alloc_device_bytes(size):
    """Allocate memory on the GPU.

    Parameters
    ----------
    size : int
        Number of bytes to allocate.

    Returns
    -------
    int
        Device address of the allocation.
    """
```

New public functions and classes must be exported from `harmonize/__init__.py`
(in `__all__`) and listed in `python-api.md`.

C++ comments use Doxygen's `//!` or `/** ... */` style.

## Building locally

Needs `doxygen`, Harmonize installed, and the packages in `requirements.txt`:

```sh
pip install -e . -r docs/requirements.txt
docs/build.sh
python -m http.server --directory docs/_build/html
```

Then open <http://localhost:8000>. Sphinx warnings fail the build; set
`SPHINXOPTS=` to see the site anyway. Doxygen's warnings are listed in
`docs/_build/doxygen-warnings.log`.

`doxygen/doxygen-awesome/` holds version 2.5.0 of doxygen-awesome-css (MIT
license); to update it, replace its two `.css` files.
