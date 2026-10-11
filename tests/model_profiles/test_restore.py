"""CLI restore (R1): linha model: volta ao valor de HEAD; conflito; edicao de corpo preservada.
Contrato: ver tests/model_profiles/__init__.py."""
from __future__ import annotations

import json

import pytest

from ._helpers import (ECON_CHANGES, HAIKU, expected_bytes, git, head_bytes, protected_hashes,
                       read_state, record_writes, run_cli)

PY_DEV = ".github/agents/python-developer.agent.md"
ROUTER = ".github/agents/agent-router.agent.md"


@pytest.fixture
def applied(repo_applied):
    return repo_applied


def test_apply_mais_restore_deixa_git_limpo_e_bytes_identicos(applied, capsys, originals):
    repo = applied
    code, out = run_cli(capsys, repo, "restore")
    assert code == 0, out
    assert git(repo, "status", "--porcelain").strip() == ""
    for rel, data in originals.items():  # LF, CRLF e BOM
        assert (repo / rel).read_bytes() == data == head_bytes(repo, rel)
    assert read_state(repo)["phase"] == "restored"


def test_restore_so_escreve_nos_arquivos_alterados_pelo_apply(applied, capsys):
    with record_writes() as paths:
        run_cli(capsys, applied, "restore")
    assert {p.resolve().relative_to(applied.resolve()).as_posix() for p in paths} == set(ECON_CHANGES)


def test_restore_nunca_escreve_catalog_nem_routing_graph(repo, capsys):
    before = protected_hashes(repo)
    run_cli(capsys, repo, "apply", "economico", "--yes")
    run_cli(capsys, repo, "restore")
    assert protected_hashes(repo) == before


def test_edicao_de_corpo_sobrevive_ao_restore(applied, capsys, originals):
    repo = applied
    p = repo / PY_DEV
    p.write_bytes(p.read_bytes() + b"linha nova no corpo\r\n")
    code, out = run_cli(capsys, repo, "restore")
    assert code == 0, out
    assert (repo / PY_DEV).read_bytes() == originals[PY_DEV] + b"linha nova no corpo\r\n"
    assert git(repo, "diff", "-U0").count("\n+model:") == 0


def test_restore_usa_valor_do_head_e_nao_o_do_state(applied, capsys, originals):
    repo = applied
    st_path = repo / ".model-profiles/state.json"
    st = json.loads(st_path.read_text(encoding="utf-8"))
    for f in st["files"]:
        f["original_model"] = "Valor Adulterado"
    st_path.write_text(json.dumps(st), encoding="utf-8")
    assert run_cli(capsys, repo, "restore")[0] == 0
    assert (repo / ROUTER).read_bytes() == originals[ROUTER]


def test_linha_model_editada_apos_apply_e_conflito_e_nao_e_tocada(applied, capsys, originals):
    repo = applied
    p = repo / PY_DEV
    edited = p.read_bytes().replace(HAIKU.encode(), b"Grok 4.7")
    p.write_bytes(edited)
    code, out = run_cli(capsys, repo, "restore")
    assert code == 1 and "[CONFLICT]" in out and "python-developer" in out
    assert p.read_bytes() == edited  # intocado
    assert (repo / ROUTER).read_bytes() == originals[ROUTER]  # demais restaurados
    assert read_state(repo)["phase"] != "restored"


def test_force_line_resolve_conflito(applied, capsys, originals):
    repo = applied
    p = repo / PY_DEV
    p.write_bytes(p.read_bytes().replace(HAIKU.encode(), b"Grok 4.7"))
    code, out = run_cli(capsys, repo, "restore", "--force-line", "--yes")
    assert code == 0, out
    assert p.read_bytes() == originals[PY_DEV]
    assert read_state(repo)["phase"] == "restored"


def test_restore_sem_perfil_ativo_e_noop(repo, capsys, originals):
    code, out = run_cli(capsys, repo, "restore")
    assert code == 0
    assert all((repo / r).read_bytes() == b for r, b in originals.items())


def test_restore_repetido_e_idempotente(applied, capsys, originals):
    assert run_cli(capsys, applied, "restore")[0] == 0
    assert run_cli(capsys, applied, "restore")[0] == 0
    assert all((applied / r).read_bytes() == b for r, b in originals.items())


def test_restore_recusa_path_traversal_no_state(applied, capsys, tmp_path):
    outside = tmp_path / "outside.agent.md"
    outside.write_bytes(b'---\nmodel: "X"\n---\n')
    st_path = applied / ".model-profiles/state.json"
    st = json.loads(st_path.read_text(encoding="utf-8"))
    st["files"][0]["path"] = "../outside.agent.md"
    st_path.write_text(json.dumps(st), encoding="utf-8")
    code, out = run_cli(capsys, applied, "restore")
    assert code == 1 and "[PATH_TRAVERSAL]" in out
    assert outside.read_bytes() == b'---\nmodel: "X"\n---\n'


def test_apply_depois_de_restore_funciona_de_novo(applied, capsys, originals):
    run_cli(capsys, applied, "restore")
    code, out = run_cli(capsys, applied, "apply", "economico", "--yes")
    assert code == 0, out
    for rel, (old, new) in ECON_CHANGES.items():
        assert (applied / rel).read_bytes() == expected_bytes(originals[rel], old, new)
