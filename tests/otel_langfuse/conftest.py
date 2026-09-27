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


@pytest.fixture(autouse=True)
def isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isola variáveis de ambiente para garantir hermeticidade dos testes."""
    for var in (
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_OTLP_AUTH",
        "LANGFUSE_HOST",
        "DEPLOY_ENV",
        "OTEL_SERVICE_NAME",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
    ):
        monkeypatch.delenv(var, raising=False)
