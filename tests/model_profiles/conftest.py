"""Fixtures dos testes do gerador de perfis de modelos (tools/model_profiles).

Todos os testes operam em um repositorio git TEMPORARIO (tmp_path). Nada toca arquivos reais.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import time
import warnings
import os
from pathlib import Path

import pytest

from ._helpers import build_targets, fast_clone, make_repo

REAL_ROOT = Path(__file__).resolve().parents[2]
_REAL_GUARDED = (".github/agents/catalog.yaml", ".github/agents/routing-graph.yaml")


def _real_snapshot() -> dict:
    snap = {r: hashlib.sha256((REAL_ROOT / r).read_bytes()).hexdigest()
            for r in _REAL_GUARDED if (REAL_ROOT / r).exists()}
    snap["model-profiles-dir"] = (REAL_ROOT / ".model-profiles").exists()
    return snap


@pytest.fixture(scope="session", autouse=True)
def _real_repo_untouched():
    """Guarda: a suite nao pode alterar catalog/routing-graph reais nem criar .model-profiles real."""
    before = _real_snapshot()
    yield
    assert _real_snapshot() == before, "a suite tocou arquivos do repositorio REAL"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Orcamento leve (sem plugin): avisa (nao falha) se um teste passar de 3 s."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    if elapsed > 3.0:
        warnings.warn(f"{item.nodeid} excedeu o orcamento de 3 s ({elapsed:.1f} s)", stacklevel=1)
@pytest.fixture(scope="session", autouse=True)
def _isolated_git_env():
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("GIT_CONFIG_GLOBAL", os.devnull)
        mp.setenv("GIT_CONFIG_NOSYSTEM", "1")
        mp.setenv("GIT_TERMINAL_PROMPT", "0")
        yield


@pytest.fixture(scope="session")
def _template_repo(tmp_path_factory, _isolated_git_env) -> Path:
    """Repo git construido UMA vez por sessao (git e lento no Windows); cada teste copia."""
    return make_repo(tmp_path_factory.mktemp("tpl"))


@pytest.fixture(scope="session")
def _template_repo_no_ignore(tmp_path_factory, _isolated_git_env) -> Path:
    return make_repo(tmp_path_factory.mktemp("tpl_ni"), ignore_state_dir=False)


@pytest.fixture
def repo(tmp_path, _template_repo) -> Path:
    """Copia do repo git temporario com agents/prompts/catalog/routing-graph/allowlist/profiles."""
    r = fast_clone(_template_repo, tmp_path / "repo")
    assert tmp_path in r.parents
    return r


@pytest.fixture
def repo_no_ignore(tmp_path, _template_repo_no_ignore) -> Path:
    """Igual a `repo`, mas sem `.model-profiles/` no .gitignore (para `init`)."""
    return fast_clone(_template_repo_no_ignore, tmp_path / "repo")


@pytest.fixture(scope="session")
def _template_applied(tmp_path_factory, _template_repo) -> Path:
    """Repo com `apply economico` ja executado (1x por sessao; ~3 spawns git)."""
    from ._helpers import load
    r = fast_clone(_template_repo, tmp_path_factory.mktemp("tpl_applied") / "repo")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = load("cli").main(["--repo", str(r), "apply", "economico", "--yes"])
    assert code == 0, buf.getvalue()
    return r
@pytest.fixture
def repo_applied(tmp_path, _template_applied) -> Path:
    """Copia barata do repo apos `apply economico` (sem spawn de git)."""
    return fast_clone(_template_applied, tmp_path / "repo")
@pytest.fixture
def originals() -> dict[str, bytes]:
    """relpath -> bytes originais (HEAD) dos 6 alvos."""
    return {rel: data for rel, (_, data) in build_targets().items()}
