"""CLI suspend/resume: HEAD temporario, reaplicacao apos pull, conflito, hash, lock."""
from __future__ import annotations

import json
import time

import pytest

from ._helpers import (HAIKU, ECON_CHANGES, add_profile, expected_bytes, git, head_bytes, read_state,
                       run_cli, write_lock)

PY_DEV = ".github/agents/python-developer.agent.md"
ROUTER = ".github/agents/agent-router.agent.md"


@pytest.fixture
def applied(repo_applied):
    return repo_applied


def test_suspend_deixa_git_limpo_e_grava_phase_suspended(applied, capsys, originals):
    code, out = run_cli(capsys, applied, "suspend", "--yes")
    assert code == 0, out
    assert git(applied, "status", "--porcelain").strip() == ""
    for rel, data in originals.items():
        assert (applied / rel).read_bytes() == data
    st = read_state(applied)
    assert st["phase"] == "suspended" and st["profile"] == "economico" and st["profile_hash"]


def test_status_e_doctor_sem_falso_drift_quando_suspenso(applied, capsys):
    run_cli(capsys, applied, "suspend", "--yes")
    code, out = run_cli(capsys, applied, "status")
    assert code == 0 and "suspended" in out and "[DRIFT]" not in out
    code, out = run_cli(capsys, applied, "doctor")
    assert "[DRIFT]" not in out and "[SUSPENDED]" in out


def test_resume_reaplica_apos_pull_em_arquivo_nao_relacionado(applied, capsys):
    run_cli(capsys, applied, "suspend", "--yes")
    (applied / "README.md").write_text("pull simulado\n", encoding="utf-8")
    git(applied, "commit", "-qam", "pull simulado")
    code, out = run_cli(capsys, applied, "resume", "--yes")
    assert code == 0, out
    for rel, (old, new) in ECON_CHANGES.items():
        assert (applied / rel).read_bytes() == expected_bytes(head_bytes(applied, rel), old, new)
    assert read_state(applied)["phase"] == "applied"
    assert run_cli(capsys, applied, "restore")[0] == 0
    assert git(applied, "status", "--porcelain").strip() == ""


def test_resume_recusa_alvo_sujo(applied, capsys):
    run_cli(capsys, applied, "suspend", "--yes")
    p = applied / PY_DEV
    p.write_bytes(p.read_bytes() + b"edicao local\r\n")
    code, out = run_cli(capsys, applied, "resume", "--yes")
    assert code == 1 and "[DIRTY]" in out
    assert read_state(applied)["phase"] == "suspended"


def test_resume_recusa_merge_em_andamento(applied, capsys):
    run_cli(capsys, applied, "suspend", "--yes")
    (applied / ".git" / "MERGE_HEAD").write_text("0" * 40 + "\n", encoding="utf-8")
    code, out = run_cli(capsys, applied, "resume", "--yes")
    assert code == 1 and "[IN_PROGRESS]" in out


def test_conflito_de_linha_no_suspend_nao_muda_phase(applied, capsys):
    p = applied / PY_DEV
    edited = p.read_bytes().replace(HAIKU.encode(), b"Grok 4.7")
    p.write_bytes(edited)
    code, out = run_cli(capsys, applied, "suspend", "--yes")
    assert code == 1 and "[CONFLICT]" in out
    assert p.read_bytes() == edited
    assert read_state(applied)["phase"] == "applied"


def test_resume_com_perfil_alterado_recusa_sem_force_e_aceita_com_force(applied, capsys):
    run_cli(capsys, applied, "suspend", "--yes")
    path = applied / "model-profiles.yaml"
    path.write_bytes(path.read_bytes().replace(b"orchestration: " + HAIKU.encode(),
                                               b"orchestration: Gemini 3.8 Flash"))
    git(applied, "commit", "-qam", "perfil mudou")
    code, out = run_cli(capsys, applied, "resume", "--yes")
    assert code == 1 and "[PROFILE_CHANGED]" in out and "--force" in out
    assert read_state(applied)["phase"] == "suspended"
    code, out = run_cli(capsys, applied, "resume", "--force", "--yes")
    assert code == 0, out
    assert read_state(applied)["phase"] == "applied"


def test_suspend_sem_perfil_ativo(repo, capsys):
    code, out = run_cli(capsys, repo, "suspend", "--yes")
    assert code == 1 and "[NO_ACTIVE_PROFILE]" in out


def test_suspend_duas_vezes_e_resume_sem_suspensao(applied, capsys):
    code, out = run_cli(capsys, applied, "resume", "--yes")
    assert code == 1 and "[NOT_SUSPENDED]" in out
    run_cli(capsys, applied, "suspend", "--yes")
    code, out = run_cli(capsys, applied, "suspend", "--yes")
    assert code == 1 and "[SUSPENDED]" in out


def test_apply_recusa_enquanto_suspenso(applied, capsys):
    run_cli(capsys, applied, "suspend", "--yes")
    code, out = run_cli(capsys, applied, "apply", "balanceado", "--yes")
    assert code == 1 and "[SUSPENDED]" in out


def test_restore_descarta_perfil_suspenso(applied, capsys):
    run_cli(capsys, applied, "suspend", "--yes")
    assert run_cli(capsys, applied, "restore")[0] == 0
    assert read_state(applied)["phase"] == "restored"


def test_lock_vivo_bloqueia_suspend_e_resume(applied, capsys):
    import os
    write_lock(applied, os.getpid(), time.time())
    code, out = run_cli(capsys, applied, "suspend", "--yes")
    assert code == 1 and "[LOCKED]" in out
    (applied / ".model-profiles" / "lock").unlink()
    run_cli(capsys, applied, "suspend", "--yes")
    write_lock(applied, os.getpid(), time.time())
    code, out = run_cli(capsys, applied, "resume", "--yes")
    assert code == 1 and "[LOCKED]" in out
    assert json.loads((applied / ".model-profiles/state.json").read_text("utf-8"))["phase"] == "suspended"


def test_suspend_sem_yes_nao_interativo_cancela(applied, capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda *_: "n")
    code, out = run_cli(capsys, applied, "suspend")
    assert code == 1 and read_state(applied)["phase"] == "applied"
