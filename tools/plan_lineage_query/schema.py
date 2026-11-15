"""Schema SSoT e validador determinístico do Frontmatter R-064 v2 (OTel & @plan-critic)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

CORRELATION_ID_REGEX = r"^[a-z0-9][a-z0-9-]{7,95}$"
_CORRELATION_ID_RE = re.compile(CORRELATION_ID_REGEX)

VALID_WORKFLOW_IDS: set[str] = {
    "WORKFLOW-BUG-FIX",
    "WORKFLOW-FEATURE-DEVELOPMENT",
    "WORKFLOW-REFACTORING",
    "WORKFLOW-FRAMEWORK-MIGRATION",
    "WORKFLOW-GOVERNANCE-MAINTENANCE",
    "WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION",
    "WORKFLOW-TECHNICAL-ANALYSIS",
    "WORKFLOW-RELEASE-READINESS",
    "WORKFLOW-PROMPT-SYNTHESIS",
    "WORKFLOW-UI-LAYOUT",
}

VALID_RUBRIC_GAP_CODES: set[str] = {
    "T1-1",
    "T1-2",
    "T1-3",
    "T1-4",
    "T1-5",
    "T1-6",
    "T1-7",
    "T1-8",
    "T2-1",
    "T2-2",
    "T2-3",
    "T2-4",
    "T2-5",
    "T2-6",
    "T2-7",
    "T2-SCOPE",
    "T2-YAGNI",
    "T2-TRACE",
    "T2-ALT",
    "T2-ADR",
    "T2-TEST",
    "T2-SEC",
    "T2-COH",
    "T2-CONS",
    "T2-COMP",
}

VALID_REVIEW_VERDICTS: set[str | None] = {
    "PASS",
    "PASS_WITH_NITS",
    "NEEDS_REVISION",
    "ESCALATED_HITL",
    "PENDING",
    None,
}

V2_CUTOFF_DATE = "2026-11-15"

V2_KEYS: set[str] = {
    "session_id",
    "workflow_id",
    "workflow_trace_id",
    "parent_plan_ref",
    "critic_rubric_gaps",
    "critic_findings_summary",
}

SUMMARY_REQUIRED_KEYS: set[str] = {
    "rounds",
    "blockers",
    "majors",
    "minors",
    "nits",
    "last_verdict",
    "author_ref",
}


def _extract_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        return {}
    try:
        loaded = yaml.safe_load(match.group(1))
        return loaded if isinstance(loaded, dict) else {}
    except yaml.YAMLError:
        return {}


def is_v2_eligible(frontmatter: dict[str, Any]) -> bool:
    """Retorna True se created_at >= V2_CUTOFF_DATE ou se houver opt-in explícito de chaves v2."""
    created_at = str(frontmatter.get("created_at", ""))
    if created_at >= V2_CUTOFF_DATE:
        return True
    return bool(V2_KEYS & set(frontmatter.keys()))


def validate_plan_v2_frontmatter(
    frontmatter: dict[str, Any],
    plan_rel_path: str,
    repo_root: Path,
) -> list[str]:
    """Valida os campos do Schema v2 R-064. Planos legados sem opt-in retornam []."""
    if not is_v2_eligible(frontmatter):
        return []

    errors: list[str] = []
    missing_v2 = sorted(V2_KEYS - set(frontmatter.keys()))
    if missing_v2:
        errors.append(
            f"[{plan_rel_path}] T1-8 chaves v2 obrigatórias ausentes: {missing_v2}"
        )

    session_id = frontmatter.get("session_id")
    if not isinstance(session_id, str) or not _CORRELATION_ID_RE.match(session_id):
        errors.append(
            f"[{plan_rel_path}] T1-8 session_id inválido ({session_id!r}); deve respeitar {CORRELATION_ID_REGEX}"
        )

    workflow_trace_id = frontmatter.get("workflow_trace_id")
    if not isinstance(workflow_trace_id, str) or not _CORRELATION_ID_RE.match(workflow_trace_id):
        errors.append(
            f"[{plan_rel_path}] T1-8 workflow_trace_id inválido ({workflow_trace_id!r}); deve respeitar {CORRELATION_ID_REGEX}"
        )

    workflow_id = frontmatter.get("workflow_id")
    if workflow_id not in VALID_WORKFLOW_IDS:
        errors.append(
            f"[{plan_rel_path}] T1-8 workflow_id inválido ({workflow_id!r}); esperado um de {sorted(VALID_WORKFLOW_IDS)}"
        )

    parent_ref = frontmatter.get("parent_plan_ref")
    if not isinstance(parent_ref, str) or not parent_ref.strip():
        errors.append(f"[{plan_rel_path}] T1-8 parent_plan_ref ausente ou vazio")
    elif parent_ref != "N/A — plano raiz":
        if not parent_ref.startswith("docs/plans/"):
            errors.append(
                f"[{plan_rel_path}] T1-8 parent_plan_ref deve ser 'N/A — plano raiz' ou caminho sob 'docs/plans/': {parent_ref!r}"
            )
        else:
            parent_abs = (repo_root / parent_ref).resolve()
            plans_root = (repo_root / "docs" / "plans").resolve()
            try:
                parent_abs.relative_to(plans_root)
            except ValueError:
                errors.append(
                    f"[{plan_rel_path}] T1-8 parent_plan_ref fora de docs/plans/: {parent_ref!r}"
                )
            else:
                if not parent_abs.is_file():
                    errors.append(
                        f"[{plan_rel_path}] T1-8 parent_plan_ref aponta para arquivo inexistente: {parent_ref!r}"
                    )
                else:
                    parent_fm = _extract_frontmatter(parent_abs)
                    if "session_id" in parent_fm and parent_fm.get("session_id") != session_id:
                        errors.append(
                            f"[{plan_rel_path}] T1-8 divergência de herança de session_id com plano pai ({parent_ref}): "
                            f"{session_id!r} != {parent_fm.get('session_id')!r}"
                        )
                    if (
                        "workflow_trace_id" in parent_fm
                        and parent_fm.get("workflow_trace_id") != workflow_trace_id
                    ):
                        errors.append(
                            f"[{plan_rel_path}] T1-8 divergência de herança de workflow_trace_id com plano pai ({parent_ref}): "
                            f"{workflow_trace_id!r} != {parent_fm.get('workflow_trace_id')!r}"
                        )

    gaps = frontmatter.get("critic_rubric_gaps")
    if not isinstance(gaps, list):
        errors.append(f"[{plan_rel_path}] T1-8 critic_rubric_gaps deve ser uma lista")
    else:
        if len(gaps) > 15:
            errors.append(
                f"[{plan_rel_path}] T1-8 critic_rubric_gaps excede o limite de 15 itens ({len(gaps)})"
            )
        invalid_gaps = [g for g in gaps if g not in VALID_RUBRIC_GAP_CODES]
        if invalid_gaps:
            errors.append(
                f"[{plan_rel_path}] T1-8 critic_rubric_gaps contém códigos inválidos: {invalid_gaps}"
            )

    summary = frontmatter.get("critic_findings_summary")
    if not isinstance(summary, dict):
        errors.append(f"[{plan_rel_path}] T1-8 critic_findings_summary deve ser um dict")
    else:
        missing_sum_keys = sorted(SUMMARY_REQUIRED_KEYS - set(summary.keys()))
        if missing_sum_keys:
            errors.append(
                f"[{plan_rel_path}] T1-8 critic_findings_summary sem chaves obrigatórias: {missing_sum_keys}"
            )
        for num_key in ("rounds", "blockers", "majors", "minors", "nits"):
            val = summary.get(num_key)
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                errors.append(
                    f"[{plan_rel_path}] T1-8 critic_findings_summary.{num_key} deve ser inteiro >= 0 (recebido: {val!r})"
                )
        last_verdict = summary.get("last_verdict")
        if last_verdict not in VALID_REVIEW_VERDICTS:
            errors.append(
                f"[{plan_rel_path}] T1-8 critic_findings_summary.last_verdict inválido: {last_verdict!r}"
            )
        author = frontmatter.get("author")
        author_ref = summary.get("author_ref")
        if author_ref != author:
            errors.append(
                f"[{plan_rel_path}] T1-8 critic_findings_summary.author_ref ({author_ref!r}) != author ({author!r})"
            )

    author = frontmatter.get("author")
    reviewer = frontmatter.get("reviewer")
    if reviewer is not None and reviewer == author:
        errors.append(
            f"[{plan_rel_path}] T1-8 violação de segregação de funções: reviewer ({reviewer!r}) == author ({author!r})"
        )

    review_verdict = frontmatter.get("review_verdict")
    if review_verdict not in VALID_REVIEW_VERDICTS:
        errors.append(
            f"[{plan_rel_path}] T1-8 review_verdict inválido: {review_verdict!r}"
        )

    return errors


PRE_PLAN_REF = "N/A — pré-plano"
HANDOFF_SUMMARY_MAX_LINES = 5
HANDOFF_SUMMARY_MAX_CHARS = 500
ASI06_FORBIDDEN_PATTERNS = (
    "IGNORE ALL PREVIOUS INSTRUCTIONS",
    "IGNORE PREVIOUS INSTRUCTIONS",
    "SYSTEM OVERRIDE",
    "DISREGARD ALL RULES",
    "BYPASS GOVERNANCE",
)


def is_valid_active_plan_ref(value: str) -> bool:
    """Valida active_plan_ref admitindo o marcador canônico pré-plano ou caminho docs/plans/."""
    if not isinstance(value, str) or not value.strip():
        return False
    if value == PRE_PLAN_REF:
        return True
    return value.startswith("docs/plans/") and value.endswith(".md")


def validate_handoff_summary_asi06(summary: str) -> list[str]:
    """Valida handoff_summary contra limites R-064 (<= 5 linhas, <= 500 chars) e OWASP ASI06."""
    errors: list[str] = []
    if not isinstance(summary, str):
        return ["handoff_summary deve ser uma string."]
    lines = summary.splitlines()
    if len(lines) > HANDOFF_SUMMARY_MAX_LINES:
        errors.append(
            f"handoff_summary excede o limite de {HANDOFF_SUMMARY_MAX_LINES} linhas (obtido: {len(lines)})."
        )
    if len(summary) > HANDOFF_SUMMARY_MAX_CHARS:
        errors.append(
            f"handoff_summary excede o limite de {HANDOFF_SUMMARY_MAX_CHARS} caracteres (obtido: {len(summary)})."
        )
    upper = summary.upper()
    for pat in ASI06_FORBIDDEN_PATTERNS:
        if pat in upper:
            errors.append(f"handoff_summary contém padrão imperativo proibido (OWASP ASI06): '{pat}'.")
    return errors
