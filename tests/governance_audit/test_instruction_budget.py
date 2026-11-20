"""Guardrails deterministicos de orcamento de instrucoes (Instruction Budget).

Garante que arquivos sempre carregados no contexto do modelo (copilot-instructions,
fragmento sincronizado de protocolo, agent-root, especialistas e SKILL.md) respeitem
tetos rigidos de linhas e nao dupliquem schemas YAML ja centralizados em SSOT (R-003/R-066).
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
COPILOT_INSTRUCTIONS = REPO_ROOT / ".github" / "copilot-instructions.md"
PROTOCOL_FRAGMENT = REPO_ROOT / "tools" / "agent_protocol_sync" / "_execution-protocol-fragment.md"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"
SCHEMA_REF = ".github/skills/agent-contracts/references/receipt-step-delta-schema.yaml"

MAX_COPILOT_INSTRUCTIONS_LINES = 160
MAX_FRAGMENT_LINES = 65
MAX_ROUTER_AGENT_LINES = 550
MAX_SPECIALIST_AGENT_LINES = 460
MAX_SKILL_LINES = 300


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def test_copilot_instructions_within_budget() -> None:
    assert COPILOT_INSTRUCTIONS.exists(), "copilot-instructions.md nao encontrado"
    lines = _line_count(COPILOT_INSTRUCTIONS)
    assert lines <= MAX_COPILOT_INSTRUCTIONS_LINES, (
        f".github/copilot-instructions.md excedeu o teto ({lines} > {MAX_COPILOT_INSTRUCTIONS_LINES} linhas)"
    )


def test_execution_protocol_fragment_compact_and_well_formed() -> None:
    assert PROTOCOL_FRAGMENT.exists(), "_execution-protocol-fragment.md nao encontrado"
    content = PROTOCOL_FRAGMENT.read_text(encoding="utf-8")
    lines = len(content.splitlines())
    assert lines <= MAX_FRAGMENT_LINES, (
        f"_execution-protocol-fragment.md excedeu o teto ({lines} > {MAX_FRAGMENT_LINES} linhas)"
    )
    for marker in (
            "<!-- BEGIN:CORE -->",
            "<!-- END:CORE -->",
            "<!-- BEGIN:CLAUSE_MUTATION -->",
            "<!-- END:CLAUSE_MUTATION -->",
            "<!-- BEGIN:CLAUSE_HANDOFF -->",
            "<!-- END:CLAUSE_HANDOFF -->",
            "<!-- BEGIN:CLAUSE_LAZY_DOCS -->",
            "<!-- END:CLAUSE_LAZY_DOCS -->",
    ):
        assert marker in content, f"Marcador obrigatorio ausente no fragmento: {marker}"

    for rule_id in ("R-059", "R-060", "R-068", "R-051", "R-064", "R-042", "R-066"):
        assert rule_id in content, f"Identificador normativo {rule_id} ausente no fragmento"

    assert SCHEMA_REF in content, (
        f"Fragmento deve apontar para o schema canonico {SCHEMA_REF}"
    )


@pytest.mark.parametrize(
    "agent_file",
    sorted(AGENTS_DIR.rglob("*.agent.md")),
    ids=lambda p: p.relative_to(AGENTS_DIR).as_posix(),
)
def test_agent_files_within_instruction_budget(agent_file: Path) -> None:
    content = agent_file.read_text(encoding="utf-8")
    lines = len(content.splitlines())
    is_router_or_root = (
            agent_file.name == "agent-root.agent.md"
            or agent_file.name.endswith("-router.agent.md")
    )
    limit = MAX_ROUTER_AGENT_LINES if is_router_or_root else MAX_SPECIALIST_AGENT_LINES
    assert lines <= limit, (
        f"{agent_file.relative_to(AGENTS_DIR)} excedeu o orcamento de instrucoes ({lines} > {limit} linhas)"
    )
    assert "exports_and_signatures:" not in content, (
        f"{agent_file.name} contem exemplo YAML inline de step_delta; referencie {SCHEMA_REF}"
    )


@pytest.mark.parametrize(
    "skill_file",
    sorted(SKILLS_DIR.glob("*/SKILL.md")),
    ids=lambda p: p.parent.name,
)
def test_skill_files_respect_progressive_disclosure_budget(skill_file: Path) -> None:
    lines = _line_count(skill_file)
    assert lines <= MAX_SKILL_LINES, (
        f"{skill_file.relative_to(REPO_ROOT)} excedeu o teto R-066 ({lines} > {MAX_SKILL_LINES} linhas)"
    )
