"""Aceite B1 (plano §9): schema v3, migracao v2->v3, projecao dos 9 workflows e hash estavel."""
from __future__ import annotations

import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from governance_runner.synth import storage
from governance_runner.synth.routing_graph import (
    calcular_workflow_hash,
    carregar_snapshot_grafo,
)
from governance_runner.synth.storage import SynthRepository, migrar_conexao

COLUNAS_PROMPTS_V3 = {"expected_workflow", "graph_workflow_id"}
COLUNAS_EVAL_V3 = {"observed_workflow", "observed_etapa", "workflow_source", "workflow_route_consistent"}


def _cols(conn: sqlite3.Connection, tabela: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({tabela})")}


def _criar_banco_v2(db: Path, *, com_linhas: bool = True) -> None:
    """Gera um banco v2 fiel: schema v3 atual com as colunas/tabela/indice v3 removidos."""
    r = SynthRepository(db, repo_root=db.parent)
    r.migrar()
    r.close()
    conn = sqlite3.connect(db)
    try:
        conn.execute("DROP INDEX IF EXISTS ix_synth_prompts_graph_workflow")
        for c in COLUNAS_PROMPTS_V3:
            conn.execute(f"ALTER TABLE synth_prompts DROP COLUMN {c}")
        for c in COLUNAS_EVAL_V3:
            conn.execute(f"ALTER TABLE synth_evaluations DROP COLUMN {c}")
        conn.execute("DROP TABLE routing_graph_workflows")
        conn.execute("UPDATE schema_meta SET value='2' WHERE key='schema_version'")
        if com_linhas:
            conn.execute(
                "INSERT INTO synth_runs (run_id, kind, started_at, status) "
                "VALUES ('r-v2','generate','2026-01-01T00:00:00Z','completed')"
            )
            for i in range(3):
                conn.execute(
                    "INSERT INTO synth_prompts (prompt_id, run_id, text, text_norm, sha256, expected_route,"
                    " agente_alvo, dimensao_perturbacao, max_similarity, created_at) "
                    "VALUES (?, 'r-v2', 't', 't', ?, 'bug-triage', 'bug-triage', 'parafrase', 0.1, '2026-01-01T00:00:00Z')",
                    (f"p{i}", f"sha{i}"),
                )
            conn.execute(
                "INSERT INTO synth_evaluations (eval_id, run_id, prompt_id, observed_route, route_source,"
                " verdict, passed, created_at) VALUES ('e0','r-v2','p0','bug-triage','text_banner','matched',1,"
                "'2026-01-01T00:00:00Z')"
            )
        conn.execute("PRAGMA user_version = 2")
        conn.commit()
    finally:
        conn.close()


def _contagens(conn: sqlite3.Connection) -> dict[str, int]:
    return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("synth_runs", "synth_prompts", "synth_evaluations")}


# ---------------------------------------------------------------- banco novo
def test_banco_novo_nasce_v3(tmp_path: Path) -> None:
    with SynthRepository(tmp_path / "novo.db", repo_root=tmp_path) as r:
        assert r.migrar() == "3"
        assert storage.SCHEMA_VERSION == "3"
        assert r.obter_schema_version() == "3"
        assert r.connection.execute("PRAGMA user_version").fetchone()[0] == 3
        assert COLUNAS_PROMPTS_V3 <= _cols(r.connection, "synth_prompts")
        assert COLUNAS_EVAL_V3 <= _cols(r.connection, "synth_evaluations")
        assert _cols(r.connection, "routing_graph_workflows") >= {
            "workflow_id", "graph_sha256", "nome", "fast_path",
            "gatilhos_json", "etapa1_padroes_json", "workflow_hash",
        }
    assert not Path(f"{tmp_path / 'novo.db'}.bak-v2").exists()


def test_banco_memoria_nasce_v3_sem_backup() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        assert migrar_conexao(conn) == "3"
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 3
    finally:
        conn.close()


# ------------------------------------------------------------- migracao v2->v3
def test_v2_migra_sem_perda_de_linhas_e_cria_backup(tmp_path: Path) -> None:
    db = tmp_path / "v2.db"
    _criar_banco_v2(db)
    conn = sqlite3.connect(db)
    antes = _contagens(conn)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 2
    assert not (COLUNAS_PROMPTS_V3 & _cols(conn, "synth_prompts"))
    conn.close()
    bytes_v2 = db.read_bytes()

    with SynthRepository(db, repo_root=tmp_path) as r:
        assert r.migrar() == "3"
        assert _contagens(r.connection) == antes
        assert r.connection.execute("PRAGMA user_version").fetchone()[0] == 3
        assert r.obter_schema_version() == "3"
        assert COLUNAS_PROMPTS_V3 <= _cols(r.connection, "synth_prompts")
        assert COLUNAS_EVAL_V3 <= _cols(r.connection, "synth_evaluations")
        nulos = r.connection.execute(
            "SELECT COUNT(*) FROM synth_prompts WHERE expected_workflow IS NULL AND graph_workflow_id IS NULL"
        ).fetchone()[0]
        assert nulos == antes["synth_prompts"]  # seeds legados = NULL
        idx = {x[1] for x in r.connection.execute("PRAGMA index_list(synth_prompts)")}
        assert "ix_synth_prompts_graph_workflow" in idx

    bak = Path(f"{db}.bak-v2")
    assert bak.exists(), "ramo v2->v3 deve criar <db>.bak-v2 (§3.2c)"
    assert bak.read_bytes() == bytes_v2
    c = sqlite3.connect(bak)
    try:
        assert c.execute("PRAGMA user_version").fetchone()[0] == 2
    finally:
        c.close()


def test_backup_existente_nao_e_sobrescrito(tmp_path: Path) -> None:
    db = tmp_path / "v2.db"
    _criar_banco_v2(db)
    bak = Path(f"{db}.bak-v2")
    bak.write_bytes(b"sentinela")
    with SynthRepository(db, repo_root=tmp_path) as r:
        assert r.migrar() == "3"
    assert bak.read_bytes() == b"sentinela"


def test_v3_reaberto_e_noop(tmp_path: Path) -> None:
    db = tmp_path / "v3.db"
    _criar_banco_v2(db)
    with SynthRepository(db, repo_root=tmp_path) as r:
        r.migrar()
    Path(f"{db}.bak-v2").unlink()
    estado1 = db.read_bytes()
    with SynthRepository(db, repo_root=tmp_path) as r:
        assert r.migrar() == "3"
        assert r.migrar() == "3"
        assert _contagens(r.connection)["synth_prompts"] == 3
    assert db.read_bytes() == estado1, "reabrir v3 nao deve alterar o arquivo"
    assert not Path(f"{db}.bak-v2").exists(), "v3 reaberto nao gera novo backup"


def test_v2_em_memoria_migra_sem_backup_em_disco(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    conn = sqlite3.connect(":memory:")
    try:
        migrar_conexao(conn)
        # v2 parcial em memoria: remove artefatos v3
        conn.execute("DROP INDEX IF EXISTS ix_synth_prompts_graph_workflow")
        for c in COLUNAS_PROMPTS_V3:
            conn.execute(f"ALTER TABLE synth_prompts DROP COLUMN {c}")
        for c in COLUNAS_EVAL_V3:
            conn.execute(f"ALTER TABLE synth_evaluations DROP COLUMN {c}")
        conn.execute("DROP TABLE routing_graph_workflows")
        conn.execute("PRAGMA user_version = 2")
        assert migrar_conexao(conn) == "3"
        assert COLUNAS_PROMPTS_V3 <= _cols(conn, "synth_prompts")
    finally:
        conn.close()
    assert list(tmp_path.glob("*.bak-v2")) == []


def test_alters_v3_idempotentes_com_colunas_parciais(tmp_path: Path) -> None:
    """user_version=2 mas uma coluna v3 ja existente (migracao interrompida/manual) nao quebra."""
    db = tmp_path / "parcial.db"
    _criar_banco_v2(db)
    conn = sqlite3.connect(db)
    conn.execute("ALTER TABLE synth_prompts ADD COLUMN expected_workflow TEXT")
    conn.commit()
    conn.close()
    with SynthRepository(db, repo_root=tmp_path) as r:
        assert r.migrar() == "3"
        assert COLUNAS_PROMPTS_V3 <= _cols(r.connection, "synth_prompts")


def test_falha_no_backup_aborta_migracao_sem_alterar_banco(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "v2.db"
    _criar_banco_v2(db)

    def _boom(*_a: object, **_k: object) -> None:
        raise OSError("disco cheio")

    monkeypatch.setattr(storage.shutil, "copy2", _boom)
    conn = sqlite3.connect(db)
    try:
        with pytest.raises(Exception):  # noqa: B017,PT011 - qualquer erro de aborto e valido
            migrar_conexao(conn)
    finally:
        conn.close()
    c = sqlite3.connect(db)
    try:
        assert c.execute("PRAGMA user_version").fetchone()[0] == 2
        assert not (COLUNAS_PROMPTS_V3 & _cols(c, "synth_prompts"))
    finally:
        c.close()


def test_rollback_preserva_v2_se_alter_falha(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "v2.db"
    _criar_banco_v2(db)
    original = storage._colunas_tabela
    chamadas = {"n": 0}

    def _falha(conn: sqlite3.Connection, tabela: str) -> set[str]:
        chamadas["n"] += 1
        if tabela == "synth_evaluations":
            raise sqlite3.OperationalError("falha injetada")
        return original(conn, tabela)

    monkeypatch.setattr(storage, "_colunas_tabela", _falha)
    conn = sqlite3.connect(db)
    try:
        with pytest.raises(sqlite3.OperationalError):
            migrar_conexao(conn)
    finally:
        conn.close()
    monkeypatch.undo()
    c = sqlite3.connect(db)
    try:
        assert c.execute("PRAGMA user_version").fetchone()[0] == 2
        assert not (COLUNAS_PROMPTS_V3 & _cols(c, "synth_prompts")), "ALTER parcial deve sofrer rollback"
    finally:
        c.close()


# ------------------------------------------------------------ projecao real
def test_snapshot_real_tem_9_workflows_com_etapa1_nao_vazia() -> None:
    snap = carregar_snapshot_grafo()
    assert len(snap.workflows) == 9
    ids = [w.workflow_id for w in snap.workflows]
    assert len(set(ids)) == 9
    assert all(i.startswith("WORKFLOW-") for i in ids)
    for w in snap.workflows:
        assert w.etapa1_padroes, f"{w.workflow_id}: etapa 1 vazia"
        assert w.gatilhos_norm, f"{w.workflow_id}: sem gatilhos"
        assert len(w.workflow_hash) == 64
    fd = next(w for w in snap.workflows if w.workflow_id == "WORKFLOW-FEATURE-DEVELOPMENT")
    assert fd.fast_path is False
    assert "prompt-structuring" in fd.etapa1_padroes
    assert next(w for w in snap.workflows if w.workflow_id == "WORKFLOW-BUG-FIX").fast_path is True


def test_hash_dos_workflows_e_estavel_e_sensivel_a_conteudo() -> None:
    s1, s2 = carregar_snapshot_grafo(), carregar_snapshot_grafo()
    assert [w.workflow_hash for w in s1.workflows] == [w.workflow_hash for w in s2.workflows]
    for w in s1.workflows:
        assert w.workflow_hash == calcular_workflow_hash(
            workflow_id=w.workflow_id, nome=w.nome, fast_path=w.fast_path,
            gatilhos_norm=w.gatilhos_norm, etapa1_padroes=w.etapa1_padroes,
        )
    w = s1.workflows[0]
    base = dict(workflow_id=w.workflow_id, nome=w.nome, fast_path=w.fast_path,
                gatilhos_norm=w.gatilhos_norm, etapa1_padroes=w.etapa1_padroes)
    h0 = calcular_workflow_hash(**base)
    assert calcular_workflow_hash(**{**base, "fast_path": not w.fast_path}) != h0
    assert calcular_workflow_hash(**{**base, "gatilhos_norm": (*w.gatilhos_norm, "x")}) != h0
    assert calcular_workflow_hash(**{**base, "nome": w.nome + "!"}) != h0
    assert len({x.workflow_hash for x in s1.workflows}) == 9


def test_registrar_workflows_grafo_persiste_e_e_idempotente(repo: SynthRepository) -> None:
    snap = carregar_snapshot_grafo()
    n1 = repo.registrar_workflows_grafo(snap)
    n2 = repo.registrar_workflows_grafo(snap)
    linhas = repo.listar_workflows_grafo(snap.sha256)
    assert n1 == n2 == 9
    assert len(linhas) == 9
    por_id = {r["workflow_id"]: r for r in linhas}
    for w in snap.workflows:
        assert por_id[w.workflow_id]["workflow_hash"] == w.workflow_hash
    assert repo.listar_workflows_grafo("inexistente") == []


def test_registrar_workflows_grafo_snapshot_sem_workflows(repo: SynthRepository) -> None:
    snap = replace(carregar_snapshot_grafo(), workflows=())
    assert repo.registrar_workflows_grafo(snap) == 0
