"""Testes de migração transacional SQLite v1 -> v2 sem executescript (B1-03 / CA-04)."""
from __future__ import annotations

import inspect
import sqlite3
from pathlib import Path

import pytest

from governance_runner.synth import storage
from governance_runner.synth.storage import SynthRepository, migrar_conexao

DDL_V1 = [
    "CREATE TABLE schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    "INSERT INTO schema_meta (key, value) VALUES ('schema_version', '1')",
    """
    CREATE TABLE synth_runs (
      run_id TEXT PRIMARY KEY,
      parent_run_id TEXT,
      kind TEXT NOT NULL,
      started_at TEXT NOT NULL,
      finished_at TEXT,
      status TEXT NOT NULL,
      motivo TEXT,
      generator TEXT,
      model TEXT,
      rng_seed INTEGER,
      params_json TEXT NOT NULL DEFAULT '{}',
      golden_set_sha256 TEXT,
      router_agent_sha256 TEXT,
      premium_requests_used INTEGER NOT NULL DEFAULT 0,
      n_candidates INTEGER NOT NULL DEFAULT 0,
      n_rejected_hash INTEGER NOT NULL DEFAULT 0,
      n_rejected_similarity INTEGER NOT NULL DEFAULT 0,
      n_rejected_override INTEGER NOT NULL DEFAULT 0,
      n_accepted INTEGER NOT NULL DEFAULT 0,
      n_evaluated INTEGER NOT NULL DEFAULT 0,
      n_passed INTEGER NOT NULL DEFAULT 0,
      n_unparseable INTEGER NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE synth_prompts (
      prompt_id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL REFERENCES synth_runs(run_id),
      text TEXT NOT NULL,
      text_norm TEXT NOT NULL,
      sha256 TEXT NOT NULL UNIQUE,
      expected_route TEXT NOT NULL,
      agente_alvo TEXT NOT NULL,
      dimensao_perturbacao TEXT NOT NULL,
      seed_case_id TEXT,
      max_similarity REAL NOT NULL,
      nearest_ref TEXT,
      status TEXT NOT NULL DEFAULT 'accepted',
      reject_reason TEXT,
      created_at TEXT NOT NULL
    )
    """,
    "PRAGMA user_version = 1",
]


def _criar_banco_v1(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        for stmt in DDL_V1:
            conn.execute(stmt)
        conn.execute(
            "INSERT INTO synth_runs (run_id, kind, started_at, status) VALUES ('r-v1', 'generate', '2026-01-01T00:00:00Z', 'completed')"
        )
        conn.execute(
            """
            INSERT INTO synth_prompts (
              prompt_id, run_id, text, text_norm, sha256, expected_route,
              agente_alvo, dimensao_perturbacao, seed_case_id, max_similarity, created_at
            ) VALUES (
              'p-v1', 'r-v1', 'texto legado', 'texto legado', 'sha-v1', 'python-developer',
              'python-developer', 'parafrase', 'G-001', 0.25, '2026-01-01T00:00:00Z'
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def test_migracao_v1_v2_adiciona_colunas_antes_do_indice(tmp_path: Path) -> None:
    """CA-04: Migra banco v1 populado para v2 sem executescript, preservando dados e criando índice depois do ALTER."""
    codigo_storage = inspect.getsource(migrar_conexao)
    assert ".executescript(" not in codigo_storage

    db = tmp_path / "v1.db"
    _criar_banco_v1(db)

    with SynthRepository(db, repo_root=tmp_path) as repo:
        ver = repo.migrar()
        assert ver == "2"
        assert repo.obter_schema_version() == "2"
        user_ver = int(repo.connection.execute("PRAGMA user_version").fetchone()[0])
        assert user_ver == 2

        prompt = repo.obter_prompt("p-v1")
        assert prompt is not None
        assert prompt["text"] == "texto legado"
        assert prompt["seed_source"] == "manual"
        assert prompt["graph_edge_id"] is None
        assert prompt["graph_edge_resolution"] is None

        run = repo.obter_run("r-v1")
        assert run is not None
        assert "routing_graph_sha256" in run

        tabelas = {
            r[0]
            for r in repo.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert {"routing_graph_edges", "synth_diagnostics"}.issubset(tabelas)

        indices = {
            r[0]
            for r in repo.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            ).fetchall()
        }
        assert "ix_prompts_graph_edge" in indices


def test_migracao_rollback_em_falha_preserva_v1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CA-04: Se ocorrer erro durante a migração v1 -> v2, faz ROLLBACK atômico mantendo user_version=1 e tabelas v1."""
    db = tmp_path / "rollback.db"
    _criar_banco_v1(db)

    monkeypatch.setattr(
        storage,
        "_DDL_TABELAS_AUX_V2",
        (storage._DDL_TABELAS_AUX_V2[0], "CREATE TABLE sql_invalido_para_forcar_rollback ("),
    )

    conn = sqlite3.connect(db)
    try:
        with pytest.raises(sqlite3.OperationalError):
            migrar_conexao(conn)

        user_ver = int(conn.execute("PRAGMA user_version").fetchone()[0])
        assert user_ver == 1
        cols_prompts = {r[1] for r in conn.execute("PRAGMA table_info(synth_prompts)").fetchall()}
        assert "seed_source" not in cols_prompts
        assert "graph_edge_id" not in cols_prompts
        row = conn.execute("SELECT text FROM synth_prompts WHERE prompt_id = 'p-v1'").fetchone()
        assert row is not None and row[0] == "texto legado"
    finally:
        conn.close()


def test_migracao_idempotente(tmp_path: Path) -> None:
    """CA-04: Executar migrar() múltiplas vezes em v1->v2 e v2->v2 é idempotente."""
    db = tmp_path / "idemp.db"
    _criar_banco_v1(db)

    with SynthRepository(db, repo_root=tmp_path) as repo:
        assert repo.migrar() == "2"
        assert repo.migrar() == "2"
        assert repo.migrar() == "2"
        assert int(repo.connection.execute("PRAGMA user_version").fetchone()[0]) == 2
        assert len(repo.listar_prompts("r-v1")) == 1


def test_banco_novo_nasce_em_user_version_2(tmp_path: Path) -> None:
    """CA-04: Banco novo nasce diretamente em user_version = 2 e schema_version = '2'."""
    db = tmp_path / "novo.db"
    with SynthRepository(db, repo_root=tmp_path) as repo:
        assert repo.migrar() == "2"
        assert repo.obter_schema_version() == "2"
        assert int(repo.connection.execute("PRAGMA user_version").fetchone()[0]) == 2
        cols = {r[1] for r in repo.connection.execute("PRAGMA table_info(synth_prompts)").fetchall()}
        assert {"seed_source", "graph_edge_id", "graph_edge_resolution"}.issubset(cols)
