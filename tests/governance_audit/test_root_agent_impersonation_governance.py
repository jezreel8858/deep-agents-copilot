"""
test_root_agent_impersonation_governance.py — Validação determinística da proibição de impersonação de agent
pelo Orquestrador Raiz (R-062 / Smell 2.29 — Root Orchestrator Agent Impersonation).

Quality Gate que garante:
1. CLAUDE.md declara a regra normativa R-062 (Zero Impersonation pelo Orquestrador Raiz).
2. copilot-instructions.md propaga a cláusula equivalente (defense-in-depth) em §1.1 e §2.
3. agent-router.agent.md estende a proibição de Zero Discovery/Zero Impersonation ao Orquestrador Raiz
   antes mesmo da invocação do router.
4. templates/router-agent.md contém a seção "Zero Impersonation pelo Orquestrador Raiz" espelhando R-062.
5. governance-audit-patterns/SKILL.md cataloga o Smell 2.29 (Root Orchestrator Agent Impersonation).
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
COPILOT_INSTRUCTIONS_PATH = REPO_ROOT / ".github" / "copilot-instructions.md"
AGENT_ROUTER_PATH = REPO_ROOT / ".github" / "agents" / "agent-router.agent.md"
ROUTER_TEMPLATE_PATH = REPO_ROOT / ".github" / "agents" / "templates" / "router-agent.md"
GOVERNANCE_SKILL_PATH = REPO_ROOT / ".github" / "skills" / "governance-audit-patterns" / "SKILL.md"


def test_r062_declared_in_claude_md():
    """Valida se R-062 (Zero Impersonation pelo Orquestrador Raiz) está formalizada em CLAUDE.md."""
    assert CLAUDE_PATH.exists(), "CLAUDE.md não encontrado"
    content = CLAUDE_PATH.read_text(encoding="utf-8")
    assert "R-062" in content, "CLAUDE.md DEVE declarar a regra normativa R-062"
    assert "Zero Impersonation" in content, (
        "CLAUDE.md DEVE nomear explicitamente a regra como 'Zero Impersonation pelo Orquestrador Raiz'"
    )
    assert "Orquestrador Raiz" in content
    assert "run_subagent" in content


def test_r062_declared_in_copilot_instructions():
    """Valida se R-062 está propagada em copilot-instructions.md (defense-in-depth)."""
    assert COPILOT_INSTRUCTIONS_PATH.exists(), "copilot-instructions.md não encontrado"
    content = COPILOT_INSTRUCTIONS_PATH.read_text(encoding="utf-8")
    assert "R-062" in content, "copilot-instructions.md DEVE declarar a regra R-062"
    assert "Zero Impersonation" in content or "impersonação" in content.lower(), (
        "copilot-instructions.md DEVE referenciar a proibição de impersonação pelo Orquestrador Raiz"
    )


def test_agent_router_extends_prohibition_to_root_orchestrator():
    """Valida se agent-router.agent.md estende a proibição de Zero Discovery/Impersonation ao Orquestrador Raiz."""
    assert AGENT_ROUTER_PATH.exists(), "agent-router.agent.md não encontrado"
    content = AGENT_ROUTER_PATH.read_text(encoding="utf-8")
    assert "R-062" in content, "agent-router.agent.md DEVE referenciar R-062"
    assert "Orquestrador Raiz" in content, (
        "agent-router.agent.md DEVE deixar explícito que a proibição também é responsabilidade do Orquestrador Raiz"
    )


def test_router_template_declares_zero_impersonation_section():
    """Valida se o template canônico router-agent.md contém a seção Zero Impersonation."""
    assert ROUTER_TEMPLATE_PATH.exists(), "templates/router-agent.md não encontrado"
    content = ROUTER_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "Zero Impersonation pelo Orquestrador Raiz" in content, (
        "router-agent.md DEVE conter a seção 'Zero Impersonation pelo Orquestrador Raiz' (R-062)"
    )
    assert "R-062" in content


def test_smell_2_29_cataloged_in_governance_audit_patterns():
    """Valida se o Smell 2.29 (Root Orchestrator Agent Impersonation) está catalogado."""
    assert GOVERNANCE_SKILL_PATH.exists(), "governance-audit-patterns/SKILL.md não encontrado"
    content = GOVERNANCE_SKILL_PATH.read_text(encoding="utf-8")
    assert "2.29" in content, "governance-audit-patterns/SKILL.md DEVE catalogar o Smell 2.29"
    assert "Root Orchestrator Agent Impersonation" in content
    assert "R-062" in content
