"""Deprecated alias for the modules now directly in `harmonize`.

Harmonize's Python modules used to live in `harmonize.python`
(e.g. `harmonize.python.config`). They are now `harmonize.config` and so on.
The old names keep working, with a `DeprecationWarning`, and will be removed in
a future release.

Each `harmonize.python.<module>` is the same module object as
`harmonize.<module>`, not a copy, so settings changed through either name
(e.g. `config.DEBUG`) are shared.
"""

import importlib
import sys
import warnings

_MODULES = (
    "adapt",
    "array",
    "atomics",
    "codegen",
    "config",
    "diagnostics",
    "errors",
    "logging",
    "pointer",
    "prim",
    "printing",
    "runtime",
    "templates",
    "timing",
    "types",
)

warnings.warn(
    "harmonize.python is deprecated; its modules are now directly in harmonize "
    "(e.g. harmonize.config instead of harmonize.python.config)",
    DeprecationWarning,
    stacklevel=2,
)

# Registering the modules under their old names makes both
# `import harmonize.python.config` and `from harmonize.python import config` work.
for _name in _MODULES:
    _module = importlib.import_module(f"harmonize.{_name}")
    sys.modules[f"{__name__}.{_name}"] = _module
    globals()[_name] = _module
del _name, _module
