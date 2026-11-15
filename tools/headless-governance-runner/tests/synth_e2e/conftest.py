"""Fixtures da suite E2E offline (sem rede, sem SDK real)."""
from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner.runner.sdk_adapter import SDKRequest, SDKResponse
from governance_runner.synth import exporter
from governance_runner.synth.golden import GOLDEN_REL_PATH, resolver_caminho_golden
from governance_runner.synth.storage import SynthRepository


class ClienteFalso:
    """Dublê offline: sempre delega para 'bug-triage' via tool_hook (gera falhas)."""

    def __init__(self) -> None:
        self.requests: list[SDKRequest] = []

    def invoke(self, request: SDKRequest) -> SDKResponse:
        self.requests.append(request)
        return SDKResponse(achados=(), premium_requests_consumidos=1, texto="",
                           tool_events=({"tool": "delegar", "para": "@bug-triage"},))


@pytest.fixture
def cliente_falso() -> ClienteFalso:
    return ClienteFalso()


@pytest.fixture
def allow_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    raiz = tmp_path / "synthetic"
    monkeypatch.setattr(exporter, "_allow_root_padrao", lambda: raiz)
    return raiz


@pytest.fixture
def router_md(tmp_path: Path) -> Path:
    p = tmp_path / "router.agent.md"
    p.write_text("---" + chr(10) + "name: agent-router" + chr(10) + "---" + chr(10) + "router" + chr(10), encoding="utf-8")
    return p


@pytest.fixture
def golden_path() -> Path:
    caminho = resolver_caminho_golden()
    assert caminho.as_posix().endswith(GOLDEN_REL_PATH.as_posix())
    return caminho


@pytest.fixture
def repo(tmp_path: Path):  # type: ignore[no-untyped-def]
    r = SynthRepository(tmp_path / "e2e.db", repo_root=tmp_path)
    r.migrar()
    yield r
    r.close()
