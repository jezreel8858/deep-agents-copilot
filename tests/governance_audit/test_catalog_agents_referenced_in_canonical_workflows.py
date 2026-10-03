"""
test_catalog_agents_referenced_in_canonical_workflows.py — Validação determinística
de cobertura integral de agents do catálogo em workflows canônicos (R-050 / R-055).

Garante que:
1. Todos os agents declarados em catalog.yaml estejam formalmente referenciados
   em .github/agents/workflows.md nos seus devidos papéis, etapas ou Quality Gates.
2. Agentes de bootstrap e setup técnico (tipo: health_check / onboarding) possuam
   exceção explícita documentada em workflows.md.
3. Não existam exceções silenciosas ou agents fantasmas fora da matriz de rastreabilidade.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import read_workflows_full_content

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
WORKFLOWS_PATH = REPO_ROOT / ".github" / "agents" / "workflows.md"

# Agentes de bootstrap / health-check intencionalmente fora dos 9 workflows canônicos
BOOTSTRAP_EXCEPTION_AGENTS = {
    "binding-initializer",
    "adapter-generator",
}


def test_catalog_and_workflows_files_exist():
    """Garante existência dos artefatos canônicos SSOT."""
    assert CATALOG_PATH.exists(), f"catalog.yaml não encontrado em {CATALOG_PATH}"
    assert WORKFLOWS_PATH.exists(), f"workflows.md não encontrado em {WORKFLOWS_PATH}"


def test_all_catalog_agents_referenced_in_workflows_or_documented_exceptions():
    """
    Valida R-050: Todo agent registrado em catalog.yaml deve estar explicitamente
    citado nos workflows canônicos em workflows.md OU constar na lista de exceções
    de bootstrap devidamente fundamentadas.
    """
    catalog_data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog_agents = set(catalog_data.get("agents", {}).keys())
    assert len(catalog_agents) >= 30, f"Catálogo incompleto: {len(catalog_agents)} agents encontrados"

    wf_content = read_workflows_full_content(REPO_ROOT)

    missing_agents: list[str] = []
    for agent_id in sorted(catalog_agents):
        if agent_id in BOOTSTRAP_EXCEPTION_AGENTS:
            continue
        # Verifica menção do agent (como @agent-id ou agent-id)
        if f"@{agent_id}" not in wf_content and agent_id not in wf_content:
            missing_agents.append(agent_id)

    missing_report = "\n".join(f"  - @{a}" for a in missing_agents)
    assert not missing_agents, (
        f"Foram encontrados {len(missing_agents)} agents de catalog.yaml não referenciados em workflows.md:\n"
        f"{missing_report}\n"
        "-> Todo agent do catálogo deve pertencer a ao menos um workflow operacional ou constar em BOOTSTRAP_EXCEPTION_AGENTS."
    )


def test_bootstrap_exception_agents_documented_in_workflows():
    """
    Valida que os agents de bootstrap em BOOTSTRAP_EXCEPTION_AGENTS possuem nota de
    exceção explícita formalmente documentada em workflows.md.
    """
    wf_content = read_workflows_full_content(REPO_ROOT)

    assert "Nota de Exceção Explícita de Governança" in wf_content, (
        "workflows.md DEVE conter a nota de exceção explícita para agentes de bootstrap"
    )

    for agent_id in BOOTSTRAP_EXCEPTION_AGENTS:
        assert agent_id in wf_content, (
            f"O agente de exceção '@{agent_id}' DEVE ser formalmente citado na nota de exceção de workflows.md"
        )


def test_bootstrap_exception_agents_exist_in_catalog():
    """Garante que a lista de exceções contém apenas agents válidos e existentes em catalog.yaml."""
    catalog_data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog_agents = set(catalog_data.get("agents", {}).keys())

    invalid_exceptions = BOOTSTRAP_EXCEPTION_AGENTS - catalog_agents
    assert not invalid_exceptions, (
        f"BOOTSTRAP_EXCEPTION_AGENTS contém identificadores que não existem em catalog.yaml: {invalid_exceptions}"
    )
