"""
test_e2e_writer_workflow_wiring.py — Validação determinística do wiring dos especialistas
e2e-writer nos workflows canônicos em routing-graph.yaml.

Quality Gate que garante:
1. Todo especialista do catálogo cujo nome termine em '-e2e-writer' (ex.: angular-e2e-writer)
   possui etapa correspondente em routing-graph.yaml (especificamente WORKFLOW-FEATURE-DEVELOPMENT)
   resolvendo para 'specialist-e2e-writer' (ou equivalente) e condicionada ao seu domain-router.
2. A etapa 'e2e_journey_validation' em WORKFLOW-FEATURE-DEVELOPMENT está formalizada com flag
   condicional e documentação de escopo por stack.
3. Exceções de domínio frontend (como Test-Last do Angular nas etapas red/green) permanecem
   devidamente anotadas e protegidas contra regressão acidental.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_GRAPH_PATH = REPO_ROOT / ".github" / "agents" / "routing-graph.yaml"
CATALOG_PATH = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"


def find_e2e_writer_agents() -> list[str]:
    """
    Descobre dinamicamente todos os agents cujo nome termine em '-e2e-writer'
    pesquisando no catalog.yaml, sub-catálogos locais (*-catalog.yaml) e arquivos .agent.md.
    """
    e2e_agents: set[str] = set()

    # 1. Catálogo central e related_agents
    if CATALOG_PATH.exists():
        cat_data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8")) or {}
        agents_dict = cat_data.get("agents", {})
        for agent_id, agent_meta in agents_dict.items():
            if str(agent_id).endswith("-e2e-writer"):
                e2e_agents.add(str(agent_id))
            if isinstance(agent_meta, dict):
                for rel in agent_meta.get("related_agents", []):
                    if str(rel).endswith("-e2e-writer"):
                        e2e_agents.add(str(rel))

    # 2. Sub-catálogos locais (*-catalog.yaml)
    for subcat_file in AGENTS_DIR.glob("**/*-catalog.yaml"):
        try:
            sub_data = yaml.safe_load(subcat_file.read_text(encoding="utf-8")) or {}
            for agent_id in sub_data.get("agents", {}).keys():
                if str(agent_id).endswith("-e2e-writer"):
                    e2e_agents.add(str(agent_id))
        except Exception:
            continue

    # 3. Arquivos .agent.md
    for agent_file in AGENTS_DIR.glob("**/*-e2e-writer.agent.md"):
        agent_id = agent_file.name.replace(".agent.md", "")
        e2e_agents.add(agent_id)

    return sorted(list(e2e_agents))


E2E_AGENTS = find_e2e_writer_agents()


@pytest.fixture(scope="session")
def routing_graph_data() -> dict:
    """Carrega o conteúdo parseado de routing-graph.yaml."""
    assert ROUTING_GRAPH_PATH.exists(), f"routing-graph.yaml não encontrado em {ROUTING_GRAPH_PATH}"
    content = ROUTING_GRAPH_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(content) or {}


def test_at_least_one_e2e_writer_discovered():
    """Garante que pelo menos o angular-e2e-writer foi descoberto no ecossistema."""
    assert len(E2E_AGENTS) > 0, "Nenhum agent terminando em '-e2e-writer' foi descoberto no catálogo"
    assert "angular-e2e-writer" in E2E_AGENTS, "angular-e2e-writer DEVE estar presente no catálogo de agentes"


@pytest.mark.parametrize("e2e_agent", E2E_AGENTS)
def test_e2e_writer_is_wired_in_routing_graph_workflows(routing_graph_data: dict, e2e_agent: str):
    """
    Valida que para cada e2e-writer descoberto existe ao menos uma etapa em routing-graph.yaml
    cujo agent resolva para 'specialist-e2e-writer' (ou nome do agente) condicionada ao seu domain-router.
    """
    # Ex: 'angular-e2e-writer' -> domain_router: 'angular-router'
    stack_prefix = e2e_agent.replace("-e2e-writer", "")
    domain_router = f"{stack_prefix}-router"

    workflows = routing_graph_data.get("workflows", [])
    matching_steps = []

    for wf in workflows:
        estados = wf.get("estados", [])
        for estado in estados:
            agent_field = str(estado.get("agent", ""))
            aplicavel_quando = str(estado.get("aplicavel_quando", ""))
            nota = str(estado.get("nota", ""))
            resolvido_por = str(estado.get("resolvido_por", ""))

            agent_matches = (
                "specialist-e2e-writer" in agent_field
                or e2e_agent in agent_field
                or "e2e-writer" in agent_field
            )
            router_matches = (
                domain_router in aplicavel_quando
                or domain_router in nota
                or domain_router in resolvido_por
            )

            if agent_matches and router_matches:
                matching_steps.append((wf.get("id"), estado.get("nome"), estado))

    assert len(matching_steps) > 0, (
        f"Nenhuma etapa em routing-graph.yaml encontrada para {e2e_agent} "
        f"com resolução specialist-e2e-writer condicionada a {domain_router}"
    )


def test_workflow_feature_development_contains_e2e_journey_validation(routing_graph_data: dict):
    """
    Garante especificamente que WORKFLOW-FEATURE-DEVELOPMENT possui a etapa 'e2e_journey_validation'
    referenciando specialist-e2e-writer e condicionada ao domain-router do Angular.
    """
    workflows = routing_graph_data.get("workflows", [])
    wf_feat = next((wf for wf in workflows if wf.get("id") == "WORKFLOW-FEATURE-DEVELOPMENT"), None)
    assert wf_feat is not None, "WORKFLOW-FEATURE-DEVELOPMENT deve existir em routing-graph.yaml"

    estados = wf_feat.get("estados", [])
    e2e_step = next((e for e in estados if e.get("nome") == "e2e_journey_validation"), None)
    assert e2e_step is not None, "Etapa 'e2e_journey_validation' DEVE existir em WORKFLOW-FEATURE-DEVELOPMENT"

    agent_field = str(e2e_step.get("agent", ""))
    assert "specialist-e2e-writer" in agent_field, (
        f"Etapa e2e_journey_validation deve definir agent como 'specialist-e2e-writer', obtido: '{agent_field}'"
    )

    aplicavel_quando = str(e2e_step.get("aplicavel_quando", ""))
    assert "angular-router" in aplicavel_quando, (
        f"Etapa e2e_journey_validation deve ser condicionada ao angular-router, obtido: '{aplicavel_quando}'"
    )

    assert e2e_step.get("condicional") is True, (
        "Etapa e2e_journey_validation deve possuir flag 'condicional: true'"
    )


def test_workflow_feature_development_red_green_has_frontend_domain_exception(routing_graph_data: dict):
    """
    Valida que as etapas 5 e 6 (red_test_authoring e green_implementation) de WORKFLOW-FEATURE-DEVELOPMENT
    em routing-graph.yaml possuem a anotação excecao_dominio_frontend documentando o desvio Test-Last do Angular.
    """
    workflows = routing_graph_data.get("workflows", [])
    wf_feat = next((wf for wf in workflows if wf.get("id") == "WORKFLOW-FEATURE-DEVELOPMENT"), None)
    assert wf_feat is not None, "WORKFLOW-FEATURE-DEVELOPMENT deve existir em routing-graph.yaml"

    estados = wf_feat.get("estados", [])
    step_red = next((e for e in estados if e.get("nome") == "red_test_authoring"), None)
    step_green = next((e for e in estados if e.get("nome") == "green_implementation"), None)

    assert step_red is not None, "Etapa 'red_test_authoring' deve existir"
    assert step_green is not None, "Etapa 'green_implementation' deve existir"

    # Etapa 5 (Red)
    exc_red = step_red.get("excecao_dominio_frontend", "")
    assert exc_red, "Etapa red_test_authoring DEVE possuir anotação 'excecao_dominio_frontend'"
    assert "angular-router" in exc_red, "excecao_dominio_frontend da etapa red DEVE citar 'angular-router'"
    assert "Test-Last" in exc_red or "Implementation-First" in exc_red, (
        "excecao_dominio_frontend da etapa red DEVE explicitar o paradigma Test-Last / Implementation-First"
    )

    # Etapa 6 (Green)
    exc_green = step_green.get("excecao_dominio_frontend", "")
    assert exc_green, "Etapa green_implementation DEVE possuir anotação 'excecao_dominio_frontend'"
    assert "angular-router" in exc_green, "excecao_dominio_frontend da etapa green DEVE citar 'angular-router'"
    assert "Test-Last" in exc_green or "Implementation-First" in exc_green, (
        "excecao_dominio_frontend da etapa green DEVE explicitar o paradigma Test-Last / Implementation-First"
    )
