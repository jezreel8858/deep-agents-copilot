"""
test_plan_lessons_harvester_governance.py — Sensores determinísticos para o contrato
de colheita de lições do @plan-critic (/plan-lessons-harvester), checklist pré-voo
lazy (C1–C9) e selo de idempotência (lessons_extracted, lessons_applied_to, lessons_at).
"""

from __future__ import annotations

import re
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKLIST_PATH = (
    REPO_ROOT
    / ".github"
    / "skills"
    / "plan-conformance-patterns"
    / "references"
    / "planner-preflight-checklist.md"
)
SKILL_PATH = REPO_ROOT / ".github" / "skills" / "plan-conformance-patterns" / "SKILL.md"
R064_REF_PATH = (
    REPO_ROOT
    / ".github"
    / "skills"
    / "plan-conformance-patterns"
    / "references"
    / "plan-frontmatter-r064.md"
)
GOV_TMPL_PATH = (
    REPO_ROOT
    / ".github"
    / "skills"
    / "governance-audit-patterns"
    / "references"
    / "plan-template-governance.md"
)
HARVESTER_PROMPT_PATH = REPO_ROOT / ".github" / "prompts" / "plan-lessons-harvester.prompt.md"
PROMPTS_CATALOG_PATH = REPO_ROOT / ".github" / "prompts" / "catalog.yaml"
PROMPTS_README_PATH = REPO_ROOT / ".github" / "prompts" / "README.md"
PROMPTS_QUICKSTART_PATH = REPO_ROOT / ".github" / "prompts" / "QUICK-START.md"

PLANNER_AGENTS = [
    REPO_ROOT / ".github" / "agents" / "agent-auditor.agent.md",
    REPO_ROOT / ".github" / "agents" / "tech-solution-architect.agent.md",
    REPO_ROOT / ".github" / "agents" / "bug-triage.agent.md",
    REPO_ROOT / ".github" / "agents" / "requirements-analyst.agent.md",
    REPO_ROOT / ".github" / "agents" / "governance-factory.agent.md",
    REPO_ROOT / ".github" / "agents" / "backend" / "python" / "python-arch-advisor.agent.md",
]


def filter_eligible_plans(plans_root: Path) -> list[Path]:
    """Retorna planos em plans_root cujo frontmatter YAML tem lessons_extracted ausente ou False."""
    eligible: list[Path] = []
    for md_file in sorted(plans_root.rglob("*.md")):
        if md_file.name == "README.md":
            continue
        text = md_file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not match:
            continue
        fm = yaml.safe_load(match.group(1)) or {}
        if fm.get("lessons_extracted") is not True:
            eligible.append(md_file)
    return eligible


def test_t1_lessons_contract_in_references_and_skill():
    """T1: Referências R-064, template governance e SKILL.md documentam lessons_* e o checklist pré-voo."""
    r064_text = R064_REF_PATH.read_text(encoding="utf-8")
    gov_text = GOV_TMPL_PATH.read_text(encoding="utf-8")
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    for key in ("lessons_extracted", "lessons_applied_to", "lessons_at"):
        assert key in r064_text, f"{key} deve estar documentado em plan-frontmatter-r064.md"
        assert key in gov_text, f"{key} deve estar documentado em plan-template-governance.md"
        assert key in skill_text, f"{key} deve estar referenciado em plan-conformance-patterns/SKILL.md"

    assert "planner-preflight-checklist.md" in skill_text


def test_t2_planner_preflight_checklist_budget_and_agent_pointers():
    """T2: Checklist lazy <= 40 linhas e <= 2048 bytes cobrindo C1–C9, e ponteiro <= 200 chars nos 6 planejadores."""
    assert CHECKLIST_PATH.exists(), "planner-preflight-checklist.md deve existir"
    raw_bytes = CHECKLIST_PATH.read_bytes()
    text = raw_bytes.decode("utf-8")
    lines = text.splitlines()

    assert len(lines) <= 40, f"Checklist excede 40 linhas: {len(lines)}"
    assert len(raw_bytes) <= 2048, f"Checklist excede 2048 bytes: {len(raw_bytes)}"

    for cls_id in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"):
        assert cls_id in text, f"Classe {cls_id} ausente em planner-preflight-checklist.md"

    for agent_path in PLANNER_AGENTS:
        assert agent_path.exists(), f"Agent planejador ausente: {agent_path}"
        agent_lines = agent_path.read_text(encoding="utf-8").splitlines()
        matching = [ln for ln in agent_lines if "planner-preflight-checklist.md" in ln]
        assert matching, f"Ponteiro para planner-preflight-checklist.md ausente em {agent_path}"
        assert all(len(ln) <= 200 for ln in matching), (
            f"Ponteiro em {agent_path} excede 200 caracteres: {[len(ln) for ln in matching]}"
        )


def test_t3_plan_lessons_harvester_prompt_two_phases_and_safeguards():
    """T3: Prompt /plan-lessons-harvester declara frontmatter válido, Fase 1 Read-Only, HITL e Fase 2 pós-pytest."""
    assert HARVESTER_PROMPT_PATH.exists(), "plan-lessons-harvester.prompt.md deve existir"
    text = HARVESTER_PROMPT_PATH.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    assert m, "Frontmatter YAML ausente em plan-lessons-harvester.prompt.md"
    fm = yaml.safe_load(m.group(1))

    assert fm.get("name") == "plan-lessons-harvester"
    assert fm.get("router_bypass") == "slash_workflow"
    assert fm.get("model") == "Gemini 4 Argon"
    tools = set(fm.get("tools") or [])
    for required_tool in (
        "ask_questions",
        "get_errors",
        "run_subagent",
        "context-mode/ctx_execute",
        "context-mode/ctx_batch",
        "context-mode/ctx_search",
    ):
        assert required_tool in tools, f"Tool obrigatória ausente no prompt: {required_tool}"

    for marker in (
        "Fase 1",
        "Fase 2",
        "lessons_extracted != true",
        "ask_questions",
        "@governance-maintainer",
        "pytest tests/governance_audit/",
        "OWASP ASI01 / ASI06",
    ):
        assert marker in text, f"Marcador contratual '{marker}' ausente em plan-lessons-harvester.prompt.md"


def test_t4_catalog_readme_quickstart_parity_r015():
    """T4: Paridade R-015 entre plan-lessons-harvester.prompt.md, catalog.yaml, README.md e QUICK-START.md."""
    cat_data = yaml.safe_load(PROMPTS_CATALOG_PATH.read_text(encoding="utf-8"))
    entries = [p for p in cat_data.get("prompts", []) if p.get("name") == "plan-lessons-harvester"]
    assert len(entries) == 1, "plan-lessons-harvester deve possuir exatamente 1 entrada em .github/prompts/catalog.yaml"
    entry = entries[0]
    assert entry.get("path") == ".github/prompts/plan-lessons-harvester.prompt.md"
    assert entry.get("router_bypass") == "slash_workflow"

    assert "/plan-lessons-harvester" in PROMPTS_README_PATH.read_text(encoding="utf-8")
    assert "/plan-lessons-harvester" in PROMPTS_QUICKSTART_PATH.read_text(encoding="utf-8")


def test_t5_idempotency_filter_helper_with_tmp_path(tmp_path: Path):
    """T5: Helper filtra corretamente planos com lessons_extracted: true (ignorado) vs false/ausente (elegível)."""
    p_sealed = tmp_path / "sealed.md"
    p_sealed.write_text(
        "---\nstatus: APPROVED\nlessons_extracted: true\nlessons_applied_to: []\nlessons_at: '2026-11-15'\n---\n# Sealed\n",
        encoding="utf-8",
    )
    p_false = tmp_path / "explicit_false.md"
    p_false.write_text(
        "---\nstatus: APPROVED\nlessons_extracted: false\n---\n# False\n",
        encoding="utf-8",
    )
    p_missing = tmp_path / "missing_key.md"
    p_missing.write_text(
        "---\nstatus: APPROVED\n---\n# Missing\n",
        encoding="utf-8",
    )

    eligible = filter_eligible_plans(tmp_path)
    assert eligible == [p_false, p_missing], (
        f"Apenas explicit_false.md e missing_key.md devem ser elegíveis; obtido: {eligible}"
    )
