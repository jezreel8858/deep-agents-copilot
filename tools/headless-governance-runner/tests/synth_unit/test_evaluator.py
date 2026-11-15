from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import SDKResponse
from governance_runner.synth.evaluator import avaliar_lote, capturar_rota, carregar_router_agent, pontuar
from governance_runner.synth.storage import SynthRepository

from .conftest import FakeSDKClient, resposta_hook


def _resp(texto: str = "", eventos: tuple[dict[str, object], ...] = ()) -> SDKResponse:
    return SDKResponse(achados=(), premium_requests_consumidos=1, texto=texto, tool_events=eventos)


def test_captura_tool_hook() -> None:
    assert capturar_rota(resposta_hook("@python-developer")) == ("python-developer", "tool_hook")


def test_captura_tool_hook_via_arguments() -> None:
    r = _resp(eventos=({"tool": "delegar", "arguments": {"para": "@Bug-Triage"}},))
    assert capturar_rota(r) == ("bug-triage", "tool_hook")


@pytest.mark.parametrize("chave", ["Delegado", "Rota", "Agente Ativo"])
def test_captura_text_banner(chave: str) -> None:
    assert capturar_rota(_resp(texto=chave + ": @docs-engineer")) == ("docs-engineer", "text_banner")


def test_hook_tem_precedencia_sobre_banner() -> None:
    r = _resp(texto="Delegado: @a-b", eventos=({"tool": "delegar", "para": "@c-d"},))
    assert capturar_rota(r) == ("c-d", "tool_hook")


@pytest.mark.parametrize(
    "texto", ["", "sem rota alguma", "Agente Ativo: agent-router", "Delegado:"]
)
def test_unparseable_nunca_inventa_rota(texto: str) -> None:
    assert capturar_rota(_resp(texto=texto)) == (None, None)


def test_evento_de_outra_tool_ignorado() -> None:
    assert capturar_rota(_resp(eventos=({"tool": "bash", "para": "x"},))) == (None, None)


@pytest.mark.parametrize(
    ("obs", "exp", "esperado"),
    [
        ("a", "@a", ("matched", True)),
        ("a", "b", ("mismatched", False)),
        (None, "a", ("unparseable", False)),
    ],
)
def test_pontuar(obs: str | None, exp: str, esperado: tuple[str, bool]) -> None:
    assert pontuar(obs, exp) == esperado


def test_carregar_router_remove_frontmatter_e_calcula_sha(router_md: Path) -> None:
    corpo, sha = carregar_router_agent(router_md)
    assert "name: agent-router" not in corpo and "router" in corpo and len(sha) == 64


def _preparar(repo: SynthRepository, semear, n: int = 3) -> None:  # type: ignore[no-untyped-def]
    rid = repo.criar_run(kind="generate", generator="template")
    for i in range(n):
        semear(repo, rid, "pedido numero " + str(i))


def test_avaliacao_cega_sem_vazamento_de_expected_route(repo, semear, router_md) -> None:  # type: ignore[no-untyped-def]
    _preparar(repo, semear)
    cli = FakeSDKClient(default=resposta_hook("python-developer"))
    rel = avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=10), router_agent_path=router_md)
    assert rel.n_avaliados == 3 and len(cli.requests) == 3
    for req in cli.requests:
        assert "zz-secret-route" not in req.prompt
        assert "zz-secret-route" not in (req.system_prompt or "")
        assert req.ferramentas_permitidas == ("delegar",)
        assert req.permission_handler("read_file", {"path": "a"}).permitido is False
    assert {r.prompt for r in cli.requests} == {"pedido numero " + str(i) for i in range(3)}


def test_veredictos_e_route_source_persistidos(repo, semear, router_md) -> None:  # type: ignore[no-untyped-def]
    rid = repo.criar_run(kind="generate", generator="template")
    semear(repo, rid, "a", rota="alvo")
    semear(repo, rid, "b", rota="alvo")
    semear(repo, rid, "c", rota="alvo")
    cli = FakeSDKClient(respostas=[resposta_hook("alvo"), _resp(texto="Rota: @outro"), _resp(texto="nada")])
    rel = avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=10),
                       router_agent_path=router_md, run_id="ev1")
    assert (rel.n_passed, rel.n_unparseable) == (1, 1)
    por_texto = {e["prompt_text"]: e for e in repo.listar_avaliacoes("ev1")}
    assert por_texto["a"]["route_source"] == "tool_hook" and por_texto["a"]["verdict"] == "matched"
    assert por_texto["b"]["route_source"] == "text_banner" and por_texto["b"]["verdict"] == "mismatched"
    assert por_texto["c"]["route_source"] is None and por_texto["c"]["verdict"] == "unparseable"


def test_orcamento_estourado_encerra_neutral(repo, semear, router_md) -> None:  # type: ignore[no-untyped-def]
    _preparar(repo, semear)
    cli = FakeSDKClient(default=resposta_hook("x", custo=1))
    rel = avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=1), router_agent_path=router_md)
    assert (rel.status, rel.motivo) == ("neutral", "budget_exhausted")
    assert rel.n_avaliados == 1 and len(cli.requests) == 1


def test_orcamento_zero_nao_invoca_cliente(repo, semear, router_md) -> None:  # type: ignore[no-untyped-def]
    _preparar(repo, semear)
    cli = FakeSDKClient()
    rel = avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=0), router_agent_path=router_md)
    assert rel.n_avaliados == 0 and cli.requests == [] and rel.status == "neutral"


def test_erro_do_cliente_nao_aborta_lote(repo, semear, router_md) -> None:  # type: ignore[no-untyped-def]
    _preparar(repo, semear, 2)
    cli = FakeSDKClient(erro=RuntimeError("falha"))
    rel = avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=5),
                       router_agent_path=router_md, run_id="ev-err")
    assert rel.n_errors == 2 and rel.n_avaliados == 2
    assert {e["verdict"] for e in repo.listar_avaliacoes("ev-err")} == {"error"}


def test_avaliacao_retomavel_nao_reavalia(repo, semear, router_md) -> None:  # type: ignore[no-untyped-def]
    _preparar(repo, semear, 2)
    cli = FakeSDKClient(default=resposta_hook("x"))
    avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=9), router_agent_path=router_md, run_id="r")
    avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=9), router_agent_path=router_md, run_id="r")
    assert len(cli.requests) == 2


def test_limit_respeitado(repo, semear, router_md) -> None:  # type: ignore[no-untyped-def]
    _preparar(repo, semear, 3)
    cli = FakeSDKClient(default=resposta_hook("x"))
    rel = avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=9),
                       router_agent_path=router_md, limit=1)
    assert rel.n_avaliados == 1
