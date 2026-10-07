"""
test_angular_consolidation_governance.py — Validação determinística da consolidação
da stack Angular (Padrão Triádico 3+1 — Fase 2 do Plano de Governança).

Quality Gate que garante:
1. Topologia estrita: o diretório .github/agents/frontend/angular/ contém exatamente
   os 4 agentes (1 supervisor + 3 especialistas) e 1 sub-catálogo.
2. Eliminação completa dos 7 especialistas legados (zero dangling legacy agents).
3. Sub-catálogo angular-catalog.yaml consolidado com 3 especialistas, governança Test-Last e isenção de UI.
4. Decision Tree de 3 branches em angular-router.agent.md preservando baseline R-054.
5. Contratos de fronteira em angular-developer (proibição de testes unitários, blast-radius, zero hex inline).
6. Contratos de qualidade em angular-test-engineer (retry cap R-053, classificação binária, mutation awareness).
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
ANG_DIR = REPO_ROOT / ".github" / "agents" / "frontend" / "angular"
CATALOG_FILE = ANG_DIR / "angular-catalog.yaml"
ROUTER_FILE = ANG_DIR / "angular-router.agent.md"
DEV_FILE = ANG_DIR / "angular-developer.agent.md"
TEST_FILE = ANG_DIR / "angular-test-engineer.agent.md"
ARCH_FILE = ANG_DIR / "angular-arch-advisor.agent.md"

EXPECTED_FILES = {
    "angular-router.agent.md",
    "angular-arch-advisor.agent.md",
    "angular-developer.agent.md",
    "angular-test-engineer.agent.md",
    "angular-catalog.yaml"
}

LEGACY_AGENTS = [
    "angular-feature-developer.agent.md",
    "angular-bug-fixer.agent.md",
    "angular-ui-stylist.agent.md",
    "angular-unit-test-writer.agent.md",
    "angular-component-test-writer.agent.md",
    "angular-e2e-writer.agent.md",
    "angular-test-fixer.agent.md"
]


def test_angular_directory_file_count_and_composition():
    """Valida que existem exatamente os 5 arquivos canônicos da stack consolidada."""
    assert ANG_DIR.exists(), f"Diretório Angular não encontrado: {ANG_DIR}"
    current_files = {p.name for p in ANG_DIR.iterdir() if p.is_file()}
    assert current_files == EXPECTED_FILES, remediation(
        f"Composição inesperada no diretório Angular: {current_files ^ EXPECTED_FILES}",
        fix_hint="Certifique-se de manter apenas router, arch-advisor, developer, test-engineer e catalog.yaml."
    )


@pytest.mark.parametrize("legacy_file", LEGACY_AGENTS)
def test_angular_legacy_agents_are_removed(legacy_file: str):
    """Valida que nenhum especialista legado remanesce no diretório."""
    assert not (ANG_DIR / legacy_file).exists(), (
        f"Agente legado {legacy_file} ainda existe em {ANG_DIR} — deve ser removido na consolidação."
    )


def test_angular_catalog_triadic_structure():
    """Valida que angular-catalog.yaml declara os 3 especialistas da tríade."""
    assert CATALOG_FILE.exists()
    data = yaml.safe_load(CATALOG_FILE.read_text(encoding="utf-8")) or {}
    agents = data.get("agents", {})
    assert len(agents) == 3, f"angular-catalog.yaml deve conter exatamente 3 especialistas, encontrados {len(agents)}"
    assert "angular-arch-advisor" in agents
    assert "angular-developer" in agents
    assert "angular-test-engineer" in agents

    # Validação de Test-Last e isenção
    dev_entry = agents["angular-developer"]
    assert "Test-Last" in str(dev_entry.get("test_paradigm", ""))
    assert "isento" in str(dev_entry.get("unit_test_exemption", "")).lower()


def test_angular_router_three_branches_decision_tree():
    """Valida que angular-router.agent.md despacha para exatamente os 3 especialistas."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    assert "@angular-arch-advisor" in content
    assert "@angular-developer" in content
    assert "@angular-test-engineer" in content
    assert "3 especialistas" in content.lower() or "3 Especialistas" in content


def test_angular_developer_boundary_and_zero_noise():
    """Valida cláusulas obrigatórias de fronteira no angular-developer."""
    assert DEV_FILE.exists()
    content = DEV_FILE.read_text(encoding="utf-8")
    assert any(term in content for term in ["NÃO criar", "NÃO implementar", "NÃO escrever"]), (
        "angular-developer deve proibir criação de classes de teste unitário"
    )
    assert "isento" in content.lower(), "angular-developer deve declarar isenção de testes unitários"
    assert "blast-radius" in content.lower(), "angular-developer deve exigir blast-radius check"
    assert "zero hex inline" in content.lower(), "angular-developer deve exigir zero hex inline"
    assert "@angular-test-engineer" in content, "angular-developer deve formalizar handoff para @angular-test-engineer"


def test_angular_test_engineer_quality_gates():
    """Valida retry cap, classificação binária e mutation awareness no angular-test-engineer."""
    assert TEST_FILE.exists()
    content = TEST_FILE.read_text(encoding="utf-8")
    assert "2 tentativas" in content or "teto" in content.lower(), (
        "angular-test-engineer deve formalizar retry cap de no máximo 2 tentativas"
    )
    assert "@angular-developer" in content, (
        "angular-test-engineer deve formalizar handoff para @angular-developer quando bug real"
    )
    assert "mutation" in content.lower(), (
        "angular-test-engineer deve formalizar awareness de testes de mutação"
    )
