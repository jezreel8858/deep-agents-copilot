"""Lock exclusivo `.model-profiles/lock` (R4). Contrato: ver tests/model_profiles/__init__.py."""
from __future__ import annotations

import json
import os
import time

import pytest

from ._helpers import LOCK_REL, dead_pid, git, load, read_state, run_cli, write_lock


def test_lock_unitario_recusa_segundo_adquirente_e_libera_ao_sair(repo):
    lock = load("lock")
    with lock.exclusive_lock(repo):
        data = json.loads((repo / LOCK_REL).read_text(encoding="utf-8"))
        assert data["pid"] == os.getpid() and abs(data["timestamp"] - time.time()) < 60
        with pytest.raises(lock.LockError):
            with lock.exclusive_lock(repo):
                pass
    assert not (repo / LOCK_REL).exists()
    with lock.exclusive_lock(repo):  # reacquire apos liberar
        pass


def test_lock_liberado_mesmo_com_excecao(repo):
    lock = load("lock")
    with pytest.raises(RuntimeError):
        with lock.exclusive_lock(repo):
            raise RuntimeError("falha")
    assert not (repo / LOCK_REL).exists()


@pytest.mark.parametrize("args", [("apply", "economico", "--yes"), ("restore",),
                                  ("doctor", "--repair", "--yes")])
def test_instancia_simultanea_e_recusada(repo, capsys, originals, args):
    write_lock(repo, os.getpid(), time.time())  # PID vivo + recente
    code, out = run_cli(capsys, repo, *args)
    assert code == 1 and "[LOCKED]" in out
    assert all((repo / r).read_bytes() == b for r, b in originals.items())
    assert (repo / LOCK_REL).exists()  # lock alheio nao e removido


def test_lock_stale_por_pid_morto_e_retomado(repo, capsys):
    write_lock(repo, dead_pid(), time.time())
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 0, out
    assert read_state(repo)["phase"] == "applied"


def test_lock_stale_por_idade_e_retomado(repo, capsys):
    write_lock(repo, os.getpid(), time.time() - 10 * 86400)
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 0, out


def test_lock_e_liberado_apos_apply_e_restore(repo, capsys):
    run_cli(capsys, repo, "apply", "economico", "--yes")
    assert not (repo / LOCK_REL).exists()
    run_cli(capsys, repo, "restore")
    assert not (repo / LOCK_REL).exists()


def test_doctor_reporta_lock_stale_e_repair_remove(repo, capsys):
    write_lock(repo, dead_pid(), time.time())
    code, out = run_cli(capsys, repo, "doctor")
    assert "[STALE_LOCK]" in out
    code, out = run_cli(capsys, repo, "doctor", "--repair", "--yes")
    assert code == 0, out
    assert not (repo / LOCK_REL).exists()
