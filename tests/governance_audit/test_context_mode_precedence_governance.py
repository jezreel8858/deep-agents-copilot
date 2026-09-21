"""
test_context_mode_precedence_governance.py — Validação determinística da precedência mandatória do context-mode (R-056 / Smell 2.24).

Garante que:
1. CLAUDE.md e copilot-instructions.md formalizam as regras normativas R-008 e R-056 com 100% de obrigatoriedade
   para leitura, modificação e criação de arquivos quando context-mode disponível.
2. Ferramentas nativas de editor (read_file, replace_string_in_file, insert_edit_into_file, create_file) e terminal
   são estritamente proibidas quando context-mode disponível, rebaixadas a fallback exclusivo de indisponibilidade.
3. governance-audit-patterns/SKILL.md cataloga o Smell 2.24 (Editor Tool Sprawl / R-056).
4. efficient-batch-code-modification/SKILL.md define a precedência Nível 1 (Context-Mode 100% Compulsório)
   e Nível 2 (Fallback Exclusivo quando Context-Mode Indisponível).
5. Templates operacionais (operational-agent.md e agent-template.md) incluem a cláusula de uso 100% obrigatório
   e proibição de editor tools / fallback exclusivo.
6. governance-factory.agent.md valida a regra R-056 e Smell 2.24 em seu checklist para novos agentes.
7. governance-maintainer.agent.md e agentes pares aplicam a precedência mandatória de context-mode.
"""
from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"


def test_r008_and_r056_declared_in_claude_md():
    """Valida se CLAUDE.md declara R-008 e R-056 com uso 100% obrigatório e proibição de editor tools."""
    claude_file = REPO_ROOT / "CLAUDE.md"
    assert claude_file.exists()
    content = claude_file.read_text(encoding="utf-8")

    assert "R-008" in content, "CLAUDE.md DEVE declarar a regra normativa R-008"
    assert "R-056" in content, "CLAUDE.md DEVE declarar a regra normativa R-056"
    assert "100% OBRIGATÓRIO" in content, (
        "CLAUDE.md DEVE explicitar a obrigatoriedade de 100% do context-mode"
    )
    assert "estritamente proibidas quando o context-mode estiver disponível" in content, (
        "CLAUDE.md DEVE declarar ferramentas nativas de editor como estritamente proibidas"
    )
    assert "fallback exclusivo" in content, (
        "CLAUDE.md DEVE rebaixar ferramentas de editor a fallback exclusivo"
    )
    assert "ctx_execute" in content, "CLAUDE.md DEVE citar ctx_execute como primário"


def test_r056_and_r008_declared_in_copilot_instructions():
    """Valida se copilot-instructions.md declara o uso 100% obrigatório e fallback exclusivo."""
    ci_file = REPO_ROOT / ".github" / "copilot-instructions.md"
    assert ci_file.exists()
    content = ci_file.read_text(encoding="utf-8")

    assert "R-008" in content, "copilot-instructions.md DEVE referenciar a regra R-008"
    assert "R-056" in content, "copilot-instructions.md DEVE referenciar a regra R-056"
    assert "100% OBRIGATÓRIO" in content, (
        "copilot-instructions.md DEVE declarar context-mode 100% obrigatório"
    )
    assert "fallback exclusivo" in content, (
        "copilot-instructions.md DEVE definir ferramentas de editor como fallback exclusivo"
    )
    assert "estritamente proibidas" in content or "estritamente proibidos" in content, (
        "copilot-instructions.md DEVE proibir ferramentas manuais de editor quando context-mode disponível"
    )


def test_smell_2_24_documented_in_governance_audit_patterns():
    """Valida se o Smell 2.24 está catalogado na skill de auditoria com a regra endurecida."""
    skill_file = SKILLS_DIR / "governance-audit-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "2.24" in content, "governance-audit-patterns/SKILL.md DEVE catalogar o Smell 2.24"
    assert "Editor Tool Sprawl" in content, (
        "Smell 2.24 DEVE identificar o anti-padrão de Editor Tool Sprawl"
    )
    assert "100% obrigatório" in content, (
        "Smell 2.24 DEVE citar o uso 100% obrigatório de context-mode"
    )
    assert "fallback exclusivo" in content, (
        "Smell 2.24 DEVE citar o rebaixamento de editor tools a fallback exclusivo"
    )


def test_efficient_batch_code_modification_skill_declares_context_mode_precedence():
    """Valida se efficient-batch-code-modification/SKILL.md define a precedência e fallback exclusivo."""
    skill_file = SKILLS_DIR / "efficient-batch-code-modification" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "R-056" in content, "efficient-batch-code-modification/SKILL.md DEVE referenciar R-056"
    assert "R-008" in content, "efficient-batch-code-modification/SKILL.md DEVE referenciar R-008"
    assert "100% OBRIGATÓRIO" in content or "100% Compulsório" in content, (
        "A skill DEVE definir o Nível 1 como 100% obrigatório/compulsório para context-mode"
    )
    assert "Fallback Exclusivo" in content or "fallback exclusivo" in content, (
        "A skill DEVE definir Nível 2 como fallback exclusivo quando context-mode indisponível"
    )
    assert "estritamente proibidas quando o context-mode estiver disponível" in content, (
        "A skill DEVE proibir expressamente ferramentas de editor quando context-mode disponível"
    )


def test_operational_and_general_templates_declare_context_mode_precedence():
    """Valida se os templates operacionais incluem a cláusula de precedência R-056 e fallback exclusivo."""
    templates = [
        AGENTS_DIR / "templates" / "operational-agent.md",
        AGENTS_DIR / "templates" / "agent-template.md",
    ]

    for tpl in templates:
        assert tpl.exists(), f"Template {tpl.name} deve existir"
        content = tpl.read_text(encoding="utf-8")

        assert "100% OBRIGATÓRIO" in content, (
            f"[{tpl.name}] DEVE declarar o uso 100% OBRIGATÓRIO de context-mode"
        )
        assert "fallback exclusivo" in content, (
            f"[{tpl.name}] DEVE declarar o rebaixamento a fallback exclusivo de ferramentas de editor"
        )


def test_governance_factory_enforces_context_mode_precedence_for_mutating_agents():
    """Valida se governance-factory.agent.md valida a regra R-056 e fallback exclusivo em seu checklist."""
    gf_file = AGENTS_DIR / "governance-factory.agent.md"
    assert gf_file.exists()
    content = gf_file.read_text(encoding="utf-8")

    assert "R-056" in content, "governance-factory.agent.md DEVE referenciar R-056 em seu checklist"
    assert "Smell 2.24" in content, "governance-factory.agent.md DEVE mencionar a prevenção do Smell 2.24"
    assert "100% obrigatório" in content, (
        "governance-factory.agent.md DEVE exigir o uso 100% obrigatório de context-mode"
    )
    assert "fallback exclusivo" in content, (
        "governance-factory.agent.md DEVE mencionar o fallback exclusivo de ferramentas de editor"
    )


def test_governance_maintainer_and_peer_agents_align_with_context_mode_precedence():
    """Valida se governance-maintainer e agentes pares declaram 100% obrigatório e fallback exclusivo."""
    gm_file = AGENTS_DIR / "governance-maintainer.agent.md"
    assert gm_file.exists()
    gm_content = gm_file.read_text(encoding="utf-8")

    assert "100% OBRIGATÓRIO" in gm_content, (
        "governance-maintainer.agent.md DEVE declarar context-mode 100% OBRIGATÓRIO"
    )
    assert "fallback exclusivo" in gm_content.lower(), (
        "governance-maintainer.agent.md DEVE citar fallback exclusivo"
    )

    peer_files = [
        AGENTS_DIR / "backend" / "ejb" / "ejb-test-fixer.agent.md",
        AGENTS_DIR / "backend" / "python" / "python-test-fixer.agent.md",
        AGENTS_DIR / "backend" / "spring-boot" / "spring-boot-test-fixer.agent.md",
        AGENTS_DIR / "backend" / "spring-reactive" / "spring-reactive-test-fixer.agent.md",
        AGENTS_DIR / "backend" / "struts" / "struts-test-fixer.agent.md",
        AGENTS_DIR / "database-specialist.agent.md",
        AGENTS_DIR / "frontend" / "angular" / "angular-test-fixer.agent.md",
    ]

    for pf in peer_files:
        assert pf.exists(), f"Peer agent {pf.name} deve existir"
        c = pf.read_text(encoding="utf-8")
        assert "100% obrigatório" in c, f"[{pf.name}] DEVE declarar context-mode 100% obrigatório"
        assert "fallback exclusivo" in c, f"[{pf.name}] DEVE citar fallback exclusivo de editor"
