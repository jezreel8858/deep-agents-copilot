"""Hardening de seguranca do gerador de perfis (achados do security-reviewer).

BLOQUEADOR 1 (escrita com conteudo obsoleto), lock, symlinks, git hardening, schema do state,
confirmacoes e sanitizacao. Reusa fixtures/fast_clone de conftest/_helpers; repos temporarios.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from ._helpers import (HAIKU, LOCK_REL, STATE_REL, commit_all, dead_pid, load, read_state,
                       run_cli, sha256, write_lock)

PY_DEV = ".github/agents/python-developer.agent.md"
ROUTER = ".github/agents/agent-router.agent.md"


# ------------------------------------------------------- BLOQUEADOR 1: conteudo obsoleto

def test_atomic_write_recusa_quando_sha_diverge(tmp_path):
    writer = load("writer")
    f = tmp_path / "a.md"
    f.write_bytes(b"old")
    with pytest.raises(writer.WriteConflictError) as exc:
        writer.atomic_write(f, b"new", expected_sha=sha256(b"stale"))
    assert exc.value.code == "CONFLICT" and f.read_bytes() == b"old"
    assert not list(tmp_path.glob(".*.tmp"))
    writer.atomic_write(f, b"new", expected_sha=sha256(b"old"))
    assert f.read_bytes() == b"new"


def test_apply_recusa_se_alvo_muda_apos_o_planejamento(repo, capsys, originals, monkeypatch):
    p = repo / PY_DEV
    edited = p.read_bytes() + b"edicao concorrente\n"

    def fake_confirm(findings, assume_yes):
        p.write_bytes(edited)
        return True

    monkeypatch.setattr(load("summary"), "confirm", fake_confirm)
    code, out = run_cli(capsys, repo, "apply", "economico")
    assert code == 1 and "[CONFLICT]" in out
    assert p.read_bytes() == edited
    assert not (repo / STATE_REL).exists()
    assert all((repo / r).read_bytes() == b for r, b in originals.items() if r != PY_DEV)


def test_apply_conflito_no_meio_das_escritas_reverte_o_que_gravou(repo, capsys, originals,
                                                                  monkeypatch):
    writer = load("writer")
    real, seen = writer.atomic_write, {}

    def fake(path, data, *a, **k):
        seen["n"] = seen.get("n", 0) + 1
        if seen["n"] == 2:  # depois do pre-flight: simula edicao entre planejamento e escrita
            seen["rel"] = Path(path).resolve().relative_to(repo.resolve()).as_posix()
            Path(path).write_bytes(Path(path).read_bytes() + b"concorrente\n")
        return real(path, data, *a, **k)

    monkeypatch.setattr(writer, "atomic_write", fake)
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 1 and "alterado desde o planejamento" in out
    edited = repo / seen["rel"]
    assert edited.read_bytes() == originals[seen["rel"]] + b"concorrente\n"
    assert all((repo / r).read_bytes() == b for r, b in originals.items() if r != seen["rel"])


def test_restore_recusa_se_arquivo_muda_entre_leitura_e_escrita(repo_applied, capsys, originals,
                                                                monkeypatch):
    writer = load("writer")
    real, p = writer.atomic_write, repo_applied / PY_DEV
    mutated = {}

    def fake(path, data, *a, **k):
        if Path(path) == p:
            mutated["b"] = p.read_bytes() + b"concorrente\n"
            p.write_bytes(mutated["b"])
        return real(path, data, *a, **k)

    monkeypatch.setattr(writer, "atomic_write", fake)
    code, out = run_cli(capsys, repo_applied, "restore")
    assert code == 1 and "[CONFLICT]" in out
    assert p.read_bytes() == mutated["b"]
    assert (repo_applied / ROUTER).read_bytes() == originals[ROUTER]


# ------------------------------------------------------------------------------- lock

@pytest.mark.parametrize("payload", [
    {"pid": "abc", "timestamp": "x"}, {"pid": None, "timestamp": None},
    {"pid": True, "timestamp": 1}, {"pid": 10 ** 30, "timestamp": 1.0},
    {"pid": 1, "timestamp": float("nan")}, {"pid": [1], "timestamp": {}},
    {"timestamp": 1.0},
])
def test_is_stale_com_tipos_malformados_nao_levanta(repo, payload):
    lock = load("lock")
    path = repo / LOCK_REL
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert lock.is_stale(path) is True
    assert lock.lock_state(repo) == "stale"


def test_release_nao_remove_lock_de_outro_token(repo):
    lock = load("lock")
    with lock.exclusive_lock(repo):
        write_lock(repo, os.getpid(), time.time())  # mesmo pid, sem o token proprio
    assert (repo / LOCK_REL).exists()


def test_release_nao_remove_lock_ilegivel(repo):
    lock = load("lock")
    with lock.exclusive_lock(repo):
        (repo / LOCK_REL).write_text("{nao-json", encoding="utf-8")
    assert (repo / LOCK_REL).read_text(encoding="utf-8") == "{nao-json"


def test_reivindicacao_de_lock_stale_nao_deixa_residuo(repo):
    lock = load("lock")
    write_lock(repo, dead_pid(), time.time())
    with lock.exclusive_lock(repo):
        assert json.loads((repo / LOCK_REL).read_text(encoding="utf-8"))["pid"] == os.getpid()
    assert not list((repo / ".model-profiles").glob("lock*"))


def test_claim_stale_devolve_lock_vivo_que_substituiu_o_obsoleto(repo, monkeypatch):
    lock = load("lock")
    write_lock(repo, dead_pid(), time.time())
    lp, real, fired = repo / LOCK_REL, os.rename, []

    def fake(src, dst, *a, **k):
        if Path(src) == lp and not fired:  # outro processo vence a corrida antes do rename
            fired.append(1)
            lp.write_text(json.dumps({"pid": os.getpid(), "timestamp": time.time(),
                                      "token": "vivo"}), encoding="utf-8")
        return real(src, dst, *a, **k)

    monkeypatch.setattr(os, "rename", fake)
    with pytest.raises(lock.LockError):
        with lock.exclusive_lock(repo):
            pass
    assert json.loads(lp.read_text(encoding="utf-8"))["token"] == "vivo"
    assert not list(lp.parent.glob("lock.*"))


# ---------------------------------------------------------------------------- symlinks

def _symlink(target: Path, link: Path, directory: bool = False) -> None:
    try:
        os.symlink(target, link, target_is_directory=directory)
    except (OSError, NotImplementedError):
        pytest.skip("symlink indisponivel neste ambiente")


def test_alvo_symlink_de_arquivo_e_recusado(repo, capsys, tmp_path):
    p = repo / PY_DEV
    outside = tmp_path / "outside.agent.md"
    outside.write_bytes(p.read_bytes())
    p.unlink()
    _symlink(outside, p)
    before = outside.read_bytes()
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 1 and "[PATH_TRAVERSAL]" in out
    assert outside.read_bytes() == before


def test_componente_symlink_e_recusado_em_validate_state_path(repo, tmp_path):
    targets = load("targets")
    real_dir = tmp_path / "real_agents"
    (repo / ".github" / "agents").rename(real_dir)
    _symlink(real_dir, repo / ".github" / "agents", directory=True)
    with pytest.raises(targets.PathTraversalError):
        targets.validate_state_path(repo, PY_DEV)


def test_caminho_fora_de_agents_e_prompts_e_recusado(repo):
    targets = load("targets")
    with pytest.raises(targets.PathTraversalError):
        targets.ensure_confined(repo, repo / "model-profiles.yaml")


# ---------------------------------------------------------------------------------- git

def test_git_roda_com_fsmonitor_e_hooks_desativados(repo, monkeypatch):
    git = load("git")
    seen = []
    real = git.subprocess.run

    def spy(argv, *a, **k):
        seen.append(list(argv))
        return real(argv, *a, **k)

    monkeypatch.setattr(git.subprocess, "run", spy)
    git.text(repo, "rev-parse", "HEAD")
    git.show_heads(repo, [PY_DEV, ROUTER])
    assert len(seen) == 2
    for argv in seen:
        assert "core.fsmonitor=false" in argv and f"core.hooksPath={os.devnull}" in argv


def test_config_get_nao_sobrescreve_hooks_path(repo, monkeypatch):
    git = load("git")
    seen = []
    real = git.subprocess.run
    monkeypatch.setattr(git.subprocess, "run", lambda argv, *a, **k: (seen.append(argv),
                                                                      real(argv, *a, **k))[1])
    git.config_get(repo, "core.hooksPath")
    assert f"core.hooksPath={os.devnull}" not in seen[0]


def test_repo_que_nao_e_a_raiz_git_e_recusado_com_mensagem_clara(repo, capsys):
    code, out = run_cli(capsys, repo / ".github", "list")
    assert code == 1 and "[REPO]" in out and "raiz" in out


# ------------------------------------------------------------------------- sugestoes

def test_restore_avisa_quando_head_ja_contem_a_variante(repo_applied, capsys):
    commit_all(repo_applied, "commit acidental da variante")
    code, out = run_cli(capsys, repo_applied, "restore")
    assert "[HEAD_HAS_VARIANT]" in out


@pytest.mark.parametrize("mutate", [
    lambda s: s.update(files=["x"]),
    lambda s: s.update(files="nao-lista"),
    lambda s: s["files"][0].update(sha256_after="ZZ"),
    lambda s: s["files"][0].update(head_blob=123),
    lambda s: s["files"][0].pop("variant_model"),
    lambda s: s["files"][0].update(path=5),
])
def test_state_com_schema_de_entrada_invalido_recusa_restore(repo_applied, capsys, originals,
                                                             mutate):
    st = read_state(repo_applied)
    mutate(st)
    (repo_applied / STATE_REL).write_text(json.dumps(st), encoding="utf-8")
    code, out = run_cli(capsys, repo_applied, "restore")
    assert code == 1 and "[STATE_CORRUPT]" in out
    assert (repo_applied / ROUTER).read_bytes() != originals[ROUTER]  # nada foi tocado


def test_force_line_pede_confirmacao(repo_applied, capsys, originals, monkeypatch):
    p = repo_applied / PY_DEV
    edited = p.read_bytes().replace(HAIKU.encode(), b"Grok 4.7")
    p.write_bytes(edited)
    monkeypatch.setattr("builtins.input", lambda *a: "n")
    code, out = run_cli(capsys, repo_applied, "restore", "--force-line")
    assert code == 1 and "cancelada" in out and p.read_bytes() == edited
    monkeypatch.setattr("builtins.input", lambda *a: "s")
    code, out = run_cli(capsys, repo_applied, "restore", "--force-line")
    assert code == 0, out
    assert p.read_bytes() == originals[PY_DEV]


def test_doctor_repair_pede_confirmacao(repo, capsys, monkeypatch):
    write_lock(repo, dead_pid(), time.time())
    monkeypatch.setattr("builtins.input", lambda *a: "")
    code, out = run_cli(capsys, repo, "doctor", "--repair")
    assert code == 1 and "cancelada" in out and (repo / LOCK_REL).exists()
    monkeypatch.setattr("builtins.input", lambda *a: "sim")
    code, out = run_cli(capsys, repo, "doctor", "--repair")
    assert code == 0, out
    assert not (repo / LOCK_REL).exists()


def test_console_remove_ansi_e_controle(capsys):
    console = load("console")
    assert console.sanitize("a\x1b[31mb\x1b[0m\x07c\x9bd\te\nf") == "ab?c?d\te\nf"
    console.say("x\x1b[2Jy\r")
    console.fail("z\x1b]0;titulo\x07w")
    cap = capsys.readouterr()
    assert "\x1b" not in cap.out + cap.err and "xy?" in cap.out and "zw" in cap.err
