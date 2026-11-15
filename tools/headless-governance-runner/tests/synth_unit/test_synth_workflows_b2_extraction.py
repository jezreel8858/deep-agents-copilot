"""Aceite B2 (plano §9): capturar_workflow, regra de consistencia 3.5, seeds de workflow e '--workflow-seeds off'."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import SDKResponse
from governance_runner.synth.evaluator import (
    PRE_ETAPAS_WORKFLOW,
    avaliar_consistencia_workflow_rota,
    avaliar_lote,
    capturar_workflow,
    validar_coerencia_workflow,
)
from governance_runner.synth.exporter import exportar_silver
from governance_runner.synth.normalize import detectar_override, sanitizar_prompt
from governance_runner.synth.routing_graph import GrafoSnapshot, WorkflowGrafo, carregar_snapshot_grafo
from governance_runner.synth.seeds import (
    calcular_cobertura_workflows_golden,
    gerar_seeds_workflows,
    identificar_workflows_uncoverable,
)
from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.use_cases import executar_synth_generate

from .conftest import FakeSDKClient

WF_FD = "WORKFLOW-FEATURE-DEVELOPMENT"
WF_BF = "WORKFLOW-BUG-FIX"
WF_PS = "WORKFLOW-PROMPT-SYNTHESIS"
IDS = frozenset({WF_FD, WF_BF, WF_PS})


# ------------------------------------------------------------ capturar_workflow
@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Workflow: WORKFLOW-BUG-FIX", (WF_BF, None, "text_banner")),
        ("Workflow: WORKFLOW-BUG-FIX\nEtapa do Workflow: 2", (WF_BF, 2, "text_banner")),
        ("Workflow: N/A", (None, None, "text_banner")),
        ("Workflow: N/A\nEtapa do Workflow: 0", (None, 0, "text_banner")),
        ("Workflow: WORKFLOW-INEXISTENTE", (None, None, "invalid_id")),
        ("Workflow: workflow-bug-fix", (None, None, "invalid_id")),  # ID case-sensitive
        ("workflow: WORKFLOW-BUG-FIX", (WF_BF, None, "text_banner")),  # rotulo case-insensitive
        ("WORKFLOW : WORKFLOW-BUG-FIX", (WF_BF, None, "text_banner")),
        ("  Workflow:   WORKFLOW-PROMPT-SYNTHESIS  ", (WF_PS, None, "text_banner")),
        ("etapa do workflow: 12\nworkflow: WORKFLOW-FEATURE-DEVELOPMENT", (WF_FD, 12, "text_banner")),
        ("Workflow: WORKFLOW-BUG-FIX extra", (None, None, "invalid_id")),
        ("Workflow:", (None, None, "none")),
        ("Etapa do Workflow: 3", (None, 3, "none")),
        ("Etapa do Workflow: tres", (None, None, "none")),
        ("sem banner algum", (None, None, "none")),
        ("", (None, None, "none")),
        ("Agente Ativo: agent-router\nDelegado: @bug-triage", (None, None, "none")),
        ("texto Workflow: WORKFLOW-BUG-FIX no meio da linha", (None, None, "none")),
    ],
)
def test_capturar_workflow_tabela(texto: str, esperado: tuple[str | None, int | None, str]) -> None:
    assert capturar_workflow(texto, IDS) == esperado


def test_capturar_workflow_id_fora_do_conjunto_valido_e_invalid_id() -> None:
    assert capturar_workflow("Workflow: WORKFLOW-BUG-FIX", {WF_FD}) == (None, None, "invalid_id")


def test_capturar_workflow_sem_ids_usa_enum_canonico_e_aceita_snapshot() -> None:
    assert capturar_workflow("Workflow: WORKFLOW-BUG-FIX")[0] == WF_BF
    snap = carregar_snapshot_grafo()
    assert capturar_workflow("Workflow: WORKFLOW-RELEASE-READINESS", snap)[0] == "WORKFLOW-RELEASE-READINESS"
    vazio = GrafoSnapshot(sha256="x", rotas=(), nos=frozenset(), workflows=())
    assert capturar_workflow("Workflow: WORKFLOW-BUG-FIX", vazio)[0] == WF_BF  # fallback canonico


def test_capturar_workflow_aceita_sdkresponse_texto_e_achados() -> None:
    r1 = SDKResponse(achados=(), premium_requests_consumidos=0, texto="Workflow: WORKFLOW-BUG-FIX\nEtapa do Workflow: 1")
    assert capturar_workflow(r1, IDS) == (WF_BF, 1, "text_banner")
    r2 = SDKResponse(achados=({"mensagem": "Workflow: WORKFLOW-BUG-FIX"},), premium_requests_consumidos=0, texto="")
    assert capturar_workflow(r2, IDS)[0] == WF_BF
    assert capturar_workflow(None, IDS) == (None, None, "none")  # type: ignore[arg-type]


@pytest.mark.parametrize("frag", ["Workflow: WORKFLOW-BUG-FIX", "Etapa do Workflow: 2", "workflow : x"])
def test_prompts_com_banner_de_workflow_sao_rejeitados(frag: str) -> None:
    assert detectar_override(f"Preciso de ajuda. {frag}") is not None
    ok, _ = sanitizar_prompt(f"Preciso de ajuda. {frag}")
    assert ok is False


# ----------------------------------------------------- regra de consistencia 3.5
SNAP = carregar_snapshot_grafo()
PAD_STACK = ("*-developer",)
PAD_ROUTER = ("*-router",)


@pytest.mark.parametrize(
    ("wf", "rota", "padroes", "esperado"),
    [
        (WF_BF, "feature-planner", SNAP, 0),  # BUG-FIX -> feature-planner incoerente
        (WF_BF, "bug-triage", SNAP, 1),
        (WF_BF, "@Bug-Triage", SNAP, 1),  # normalizacao
        (WF_FD, "prompt-structuring", SNAP, 1),  # FEATURE-DEV: pre-etapa e a etapa 1
        (WF_PS, "prompt-structuring", SNAP, 1),
        (WF_PS, "requirements-analyst", SNAP, 1),
        ("WORKFLOW-RELEASE-READINESS", "prompt-structuring", SNAP, None),  # fast-path: pre-etapa legitima
        (WF_BF, "prompt-structuring", SNAP, None),
        (WF_BF, "binding-initializer", SNAP, None),
        (WF_FD, "binding-initializer", SNAP, None),  # NULL em qualquer workflow
        (WF_BF, None, SNAP, None),
        (None, "bug-triage", SNAP, None),
        ("", "bug-triage", SNAP, None),
        (WF_BF, "", SNAP, None),
        # coringas <stack> e domain-router
        (WF_FD, "python-developer", PAD_STACK, 1),
        (WF_FD, "java-developer", PAD_STACK, 1),
        (WF_FD, "python-reviewer", PAD_STACK, 0),
        (WF_FD, "developer", PAD_STACK, 0),  # fronteira: sem prefixo
        (WF_FD, "python-router", PAD_ROUTER, 1),
        (WF_FD, "agent-router", PAD_ROUTER, 1),
        (WF_FD, "router", PAD_ROUTER, 0),
        (WF_FD, "python-developer", ("<stack>-developer",), 1),
        (WF_FD, "python-router", ("domain-router",), 1),
        (WF_FD, "bug-triage", ("bug-triage|feature-planner",), 1),  # alternativas por pipe
        (WF_FD, "feature-planner", ("bug-triage|feature-planner",), 1),
        (WF_FD, "sql-dba", ("bug-triage|feature-planner",), 0),
        (WF_FD, "prompt-structuring", (), 1),  # sem padroes: FEATURE-DEV + prompt-structuring
        (WF_BF, "bug-triage", (), None),  # sem padroes: nao ha como julgar
        (WF_BF, "bug-triage", None, None),
        (WF_BF, "bug-triage", {WF_BF: ("bug-triage",)}, 1),
        (WF_BF, "sql-dba", {WF_BF: ("bug-triage",)}, 0),
        (WF_BF, "bug-triage", {WF_BF: next(w for w in SNAP.workflows if w.workflow_id == WF_BF)}, 1),
        (WF_BF, "bug-triage", {"OUTRO": ("x",)}, None),
        (WF_BF, "bug-triage", next(w for w in SNAP.workflows if w.workflow_id == WF_BF), 1),
    ],
)
def test_regra_consistencia_3_5(wf, rota, padroes, esperado) -> None:  # type: ignore[no-untyped-def]
    assert avaliar_consistencia_workflow_rota(wf, rota, padroes) == esperado


def test_alias_validar_coerencia_workflow_e_pre_etapas() -> None:
    assert validar_coerencia_workflow is avaliar_consistencia_workflow_rota
    assert PRE_ETAPAS_WORKFLOW == frozenset({"binding-initializer", "prompt-structuring"})


# ------------------------------------------------------- seeds de workflow
def test_workflow_seeds_off_nao_gera_nada() -> None:
    assert gerar_seeds_workflows(SNAP, "off") == ()
    assert gerar_seeds_workflows(SNAP) == ()


def test_workflow_seeds_all_gera_seed_por_gatilho_com_expected_workflow() -> None:
    seeds = gerar_seeds_workflows(SNAP, "all", max_seeds_por_workflow=2)
    assert seeds
    ids = {w.workflow_id for w in SNAP.workflows}
    for s in seeds:
        assert s.expected_workflow in ids
        assert s.graph_workflow_id == s.expected_workflow
        assert s.seed_source == "routing_graph"
        assert sanitizar_prompt(s.prompt)[0] is True
        assert "Workflow:" not in s.prompt
    assert {s.expected_workflow for s in seeds} == ids
    por_wf = {w.workflow_id: w for w in SNAP.workflows}
    for s in seeds:
        if s.seed_case_id.startswith("wf:"):
            assert len([x for x in seeds if x.seed_case_id.startswith(f"wf:{s.expected_workflow}:")]) <= 2
    # determinismo
    assert gerar_seeds_workflows(SNAP, "all", rng_seed=7) == gerar_seeds_workflows(SNAP, "all", rng_seed=7)
    assert por_wf  # sanity


def test_workflow_seeds_gaps_respeita_cobertura_e_fronteira() -> None:
    todos = gerar_seeds_workflows(SNAP, "all")
    cobertura_total = {w.workflow_id: 99 for w in SNAP.workflows}
    assert gerar_seeds_workflows(SNAP, "gaps", cobertura=cobertura_total) == ()
    cobertura_parcial = {**cobertura_total, WF_BF: 0}
    parciais = gerar_seeds_workflows(SNAP, "gaps", cobertura=cobertura_parcial)
    assert parciais and {s.expected_workflow for s in parciais} <= {w.workflow_id for w in SNAP.workflows}
    assert WF_BF in {s.expected_workflow for s in parciais}
    assert len(parciais) < len(todos)
    # limite inferior do teto por workflow (max(1, 0) == 1)
    um = gerar_seeds_workflows(SNAP, "all", max_seeds_por_workflow=0)
    assert all(s.seed_case_id.endswith(":0") or s.seed_case_id.count(":") >= 2 for s in um)


def _wf(wid: str, gat: tuple[str, ...], padroes: tuple[str, ...]) -> WorkflowGrafo:
    return WorkflowGrafo(workflow_id=wid, nome=wid.lower(), fast_path=False, gatilhos_norm=gat,
                         etapa1_padroes=padroes, workflow_hash="h" * 64, gatilhos=gat)


def test_seeds_de_fronteira_para_gatilho_compartilhado_e_uncoverable() -> None:
    snap = GrafoSnapshot(
        sha256="x", rotas=(), nos=frozenset({"bug-triage", "feature-planner"}),
        workflows=(
            _wf("WORKFLOW-A", ("erro critico",), ("bug-triage",)),
            _wf("WORKFLOW-B", ("erro critico",), ("feature-planner",)),
            _wf("WORKFLOW-C", (), ("bug-triage",)),
            _wf("WORKFLOW-D", ("algo",), ()),
        ),
    )
    assert identificar_workflows_uncoverable(snap) == ("WORKFLOW-C", "WORKFLOW-D")
    seeds = gerar_seeds_workflows(snap, "all")
    fronteira = [s for s in seeds if not s.seed_case_id.startswith("wf:WORKFLOW-A:0") and "erro critico" in s.prompt.lower()]
    assert len(fronteira) >= 2  # 1 por workflow + seeds de par colidente
    assert {s.expected_route for s in seeds if s.expected_workflow == "WORKFLOW-A"} == {"bug-triage"}
    assert {s.expected_route for s in seeds if s.expected_workflow == "WORKFLOW-B"} == {"feature-planner"}


def test_cobertura_workflows_golden_conta_por_workflow() -> None:
    cov = calcular_cobertura_workflows_golden((), SNAP)
    assert set(cov) == {w.workflow_id for w in SNAP.workflows}
    assert all(v == 0 for v in cov.values())


# ------------------------- '--workflow-seeds off' byte-identico a v2 (sem workflow)
def _gerar(repo: SynthRepository, **kw: object) -> list[tuple[str, str, str, str | None]]:
    rel = executar_synth_generate(
        repo=repo, generator_mode="template", targets=["bug-triage"], dimensions=["parafrase"],
        per_stratum=2, rng_seed=42, env={}, **kw,  # type: ignore[arg-type]
    )
    assert rel.exit_code == 0 and rel.run_id
    ps = repo.listar_prompts(rel.run_id)
    assert rel.contadores.get("n_workflow_seeds", 0) == 0 or kw.get("workflow_seeds") != "off"
    return sorted((p["text"], p["expected_route"], p["seed_source"], p["seed_case_id"]) for p in ps)


def test_workflow_seeds_off_e_byte_identico_ao_comportamento_v2(tmp_path: Path) -> None:
    with SynthRepository(tmp_path / "a.db", repo_root=tmp_path) as ra, SynthRepository(tmp_path / "b.db", repo_root=tmp_path) as rb:
        ra.migrar(); rb.migrar()
        padrao = _gerar(ra)
        off = _gerar(rb, workflow_seeds="off")
        assert padrao == off and padrao
        q = ("SELECT seed_case_id, seed_source, expected_workflow FROM synth_prompts "
             "WHERE expected_workflow IS NOT NULL OR graph_workflow_id IS NOT NULL ORDER BY 1")
        ca, cb = ra.connection.execute(q).fetchall(), rb.connection.execute(q).fetchall()
        assert ca == cb  # off == default
        # workflow so vem de seeds golden manuais (que ja declaram 'workflow:'); nenhum seed sintetico wf:*
        assert all(r[1] == "manual" and not str(r[0]).startswith("wf:") for r in ca)
        assert not any(str(r[0]).startswith("wf:") for r in ra.connection.execute("SELECT seed_case_id FROM synth_prompts"))


def test_workflow_seeds_all_acrescenta_prompts_com_workflow(tmp_path: Path) -> None:
    with SynthRepository(tmp_path / "a.db", repo_root=tmp_path) as r:
        r.migrar()
        rel = executar_synth_generate(
            repo=r, generator_mode="template", targets=["bug-triage"], dimensions=["parafrase"],
            per_stratum=1, rng_seed=42, env={}, workflow_seeds="all",
        )
        assert rel.exit_code == 0
        assert rel.contadores.get("n_workflow_seeds", 0) > 0
        ps = r.listar_prompts(rel.run_id)
        com_wf = [p for p in ps if p.get("expected_workflow")]
        assert com_wf and all(p["graph_workflow_id"] == p["expected_workflow"] for p in com_wf)


def test_workflow_seeds_modo_invalido_levanta_value_error(repo: SynthRepository) -> None:
    with pytest.raises(ValueError, match="workflow-seeds"):
        executar_synth_generate(repo=repo, generator_mode="template", workflow_seeds="bogus", env={})  # type: ignore[arg-type]


# --------------------------------------------- avaliar_lote + exportacao silver
def test_avaliar_lote_persiste_workflow_e_consistencia_e_exporta(repo: SynthRepository, router_md: Path, tmp_path: Path) -> None:
    rid = repo.criar_run(kind="generate", generator="template")
    for i, (wf, rota) in enumerate([(WF_BF, "bug-triage"), (WF_BF, "bug-triage"), (WF_BF, "bug-triage")]):
        repo.inserir_prompt(run_id=rid, text=f"p{i}", text_norm=f"p{i}", sha256=f"s{i}", expected_route=rota,
                            agente_alvo=rota, dimensao_perturbacao="parafrase", expected_workflow=wf, graph_workflow_id=wf)
    repo.inserir_prompt(run_id=rid, text="legado", text_norm="legado", sha256="sl", expected_route="bug-triage",
                        agente_alvo="bug-triage", dimensao_perturbacao="parafrase")
    respostas = [
        SDKResponse(achados=(), premium_requests_consumidos=1, texto="Workflow: WORKFLOW-BUG-FIX\nEtapa do Workflow: 1\nDelegado: @bug-triage"),
        SDKResponse(achados=(), premium_requests_consumidos=1, texto="Workflow: WORKFLOW-BUG-FIX\nDelegado: @feature-planner"),
        SDKResponse(achados=(), premium_requests_consumidos=1, texto="Workflow: WORKFLOW-XYZ\nDelegado: @bug-triage"),
        SDKResponse(achados=(), premium_requests_consumidos=1, texto="Delegado: @bug-triage"),
    ]
    cli = FakeSDKClient(respostas=respostas)
    avaliar_lote(repo=repo, cliente=cli, budget_lote=Budget(max_premium_requests=10), router_agent_path=router_md, run_id="ev-wf")
    avs = {e["prompt_text"]: e for e in repo.listar_avaliacoes("ev-wf")}
    assert len(avs) == 4
    cons = sorted(((e["observed_workflow"], e["workflow_source"], e["workflow_route_consistent"]) for e in avs.values()
                  if e["observed_workflow"] or e["workflow_source"] != "none"), key=str)
    assert (WF_BF, "text_banner", 1) in cons and (WF_BF, "text_banner", 0) in cons
    assert any(e["workflow_source"] == "invalid_id" and e["observed_workflow"] is None for e in avs.values())
    assert any(e["observed_etapa"] == 1 for e in avs.values())
    assert all(e["workflow_route_consistent"] is None for e in avs.values() if e["observed_workflow"] is None)

    res = exportar_silver(repo=repo, eval_run_id="ev-wf", only_failures=False, allow_root=tmp_path / "out")
    doc = yaml.safe_load(Path(res.path).read_text(encoding="utf-8"))
    com = [c for c in doc["casos"] if "workflow" in c["expected"]]
    sem = [c for c in doc["casos"] if "workflow" not in c["expected"]]
    assert com and sem
    assert all(c["expected"]["workflow"] == WF_BF for c in com)
    for c in sem:  # campos omitidos quando NULL (compat v2)
        assert "observed" not in c and "observed_workflow" not in c["silver"]
# ------------------------------------------------------------------------ CLI
def test_cli_workflow_seeds_default_off_e_choices() -> None:
    from governance_runner import cli
    parser = cli.construir_parser()
    assert parser.parse_args(["--use-case", "synth-generate"]).workflow_seeds == "off"
    assert parser.parse_args(["--use-case", "synth-generate", "--workflow-seeds", "all"]).workflow_seeds == "all"
    with pytest.raises(SystemExit):
        parser.parse_args(["--use-case", "synth-generate", "--workflow-seeds", "bogus"])
def test_cli_generate_com_workflow_seeds_all_exit_0(tmp_path: Path) -> None:
    from governance_runner import cli
    rc = cli.main(["--use-case", "synth-generate", "--db", str(tmp_path / "c.db"), "--per-stratum", "1",
                   "--dimensions", "parafrase", "--workflow-seeds", "all"])
    assert rc == 0

def test_capturar_workflow_e_rota_com_prefixo_lista_markdown() -> None:
    from governance_runner.synth.evaluator import _REGEX_BANNER, _REGEX_ETAPA_WORKFLOW, capturar_rota, capturar_workflow
    texto_banner = (
        "Agente Ativo: @bug-triage\n\n"
        "- Transição: Nova triagem (1º turno)\n"
        "Workflow: WORKFLOW-BUG-FIX\n"
        "- Etapa do Workflow: 2\n"
        "- Rota: bug_fix\n"
        "- [Model] Delegando para @bug-triage — modelo solicitado: Claude Sonnet 4.6\n"
        "- Delegado: @bug-triage\n"
        "- Motivo: Triagem inicial de bug\n"
        "- Confiança: alta\n"
        "- Confidence Score: 0.95\n"
        "- Nível de Routing: rule-based"
    )
    wf_id, etapa, wf_source = capturar_workflow(texto_banner, IDS)
    assert wf_id == WF_BF
    assert etapa == 2
    assert wf_source == "text_banner"

    assert _REGEX_ETAPA_WORKFLOW.search("- **Etapa do Workflow**: 3") is not None
    assert _REGEX_BANNER["Delegado"].search(texto_banner).group(1).strip() == "@bug-triage"
    assert _REGEX_BANNER["Rota"].search(texto_banner).group(1).strip() == "bug_fix"
    assert _REGEX_BANNER["Agente Ativo"].search("- Agente Ativo: @bug-triage").group(1).strip() == "@bug-triage"

    rota, fonte = capturar_rota(SDKResponse(achados=(), premium_requests_consumidos=1, texto=texto_banner))
    assert rota == "bug-triage"
    assert fonte == "text_banner"
