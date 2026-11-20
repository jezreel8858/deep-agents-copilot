"""CLI determinístico zero-dependência para consulta e auditoria dos logs JSONL de sessão (P4 / P7)."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_AUDIT_DIR = Path(".context") / "audit"
RULE_PATTERN = re.compile(r"\b(R-\d{3}|Invariante \d+)\b")


def load_audit_entries(
    audit_dir: Path = DEFAULT_AUDIT_DIR,
    workflow_trace_id: str | None = None,
    session_id: str | None = None,
    agent: str | None = None,
    failures_only: bool = False,
) -> list[dict[str, Any]]:
    """Carrega e filtra registros JSONL append-only de auditoria."""
    if not audit_dir.exists():
        return []

    target_files = (
        [audit_dir / f"{workflow_trace_id}.jsonl"]
        if workflow_trace_id
        else sorted(audit_dir.glob("*.jsonl"))
    )

    entries: list[dict[str, Any]] = []
    for file_path in target_files:
        if not file_path.exists() or not file_path.is_file():
            continue
        for line_num, raw_line in enumerate(
            file_path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                record = {
                    "parse_error": str(exc),
                    "source_file": str(file_path),
                    "line": line_num,
                    "decision": "block",
                }

            if session_id and record.get("session_id") != session_id:
                continue
            if agent and record.get("agent") != agent:
                continue
            if failures_only and not _is_failure(record):
                continue
            entries.append(record)

    return entries


def _is_failure(record: dict[str, Any]) -> bool:
    return (
        record.get("decision") == "block"
        or bool(record.get("drift_detected"))
        or record.get("status") in {"failed", "blocked"}
        or bool(record.get("errors"))
    )


def _extract_rule_code(record: dict[str, Any]) -> str:
    errors = record.get("errors") or []
    joined = " | ".join(str(e) for e in errors)
    if "micro_task_scope_violation" in joined:
        return "R-068:micro_task_scope"
    if "plan_drift_detected" in joined or record.get("drift_detected"):
        return "R-064:plan_drift"
    match = RULE_PATTERN.search(joined)
    if match:
        return match.group(1)
    return "RUNTIME_FAILURE"


def summarize_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Gera estatísticas agregadas de conformidade, drifts e bloqueios."""
    by_agent: Counter[str] = Counter()
    by_decision: Counter[str] = Counter()
    drift_count = 0
    total_files_touched = 0

    for item in entries:
        by_agent[str(item.get("agent", "unknown"))] += 1
        by_decision[str(item.get("decision", "unknown"))] += 1
        if item.get("drift_detected"):
            drift_count += 1
        total_files_touched += int(item.get("files_touched_count") or 0)

    failures = [item for item in entries if _is_failure(item)]
    return {
        "total_events": len(entries),
        "failures_count": len(failures),
        "drift_count": drift_count,
        "total_files_touched": total_files_touched,
        "by_decision": dict(by_decision),
        "by_agent": dict(by_agent),
        "failure_samples": failures[-10:],
    }


def harvest_lesson_candidates(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Agrupa falhas operacionais em candidatos de lição e regressão para /plan-lessons-harvester (P7)."""
    failures = [item for item in entries if _is_failure(item)]
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

    for item in failures:
        agent_slug = str(item.get("agent") or "unknown")
        rule_code = _extract_rule_code(item)
        plan_ref = str(item.get("plan_ref") or "N/A")
        grouped[(agent_slug, rule_code, plan_ref)].append(item)

    candidates: list[dict[str, Any]] = []
    for (agent_slug, rule_code, plan_ref), items in sorted(
        grouped.items(), key=lambda kv: (-len(kv[1]), kv[0][0], kv[0][1])
    ):
        sample_errors: list[str] = []
        for it in items:
            for err in it.get("errors") or []:
                err_str = str(err)
                if err_str not in sample_errors:
                    sample_errors.append(err_str)
                if len(sample_errors) >= 3:
                    break
            if len(sample_errors) >= 3:
                break

        suggested_target = (
            ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md"
            if rule_code.startswith("R-064")
            else f".github/agents/{agent_slug.lstrip('@')}.agent.md"
            if agent_slug.startswith("@") and agent_slug != "unknown"
            else ".github/skills/agent-contracts/references/receipt-step-delta-schema.yaml"
        )

        candidates.append(
            {
                "agent": agent_slug,
                "rule_code": rule_code,
                "plan_ref": plan_ref,
                "occurrences": len(items),
                "workflow_traces": sorted(
                    {str(it.get("workflow_trace_id") or "unknown") for it in items}
                ),
                "sample_errors": sample_errors,
                "suggested_hardening_target": suggested_target,
                "recommended_regression_suite": "tests/operational_flow/test_stop_hook_receipt_validator.py",
            }
        )

    return {
        "total_failures_analyzed": len(failures),
        "candidates_count": len(candidates),
        "candidates": candidates,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Consulta forense de trilhas append-only .context/audit/*.jsonl (P4/P7)."
    )
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=DEFAULT_AUDIT_DIR,
        help="Diretório base dos arquivos JSONL (padrão: .context/audit)",
    )
    parser.add_argument("--workflow-trace-id", help="Filtra por workflow_trace_id específico")
    parser.add_argument("--session-id", help="Filtra por session_id específico")
    parser.add_argument("--agent", help="Filtra por slug do agente (ex.: @spring-boot-developer)")
    parser.add_argument(
        "--failures-only",
        action="store_true",
        help="Retorna apenas eventos bloqueados, com falha ou plan_drift_detected",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Emite resumo estatístico agregado em JSON",
    )
    parser.add_argument(
        "--harvest-lessons",
        action="store_true",
        help="Agrupa falhas recorrentes em candidatos de lição/regressão para /plan-lessons-harvester (P7)",
    )
    args = parser.parse_args(argv)

    entries = load_audit_entries(
        audit_dir=args.audit_dir,
        workflow_trace_id=args.workflow_trace_id,
        session_id=args.session_id,
        agent=args.agent,
        failures_only=args.failures_only,
    )

    if args.harvest_lessons:
        payload: Any = harvest_lesson_candidates(entries)
    elif args.stats:
        payload = summarize_entries(entries)
    else:
        payload = {"count": len(entries), "entries": entries}

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())