# shim for pylib going away
# if pylib is installed this file will get skipped
# (`py/__init__.py` has higher precedence)
from __future__ import annotations

import sys

from _pytest._py import error, path

sys.modules["py.error"] = error
sys.modules["py.path"] = path

__all__ = ["error", "path"]
