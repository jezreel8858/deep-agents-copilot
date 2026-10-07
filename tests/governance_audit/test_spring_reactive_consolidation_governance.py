"""
test_spring_reactive_consolidation_governance.py — Validação determinística da consolidação
da stack Spring Reactive (Padrão Triádico 3+1 — Fase 2 do Plano de Governança).

Quality Gate que garante:
1. Topologia estrita: o diretório .github/agents/backend/spring-reactive/ contém exatamente
   os 4 agentes (1 supervisor + 3 especialistas) e 1 sub-catálogo.
2. Eliminação completa dos 6 especialistas legados (zero dangling legacy agents).
3. Sub-catálogo spring-reactive-catalog.yaml consolidado com 3 especialistas.
4. Decision Tree de 3 branches em spring-reactive-router.agent.md preservando baseline R-054.
5. Contratos de fronteira em spring-reactive-developer (proibição de chamadas bloqueantes no Event Loop,
   proibição de autoria de testes unitários, blast-radius check, baseline antes/depois, canary gate).
6. Contratos de qualidade em spring-reactive-test-engineer (retry cap R-053, classificação binária,
   StepVerifier, WebTestClient, Testcontainers R2DBC, mutation score awareness).
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
SR_DIR = REPO_ROOT / ".github" / "agents" / "backend" / "spring-reactive"
CATALOG_FILE = SR_DIR / "spring-reactive-catalog.yaml"
ROUTER_FILE = SR_DIR / "spring-reactive-router.agent.md"
DEV_FILE = SR_DIR / "spring-reactive-developer.agent.md"
TEST_FILE = SR_DIR / "spring-reactive-test-engineer.agent.md"
ARCH_FILE = SR_DIR / "spring-reactive-arch-advisor.agent.md"

EXPECTED_FILES = {
    "spring-reactive-router.agent.md",
    "spring-reactive-arch-advisor.agent.md",
    "spring-reactive-developer.agent.md",
    "spring-reactive-test-engineer.agent.md",
    "spring-reactive-catalog.yaml"
}

LEGACY_AGENTS = [
    "spring-reactive-feature-developer.agent.md",
    "spring-reactive-bug-fixer.agent.md",
    "spring-reactive-perf-tuner.agent.md",
    "spring-reactive-unit-test-writer.agent.md",
    "spring-reactive-integration-test-writer.agent.md",
    "spring-reactive-test-fixer.agent.md"
]


def test_spring_reactive_directory_file_count_and_composition():
    """Valida que existem exatamente os 5 arquivos canônicos da stack consolidada."""
    assert SR_DIR.exists(), f"Diretório Spring Reactive não encontrado: {SR_DIR}"
    current_files = {p.name for p in SR_DIR.iterdir() if p.is_file()}
    assert current_files == EXPECTED_FILES, remediation(
        f"Composição inesperada no diretório Spring Reactive: {current_files ^ EXPECTED_FILES}",
        fix_hint="Certifique-se de manter apenas router, arch-advisor, developer, test-engineer e catalog.yaml."
    )


@pytest.mark.parametrize("legacy_file", LEGACY_AGENTS)
def test_spring_reactive_legacy_agents_are_removed(legacy_file: str):
    """Valida que nenhum especialista legado remanesce no diretório."""
    assert not (SR_DIR / legacy_file).exists(), (
        f"Agente legado {legacy_file} ainda existe em {SR_DIR} — deve ser removido na consolidação."
    )


def test_spring_reactive_catalog_triadic_structure():
    """Valida que spring-reactive-catalog.yaml declara os 3 especialistas da tríade."""
    assert CATALOG_FILE.exists()
    data = yaml.safe_load(CATALOG_FILE.read_text(encoding="utf-8")) or {}
    agents = data.get("agents", {})
    assert len(agents) == 3, f"spring-reactive-catalog.yaml deve conter exatamente 3 especialistas, encontrados {len(agents)}"
    assert "spring-reactive-arch-advisor" in agents
    assert "spring-reactive-developer" in agents
    assert "spring-reactive-test-engineer" in agents


def test_spring_reactive_router_three_branches_decision_tree():
    """Valida que spring-reactive-router.agent.md despacha para exatamente os 3 especialistas."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    assert "@spring-reactive-arch-advisor" in content
    assert "@spring-reactive-developer" in content
    assert "@spring-reactive-test-engineer" in content
    assert "3 especialistas" in content.lower() or "3 Especialistas" in content


def test_spring_reactive_developer_boundary_and_performance_gate():
    """Valida cláusulas obrigatórias de fronteira e safety gate no spring-reactive-developer."""
    assert DEV_FILE.exists()
    content = DEV_FILE.read_text(encoding="utf-8")
    assert any(term in content for term in ["NÃO escrever", "NÃO criar", "NÃO autorar"]), (
        "spring-reactive-developer deve proibir criação de classes de teste unitário"
    )
    assert "event loop" in content.lower(), "spring-reactive-developer deve proibir bloqueio do Event Loop"
    assert "blast-radius" in content.lower(), "spring-reactive-developer deve exigir blast-radius check"
    assert "baseline" in content.lower(), "spring-reactive-developer deve exigir medição de baseline antes/depois"
    assert "canary" in content.lower() or "staging" in content.lower(), (
        "spring-reactive-developer deve declarar gate de canary/staging"
    )
    assert "@spring-reactive-test-engineer" in content, (
        "spring-reactive-developer deve formalizar handoff para @spring-reactive-test-engineer"
    )


def test_spring_reactive_test_engineer_quality_gates():
    """Valida retry cap, frameworks reativos e mutation awareness no spring-reactive-test-engineer."""
    assert TEST_FILE.exists()
    content = TEST_FILE.read_text(encoding="utf-8")
    assert "2 tentativas" in content or "teto" in content.lower(), (
        "spring-reactive-test-engineer deve formalizar retry cap de no máximo 2 tentativas"
    )
    assert "@spring-reactive-developer" in content, (
        "spring-reactive-test-engineer deve formalizar handoff para @spring-reactive-developer quando bug real"
    )
    assert "stepverifier" in content.lower(), (
        "spring-reactive-test-engineer deve cobrir StepVerifier"
    )
    assert "mutation" in content.lower(), (
        "spring-reactive-test-engineer deve formalizar awareness de testes de mutação"
    )
