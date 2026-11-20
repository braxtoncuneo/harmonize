"""Compile the C++ examples against the headers, as their Makefiles do.

Compiling needs the platform's compiler (nvcc or hipcc) but no GPU, so on CUDA
these run in CI on every pull request.
"""

import os
import subprocess

import pytest

import harmonize
from gpu_platform import compiler, platform

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "examples", "cpp")
SOURCES = [
    "barrier_demo/demo.cpp",
    "collaz/collaz_hrm.cpp",
    "collaz/collaz_std.cpp",
    "example_neutron/program.cpp",
]
# The GPU architecture to compile for. Any one Harmonize supports will do:
# this checks that the code compiles. Default: sm_80 on CUDA, and hipcc's
# default (the machine's GPU) on ROCm.
ARCH = os.environ.get("HARMONIZE_TEST_GPU_ARCH")


def compile_command(source, header, output):
    files = ["-include", header, source, "-o", output]
    if platform() == "rocm":
        arch = [f"--offload-arch={ARCH}"] if ARCH else []
        return [compiler(), "-std=c++17", "-x", "hip", *arch, *files]
    arch = f"-arch=sm_{ARCH or '80'}"
    return [compiler(), "-std=c++17", "-x", "cu", "--restrict", arch, *files]


@pytest.mark.compiler
@pytest.mark.parametrize("source", SOURCES)
def test_example_compiles(source, tmp_path):
    header = os.path.join(harmonize.get_include(), "harmonize.h")
    command = compile_command(
        os.path.basename(source), header, str(tmp_path / "example.exe")
    )
    result = subprocess.run(
        command,
        cwd=os.path.join(EXAMPLES, os.path.dirname(source)),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        " ".join(command) + "\n" + result.stdout + result.stderr
    )
