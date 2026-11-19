# Changelog

Notable changes to Harmonize. Versions follow [semantic versioning](https://semver.org/);
before 1.0, a minor version (0.x.0) may include breaking changes.

## 0.1.0 (2026-11-18)

### Changed (breaking)

- Harmonize is published on PyPI as `harmonize-python`; it is still imported as
  `harmonize`. (The PyPI project named `harmonize` is unrelated.)
- The Python modules moved from `harmonize.python` into `harmonize` (for
  example, `harmonize.config` instead of `harmonize.python.config`), and the
  public API is importable from `harmonize` directly. The old names still work,
  as the same modules, but `import harmonize.python` raises a
  `DeprecationWarning`; they will be removed in a future release.
- Requires Python 3.10 or newer.
- GPU backends are installed as extras: `harmonize-python[cuda13]` or
  `harmonize-python[cuda12]`. For AMD GPUs, `numba-hip` is installed separately
  for your ROCm release.
- The GPU platform is chosen once, at import. Set `HARMONIZE_PLATFORM` to
  `cuda` or `rocm` to require one; the default, `auto`, prefers ROCm when its
  Numba backend is installed.

### Added

- `python -m harmonize info` reports the platform, toolchain, and GPUs, and
  `python -m harmonize check` diagnoses common setup problems, including an nvcc
  too old to assemble the PTX that Numba's NVVM emits.
- `harmonize.get_include()` returns the directory of the C++ headers, and
  `harmonize.__version__` the installed version.
- Host/device memory functions: `alloc_device_bytes`, `alloc_managed_bytes`,
  `free_device_bytes`, `memcpy_host_to_device`, `memcpy_device_to_host`, and
  `array_from_ptr`, with refined pointer utilities in `harmonize.pointer`.
- `get_wall_clock()`, a wall-clock builtin for device code.
- State load and store functions accept CPU states that are either record
  objects or arrays.
- A [documentation site](https://harmonize-software.github.io/harmonize/) with
  guides and the Python and C++ API references.
- Tests, run in CI on every pull request.

### Fixed

- `memcpy_device_to_host` used the wrong copy direction, and the Python
  memcpy functions copied too few bytes for multidimensional arrays.
- ROCm: device code is compiled to object files and linked with
  `llvm-link --override`, which resolves multiply-defined symbols; builds
  pass ROCm 7.1's stricter checks.
- The `barrier_demo` C++ example compiles against the current headers.

### Removed

- `install.sh`; see the installation section of the README.

## 0.0.2 (2024-10-31)

- AMD GPU support through `numba-hip`, with CUDA/HIP adapters, AMD-friendly
  atomics, and multi-field states.
- Event-mode status flags, with a Python wrapper; separate binding and loading
  steps; a setting to disable or force compilation.
- `local_array`, a `select_device` builtin, and import checks.
- Verbose printing is off by default.

## 0.0.1 (2024-04-20)

- First release, with the Python package structure.
