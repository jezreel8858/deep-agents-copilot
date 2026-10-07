"""
test_python_consolidation_governance.py — Validação determinística da consolidação
da stack Python Backend (Padrão Triádico 3+1 — Fase 4/5 do Plano de Governança).

Quality Gate que garante:
1. Topologia estrita: o diretório .github/agents/backend/python/ contém exatamente
   os 4 agentes (1 supervisor + 3 especialistas) e 1 sub-catálogo.
2. Eliminação completa dos 6 especialistas legados (zero dangling legacy agents).
3. Sub-catálogo python-catalog.yaml consolidado com 3 especialistas da tríade.
4. Decision Tree de 3 branches em python-router.agent.md preservando baseline R-054.
5. Contratos de fronteira em python-developer (proibição de autoria de testes unitários,
   blast-radius check, baseline antes/depois, canary gate).
6. Contratos de qualidade em python-test-engineer (retry cap R-053 de no máximo 2 tentativas,
   classificação binária, pytest/TestClient/Testcontainers, mutation score awareness).
7. Contratos de governança em python-arch-advisor (Read-Only estrito, escopo de profiling/tuning).
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
PY_DIR = REPO_ROOT / ".github" / "agents" / "backend" / "python"
CATALOG_FILE = PY_DIR / "python-catalog.yaml"
ROUTER_FILE = PY_DIR / "python-router.agent.md"
DEV_FILE = PY_DIR / "python-developer.agent.md"
TEST_FILE = PY_DIR / "python-test-engineer.agent.md"
ARCH_FILE = PY_DIR / "python-arch-advisor.agent.md"

EXPECTED_FILES = {
    "python-router.agent.md",
    "python-arch-advisor.agent.md",
    "python-developer.agent.md",
    "python-test-engineer.agent.md",
    "python-catalog.yaml"
}

LEGACY_AGENTS = [
    "python-feature-developer.agent.md",
    "python-bug-fixer.agent.md",
    "python-perf-tuner.agent.md",
    "python-unit-test-writer.agent.md",
    "python-integration-test-writer.agent.md",
    "python-test-fixer.agent.md"
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


def test_python_directory_file_count_and_composition():
    """Valida que existem exatamente os 5 arquivos canônicos da stack consolidada."""
    assert PY_DIR.exists(), f"Diretório Python não encontrado: {PY_DIR}"
    current_files = {p.name for p in PY_DIR.iterdir() if p.is_file()}
    assert current_files == EXPECTED_FILES, remediation(
        f"Composição inesperada no diretório Python: {current_files ^ EXPECTED_FILES}",
        fix_hint="Certifique-se de manter apenas router, arch-advisor, developer, test-engineer e catalog.yaml."
    )


@pytest.mark.parametrize("legacy_file", LEGACY_AGENTS)
def test_python_legacy_agents_are_removed(legacy_file: str):
    """Valida que nenhum especialista legado remanesce no diretório."""
    assert not (PY_DIR / legacy_file).exists(), (
        f"Agente legado {legacy_file} ainda existe em {PY_DIR} — deve ser removido na consolidação."
    )


def test_python_catalog_triadic_structure():
    """Valida que python-catalog.yaml declara os 3 especialistas da tríade e o router."""
    assert CATALOG_FILE.exists()
    data = yaml.safe_load(CATALOG_FILE.read_text(encoding="utf-8")) or {}
    assert data.get("router", {}).get("id") == "python-router"
    agents = data.get("agents", {})
    assert len(agents) == 3, f"python-catalog.yaml deve conter exatamente 3 especialistas, encontrados {len(agents)}"
    assert "python-arch-advisor" in agents
    assert "python-developer" in agents
    assert "python-test-engineer" in agents


def test_python_router_preserves_r054_tools():
    """Valida que python-router preserva exatamente as 7 tools canônicas sob R-054."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    frontmatter = content.split("---")[1]
    parsed = yaml.safe_load(frontmatter)

    tools = set(parsed.get("tools", []))
    assert tools == R054_CANONICAL_ROUTER_TOOLS, (
        f"python-router DEVE conter as 7 tools canônicas R-054. Encontrado: {tools}"
    )


def test_python_router_three_branches_decision_tree():
    """Valida que python-router.agent.md despacha para exatamente os 3 especialistas."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    assert "@python-arch-advisor" in content
    assert "@python-developer" in content
    assert "@python-test-engineer" in content
    assert "3 especialistas" in content.lower() or "3 Especialistas" in content


def test_python_developer_boundary_and_performance_gate():
    """Valida cláusulas obrigatórias de fronteira e safety gate no python-developer."""
    assert DEV_FILE.exists()
    content = DEV_FILE.read_text(encoding="utf-8")
    assert any(term in content for term in ["NÃO escrever", "NÃO criar", "NÃO autorar"]), (
        "python-developer deve proibir criação de classes/funções de teste unitário"
    )
    assert "blast-radius" in content.lower(), "python-developer deve exigir blast-radius check"
    assert "baseline" in content.lower(), "python-developer deve exigir medição de baseline antes/depois"
    assert "canary" in content.lower() or "staging" in content.lower(), (
        "python-developer deve declarar gate de canary/staging"
    )
    assert "@python-test-engineer" in content, (
        "python-developer deve formalizar handoff para @python-test-engineer"
    )


def test_python_test_engineer_quality_gates():
    """Valida retry cap, frameworks de teste e mutation awareness no python-test-engineer."""
    assert TEST_FILE.exists()
    content = TEST_FILE.read_text(encoding="utf-8")
    assert "2 tentativas" in content or "teto" in content.lower(), (
        "python-test-engineer deve formalizar retry cap de no máximo 2 tentativas"
    )
    assert "@python-developer" in content, (
        "python-test-engineer deve formalizar handoff para @python-developer quando bug real"
    )
    assert any(fw in content.lower() for fw in ["pytest", "testclient", "testcontainers"]), (
        "python-test-engineer deve cobrir pytest, TestClient ou Testcontainers"
    )
    assert "mutation" in content.lower(), (
        "python-test-engineer deve formalizar awareness de testes de mutação"
    )


def test_python_arch_advisor_read_only_and_tuning():
    """Valida que python-arch-advisor é Read-Only e absorveu profiling e tuning."""
    assert ARCH_FILE.exists()
    content = ARCH_FILE.read_text(encoding="utf-8")
    frontmatter = content.split("---")[1]
    parsed = yaml.safe_load(frontmatter)

    tools = set(parsed.get("tools", []))
    assert not any(t in tools for t in ["run_in_terminal", "insert_edit_into_file", "replace_string_in_file", "create_file"]), (
        "python-arch-advisor não deve possuir ferramentas mutativas de terminal ou edição de código."
    )
    assert "read-only" in content.lower()
    assert any(w in content.lower() for w in ["event-loop", "event loop", "n+1", "profiling"]), (
        "python-arch-advisor deve abordar análise de event loop, queries N+1 ou profiling"
    )
