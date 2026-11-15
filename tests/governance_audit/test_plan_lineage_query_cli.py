"""
test_plan_lineage_query_cli.py — Testes determinísticos do pacote CLI Read-Only
tools.plan_lineage_query (filtros OTel, curadoria ASI06 e bloqueio de path traversal).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.plan_lineage_query.__main__ import main

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(args: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str, str]:
    code = main(args, repo_root=REPO_ROOT)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_cli_query_by_session_id(capsys: pytest.CaptureFixture[str]):
    code, out, _ = _run_cli(["--session-id", "sess-20261114-200000-r064-otel", "--strict"], capsys)
    assert code == 0
    data = json.loads(out)
    assert data["count"] >= 3
    paths = {p["plan_path"] for p in data["plans"]}
    assert "docs/plans/requirements/20261114-200000-r064-otel-correlation-critic-telemetry.md" in paths
    assert "docs/plans/architecture/20261114-200500-feature-r064-otel-correlation-critic-telemetry.md" in paths
    assert "docs/plans/governance/20261114-210000-governance-maintenance-otel-handoff-hydration.md" in paths


def test_cli_query_by_workflow_id(capsys: pytest.CaptureFixture[str]):
    code, out, _ = _run_cli(["--workflow-id", "WORKFLOW-FEATURE-DEVELOPMENT"], capsys)
    assert code == 0
    data = json.loads(out)
    assert data["count"] >= 2
    assert all(p["workflow_id"] == "WORKFLOW-FEATURE-DEVELOPMENT" for p in data["plans"])


def test_cli_query_by_workflow_trace_id_and_markdown_format(capsys: pytest.CaptureFixture[str]):
    code, out, _ = _run_cli(
        [
            "--workflow-trace-id",
            "wf-20261114-200000-feat-r064-otel-correlation",
            "--curation-candidates",
            "--format",
            "md",
        ],
        capsys,
    )
    assert code == 0
    assert "# Plan Lineage & Critic Telemetry Query (R-064 v2)" in out
    assert "requires_hitl: true" in out
    assert "wf-20261114-200000-feat-r064-otel-correlation" in out


def test_cli_query_by_author_and_curation_candidates(capsys: pytest.CaptureFixture[str]):
    code, out, _ = _run_cli(
        ["--author", "@tech-solution-architect", "--curation-candidates"],
        capsys,
    )
    assert code == 0
    data = json.loads(out)
    assert data["count"] >= 1
    candidates = data["curation_candidates"]
    assert len(candidates) >= 1
    for cand in candidates:
        assert cand["author"] == "@tech-solution-architect"
        assert cand["requires_hitl"] is True
        assert cand["occurrences"] >= 1
        assert "wf-20261114-200000-feat-r064-otel-correlation" in cand["workflow_trace_ids"]


def test_cli_blocks_path_traversal_with_exit_code_2(capsys: pytest.CaptureFixture[str]):
    code, _, err = _run_cli(["--root", "../outside-repo"], capsys)
    assert code == 2
    assert "path_confinement" in err
