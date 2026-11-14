"""
test_spring_reactive_perf_tuner_registration.py — Validação determinística da consolidação
do papel de performance tuning na stack Spring Reactive (Padrão Triádico 3+1).

Quality Gate que garante:
1. O papel de performance tuning está formalmente consolidado em spring-reactive-developer.agent.md.
2. spring-reactive-developer.agent.md formaliza o modo 'perf', medição de baseline antes/depois e safety gate.
3. spring-reactive-catalog.yaml registra spring-reactive-developer com keywords de performance (perf tuner, concorrencia reativa).
4. O router spring-reactive-router.agent.md despacha tuning de performance para @spring-reactive-developer na Decision Tree branch [2].
5. O catálogo raiz catalog.yaml e routing-graph.yaml registram a topologia consolidada de 3 especialistas.
"""
from __future__ import annotations

import re
from pathlib import Path
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
SR_DIR = REPO_ROOT / ".github" / "agents" / "backend" / "spring-reactive"
DEV_FILE = SR_DIR / "spring-reactive-developer.agent.md"
SUB_CATALOG_FILE = SR_DIR / "spring-reactive-catalog.yaml"
ROUTER_FILE = SR_DIR / "spring-reactive-router.agent.md"
ROOT_CATALOG_FILE = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
ROUTING_GRAPH_FILE = REPO_ROOT / ".github" / "agents" / "routing-graph.yaml"


def test_spring_reactive_developer_consolidates_performance_role():
    """Valida que spring-reactive-developer consolida as atribuições de tuning e performance."""
    assert DEV_FILE.exists(), remediation(
        f"Arquivo não encontrado: {DEV_FILE}",
        fix_hint="Crie o especialista spring-reactive-developer.agent.md no diretório spring-reactive."
    )
    content = DEV_FILE.read_text(encoding="utf-8")
    assert "Modo Performance" in content or "perf" in content, (
        "spring-reactive-developer deve conter seção de modo Performance/Tuning"
    )
    assert "baseline" in content.lower(), (
        "spring-reactive-developer deve exigir medição de baseline antes e depois"
    )
    assert "canary" in content.lower() or "staging" in content.lower(), (
        "spring-reactive-developer deve declarar gate de segurança canary/staging"
    )


def test_spring_reactive_sub_catalog_consolidation():
    """Valida que o sub-catálogo spring-reactive-catalog.yaml registra os 3 especialistas consolidados."""
    assert SUB_CATALOG_FILE.exists(), remediation(
        f"Sub-catálogo não encontrado: {SUB_CATALOG_FILE}",
        fix_hint="Verifique o arquivo spring-reactive-catalog.yaml."
    )
    data = yaml.safe_load(SUB_CATALOG_FILE.read_text(encoding="utf-8")) or {}
    agents = data.get("agents", {})

    assert "spring-reactive-developer" in agents, "spring-reactive-developer deve constar no sub-catálogo"
    assert "spring-reactive-arch-advisor" in agents, "spring-reactive-arch-advisor deve constar no sub-catálogo"
    assert "spring-reactive-test-engineer" in agents, "spring-reactive-test-engineer deve constar no sub-catálogo"
    assert len(agents) == 3, f"Sub-catálogo deve conter exatamente 3 especialistas, encontrados {len(agents)}"


def test_spring_reactive_router_decision_tree_reference():
    """Valida que o router spring-reactive-router.agent.md despacha performance para spring-reactive-developer."""
    assert ROUTER_FILE.exists(), remediation(
        f"Router não encontrado: {ROUTER_FILE}",
        fix_hint="Verifique a existência do spring-reactive-router.agent.md."
    )
    content = ROUTER_FILE.read_text(encoding="utf-8")
    assert "@spring-reactive-developer" in content, (
        "spring-reactive-router deve referenciar @spring-reactive-developer na Decision Tree"
    )
    assert "@spring-reactive-arch-advisor" in content, (
        "spring-reactive-router deve referenciar @spring-reactive-arch-advisor na Decision Tree"
    )
    assert "@spring-reactive-test-engineer" in content, (
        "spring-reactive-router deve referenciar @spring-reactive-test-engineer na Decision Tree"
    )


def test_spring_reactive_root_catalog_three_specialists_topology():
    """Valida que catalog.yaml registra os 3 especialistas sob related_agents do spring-reactive-router."""
    assert ROOT_CATALOG_FILE.exists()
    cat_data = yaml.safe_load(ROOT_CATALOG_FILE.read_text(encoding="utf-8")) or {}
    router_entry = cat_data.get("agents", {}).get("spring-reactive-router", {})
    related = router_entry.get("related_agents", [])

    assert "spring-reactive-developer" in related
    assert "spring-reactive-arch-advisor" in related
    assert "spring-reactive-test-engineer" in related
    assert "spring-reactive-perf-tuner" not in related


def test_spring_reactive_routing_graph_three_specialists_reference():
    """Valida que routing-graph.yaml descreve a topologia consolidada de 3 especialistas."""
    assert ROUTING_GRAPH_FILE.exists()
    content = ROUTING_GRAPH_FILE.read_text(encoding="utf-8")
    assert "3 especialistas" in content
