"""Compile the C++ examples against the headers, as their Makefiles do.

Compiling needs nvcc but no GPU, so these run in CI on every pull request.
"""

import os
import subprocess

import pytest

import harmonize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "examples", "cpp")
SOURCES = [
    "barrier_demo/demo.cpp",
    "collaz/collaz_hrm.cpp",
    "collaz/collaz_std.cpp",
    "example_neutron/program.cpp",
]
# Any architecture Harmonize supports; this checks that the code compiles.
ARCH = os.environ.get("HARMONIZE_TEST_CUDA_ARCH", "80")


@pytest.mark.nvcc
@pytest.mark.parametrize("source", SOURCES)
def test_example_compiles(source, tmp_path):
    header = os.path.join(harmonize.get_include(), "harmonize.h")
    command = [
        "nvcc", "-std=c++17", "-x", "cu", "--restrict", f"-arch=sm_{ARCH}",
        "-include", header, os.path.basename(source),
        "-o", str(tmp_path / "example.exe"),
    ]
    result = subprocess.run(
        command,
        cwd=os.path.join(EXAMPLES, os.path.dirname(source)),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
