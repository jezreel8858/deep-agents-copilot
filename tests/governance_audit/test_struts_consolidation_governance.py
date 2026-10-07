"""
test_struts_consolidation_governance.py — Validação determinística da consolidação
da stack Java Legado Struts (Padrão Triádico 3+1 — Fase 3 do Plano de Governança).

Quality Gate que garante:
1. Topologia estrita: o diretório .github/agents/backend/struts/ contém exatamente
   os 4 agentes (1 supervisor + 3 especialistas) e 1 sub-catálogo.
2. Eliminação completa dos 6 especialistas legados (zero dangling legacy agents).
3. Sub-catálogo struts-catalog.yaml consolidado com 3 especialistas.
4. Decision Tree de 3 branches em struts-router.agent.md preservando baseline R-054.
5. Contratos de fronteira em struts-developer (proibição de testes unitários, blast-radius check,
   baseline antes/depois, canary gate).
6. Contratos de qualidade em struts-test-engineer (retry cap R-053, classificação binária,
   StrutsTestCase/mock servlet, mutation score awareness).
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
STRUTS_DIR = REPO_ROOT / ".github" / "agents" / "backend" / "struts"
CATALOG_FILE = STRUTS_DIR / "struts-catalog.yaml"
ROUTER_FILE = STRUTS_DIR / "struts-router.agent.md"
DEV_FILE = STRUTS_DIR / "struts-developer.agent.md"
TEST_FILE = STRUTS_DIR / "struts-test-engineer.agent.md"
ARCH_FILE = STRUTS_DIR / "struts-arch-advisor.agent.md"

EXPECTED_FILES = {
    "struts-router.agent.md",
    "struts-arch-advisor.agent.md",
    "struts-developer.agent.md",
    "struts-test-engineer.agent.md",
    "struts-catalog.yaml"
}

LEGACY_AGENTS = [
    "struts-feature-developer.agent.md",
    "struts-bug-fixer.agent.md",
    "struts-perf-tuner.agent.md",
    "struts-unit-test-writer.agent.md",
    "struts-integration-test-writer.agent.md",
    "struts-test-fixer.agent.md"
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


def test_struts_directory_file_count_and_composition():
    """Valida que existem exatamente os 5 arquivos canônicos da stack consolidada."""
    assert STRUTS_DIR.exists(), f"Diretório Struts não encontrado: {STRUTS_DIR}"
    current_files = {p.name for p in STRUTS_DIR.iterdir() if p.is_file()}
    assert current_files == EXPECTED_FILES, remediation(
        f"Composição inesperada no diretório Struts: {current_files ^ EXPECTED_FILES}",
        fix_hint="Certifique-se de manter apenas router, arch-advisor, developer, test-engineer e catalog.yaml."
    )


@pytest.mark.parametrize("legacy_file", LEGACY_AGENTS)
def test_struts_legacy_agents_are_removed(legacy_file: str):
    """Valida que nenhum especialista legado remanesce no diretório."""
    assert not (STRUTS_DIR / legacy_file).exists(), (
        f"Agente legado {legacy_file} ainda existe em {STRUTS_DIR} — deve ser removido na consolidação."
    )


def test_struts_catalog_triadic_structure():
    """Valida que struts-catalog.yaml declara os 3 especialistas da tríade e o router."""
    assert CATALOG_FILE.exists()
    data = yaml.safe_load(CATALOG_FILE.read_text(encoding="utf-8")) or {}
    assert data.get("router", {}).get("id") == "struts-router"
    agents = data.get("agents", {})
    assert len(agents) == 3, f"struts-catalog.yaml deve conter exatamente 3 especialistas, encontrados {len(agents)}"
    assert "struts-arch-advisor" in agents
    assert "struts-developer" in agents
    assert "struts-test-engineer" in agents


def test_struts_router_preserves_r054_tools():
    """Valida que struts-router preserva exatamente as 7 tools canônicas sob R-054."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    frontmatter = content.split("---")[1]
    parsed = yaml.safe_load(frontmatter)

    tools = set(parsed.get("tools", []))
    assert tools == R054_CANONICAL_ROUTER_TOOLS, (
        f"struts-router DEVE conter as 7 tools canônicas R-054. Encontrado: {tools}"
    )


def test_struts_router_three_branches_decision_tree():
    """Valida que struts-router.agent.md despacha para exatamente os 3 especialistas."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    assert "@struts-arch-advisor" in content
    assert "@struts-developer" in content
    assert "@struts-test-engineer" in content
    assert "3 especialistas" in content.lower() or "3 Especialistas" in content


def test_struts_developer_boundary_and_performance_gate():
    """Valida cláusulas obrigatórias de fronteira e safety gate no struts-developer."""
    assert DEV_FILE.exists()
    content = DEV_FILE.read_text(encoding="utf-8")
    assert any(term in content for term in ["NÃO escrever", "NÃO criar", "NÃO autorar"]), (
        "struts-developer deve proibir criação de classes de teste unitário"
    )
    assert "blast-radius" in content.lower(), "struts-developer deve exigir blast-radius check"
    assert "baseline" in content.lower(), "struts-developer deve exigir medição de baseline antes/depois"
    assert "canary" in content.lower() or "staging" in content.lower(), (
        "struts-developer deve declarar gate de canary/staging"
    )
    assert "@struts-test-engineer" in content, (
        "struts-developer deve formalizar handoff para @struts-test-engineer"
    )


def test_struts_test_engineer_quality_gates():
    """Valida retry cap, frameworks de teste e mutation awareness no struts-test-engineer."""
    assert TEST_FILE.exists()
    content = TEST_FILE.read_text(encoding="utf-8")
    assert "2 tentativas" in content or "teto" in content.lower(), (
        "struts-test-engineer deve formalizar retry cap de no máximo 2 tentativas"
    )
    assert "@struts-developer" in content, (
        "struts-test-engineer deve formalizar handoff para @struts-developer quando bug real"
    )
    assert "strutstestcase" in content.lower(), (
        "struts-test-engineer deve cobrir StrutsTestCase"
    )
    assert "mutation" in content.lower(), (
        "struts-test-engineer deve formalizar awareness de testes de mutação"
    )
