"""
test_context_mode_precedence_governance.py — Validação determinística da precedência mandatória do context-mode (R-056 / Smell 2.24).

Garante que:
1. CLAUDE.md e copilot-instructions.md formalizam a regra normativa R-056.
2. governance-audit-patterns/SKILL.md cataloga o Smell 2.24 (Editor Tool Sprawl).
3. efficient-batch-code-modification/SKILL.md define a precedência Nível 1 (Context-Mode) e Nível 2 (Editor Fallback).
4. Templates operacionais (operational-agent.md e agent-template.md) incluem a cláusula de precedência R-056.
5. governance-factory.agent.md valida a precedência R-056 para novos agentes mutadores.
"""
from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"


def test_r056_declared_in_claude_md():
    """Valida se CLAUDE.md declara a regra normativa R-056 e a precedência de context-mode."""
    claude_file = REPO_ROOT / "CLAUDE.md"
    assert claude_file.exists()
    content = claude_file.read_text(encoding="utf-8")

    assert "R-056" in content, "CLAUDE.md DEVE declarar a regra normativa R-056"
    assert "Precedência Mandatória de Context Mode" in content or "Precedência" in content, (
        "CLAUDE.md DEVE explicitar a precedência mandatória de context-mode"
    )
    assert "ctx_execute" in content, "CLAUDE.md DEVE citar ctx_execute como primário"


def test_r056_declared_in_copilot_instructions():
    """Valida se copilot-instructions.md declara a diretriz de autonomia R-056."""
    ci_file = REPO_ROOT / ".github" / "copilot-instructions.md"
    assert ci_file.exists()
    content = ci_file.read_text(encoding="utf-8")

    assert "R-056" in content, "copilot-instructions.md DEVE referenciar a regra R-056"
    assert "Context Mode" in content or "context-mode" in content, (
        "copilot-instructions.md DEVE mencionar a priorização de context-mode"
    )


def test_smell_2_24_documented_in_governance_audit_patterns():
    """Valida se o Smell 2.24 está catalogado na skill de auditoria."""
    skill_file = SKILLS_DIR / "governance-audit-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "2.24" in content, "governance-audit-patterns/SKILL.md DEVE catalogar o Smell 2.24"
    assert "Editor Tool Sprawl" in content or "Precedência de Context-Mode" in content, (
        "Smell 2.24 DEVE identificar o anti-padrão de Editor Tool Sprawl"
    )


def test_efficient_batch_code_modification_skill_declares_context_mode_precedence():
    """Valida se efficient-batch-code-modification/SKILL.md define a precedência de ferramentas (R-056)."""
    skill_file = SKILLS_DIR / "efficient-batch-code-modification" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "R-056" in content, "efficient-batch-code-modification/SKILL.md DEVE referenciar R-056"
    assert "Nível 1 (Primário / Compulsório)" in content or "Primário" in content, (
        "A skill DEVE definir o Nível 1 primário para context-mode"
    )
    assert "Nível 2 (Fallback Restrito de Última Instância)" in content or "Fallback" in content, (
        "A skill DEVE rebaixar ferramentas manuais de editor para fallback"
    )


def test_operational_and_general_templates_declare_context_mode_precedence():
    """Valida se os templates operacionais incluem a cláusula de precedência R-056."""
    templates = [
        AGENTS_DIR / "templates" / "operational-agent.md",
        AGENTS_DIR / "templates" / "agent-template.md",
    ]

    for tpl in templates:
        assert tpl.exists(), f"Template {tpl.name} deve existir"
        content = tpl.read_text(encoding="utf-8")

        assert "R-056" in content or "context-mode" in content.lower(), (
            f"[{tpl.name}] DEVE declarar a regra R-056 de priorização de context-mode"
        )


def test_governance_factory_enforces_context_mode_precedence_for_mutating_agents():
    """Valida se governance-factory.agent.md valida a regra R-056 para novos agentes mutadores."""
    gf_file = AGENTS_DIR / "governance-factory.agent.md"
    assert gf_file.exists()
    content = gf_file.read_text(encoding="utf-8")

    assert "R-056" in content, "governance-factory.agent.md DEVE referenciar R-056 em seu checklist"
    assert "Smell 2.24" in content or "context-mode" in content, (
        "governance-factory.agent.md DEVE mencionar a prevenção do Smell 2.24"
    )
