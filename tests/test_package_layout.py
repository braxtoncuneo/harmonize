"""The package layout and the deprecated `harmonize.python` names.

These tests need no GPU.
"""

import importlib
import os
import sys
import warnings

import pytest

import harmonize

OLD_MODULES = [
    "adapt", "array", "atomics", "codegen", "config", "diagnostics", "errors",
    "logging", "pointer", "prim", "printing", "runtime", "templates", "timing",
    "types",
]


def _forget_old_names():
    for name in list(sys.modules):
        if name == "harmonize.python" or name.startswith("harmonize.python."):
            del sys.modules[name]


def test_headers_are_found():
    assert os.path.isfile(os.path.join(harmonize.get_include(), "harmonize.h"))
    assert os.path.isfile(harmonize.config.HARMONIZE_ROOT_HEADER)


def test_public_names_exist():
    for name in harmonize.__all__:
        assert hasattr(harmonize, name), name


def test_old_package_warns():
    _forget_old_names()
    with pytest.warns(DeprecationWarning, match="harmonize.python is deprecated"):
        importlib.import_module("harmonize.python")


@pytest.mark.parametrize("name", OLD_MODULES)
def test_old_module_names_are_the_same_modules(name):
    new = importlib.import_module(f"harmonize.{name}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        _forget_old_names()
        old = importlib.import_module(f"harmonize.python.{name}")
        from harmonize.python import config as old_config
    assert old is new
    assert old_config is harmonize.config


def test_settings_are_shared_between_old_and_new_names():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        import harmonize.python.config as old_config
    saved = harmonize.config.VERBOSE
    try:
        old_config.VERBOSE = not saved
        assert harmonize.config.VERBOSE is (not saved)
    finally:
        old_config.VERBOSE = saved
