"""Fixtures compartilhadas da suite tests/synth_unit (B1-07 / B2-06 / B3-06)."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from governance_runner.runner.sdk_adapter import SDKRequest, SDKResponse
from governance_runner.synth.storage import SynthRepository

ROUTER_MD = "---" + chr(10) + "name: agent-router" + chr(10) + "---" + chr(10) + "Voce e o router." + chr(10)


class FakeSDKClient:
    """Dublê de CopilotSDKClient: registra requests e devolve respostas programadas."""

    def __init__(self, respostas: list[SDKResponse] | None = None, default: SDKResponse | None = None,
                 erro: Exception | None = None) -> None:
        self.requests: list[SDKRequest] = []
        self._respostas = list(respostas or [])
        self._default = default or SDKResponse(achados=(), premium_requests_consumidos=1, texto="")
        self._erro = erro

    def invoke(self, request: SDKRequest) -> SDKResponse:
        self.requests.append(request)
        if self._erro is not None:
            raise self._erro
        if self._respostas:
            return self._respostas.pop(0)
        return self._default


def resposta_hook(destino: str, custo: int = 1) -> SDKResponse:
    return SDKResponse(
        achados=(), premium_requests_consumidos=custo, texto="",
        tool_events=({"tool": "delegar", "para": destino},),
    )


@pytest.fixture
def repo(tmp_path: Path) -> Iterator[SynthRepository]:
    r = SynthRepository(tmp_path / "synth.db", repo_root=tmp_path)
    r.migrar()
    yield r
    r.close()


@pytest.fixture
def router_md(tmp_path: Path) -> Path:
    p = tmp_path / "router.agent.md"
    p.write_text(ROUTER_MD, encoding="utf-8")
    return p


@pytest.fixture
def fake_client_cls() -> type[FakeSDKClient]:
    return FakeSDKClient


def semear_prompt(repo: SynthRepository, run_id: str, texto: str, rota: str = "zz-secret-route",
                  sha: str | None = None, similarity: float = 0.0) -> str:
    return repo.inserir_prompt(
        run_id=run_id, text=texto, text_norm=texto.lower(), sha256=sha or ("sha-" + texto),
        expected_route=rota, agente_alvo="python-developer", dimensao_perturbacao="parafrase",
        max_similarity=similarity,
    )


@pytest.fixture
def semear() -> Any:
    return semear_prompt
