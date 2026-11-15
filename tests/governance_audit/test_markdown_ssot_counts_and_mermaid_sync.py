"""Suíte determinística de paridade SSOT em Markdown e blocos Mermaid de workflows (R-015 / R-033 / R-055 / R-064)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tools.governance_sync.core import SyncOptions
from tools.governance_sync.sync_docs_counts_and_mermaid import (
    CANONICAL_AGENT_COVERAGE_DOCS,
    EXCLUDED_HISTORICAL_PATHS,
    MONITORED_MARKDOWN_FILES,
    R064_PRE_HITL_WORKFLOW_MERMAID_FILES,
    REMOVED_GHOST_AGENTS,
    REPO_ROOT,
    WORKFLOW_MERMAID_EXEMPTIONS,
    check_catalog_agent_coverage,
    check_or_sync_markdown_counts,
    check_workflow_mermaid_blocks,
    collect_ssot_counts,
    extract_mermaid_blocks,
    is_excluded_historical_path,
    load_catalog_agent_names,
    main,
    run_sync,
    validate_mermaid_block_syntax,
)


def test_ssot_counts_match_canonical_repository_topology() -> None:
    """1) Paridade dinâmica das contagens SSOT contra os diretórios e catálogos reais."""
    counts = collect_ssot_counts(REPO_ROOT)

    assert counts.total_agent_files == counts.root_agent_files + counts.stack_agent_files
    assert counts.total_agent_files == 63
    assert counts.root_agent_files == 31
    assert counts.stack_agent_files == 32
    assert counts.catalog_root_entries == 39
    assert counts.routing_graph_nodes == 39
    assert counts.total_skills == 81
    assert counts.tier1_skills == 15
    assert counts.tier2_skills == 65
    assert counts.tier3_skills == 1
    assert counts.tier1_skills + counts.tier2_skills + counts.tier3_skills == counts.total_skills
    assert counts.total_canonical_workflows == 10
    assert counts.generic_instructions == 6


def test_monitored_markdown_files_have_zero_count_drift() -> None:
    """1b) Todos os documentos .md vivos monitorados estão alinhados com o SSOT real."""
    counts = collect_ssot_counts(REPO_ROOT)
    checked, updated, issues = check_or_sync_markdown_counts(
        repo_root=REPO_ROOT,
        counts=counts,
        apply=False,
    )
    assert len(checked) == len(MONITORED_MARKDOWN_FILES)
    assert updated == []
    assert issues == [], f"Desvios de contagem SSOT detectados: {issues}"


@pytest.mark.parametrize("historical_path", [
    "docs/plans/governance/20261114-120000-plan-critic-mermaid-counts-sync-enforcement.md",
    "CHANGELOG.md",
    "docs/adr/ADR-0014-pre-hitl-skeptical-plan-review-gate.md",
])
def test_historical_paths_are_excluded_from_mutation(historical_path: str) -> None:
    """Garante que artefatos históricos imutáveis são excluídos da sincronização."""
    assert is_excluded_historical_path(historical_path) is True
    for prefix in EXCLUDED_HISTORICAL_PATHS:
        assert is_excluded_historical_path(prefix) is True


def test_catalog_agents_100_percent_present_in_canonical_docs_and_no_ghosts() -> None:
    """2) 100% dos agents de catalog.yaml (incluindo plan-critic) constam em README.md e .github/agents/README.md, sem refactor-executor."""
    catalog_agents = load_catalog_agent_names(REPO_ROOT)
    assert "plan-critic" in catalog_agents
    for ghost in REMOVED_GHOST_AGENTS:
        assert ghost not in catalog_agents

    issues = check_catalog_agent_coverage(REPO_ROOT, CANONICAL_AGENT_COVERAGE_DOCS)
    assert issues == [], f"Falha de cobertura documental de agents: {issues}"


@pytest.mark.parametrize("workflow_rel_path", R064_PRE_HITL_WORKFLOW_MERMAID_FILES)
def test_r064_workflows_have_plan_critic_in_valid_mermaid_blocks(workflow_rel_path: str) -> None:
    """3) Presença obrigatória de plan-critic nos blocos mermaid dos 10 arquivos de R064_PRE_HITL_WORKFLOW_MERMAID_FILES e integridade sintática."""
    workflow_path = REPO_ROOT / workflow_rel_path
    assert workflow_path.is_file(), f"Arquivo de workflow ausente: {workflow_rel_path}"

    text = workflow_path.read_text(encoding="utf-8")
    blocks = extract_mermaid_blocks(text)
    assert len(blocks) >= 1, f"Nenhum bloco mermaid encontrado em {workflow_rel_path}"
    assert any("plan-critic" in b for b in blocks), (
        f"plan-critic ausente nos blocos mermaid de {workflow_rel_path}"
    )

    for block in blocks:
        assert validate_mermaid_block_syntax(block) == []


def test_workflow_mermaid_exemptions_and_batch_checker() -> None:
    """3b) Verifica isenção explícita de workflow-prompt-synthesis.md e validação em lote sem erros."""
    assert ".github/agents/workflows/workflow-prompt-synthesis.md" in WORKFLOW_MERMAID_EXEMPTIONS
    assert check_workflow_mermaid_blocks(REPO_ROOT) == []


def test_governance_sync_cli_check_mode_exits_zero() -> None:
    """4) Execução limpa (exit_code == 0 / zero pendências) de tools.governance_sync em modo --check."""
    exit_code = main(["--check"])
    assert exit_code == 0

    report = run_sync(SyncOptions(mode="check"), repo_root=REPO_ROOT)
    assert getattr(report, "issues", []) == []


def test_governance_sync_detects_and_repairs_synthetic_drift_in_tmp_path(tmp_path: Path) -> None:
    """4b) Teste unitário de detecção de drift sintético e auto-reparo (--apply) em tmp_path."""
    counts = collect_ssot_counts(REPO_ROOT)
    sample_doc = tmp_path / "README.md"
    sample_doc.write_text(
        "# Repo\n"
        "Temos 62 arquivos `.agent.md` (30 na raiz + 32 em `stacks/`), "
        "38 nós no `routing-graph.yaml`, 80 skills ativas e 9 workflows canônicos.\n",
        encoding="utf-8",
    )

    checked, updated, issues = check_or_sync_markdown_counts(
        repo_root=tmp_path,
        counts=counts,
        apply=False,
        monitored_files=("README.md",),
    )
    assert checked == ["README.md"]
    assert updated == []
    assert len(issues) >= 4

    # Agora aplica auto-reparo (--apply)
    _, updated_apply, _ = check_or_sync_markdown_counts(
        repo_root=tmp_path,
        counts=counts,
        apply=True,
        monitored_files=("README.md",),
    )
    assert updated_apply == ["README.md"]

    # Revalida após apply: zero issues
    _, _, issues_after = check_or_sync_markdown_counts(
        repo_root=tmp_path,
        counts=counts,
        apply=False,
        monitored_files=("README.md",),
    )
    assert issues_after == []
    repaired_text = sample_doc.read_text(encoding="utf-8")
    assert f"{counts.total_agent_files} arquivos `.agent.md`" in repaired_text
    assert f"{counts.routing_graph_nodes} nós no `routing-graph.yaml`" in repaired_text


def test_plan_critic_routing_eval_cases_present() -> None:
    """5) Presença de casos de roteamento para plan-critic em .github/agents/evals/casos-roteamento.yaml."""
    evals_path = REPO_ROOT / ".github" / "agents" / "evals" / "casos-roteamento.yaml"
    assert evals_path.is_file(), "casos-roteamento.yaml ausente"

    raw_text = evals_path.read_text(encoding="utf-8")
    assert "plan-critic" in raw_text, "plan-critic ausente em casos-roteamento.yaml"

    data = yaml.safe_load(raw_text)
    cases = []
    if isinstance(data, list):
        cases = data
    elif isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                cases.extend(v)
    plan_critic_cases = [
        c for c in cases
        if isinstance(c, dict) and "plan-critic" in str(c)
    ]
    assert len(plan_critic_cases) >= 1, "Nenhum caso de teste de roteamento encontrado para plan-critic"
