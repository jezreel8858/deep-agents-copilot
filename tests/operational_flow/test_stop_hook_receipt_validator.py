"""Testes determinísticos do Stop-Hook Mecânico de Validação de Receipt, Escopo e Audit Log JSONL (P1/P2/P4/P7 — R-064 / R-068)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
import pytest

from tools.audit_log_query import harvest_lesson_candidates, load_audit_entries, summarize_entries

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / "tools" / "hooks" / "validate_step_receipt.js"
HOOKS_CONFIG = REPO_ROOT / ".github" / "hooks" / "context-mode.json"

NODE_AVAILABLE = shutil.which("node") is not None


def _init_temp_git_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test Runner"], cwd=tmp_path, check=True)

    plan_dir = tmp_path / "docs" / "plans" / "implementation"
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plan_dir / "20261120-020000-feature-demo.md"
    plan_file.write_text(
        "---\n"
        'title: "Plano Demo"\n'
        'status: "APPROVED"\n'
        "approved: true\n"
        "allowed_files:\n"
        '  - "src/service/PedidoService.java"\n'
        '  - "src/dto/*"\n'
        "---\n\n# Plano Demo\n",
        encoding="utf-8",
    )

    src_dir = tmp_path / "src" / "service"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "PedidoService.java").write_text("class PedidoService {}\n", encoding="utf-8")
    (src_dir / "OutroService.java").write_text("class OutroService {}\n", encoding="utf-8")

    dto_dir = tmp_path / "src" / "dto"
    dto_dir.mkdir(parents=True, exist_ok=True)
    (dto_dir / "PedidoDto.java").write_text("class PedidoDto {}\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "chore: baseline"], cwd=tmp_path, check=True)
    return tmp_path


def _run_hook(cwd: Path, payload: dict) -> tuple[int, dict]:
    proc = subprocess.run(
        ["node", str(HOOK_SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=cwd,
        timeout=10,
    )
    return proc.returncode, json.loads(proc.stdout.strip())


def test_hooks_json_registers_stop_and_subagent_stop() -> None:
    assert HOOK_SCRIPT.exists(), "tools/hooks/validate_step_receipt.js não encontrado"
    cfg = json.loads(HOOKS_CONFIG.read_text(encoding="utf-8"))
    hooks = cfg["hooks"]
    for event_name in ("subagentStop", "SubagentStop", "stop", "Stop"):
        assert event_name in hooks, f"Evento '{event_name}' ausente em .github/hooks/context-mode.json"
        assert any("validate_step_receipt.js" in entry.get("bash", "") for entry in hooks[event_name])


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js não disponível no ambiente")
def test_readonly_turn_without_mutations_approves(tmp_path: Path) -> None:
    repo = _init_temp_git_repo(tmp_path)
    code, out = _run_hook(
        repo,
        {
            "cwd": str(repo),
            "last_assistant_message": "Agente Ativo: agent-router\nTriagem concluída.",
        },
    )
    assert code == 0
    assert out["decision"] == "approve"


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js não disponível no ambiente")
def test_mutation_without_receipt_is_blocked(tmp_path: Path) -> None:
    repo = _init_temp_git_repo(tmp_path)
    (repo / "src" / "service" / "PedidoService.java").write_text("class PedidoService { int x = 1; }\n", encoding="utf-8")

    code, out = _run_hook(
        repo,
        {
            "cwd": str(repo),
            "workflow_trace_id": "wf-trace-audit-01",
            "last_assistant_message": "Agente Ativo: spring-boot-developer\nImplementação concluída com sucesso!",
        },
    )
    assert code == 2
    assert out["decision"] == "block"
    assert "RECEIPT_VALIDATION_FAILED" in out["reason"]

    entries = load_audit_entries(repo / ".context" / "audit", workflow_trace_id="wf-trace-audit-01")
    assert len(entries) == 1
    assert entries[0]["decision"] == "block"
    assert entries[0]["agent"] == "@spring-boot-developer"


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js não disponível no ambiente")
def test_valid_receipt_within_allowed_files_approves_and_appends_jsonl(tmp_path: Path) -> None:
    repo = _init_temp_git_repo(tmp_path)
    (repo / "src" / "service" / "PedidoService.java").write_text("class PedidoService { int x = 2; }\n", encoding="utf-8")

    msg = """Agente Ativo: spring-boot-developer

```yaml
receipt:
  receipt_id: "rcpt-001"
  n: 1
  agent: "@spring-boot-developer"
  banner_ref: "spring-boot-developer"
  handoff_seq: 1
  artefato: "src/service/PedidoService.java"
  plan_ref: "docs/plans/implementation/20261120-020000-feature-demo.md"
  gate_resolucao: "none"
  verdict_from_agent: "IMPLEMENTED"
  status: "done"
  step_delta:
    mode: "mutation"
    task_id: "T-01"
    target_files:
      - "src/service/PedidoService.java"
    verification_command_output: "mvn test -Dtest=PedidoServiceTest -> EXIT 0 (1/1 passed)"
    files_modified:
      - path: "src/service/PedidoService.java"
        summary: "Adicionado campo x"
    files_created: []
    exports_and_signatures:
      - "int x"
    plan_conformance:
      within_allowed_files: true
      out_of_scope_files: []
    overflow_ref: "N/A"
    notes_for_next_step: "Cobrir campo x nos testes unitários"
```
"""
    code, out = _run_hook(
        repo,
        {
            "cwd": str(repo),
            "session_id": "sess-999",
            "workflow_trace_id": "wf-trace-audit-02",
            "last_assistant_message": msg,
        },
    )
    assert code == 0
    assert out["decision"] == "approve"

    entries = load_audit_entries(repo / ".context" / "audit", workflow_trace_id="wf-trace-audit-02")
    assert len(entries) == 1
    assert entries[0]["session_id"] == "sess-999"
    assert entries[0]["task_id"] == "T-01"
    assert entries[0]["within_allowed_files"] is True
    assert entries[0]["files_touched_count"] == 1


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js não disponível no ambiente")
def test_out_of_scope_git_mutation_triggers_plan_drift_block(tmp_path: Path) -> None:
    repo = _init_temp_git_repo(tmp_path)
    (repo / "src" / "service" / "OutroService.java").write_text("class OutroService { int hack = 1; }\n", encoding="utf-8")

    msg = """Agente Ativo: spring-boot-developer

```yaml
receipt:
  receipt_id: "rcpt-002"
  n: 1
  agent: "@spring-boot-developer"
  banner_ref: "spring-boot-developer"
  handoff_seq: 1
  artefato: "src/service/PedidoService.java"
  plan_ref: "docs/plans/implementation/20261120-020000-feature-demo.md"
  gate_resolucao: "none"
  verdict_from_agent: "IMPLEMENTED"
  status: "done"
  step_delta:
    mode: "mutation"
    files_modified:
      - path: "src/service/PedidoService.java"
        summary: "Alteração declarada"
    files_created: []
    exports_and_signatures: []
    plan_conformance:
      within_allowed_files: true
      out_of_scope_files: []
    overflow_ref: "N/A"
    notes_for_next_step: "Seguir para testes"
```
"""
    code, out = _run_hook(
        repo,
        {
            "cwd": str(repo),
            "workflow_trace_id": "wf-trace-audit-03",
            "last_assistant_message": msg,
        },
    )
    assert code == 2
    assert out["decision"] == "block"
    assert out["drift_detected"] is True
    assert "PLAN_DRIFT_DETECTED" in out["reason"]
    assert "src/service/OutroService.java" in out["reason"]

    stats = summarize_entries(load_audit_entries(repo / ".context" / "audit"))
    assert stats["drift_count"] == 1
    assert stats["failures_count"] == 1


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js não disponível no ambiente")
def test_micro_task_target_files_violation_is_blocked(tmp_path: Path) -> None:
    repo = _init_temp_git_repo(tmp_path)
    (repo / "src" / "dto" / "PedidoDto.java").write_text("class PedidoDto { int z = 1; }\n", encoding="utf-8")

    msg = """```yaml
receipt:
  receipt_id: "rcpt-004"
  n: 1
  agent: "@spring-boot-developer"
  banner_ref: "spring-boot-developer"
  handoff_seq: 1
  artefato: "src/service/PedidoService.java"
  plan_ref: "docs/plans/implementation/20261120-020000-feature-demo.md"
  gate_resolucao: "none"
  verdict_from_agent: "IMPLEMENTED"
  status: "done"
  step_delta:
    mode: "mutation"
    task_id: "T-01"
    target_files:
      - "src/service/PedidoService.java"
    verification_command_output: "mvn test -Dtest=PedidoServiceTest -> EXIT 0"
    files_modified:
      - path: "src/dto/PedidoDto.java"
        summary: "Alterou DTO fora do escopo da micro-tarefa T-01"
    files_created: []
    exports_and_signatures: []
    plan_conformance:
      within_allowed_files: true
      out_of_scope_files: []
    overflow_ref: "N/A"
    notes_for_next_step: "N/A"
```"""
    code, out = _run_hook(repo, {"cwd": str(repo), "last_assistant_message": msg})
    assert code == 2
    assert out["decision"] == "block"
    assert "micro_task_scope_violation" in out["reason"]
    assert "T-01" in out["reason"]


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js não disponível no ambiente")
def test_micro_task_valid_target_files_subset_approves(tmp_path: Path) -> None:
    repo = _init_temp_git_repo(tmp_path)
    (repo / "src" / "dto" / "PedidoDto.java").write_text("class PedidoDto { int ok = 1; }\n", encoding="utf-8")

    msg = """```yaml
receipt:
  receipt_id: "rcpt-005"
  n: 2
  agent: "@spring-boot-developer"
  banner_ref: "spring-boot-developer"
  handoff_seq: 2
  artefato: "src/dto/PedidoDto.java"
  plan_ref: "docs/plans/implementation/20261120-020000-feature-demo.md"
  gate_resolucao: "none"
  verdict_from_agent: "IMPLEMENTED"
  status: "done"
  step_delta:
    mode: "mutation"
    task_id: "T-02"
    target_files:
      - "src/dto/*"
    verification_command_output: "mvn test -Dtest=PedidoDtoTest -> EXIT 0 (2/2 passed)"
    files_modified:
      - path: "src/dto/PedidoDto.java"
        summary: "Adicionado campo ok dentro de target_files da T-02"
    files_created: []
    exports_and_signatures:
      - "int ok"
    plan_conformance:
      within_allowed_files: true
      out_of_scope_files: []
    overflow_ref: "N/A"
    notes_for_next_step: "Micro-tarefa T-02 concluída"
```"""
    code, out = _run_hook(repo, {"cwd": str(repo), "last_assistant_message": msg})
    assert code == 0
    assert out["decision"] == "approve"


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js não disponível no ambiente")
def test_draft_plan_execution_is_blocked(tmp_path: Path) -> None:
    repo = _init_temp_git_repo(tmp_path)
    plan_file = repo / "docs" / "plans" / "implementation" / "20261120-020000-feature-demo.md"
    plan_file.write_text(
        plan_file.read_text(encoding="utf-8").replace('status: "APPROVED"', 'status: "DRAFT"'),
        encoding="utf-8",
    )
    (repo / "src" / "service" / "PedidoService.java").write_text("class PedidoService { int y = 1; }\n", encoding="utf-8")

    msg = """```yaml
receipt:
  receipt_id: "rcpt-003"
  n: 1
  agent: "@spring-boot-developer"
  banner_ref: "spring-boot-developer"
  handoff_seq: 1
  artefato: "src/service/PedidoService.java"
  plan_ref: "docs/plans/implementation/20261120-020000-feature-demo.md"
  gate_resolucao: "none"
  verdict_from_agent: "IMPLEMENTED"
  status: "done"
  step_delta:
    mode: "mutation"
    files_modified:
      - path: "src/service/PedidoService.java"
        summary: "Alterado antes da aprovação"
    files_created: []
    exports_and_signatures: []
    plan_conformance:
      within_allowed_files: true
      out_of_scope_files: []
    overflow_ref: "N/A"
    notes_for_next_step: "N/A"
```"""
    code, out = _run_hook(repo, {"cwd": str(repo), "last_assistant_message": msg})
    assert code == 2
    assert out["decision"] == "block"
    assert "DRAFT" in out["reason"]


def test_audit_log_harvest_lessons_groups_recurring_failures(tmp_path: Path) -> None:
    audit_dir = tmp_path / ".context" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    jsonl_file = audit_dir / "wf-trace-harvest.jsonl"
    events = [
        {
            "timestamp": "2026-11-20T12:00:00Z",
            "event": "subagentstop",
            "session_id": "s1",
            "workflow_trace_id": "wf-trace-harvest",
            "agent": "@spring-boot-developer",
            "status": "blocked",
            "plan_ref": "docs/plans/implementation/20261120-020000-feature-demo.md",
            "decision": "block",
            "drift_detected": True,
            "errors": ["R-064 (plan_drift_detected): Mutação detectada fora de allowed_files"],
        },
        {
            "timestamp": "2026-11-20T12:01:00Z",
            "event": "subagentstop",
            "session_id": "s2",
            "workflow_trace_id": "wf-trace-harvest",
            "agent": "@spring-boot-developer",
            "status": "blocked",
            "plan_ref": "docs/plans/implementation/20261120-020000-feature-demo.md",
            "decision": "block",
            "drift_detected": True,
            "errors": ["R-064 (plan_drift_detected): Mutação detectada fora de allowed_files"],
        },
    ]
    jsonl_file.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")

    harvested = harvest_lesson_candidates(load_audit_entries(audit_dir))
    assert harvested["total_failures_analyzed"] == 2
    assert harvested["candidates_count"] == 1
    candidate = harvested["candidates"][0]
    assert candidate["agent"] == "@spring-boot-developer"
    assert candidate["rule_code"] == "R-064:plan_drift"
    assert candidate["occurrences"] == 2
    assert "planner-preflight-checklist.md" in candidate["suggested_hardening_target"]