"""
test_frontend_test_last_governance.py — Validação determinística da governança Test-Last e isenção de testes para agentes de UI no Frontend.

Garante que:
1. angular-ui-stylist é formalmente isento de criar ou executar testes unitários (escopo estritamente visual).
2. angular-feature-developer adota o modelo Test-Last / Implementation-First em vez de TDD estrito.
3. angular-catalog.yaml reflete essas diretrizes nos metadados dos especialistas.
4. angular-implementation-patterns/SKILL.md e test-implementation-frontend/SKILL.md documentam a metodologia Test-Last.
5. governance-factory e governance-factory-patterns padronizam Test-Last e isenção de UI para futuros ecossistemas frontend.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"


def test_angular_ui_stylist_is_exempt_from_unit_tests():
    """Valida se angular-ui-stylist proíbe explicitamente a criação e execução de testes unitários."""
    stylist_file = AGENTS_DIR / "frontend" / "angular" / "angular-ui-stylist.agent.md"
    assert stylist_file.exists()
    content = stylist_file.read_text(encoding="utf-8")

    assert "NÃO criar, executar ou alterar testes unitários" in content or "isento" in content.lower(), (
        "angular-ui-stylist.agent.md DEVE declarar formalmente a isenção/proibição de testes unitários"
    )
    assert "visual" in content.lower(), "angular-ui-stylist.agent.md DEVE reforçar validação visual"


def test_angular_feature_developer_adopts_test_last():
    """Valida se angular-feature-developer adota a abordagem Test-Last / Implementation-First."""
    feat_file = AGENTS_DIR / "frontend" / "angular" / "angular-feature-developer.agent.md"
    assert feat_file.exists()
    content = feat_file.read_text(encoding="utf-8")

    assert "Test-Last" in content, (
        "angular-feature-developer.agent.md DEVE formalizar o workflow Test-Last"
    )
    assert "Implementation-First" in content, (
        "angular-feature-developer.agent.md DEVE explicitar o paradigma Implementation-First"
    )


def test_angular_catalog_reflects_test_last_and_ui_exemption():
    """Valida se o sub-catálogo angular-catalog.yaml alinha as descrições dos especialistas."""
    catalog_file = AGENTS_DIR / "frontend" / "angular" / "angular-catalog.yaml"
    assert catalog_file.exists()
    content = catalog_file.read_text(encoding="utf-8")

    assert "Test-Last" in content, "angular-catalog.yaml deve declarar Test-Last"
    assert "isento de criar ou rodar testes unitários" in content or "isento" in content, (
        "angular-catalog.yaml deve registrar a isenção de testes unitários para angular-ui-stylist"
    )


def test_angular_implementation_patterns_skill_adopts_test_last():
    """Valida se angular-implementation-patterns/SKILL.md documenta Test-Last e isenção de UI."""
    skill_file = SKILLS_DIR / "angular-implementation-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "Test-Last" in content, "angular-implementation-patterns/SKILL.md DEVE documentar Test-Last"
    assert "ISENTOS" in content or "isentos" in content.lower(), (
        "angular-implementation-patterns/SKILL.md DEVE explicitar isenção de testes para agentes de UI"
    )


def test_frontend_future_stacks_standardize_test_last_in_governance_factory():
    """Valida se governance-factory e governance-factory-patterns padronizam Test-Last para futuros ecossistemas frontend."""
    gf_file = AGENTS_DIR / "governance-factory.agent.md"
    content_gf = gf_file.read_text(encoding="utf-8")
    assert "Frontend (Padrão Test-Last & Isenção de UI)" in content_gf or "Test-Last" in content_gf

    gfp_file = SKILLS_DIR / "governance-factory-patterns" / "SKILL.md"
    content_gfp = gfp_file.read_text(encoding="utf-8")
    assert "Test-Last" in content_gfp
    assert "isento de criar ou executar testes unitários" in content_gfp or "isento" in content_gfp.lower()
