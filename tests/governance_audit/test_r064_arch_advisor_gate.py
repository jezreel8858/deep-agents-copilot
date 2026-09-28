"""
test_r064_arch_advisor_gate.py — Validação determinística do gate de Plano de Implementação R-064
e prioridade do specialist-arch-advisor antes de qualquer codemod/feature-developer.

Quality Gate que garante:
1. WORKFLOW-FRAMEWORK-MIGRATION em routing-graph.yaml possui etapa de arch-advisor
   posicionada estritamente antes de qualquer etapa de codemod/rewrite.
2. Cada um dos 6 routers de domínio (5 backend: ejb, spring-boot, spring-reactive, python, struts;
   e 1 frontend: angular) formaliza a regra R-064 no seu fluxo de decisão para handoff
   do tech-solution-architect.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_GRAPH_PATH = REPO_ROOT / ".github" / "agents" / "routing-graph.yaml"
AGENTS_BACKEND_DIR = REPO_ROOT / ".github" / "agents" / "backend"
AGENTS_FRONTEND_DIR = REPO_ROOT / ".github" / "agents" / "frontend"

BACKEND_STACKS = ["ejb", "spring-boot", "spring-reactive", "python", "struts"]
ALL_DOMAIN_STACKS = ["ejb", "spring-boot", "spring-reactive", "python", "struts", "angular"]


def resolve_router_file(stack: str) -> Path:
    """Resolve o caminho do arquivo do router dependendo se é frontend ou backend."""
    if stack == "angular":
        return AGENTS_FRONTEND_DIR / "angular" / "angular-router.agent.md"
    return AGENTS_BACKEND_DIR / stack / f"{stack}-router.agent.md"


@pytest.fixture(scope="session")
def routing_graph_data():
    """Carrega o conteúdo parseado de routing-graph.yaml."""
    assert ROUTING_GRAPH_PATH.exists(), f"routing-graph.yaml não encontrado em {ROUTING_GRAPH_PATH}"
    content = ROUTING_GRAPH_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(content) or {}


@pytest.mark.parametrize("stack", ALL_DOMAIN_STACKS)
def test_workflow_framework_migration_arch_advisor_precedes_codemod(routing_graph_data, stack: str):
    """
    Garante que no WORKFLOW-FRAMEWORK-MIGRATION existe uma etapa de arch-advisor
    posicionada ANTES de qualquer etapa de codemod/rewrite.
    Angular não participa diretamente do WORKFLOW-FRAMEWORK-MIGRATION backend-to-backend (R-064).
    """
    if stack == "angular":
        pytest.skip("Angular é stack frontend e não participa diretamente do WORKFLOW-FRAMEWORK-MIGRATION backend-to-backend")

    workflows = routing_graph_data.get("workflows", [])
    wf_migration = next((wf for wf in workflows if wf.get("id") == "WORKFLOW-FRAMEWORK-MIGRATION"), None)
    assert wf_migration is not None, "WORKFLOW-FRAMEWORK-MIGRATION deve existir em routing-graph.yaml"

    estados = wf_migration.get("estados", [])
    assert len(estados) > 0, "WORKFLOW-FRAMEWORK-MIGRATION deve conter estados definidos"

    arch_advisor_index = -1
    codemod_index = -1

    for idx, estado in enumerate(estados):
        agent_field = str(estado.get("agent", "")).lower()
        nome_field = str(estado.get("nome", "")).lower()
        resolvido_field = str(estado.get("resolvido_por", "")).lower()

        is_arch_advisor = (
            "arch-advisor" in agent_field
            or "arch-advisor" in resolvido_field
            or "implementation_plan" in nome_field
        )
        is_codemod = (
            "codemod" in nome_field
            or "rewrite" in nome_field
            or "codemod" in agent_field
        )

        if is_arch_advisor and arch_advisor_index == -1:
            arch_advisor_index = idx

        if is_codemod and codemod_index == -1:
            codemod_index = idx

    assert arch_advisor_index != -1, "Etapa com specialist-arch-advisor não foi encontrada no WORKFLOW-FRAMEWORK-MIGRATION"
    assert codemod_index != -1, "Etapa de codemod/rewrite não foi encontrada no WORKFLOW-FRAMEWORK-MIGRATION"
    assert arch_advisor_index < codemod_index, (
        f"A etapa de arch-advisor (índice {arch_advisor_index}) DEVE anteceder "
        f"a etapa de codemod/rewrite (índice {codemod_index}) conforme R-064"
    )


@pytest.mark.parametrize("stack", ALL_DOMAIN_STACKS)
def test_router_decision_tree_enforces_r064_arch_advisor_gate(stack: str):
    """
    Garante que cada um dos routers de domínio (backend e frontend) declara a regra R-064
    e o encaminhamento para <stack>-arch-advisor antes de despachar para feature-developer.
    """
    router_file = resolve_router_file(stack)
    assert router_file.exists(), f"Router não encontrado: {router_file}"

    content = router_file.read_text(encoding="utf-8")

    assert "R-064" in content, f"{router_file.name} DEVE citar explicitamente a regra R-064"
    assert "arch-advisor" in content, f"{router_file.name} DEVE referenciar arch-advisor na árvore de decisão"
    assert "feature-developer" in content, f"{router_file.name} DEVE referenciar feature-developer na árvore de decisão"
    assert "tech-solution-architect" in content, (
        f"{router_file.name} DEVE referenciar handoff de tech-solution-architect vinculado a R-064"
    )
