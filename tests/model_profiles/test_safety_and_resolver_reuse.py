"""Path traversal e reuso do resolver.py (sem logica duplicada).
Contrato: ver tests/model_profiles/__init__.py."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest
import yaml

from ._helpers import commit_all, load, protected_hashes, run_cli

RESOLVER_API = {"get_canonical_key", "get_tier_for_key", "normalize_model_name",
                "validate_profile_keys", "resolve_profile", "resolve_target_model"}
PKG = Path(__file__).resolve().parents[2] / "tools" / "model_profiles"
OUTSIDE_BYTES = b'---\nname: out\nmodel: "Claude Sonnet 5.5"\n---\ncorpo\n'


@pytest.mark.parametrize("key", [
    "../../../outside",
    "..\\..\\..\\outside",
    "templates/../../../../outside",
    "ABSOLUTE",
])
def test_path_traversal_em_tier_map_e_rejeitado(repo, capsys, tmp_path, originals, key):
    outside = tmp_path / "outside.agent.md"  # fora do repo
    outside.write_bytes(OUTSIDE_BYTES)
    if key == "ABSOLUTE":
        key = (tmp_path / "outside").as_posix()
    cfg = repo / "model-profiles.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["tier_map"]["light"].append(key)
    cfg.write_bytes(yaml.safe_dump(data, sort_keys=False).encode("utf-8"))
    commit_all(repo, "chave maliciosa")
    before = protected_hashes(repo)
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 1 and "[PATH_TRAVERSAL]" in out
    assert outside.read_bytes() == OUTSIDE_BYTES
    assert all((repo / r).read_bytes() == b for r, b in originals.items())
    assert protected_hashes(repo) == before


def test_perfil_com_nome_de_caminho_e_recusado(repo, capsys, originals):
    code, _ = run_cli(capsys, repo, "apply", "../../etc/passwd", "--yes")
    assert code == 1
    assert all((repo / r).read_bytes() == b for r, b in originals.items())


def test_modulos_nao_redefinem_funcoes_do_resolver():
    modules = [p for p in PKG.glob("*.py") if p.name not in {"resolver.py", "__init__.py"}]
    assert {p.name for p in modules} >= {"cli.py", "apply.py", "restore.py", "state.py",
                                         "lock.py", "doctor.py", "writer.py"}
    for p in modules:
        tree = ast.parse(p.read_text(encoding="utf-8"))
        defined = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef,
                                                                     ast.AsyncFunctionDef))}
        assert not (defined & RESOLVER_API), f"{p.name} duplica {defined & RESOLVER_API}"


def test_apply_importa_o_resolver():
    tree = ast.parse((PKG / "apply.py").read_text(encoding="utf-8"))
    imported = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            imported.add(n.module or "")
            imported.update(f"{n.module}.{a.name}" for a in n.names)
        elif isinstance(n, ast.Import):
            imported.update(a.name for a in n.names)
    assert any(i.endswith("model_profiles.resolver") or i == "tools.model_profiles.resolver"
               for i in imported), imported


def test_apply_delega_ao_resolver_em_runtime(repo, capsys, monkeypatch):
    resolver = load("resolver")
    calls = {"profile": 0, "target": 0, "key": 0}
    real = (resolver.resolve_profile, resolver.resolve_target_model, resolver.get_canonical_key)

    def spy_profile(*a, **k):
        calls["profile"] += 1
        return real[0](*a, **k)

    def spy_target(*a, **k):
        calls["target"] += 1
        return real[1](*a, **k)

    def spy_key(*a, **k):
        calls["key"] += 1
        return real[2](*a, **k)

    monkeypatch.setattr(resolver, "resolve_profile", spy_profile)
    monkeypatch.setattr(resolver, "resolve_target_model", spy_target)
    monkeypatch.setattr(resolver, "get_canonical_key", spy_key)
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 0, out
    assert calls["profile"] >= 1 and calls["target"] >= 6 and calls["key"] >= 6


def test_resolucao_hierarquica_do_resolver_reflete_no_apply(repo, capsys):
    """economico herda premium(balanceado)=Sonnet e light(default)=Flash via extends do resolver."""
    from ._helpers import FLASH, SONNET
    assert run_cli(capsys, repo, "apply", "economico", "--yes")[0] == 0
    tsa = (repo / ".github/agents/tech-solution-architect.agent.md").read_bytes()
    docs = (repo / ".github/agents/docs-engineer.agent.md").read_bytes()
    assert f'model: "{SONNET}"'.encode() in tsa and f'model: "{FLASH}"'.encode() in docs
