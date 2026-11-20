"""Pipeline Unificado Factory -> Eval -> Audit (Toolsmith CLI — P5/P6/P8).

Encadeia em uma única execução determinística:
1. Sync & Paridade de Protocolo (`python -m tools.agent_protocol_sync --check`)
2. Sync & Paridade de Catálogos (`python -m tools.governance_sync --check`)
3. Audit Estrutural & Orçamento R-066 (`pytest tests/governance_audit/ -q`)
4. Evals de Roteamento & Fluxo Operacional (`pytest tests/operational_flow/ -q`)

Modo `--core`: executa verificação rápida de paridade de catálogo + guardas
determinísticos de P1–P8 (Stop-Hook, Plan-Drift, Audit/Harvest, Skill A/B Eval,
Toolsmith CLI e Exportador Multi-Runtime).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PipelineStage:
    id: str
    label: str
    command: tuple[str, ...]
    optional: bool = False


DEFAULT_STAGES: tuple[PipelineStage, ...] = (
    PipelineStage(
        id="protocol_sync",
        label="Protocol Sync Check (R-015 / R-040)",
        command=(sys.executable, "-m", "tools.agent_protocol_sync", "--check"),
    ),
    PipelineStage(
        id="governance_sync",
        label="Catalog & Index Parity Check (R-015)",
        command=(sys.executable, "-m", "tools.governance_sync", "--check"),
    ),
    PipelineStage(
        id="governance_audit",
        label="Governance Audit & Budget R-066 (pytest)",
        command=(sys.executable, "-m", "pytest", "tests/governance_audit/", "-q"),
    ),
    PipelineStage(
        id="operational_evals",
        label="Operational Flow & Stop-Hook Evals (pytest)",
        command=(sys.executable, "-m", "pytest", "tests/operational_flow/", "-q"),
    ),
)

CORE_STAGES: tuple[PipelineStage, ...] = (
    PipelineStage(
        id="governance_sync",
        label="Catalog & Index Parity Check (R-015)",
        command=(sys.executable, "-m", "tools.governance_sync", "--check"),
    ),
    PipelineStage(
        id="core_guards",
        label="Toolsmith, Bundles, Skill A/B & Stop-Hook Guards (pytest)",
        command=(
            sys.executable,
            "-m",
            "pytest",
            "tests/governance_audit/test_toolsmith_verify.py",
            "tests/governance_audit/test_export_bundle.py",
            "tests/operational_flow/test_stop_hook_receipt_validator.py",
            "tests/evals/test_skill_ab_eval.py",
            "-q",
        ),
    ),
)


@dataclass
class StageResult:
    id: str
    label: str
    command: list[str]
    returncode: int
    passed: bool
    duration_ms: int
    stdout_tail: str
    stderr_tail: str


def _tail(text: str, max_lines: int = 20) -> str:
    lines = [line for line in (text or "").splitlines() if line.strip()]
    return "\n".join(lines[-max_lines:])


def run_toolsmith_pipeline(
    repo_root: Path = REPO_ROOT,
    stages: Sequence[PipelineStage] = DEFAULT_STAGES,
    fail_fast: bool = False,
) -> dict:
    """Executa todas as etapas do pipeline Toolsmith e retorna relatório estruturado."""
    results: list[StageResult] = []
    overall_passed = True
    child_env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}

    for stage in stages:
        start = time.perf_counter()
        proc = subprocess.run(
            list(stage.command),
            cwd=repo_root,
            env=child_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        passed = proc.returncode == 0
        if not passed and not stage.optional:
            overall_passed = False

        results.append(
            StageResult(
                id=stage.id,
                label=stage.label,
                command=list(stage.command),
                returncode=proc.returncode,
                passed=passed,
                duration_ms=elapsed_ms,
                stdout_tail=_tail(proc.stdout),
                stderr_tail=_tail(proc.stderr),
            )
        )

        if not passed and fail_fast:
            break

    return {
        "verdict": "PASS" if overall_passed else "FAIL",
        "passed": overall_passed,
        "stages_executed": len(results),
        "stages_total": len(stages),
        "stages": [asdict(r) for r in results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline Unificado Factory -> Eval -> Audit (Toolsmith CLI - P5/P6/P8)."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Raiz do repositorio de governanca.",
    )
    parser.add_argument(
        "--core",
        action="store_true",
        help="Executa apenas o nucleo rapido (Catalog Sync + Guardas P1-P8).",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Interrompe imediatamente na primeira etapa com falha.",
    )
    parser.add_argument(
        "--skip-evals",
        action="store_true",
        help="Executa apenas Sync + Audit (modo rapido pre-commit).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emite saida estritamente em JSON estruturado.",
    )
    args = parser.parse_args(argv)

    base_stages = CORE_STAGES if args.core else DEFAULT_STAGES
    selected_stages = tuple(
        s for s in base_stages if not (args.skip_evals and s.id == "operational_evals")
    )
    report = run_toolsmith_pipeline(
        repo_root=args.repo_root.resolve(),
        stages=selected_stages,
        fail_fast=args.fail_fast,
    )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Toolsmith Verify Verdict: {report['verdict']} ({report['stages_executed']}/{report['stages_total']} etapas)")
        for st in report["stages"]:
            icon = "PASS" if st["passed"] else "FAIL"
            print(f"  [{icon}] {st['label']} ({st['duration_ms']} ms)")
            if not st["passed"]:
                detail = st["stderr_tail"] or st["stdout_tail"]
                if detail:
                    for line in detail.splitlines():
                        print(f"         {line}")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())