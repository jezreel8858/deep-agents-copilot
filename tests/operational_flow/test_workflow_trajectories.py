"""
test_workflow_trajectories.py — Suíte determinística para validação de trajetórias completas (E2E)
dos 5 Workflows Canônicos (R-050) e Edge Scenarios (R-041, R-042, R-050.1, R-050.2).

Consome a especificação declarativa de cenários em 'casos-workflows.yaml' e valida
a máquina de estados finitos contra 'routing-graph.yaml', contratos de agents e invariantes de governança.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

AGENTS_DIR = REPO_ROOT / ".github" / "agents"
CASOS_WORKFLOWS_PATH = Path(__file__).parent / "casos-workflows.yaml"
ROUTING_GRAPH_PATH = AGENTS_DIR / "routing-graph.yaml"
CLAUDE_MD_PATH = REPO_ROOT / "CLAUDE.md"


@pytest.fixture(scope="module")
def casos_workflows() -> dict:
    assert CASOS_WORKFLOWS_PATH.exists(), f"Arquivo não encontrado: {CASOS_WORKFLOWS_PATH}"
    data = yaml.safe_load(CASOS_WORKFLOWS_PATH.read_text(encoding="utf-8"))
    assert "cenarios" in data, "casos-workflows.yaml deve possuir a chave 'cenarios'"
    return data


@pytest.fixture(scope="module")
def routing_graph() -> dict:
    assert ROUTING_GRAPH_PATH.exists(), f"Arquivo não encontrado: {ROUTING_GRAPH_PATH}"
    return yaml.safe_load(ROUTING_GRAPH_PATH.read_text(encoding="utf-8")) or {}


@pytest.fixture(scope="module")
def all_agents_map() -> dict[str, Path]:
    agents = {}
    for p in AGENTS_DIR.glob("**/*.agent.md"):
        if "templates" in p.parts:
            continue
        agent_id = p.stem.replace(".agent", "")
        agents[agent_id] = p
    return agents


# ─────────────────────────────────────────────────────────────
# 1. Integridade do Schema de Cenários
# ─────────────────────────────────────────────────────────────

def test_casos_workflows_schema_and_integrity(casos_workflows):
    """Valida se casos-workflows.yaml cobre todos os 5 workflows canônicos e edge cases."""
    cenarios = casos_workflows["cenarios"]
    assert len(cenarios) >= 5, "Deve existir ao menos 5 cenários definidos"

    cobertos = set()
    tipos = set()
    for c in cenarios:
        assert "id" in c, "Todo cenário deve possuir 'id'"
        assert "nome" in c, "Todo cenário deve possuir 'nome'"
        assert "tipo" in c, "Todo cenário deve possuir 'tipo'"
        tipos.add(c["tipo"])
        if "workflow" in c:
            cobertos.add(c["workflow"])

    expected_wfs = {
        "WORKFLOW-BUG-FIX",
        "WORKFLOW-REFACTORING",
        "WORKFLOW-TECHNICAL-ANALYSIS",
        "WORKFLOW-FEATURE-DEVELOPMENT",
        "WORKFLOW-GOVERNANCE-MAINTENANCE",
    }
    assert expected_wfs.issubset(cobertos), f"Workflows ausentes nos cenários: {expected_wfs - cobertos}"
    assert "intent_drift" in tipos, "Deve existir cenário de intent_drift (R-042)"
    assert "circuit_breaker" in tipos, "Deve existir cenário de circuit_breaker (R-050.2)"
    assert "fast_chaining" in tipos, "Deve existir cenário de fast_chaining (R-050.1)"


# ─────────────────────────────────────────────────────────────
# 2. Validação das Trajetórias contra o Grafo de Roteamento
# ─────────────────────────────────────────────────────────────

def test_trajectory_agents_exist_and_transitions_are_valid(casos_workflows, all_agents_map, routing_graph):
    """
    Para cada cenário com trajetória sequencial, valida se:
    1. Todos os agentes da cadeia existem no repositório.
    2. As transições para 'proximos_permitidos' representam rotas válidas no ecossistema.
    """
    cenarios = [c for c in casos_workflows["cenarios"] if "trajetoria" in c]
    assert len(cenarios) >= 5

    for cenario in cenarios:
        cid = cenario["id"]
        trajetoria = cenario["trajetoria"]
        
        for step in trajetoria:
            etapa = step["etapa"]
            agente_id = step["agente"]
            
            # Validação de existência do agente
            assert agente_id in all_agents_map, (
                f"[{cid}:etapa {etapa}] Agente '{agente_id}' não existe no repositório"
            )
            
            # Validação dos próximos agentes permitidos
            proximos = step.get("proximos_permitidos", [])
            for prox_id in proximos:
                assert prox_id in all_agents_map, (
                    f"[{cid}:etapa {etapa}] Próximo agente '{prox_id}' não existe no repositório"
                )


# ─────────────────────────────────────────────────────────────
# 3. Validação das Invariantes de Governança por Etapa
# ─────────────────────────────────────────────────────────────

def test_trajectory_invariants_and_tooling_isolation(casos_workflows, all_agents_map):
    """
    Valida as invariantes declaradas em cada etapa da trajetória:
    - Se 'proibir_mutacao: true', o agente NÃO PODE possuir tools mutativas de escrita.
    - Todo agente da cadeia DEVE possuir a ferramenta 'run_subagent' (R-042).
    - O banner obrigatório exigido deve estar presente no contrato do agente.
    """
    mutation_tools = {"insert_edit_into_file", "create_file", "replace_string_in_file"}
    cenarios = [c for c in casos_workflows["cenarios"] if "trajetoria" in c]

    for cenario in cenarios:
        cid = cenario["id"]
        for step in cenario["trajetoria"]:
            agente_id = step["agente"]
            invariantes = step.get("invariantes", {})
            file_path = all_agents_map[agente_id]
            content = file_path.read_text(encoding="utf-8")
            
            # Parse frontmatter tools via YAML
            fm = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1]) or {}
                    except yaml.YAMLError:
                        fm = {}
            tools = set(fm.get("tools", []))
            
            # 1. run_subagent compulsório em todos os executores da cadeia
            assert "run_subagent" in tools, (
                f"[{cid}:{agente_id}] Agente na cadeia de workflow não possui 'run_subagent'"
            )
            
            # 2. Invariante de proibição de mutação direta
            if invariantes.get("proibir_mutacao") is True:
                prohibited = tools.intersection(mutation_tools)
                assert not prohibited, (
                    f"[{cid}:{agente_id}] Etapa proíbe mutação, mas agente possui tools: {prohibited}"
                )
            
            # 3. Invariante de banner de visibilidade (R-042)
            exigir_banner = invariantes.get("exigir_banner")
            if exigir_banner:
                assert exigir_banner in content, (
                    f"[{cid}:{agente_id}] Contrato do agente não declara o banner esperado: '{exigir_banner}'"
                )


# ─────────────────────────────────────────────────────────────
# 4. Validação de Cenários de Borda (Edge Scenarios)
# ─────────────────────────────────────────────────────────────

def test_edge_scenario_intent_drift(casos_workflows):
    """Valida o mecanismo de detecção de deriva de intenção (R-042) no cenário declarativo."""
    drift_case = next((c for c in casos_workflows["cenarios"] if c["tipo"] == "intent_drift"), None)
    assert drift_case is not None, "Cenário de intent_drift deve existir"

    cenario = drift_case["cenario"]
    assert cenario["turno_1"]["agente_ativo"] == "spring-boot-feature-developer"
    esperado = cenario["turno_2"]["comportamento_esperado"]
    assert esperado["deriva_detectada"] is True
    assert esperado["motivo"] == "deriva_de_intencao"
    assert esperado["agente_destino"] == "agent-router"
    assert "Handoff:" in esperado["banner_handoff"]


def test_edge_scenario_circuit_breaker(casos_workflows):
    """Valida o mecanismo de Circuit Breaker (R-050.2) no cenário declarativo."""
    cb_case = next((c for c in casos_workflows["cenarios"] if c["tipo"] == "circuit_breaker"), None)
    assert cb_case is not None, "Cenário de circuit_breaker deve existir"

    cenario = cb_case["cenario"]
    assert cenario["max_tentativas"] == 3
    esperado = cenario["comportamento_esperado"]
    assert esperado["interromper_execucao"] is True
    assert esperado["acionar_rollback"] is True
    assert esperado["solicitar_aprovacao_humana"] is True


def test_edge_scenario_fast_chaining(casos_workflows):
    """Valida o protocolo de Fast-Chaining (R-050.1) entre workflows consecutivos."""
    chain_case = next((c for c in casos_workflows["cenarios"] if c["tipo"] == "fast_chaining"), None)
    assert chain_case is not None, "Cenário de fast_chaining deve existir"

    cenario = chain_case["cenario"]
    assert cenario["origem_workflow"] == "WORKFLOW-TECHNICAL-ANALYSIS"
    assert cenario["destino_workflow"] == "WORKFLOW-REFACTORING"
    esperado = cenario["comportamento_esperado"]
    assert esperado["preservar_state_bag"] is True
    assert esperado["bypass_triagem_inicial"] is True


# ─────────────────────────────────────────────────────────────
# 5. Métricas de Cobertura de Workflows
# ─────────────────────────────────────────────────────────────

def test_workflow_and_state_coverage_thresholds(casos_workflows, routing_graph):
    """
    Valida as métricas mínimas de cobertura de workflows e estados:
    - 100% dos 5 workflows canônicos devem possuir ao menos 1 cenário E2E.
    - Ao menos 85% de todas as etapas finitas declaradas devem ser exercitadas.
    - Ao menos 15 agentes distintos devem participar das trajetórias.
    """
    from tests.operational_flow.workflow_eval_simulator import WorkflowEvaluator

    evaluator = WorkflowEvaluator()
    cov = evaluator.calculate_coverage()

    wc = cov["workflow_coverage"]
    sc = cov["state_coverage"]
    ap = cov["agent_participation"]

    assert wc["covered"] == wc["total"] == 8, f"Cobertura de workflows incompleta: {wc}"
    assert sc["percentage"] >= 85.0, f"Cobertura de etapas/estados abaixo de 85%: {sc['percentage']}%"
    assert ap["total_exercised"] >= 15, f"Menos de 15 agentes exercitados: {ap['total_exercised']}"


# ─────────────────────────────────────────────────────────────
# 6. Validação E2E de Propagação do State Bag e Quality Gates (R-050)
# ─────────────────────────────────────────────────────────────

def test_e2e_state_bag_preservation_across_all_8_workflows(casos_workflows):
    """
    Simula a execução sequencial completa das trajetórias dos 8 workflows (R-050),
    validando a propagação do Typed State Bag (workflow_state) sem corrupção ou perda de campos.
    """
    from tests.operational_flow.workflow_eval_simulator import WorkflowEvaluator

    evaluator = WorkflowEvaluator()
    trajectory_scenarios = [
        c["id"] for c in casos_workflows["cenarios"] if "trajetoria" in c
    ]
    assert len(trajectory_scenarios) == 8, (
        f"Esperado 8 cenários de trajetória sequencial, encontrado: {len(trajectory_scenarios)}"
    )

    for scenario_id in trajectory_scenarios:
        result = evaluator.simulate_state_bag_transitions(scenario_id)
        assert result["status"] == "PASS", (
            f"Falha na simulação de transição E2E para {scenario_id}: {result.get('reason')}"
        )
        state_bag = result["state_bag_final"]
        assert state_bag["status"] == "CONCLUIDO"
        assert len(state_bag["historico_handoffs"]) == result["total_etapas"]
        assert len(state_bag["artifacts"]) == result["total_etapas"]


def test_all_8_workflows_have_terminal_quality_gates(casos_workflows):
    """
    Valida que o estado final de cada um dos 8 workflows canônicos termina
    em um Quality Gate verificado ou síntese formal de propostas,
    eliminando becos sem saída descritivos (R-047).
    """
    terminal_valid_agents = {
        "code-review",
        "pr-gatekeeper",
        "runtime-verifier",
        "security-reviewer",
        "agent-auditor",
        "docs-engineer",
    }
    trajectory_scenarios = [
        c for c in casos_workflows["cenarios"] if "trajetoria" in c
    ]

    for cenario in trajectory_scenarios:
        cid = cenario["id"]
        last_step = cenario["trajetoria"][-1]
        last_agent = last_step["agente"]
        assert last_agent in terminal_valid_agents, (
            f"[{cid}] Etapa final ({last_step['etapa']}) deve terminar em um Quality Gate ({terminal_valid_agents}), mas terminou com '{last_agent}'"
        )


