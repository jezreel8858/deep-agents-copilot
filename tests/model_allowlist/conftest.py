"""Fixtures leves para os testes de tools.model_allowlist.refresh.

Garantias: nenhuma chamada de rede real (guard autouse) e allowlist de trabalho
sempre em ``tmp_path`` (nunca o ``model-allowlist.yaml`` real nem ``.model-profiles``).
"""

from __future__ import annotations

import datetime as dt
import socket
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TODAY = dt.date(2026, 10, 15)

BASE_YAML = """schema_version: 1
verified_at: "2026-10-10"          # frescor global
freshness_days: 30
models:
  # comentário do Auto
  - name: Auto
    provider: github
    status: special
    pinnable: false               # seletor da IDE
    retirement_date: null
    cost:
      label: variable
    cost_rank: null

  - name: Claude Haiku 5.5
    provider: anthropic
    status: ga
    pinnable: true
    retirement_date: null         # sem data
    cost:
      label: low
      input: 10
    cost_rank: 1

  - name: Gemini 3.8 Flash
    provider: google
    status: ga
    pinnable: true
    retirement_date: null
    cost:
      label: low
      input: 5
    cost_rank: 2

  - name: Legacy Model 1
    provider: openai
    status: ga
    pinnable: true
    retirement_date: "2026-09-01"
    cost_rank: 3
# comentário final
"""


@pytest.fixture(autouse=True)
def _no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha o teste se qualquer socket for aberto/conectado."""

    def _boom(*_a, **_k):
        raise AssertionError("acesso de rede real proibido nos testes")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)
    monkeypatch.setattr(socket, "getaddrinfo", _boom)


@pytest.fixture
def today() -> dt.date:
    return TODAY


@pytest.fixture
def load_html():
    def _load(name: str) -> str:
        return (FIXTURES_DIR / name).read_text(encoding="utf-8")

    return _load


@pytest.fixture
def valid_html(load_html) -> str:
    return load_html("valid_supported_models.html")


@pytest.fixture
def allowlist_text() -> str:
    return BASE_YAML


@pytest.fixture
def allowlist_file(tmp_path: Path) -> Path:
    path = tmp_path / "work" / "model-allowlist.yaml"
    path.parent.mkdir()
    path.write_bytes(BASE_YAML.encode("utf-8"))
    return path


@pytest.fixture
def allowlist_data(allowlist_text):
    import yaml

    return yaml.safe_load(allowlist_text)
