"""Permite ``python -m tools.model_allowlist``."""

from __future__ import annotations

import sys

from .refresh import main

if __name__ == "__main__":
    sys.exit(main())
