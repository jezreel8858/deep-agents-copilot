"""
test_spring_reactive_perf_tuner_registration.py — Validação determinística do registro
e wiring do especialista spring-reactive-perf-tuner no ecossistema reativo.

Quality Gate que garante:
1. O arquivo .github/agents/backend/spring-reactive/spring-reactive-perf-tuner.agent.md existe.
2. Está formalmente registrado no sub-catálogo spring-reactive-catalog.yaml com role 'performance'.
3. É referenciado na Decision Tree do supervisor spring-reactive-router.agent.md.
4. Possui entrada no catalog.yaml raiz (sob related_agents do spring-reactive-router e contagem de 7 especialistas).
5. O supervisor spring-reactive-router em routing-graph.yaml referencia o sub-catálogo de 7 especialistas.
"""
from __future__ import annotations

import re
from pathlib import Path
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
SR_DIR = REPO_ROOT / ".github" / "agents" / "backend" / "spring-reactive"
AGENT_FILE = SR_DIR / "spring-reactive-perf-tuner.agent.md"
SUB_CATALOG_FILE = SR_DIR / "spring-reactive-catalog.yaml"
ROUTER_FILE = SR_DIR / "spring-reactive-router.agent.md"
ROOT_CATALOG_FILE = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
ROUTING_GRAPH_FILE = REPO_ROOT / ".github" / "agents" / "routing-graph.yaml"


def test_spring_reactive_perf_tuner_file_exists():
    """Valida a existência do arquivo spring-reactive-perf-tuner.agent.md."""
    assert AGENT_FILE.exists(), remediation(
        f"Arquivo não encontrado: {AGENT_FILE}",
        fix_hint="Crie o especialista spring-reactive-perf-tuner.agent.md no diretório spring-reactive."
    )


def test_spring_reactive_perf_tuner_sub_catalog_registration():
    """Valida que o agente está registrado no spring-reactive-catalog.yaml com role e id corretos."""
    assert SUB_CATALOG_FILE.exists(), remediation(
        f"Sub-catálogo não encontrado: {SUB_CATALOG_FILE}",
        fix_hint="Verifique o arquivo spring-reactive-catalog.yaml."
    )
    data = yaml.safe_load(SUB_CATALOG_FILE.read_text(encoding="utf-8")) or {}
    agents = data.get("agents", {})

    assert "spring-reactive-perf-tuner" in agents, remediation(
        "spring-reactive-perf-tuner ausente na seção 'agents' de spring-reactive-catalog.yaml",
        fix_hint="Adicione a entrada 'spring-reactive-perf-tuner' com role 'performance' no sub-catálogo."
    )

    perf_entry = agents["spring-reactive-perf-tuner"]
    assert perf_entry.get("role") == "performance", remediation(
        f"Role esperado 'performance', encontrado '{perf_entry.get('role')}'",
        fix_hint="Defina role: 'performance' no spring-reactive-catalog.yaml."
    )


def test_spring_reactive_perf_tuner_router_decision_tree_reference():
    """Valida que o router spring-reactive-router.agent.md referencia o perf-tuner na Decision Tree."""
    assert ROUTER_FILE.exists(), remediation(
        f"Router não encontrado: {ROUTER_FILE}",
        fix_hint="Verifique a existência do spring-reactive-router.agent.md."
    )
    content = ROUTER_FILE.read_text(encoding="utf-8")

    assert "@spring-reactive-perf-tuner" in content, remediation(
        "Referência a '@spring-reactive-perf-tuner' ausente no spring-reactive-router.agent.md",
        fix_hint="Inclua '@spring-reactive-perf-tuner' na Decision Tree do router reativo."
    )
    assert "specialist-perf-tuner" in content, remediation(
        "Slot lógico 'specialist-perf-tuner' ausente no spring-reactive-router.agent.md",
        fix_hint="Vincule 'specialist-perf-tuner' -> '@spring-reactive-perf-tuner' na Decision Tree."
    )


def test_spring_reactive_perf_tuner_root_catalog_and_routing_graph_parity():
    """
    Valida a paridade no catalog.yaml raiz e routing-graph.yaml:
    (a) catalog.yaml lista spring-reactive-perf-tuner em related_agents e menciona 7 especialistas;
    (b) routing-graph.yaml referencia o catálogo com 7 especialistas no nó ou aresta.
    """
    assert ROOT_CATALOG_FILE.exists(), remediation(
        f"catalog.yaml não encontrado em {ROOT_CATALOG_FILE}",
        fix_hint="Verifique a existência do catalog.yaml raiz."
    )
    cat_data = yaml.safe_load(ROOT_CATALOG_FILE.read_text(encoding="utf-8")) or {}
    sr_router = cat_data.get("agents", {}).get("spring-reactive-router", {})

    related = sr_router.get("related_agents", [])
    assert "spring-reactive-perf-tuner" in related, remediation(
        "'spring-reactive-perf-tuner' ausente em related_agents do spring-reactive-router no catalog.yaml raiz",
        fix_hint="Adicione 'spring-reactive-perf-tuner' à lista related_agents de spring-reactive-router no catalog.yaml."
    )

    desc = sr_router.get("description", "")
    assert "7 especialistas" in desc or "7" in desc, remediation(
        "Descrição do spring-reactive-router no catalog.yaml raiz não reflete os 7 especialistas.",
        fix_hint="Atualize a contagem na descrição de spring-reactive-router no catalog.yaml para 7 especialistas."
    )

    assert ROUTING_GRAPH_FILE.exists(), remediation(
        f"routing-graph.yaml não encontrado em {ROUTING_GRAPH_FILE}",
        fix_hint="Verifique o arquivo routing-graph.yaml."
    )
    rg_text = ROUTING_GRAPH_FILE.read_text(encoding="utf-8")
    assert re.search(r"7\s+especialistas", rg_text), remediation(
        "routing-graph.yaml não referencia a topologia de 7 especialistas no domínio reativo.",
        fix_hint="Atualize a menção no nó ou aresta do spring-reactive-router para '7 especialistas'."
    )
