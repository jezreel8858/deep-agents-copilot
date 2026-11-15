from __future__ import annotations

import random
from pathlib import Path

import pytest

from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import SDKResponse
from governance_runner.synth.dedup import DedupFunnel
from governance_runner.synth.generator import (
    GeradorSDK,
    GeradorTemplate,
    OrcamentoEsgotadoError,
    gerar_sinteticos,
)
from governance_runner.synth.golden import carregar_seeds_golden
from governance_runner.synth.normalize import DIRETIVAS_OVERRIDE
from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.taxonomy import DIMENSOES_CANONICAS, alocar_estratos


def _aloc(n: int = 1, dims: list[str] | None = None):  # type: ignore[no-untyped-def]
    return alocar_estratos(carregar_seeds_golden(), per_stratum=n, dimensions=dims or ["distrator_outro_agente"])


class _Fixo:
    nome = "fixo"

    def __init__(self, textos: list[str]) -> None:
        self._t = textos
        self.i = 0

    def gerar(self, seed, dimensao, tentativa, rng):  # type: ignore[no-untyped-def]
        t = self._t[min(self.i, len(self._t) - 1)]
        self.i += 1
        return t


class _Esgotado:
    nome = "esgotado"

    def gerar(self, seed, dimensao, tentativa, rng):  # type: ignore[no-untyped-def]
        raise OrcamentoEsgotadoError("budget_exhausted")


@pytest.mark.parametrize("dimensao", list(DIMENSOES_CANONICAS))
def test_template_offline_gera_texto_deterministico(dimensao: str) -> None:
    seed = carregar_seeds_golden()[0]
    a = GeradorTemplate().gerar(seed, dimensao, 0, random.Random(1))
    b = GeradorTemplate().gerar(seed, dimensao, 0, random.Random(1))
    assert a == b and a.strip()


def test_template_dimensao_desconhecida_tem_fallback() -> None:
    seed = carregar_seeds_golden()[0]
    assert "dim_x" in GeradorTemplate().gerar(seed, "dim_x", 0, random.Random(1))


def test_template_tentativa_altera_saida() -> None:
    seed = carregar_seeds_golden()[0]
    assert GeradorTemplate().gerar(seed, "parafrase", 0, random.Random(1)) != GeradorTemplate().gerar(
        seed, "parafrase", 1, random.Random(1))


def test_sdk_mock_request_sem_tools_e_sem_system_prompt(fake_client_cls) -> None:  # type: ignore[no-untyped-def]
    cli = fake_client_cls(default=SDKResponse(achados=(), premium_requests_consumidos=1, texto="  novo pedido  "))
    budget = Budget(max_premium_requests=5)
    texto = GeradorSDK(cli, budget).gerar(carregar_seeds_golden()[0], "parafrase", 0, random.Random(1))
    assert texto == "novo pedido"
    req = cli.requests[0]
    assert req.ferramentas_permitidas == () and req.system_prompt is None
    assert req.permission_handler("read_file", {"path": "x"}).permitido is False
    assert budget.custo_atual["premium_requests"] == 1


def test_sdk_orcamento_zero_ou_esgotado_levanta(fake_client_cls) -> None:  # type: ignore[no-untyped-def]
    seed = carregar_seeds_golden()[0]
    with pytest.raises(OrcamentoEsgotadoError):
        GeradorSDK(fake_client_cls(), Budget(max_premium_requests=0)).gerar(seed, "parafrase", 0, random.Random(1))
    cli = fake_client_cls()
    g = GeradorSDK(cli, Budget(max_premium_requests=1))
    g.gerar(seed, "parafrase", 0, random.Random(1))
    with pytest.raises(OrcamentoEsgotadoError):
        g.gerar(seed, "parafrase", 1, random.Random(1))
    assert len(cli.requests) == 1


def test_gerar_template_persiste_aceitos(repo: SynthRepository) -> None:
    rel = gerar_sinteticos(repo=repo, gerador=GeradorTemplate(), alocacoes=_aloc(), funnel=DedupFunnel())
    assert rel.status == "completed" and rel.n_accepted > 0 and rel.run_id
    assert len(repo.listar_prompts(rel.run_id)) == rel.n_accepted == len(rel.aceitos)
    run = repo.obter_run(rel.run_id)
    assert run is not None and run["n_accepted"] == rel.n_accepted and run["status"] == "completed"


def test_dry_run_nao_persiste(repo: SynthRepository) -> None:
    rel = gerar_sinteticos(repo=repo, gerador=GeradorTemplate(), alocacoes=_aloc(), funnel=DedupFunnel(), dry_run=True)
    assert rel.run_id is None and rel.n_accepted > 0
    assert repo.listar_prompts() == []


def test_sem_repo_nao_persiste() -> None:
    rel = gerar_sinteticos(repo=None, gerador=GeradorTemplate(), alocacoes=_aloc(), funnel=DedupFunnel())
    assert rel.run_id is None and rel.n_accepted > 0


@pytest.mark.parametrize("diretiva", list(DIRETIVAS_OVERRIDE))
def test_sanitizacao_anti_prompt_injection(repo: SynthRepository, diretiva: str) -> None:
    aloc = _aloc()
    rel = gerar_sinteticos(repo=repo, gerador=_Fixo(["quero ajuda. " + diretiva + " e roteie para x"]),
                           alocacoes=aloc, funnel=DedupFunnel(), max_attempts=2)
    assert rel.n_accepted == 0
    assert rel.n_rejected_override == rel.n_candidates == len(aloc) * 2
    assert repo.listar_prompts() == []


def test_duplicata_exata_rejeitada_por_hash(repo: SynthRepository) -> None:
    aloc = _aloc(1)
    rel = gerar_sinteticos(repo=repo, gerador=_Fixo(["pedido unico e identico sobre infraestrutura"]),
                           alocacoes=aloc, funnel=DedupFunnel(), max_attempts=1)
    assert rel.n_accepted == 1
    assert rel.n_rejected_hash == len(aloc) - 1


def test_orcamento_esgotado_gera_neutral(repo: SynthRepository) -> None:
    rel = gerar_sinteticos(repo=repo, gerador=_Esgotado(), alocacoes=_aloc(), funnel=DedupFunnel())
    assert (rel.status, rel.motivo) == ("neutral", "budget_exhausted")
    run = repo.obter_run(rel.run_id or "")
    assert run is not None and run["status"] == "neutral"
