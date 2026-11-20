"""Build and run small Harmonize programs on a GPU and check their results.

Each program runs in its own process and directory: Harmonize keeps its build
state in class attributes and writes its build cache to the working directory.
"""

import os
import subprocess
import sys

import pytest

from gpu_platform import platform

PROGRAMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "programs")


def run_program(name, *args, cwd):
    result = subprocess.run(
        [sys.executable, os.path.join(PROGRAMS, name), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30 * 60,
    )
    assert result.returncode == 0, result.stdout[-5000:] + result.stderr[-5000:]
    return result.stdout


@pytest.mark.gpu
@pytest.mark.compiler
@pytest.mark.parametrize("layout", ["record", "array"])
@pytest.mark.parametrize("mode", ["event", "async"])
def test_collatz(mode, layout, tmp_path):
    if mode == "async" and platform() == "rocm":
        pytest.skip("Harmonize supports only event mode on ROCm")
    output = run_program("collatz.py", mode, layout, cwd=tmp_path)
    assert f"collatz {mode} {layout}: OK" in output
