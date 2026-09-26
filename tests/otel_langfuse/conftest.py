"""
conftest.py — Configuração de caminhos e fixtures compartilhadas para testes do otel_langfuse.
"""

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
OTEL_LANGFUSE_DIR = REPO_ROOT / "tools" / "otel-langfuse"

if str(OTEL_LANGFUSE_DIR) not in sys.path:
    sys.path.insert(0, str(OTEL_LANGFUSE_DIR))
