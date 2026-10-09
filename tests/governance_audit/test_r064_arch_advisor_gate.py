"""
test_r064_arch_advisor_gate.py — Validação determinística do gate de Plano de Implementação R-064
e prioridade do specialist-arch-advisor antes de qualquer codificação/mutação de código.

Quality Gate que garante:
1. Todo workflow canônico em routing-graph.yaml que envolve mutação de código possui etapa
   de autoria de plano (implementation_plan_authoring) antecedendo estritamente as etapas
   de código, as quais declaram a guarda requires_plan: true.
2. Cada um dos 8 routers de domínio (5 backend: ejb, spring-boot, spring-reactive, python, struts;
   2 frontend: angular, react; e 1 database) formaliza a regra R-064 no seu fluxo de decisão,
   encaminhando para <stack>-arch-advisor antes de despachar executores downstream.
3. Desenvolvedores, engenheiros de teste e especialistas de banco declaram a pré-condição
   de plano (R-064) com bloqueio (retorno ao router com motivo pre_condicao_plano).
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
ALL_DOMAIN_STACKS = ["ejb", "spring-boot", "spring-reactive", "python", "struts", "angular", "react", "database"]

ALL_DEVELOPERS = [
    "angular-developer",
    "react-developer",
    "spring-boot-developer",
    "spring-reactive-developer",
    "ejb-developer",
    "python-developer",
    "struts-developer",
]

ALL_TEST_ENGINEERS = [
    "angular-test-engineer",
    "react-test-engineer",
    "spring-boot-test-engineer",
    "spring-reactive-test-engineer",
    "ejb-test-engineer",
    "python-test-engineer",
    "struts-test-engineer",
]

ALL_DB_SPECIALISTS = [
    "oracle-database-specialist",
    "informix-database-specialist",
    "database-specialist",
]

CODE_WORKFLOWS = [
    "WORKFLOW-BUG-FIX",
    "WORKFLOW-REFACTORING",
    "WORKFLOW-FEATURE-DEVELOPMENT",
    "WORKFLOW-GOVERNANCE-MAINTENANCE",
    "WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION",
    "WORKFLOW-FRAMEWORK-MIGRATION",
]


def resolve_router_file(stack: str) -> Path:
    """Resolve o caminho do arquivo do router dependendo se é frontend ou backend."""
    if stack in ("angular", "react"):
        return AGENTS_FRONTEND_DIR / stack / f"{stack}-router.agent.md"
    if stack == "database":
        return AGENTS_BACKEND_DIR / "database" / "database-router.agent.md"
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
    Angular, React e Database não participam diretamente do WORKFLOW-FRAMEWORK-MIGRATION backend-to-backend (R-064).
    """
    if stack in ("angular", "react", "database"):
        pytest.skip(f"{stack} não participa diretamente do WORKFLOW-FRAMEWORK-MIGRATION backend-to-backend principal")

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
    Garante que cada um dos routers de domínio (backend, frontend e database) declara a regra R-064
    e o encaminhamento para <stack>-arch-advisor antes de despachar para executores de código.
    """
    router_file = resolve_router_file(stack)
    assert router_file.exists(), f"Router não encontrado: {router_file}"

    content = router_file.read_text(encoding="utf-8")

    assert "R-064" in content, f"{router_file.name} DEVE citar explicitamente a regra R-064"
    assert "arch-advisor" in content, f"{router_file.name} DEVE referenciar arch-advisor na árvore de decisão"
    assert ("developer" in content or "specialist" in content), (
        f"{router_file.name} DEVE referenciar developer ou specialist na árvore de decisão"
    )
    assert ("plan_ref" in content or "Plano de Implementação" in content), (
        f"{router_file.name} DEVE referenciar plan_ref ou Plano de Implementação vinculado a R-064"
    )


@pytest.mark.parametrize("wf_id", CODE_WORKFLOWS)
def test_all_workflows_with_code_mutation_have_implementation_plan_guard(routing_graph_data, wf_id: str):
    """
    Nova invariante universal R-064: todo workflow canônico que envolva mutação de código
    possui etapa de autoria de plano (implementation_plan_authoring) antecedendo
    estritamente as etapas de código, as quais declaram a guarda requires_plan: true.
    """
    workflows = routing_graph_data.get("workflows", [])
    wf = next((w for w in workflows if w.get("id") == wf_id), None)
    assert wf is not None, f"Workflow {wf_id} não encontrado em routing-graph.yaml"

    estados = wf.get("estados", [])
    assert len(estados) > 0, f"Workflow {wf_id} deve conter estados"

    plan_stage_idx = -1
    first_code_stage_idx = -1

    for idx, estado in enumerate(estados):
        nome = str(estado.get("nome", "")).lower()
        if "implementation_plan" in nome:
            plan_stage_idx = idx
        if estado.get("requires_plan") is True:
            if first_code_stage_idx == -1:
                first_code_stage_idx = idx

    assert plan_stage_idx != -1, f"Etapa 'implementation_plan_authoring' ausente no workflow {wf_id}"
    assert first_code_stage_idx != -1, f"Nenhuma etapa com 'requires_plan: true' encontrada no workflow {wf_id}"
    assert plan_stage_idx < first_code_stage_idx, (
        f"No workflow {wf_id}, a etapa de plano (índice {plan_stage_idx}) DEVE anteceder "
        f"a etapa de código (índice {first_code_stage_idx})"
    )


@pytest.mark.parametrize("dev_name", ALL_DEVELOPERS)
def test_developer_enforces_r064_precondition(dev_name: str):
    """Valida pré-condição R-064 em todos os agentes desenvolvedores."""
    matches = list(REPO_ROOT.glob(f"**/{dev_name}.agent.md"))
    assert len(matches) == 1, f"Agente {dev_name} não encontrado unicamente"
    content = matches[0].read_text(encoding="utf-8")

    assert "R-064" in content, f"[{dev_name}] Deve citar a regra R-064"
    assert "plan_ref" in content, f"[{dev_name}] Deve exigir plan_ref"
    assert "pre_condicao_plano" in content, f"[{dev_name}] Deve retornar motivo pre_condicao_plano"


@pytest.mark.parametrize("te_name", ALL_TEST_ENGINEERS)
def test_test_engineer_enforces_r064_precondition(te_name: str):
    """Valida pré-condição R-064 e exceção testes-only em todos os test-engineers."""
    matches = list(REPO_ROOT.glob(f"**/{te_name}.agent.md"))
    assert len(matches) == 1, f"Agente {te_name} não encontrado unicamente"
    content = matches[0].read_text(encoding="utf-8")

    assert "R-064" in content, f"[{te_name}] Deve citar a regra R-064"
    assert "plan_ref" in content, f"[{te_name}] Deve exigir plan_ref para código de produção"
    assert "pre_condicao_plano" in content, f"[{te_name}] Deve retornar motivo pre_condicao_plano"
    assert ("testes-only" in content or "testes unitários" in content), f"[{te_name}] Deve citar exceção testes-only"


@pytest.mark.parametrize("db_spec_name", ALL_DB_SPECIALISTS)
def test_db_specialist_enforces_r064_precondition(db_spec_name: str):
    """Valida pré-condição R-064 em todos os especialistas de banco de dados."""
    matches = list(REPO_ROOT.glob(f"**/{db_spec_name}.agent.md"))
    assert len(matches) == 1, f"Agente {db_spec_name} não encontrado unicamente"
    content = matches[0].read_text(encoding="utf-8")

    assert "R-064" in content, f"[{db_spec_name}] Deve citar a regra R-064"
    assert "plan_ref" in content, f"[{db_spec_name}] Deve exigir plan_ref para DDL/migrações"
    assert "pre_condicao_plano" in content, f"[{db_spec_name}] Deve retornar motivo pre_condicao_plano"
