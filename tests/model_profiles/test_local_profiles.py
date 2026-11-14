"""Perfis locais (model-profiles.local.yaml) em repositorio temporario.

Nunca le nem grava o model-profiles.local.yaml real do workspace.
"""
from __future__ import annotations

import yaml

from ._helpers import FLASH, HAIKU, OPUS, SONNET, expected_bytes, run_cli

LOCAL = "model-profiles.local.yaml"


def _unchanged(repo, originals) -> bool:
    return all((repo / rel).read_bytes() == data for rel, data in originals.items())


def _write_local(repo, profiles: dict, tier_map: dict | None = None) -> None:
    data: dict = {"schema_version": 1, "profiles": profiles}
    if tier_map is not None:
        data["tier_map"] = tier_map
    (repo / LOCAL).write_bytes(yaml.safe_dump(data, sort_keys=False, allow_unicode=True).encode("utf-8"))


def test_apply_perfil_local(repo, capsys, originals):
    _write_local(repo, {
        "meu-perfil": {
            "extends": "economico",
            "description": "overlay",
            "tiers": {"light": HAIKU},
            "agents": {"docs-engineer": OPUS},
            "prompts": {"prompt:commit": FLASH},
        },
    })
    code, out = run_cli(capsys, repo, "list")
    assert code == 0, out
    local_line = next(ln for ln in out.splitlines() if "meu-perfil" in ln)
    assert "(local)" in local_line
    assert not any("(local)" in ln and "economico" in ln for ln in out.splitlines())

    code, out = run_cli(capsys, repo, "apply", "meu-perfil", "--yes")
    assert code == 0, out
    # D2: agents > tiers (light seria Haiku; override mantem Opus no docs-engineer)
    assert (repo / ".github/agents/docs-engineer.agent.md").read_bytes() == expected_bytes(
        originals[".github/agents/docs-engineer.agent.md"], FLASH, OPUS)
    # D2: prompts > tiers (light seria Haiku; prompt:commit permanece Flash)
    assert (repo / ".github/prompts/commit.prompt.md").read_bytes() == originals[
        ".github/prompts/commit.prompt.md"]
    # extends economico rebaixa orquestracao e standard
    assert (repo / ".github/agents/agent-router.agent.md").read_bytes() == expected_bytes(
        originals[".github/agents/agent-router.agent.md"], SONNET, HAIKU)
    assert (repo / ".github/agents/python-developer.agent.md").read_bytes() == expected_bytes(
        originals[".github/agents/python-developer.agent.md"], SONNET, HAIKU)

    code, out = run_cli(capsys, repo, "status")
    assert code == 0 and "meu-perfil (local)" in out, out


def test_colisao_builtin(repo, capsys, originals):
    _write_local(repo, {"economico": {"extends": "default", "description": "sombra"}})
    code, out = run_cli(capsys, repo, "list")
    assert code == 1 and "[PROFILE_COLLISION]" in out and "economico" in out
    assert _unchanged(repo, originals)
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 1 and "[PROFILE_COLLISION]" in out
    assert _unchanged(repo, originals)


def test_modelo_fora_allowlist(repo, capsys, originals):
    _write_local(repo, {
        "fantasma": {"extends": "default", "description": "x",
                     "tiers": {"light": "Modelo Fantasma 9"}},
    })
    code, out = run_cli(capsys, repo, "apply", "fantasma", "--yes")
    assert code == 1 and "[UNKNOWN_MODEL]" in out
    assert _unchanged(repo, originals)


def test_arquivo_local_ausente(repo, capsys, originals):
    assert not (repo / LOCAL).exists()
    code, out = run_cli(capsys, repo, "list")
    assert code == 0 and "(local)" not in out
    assert all(name in out for name in ("default", "balanceado", "economico"))
    code, out = run_cli(capsys, repo, "apply", "economico", "--yes")
    assert code == 0, out
    assert (repo / ".github/agents/agent-router.agent.md").read_bytes() == expected_bytes(
        originals[".github/agents/agent-router.agent.md"], SONNET, HAIKU)


def test_tier_map_local_rejeita_chave_nova(repo, capsys, originals):
    _write_local(repo, {"meu-perfil": {"extends": "default", "description": "x"}},
                 tier_map={"light": ["prompt:commit", "agent-novo"]})
    code, out = run_cli(capsys, repo, "list")
    assert code == 1 and "[TIER_MAP]" in out and "agent-novo" in out
    assert _unchanged(repo, originals)


def test_perfil_local_respeita_d6_e_path_traversal(repo, capsys, originals):
    _write_local(repo, {
        "caro": {"extends": "economico", "description": "x",
                 "agents": {"python-developer": OPUS}},
    })
    code, out = run_cli(capsys, repo, "apply", "caro", "--yes")
    assert code == 1 and "[COST_HIERARCHY]" in out
    assert _unchanged(repo, originals)

    _write_local(repo, {
        "traversal": {"extends": "default", "description": "x",
                      "agents": {"../fora": FLASH}},
    })
    code, out = run_cli(capsys, repo, "apply", "traversal", "--yes")
    assert code == 1 and "[PATH_TRAVERSAL]" in out
    assert _unchanged(repo, originals)


def test_prompt_local_exige_forma_canonica(repo, capsys, originals):
    _write_local(repo, {
        "ruim": {"extends": "default", "description": "x", "prompts": {"commit": FLASH}},
    })
    code, out = run_cli(capsys, repo, "list")
    assert code == 1 and "[PROFILE]" in out and "prompt:" in out
    assert _unchanged(repo, originals)


def test_init_copia_example_sem_sobrescrever(repo, capsys):
    example = repo / "model-profiles.local.yaml.example"
    payload = "schema_version: 1\nprofiles:\n  meu-perfil:\n    extends: economico\n"
    example.write_text(payload, encoding="utf-8", newline="\n")
    code, out = run_cli(capsys, repo, "init")
    assert code == 0, out
    dest = repo / LOCAL
    assert dest.read_text(encoding="utf-8") == payload
    assert "criado a partir" in out
    dest.write_text("custom: true\n", encoding="utf-8", newline="\n")
    code, out = run_cli(capsys, repo, "init")
    assert code == 0, out
    assert dest.read_text(encoding="utf-8") == "custom: true\n"
    assert "nao sobrescrito" in out
