"""Aceite B3 (plano §9): metricas/sugestoes de workflow, golden do relatorio, regressao de arestas, ordem SUG-WF-*."""
from __future__ import annotations

import os
import random
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from governance_runner.synth.diagnostic_exporter import (
    renderizar_diagnostico_md,
    renderizar_diagnostico_yaml,
    serializar_diagnostico_dict,
)
from governance_runner.synth.diagnostics import (
    CODIGOS_SUGESTAO,
    LIMIAR_F1_WORKFLOW,
    diagnosticar_avaliacao,
)
from governance_runner.synth.routing_graph import GrafoSnapshot, RotaGrafo, WorkflowGrafo
from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.use_cases import executar_synth_diagnose

GOLDEN_DIR = Path(__file__).parent / "golden"
RUN_INFO = {"run_id": "run-wf", "kind": "eval", "finished_at": "2026-11-15T15:00:00+00:00"}
WF_A, WF_B, WF_C, WF_D = "WORKFLOW-BUG-FIX", "WORKFLOW-REFACTORING", "WORKFLOW-NOGATILHO", "WORKFLOW-FEATURE-DEVELOPMENT"


def _rota(eid: str, para: str, kws: tuple[str, ...]) -> RotaGrafo:
    return RotaGrafo(edge_id=eid, de="agent-router", para=para, tipo="keyword_based", regra=None,
                     prioridade=1.0, threshold_score=0.7, nivel_routing="L1", keywords=kws)


def _wf(wid: str, gat: tuple[str, ...], padroes: tuple[str, ...]) -> WorkflowGrafo:
    return WorkflowGrafo(workflow_id=wid, nome=wid.lower(), fast_path=True, gatilhos_norm=gat,
                         etapa1_padroes=padroes, workflow_hash="h" * 64, gatilhos=gat)


def _snap(com_workflows: bool = True) -> GrafoSnapshot:
    rotas = (
        _rota("e-aaaa00000001", "bug-triage", ("erro", "bug")),
        _rota("e-bbbb00000002", "business-rules-extractor", ("refatorar",)),
    )
    wfs = (
        (
            _wf(WF_A, ("erro", "falha critica"), ("bug-triage",)),
            _wf(WF_B, ("erro", "refatorar"), ("business-rules-extractor",)),
            _wf(WF_C, (), ("bug-triage",)),
            _wf(WF_D, ("criar feature",), ("prompt-structuring",)),
        )
        if com_workflows
        else ()
    )
    return GrafoSnapshot(sha256="1" * 64, rotas=rotas, nos=frozenset({"bug-triage", "business-rules-extractor", "agent-router"}),
                         todas_rotas=rotas, workflows=wfs)


def _ev(i: int, exp_route: str, obs_route: str | None, **wf: object) -> dict:
    base = {
        "eval_id": f"ev-{i:02d}", "prompt_id": f"p-{i:02d}", "expected_route": exp_route, "observed_route": obs_route,
        "verdict": "matched" if exp_route == obs_route else ("unparseable" if obs_route is None else "mismatched"),
        "passed": 1 if exp_route == obs_route else 0, "seed_source": "routing_graph",
        "graph_edge_id": "e-aaaa00000001" if exp_route == "bug-triage" else "e-bbbb00000002",
        "prompt_text": f"prompt {i}",
    }
    base.update(wf)
    return base


def _evals_wf() -> list[dict]:
    return [
        # BUG-FIX esperado 3x, observado REFACTORING (recall 0, FP para REFACTORING)
        _ev(1, "bug-triage", "business-rules-extractor", expected_workflow=WF_A, observed_workflow=WF_B, workflow_source="text_banner", workflow_route_consistent=1),
        _ev(2, "bug-triage", "business-rules-extractor", expected_workflow=WF_A, observed_workflow=WF_B, workflow_source="text_banner", workflow_route_consistent=1),
        _ev(3, "bug-triage", "feature-planner", expected_workflow=WF_A, observed_workflow=WF_A, workflow_source="text_banner", workflow_route_consistent=0),
        _ev(4, "bug-triage", "feature-planner", expected_workflow=WF_A, observed_workflow=WF_A, workflow_source="text_banner", workflow_route_consistent=0),
        # REFACTORING esperado 2x, 1 acerto, 1 sem banner
        _ev(5, "business-rules-extractor", "business-rules-extractor", expected_workflow=WF_B, observed_workflow=WF_B, workflow_source="text_banner", workflow_route_consistent=1),
        _ev(6, "business-rules-extractor", "business-rules-extractor", expected_workflow=WF_B, workflow_source="none"),
        # ID desconhecido
        _ev(7, "bug-triage", "bug-triage", expected_workflow=WF_A, workflow_source="invalid_id"),
        # legado (sem workflow)
        _ev(8, "bug-triage", "bug-triage"),
    ]


def _diag(snap: GrafoSnapshot, evals: list[dict], **kw: object):  # type: ignore[no-untyped-def]
    return diagnosticar_avaliacao(
        eval_run_id="run-wf", run_info=RUN_INFO, avaliacoes=evals, snapshot=snap,
        router_md_texto="@bug-triage @business-rules-extractor", router_agent_sha256="2" * 64,
        golden_set_sha256="3" * 64, min_support=2, **kw,  # type: ignore[arg-type]
    )


# ----------------------------------------------------------- metricas de workflow
def test_metricas_workflow_precision_recall_f1_macro_e_matriz() -> None:
    d = _diag(_snap(), _evals_wf())
    m = {x.workflow_id: x for x in d.por_workflow}
    assert set(m) == {WF_A, WF_B, WF_C, WF_D}
    a, b = m[WF_A], m[WF_B]
    assert (a.suporte, a.tp, a.fp, a.fn) == (5, 2, 0, 3)
    assert a.precision == 1.0 and a.recall == pytest.approx(0.4)
    assert (b.suporte, b.tp, b.fp, b.fn) == (2, 1, 2, 1)
    assert b.precision == pytest.approx(1 / 3, abs=1e-6) and b.recall == 0.5
    assert b.f1 == pytest.approx(0.4, abs=1e-6)
    assert m[WF_C].precision is None and m[WF_C].recall is None and m[WF_C].f1 is None  # sem dados: nao inventa 0
    assert d.resumo.workflow_accuracy == pytest.approx(3 / 7)
    assert d.resumo.workflow_macro_f1 == pytest.approx((a.f1 + b.f1) / 2, abs=1e-6)  # so quem tem suporte/FP
    assert d.resumo.workflow_route_consistency_rate == pytest.approx(3 / 5)  # NULL excluido do denominador
    assert d.matriz_confusao_workflow[WF_A] == {WF_A: 2, WF_B: 2, "<none>": 1}
    assert d.matriz_confusao_workflow[WF_B] == {WF_B: 1, "<none>": 1}
    assert WF_C not in d.matriz_confusao_workflow


def test_colisoes_de_gatilhos_entre_workflows() -> None:
    d = _diag(_snap(), _evals_wf())
    exatas = [c for c in d.colisoes_workflow if c.tipo == "exata"]
    assert [(c.gatilho_norm, c.workflows) for c in exatas] == [("erro", (WF_A, WF_B))]
    # gatilho "erro" tambem e keyword da aresta -> bug-triage; para WF_B (etapa1 != bug-triage) e colisao gatilho x aresta
    assert any(c.tipo == "gatilho_aresta" and WF_B in c.workflows for c in d.colisoes_workflow)


def test_sugestoes_workflow_codigos_e_ordem_estavel() -> None:
    d = _diag(_snap(), _evals_wf())
    wf_sugs = [s for s in d.sugestoes if s.codigo.startswith("SUG-WF-")]
    codigos = [s.codigo for s in wf_sugs]
    assert set(codigos) == {
        "SUG-WF-COLLISION", "SUG-WF-LOW-RECALL", "SUG-WF-LOW-PRECISION", "SUG-WF-INCONSISTENT-ROUTE",
        "SUG-WF-MISSING-BANNER", "SUG-WF-UNKNOWN-ID", "SUG-WF-UNCOVERABLE",
    }
    assert set(codigos) <= set(CODIGOS_SUGESTAO)
    ordem = list(CODIGOS_SUGESTAO)
    ordem_real = [c for c in ordem if c in codigos]
    # dentro do bloco SUG-WF-* a ordem de emissao segue a ordem do contrato (§4)
    primeiro = {c: codigos.index(c) for c in set(codigos)}
    assert sorted(primeiro, key=primeiro.get) == ordem_real  # type: ignore[arg-type]
    unc = [s for s in wf_sugs if s.codigo == "SUG-WF-UNCOVERABLE"]
    assert len(unc) == 1 and WF_C in unc[0].alvo_ancora


def test_ordem_sug_wf_deterministica_sob_permutacao_de_entradas() -> None:
    snap = _snap()
    evals = _evals_wf()
    ref = _diag(snap, evals)
    ref_sug = [(s.codigo, s.alvo_ancora) for s in ref.sugestoes]
    ref_yaml = renderizar_diagnostico_yaml(ref)
    rng = random.Random(1234)
    for _ in range(5):
        ev2 = evals[:]
        rng.shuffle(ev2)
        wf2 = list(snap.workflows)
        rng.shuffle(wf2)
        d2 = _diag(replace(snap, workflows=tuple(wf2)), ev2)
        assert [(s.codigo, s.alvo_ancora) for s in d2.sugestoes] == ref_sug
        assert renderizar_diagnostico_yaml(d2) == ref_yaml


@pytest.mark.parametrize(
    ("recall_tp", "recall_fn", "esperado"),
    [(2, 3, True), (7, 3, False), (1, 0, False)],
)
def test_low_recall_fronteira_limiar_e_suporte_minimo(recall_tp: int, recall_fn: int, esperado: bool) -> None:
    """recall exatamente no limiar (0.7) nao dispara; suporte abaixo de min_support nao dispara."""
    evs = []
    for i in range(recall_tp):
        evs.append(_ev(i, "bug-triage", "bug-triage", expected_workflow=WF_A, observed_workflow=WF_A, workflow_source="text_banner"))
    for i in range(recall_fn):
        evs.append(_ev(100 + i, "bug-triage", "bug-triage", expected_workflow=WF_A, observed_workflow=WF_D, workflow_source="text_banner"))
    d = _diag(_snap(), evs)
    disparou = any(s.codigo == "SUG-WF-LOW-RECALL" and WF_A in s.alvo_ancora for s in d.sugestoes)
    assert disparou is esperado
    assert LIMIAR_F1_WORKFLOW == 0.7


def test_recall_exatamente_no_limiar_nao_dispara() -> None:
    evs = [_ev(i, "bug-triage", "bug-triage", expected_workflow=WF_A, observed_workflow=WF_A, workflow_source="text_banner") for i in range(7)]
    evs += [_ev(50 + i, "bug-triage", "bug-triage", expected_workflow=WF_A, observed_workflow=WF_D, workflow_source="text_banner") for i in range(3)]
    d = _diag(_snap(), evs)
    assert next(m for m in d.por_workflow if m.workflow_id == WF_A).recall == pytest.approx(0.7)
    assert not any(s.codigo == "SUG-WF-LOW-RECALL" and WF_A in s.alvo_ancora for s in d.sugestoes)


# ------------------------------------------- regressao: metricas de arestas intactas
def _snapshot_de_arestas() -> tuple[GrafoSnapshot, list[dict]]:
    snap = _snap(com_workflows=False)
    evs = [_ev(i, "bug-triage", "bug-triage" if i % 2 else "business-rules-extractor") for i in range(1, 7)]
    return snap, evs


def test_metricas_de_arestas_inalteradas_com_ou_sem_workflows() -> None:
    snap0, evs = _snapshot_de_arestas()
    d0 = _diag(snap0, evs)
    d1 = _diag(_snap(True), evs)  # mesmas avaliacoes, grafo com workflows e sem dados de workflow
    assert d0.por_aresta == d1.por_aresta
    assert d0.matriz_confusao == d1.matriz_confusao
    assert d0.resumo.acuracia_global == d1.resumo.acuracia_global
    assert d0.resumo.total_avaliacoes == d1.resumo.total_avaliacoes == 6
    assert d0.orfas == d1.orfas
    assert d0.colisoes == d1.colisoes
    nao_wf = lambda d: [(s.codigo, s.alvo_ancora) for s in d.sugestoes if not s.codigo.startswith("SUG-WF-")]  # noqa: E731
    assert nao_wf(d0) == nao_wf(d1)
    # e dados de workflow nao alteram as metricas de aresta
    d2 = _diag(_snap(True), _evals_wf())
    d3 = _diag(_snap(True), [{k: v for k, v in e.items() if "workflow" not in k} for e in _evals_wf()])
    assert d2.por_aresta == d3.por_aresta and d2.matriz_confusao == d3.matriz_confusao


def test_sem_dados_de_workflow_sem_sugestoes_de_dados() -> None:
    snap0, evs = _snapshot_de_arestas()
    d0 = _diag(snap0, evs)
    assert d0.por_workflow == () and d0.colisoes_workflow == () and d0.matriz_confusao_workflow == {}
    assert not any(s.codigo.startswith("SUG-WF-") for s in d0.sugestoes)
    assert d0.resumo.workflow_macro_f1 is None and d0.resumo.workflow_route_consistency_rate is None


# ----------------------------------------------- secao 'Workflows' ausente sem dados
def test_secao_workflows_ausente_sem_dados_e_presente_com_dados() -> None:
    snap0, evs = _snapshot_de_arestas()
    d0 = _diag(snap0, evs)
    md0, y0 = renderizar_diagnostico_md(d0), renderizar_diagnostico_yaml(d0)
    assert "## Workflows" not in md0
    assert "Gatilhos de Workflows" not in md0
    assert "workflows" not in yaml.safe_load(y0)
    assert "workflows" not in serializar_diagnostico_dict(d0)

    d1 = _diag(_snap(), _evals_wf())
    md1, y1 = renderizar_diagnostico_md(d1), renderizar_diagnostico_yaml(d1)
    assert "## Workflows" in md1 and "Gatilhos de Workflows" in md1
    bloco = yaml.safe_load(y1)["workflows"]
    assert "workflow_macro_f1" in str(bloco) or "metricas" in bloco or bloco


# --------------------------------------------------------------- golden do relatorio
def _comparar_golden(nome: str, atual: str) -> None:
    alvo = GOLDEN_DIR / nome
    if os.environ.get("SYNTH_UPDATE_GOLDEN") == "1":
        alvo.write_bytes(atual.encode("utf-8"))
    assert alvo.exists(), f"golden ausente: {alvo} (gerar com SYNTH_UPDATE_GOLDEN=1)"
    assert alvo.read_bytes().decode("utf-8") == atual


def test_golden_relatorio_md_e_yaml_com_workflows() -> None:
    d = _diag(_snap(), _evals_wf())
    _comparar_golden("diagnostic_workflows.md", renderizar_diagnostico_md(d))
    _comparar_golden("diagnostic_workflows.yaml", renderizar_diagnostico_yaml(d))


def test_golden_relatorio_sem_workflows_e_estavel_e_sem_secao() -> None:
    snap0, evs = _snapshot_de_arestas()
    d = _diag(snap0, evs)
    _comparar_golden("diagnostic_edges_only.md", renderizar_diagnostico_md(d))


# --------------------------------------------- use case: persistencia e RelatorioSynth
def test_executar_synth_diagnose_registra_workflows_e_preenche_relatorio(tmp_path: Path, repo: SynthRepository, router_md: Path) -> None:
    rid = repo.criar_run(kind="generate", generator="template")
    eid = "ev-uc"
    repo.criar_run(kind="eval", run_id=eid)
    for i in range(4):
        pid = repo.inserir_prompt(run_id=rid, text=f"t{i}", text_norm=f"t{i}", sha256=f"s{i}", expected_route="bug-triage",
                                  agente_alvo="bug-triage", dimensao_perturbacao="parafrase",
                                  expected_workflow="WORKFLOW-BUG-FIX", graph_workflow_id="WORKFLOW-BUG-FIX")
        repo.inserir_avaliacao(run_id=eid, prompt_id=pid, observed_route="bug-triage", route_source="text_banner",
                               verdict="matched", passed=True,
                               observed_workflow="WORKFLOW-BUG-FIX" if i < 3 else "WORKFLOW-REFACTORING",
                               workflow_source="text_banner", workflow_route_consistent=1 if i < 3 else 0)
    rel = executar_synth_diagnose(repo=repo, eval_run_id=eid, router_agent_path=router_md, out_dir=tmp_path / "out",
                                  formato="both", allow_root=tmp_path / "out", repo_root=None)
    assert rel.exit_code == 0
    assert rel.workflow_macro_f1 is not None
    assert rel.workflow_route_consistency_rate == pytest.approx(0.75)
    assert rel.n_colisoes_workflow >= 0
    sha = repo.connection.execute("SELECT graph_sha256 FROM routing_graph_workflows LIMIT 1").fetchone()[0]
    assert len(repo.listar_workflows_grafo(sha)) == 9
