"""
test_anti_manual_user_delegation_governance.py — Validação determinística da proibição de terceirização manual ao usuário (R-057 / Smell 2.25).

Quality Gate que garante:
1. CLAUDE.md declara a regra normativa R-057.
2. copilot-instructions.md declara a diretriz R-057.
3. governance-audit-patterns/SKILL.md cataloga o Smell 2.25 (Anti-Manual User Delegation & Dead-End Analysis).
4. Templates canônicos (research-agent.md, agent-template.md, router-agent.md) proíbem instrução de edição manual ao usuário.
5. Agentes analíticos e read-only declaram a proibição de terceirização manual ao usuário no bloco CRÍTICO de Não-Escopo.
6. governance-factory.agent.md impõe a verificação de R-057 para agentes analíticos/read-only.
7. workflows.md formaliza o Invariante 16 proibindo a terceirização de execução ao usuário em etapas analíticas/diagnósticas.
"""
from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
COPILOT_INSTRUCTIONS_PATH = REPO_ROOT / ".github" / "copilot-instructions.md"
GOVERNANCE_SKILL_PATH = REPO_ROOT / ".github" / "skills" / "governance-audit-patterns" / "SKILL.md"
TEMPLATES_DIR = REPO_ROOT / ".github" / "agents" / "templates"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
WORKFLOWS_PATH = AGENTS_DIR / "workflows.md"
GOVERNANCE_FACTORY_PATH = AGENTS_DIR / "governance-factory.agent.md"


def test_r057_declared_in_claude_md():
    """Valida se R-057 está formalizada em CLAUDE.md."""
    assert CLAUDE_PATH.exists(), "CLAUDE.md não encontrado"
    content = CLAUDE_PATH.read_text(encoding="utf-8")
    assert "R-057" in content, "CLAUDE.md DEVE declarar a regra normativa R-057"
    assert "Anti-Manual User Delegation" in content or "edição manual ao usuário" in content, (
        "CLAUDE.md DEVE explicitar a proibição de terceirizar edição manual ao usuário"
    )


def test_r057_declared_in_copilot_instructions():
    """Valida se R-057 está formalizada em copilot-instructions.md."""
    assert COPILOT_INSTRUCTIONS_PATH.exists(), "copilot-instructions.md não encontrado"
    content = COPILOT_INSTRUCTIONS_PATH.read_text(encoding="utf-8")
    assert "R-057" in content, "copilot-instructions.md DEVE declarar a regra R-057"
    assert "Anti-Manual User Delegation" in content or "edição manual" in content, (
        "copilot-instructions.md DEVE referenciar a proibição de terceirizar edição manual ao usuário"
    )


def test_smell_2_25_cataloged_in_governance_audit_patterns():
    """Valida se o Smell 2.25 está catalogado na skill de auditoria de governança."""
    assert GOVERNANCE_SKILL_PATH.exists(), "governance-audit-patterns/SKILL.md não encontrado"
    content = GOVERNANCE_SKILL_PATH.read_text(encoding="utf-8")
    assert "2.25" in content, "governance-audit-patterns/SKILL.md DEVE catalogar o Smell 2.25"
    assert "Terceirização Indevida de Edição ao Usuário" in content or "Anti-Manual User Delegation" in content, (
        "Smell 2.25 DEVE identificar o anti-padrão de terceirização indevida de edição ao usuário"
    )


def test_templates_declare_anti_manual_user_delegation():
    """Valida se os templates canônicos proíbem instrução de edição manual ao usuário."""
    research_template = (TEMPLATES_DIR / "research-agent.md").read_text(encoding="utf-8")
    assert "R-057" in research_template or "Smell 2.25" in research_template, (
        "research-agent.md DEVE declarar a proibição de terceirização manual ao usuário (R-057 / Smell 2.25)"
    )

    agent_template = (TEMPLATES_DIR / "agent-template.md").read_text(encoding="utf-8")
    assert "R-057" in agent_template or "Smell 2.25" in agent_template, (
        "agent-template.md DEVE declarar a proibição de terceirização manual ao usuário (R-057 / Smell 2.25)"
    )

    router_template = (TEMPLATES_DIR / "router-agent.md").read_text(encoding="utf-8")
    assert "R-057" in router_template or "Smell 2.25" in router_template, (
        "router-agent.md DEVE declarar a proibição de terceirização manual ao usuário (R-057 / Smell 2.25)"
    )


def test_canonical_analytical_agents_declare_anti_manual_user_delegation():
    """Valida se agentes analíticos canônicos proíbem instrução de edição manual ao usuário."""
    key_analytical_agents = [
        "agent-auditor.agent.md",
        "code-review.agent.md",
        "adr-sentinel.agent.md",
        "repo-hygiene-auditor.agent.md",
        "requirements-analyst.agent.md",
        "test-strategy.agent.md",
        "bug-triage.agent.md",
        "refactor-planner.agent.md",
        "runtime-verifier.agent.md",
        "deep-search.agent.md",
        "tech-solution-architect.agent.md",
        "ddd-bounded-context-mapper.agent.md"
    ]
    for agent_file in key_analytical_agents:
        p = AGENTS_DIR / agent_file
        assert p.exists(), f"Agente analítico {agent_file} não encontrado"
        content = p.read_text(encoding="utf-8")
        assert "R-057" in content or "Smell 2.25" in content or "edições manuais" in content or "edição manual" in content, (
            f"Agente analítico {agent_file} DEVE conter cláusula de proibição de transferência de edição ao usuário (R-057 / Smell 2.25)"
        )


def test_governance_factory_enforces_anti_manual_user_delegation():
    """Valida se o governance-factory impõe a cláusula R-057 para agentes analíticos/read-only."""
    content = GOVERNANCE_FACTORY_PATH.read_text(encoding="utf-8")
    assert "R-057" in content or "Smell 2.25" in content, (
        "governance-factory.agent.md DEVE validar a inclusão de R-057 / Smell 2.25 para agentes analíticos"
    )


def test_workflows_declare_anti_manual_user_delegation_invariant():
    """Valida se workflows.md declara o Invariante de proibição de terceirização de execução ao usuário."""
    content = WORKFLOWS_PATH.read_text(encoding="utf-8")
    assert "Invariante de Proibição Estrita de Terceirização ao Usuário" in content or "R-057" in content, (
        "workflows.md DEVE formalizar o invariante anti-terceirização de execução ao usuário em etapas analíticas/diagnósticas"
    )
