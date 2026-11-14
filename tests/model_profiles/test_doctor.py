"""doctor + journal write-ahead + recuperacao apos crash (R3/R7).
Contrato: ver tests/model_profiles/__init__.py."""
from __future__ import annotations

import pytest

from ._helpers import (ECON_CHANGES, LOCK_REL, SimulatedCrash, crash_after_writes, dead_pid,
                       git, protected_hashes, read_state, run_cli, write_lock)
import time


def _simulate_dead_process(repo):
    """Um kill real deixaria o lock com PID morto."""
    if (repo / LOCK_REL).exists():
        write_lock(repo, dead_pid(), time.time())


@pytest.mark.parametrize("writes_before_crash", [0, 1, 3])
def test_doctor_repair_restaura_apos_crash_no_meio_do_apply(repo, capsys, originals,
                                                            writes_before_crash):
    before = protected_hashes(repo)
    with crash_after_writes(writes_before_crash):
        with pytest.raises(SimulatedCrash):
            run_cli(capsys, repo, "apply", "economico", "--yes")
    _simulate_dead_process(repo)

    st = read_state(repo)  # journal write-ahead: lista completa gravada ANTES da 1a escrita
    assert st["phase"] == "pending"
    assert {f["path"] for f in st["files"]} == set(ECON_CHANGES)

    code, out = run_cli(capsys, repo, "status")
    assert code == 1 and "[ORPHAN_JOURNAL]" in out
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 1  # journal orfao bloqueia novo apply
    code, out = run_cli(capsys, repo, "doctor")
    assert code == 1 and "[ORPHAN_JOURNAL]" in out

    code, out = run_cli(capsys, repo, "doctor", "--repair", "--yes")
    assert code == 0, out
    for rel, data in originals.items():
        assert (repo / rel).read_bytes() == data, rel
    assert git(repo, "status", "--porcelain").strip() == ""
    assert read_state(repo)["phase"] == "restored"
    assert protected_hashes(repo) == before
    assert not (repo / LOCK_REL).exists()
    assert run_cli(capsys, repo, "doctor")[0] == 0


def test_repair_preserva_edicao_de_corpo_de_arquivo_parcialmente_aplicado(repo, capsys, originals):
    with crash_after_writes(1):
        with pytest.raises(SimulatedCrash):
            run_cli(capsys, repo, "apply", "economico", "--yes")
    _simulate_dead_process(repo)
    p = repo / ".github/agents/agent-router.agent.md"
    p.write_bytes(p.read_bytes() + b"nota\n")
    code, out = run_cli(capsys, repo, "doctor", "--repair", "--yes")
    assert code == 0, out
    assert p.read_bytes() == originals[".github/agents/agent-router.agent.md"] + b"nota\n"


def test_journal_phases_pending_applied_restored(repo, capsys):
    run_cli(capsys, repo, "apply", "economico", "--yes")
    assert read_state(repo)["phase"] == "applied"
    run_cli(capsys, repo, "restore")
    assert read_state(repo)["phase"] == "restored"


def test_doctor_em_repo_limpo_retorna_zero(repo, capsys):
    code, out = run_cli(capsys, repo, "doctor")
    assert code == 0, out


def test_doctor_detecta_skip_worktree_residual(repo, capsys):
    git(repo, "update-index", "--skip-worktree", ".github/agents/agent-router.agent.md")
    code, out = run_cli(capsys, repo, "doctor")
    assert code == 1 and "[SKIP_WORKTREE]" in out


def test_doctor_verifica_core_hooks_path(repo, capsys):
    code, out = run_cli(capsys, repo, "doctor")
    assert "[HOOKS_PATH]" in out
    (repo / ".githooks").mkdir()
    (repo / ".githooks/pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
    git(repo, "config", "core.hooksPath", ".githooks")
    code, out = run_cli(capsys, repo, "doctor")
    assert "[HOOKS_PATH]" not in out
