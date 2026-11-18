"""Test options shared by all tests.

Tests that need nvcc or a CUDA GPU skip when it is missing. Pass
`--require nvcc` or `--require gpu` (CI does) to make them fail instead, so a
broken environment cannot pass by skipping everything.
"""

import functools
import os
import shutil
import subprocess
import sys

import pytest

REQUIREMENTS = ("nvcc", "gpu")


def pytest_addoption(parser):
    parser.addoption(
        "--require",
        action="append",
        default=[],
        choices=REQUIREMENTS,
        help="fail, instead of skip, tests that need this (repeatable)",
    )


def pytest_report_header(config):
    import harmonize

    # Shows whether the tests import an installed wheel or a source checkout
    return f"harmonize: {os.path.dirname(harmonize.__file__)}"


def pytest_configure(config):
    config.addinivalue_line("markers", "nvcc: needs nvcc")
    config.addinivalue_line("markers", "gpu: needs a CUDA GPU")


@functools.cache
def _missing(requirement):
    """Why `requirement` is unavailable, or None if it is available."""
    if requirement == "nvcc":
        return None if shutil.which("nvcc") else "nvcc is not on PATH"
    # Ask in a subprocess, so this process does not initialize CUDA.
    probe = subprocess.run(
        [sys.executable, "-c", "from numba import cuda; print(cuda.is_available())"],
        capture_output=True,
        text=True,
    )
    return None if probe.stdout.strip() == "True" else "no CUDA GPU is available"


def pytest_runtest_setup(item):
    for requirement in REQUIREMENTS:
        if item.get_closest_marker(requirement) is None:
            continue
        reason = _missing(requirement)
        if reason is None:
            continue
        if requirement in item.config.getoption("require"):
            pytest.fail(f"{reason}, and --require {requirement} was given")
        pytest.skip(reason)
