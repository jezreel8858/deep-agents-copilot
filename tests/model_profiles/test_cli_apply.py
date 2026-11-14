"""CLI apply/list/status/init: edicao so da linha model:, LF/CRLF/BOM, state.json, recusas, confirmacao.
Contrato: ver tests/model_profiles/__init__.py."""
from __future__ import annotations

import re

import pytest

from ._helpers import (BALANCEADO_CHANGES, ECON_CHANGES, ECON_UNCHANGED, ECON_WARNING, HAIKU,
                       expected_bytes, git, protected_hashes, read_state, record_writes, run_cli,
                       sha256)

STATE = ".model-profiles/state.json"


def _unchanged(repo, originals):
    return all((repo / r).read_bytes() == b for r, b in originals.items())


def test_apply_economico_edita_somente_linha_model_byte_a_byte(repo, capsys, originals):
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 0, out
    for rel, (old, new) in ECON_CHANGES.items():
        assert (repo / rel).read_bytes() == expected_bytes(originals[rel], old, new), rel
    for rel in ECON_UNCHANGED:
        assert (repo / rel).read_bytes() == originals[rel], rel


def test_apply_diff_git_contem_somente_linhas_model(repo, capsys):
    run_cli(capsys, repo, "apply", "economico", "--yes")
    diff = git(repo, "diff", "-U0")
    changed = [ln for ln in diff.splitlines()
               if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    assert changed and all(re.match(r"^[+-]model: ", ln) for ln in changed), changed
    assert len(changed) == 2 * len(ECON_CHANGES)


def test_apply_preserva_eol_e_bom_por_arquivo(repo, capsys, originals):
    run_cli(capsys, repo, "apply", "economico", "--yes")
    for rel, orig in originals.items():
        now = (repo / rel).read_bytes()
        assert now.count(b"\r\n") == orig.count(b"\r\n"), rel
        assert now.count(b"\n") == orig.count(b"\n"), rel
        assert now.startswith(b"\xef\xbb\xbf") == orig.startswith(b"\xef\xbb\xbf"), rel


def test_apply_nunca_escreve_catalog_nem_routing_graph(repo, capsys):
    before = protected_hashes(repo)
    with record_writes() as paths:
        code, _ = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 0
    assert protected_hashes(repo) == before
    written = {p.resolve().relative_to(repo.resolve()).as_posix() for p in paths}
    assert written == set(ECON_CHANGES)  # nenhuma escrita fora dos alvos que mudam


def test_apply_balanceado_so_toca_premium(repo, capsys, originals):
    code, _ = run_cli(capsys, repo, "apply", "balanceado", "--yes")
    assert code == 0
    for rel, orig in originals.items():
        if rel in BALANCEADO_CHANGES:
            old, new = BALANCEADO_CHANGES[rel]
            assert (repo / rel).read_bytes() == expected_bytes(orig, old, new)
        else:
            assert (repo / rel).read_bytes() == orig


def test_state_json_v1_com_hash_e_journal(repo, capsys, originals):
    run_cli(capsys, repo, "apply", "economico", "--yes")
    st = read_state(repo)
    assert st["schema_version"] == 1 and st["profile"] == "economico"
    assert st["phase"] == "applied"
    assert re.fullmatch(r"[0-9a-f]{64}", st["profile_hash"])
    assert st["head_commit"] == git(repo, "rev-parse", "HEAD").strip()
    assert st["applied_at"]
    files = {f["path"]: f for f in st["files"]}
    assert set(files) == set(ECON_CHANGES)  # so arquivos cujo modelo muda
    for rel, (old, new) in ECON_CHANGES.items():
        f = files[rel]
        assert f["original_model"] == old and f["variant_model"] == new
        assert f["eol"] == ("crlf" if b"\r\n" in originals[rel] else "lf")
        assert f["sha256_after"] == sha256((repo / rel).read_bytes())
        assert f["head_blob"] == git(repo, "rev-parse", f"HEAD:{rel}").strip()


def test_apply_deixa_state_fora_do_git_status(repo, capsys):
    run_cli(capsys, repo, "apply", "economico", "--yes")
    status = git(repo, "status", "--porcelain")
    assert ".model-profiles" not in status


def test_dry_run_so_mostra_resumo_aviso_e_nao_grava(repo, capsys, originals):
    code, out = run_cli(capsys, repo, "apply", "economico", "--dry-run")
    assert code == 0, out
    assert "economico" in out and HAIKU in out
    assert re.search(r"\b4\s+arquivos?", out)
    assert ECON_WARNING in out  # aviso de perda de qualidade
    assert "commit" in out.lower()  # aviso "nao commitar"
    assert _unchanged(repo, originals)
    assert not (repo / STATE).exists()


def test_sem_yes_pede_confirmacao_e_recusa_resposta_negativa(repo, capsys, monkeypatch, originals):
    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    code, out = run_cli(capsys, repo, "apply", "economico")
    assert code == 1 and ECON_WARNING in out
    assert _unchanged(repo, originals)


def test_sem_yes_e_sem_tty_recusa(repo, capsys, monkeypatch, originals):
    def eof(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", eof)
    code, _ = run_cli(capsys, repo, "apply", "economico")
    assert code == 1 and _unchanged(repo, originals)


@pytest.mark.parametrize("answer", ["s", "sim", "y", "yes"])
def test_confirmacao_afirmativa_aplica(repo, capsys, monkeypatch, answer):
    monkeypatch.setattr("builtins.input", lambda prompt="": answer)
    code, out = run_cli(capsys, repo, "apply", "economico")
    assert code == 0, out
    assert read_state(repo)["phase"] == "applied"


def test_yes_dispensa_input(repo, capsys, monkeypatch):
    def boom(prompt=""):
        raise AssertionError("input() nao deve ser chamado com --yes")

    monkeypatch.setattr("builtins.input", boom)
    assert run_cli(capsys, repo, "apply", "economico", "--yes")[0] == 0


def test_perfil_inexistente_e_recusado(repo, capsys, originals):
    code, out = run_cli(capsys, repo, "apply", "nao-existe", "--yes")
    assert code == 1 and _unchanged(repo, originals)


# ------------------------------------------------------------------ recusas R2
@pytest.mark.parametrize("how", ["worktree", "staged"])
@pytest.mark.parametrize("rel", [
    ".github/agents/python-developer.agent.md",  # sera alterado pelo perfil
    ".github/agents/docs-engineer.agent.md",  # alvo que o perfil NAO altera
])
def test_apply_recusa_alvo_sujo(repo, capsys, originals, how, rel):
    p = repo / rel
    p.write_bytes(p.read_bytes() + b"edicao local\n")
    if how == "staged":
        git(repo, "add", rel)
    snapshot = {r: (repo / r).read_bytes() for r in originals}
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 1 and "[DIRTY]" in out
    assert {r: (repo / r).read_bytes() for r in originals} == snapshot
    assert not (repo / STATE).exists()


def test_apply_ignora_arquivo_sujo_fora_dos_alvos(repo, capsys):
    (repo / "README.md").write_text("alterado\n", encoding="utf-8")
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 0, out


@pytest.mark.parametrize("kind,name", [
    ("file", "MERGE_HEAD"), ("file", "CHERRY_PICK_HEAD"), ("file", "REVERT_HEAD"),
    ("dir", "rebase-merge"), ("dir", "rebase-apply"),
])
def test_apply_recusa_merge_rebase_em_andamento(repo, capsys, originals, kind, name):
    target = repo / ".git" / name
    if kind == "file":
        target.write_text(git(repo, "rev-parse", "HEAD"), encoding="utf-8")
    else:
        target.mkdir()
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 1 and "[IN_PROGRESS]" in out
    assert _unchanged(repo, originals)


def test_segundo_apply_com_perfil_ativo_e_recusado(repo, capsys):
    assert run_cli(capsys, repo, "apply", "balanceado", "--yes")[0] == 0
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 1


# ------------------------------------------------------------------ list/status/init
def test_list_mostra_perfis_e_marca_ativo(repo, capsys):
    code, out = run_cli(capsys, repo, "list")
    assert code == 0 and all(n in out for n in ("default", "balanceado", "economico"))
    run_cli(capsys, repo, "apply", "economico", "--yes")
    _, out = run_cli(capsys, repo, "list")
    line = next(ln for ln in out.splitlines() if "economico" in ln)
    assert "*" in line or "ativo" in line.lower()


def test_status_sem_perfil_ativo_e_com_perfil_ativo(repo, capsys):
    code, out = run_cli(capsys, repo, "status")
    assert code == 0 and "default" in out
    run_cli(capsys, repo, "apply", "economico", "--yes")
    code, out = run_cli(capsys, repo, "status")
    assert code == 0 and "economico" in out and "applied" in out


def test_status_detecta_drift_da_linha_model(repo, capsys):
    run_cli(capsys, repo, "apply", "economico", "--yes")
    p = repo / ".github/agents/agent-router.agent.md"
    p.write_bytes(p.read_bytes().replace(HAIKU.encode(), b"Grok 4.7"))
    code, out = run_cli(capsys, repo, "status")
    assert code == 1 and "[DRIFT]" in out and "agent-router" in out


def test_cli_usa_git_toplevel_do_cwd_por_padrao(repo, capsys, monkeypatch):
    from ._helpers import load
    monkeypatch.chdir(repo)
    capsys.readouterr()
    assert load("cli").main(["status"]) == 0


def test_comando_desconhecido_retorna_uso_invalido(repo, capsys):
    code, _ = run_cli(capsys, repo, "explodir")
    assert code == 2


def test_init_cria_dir_e_ignora_via_info_exclude_idempotente(repo_no_ignore, capsys):
    repo = repo_no_ignore
    assert run_cli(capsys, repo, "init")[0] == 0
    assert (repo / ".model-profiles").is_dir()
    assert git(repo, "check-ignore", ".model-profiles/state.json", check=False).strip()
    assert run_cli(capsys, repo, "init")[0] == 0
    exclude = (repo / ".git/info/exclude").read_text(encoding="utf-8")
    assert exclude.count(".model-profiles") == 1
    assert git(repo, "status", "--porcelain").strip() == ""
