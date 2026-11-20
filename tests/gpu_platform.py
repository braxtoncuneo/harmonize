"""The GPU platform Harmonize selected for this test run, and its compiler."""

from harmonize import config

# Ask in a subprocess, so the test process does not initialize the GPU driver.
GPU_PROBE = """
from harmonize import config
if config.ROCM_AVAILABLE:
    print(config.hip.is_available())
elif config.CUDA_AVAILABLE:
    print(config.cuda.is_available())
"""


def platform():
    """The platform Harmonize selected: "cuda", "rocm", or None."""
    if config.ROCM_AVAILABLE:
        return "rocm"
    if config.CUDA_AVAILABLE:
        return "cuda"
    return None


def compiler():
    """The selected platform's compiler command (nvcc or hipcc), or None."""
    if platform() == "rocm":
        return config.hipcc_path()
    if platform() == "cuda":
        return config.nvcc_path()
    return None
