"""Harmonize: an asynchronous GPU execution framework.

The names below are Harmonize's public Python API. The C++ headers are in the
`cpp` directory of this package; see `get_include()`.
"""

from importlib.metadata import PackageNotFoundError, version as _version
from os.path import dirname, join

try:
    __version__ = _version("harmonize-python")
except PackageNotFoundError:  # imported from a source tree that is not installed
    __version__ = "unknown"

import harmonize.config as config
import harmonize.pointer as pointer

from harmonize.runtime import (
    RuntimeSpec,
)

from harmonize.atomics import (
    array_atomic_add,
    array_atomic_max,
)

from harmonize.printing import print_formatted
from harmonize.timing import get_wall_clock

from harmonize.array import (
    local_array,
    array_from_ptr,
    alloc_device_bytes,
    alloc_managed_bytes,
    free_device_bytes,
    memcpy_device_to_host,
    memcpy_host_to_device,
)


def get_include():
    """Return the directory containing Harmonize's C++ headers.

    Add it to a C++ build's include path to use `#include "harmonize.h"`.
    """
    return join(dirname(__file__), "cpp")


__all__ = [
    "config",
    "pointer",
    "RuntimeSpec",
    "array_atomic_add",
    "array_atomic_max",
    "print_formatted",
    "get_wall_clock",
    "local_array",
    "array_from_ptr",
    "alloc_device_bytes",
    "alloc_managed_bytes",
    "free_device_bytes",
    "memcpy_device_to_host",
    "memcpy_host_to_device",
    "get_include",
]
