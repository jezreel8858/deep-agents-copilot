"""CLI Read-Only para consulta de linhagem OTel e telemetria do @plan-critic (R-064 v2)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .query import (
    PathTraversalError,
    compute_curation_candidates,
    load_all_plans,
    query_plans,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.plan_lineage_query",
        description="Consulta Read-Only de linhagem OTel e telemetria cética dos planos R-064.",
    )
    parser.add_argument("--session-id", dest="session_id", help="Filtra por session_id")
    parser.add_argument("--workflow-id", dest="workflow_id", help="Filtra por workflow_id")
    parser.add_argument(
        "--workflow-trace-id", dest="workflow_trace_id", help="Filtra por workflow_trace_id"
    )
    parser.add_argument("--author", dest="author", help="Filtra por author (ex.: @tech-solution-architect)")
    parser.add_argument("--gap-code", dest="gap_code", help="Filtra por código de rubrica em critic_rubric_gaps")
    parser.add_argument(
        "--include-legacy",
        action="store_true",
        help="Inclui planos legados (v1 sem chaves v2)",
    )
    parser.add_argument(
        "--curation-candidates",
        action="store_true",
        help="Agrega candidatos de curadoria por (author, gap_code) sob proteção OWASP ASI06 (requires_hitl=True)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Retorna exit code 1 se houver qualquer violação de schema v2 nos planos analisados",
    )
    parser.add_argument(
        "--format",
        choices=("json", "md"),
        default="json",
        help="Formato de saída (json ou md)",
    )
    parser.add_argument(
        "--root",
        default="docs/plans",
        help="Diretório raiz dos planos relativo ao repositório (default: docs/plans)",
    )
    return parser


def _render_markdown(payload: dict) -> str:
    lines = ["# Plan Lineage & Critic Telemetry Query (R-064 v2)", ""]
    lines.append(f"- **Total Plans Matched**: {payload['count']}")
    if payload.get("curation_candidates") is not None:
        lines.append("")
        lines.append("## Curation Candidates (OWASP ASI06 — requires_hitl: true)")
        lines.append("| Author | Gap Code | Occurrences | Workflow Trace IDs | Requires HITL |")
        lines.append("|---|---|---|---|---|")
        for item in payload["curation_candidates"]:
            traces = ", ".join(item["workflow_trace_ids"]) or "N/A"
            lines.append(
                f"| {item['author']} | {item['gap_code']} | {item['occurrences']} | {traces} | {item['requires_hitl']} |"
            )
    lines.append("")
    lines.append("## Plans")
    lines.append("| Plan Path | Type | Author | Session ID | Workflow ID | Trace ID | Verdict |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in payload["plans"]:
        lines.append(
            f"| {p['plan_path']} | {p['plan_type']} | {p['author']} | "
            f"{p.get('session_id') or 'N/A'} | {p.get('workflow_id') or 'N/A'} | "
            f"{p.get('workflow_trace_id') or 'N/A'} | {p.get('review_verdict') or 'N/A'} |"
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None, repo_root: Path | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    resolved_repo_root = (repo_root or Path(__file__).resolve().parents[2]).resolve()

    try:
        all_records = load_all_plans(resolved_repo_root, args.root)
    except PathTraversalError as exc:
        sys.stderr.write(f"ERROR [path_confinement]: {exc}\n")
        return 2
    except ValueError as exc:
        sys.stderr.write(f"ERROR [validation]: {exc}\n")
        return 1

    filtered = query_plans(
        all_records,
        session_id=args.session_id,
        workflow_id=args.workflow_id,
        workflow_trace_id=args.workflow_trace_id,
        author=args.author,
        gap_code=args.gap_code,
        include_legacy=args.include_legacy,
    )

    all_errors = [err for rec in filtered for err in rec.get("validation_errors", [])]

    serializable_plans = [
        {k: v for k, v in rec.items() if k != "frontmatter"} for rec in filtered
    ]

    payload: dict = {
        "count": len(serializable_plans),
        "plans": serializable_plans,
        "validation_errors": all_errors,
    }
    if args.curation_candidates:
        payload["curation_candidates"] = compute_curation_candidates(filtered)

    if args.format == "md":
        sys.stdout.write(_render_markdown(payload) + "\n")
    else:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    if args.strict and all_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
