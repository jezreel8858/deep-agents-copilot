"""
test_systemic_reuse_gate.py — Validação determinística do Portão de Reúso e Generalização Sistêmica (R-055 / Anti-Silo Fix).

Garante que:
1. CLAUDE.md e copilot-instructions.md formalizam a regra normativa R-055.
2. workflows.md (WORKFLOW-GOVERNANCE-MAINTENANCE) institui a análise obrigatória Q1/Q2/Q3.
3. governance-factory-patterns/SKILL.md documenta o gate em sua Decision Tree, Checklist e Formato de Saída.
4. Os 3 agentes de governança (agent-auditor, governance-factory, governance-maintainer) incorporam
   compulsoriamente a autorreflexão de reúso sistêmico em seus contratos operacionais.
"""
from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"


def test_r055_declared_in_claude_md():
    """Valida se CLAUDE.md declara a regra normativa R-055 e suas 3 perguntas canônicas Q1, Q2, Q3."""
    claude_file = REPO_ROOT / "CLAUDE.md"
    assert claude_file.exists()
    content = claude_file.read_text(encoding="utf-8")

    assert "R-055" in content, "CLAUDE.md DEVE declarar a regra normativa R-055"
    assert "Anti-Silo Fix" in content or "Portão de Reúso" in content, (
        "CLAUDE.md DEVE mencionar o conceito de Anti-Silo Fix / Portão de Reúso"
    )
    assert "Q1" in content and "Q2" in content and "Q3" in content, (
        "CLAUDE.md DEVE explicitar as 3 perguntas canônicas do gate (Q1, Q2, Q3)"
    )


def test_r055_declared_in_copilot_instructions():
    """Valida se copilot-instructions.md declara a diretriz de autonomia R-055."""
    ci_file = REPO_ROOT / ".github" / "copilot-instructions.md"
    assert ci_file.exists()
    content = ci_file.read_text(encoding="utf-8")

    assert "R-055" in content, "copilot-instructions.md DEVE referenciar a regra R-055"
    assert "Portão de Reúso" in content or "Systemic Reuse Gate" in content, (
        "copilot-instructions.md DEVE mencionar o Portão de Reúso Sistêmico"
    )


def test_systemic_reuse_gate_declared_in_workflows():
    """Valida se workflows.md formaliza o Systemic Reuse Gate no WORKFLOW-GOVERNANCE-MAINTENANCE."""
    wf_file = AGENTS_DIR / "workflows.md"
    assert wf_file.exists()
    content = wf_file.read_text(encoding="utf-8")

    assert "Portão de Reúso e Generalização Sistêmica" in content, (
        "workflows.md DEVE declarar a seção do Portão de Reúso e Generalização Sistêmica"
    )
    assert "R-055" in content, "workflows.md DEVE vincular o gate à regra R-055"
    assert "Q1" in content and "Q2" in content and "Q3" in content, (
        "workflows.md DEVE conter as 3 perguntas canônicas (Q1, Q2, Q3) em WORKFLOW-GOVERNANCE-MAINTENANCE"
    )


def test_governance_factory_patterns_skill_declares_systemic_reuse_gate():
    """Valida se governance-factory-patterns/SKILL.md documenta o Systemic Reuse Gate."""
    skill_file = SKILLS_DIR / "governance-factory-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "R-055" in content, "governance-factory-patterns/SKILL.md DEVE referenciar R-055"
    assert "Portão de Reúso e Generalização Sistêmica" in content or "Portão de Reúso Sistêmico" in content, (
        "governance-factory-patterns/SKILL.md DEVE documentar o Portão de Reúso Sistêmico"
    )
    assert "Q1" in content and "Q2" in content and "Q3" in content, (
        "governance-factory-patterns/SKILL.md DEVE detalhar as 3 perguntas do gate"
    )


def test_governance_agents_declare_systemic_reuse_gate():
    """Valida se os 3 agentes de governança (agent-auditor, governance-factory, governance-maintainer)
    incorporam formalmente a regra R-055 e o Portão de Reúso Sistêmico."""
    expected_agents = [
        "agent-auditor.agent.md",
        "governance-factory.agent.md",
        "governance-maintainer.agent.md",
    ]

    for agent_name in expected_agents:
        agent_file = AGENTS_DIR / agent_name
        assert agent_file.exists(), f"Agente {agent_name} deve existir"
        content = agent_file.read_text(encoding="utf-8")

        assert "R-055" in content, f"[{agent_name}] DEVE referenciar a regra R-055"
        assert "Reúso Sistêmico" in content or "reúso sistêmico" in content or "Portão de Reúso" in content, (
            f"[{agent_name}] DEVE declarar o Portão de Reúso Sistêmico em seu contrato"
        )

