"""Testes determinísticos do Contrato de Qualidade e UX do ask_questions (R-027 / CA-03..CA-06)."""

from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_ca03_ca04_ca05_ssot_in_structured_intake_patterns() -> None:
    content = _read(".github/skills/structured-intake-patterns/SKILL.md")
    assert "CA-03" in content
    assert "CA-04" in content
    assert "CA-05" in content
    assert "[Consequência prática / O que faz] + [Trade-off principal ou quando escolher]" in content
    assert "(Recomendado)" in content
    assert "Anti-Strawman" in content
    assert "allowFreeformInput" in content
    assert "25" in content
    assert "questions_good" in content and "questions_bad" in content


def test_ca06_peer_skills_alignment() -> None:
    socratic = _read(".github/skills/socratic-grilling-patterns/SKILL.md")
    assert "CA-03" in socratic and "CA-04" in socratic and "CA-05" in socratic
    assert "structured-intake-patterns" in socratic
    assert "(Recomendado)" in socratic

    prompt_eng = _read(".github/skills/prompt-engineering-patterns/SKILL.md")
    assert "CA-03..CA-05" in prompt_eng
    assert "structured-intake-patterns" in prompt_eng

    audit_skill = _read(".github/skills/governance-audit-patterns/SKILL.md")
    audit_refs = _read(".github/skills/governance-audit-patterns/references/smells-catalog-detailed.md")
    assert "Degradação de UX no `ask_questions`" in audit_skill
    assert "Degradação de UX no `ask_questions`" in audit_refs
    assert "CA-03" in audit_refs and "CA-04" in audit_refs and "CA-05" in audit_refs


def test_ca06_normative_documents_and_execution_protocol_fragment() -> None:
    claude = _read("CLAUDE.md")
    assert "R-027" in claude
    assert "(Recomendado)" in claude
    assert "Anti-Strawman" in claude
    assert "structured-intake-patterns" in claude

    copilot = _read(".github/copilot-instructions.md")
    assert "R-027" in copilot
    assert "(Recomendado)" in copilot
    assert "structured-intake-patterns" in copilot

    invariantes = _read(".github/agents/workflows/invariantes-e-protocolos.md")
    assert "CA-03" in invariantes and "CA-04" in invariantes and "CA-05" in invariantes
    assert "(Recomendado)" in invariantes

    fragment = _read("tools/agent_protocol_sync/_execution-protocol-fragment.md")
    assert "R-027" in fragment
    assert "(Recomendado)" in fragment
    assert "allowFreeformInput: true" in fragment


@pytest.mark.parametrize(
    "tpl_path",
    [
        ".github/agents/templates/agent-template.md",
        ".github/agents/templates/operational-agent.md",
        ".github/agents/templates/research-agent.md",
        ".github/agents/templates/router-agent.md",
        ".github/prompts/templates/prompt-template.md",
    ],
)
def test_ca06_templates_include_ask_questions_contract(tpl_path: str) -> None:
    content = _read(tpl_path)
    assert "R-027" in content
    assert "CA-03..CA-05" in content
    assert "(Recomendado)" in content
