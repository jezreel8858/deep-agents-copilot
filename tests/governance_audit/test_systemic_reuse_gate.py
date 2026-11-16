"""
test_systemic_reuse_gate.py — Validação determinística do Portão de Reúso e Generalização Sistêmica (R-055 / Anti-Silo Fix).

Garante que:
1. CLAUDE.md e copilot-instructions.md formalizam a regra normativa R-055.
2. workflows.md (WORKFLOW-GOVERNANCE-MAINTENANCE) institui a análise obrigatória Q1/Q2/Q3.
3. governance-factory-patterns/SKILL.md documenta o gate em sua Decision Tree, Checklist e Formato de Saída.
4. Os 3 agentes de governança (agent-auditor, governance-factory, governance-maintainer) incorporam
   compulsoriamente a autorreflexão de reúso sistêmico em seus contratos operacionais.
5. O @governance-maintainer possui Veto Fail-Closed explícito para *.py, conftest.py e pyproject.toml
   e delega R-055 Q3 para a Tríade Python (@python-router -> @python-arch-advisor -> @python-test-engineer).
6. @python-router e @python-arch-advisor (resolvidos via rglob em .github/agents/) formalizam o fluxo
   de 2 passos e a cobertura explícita de tools/**/*.py, scripts/**/*.py e tests/**/*.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

from tests.governance_audit._helpers import read_workflows_full_content

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"


def _resolve_agent_file(agent_filename: str) -> Path:
    """Localiza recursivamente um arquivo de agente em .github/agents/ (suporte a subpastas via rglob)."""
    direct_path = AGENTS_DIR / agent_filename
    if direct_path.exists():
        return direct_path
    matches = sorted(AGENTS_DIR.rglob(agent_filename))
    assert matches, f"Agente {agent_filename} não encontrado em {AGENTS_DIR} (via rglob)"
    assert len(matches) == 1, f"Múltiplos arquivos encontrados para {agent_filename}: {matches}"
    return matches[0]


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
    """Valida se workflows.md (fatiado em .github/agents/workflows/, R-066/F3) formaliza
    o Systemic Reuse Gate no WORKFLOW-GOVERNANCE-MAINTENANCE."""
    content = read_workflows_full_content(REPO_ROOT)

    assert "Portão de Reúso e Generalização Sistêmica" in content, (
        "workflows.md (ou arquivos fatiado em workflows/) DEVE declarar a seção do Portão de Reúso e Generalização Sistêmica"
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
        agent_file = _resolve_agent_file(agent_name)
        assert agent_file.exists(), f"Agente {agent_name} deve existir"
        content = agent_file.read_text(encoding="utf-8")

        assert "R-055" in content, f"[{agent_name}] DEVE referenciar a regra R-055"
        assert "Reúso Sistêmico" in content or "reúso sistêmico" in content or "Portão de Reúso" in content, (
            f"[{agent_name}] DEVE declarar o Portão de Reúso Sistêmico em seu contrato"
        )


def test_governance_maintainer_veto_fail_closed_python():
    """Teste 1: Valida em governance-maintainer.agent.md a proibição explícita (Veto Fail-Closed)
    de criar, editar, formatar ou refatorar *.py, conftest.py e pyproject.toml."""
    agent_file = _resolve_agent_file("governance-maintainer.agent.md")
    content = agent_file.read_text(encoding="utf-8")

    assert "*.py" in content, "governance-maintainer.agent.md DEVE vetar explicitamente *.py"
    assert "conftest.py" in content, "governance-maintainer.agent.md DEVE vetar explicitamente conftest.py"
    assert "pyproject.toml" in content, "governance-maintainer.agent.md DEVE vetar explicitamente pyproject.toml"
    assert "NÃO criar, editar, formatar ou refatorar arquivos Python" in content, (
        "governance-maintainer.agent.md DEVE conter a diretriz explícita de Veto Fail-Closed para arquivos Python"
    )


def test_governance_maintainer_forbids_python_code_mutation_and_delegates_q3_to_python_router():
    """Teste 2: Valida em governance-maintainer.agent.md a delegação obrigatória de R-055 Q3
    na cadeia @python-router -> @python-arch-advisor -> @python-test-engineer."""
    agent_file = _resolve_agent_file("governance-maintainer.agent.md")
    content = agent_file.read_text(encoding="utf-8")

    assert "Q3" in content and "R-055" in content, (
        "governance-maintainer.agent.md DEVE declarar o requisito Q3 sob R-055"
    )
    assert "@python-router" in content, (
        "governance-maintainer.agent.md DEVE delegar demandas Python/Q3 para @python-router"
    )
    assert "@python-arch-advisor" in content, (
        "governance-maintainer.agent.md DEVE referenciar @python-arch-advisor como 1º passo da Tríade Python em Q3"
    )
    assert "@python-test-engineer" in content, (
        "governance-maintainer.agent.md DEVE referenciar @python-test-engineer como executor de testes em Q3"
    )


def test_python_triad_two_step_flow_and_repo_tooling_coverage():
    """Teste 3: Valida o fluxo de 2 passos (1º @python-arch-advisor -> 2º @python-developer / @python-test-engineer)
    e a cobertura explícita de tools/**/*.py, scripts/**/*.py e tests/**/*.py em
    python-router.agent.md e python-arch-advisor.agent.md (localizados via rglob)."""
    router_file = _resolve_agent_file("python-router.agent.md")
    advisor_file = _resolve_agent_file("python-arch-advisor.agent.md")

    assert "backend/python/python-router.agent.md" in router_file.as_posix()
    assert "backend/python/python-arch-advisor.agent.md" in advisor_file.as_posix()

    router_content = router_file.read_text(encoding="utf-8")
    advisor_content = advisor_file.read_text(encoding="utf-8")

    for name, content in [
        ("python-router.agent.md", router_content),
        ("python-arch-advisor.agent.md", advisor_content),
    ]:
        assert "tools/**/*.py" in content, f"[{name}] DEVE declarar cobertura de tools/**/*.py"
        assert "scripts/**/*.py" in content, f"[{name}] DEVE declarar cobertura de scripts/**/*.py"
        assert "tests/**/*.py" in content, f"[{name}] DEVE declarar cobertura de tests/**/*.py"
        assert "docs/plans/implementation/" in content, (
            f"[{name}] DEVE referenciar planos técnicos em docs/plans/implementation/"
        )

    assert "1º Passo" in router_content and "2º Passo" in router_content, (
        "python-router.agent.md DEVE explicitar o fluxo de 1º Passo (@python-arch-advisor) e 2º Passo (@python-developer / @python-test-engineer)"
    )
    assert "@python-arch-advisor" in router_content and "@python-developer" in router_content and "@python-test-engineer" in router_content, (
        "python-router.agent.md DEVE articular toda a Tríade Python"
    )
    assert "1º passo" in advisor_content.lower() and "@python-router" in advisor_content, (
        "python-arch-advisor.agent.md DEVE declarar seu papel como 1º passo da Tríade Python sob @python-router"
    )
