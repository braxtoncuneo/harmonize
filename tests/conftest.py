"""Test options shared by all tests.

Tests run on the GPU platform Harmonize selects at import (CUDA or ROCm; set
HARMONIZE_PLATFORM to choose). Tests that need that platform's compiler (nvcc
or hipcc) or a GPU skip when it is missing. Pass `--require compiler` or
`--require gpu` (CI does) to make them fail instead, so a broken environment
cannot pass by skipping everything.
"""

import functools
import os
import shutil
import subprocess
import sys

import pytest

from gpu_platform import GPU_PROBE, compiler, platform

REQUIREMENTS = ("compiler", "gpu")


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

    # Shows the platform, and whether the tests import an installed wheel or
    # a source checkout
    return [
        f"harmonize: {os.path.dirname(harmonize.__file__)}",
        f"harmonize platform: {platform() or 'none'} (compiler: {compiler()})",
    ]


def pytest_configure(config):
    config.addinivalue_line("markers", "compiler: needs nvcc (CUDA) or hipcc (ROCm)")
    config.addinivalue_line("markers", "gpu: needs a GPU of the selected platform")


@functools.cache
def _missing(requirement):
    """Why `requirement` is unavailable, or None if it is available."""
    if platform() is None:
        return "Harmonize found no GPU platform (neither numba-cuda nor numba-hip)"
    if requirement == "compiler":
        return None if shutil.which(compiler()) else f"{compiler()} is not on PATH"
    probe = subprocess.run(
        [sys.executable, "-c", GPU_PROBE], capture_output=True, text=True
    )
    if probe.stdout.strip() == "True":
        return None
    return f"no {platform().upper()} GPU is available"


def pytest_runtest_setup(item):
    required = item.config.getoption("require")
    missing = [
        (requirement, _missing(requirement))
        for requirement in REQUIREMENTS
        if item.get_closest_marker(requirement) and _missing(requirement)
    ]
    for requirement, reason in missing:
        if requirement in required:
            pytest.fail(f"{reason}, and --require {requirement} was given")
    if missing:
        pytest.skip(missing[0][1])
