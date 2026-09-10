"""
test_operational_workflows.py — Suíte determinística para validar o fluxo operacional e
a integridade de transição entre agents (Operational Dynamic Compliance).

Cobre:
1. Validação estática e semântica dos diagramas Mermaid no README.md (Fluxo Operacional e Mapa de Perfis).
2. Consistência e alcançabilidade dos alvos declarados na seção 'Quando Delegar' de cada agent.
3. Conformidade dos 'Golden Paths' operacionais (R-041, R-045, R-047 e pesquisa prévia de governança).
4. Isolamento operacional de agents Read-Only / Advisory (prevenção de mutação direta).
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
ROUTING_GRAPH_PATH = AGENTS_DIR / "routing-graph.yaml"
README_PATH = REPO_ROOT / "README.md"

LEGACY_DEPRECATED_AGENTS = {
    "docs-writer",
    "docs-curator",
    "agent-factory",
    "skill-factory",
    "prompt-factory",
    "impact-architect",
    "test-implementation",
    "test-fix",
}

READONLY_ADVISORY_AGENTS = {
    "agent-auditor",
    "adr-sentinel",
    "ddd-bounded-context-mapper",
    "compliance-guardrails",
    "security-reviewer",
    "performance-agent",
    "code-style-enforcer",
    "runtime-verifier",
}


@pytest.fixture(scope="module")
def all_existing_agents() -> dict[str, Path]:
    agents = {}
    for p in AGENTS_DIR.glob("**/*.agent.md"):
        if "templates" in p.parts:
            continue
        agent_id = p.stem.replace(".agent", "")
        agents[agent_id] = p
    return agents


@pytest.fixture(scope="module")
def routing_graph():
    assert ROUTING_GRAPH_PATH.exists()
    with open(ROUTING_GRAPH_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_readme_mermaid_syntax_and_integrity(all_existing_agents):
    """Valida se os blocos Mermaid em README.md possuem sintaxe válida e referenciam agents reais"""
    assert README_PATH.exists()
    content = README_PATH.read_text(encoding="utf-8")
    blocks = re.findall(r'```mermaid[\r\n]+(.*?)[\r\n]+```', content, re.DOTALL)
    assert len(blocks) >= 2, "README.md deve conter ao menos 2 diagramas Mermaid (Fluxo e Perfis)"

    # Diagrama 0: Fluxo operacional
    fluxo_op = blocks[0]
    assert "flowchart TD" in fluxo_op or "graph TD" in fluxo_op

    # Diagrama 1: Mapa de agents por perfil
    mapa_perfis = blocks[1]
    assert "graph TB" in mapa_perfis or "flowchart TB" in mapa_perfis

    for idx, block in enumerate(blocks):
        assert block.count("[") == block.count("]"), f"Diagrama #{idx}: colchetes desbalanceados"
        assert block.count("{") == block.count("}"), f"Diagrama #{idx}: chaves desbalanceadas"

        for legacy in LEGACY_DEPRECATED_AGENTS:
            assert legacy not in block, f"Diagrama #{idx} cita agent obsoleto '{legacy}'"

        normalized_block = block.replace("\\n", " ")
        words = re.findall(r'\b[a-z][a-z0-9]+-[a-z0-9-]+\b', normalized_block)
        for w in words:
            if w.startswith("init-") or w.startswith("add-") or w in {"sub-rotina", "rule-based", "full-text", "deep-search"}:
                continue
            if w in all_existing_agents:
                continue
            agent_suffixes = ["router", "engineer", "specialist", "mapper", "sentinel", "auditor", "planner", "reviewer", "verifier", "triage", "extractor", "summarizer", "gatekeeper", "structuring"]
            if any(part in w for part in agent_suffixes):
                assert w in all_existing_agents, f"Diagrama #{idx} em README.md cita agent desconhecido: '{w}'"


def test_readme_diagrams_cover_all_routing_graph_agents(routing_graph):
    """Garante que 100% dos agents downstream e fallback declarados no routing-graph.yaml
    estão devidamente representados nos diagramas do README.md (Fluxo Operacional e Mapa de Perfis)."""
    content = README_PATH.read_text(encoding="utf-8")
    blocks = re.findall(r'```mermaid[\r\n]+(.*?)[\r\n]+```', content, re.DOTALL)
    assert len(blocks) >= 2, "README.md deve conter ao menos 2 diagramas Mermaid"
    fluxo_op = blocks[0]
    mapa_perfis = blocks[1]

    # Coleta todos os nós downstream e fallback que devem constar na visão arquitetural
    graph_agents = [
        node["id"]
        for node in routing_graph.get("nos", [])
        if node.get("tipo") in {"downstream", "fallback"}
    ]

    missing_in_fluxo = [a for a in graph_agents if a not in fluxo_op]
    assert not missing_in_fluxo, (
        f"Diagrama 'Fluxo operacional' no README.md não cobre os seguintes agents do grafo: {missing_in_fluxo}"
    )

    missing_in_mapa = [a for a in graph_agents if a not in mapa_perfis]
    assert not missing_in_mapa, (
        f"Diagrama 'Mapa de Perfis' no README.md não cobre os seguintes agents do grafo: {missing_in_mapa}"
    )


def test_when_delegating_targets_are_real_agents(all_existing_agents):
    """Valida se todo agent citado na seção 'Quando Delegar' de cada .agent.md existe no catálogo"""
    for agent_id, file_path in all_existing_agents.items():
        content = file_path.read_text(encoding="utf-8")
        if "## Quando Delegar" not in content:
            continue

        quando_delegar_section = content.split("## Quando Delegar", 1)[1]
        if "\n## " in quando_delegar_section:
            quando_delegar_section = quando_delegar_section.split("\n## ", 1)[0]

        targets = set()
        # Captura @agent-name mas ignora escopos de pacotes npm como @optave/codegraph
        raw_mentions = re.findall(r'@([a-z0-9-]+(?:/[a-z0-9-]+)?)', quando_delegar_section)
        for m in raw_mentions:
            if "/" not in m:
                targets.add(m)
        targets.update(re.findall(r'\[@?([a-z0-9-]+)\]\(', quando_delegar_section))

        for target in targets:
            if target in {"agent", "plan", "commit", "review", "implement", "validate", "audit"}:
                continue
            assert target in all_existing_agents, f"[{file_path.name}] Seção 'Quando Delegar' referencia agent inexistente: '@{target}'"
            assert target not in LEGACY_DEPRECATED_AGENTS, f"[{file_path.name}] Seção 'Quando Delegar' referencia agent obsoleto: '@{target}'"


def test_operational_golden_path_router_to_prompt_structuring(routing_graph):
    """Golden Path 1 (R-041): agent-router deve obrigatoriamente rotear primeiro para prompt-structuring"""
    arestas = routing_graph["arestas"]
    has_r041_edge = any(
        a.get("de") == "agent-router" and a.get("para") == "prompt-structuring"
        for a in arestas
    )
    assert has_r041_edge


def test_operational_golden_path_refactor_requires_codegraph(all_existing_agents):
    """Golden Path 2 (R-045): refactor-planner deve delegar compulsoriamente para code-knowledge-graph"""
    planner_file = all_existing_agents.get("refactor-planner")
    assert planner_file is not None
    content = planner_file.read_text(encoding="utf-8")
    assert "code-knowledge-graph" in content


def test_operational_golden_path_governance_factory_requires_deep_search(all_existing_agents):
    """Golden Path 3: governance-factory deve delegar pesquisa prévia de mercado para deep-search"""
    factory_file = all_existing_agents.get("governance-factory")
    assert factory_file is not None
    content = factory_file.read_text(encoding="utf-8")
    assert "deep-search" in content


def test_operational_golden_path_ddd_mapper_requires_codegraph(all_existing_agents):
    """Golden Path 4: ddd-bounded-context-mapper deve consumir o mapa estrutural de code-knowledge-graph"""
    ddd_file = all_existing_agents.get("ddd-bounded-context-mapper")
    assert ddd_file is not None
    content = ddd_file.read_text(encoding="utf-8")
    assert "code-knowledge-graph" in content


def test_readonly_advisory_agents_do_not_contain_mutation_tools(all_existing_agents):
    """Valida se nenhum agent Read-Only possui ferramentas de mutação direta no frontmatter"""
    mutation_tools = {"create_file", "insert_edit_into_file", "replace_string_in_file"}

    for agent_id in READONLY_ADVISORY_AGENTS:
        file_path = all_existing_agents.get(agent_id)
        assert file_path is not None
        content = file_path.read_text(encoding="utf-8")

        tools_match = re.search(r'tools:\s*(\[[^\]]*\])', content)
        if tools_match:
            tools = tools_match.group(1)
            for m_tool in mutation_tools:
                assert m_tool not in tools, f"Agent Read-Only '{agent_id}' possui tool mutativa: '{m_tool}'"


WORKFLOWS_MD_PATH = AGENTS_DIR / "workflows.md"
CLAUDE_MD_PATH = REPO_ROOT / "CLAUDE.md"
HANDOFF_SKILL_PATH = REPO_ROOT / ".github" / "skills" / "handoff-governance" / "SKILL.md"
CANONICAL_WORKFLOW_IDS = {
    "WORKFLOW-BUG-FIX",
    "WORKFLOW-REFACTORING",
    "WORKFLOW-TECHNICAL-ANALYSIS",
    "WORKFLOW-FEATURE-DEVELOPMENT",
    "WORKFLOW-GOVERNANCE-MAINTENANCE",
}
def test_workflows_specification_file_exists_and_covers_all_five():
    """Valida que workflows.md existe, possui sintaxe válida e cobre os 5 workflows canônicos (R-050)."""
    assert WORKFLOWS_MD_PATH.exists(), f"Arquivo de especificação não encontrado: {WORKFLOWS_MD_PATH}"
    content = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    for wf_id in CANONICAL_WORKFLOW_IDS:
        assert wf_id in content, f"workflows.md deve especificar o workflow: {wf_id}"
    assert "workflow_tracking" in content, "workflows.md deve documentar o bloco workflow_tracking de handoff"
def test_routing_graph_declares_all_five_workflows(routing_graph):
    """Valida que routing-graph.yaml declara o bloco 'workflows' com os 5 pipelines e estados finitos."""
    assert "workflows" in routing_graph, "routing-graph.yaml deve conter bloco 'workflows' (R-050)"
    declared_wf_ids = {wf["id"] for wf in routing_graph["workflows"]}
    assert CANONICAL_WORKFLOW_IDS.issubset(declared_wf_ids), (
        f"routing-graph.yaml deve conter todos os 5 workflows canônicos. Declarados: {declared_wf_ids}"
    )
    for wf in routing_graph["workflows"]:
        assert "estados" in wf, f"Workflow {wf['id']} deve declarar lista de estados"
        assert len(wf["estados"]) >= 3, f"Workflow {wf['id']} deve ter ao menos 3 etapas de execução"
        assert "gatilhos" in wf, f"Workflow {wf['id']} deve listar gatilhos de ativação"
def test_fast_path_bypass_in_prompt_structuring_edge(routing_graph):
    """Valida que a aresta de prompt-structuring possui gatilho de fast_path_bypass configurado."""
    structuring_edge = next(
        (a for a in routing_graph["arestas"] if a.get("para") == "prompt-structuring"),
        None,
    )
    assert structuring_edge is not None, "Aresta para prompt-structuring não encontrada"
    condicoes = structuring_edge.get("condicoes", {})
    assert "fast_path_bypass" in condicoes, "Aresta prompt-structuring deve declarar 'fast_path_bypass'"
def test_r050_and_r041_normative_rules_in_claude_md():
    """Valida que CLAUDE.md possui R-050 formalizada e R-041 com Fast-Path determinístico."""
    content = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    assert "R-050" in content, "CLAUDE.md deve formalizar a regra R-050"
    assert "WORKFLOW-BUG-FIX" in content, "CLAUDE.md R-050 deve declarar WORKFLOW-BUG-FIX"
    assert "Fast-Path" in content, "CLAUDE.md deve documentar a política de Fast-Path"
def test_handoff_governance_supports_workflow_tracking():
    """Valida que handoff-governance/SKILL.md inclui o schema de workflow_tracking."""
    content = HANDOFF_SKILL_PATH.read_text(encoding="utf-8")
    assert "workflow_tracking:" in content
    assert "workflow_id:" in content
    assert "etapa_atual:" in content
    assert "proximos_agentes_permitidos:" in content
