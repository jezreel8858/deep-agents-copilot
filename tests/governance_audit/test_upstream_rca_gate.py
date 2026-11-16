"""Gate de regressão estático para R-065 (RCA Upstream Q0 & Anti-Symptom-Patching).

Valida que todas as âncoras normativas introduzidas na Onda 1 (T1 a T8)
permanecem íntegras nos 12 arquivos Markdown de governança, skills, agents e README.
"""

from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

WAVE_1_TARGET_FILES: tuple[str, ...] = (
    ".github/skills/governance-audit-patterns/references/plan-template-governance.md",
    ".github/skills/governance-audit-patterns/SKILL.md",
    ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md",
    ".github/agents/plan-critic.agent.md",
    ".github/agents/agent-auditor.agent.md",
    ".github/agents/governance-factory.agent.md",
    ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".github/agents/workflows.md",
    ".github/agents/workflows/invariantes-e-protocolos.md",
    "CHANGELOG.md",
)

TASK_ANCHORS_SPEC: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "T1-template",
        ".github/skills/governance-audit-patterns/references/plan-template-governance.md",
        (
            "Q0",
            "NEEDS_REVISION",
            "Neutralização na Fonte",
            "Diagnóstico Forense — RCA Upstream (R-055 Q0)",
        ),
    ),
    (
        "T2-skill",
        ".github/skills/governance-audit-patterns/SKILL.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T3-rubric",
        ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md",
        (
            "R-065",
            "Q0",
            "NEEDS_REVISION",
            "T2-RCA",
            "Neutralização na Fonte",
        ),
    ),
    (
        "T4-critic",
        ".github/agents/plan-critic.agent.md",
        (
            "R-065",
            "NEEDS_REVISION",
            "T2-RCA",
            "Neutralização na Fonte",
        ),
    ),
    (
        "T5-auditor",
        ".github/agents/agent-auditor.agent.md",
        (
            "Q0",
        ),
    ),
    (
        "T5-factory",
        ".github/agents/governance-factory.agent.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T6-preflight",
        ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T7-claude",
        "CLAUDE.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T7-copilot",
        ".github/copilot-instructions.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T7-workflows",
        ".github/agents/workflows.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T7-invariantes",
        ".github/agents/workflows/invariantes-e-protocolos.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T8-changelog",
        "CHANGELOG.md",
        (
            "Q0",
            "T2-RCA",
            "Neutralização na Fonte",
        ),
    ),
)


def _read_utf8(rel_path: str) -> str:
    target = REPO_ROOT / rel_path
    assert target.is_file(), f"Arquivo obrigatório de R-065 ausente: {rel_path}"
    return target.read_text(encoding="utf-8")


def test_wave1_target_files_count_and_existence() -> None:
    """Garante que os 12 arquivos da Onda 1 existem e referenciam R-065."""
    assert len(WAVE_1_TARGET_FILES) == 12
    for rel_path in WAVE_1_TARGET_FILES:
        content = _read_utf8(rel_path)
        assert ("R-065" in content or "Q0" in content), f"{rel_path} deve conter referência explícita a R-065 ou Q0"


@pytest.mark.parametrize(
    ("task_id", "rel_path", "expected_anchors"),
    TASK_ANCHORS_SPEC,
    ids=[item[0] for item in TASK_ANCHORS_SPEC],
)
def test_upstream_rca_gate_anchors_t1_to_t8(
    task_id: str,
    rel_path: str,
    expected_anchors: tuple[str, ...],
) -> None:
    """Valida todas as âncoras normativas de T1 a T8 nos 12 arquivos Markdown."""
    content = _read_utf8(rel_path)
    for anchor in expected_anchors:
        assert anchor in content, (
            f"[{task_id}] Âncora obrigatória '{anchor}' ausente em {rel_path}"
        )
