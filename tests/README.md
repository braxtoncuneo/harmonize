# Tests

```sh
pip install -e ".[cuda13]" pytest
pytest tests
```

| Tests | Need | In CI |
|---|---|---|
| `test_package_layout.py`: package layout, deprecated `harmonize.python` names | nothing | every job |
| `test_cpp_examples.py`: the C++ examples compile | nvcc or hipcc | CUDA 13 job |
| `test_programs.py`: small programs in `programs/` build, run, and give correct results in event and async modes (event only on ROCm) | nvcc or hipcc, and a GPU | not yet (no GPU runners) |

The tests run on the GPU platform Harmonize selects (CUDA or ROCm; set
`HARMONIZE_PLATFORM` to choose), with its compiler: nvcc for CUDA, hipcc for
ROCm. The pytest header shows which. Set `HARMONIZE_TEST_GPU_ARCH` to compile
the C++ examples for another GPU (default: `80` on CUDA, hipcc's default on
ROCm; e.g. `gfx942` for an MI300A).

Tests skip when what they need is missing; the reason is printed with `-rs`.
`--require compiler` or `--require gpu` makes them fail instead, so a broken
environment cannot pass by skipping everything. To run the GPU tests:

```sh
pytest --require compiler --require gpu tests
```

nvcc must come from the same CUDA release as Numba's NVVM, and no newer than
the driver supports (`python -m harmonize check` tests both). With CUDA 13 from
pip, `pip install "cuda-toolkit[nvcc]==13.*"` installs a matching nvcc into
`site-packages/nvidia/cu13/bin`. That release ships `libcudart.so.13` but not
`libcudart.so`, which linking a Harmonize program needs; point the linker at
it with a symbolic link:

```sh
mkdir -p ~/cudart-link
ln -sf "$(python -c 'import nvidia; print(nvidia.__path__[0])')/cu13/lib/libcudart.so.13" ~/cudart-link/libcudart.so
export LIBRARY_PATH=~/cudart-link
```

A conda `cuda-nvcc` or a system CUDA toolkit does not need this.
