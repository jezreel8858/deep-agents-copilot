"""
test_frontend_test_last_governance.py — Validação determinística da governança Test-Last e isenção de testes para agentes de UI no Frontend.

Garante que:
1. angular-developer é formalmente isento de criar ou executar testes unitários (escopo estritamente visual e de lógica de aplicação, modelo Test-Last / Implementation-First).
2. angular-developer adota o modelo Test-Last / Implementation-First em vez de TDD estrito e formaliza delegação para @angular-test-engineer.
3. angular-catalog.yaml reflete essas diretrizes nos metadados dos especialistas.
4. angular-implementation-patterns/SKILL.md e test-implementation-frontend/SKILL.md documentam a metodologia Test-Last.
5. react-developer e react-catalog.yaml mantêm as mesmas garantias de Test-Last e isenção de UI para futuros ecossistemas frontend.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"


def test_angular_developer_is_exempt_from_unit_tests():
    """Valida se angular-developer proíbe explicitamente a criação e execução de testes unitários."""
    dev_file = AGENTS_DIR / "frontend" / "angular" / "angular-developer.agent.md"
    assert dev_file.exists()
    content = dev_file.read_text(encoding="utf-8")
    assert any(term in content for term in ["NÃO criar", "NÃO implementar", "NÃO escrever"]), (
        "angular-developer.agent.md DEVE declarar proibição de autoria de testes unitários"
    )
    assert "isento" in content.lower(), (
        "angular-developer.agent.md DEVE declarar isenção de testes unitários"
    )
    assert "angular-test-engineer" in content, (
        "angular-developer.agent.md DEVE formalizar delegação/handoff para @angular-test-engineer"
    )


def test_angular_developer_adopts_test_last():
    """Valida se angular-developer formaliza o workflow Test-Last / Implementation-First."""
    dev_file = AGENTS_DIR / "frontend" / "angular" / "angular-developer.agent.md"
    assert dev_file.exists()
    content = dev_file.read_text(encoding="utf-8")
    assert "Test-Last" in content, (
        "angular-developer.agent.md DEVE formalizar o workflow Test-Last"
    )
    assert "Implementation-First" in content, (
        "angular-developer.agent.md DEVE explicitar o paradigma Implementation-First"
    )


def test_angular_catalog_reflects_test_last_and_ui_exemption():
    """Valida se o sub-catálogo angular-catalog.yaml alinha as descrições dos especialistas."""
    catalog_file = AGENTS_DIR / "frontend" / "angular" / "angular-catalog.yaml"
    assert catalog_file.exists()
    content = catalog_file.read_text(encoding="utf-8")
    assert "Test-Last" in content, "angular-catalog.yaml deve declarar Test-Last"
    assert "isento" in content.lower(), (
        "angular-catalog.yaml deve registrar a isenção de testes unitários para angular-developer"
    )


def test_angular_implementation_patterns_skill_adopts_test_last():
    """Valida se angular-implementation-patterns/SKILL.md documenta Test-Last e isenção de UI."""
    skill_file = SKILLS_DIR / "angular-implementation-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")
    assert "Test-Last" in content, "SKILL.md deve mencionar Test-Last"
    assert "Implementation-First" in content, "SKILL.md deve mencionar Implementation-First"


def test_test_implementation_frontend_skill_covers_test_last():
    """Valida se test-implementation-frontend/SKILL.md documenta o papel do test-writer sob Test-Last."""
    skill_file = SKILLS_DIR / "test-implementation-frontend" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")
    assert "Test-Last" in content, "SKILL.md de testes deve mencionar Test-Last"


def test_react_developer_is_exempt_from_unit_tests():
    """Valida se react-developer proíbe explicitamente a criação e execução de testes unitários."""
    dev_file = AGENTS_DIR / "frontend" / "react" / "react-developer.agent.md"
    assert dev_file.exists()
    content = dev_file.read_text(encoding="utf-8")
    assert any(term in content for term in ["NÃO criar", "NÃO implementar", "NÃO escrever"]), (
        "react-developer.agent.md DEVE declarar proibição de autoria de testes unitários"
    )
    assert "isento" in content.lower(), (
        "react-developer.agent.md DEVE declarar isenção de testes unitários"
    )
    assert "react-test-engineer" in content, (
        "react-developer.agent.md DEVE formalizar delegação/handoff para @react-test-engineer"
    )


def test_react_catalog_reflects_test_last_and_ui_exemption():
    """Valida se react-catalog.yaml alinha as descrições dos especialistas consolidados."""
    cat_file = AGENTS_DIR / "frontend" / "react" / "react-catalog.yaml"
    assert cat_file.exists()
    content = cat_file.read_text(encoding="utf-8")
    assert "Test-Last" in content, "react-catalog.yaml deve declarar Test-Last"
    assert "isento" in content.lower(), "react-catalog.yaml deve declarar isenção de testes para react-developer"
