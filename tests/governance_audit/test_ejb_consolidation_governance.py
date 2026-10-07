"""
test_ejb_consolidation_governance.py — Validação determinística da consolidação
da stack Java Legado EJB (Padrão Triádico 3+1 — Fase 3 do Plano de Governança).

Quality Gate que garante:
1. Topologia estrita: o diretório .github/agents/backend/ejb/ contém exatamente
   os 4 agentes (1 supervisor + 3 especialistas) e 1 sub-catálogo.
2. Eliminação completa dos 6 especialistas legados (zero dangling legacy agents).
3. Sub-catálogo ejb-catalog.yaml consolidado com 3 especialistas.
4. Decision Tree de 3 branches em ejb-router.agent.md preservando baseline R-054.
5. Contratos de fronteira em ejb-developer (proibição de testes unitários, blast-radius check,
   baseline antes/depois, canary gate).
6. Contratos de qualidade em ejb-test-engineer (retry cap R-053, classificação binária,
   TomEE/OpenEJB/Arquillian embutido, mutation score awareness).
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
EJB_DIR = REPO_ROOT / ".github" / "agents" / "backend" / "ejb"
CATALOG_FILE = EJB_DIR / "ejb-catalog.yaml"
ROUTER_FILE = EJB_DIR / "ejb-router.agent.md"
DEV_FILE = EJB_DIR / "ejb-developer.agent.md"
TEST_FILE = EJB_DIR / "ejb-test-engineer.agent.md"
ARCH_FILE = EJB_DIR / "ejb-arch-advisor.agent.md"

EXPECTED_FILES = {
    "ejb-router.agent.md",
    "ejb-arch-advisor.agent.md",
    "ejb-developer.agent.md",
    "ejb-test-engineer.agent.md",
    "ejb-catalog.yaml"
}

LEGACY_AGENTS = [
    "ejb-feature-developer.agent.md",
    "ejb-bug-fixer.agent.md",
    "ejb-perf-tuner.agent.md",
    "ejb-unit-test-writer.agent.md",
    "ejb-integration-test-writer.agent.md",
    "ejb-test-fixer.agent.md"
]

R054_CANONICAL_ROUTER_TOOLS = {
    "read_file",
    "file_search",
    "grep_search",
    "list_dir",
    "ask_questions",
    "run_subagent",
    "context-mode/ctx_search",
}


def test_ejb_directory_file_count_and_composition():
    """Valida que existem exatamente os 5 arquivos canônicos da stack consolidada."""
    assert EJB_DIR.exists(), f"Diretório EJB não encontrado: {EJB_DIR}"
    current_files = {p.name for p in EJB_DIR.iterdir() if p.is_file()}
    assert current_files == EXPECTED_FILES, remediation(
        f"Composição inesperada no diretório EJB: {current_files ^ EXPECTED_FILES}",
        fix_hint="Certifique-se de manter apenas router, arch-advisor, developer, test-engineer e catalog.yaml."
    )


@pytest.mark.parametrize("legacy_file", LEGACY_AGENTS)
def test_ejb_legacy_agents_are_removed(legacy_file: str):
    """Valida que nenhum especialista legado remanesce no diretório."""
    assert not (EJB_DIR / legacy_file).exists(), (
        f"Agente legado {legacy_file} ainda existe em {EJB_DIR} — deve ser removido na consolidação."
    )


def test_ejb_catalog_triadic_structure():
    """Valida que ejb-catalog.yaml declara os 3 especialistas da tríade e o router."""
    assert CATALOG_FILE.exists()
    data = yaml.safe_load(CATALOG_FILE.read_text(encoding="utf-8")) or {}
    assert data.get("router", {}).get("id") == "ejb-router"
    agents = data.get("agents", {})
    assert len(agents) == 3, f"ejb-catalog.yaml deve conter exatamente 3 especialistas, encontrados {len(agents)}"
    assert "ejb-arch-advisor" in agents
    assert "ejb-developer" in agents
    assert "ejb-test-engineer" in agents


def test_ejb_router_preserves_r054_tools():
    """Valida que ejb-router preserva exatamente as 7 tools canônicas sob R-054."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    frontmatter = content.split("---")[1]
    parsed = yaml.safe_load(frontmatter)

    tools = set(parsed.get("tools", []))
    assert tools == R054_CANONICAL_ROUTER_TOOLS, (
        f"ejb-router DEVE conter as 7 tools canônicas R-054. Encontrado: {tools}"
    )


def test_ejb_router_three_branches_decision_tree():
    """Valida que ejb-router.agent.md despacha para exatamente os 3 especialistas."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    assert "@ejb-arch-advisor" in content
    assert "@ejb-developer" in content
    assert "@ejb-test-engineer" in content
    assert "3 especialistas" in content.lower() or "3 Especialistas" in content


def test_ejb_developer_boundary_and_performance_gate():
    """Valida cláusulas obrigatórias de fronteira e safety gate no ejb-developer."""
    assert DEV_FILE.exists()
    content = DEV_FILE.read_text(encoding="utf-8")
    assert any(term in content for term in ["NÃO escrever", "NÃO criar", "NÃO autorar"]), (
        "ejb-developer deve proibir criação de classes de teste unitário"
    )
    assert "blast-radius" in content.lower(), "ejb-developer deve exigir blast-radius check"
    assert "baseline" in content.lower(), "ejb-developer deve exigir medição de baseline antes/depois"
    assert "canary" in content.lower() or "staging" in content.lower(), (
        "ejb-developer deve declarar gate de canary/staging"
    )
    assert "@ejb-test-engineer" in content, (
        "ejb-developer deve formalizar handoff para @ejb-test-engineer"
    )


def test_ejb_test_engineer_quality_gates():
    """Valida retry cap, frameworks embutidos e mutation awareness no ejb-test-engineer."""
    assert TEST_FILE.exists()
    content = TEST_FILE.read_text(encoding="utf-8")
    assert "2 tentativas" in content or "teto" in content.lower(), (
        "ejb-test-engineer deve formalizar retry cap de no máximo 2 tentativas"
    )
    assert "@ejb-developer" in content, (
        "ejb-test-engineer deve formalizar handoff para @ejb-developer quando bug real"
    )
    assert any(fw in content.lower() for fw in ["openejb", "tomee", "arquillian"]), (
        "ejb-test-engineer deve cobrir OpenEJB, TomEE ou Arquillian"
    )
    assert "mutation" in content.lower(), (
        "ejb-test-engineer deve formalizar awareness de testes de mutação"
    )
