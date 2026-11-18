# Harmonize

Harmonize is an execution framework for GPU with the aims of increasing performance and decreasing development burden for applications requiring complex processing patterns.
Harmonize is currently available both as a headers-only CUDA/HIP C++ library and as a Python package. In both forms, functionality is exposed as an asynchronous processing framework.

## Fundamentals

The system of asynchronous functions that are executed within a given runtime are defined in advance through a **program specification**.
A program specification only represents these systems abstractly, but they may be transformed into an implementation by declaring a **program** ***specialization***.

Program specifications are defined by application developers, and represent the business logic of what needs to be accomplished in the GPU, whereas the templates (**program types**) used to transform them into specializations are defined by framework developers.
This structure is used because it separates much of the underlying implementation details away from application developers, delegating those concerns to the framework developers.
Ideally, with the addition of a program type, transitioning a codebase to this other program could be as little as a one-line refactor:

```
< using MyProgram = EventProgram<MyProgramSpec>;
> using MyProgram = AsyncProgram<MyProgramSpec>;
```

Likewise, as long as the interface between the specification and the program type does not change, program types may be updated without requiring refactors from the application developers.

## Why Async?

Asynchronous programming represents a looser contract between program and execution environment.
Once a function is called, there is no guarantee of where or when that call is actually evaluated.
If the call is lazy, then the evaluation may not happen at all.

This looser contract is useful, because it allows an interface to represent a wide variety of execution strategies without breaking any promises.
By representing all program types as different asynchronous runtimes, they can be used interchangeably as long as they fulfill the few promises made by the runtime's interface.


## Dependencies

### CUDA C++ Dependencies

The C++ framework currently requires the following for CUDA:

- a CUDA compiler (e.g. `nvcc`)
- the CUDA runtime (host and device)

### HIP C++ Dependencies

The C++ framework currently requires the following for ROCM:

- a HIP compiler (e.g. `hipcc`)
- the ROCM runtime (host and device)


### Python Dependencies

Python bindings require:

- Non-package Dependencies
  - CUDA execution requires the CUDA toolkit, including:
    - `nvcc`
    - CUDA runtime (host and device)
  - ROCM execution requires the ROCM 6.0.0 toolkit, including its version of:
    - `hipcc`
    - `clang-offload-bundler`
    - `llvm-link`
    - `llvm-as`
    - HIP runtime (host and device)

- Python Package Dependencies
  - [`numpy`](https://github.com/numpy/numpy)
  - [`llvmlite`](https://github.com/numba/llvmlite)
  - For CUDA:
    - [`numba`](https://github.com/numba/numba)
  - For ROCM:
    - [the AMD fork of `numba`](https://github.com/ROCm/numba-hip)


## Installation

Harmonize is published on PyPI as `harmonize-python` and imported as
`harmonize`. (The PyPI project named `harmonize` is unrelated.)

For NVIDIA GPUs, install the extra matching your CUDA toolkit's major version:

```sh
pip install "harmonize-python[cuda13]"   # or harmonize-python[cuda12]
```

That version's `nvcc` must also be available from the system, an environment
module (`module load cuda`), or conda (`conda install -c nvidia cuda-nvcc`).

For AMD GPUs, install ROCm and the corresponding version of `numba-hip` for
your ROCm release (here, ROCm 6.4.0):

```sh
pip install --extra-index-url https://test.pypi.org/simple \
    "numba-hip[rocm-6-4-0] @ git+https://github.com/ROCm/numba-hip.git"
pip install harmonize-python
```

To install from a clone of this repository instead, run
`pip install ".[cuda13]"` (or `pip install .` for AMD) in it; add `-e` to
work on Harmonize itself.


## Checking your setup

```sh
python -m harmonize info    # detected platform, toolchain, and devices
python -m harmonize check   # problems that would stop GPU builds; exits non-zero if any
```

`check` reports, for example, a missing `nvcc`, a CUDA toolkit newer than the
driver, a toolkit too old to target the installed GPU, or Numba's NVVM emitting
PTX newer than `nvcc` can assemble (pip's CUDA packages can be newer than the
`nvcc` on `PATH`; `check` compiles a small function and assembles it to test this).
Include the output of `info` when reporting problems.


## Selecting a platform

By default, Harmonize uses ROCm when `numba-hip` is installed and CUDA
otherwise. To explicitly require a platform, set `HARMONIZE_PLATFORM` to
`cuda` or `rocm`:

```sh
HARMONIZE_PLATFORM=cuda python my_program.py
```

Toolkit locations can be set with `harmonize.config.set_cuda_path()` and
`harmonize.config.set_rocm_path()`, otherwise `nvcc` and `hipcc` are found
on `PATH`.



