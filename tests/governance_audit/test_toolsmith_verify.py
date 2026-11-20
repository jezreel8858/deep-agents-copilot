"""Testes determinísticos do Pipeline Unificado Factory -> Eval -> Audit (tools/toolsmith_verify.py — P6)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tools.toolsmith_verify import PipelineStage, run_toolsmith_pipeline

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_toolsmith_pipeline_reports_pass_on_green_stages(tmp_path: Path) -> None:
    stages = (
        PipelineStage(
            id="step_ok_1",
            label="Step 1 OK",
            command=(sys.executable, "-c", "print('ok 1')"),
        ),
        PipelineStage(
            id="step_ok_2",
            label="Step 2 OK",
            command=(sys.executable, "-c", "print('ok 2')"),
        ),
    )
    report = run_toolsmith_pipeline(repo_root=tmp_path, stages=stages)
    assert report["passed"] is True
    assert report["verdict"] == "PASS"
    assert report["stages_executed"] == 2
    assert all(st["passed"] for st in report["stages"])


def test_toolsmith_pipeline_fail_fast_stops_on_first_failure(tmp_path: Path) -> None:
    stages = (
        PipelineStage(
            id="step_fail",
            label="Step Fail",
            command=(sys.executable, "-c", "import sys; sys.stderr.write('boom\\n'); sys.exit(1)"),
        ),
        PipelineStage(
            id="step_never_runs",
            label="Step Never Runs",
            command=(sys.executable, "-c", "print('should not run')"),
        ),
    )
    report = run_toolsmith_pipeline(repo_root=tmp_path, stages=stages, fail_fast=True)
    assert report["passed"] is False
    assert report["verdict"] == "FAIL"
    assert report["stages_executed"] == 1
    assert "boom" in report["stages"][0]["stderr_tail"]


def test_toolsmith_cli_json_help_and_module_entrypoint() -> None:
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, "-m", "tools.toolsmith_verify", "--help"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert proc.returncode == 0
    normalized_stdout = " ".join(proc.stdout.split())
    assert "--fail-fast" in normalized_stdout
    assert "--core" in normalized_stdout


def test_governance_contracts_reference_toolsmith_verify() -> None:
    factory_text = (REPO_ROOT / ".github" / "agents" / "governance-factory.agent.md").read_text(encoding="utf-8")
    maintainer_text = (REPO_ROOT / ".github" / "agents" / "governance-maintainer.agent.md").read_text(encoding="utf-8")
    workflows_text = (REPO_ROOT / ".github" / "agents" / "workflows.md").read_text(encoding="utf-8")

    assert "tools.toolsmith_verify" in factory_text
    assert "tools.toolsmith_verify" in maintainer_text
    assert "tools.toolsmith_verify" in workflows_text