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
    "code-summarizer",
    "context-builder",
    "angular-engineer",
    "spring-boot-engineer",
    "spring-reactive-engineer",
    "test-engineer",
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
    # Ampliação carry-forward (auditoria Workflow 3 — 2026-09): especialistas read-only
    # despachados por WORKFLOW-TECHNICAL-ANALYSIS sem cobertura de teste equivalente.
    "code-knowledge-graph",
    "devops-engineer",
    "tech-solution-architect",
    "angular-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "ejb-arch-advisor",
    "oracle-query-tuner",
    "informix-query-tuner",
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


def test_workflows_support_fast_chaining_circuit_breaker_and_multi_project():
    """Valida que workflows.md documenta Fast-Chaining (R-050.1), Circuit Breaker/Rollback (R-050.2)
    e Multi-Project Target Tracking (R-050.3)."""
    content = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "Fast-Chaining" in content, "workflows.md deve especificar o protocolo de Fast-Chaining"
    assert "Circuit Breaker" in content, "workflows.md deve especificar o Circuit Breaker"
    assert "projeto_alvo" in content, "workflows.md deve especificar o rastreamento de projeto_alvo"
    assert "carry_over_state" in content, "workflows.md deve especificar a transferência de estado no chaining"


def test_handoff_governance_v13_schema():
    """Valida que handoff-governance/SKILL.md formaliza a v1.3 com projeto_alvo e chaining."""
    content = HANDOFF_SKILL_PATH.read_text(encoding="utf-8")
    assert 'versao: "1.3"' in content, "SKILL.md deve declarar versao 1.3 do schema"
    assert "projeto_alvo:" in content, "SKILL.md deve conter projeto_alvo no workflow_tracking"
    assert "chaining:" in content, "SKILL.md deve conter chaining no workflow_tracking"
    assert "root_path:" in content, "SKILL.md deve declarar root_path do projeto alvo"


def test_agent_router_fast_chaining_and_target_project():
    """Valida que agent-router.agent.md formaliza o Fast-Chaining e a resolução de projeto-alvo."""
    router_path = AGENTS_DIR / "agent-router.agent.md"
    content = router_path.read_text(encoding="utf-8")
    assert "Fast-Chaining" in content, "agent-router deve conter regra de Fast-Chaining"
    assert "workflow_tracking.projeto_alvo" in content, "agent-router deve resolver projeto_alvo"


def test_workflow_bug_fix_edge_scenarios_and_state_bag(routing_graph):
    """Valida que WORKFLOW-BUG-FIX cobre cenários de layout, DDL, repro gate, baseline e typed state bag."""
    content_wf = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "Repro Gate" in content_wf, "workflows.md deve especificar o Repro Gate para bugs intermitentes"
    assert "Layout Spec" in content_wf, "workflows.md deve especificar a ramificação de Layout/CSS"
    assert "Migração DDL" in content_wf, "workflows.md deve cobrir dependência de DDL via database-specialist"
    assert "workflow_state:" in content_wf, "workflows.md deve definir o Typed State Bag do Workflow 1"

    # Validação estrutural no routing-graph.yaml
    wf1 = next((wf for wf in routing_graph.get("workflows", []) if wf["id"] == "WORKFLOW-BUG-FIX"), None)
    assert wf1 is not None, "WORKFLOW-BUG-FIX deve existir no routing-graph.yaml"
    estados = wf1.get("estados", [])
    assert any("ui-stylist" in e.get("agent", "") for e in estados), "Workflow 1 deve incluir ui-stylist para layout"
    assert any("database-specialist" in str(e.get("sub_rotinas_permitidas", [])) for e in estados), "Workflow 1 deve suportar database-specialist"

def test_workflow_refactoring_edge_scenarios_and_state_bag(routing_graph):
    """Valida que WORKFLOW-REFACTORING cobre cenários de Golden Master, Breaking Changes,
    Expand and Contract (BD), Árvore Mikado e Typed State Bag."""
    content_wf = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "Golden Master" in content_wf, "workflows.md deve especificar Golden Master Safety Net para código legado"
    assert "Contract & Deprecation Plan" in content_wf, "workflows.md deve cobrir gate de breaking change"
    assert "Expand and Contract" in content_wf, "workflows.md deve cobrir refatoração de schema de banco"
    assert "Mikado Method" in content_wf, "workflows.md deve documentar decomposição Mikado"
    assert "alvo_refatoracao:" in content_wf, "workflows.md deve definir o Typed State Bag do Workflow 2"

    # Validação estrutural no routing-graph.yaml
    wf2 = next((wf for wf in routing_graph.get("workflows", []) if wf["id"] == "WORKFLOW-REFACTORING"), None)
    assert wf2 is not None, "WORKFLOW-REFACTORING deve existir no routing-graph.yaml"
    estados = wf2.get("estados", [])
    assert any("golden master" in str(e.get("safety_net_gate", "")) for e in estados), "Workflow 2 deve ter safety_net_gate"
    assert any("tech-solution-architect" in str(e.get("sub_rotinas_permitidas", [])) for e in estados), "Workflow 2 deve ter sub-rotina de contratos"
    assert any("database-specialist" in str(e.get("sub_rotinas_permitidas", [])) for e in estados), "Workflow 2 deve suportar database-specialist"
    assert any("mikado_method" in str(e.get("estrategia_decomposicao", "")) for e in estados), "Workflow 2 deve declarar mikado_method"

def test_workflow_technical_analysis_edge_scenarios_and_proposals(routing_graph):
    """Valida que WORKFLOW-TECHNICAL-ANALYSIS cobre arquitetura de stack (Angular, Spring, EJB),
    análise composta, tabela de propostas acionáveis para Fast-Chaining e Typed State Bag."""
    content_wf = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "angular-arch-advisor" in content_wf, "workflows.md deve incluir angular-arch-advisor"
    assert "spring-boot-arch-advisor" in content_wf, "workflows.md deve incluir spring-boot-arch-advisor"
    assert "Sub-rotina Analítica Composta" in content_wf, "workflows.md deve especificar análise composta"
    assert "Tabela Mandatória de Propostas Acionáveis" in content_wf, "workflows.md deve exigir tabela de propostas"
    assert "propostas_acionaveis:" in content_wf, "workflows.md deve definir propostas_acionaveis no State Bag"

    # Validação estrutural no routing-graph.yaml
    wf3 = next((wf for wf in routing_graph.get("workflows", []) if wf["id"] == "WORKFLOW-TECHNICAL-ANALYSIS"), None)
    assert wf3 is not None, "WORKFLOW-TECHNICAL-ANALYSIS deve existir no routing-graph.yaml"
    estados = wf3.get("estados", [])
    etapa1 = next((e for e in estados if e["etapa"] == 1), {})
    permitidos = etapa1.get("agents_permitidos", [])
    assert "angular-arch-advisor" in permitidos, "Workflow 3 deve permitir angular-arch-advisor"
    assert "spring-boot-arch-advisor" in permitidos, "Workflow 3 deve permitir spring-boot-arch-advisor"
    assert "oracle-query-tuner" in permitidos, "Workflow 3 deve permitir query tuners"

def test_workflow_feature_development_edge_scenarios_and_state_bag(routing_graph):
    """Valida que WORKFLOW-FEATURE-DEVELOPMENT cobre particionamento de escopo (Fullstack/Back/Front),
    Checkpoint de Blueprint, Contract-First TDD, Security Gate (OWASP) e Typed State Bag."""
    content_wf = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "Checkpoint de Blueprint" in content_wf, "workflows.md deve exigir Checkpoint de Blueprint"
    assert "Contract-First" in content_wf, "workflows.md deve exigir Contract-First TDD"
    assert "Security Review (OWASP)" in content_wf, "workflows.md deve incluir security-reviewer no gate"
    assert "feature_id:" in content_wf, "workflows.md deve definir Typed State Bag do Workflow 4"

    # Validação estrutural no routing-graph.yaml
    wf4 = next((wf for wf in routing_graph.get("workflows", []) if wf["id"] == "WORKFLOW-FEATURE-DEVELOPMENT"), None)
    assert wf4 is not None, "WORKFLOW-FEATURE-DEVELOPMENT deve existir no routing-graph.yaml"
    estados = wf4.get("estados", [])
    etapa3 = next((e for e in estados if e["etapa"] == 3), {})
    assert "aprovacao_blueprint" in str(etapa3.get("checkpoint_humano", "")), "Workflow 4 deve ter checkpoint_humano na etapa 3"
    assert "fullstack" in str(etapa3.get("particionamento_escopo", [])), "Workflow 4 deve suportar particionamento de escopo"

    etapa6 = next((e for e in estados if e["etapa"] == 6), {})
    assert "security-reviewer" in str(etapa6.get("sub_rotinas_permitidas", [])), "Workflow 4 deve ter security-reviewer no gate"

def test_workflow_governance_maintenance_edge_scenarios_and_state_bag(routing_graph):
    """Valida que WORKFLOW-GOVERNANCE-MAINTENANCE cobre pesquisa prévia de mercado via deep-search,
    Checkpoint de Aprovação Humana, Sincronização Quádrupla SSOT (R-015), Quality Gate Tier 1 e State Bag."""
    content_wf = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "Pesquisa Prévia de Mercado" in content_wf, "workflows.md deve especificar pesquisa prévia"
    assert "Checkpoint de Aprovação" in content_wf, "workflows.md deve exigir aprovação humana"
    assert "Sincronização Quádrupla SSOT" in content_wf, "workflows.md deve exigir sincronização quádrupla R-015"
    assert "Quality Gate de Governança (Tier 1)" in content_wf, "workflows.md deve incluir gate de testes de governança"
    assert "tipo_demanda:" in content_wf, "workflows.md deve definir Typed State Bag do Workflow 5"

    # Validação estrutural no routing-graph.yaml
    wf5 = next((wf for wf in routing_graph.get("workflows", []) if wf["id"] == "WORKFLOW-GOVERNANCE-MAINTENANCE"), None)
    assert wf5 is not None, "WORKFLOW-GOVERNANCE-MAINTENANCE deve existir no routing-graph.yaml"
    estados = wf5.get("estados", [])
    etapa1 = next((e for e in estados if e["etapa"] == 1), {})
    assert "deep-search" in str(etapa1.get("sub_rotinas_permitidas", [])), "Workflow 5 deve permitir deep-search na etapa 1"

    etapa3 = next((e for e in estados if e["etapa"] == 3), {})
    assert etapa3.get("sincronizacao_quadrupla_r015") is True, "Workflow 5 deve declarar sincronizacao_quadrupla_r015"

    etapa4 = next((e for e in estados if e["etapa"] == 4), {})
    assert "pytest" in str(etapa4.get("validacao_automatizada", "")), "Workflow 5 deve ter validação automatizada na etapa 4"



def test_workflow_dependency_remediation_edge_scenarios_and_state_bag(routing_graph):
    """Valida que WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION cobre triagem SCA, blast radius,
    bump de manifesto, adaptação de breaking changes e Typed State Bag."""
    content_wf = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION" in content_wf
    assert "Triagem de Vulnerabilidade & Advisory" in content_wf
    assert "Mapeamento de Blast Radius da Dependência" in content_wf
    assert "tipo_remediacao:" in content_wf, "workflows.md deve definir Typed State Bag do Workflow 6"

    wf6 = next((wf for wf in routing_graph.get("workflows", []) if wf["id"] == "WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION"), None)
    assert wf6 is not None, "WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION deve existir no routing-graph.yaml"
    estados = wf6.get("estados", [])
    etapa1 = next((e for e in estados if e["etapa"] == 1), {})
    assert "security-reviewer" in etapa1.get("agent", "")
    etapa2 = next((e for e in estados if e["etapa"] == 2), {})
    assert "code-knowledge-graph" in etapa2.get("agent", "")


def test_workflow_framework_migration_edge_scenarios_and_state_bag(routing_graph):
    """Valida que WORKFLOW-FRAMEWORK-MIGRATION cobre avaliação de compatibilidade pre-flight,
    decomposição em fases, codemods automatizados, testes de paridade e State Bag."""
    content_wf = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "WORKFLOW-FRAMEWORK-MIGRATION" in content_wf
    assert "Pre-Flight Compatibility Assessment" in content_wf
    assert "Migration Phasing & Blueprint" in content_wf
    assert "stack_migracao:" in content_wf, "workflows.md deve definir Typed State Bag do Workflow 7"

    wf7 = next((wf for wf in routing_graph.get("workflows", []) if wf["id"] == "WORKFLOW-FRAMEWORK-MIGRATION"), None)
    assert wf7 is not None, "WORKFLOW-FRAMEWORK-MIGRATION deve existir no routing-graph.yaml"
    estados = wf7.get("estados", [])
    etapa1 = next((e for e in estados if e["etapa"] == 1), {})
    assert "tech-solution-architect" in etapa1.get("agent", "")
    etapa2 = next((e for e in estados if e["etapa"] == 2), {})
    assert "aprovacao_fases_migracao" in str(etapa2.get("checkpoint_humano", ""))


def test_workflow_release_readiness_edge_scenarios_and_state_bag(routing_graph):
    """Valida que WORKFLOW-RELEASE-READINESS cobre auditoria de contratos OpenAPI, rollout DDL
    com rollback testado, varredura de segredos, packaging semântico e State Bag."""
    content_wf = WORKFLOWS_MD_PATH.read_text(encoding="utf-8")
    assert "WORKFLOW-RELEASE-READINESS" in content_wf
    assert "Contract & API Compatibility Audit" in content_wf
    assert "Database Rollout Pre-Flight" in content_wf
    assert "release_versao:" in content_wf, "workflows.md deve definir Typed State Bag do Workflow 8"

    wf8 = next((wf for wf in routing_graph.get("workflows", []) if wf["id"] == "WORKFLOW-RELEASE-READINESS"), None)
    assert wf8 is not None, "WORKFLOW-RELEASE-READINESS deve existir no routing-graph.yaml"
    estados = wf8.get("estados", [])
    etapa1 = next((e for e in estados if e["etapa"] == 1), {})
    assert "tech-solution-architect" in etapa1.get("agent", "")
    etapa2 = next((e for e in estados if e["etapa"] == 2), {})
    assert "database-specialist" in etapa2.get("agent", "")
    etapa4 = next((e for e in estados if e["etapa"] == 4), {})
    assert "pr-gatekeeper" in etapa4.get("agent", "")
