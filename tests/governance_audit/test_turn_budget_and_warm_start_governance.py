from __future__ import annotations
import glob
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
COPILOT_INSTRUCTIONS = REPO_ROOT / ".github" / "copilot-instructions.md"
AGENT_TEMPLATE = REPO_ROOT / ".github" / "agents" / "templates" / "agent-template.md"
CKG_AGENT = REPO_ROOT / ".github" / "agents" / "code-knowledge-graph.agent.md"
CODEGRAPH_SKILL = REPO_ROOT / ".github" / "skills" / "codegraph-optave-usage" / "SKILL.md"
EFFICIENT_BATCH_SKILL = REPO_ROOT / ".github" / "skills" / "efficient-batch-code-modification" / "SKILL.md"
CHANGELOG_MD = REPO_ROOT / "CHANGELOG.md"

AGENTS_DIR = REPO_ROOT / ".github" / "agents"

CONTROL_CHARS = {chr(7): "BELL", chr(8): "BACKSPACE", chr(12): "FORMFEED"}


def get_all_agent_files() -> list[Path]:
    return [p for p in AGENTS_DIR.glob("**/*.agent.md") if "templates" not in p.parts]


def get_non_router_agent_files() -> list[Path]:
    all_agents = get_all_agent_files()
    return [
        p for p in all_agents
        if not p.name.endswith("-router.agent.md")
        and p.name != "agent-router.agent.md"
        and p.name != "prompt-structuring.agent.md"
    ]


def test_r060_declared_in_claude_md():
    text = CLAUDE_MD.read_text(encoding="utf-8")
    assert "R-060" in text
    assert "Teto R" in text
    assert "Warm Start" in text
    assert "Consolida" in text


def test_r060_declared_in_copilot_instructions():
    text = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
    assert "R-060" in text
    assert "Teto R" in text
    assert "Warm Start" in text
    assert "Edge Truncation" in text or "Destila" in text


def test_codegraph_skill_declares_warm_start_and_batch_querying():
    text = CODEGRAPH_SKILL.read_text(encoding="utf-8")
    assert "Warm Start" in text
    assert "Build-if-Missing" in text
    assert "batch_query" in text


def test_efficient_batch_skill_declares_turn_budget_and_edge_truncation():
    text = EFFICIENT_BATCH_SKILL.read_text(encoding="utf-8")
    assert "Teto R" in text
    assert "Circuit Breaker" in text
    assert "Edge Truncation" in text


def test_agent_template_declares_turn_budget_in_execution_protocol():
    text = AGENT_TEMPLATE.read_text(encoding="utf-8")
    assert "<execution_protocol>" in text
    assert "Teto R" in text
    assert "R-060" in text


def test_code_knowledge_graph_declares_turn_budget_and_warm_start():
    text = CKG_AGENT.read_text(encoding="utf-8")
    assert "<execution_protocol>" in text
    assert "Teto R" in text
    assert "Build-if-Missing" in text
    assert "batch_query" in text


def test_changelog_documents_r060():
    text = CHANGELOG_MD.read_text(encoding="utf-8")
    assert "R-060" in text
    assert "2.33.0" in text


def test_all_non_router_agents_declare_r060_turn_budget():
    """
    Garante propagacao sistemica de R-060 (Teto de Tool Turns, Warm Start,
    Batch Querying) para 100 por cento dos agentes executores nao-roteadores.
    Previne a regressao do gap onde R-060 existia apenas no template e no
    code-knowledge-graph, mas nao nos demais 76 agentes executores.
    """
    non_routers = get_non_router_agent_files()
    missing = []
    for af in non_routers:
        text = af.read_text(encoding="utf-8")
        if "R-060" not in text:
            missing.append(str(af.relative_to(REPO_ROOT)))
    assert not missing, (
        f"Agentes nao-roteadores sem R-060 no execution_protocol ({len(missing)}):\n"
        + "\n".join(missing)
    )


def test_no_control_character_corruption_in_governance_files():
    """
    Guardrail anti-regressao: escapes Python (\\a, \\b, \\f) executados via
    shell sandbox podem corromper texto em BELL/BACKSPACE/FORMFEED quando
    strings contem sequencias tipo ask_questions, build-if-missing,
    batch_query, find_cycles. Este teste garante zero caracteres de
    controle em todos os arquivos de governanca versionados.
    """
    files_to_scan = get_all_agent_files() + [
        CLAUDE_MD,
        COPILOT_INSTRUCTIONS,
        AGENT_TEMPLATE,
        CODEGRAPH_SKILL,
        EFFICIENT_BATCH_SKILL,
        CHANGELOG_MD,
    ]
    violations = []
    for fp in files_to_scan:
        text = fp.read_text(encoding="utf-8")
        for ch, desc in CONTROL_CHARS.items():
            if ch in text:
                violations.append(f"[{fp.relative_to(REPO_ROOT)}] caractere de controle {desc} detectado")
    assert not violations, (
        f"Corrupcao de caracteres de controle detectada ({len(violations)}):\n"
        + "\n".join(violations)
    )
