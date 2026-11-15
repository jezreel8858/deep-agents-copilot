"""Testes de guardas de path e denylist imutável (B3-04 / CA-07)."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from governance_runner import cli
from governance_runner.synth.diagnostic_exporter import (
    DENYLIST_REL_PATHS,
    SynthDiagnosticPathError,
    ensure_allowed_write_path,
)
from governance_runner.synth.routing_graph import (
    RoutingGraphPathError,
    resolver_caminho_routing_graph,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_out_path_traversal_rejeitado(tmp_path: Path) -> None:
    """CA-07: Qualquer tentativa de path traversal ('..') ou escrita fora das pastas permitidas falha com exit_code 5."""
    with pytest.raises(SynthDiagnosticPathError) as exc_tr:
        ensure_allowed_write_path("../escape/diagnostic.yaml", repo_root=tmp_path)
    assert exc_tr.value.exit_code == 5

    with pytest.raises(SynthDiagnosticPathError) as exc_fora:
        ensure_allowed_write_path(tmp_path / "docs" / "diagnostic.yaml", repo_root=tmp_path, allow_root=False)
    assert exc_fora.value.exit_code == 5

    ok_synth = ensure_allowed_write_path(
        ".github/agents/evals/synthetic/diagnostic-r1.yaml", repo_root=tmp_path
    )
    ok_dot = ensure_allowed_write_path(".synth/diagnostic-r1.yaml", repo_root=tmp_path)
    assert ok_synth.name == "diagnostic-r1.yaml"
    assert ok_dot.name == "diagnostic-r1.yaml"


def test_routing_graph_fora_do_repo_rejeitado(tmp_path: Path) -> None:
    """CA-07: --routing-graph fora do repo_root, com '..' ou via symlink que escapa falha com RoutingGraphPathError (exit 5)."""
    fora = tmp_path.parent / "externo-routing-graph.yaml"
    with pytest.raises(RoutingGraphPathError) as exc_abs:
        resolver_caminho_routing_graph(fora, repo_root=tmp_path)
    assert exc_abs.value.exit_code == 5

    with pytest.raises(RoutingGraphPathError) as exc_dots:
        resolver_caminho_routing_graph("../routing-graph.yaml", repo_root=tmp_path)
    assert exc_dots.value.exit_code == 5

    alvo_ext = tmp_path.parent / f"alvo_ext_{tmp_path.name}.yaml"
    alvo_ext.write_text("versao: '1.0.0'\n", encoding="utf-8")
    link = tmp_path / "link-grafo.yaml"
    try:
        os.symlink(alvo_ext, link)
    except (OSError, NotImplementedError):
        alvo_ext.unlink(missing_ok=True)
        pytest.skip("Symlink indisponível neste ambiente Windows sem privilégio de desenvolvedor.")
    try:
        with pytest.raises(RoutingGraphPathError) as exc_sym:
            resolver_caminho_routing_graph(link, repo_root=tmp_path)
        assert exc_sym.value.exit_code == 5
    finally:
        alvo_ext.unlink(missing_ok=True)


@pytest.mark.parametrize(
    "rel_protegido",
    [p.as_posix() for p in DENYLIST_REL_PATHS],
)
def test_allow_root_nao_permite_sobrescrever_arquivos_protegidos(
    tmp_path: Path,
    rel_protegido: str,
) -> None:
    """CA-07: Mesmo com allow_root=True ou allow_root customizado, a denylist imutável bloqueia escrita (exit 5)."""
    alvo = tmp_path / rel_protegido
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text("conteudo protegido original\n", encoding="utf-8")
    hash_antes = _sha256(alvo)

    with pytest.raises(SynthDiagnosticPathError) as exc_bool:
        ensure_allowed_write_path(alvo, repo_root=tmp_path, allow_root=True)
    assert exc_bool.value.exit_code == 5

    with pytest.raises(SynthDiagnosticPathError) as exc_path:
        ensure_allowed_write_path(alvo, repo_root=tmp_path, allow_root=alvo.parent)
    assert exc_path.value.exit_code == 5

    copia_basename = tmp_path / ".synth" / Path(rel_protegido).name
    with pytest.raises(SynthDiagnosticPathError) as exc_base:
        ensure_allowed_write_path(copia_basename, repo_root=tmp_path, allow_root=True)
    assert exc_base.value.exit_code == 5

    assert _sha256(alvo) == hash_antes


def test_fontes_readonly_do_repositorio_permanecem_intactas(tmp_path: Path) -> None:
    """CA-07: Verifica os hashes SHA-256 reais das 3 fontes read-only do repositório antes e depois de comandos CLI."""
    repo_root = Path(__file__).resolve().parents[4]
    fontes = [repo_root / p for p in DENYLIST_REL_PATHS]
    hashes_antes = {f: _sha256(f) for f in fontes}

    db = str(tmp_path / "guard.db")
    rc = cli.main(
        [
            "--use-case",
            "synth-generate",
            "--db",
            db,
            "--routing-graph",
            "../fora/routing-graph.yaml",
        ]
    )
    assert rc == 5

    for f, h_ant in hashes_antes.items():
        assert _sha256(f) == h_ant
