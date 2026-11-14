"""Allowlist (pinnable/status/frescor) e regra D6 pai>=filho via cost_rank.
Contrato: ver tests/model_profiles/__init__.py."""
from __future__ import annotations

import datetime as dt

import pytest

from ._helpers import (ECON_WARNING, FLASH, HAIKU, OPUS, SONNET, add_profile, edit_allowlist,
                       git, load, read_state, run_cli)

AGENTS = ".github/agents/"


def _unchanged(repo, originals):
    return all((repo / r).read_bytes() == b for r, b in originals.items())


# ------------------------------------------------------------------ D6 unitario
@pytest.mark.parametrize("parent_rank,child_rank,violates", [
    (4, 4, False), (4, 3, False), (4, 5, True), (1, 6, True), (6, 1, False),
])
def test_find_violations_fronteira_cost_rank(parent_rank, child_rank, violates):
    h = load("hierarchy")
    ranks = {"P": parent_rank, "C": child_rank}
    out = h.find_violations([("p", "c")], {"p": "P", "c": "C"}, ranks)
    assert [(v.parent, v.child, v.kind) for v in out] == (
        [("p", "c", "cost_hierarchy")] if violates else [])


def test_find_violations_excecao_por_model_exception_reason():
    h = load("hierarchy")
    args = ([("p", "c")], {"p": "P", "c": "C"}, {"P": 1, "C": 6})
    assert h.find_violations(*args, exceptions={"c"}) == []
    assert len(h.find_violations(*args, exceptions={"p"})) == 1  # excecao e do FILHO


@pytest.mark.parametrize("ranks", [{"P": None, "C": 3}, {"P": 3, "C": None}])
def test_find_violations_cost_rank_null_e_nao_verificavel(ranks):
    h = load("hierarchy")
    out = h.find_violations([("p", "c")], {"p": "P", "c": "C"}, ranks)
    assert [v.kind for v in out] == ["cost_rank_unverifiable"]


def test_load_edges_le_arestas_do_routing_graph(repo):
    h = load("hierarchy")
    edges = h.load_edges(repo / ".github/agents/routing-graph.yaml")
    assert ("agent-router", "python-developer") in edges
    assert ("agent-router", "tech-solution-architect") in edges


# ------------------------------------------------------------------ D6 via CLI
def test_economico_rebaixa_router_e_orquestrador_e_passa_d6(repo, capsys, originals):
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 0, out
    router = (repo / AGENTS / "agent-router.agent.md").read_bytes()
    assert f'model: "{HAIKU}"'.encode() in router
    assert "[COST_HIERARCHY]" not in out  # TSA (Sonnet > Haiku) isento por model_exception_reason


def test_apply_recusa_perfil_que_viola_hierarquia(repo, capsys, originals):
    add_profile(repo, "invertido", {"extends": "default", "description": "ruim", "tiers": {
        "orchestration": HAIKU, "standard": OPUS}})
    code, out = run_cli(capsys, repo, "apply", "invertido", "--yes")
    assert code == 1 and "[COST_HIERARCHY]" in out
    assert _unchanged(repo, originals)
    assert not (repo / ".model-profiles/state.json").exists()


def test_excecao_so_vale_com_model_exception_reason(repo, capsys):
    path = repo / AGENTS / "tech-solution-architect.agent.md"
    data = path.read_bytes()
    lines = [ln for ln in data.split(b"\n") if not ln.startswith(b"model_exception_reason")]
    path.write_bytes(b"\n".join(lines))
    git(repo, "commit", "-qam", "remove excecao")
    code, out = run_cli(capsys, repo, "doctor")
    assert code == 1 and "[COST_HIERARCHY]" in out


def test_doctor_com_excecao_presente_nao_reporta_d6(repo, capsys):
    code, out = run_cli(capsys, repo, "doctor")
    assert code == 0, out
    assert "[COST_HIERARCHY]" not in out


# ------------------------------------------------------------------ allowlist
@pytest.mark.parametrize("model,tag", [
    ("Auto", "[NOT_PINNABLE]"), ("Retired Model 1", "[RETIRED]"),
    ("Modelo Fantasma 9", "[UNKNOWN_MODEL]"),
])
def test_apply_recusa_modelo_fora_da_allowlist(repo, capsys, originals, model, tag):
    add_profile(repo, "ruim", {"extends": "default", "description": "x",
                               "tiers": {"light": model}})
    code, out = run_cli(capsys, repo, "apply", "ruim", "--yes")
    assert code == 1 and tag in out
    assert _unchanged(repo, originals)


@pytest.mark.parametrize("model,tag", [("Deprecated Model 1", "[DEPRECATED]"),
                                       ("Sunset Model 1", "[RETIREMENT_SOON]")])
def test_apply_avisa_mas_permite_deprecated_ou_aposentadoria_proxima(repo, capsys, model, tag):
    add_profile(repo, "aviso", {"extends": "default", "description": "x",
                                "tiers": {"light": model}})
    code, out = run_cli(capsys, repo, "apply", "aviso", "--yes")
    assert code == 0 and tag in out


def test_retirement_date_fora_da_janela_de_30_dias_nao_avisa(repo, capsys):
    def far(d):
        for m in d["models"]:
            if m["name"] == "Sunset Model 1":
                m["retirement_date"] = (dt.date.today() + dt.timedelta(days=31)).isoformat()
    edit_allowlist(repo, far)
    add_profile(repo, "aviso", {"extends": "default", "description": "x",
                                "tiers": {"light": "Sunset Model 1"}})
    code, out = run_cli(capsys, repo, "apply", "aviso", "--yes")
    assert code == 0 and "[RETIREMENT_SOON]" not in out


@pytest.mark.parametrize("age_days,stale", [(30, False), (31, True), (400, True)])
def test_frescor_da_allowlist_doctor_e_status(repo, capsys, age_days, stale):
    def age(d):
        d["verified_at"] = (dt.date.today() - dt.timedelta(days=age_days)).isoformat()
    edit_allowlist(repo, age)
    for cmd in ("doctor", "status"):
        code, out = run_cli(capsys, repo, cmd)
        assert code == 0, out  # aviso nao reprova
        assert ("[ALLOWLIST_STALE]" in out) is stale


@pytest.fixture
def norank_profile(repo):
    add_profile(repo, "semrank", {"extends": "default", "description": "x",
                                  "tiers": {"standard": "NoRank Model 1"}})


def test_cost_rank_null_doctor_avisa(repo, capsys, norank_profile):
    code, out = run_cli(capsys, repo, "doctor")
    assert "[COST_RANK_NULL]" in out


def test_cost_rank_null_yes_sozinho_nao_basta(repo, capsys, originals, norank_profile):
    code, out = run_cli(capsys, repo, "apply", "semrank", "--yes")
    assert code == 1 and "[COST_RANK_NULL]" in out
    assert _unchanged(repo, originals)


def test_cost_rank_null_aceita_confirmacao_reforcada(repo, capsys, monkeypatch, norank_profile):
    monkeypatch.setattr("builtins.input", lambda prompt="": "CONFIRMAR")
    code, out = run_cli(capsys, repo, "apply", "semrank")
    assert code == 0, out
    assert read_state(repo)["phase"] == "applied"
