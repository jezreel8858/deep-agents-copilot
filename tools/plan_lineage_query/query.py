"""Motor Read-Only de leitura, filtragem e agregação de planos R-064 em docs/plans/."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .schema import is_v2_eligible, validate_plan_v2_frontmatter

MAX_PLAN_FILE_BYTES = 256 * 1024  # 256 KB


class PathTraversalError(ValueError):
    """Erro disparado quando o caminho de busca escapa do repositório."""


def resolve_confined_plans_root(repo_root: Path, plans_root_arg: str | Path) -> Path:
    """Garante que o diretório de planos está estritamente contido dentro de repo_root."""
    repo_abs = repo_root.resolve()
    candidate = Path(plans_root_arg)
    target_abs = (repo_abs / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    try:
        target_abs.relative_to(repo_abs)
    except ValueError as exc:
        raise PathTraversalError(
            f"Diretório '{plans_root_arg}' escapa do limite do repositório '{repo_abs}'."
        ) from exc
    if not target_abs.exists() or not target_abs.is_dir():
        raise PathTraversalError(
            f"Diretório de planos inexistente ou inválido: '{target_abs}'."
        )
    return target_abs


def _parse_plan_file(path: Path, repo_root: Path) -> dict[str, Any] | None:
    size = path.stat().st_size
    if size > MAX_PLAN_FILE_BYTES:
        raise ValueError(f"Arquivo excede o limite de 256 KB ({size} bytes): {path}")
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        return None
    loaded = yaml.safe_load(match.group(1))
    if not isinstance(loaded, dict):
        return None
    rel_path = path.resolve().relative_to(repo_root.resolve()).as_posix()
    v2 = is_v2_eligible(loaded)
    validation_errors = validate_plan_v2_frontmatter(loaded, rel_path, repo_root)
    return {
        "plan_path": rel_path,
        "plan_type": loaded.get("plan_type"),
        "status": loaded.get("status"),
        "approved": loaded.get("approved"),
        "author": loaded.get("author"),
        "created_at": str(loaded.get("created_at", "")),
        "session_id": loaded.get("session_id"),
        "workflow_id": loaded.get("workflow_id"),
        "workflow_trace_id": loaded.get("workflow_trace_id"),
        "parent_plan_ref": loaded.get("parent_plan_ref"),
        "review_verdict": loaded.get("review_verdict"),
        "review_rounds": loaded.get("review_rounds"),
        "reviewer": loaded.get("reviewer"),
        "critic_rubric_gaps": list(loaded.get("critic_rubric_gaps") or []),
        "critic_findings_summary": loaded.get("critic_findings_summary"),
        "is_v2": v2,
        "validation_errors": validation_errors,
        "frontmatter": loaded,
    }


def load_all_plans(
    repo_root: Path,
    plans_root: str | Path = "docs/plans",
) -> list[dict[str, Any]]:
    """Carrega todos os planos em docs/plans/<tipo>/*.md com confinamento e limite de 256 KB."""
    target_root = resolve_confined_plans_root(repo_root, plans_root)
    records: list[dict[str, Any]] = []
    for sub in sorted(target_root.iterdir()):
        if not sub.is_dir():
            continue
        for md_file in sorted(sub.glob("*.md")):
            if md_file.name == "README.md":
                continue
            parsed = _parse_plan_file(md_file, repo_root)
            if parsed is not None:
                records.append(parsed)
    return records


def query_plans(
    records: list[dict[str, Any]],
    *,
    session_id: str | None = None,
    workflow_id: str | None = None,
    workflow_trace_id: str | None = None,
    author: str | None = None,
    gap_code: str | None = None,
    include_legacy: bool = False,
) -> list[dict[str, Any]]:
    """Filtra os registros de planos conforme critérios fornecidos."""
    results: list[dict[str, Any]] = []
    for rec in records:
        if not include_legacy and not rec["is_v2"]:
            continue
        if session_id and rec.get("session_id") != session_id:
            continue
        if workflow_id and rec.get("workflow_id") != workflow_id:
            continue
        if workflow_trace_id and rec.get("workflow_trace_id") != workflow_trace_id:
            continue
        if author and rec.get("author") != author:
            continue
        if gap_code and gap_code not in (rec.get("critic_rubric_gaps") or []):
            continue
        results.append(rec)
    return results


def compute_curation_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Agrega gaps recorrentes por (author, gap_code) com flag requires_hitl=True (OWASP ASI06)."""
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    for rec in records:
        author = str(rec.get("author") or "UNKNOWN")
        trace_id = rec.get("workflow_trace_id")
        plan_path = rec["plan_path"]
        for gap in rec.get("critic_rubric_gaps") or []:
            key = (author, str(gap))
            if key not in buckets:
                buckets[key] = {
                    "author": author,
                    "gap_code": str(gap),
                    "occurrences": 0,
                    "workflow_trace_ids": [],
                    "plan_paths": [],
                    "requires_hitl": True,
                }
            entry = buckets[key]
            entry["occurrences"] += 1
            if trace_id and trace_id not in entry["workflow_trace_ids"]:
                entry["workflow_trace_ids"].append(trace_id)
            if plan_path not in entry["plan_paths"]:
                entry["plan_paths"].append(plan_path)

    return sorted(
        buckets.values(),
        key=lambda item: (-item["occurrences"], item["author"], item["gap_code"]),
    )
