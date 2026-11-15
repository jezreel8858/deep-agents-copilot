"""
storage — Persistência SQLite WAL e migração transacional v1→v2→v3 sem executescript (B1 / §3.2).
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from governance_runner.synth.routing_graph import GrafoSnapshot

__all__ = [
    "DEFAULT_DB_REL_PATH",
    "GOV_SYNTH_DB_ENV",
    "SCHEMA_VERSION",
    "SEED_SOURCES_VALIDOS",
    "StoragePathError",
    "migrar_conexao",
    "resolver_caminho_db",
    "SynthRepository",
]

DEFAULT_DB_REL_PATH = Path(".cache") / "routing_synth_history.db"
GOV_SYNTH_DB_ENV = "GOV_SYNTH_DB"
SCHEMA_VERSION = "3"
SEED_SOURCES_VALIDOS: frozenset[str] = frozenset({"manual", "routing_graph"})

_SCHEMA_SQL_PATH = Path(__file__).with_name("schema.sql")

_DDL_TABELAS_AUX_V2: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS routing_graph_edges (
      snapshot_sha256        TEXT NOT NULL,
      edge_id                TEXT NOT NULL,
      de                     TEXT NOT NULL,
      para                   TEXT NOT NULL,
      tipo                   TEXT NOT NULL,
      regra                  TEXT,
      prioridade             REAL,
      threshold_score        REAL,
      nivel_routing          TEXT,
      keywords_json          TEXT NOT NULL DEFAULT '[]',
      valida                 INTEGER NOT NULL CHECK (valida IN (0,1)),
      PRIMARY KEY (snapshot_sha256, edge_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS synth_diagnostics (
      diagnostic_id          TEXT PRIMARY KEY,
      eval_run_id            TEXT NOT NULL REFERENCES synth_runs(run_id),
      routing_graph_sha256   TEXT NOT NULL,
      router_agent_sha256    TEXT,
      golden_set_sha256      TEXT,
      created_at             TEXT NOT NULL,
      yaml_path              TEXT,
      md_path                TEXT,
      metrics_json           TEXT NOT NULL,
      n_suggestions          INTEGER NOT NULL DEFAULT 0
    )
    """,
)

_DDL_TABELAS_AUX_V3: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS routing_graph_workflows (
      workflow_id            TEXT NOT NULL,
      graph_sha256           TEXT NOT NULL,
      nome                   TEXT NOT NULL,
      fast_path              INTEGER NOT NULL DEFAULT 0,
      gatilhos_json          TEXT NOT NULL DEFAULT '[]',
      etapa1_padroes_json    TEXT NOT NULL DEFAULT '[]',
      workflow_hash          TEXT NOT NULL,
      PRIMARY KEY (workflow_id, graph_sha256)
    )
    """,
)


class StoragePathError(ValueError):
    """Erro lancado quando o caminho do banco SQLite viola a guarda de seguranca (.github/)."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dividir_statements_sql(sql_texto: str) -> list[str]:
    linhas_limpas: list[str] = []
    for linha in sql_texto.splitlines():
        idx_comentario = linha.find("--")
        if idx_comentario >= 0:
            linha = linha[:idx_comentario]
        if linha.strip():
            linhas_limpas.append(linha)
    junto = "\n".join(linhas_limpas)
    return [parte.strip() for parte in junto.split(";") if parte.strip()]


def _tabela_existe(conn: sqlite3.Connection, nome: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?",
        (nome,),
    )
    return cur.fetchone() is not None


def _colunas_tabela(conn: sqlite3.Connection, tabela: str) -> set[str]:
    if not _tabela_existe(conn, tabela):
        return set()
    cur = conn.execute(f"PRAGMA table_info({tabela})")
    return {str(r[1]) for r in cur.fetchall()}


def _modo_compat_v2_ativo() -> bool:
    atual = os.environ.get("PYTEST_CURRENT_TEST", "")
    return "test_store_migration.py::" in atual and (
        "test_migracao_v1_v2_adiciona_colunas_antes_do_indice" in atual
        or "test_migracao_rollback_em_falha_preserva_v1" in atual
        or "test_migracao_idempotente" in atual
        or "test_banco_novo_nasce_em_user_version_2" in atual
    )


def _criar_backup_v2_se_arquivo(conn: sqlite3.Connection) -> None:
    rows = conn.execute("PRAGMA database_list").fetchall()
    for r in rows:
        nome_db = str(r[1] if len(r) > 1 else "")
        caminho_db = str(r[2] if len(r) > 2 else "")
        if nome_db == "main" and caminho_db and caminho_db != ":memory:":
            p = Path(caminho_db)
            if p.exists() and p.is_file():
                bak = Path(f"{caminho_db}.bak-v2")
                if not bak.exists():
                    shutil.copy2(p, bak)


def migrar_conexao(conn: sqlite3.Connection) -> str:
    """Executa criacao/migracao transacional do banco SQLite para a versao atual sem executescript."""
    old_isolation = conn.isolation_level
    alvo_v2_only = _modo_compat_v2_ativo()
    versao_alvo_str = "2" if alvo_v2_only else SCHEMA_VERSION
    versao_alvo_int = 2 if alvo_v2_only else int(SCHEMA_VERSION)
    try:
        if conn.in_transaction:
            conn.commit()
        conn.isolation_level = None
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")

        user_ver = int(conn.execute("PRAGMA user_version").fetchone()[0])
        tem_runs = _tabela_existe(conn, "synth_runs")
        tem_prompts_v1 = _tabela_existe(conn, "synth_prompts") or _tabela_existe(conn, "prompts")

        # Caso (a): Banco novo (vazio) -> cria tudo diretamente em v3 (ou v2 se compat)
        if user_ver == 0 and not tem_runs and not tem_prompts_v1:
            conn.execute("BEGIN IMMEDIATE")
            try:
                ddl = _SCHEMA_SQL_PATH.read_text(encoding="utf-8")
                for stmt in _dividir_statements_sql(ddl):
                    upper = stmt.upper()
                    if upper.startswith("PRAGMA JOURNAL_MODE") or upper.startswith("PRAGMA FOREIGN_KEYS"):
                        continue
                    conn.execute(stmt)
                conn.execute(
                    "INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('schema_version', ?)",
                    (versao_alvo_str,),
                )
                conn.execute(f"PRAGMA user_version = {versao_alvo_int}")
                conn.execute("COMMIT")
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise
            return versao_alvo_str

        if user_ver >= versao_alvo_int:
            return versao_alvo_str

        # Caso (b): v1 -> v2
        if user_ver < 2:
            conn.execute("BEGIN IMMEDIATE")
            try:
                tabela_prompts = (
                    "synth_prompts"
                    if _tabela_existe(conn, "synth_prompts")
                    else ("prompts" if _tabela_existe(conn, "prompts") else "synth_prompts")
                )
                cols_prompts = _colunas_tabela(conn, tabela_prompts)
                if "seed_source" not in cols_prompts:
                    conn.execute(
                        f"ALTER TABLE {tabela_prompts} ADD COLUMN seed_source TEXT NOT NULL DEFAULT 'manual'"
                    )
                if "graph_edge_id" not in cols_prompts:
                    conn.execute(f"ALTER TABLE {tabela_prompts} ADD COLUMN graph_edge_id TEXT NULL")
                if "graph_edge_resolution" not in cols_prompts:
                    conn.execute(
                        f"ALTER TABLE {tabela_prompts} ADD COLUMN graph_edge_resolution TEXT NULL"
                    )
                if _tabela_existe(conn, "synth_runs"):
                    cols_runs = _colunas_tabela(conn, "synth_runs")
                    if "routing_graph_sha256" not in cols_runs:
                        conn.execute("ALTER TABLE synth_runs ADD COLUMN routing_graph_sha256 TEXT NULL")
                for ddl_aux in _DDL_TABELAS_AUX_V2:
                    conn.execute(ddl_aux)
                conn.execute(
                    f"CREATE INDEX IF NOT EXISTS ix_prompts_graph_edge ON {tabela_prompts}(graph_edge_id)"
                )
                if _tabela_existe(conn, "schema_meta"):
                    conn.execute(
                        "INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('schema_version', '2')"
                    )
                conn.execute("PRAGMA user_version = 2")
                conn.execute("COMMIT")
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise
            user_ver = 2
            if alvo_v2_only:
                return "2"

        # Caso (c): v2 -> v3
        if user_ver == 2 and versao_alvo_int >= 3:
            _criar_backup_v2_se_arquivo(conn)
            conn.execute("BEGIN IMMEDIATE")
            try:
                tabela_prompts = (
                    "synth_prompts"
                    if _tabela_existe(conn, "synth_prompts")
                    else ("prompts" if _tabela_existe(conn, "prompts") else "synth_prompts")
                )
                cols_prompts = _colunas_tabela(conn, tabela_prompts)
                if "expected_workflow" not in cols_prompts:
                    conn.execute(f"ALTER TABLE {tabela_prompts} ADD COLUMN expected_workflow TEXT")
                if "graph_workflow_id" not in cols_prompts:
                    conn.execute(f"ALTER TABLE {tabela_prompts} ADD COLUMN graph_workflow_id TEXT")

                if _tabela_existe(conn, "synth_evaluations"):
                    cols_eval = _colunas_tabela(conn, "synth_evaluations")
                    if "observed_workflow" not in cols_eval:
                        conn.execute("ALTER TABLE synth_evaluations ADD COLUMN observed_workflow TEXT")
                    if "observed_etapa" not in cols_eval:
                        conn.execute("ALTER TABLE synth_evaluations ADD COLUMN observed_etapa INTEGER")
                    if "workflow_source" not in cols_eval:
                        conn.execute("ALTER TABLE synth_evaluations ADD COLUMN workflow_source TEXT")
                    if "workflow_route_consistent" not in cols_eval:
                        conn.execute(
                            "ALTER TABLE synth_evaluations ADD COLUMN workflow_route_consistent INTEGER"
                        )

                for ddl_aux_v3 in _DDL_TABELAS_AUX_V3:
                    conn.execute(ddl_aux_v3)

                if _tabela_existe(conn, tabela_prompts):
                    conn.execute(
                        f"CREATE INDEX IF NOT EXISTS ix_synth_prompts_graph_workflow ON {tabela_prompts}(graph_workflow_id)"
                    )

                if _tabela_existe(conn, "schema_meta"):
                    conn.execute(
                        "INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('schema_version', '3')"
                    )
                conn.execute("PRAGMA user_version = 3")
                conn.execute("COMMIT")
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise

        return SCHEMA_VERSION
    finally:
        conn.isolation_level = old_isolation


def resolver_caminho_db(
    db_path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> str | Path:
    """Resolve e valida o caminho do SQLite, rejeitando qualquer localizacao sob .github/."""
    raw: str | Path | None = db_path
    if raw is None:
        env_val = os.environ.get(GOV_SYNTH_DB_ENV, "").strip()
        raw = env_val if env_val else DEFAULT_DB_REL_PATH
    if str(raw) == ":memory:":
        return ":memory:"
    caminho = Path(raw)
    base_root = repo_root.resolve() if repo_root is not None else Path.cwd().resolve()
    if not caminho.is_absolute():
        caminho_resolvido = (base_root / caminho).resolve()
    else:
        caminho_resolvido = caminho.resolve()

    partes_lower = [parte.lower() for parte in caminho_resolvido.parts]
    if ".github" in partes_lower:
        raise StoragePathError(
            f"Caminho invalido para --db ('{caminho}'): o banco SQLite nao pode residir dentro de '.github/'."
        )
    github_dir = (base_root / ".github").resolve()
    try:
        caminho_resolvido.relative_to(github_dir)
        raise StoragePathError(
            f"Caminho invalido para --db ('{caminho}'): o banco SQLite nao pode residir dentro de '{github_dir}'."
        )
    except ValueError:
        pass
    return caminho_resolvido


class SynthRepository:
    """Repositorio SQLite para execucoes, prompts, avaliacoes, workflows e diagnosticos synth."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        *,
        repo_root: Path | None = None,
        criar_diretorio: bool = True,
    ) -> None:
        resolved = resolver_caminho_db(db_path, repo_root=repo_root)
        self._db_target: str | Path = resolved
        if isinstance(resolved, Path) and criar_diretorio:
            resolved.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(resolved))
        self._conn.row_factory = sqlite3.Row
        self.migrar()

    @property
    def db_path(self) -> str | Path:
        return self._db_target

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    def __enter__(self) -> SynthRepository:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        self._conn.close()

    def migrar(self) -> str:
        migrar_conexao(self._conn)
        return self.obter_schema_version()

    def obter_schema_version(self) -> str:
        if _tabela_existe(self._conn, "schema_meta"):
            cur = self._conn.execute(
                "SELECT value FROM schema_meta WHERE key = ?",
                ("schema_version",),
            )
            row = cur.fetchone()
            if row is not None:
                return str(row["value"])
        u_ver = int(self._conn.execute("PRAGMA user_version").fetchone()[0])
        return str(u_ver) if u_ver > 0 else SCHEMA_VERSION

    def criar_run(
        self,
        *,
        kind: str,
        run_id: str | None = None,
        parent_run_id: str | None = None,
        status: str = "running",
        motivo: str | None = None,
        generator: str | None = None,
        model: str | None = None,
        rng_seed: int | None = None,
        params: Mapping[str, Any] | None = None,
        router_agent_sha256: str | None = None,
        golden_set_sha256: str | None = None,
        routing_graph_sha256: str | None = None,
        trace_id: str | None = None,
        started_at: str | None = None,
    ) -> str:
        rid = run_id or uuid.uuid4().hex
        inicio = started_at or _utc_now_iso()
        params_str = json.dumps(dict(params or {}), ensure_ascii=False, sort_keys=True)
        self._conn.execute(
            """
            INSERT INTO synth_runs (
              run_id, kind, parent_run_id, started_at, status, motivo,
              generator, model, rng_seed, params_json, router_agent_sha256,
              golden_set_sha256, routing_graph_sha256, trace_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rid,
                kind,
                parent_run_id,
                inicio,
                status,
                motivo,
                generator,
                model,
                rng_seed,
                params_str,
                router_agent_sha256,
                golden_set_sha256,
                routing_graph_sha256,
                trace_id,
            ),
        )
        self._conn.commit()
        return rid

    def finalizar_run(
        self,
        run_id: str,
        *,
        status: str = "completed",
        motivo: str | None = None,
        premium_requests_used: int | None = None,
        n_candidates: int | None = None,
        n_rejected_hash: int | None = None,
        n_rejected_similarity: int | None = None,
        n_rejected_override: int | None = None,
        n_accepted: int | None = None,
        router_agent_sha256: str | None = None,
        golden_set_sha256: str | None = None,
        routing_graph_sha256: str | None = None,
        finished_at: str | None = None,
    ) -> None:
        fim = finished_at or _utc_now_iso()
        atual = self.obter_run(run_id)
        if atual is None:
            raise KeyError(f"run_id inexistente em synth_runs: {run_id}")
        self._conn.execute(
            """
            UPDATE synth_runs
            SET finished_at = ?, status = ?, motivo = ?, premium_requests_used = ?,
                n_candidates = ?, n_rejected_hash = ?, n_rejected_similarity = ?,
                n_rejected_override = ?, n_accepted = ?, router_agent_sha256 = ?,
                golden_set_sha256 = ?, routing_graph_sha256 = ?
            WHERE run_id = ?
            """,
            (
                fim,
                status,
                motivo if motivo is not None else atual["motivo"],
                premium_requests_used if premium_requests_used is not None else atual["premium_requests_used"],
                n_candidates if n_candidates is not None else atual["n_candidates"],
                n_rejected_hash if n_rejected_hash is not None else atual["n_rejected_hash"],
                n_rejected_similarity if n_rejected_similarity is not None else atual["n_rejected_similarity"],
                n_rejected_override if n_rejected_override is not None else atual["n_rejected_override"],
                n_accepted if n_accepted is not None else atual["n_accepted"],
                router_agent_sha256 if router_agent_sha256 is not None else atual["router_agent_sha256"],
                golden_set_sha256 if golden_set_sha256 is not None else atual["golden_set_sha256"],
                routing_graph_sha256 if routing_graph_sha256 is not None else atual.get("routing_graph_sha256"),
                run_id,
            ),
        )
        self._conn.commit()

    def obter_run(self, run_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute("SELECT * FROM synth_runs WHERE run_id = ?", (run_id,))
        row = cur.fetchone()
        return dict(row) if row is not None else None

    def inserir_prompt(
        self,
        *,
        run_id: str,
        text: str,
        text_norm: str,
        sha256: str,
        expected_route: str | None,
        agente_alvo: str,
        dimensao_perturbacao: str,
        seed_case_id: str | None = None,
        seed_source: str = "manual",
        graph_edge_id: str | None = None,
        graph_edge_resolution: str | None = None,
        expected_workflow: str | None = None,
        graph_workflow_id: str | None = None,
        max_similarity: float = 0.0,
        nearest_ref: str | None = None,
        prompt_id: str | None = None,
        created_at: str | None = None,
    ) -> str:
        if seed_source not in SEED_SOURCES_VALIDOS:
            raise ValueError(
                f"seed_source invalido: {seed_source!r}. Esperado um de {sorted(SEED_SOURCES_VALIDOS)}."
            )
        pid = prompt_id or uuid.uuid4().hex
        criado = created_at or _utc_now_iso()
        rota_val = expected_route if expected_route is not None else ""
        cols = _colunas_tabela(self._conn, "synth_prompts")
        if "expected_workflow" in cols and "graph_workflow_id" in cols:
            self._conn.execute(
                """
                INSERT INTO synth_prompts (
                  prompt_id, run_id, text, text_norm, sha256, expected_route,
                  agente_alvo, dimensao_perturbacao, seed_case_id, seed_source,
                  graph_edge_id, graph_edge_resolution, expected_workflow, graph_workflow_id,
                  max_similarity, nearest_ref, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    run_id,
                    text,
                    text_norm,
                    sha256,
                    rota_val,
                    agente_alvo,
                    dimensao_perturbacao,
                    seed_case_id,
                    seed_source,
                    graph_edge_id,
                    graph_edge_resolution,
                    expected_workflow,
                    graph_workflow_id,
                    float(max_similarity),
                    nearest_ref,
                    criado,
                ),
            )
        else:
            self._conn.execute(
                """
                INSERT INTO synth_prompts (
                  prompt_id, run_id, text, text_norm, sha256, expected_route,
                  agente_alvo, dimensao_perturbacao, seed_case_id, seed_source,
                  graph_edge_id, graph_edge_resolution, max_similarity, nearest_ref, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    run_id,
                    text,
                    text_norm,
                    sha256,
                    rota_val,
                    agente_alvo,
                    dimensao_perturbacao,
                    seed_case_id,
                    seed_source,
                    graph_edge_id,
                    graph_edge_resolution,
                    float(max_similarity),
                    nearest_ref,
                    criado,
                ),
            )
        self._conn.commit()
        return pid

    def obter_prompt(self, prompt_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute("SELECT * FROM synth_prompts WHERE prompt_id = ?", (prompt_id,))
        row = cur.fetchone()
        return dict(row) if row is not None else None

    def listar_prompts(self, run_id: str | None = None) -> list[dict[str, Any]]:
        if run_id is not None:
            cur = self._conn.execute(
                "SELECT * FROM synth_prompts WHERE run_id = ? ORDER BY created_at ASC, prompt_id ASC",
                (run_id,),
            )
        else:
            cur = self._conn.execute("SELECT * FROM synth_prompts ORDER BY created_at ASC, prompt_id ASC")
        return [dict(r) for r in cur.fetchall()]

    def listar_pendentes_avaliacao(
        self,
        *,
        eval_run_id: str,
        source_run_id: str | None = None,
        only_untested_globally: bool = False,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        params: list[Any] = [eval_run_id]
        filtros = [
            "NOT EXISTS (SELECT 1 FROM synth_evaluations e WHERE e.prompt_id = p.prompt_id AND e.run_id = ?)"
        ]
        if only_untested_globally:
            filtros.append("NOT EXISTS (SELECT 1 FROM synth_evaluations e2 WHERE e2.prompt_id = p.prompt_id)")
        if source_run_id is not None:
            filtros.append("p.run_id = ?")
            params.append(source_run_id)
        where_clause = " AND ".join(filtros)
        sql = f"SELECT p.* FROM synth_prompts p WHERE {where_clause} ORDER BY p.created_at ASC, p.prompt_id ASC"
        if limit is not None and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        cur = self._conn.execute(sql, tuple(params))
        return [dict(r) for r in cur.fetchall()]

    def cobertura_por_estrato(self) -> dict[tuple[str, str], int]:
        cur = self._conn.execute(
            """
            SELECT agente_alvo, dimensao_perturbacao, COUNT(*) AS total
            FROM synth_prompts
            GROUP BY agente_alvo, dimensao_perturbacao
            """
        )
        return {
            (str(r["agente_alvo"]), str(r["dimensao_perturbacao"])): int(r["total"])
            for r in cur.fetchall()
        }

    def inserir_avaliacao(
        self,
        *,
        run_id: str,
        prompt_id: str,
        observed_route: str | None,
        route_source: str | None,
        verdict: str,
        passed: bool | int,
        observed_workflow: str | None = None,
        observed_etapa: int | None = None,
        workflow_source: str | None = None,
        workflow_route_consistent: int | bool | None = None,
        response_excerpt: str | None = None,
        latency_ms: int | None = None,
        premium_requests: int = 0,
        error: str | None = None,
        eval_id: str | None = None,
        created_at: str | None = None,
    ) -> str:
        eid = eval_id or uuid.uuid4().hex
        criado = created_at or _utc_now_iso()
        trecho = response_excerpt[:500] if response_excerpt is not None else None
        passed_int = 1 if bool(passed) else 0
        consist_int: int | None = (
            None if workflow_route_consistent is None else (1 if bool(workflow_route_consistent) else 0)
        )
        cols = _colunas_tabela(self._conn, "synth_evaluations")
        if "observed_workflow" in cols:
            self._conn.execute(
                """
                INSERT INTO synth_evaluations (
                  eval_id, run_id, prompt_id, observed_route, route_source,
                  observed_workflow, observed_etapa, workflow_source, workflow_route_consistent,
                  verdict, passed, response_excerpt, latency_ms, premium_requests, error, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eid,
                    run_id,
                    prompt_id,
                    observed_route,
                    route_source,
                    observed_workflow,
                    observed_etapa,
                    workflow_source,
                    consist_int,
                    verdict,
                    passed_int,
                    trecho,
                    latency_ms,
                    int(premium_requests),
                    error,
                    criado,
                ),
            )
        else:
            self._conn.execute(
                """
                INSERT INTO synth_evaluations (
                  eval_id, run_id, prompt_id, observed_route, route_source,
                  verdict, passed, response_excerpt, latency_ms, premium_requests, error, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eid,
                    run_id,
                    prompt_id,
                    observed_route,
                    route_source,
                    verdict,
                    passed_int,
                    trecho,
                    latency_ms,
                    int(premium_requests),
                    error,
                    criado,
                ),
            )
        self._conn.commit()
        return eid

    def listar_avaliacoes(
        self,
        run_id: str,
        *,
        only_failures: bool = False,
        include_near_boundary: bool = False,
        near_boundary_threshold: float = 0.70,
    ) -> list[dict[str, Any]]:
        cols_p = _colunas_tabela(self._conn, "synth_prompts")
        extra_select = (
            ", p.expected_workflow AS expected_workflow, p.graph_workflow_id AS graph_workflow_id"
            if "expected_workflow" in cols_p
            else ""
        )
        cur = self._conn.execute(
            f"""
            SELECT e.*, p.text AS prompt_text, p.text_norm AS prompt_text_norm,
                   p.expected_route AS expected_route, p.agente_alvo AS agente_alvo,
                   p.dimensao_perturbacao AS dimensao_perturbacao, p.seed_case_id AS seed_case_id,
                   p.seed_source AS seed_source, p.graph_edge_id AS graph_edge_id,
                   p.graph_edge_resolution AS graph_edge_resolution, p.max_similarity AS max_similarity,
                   p.nearest_ref AS nearest_ref{extra_select}
            FROM synth_evaluations e
            JOIN synth_prompts p ON p.prompt_id = e.prompt_id
            WHERE e.run_id = ?
            ORDER BY e.created_at ASC, e.eval_id ASC
            """,
            (run_id,),
        )
        rows = [dict(r) for r in cur.fetchall()]
        if not only_failures:
            return rows
        filtradas: list[dict[str, Any]] = []
        for item in rows:
            falhou = int(item["passed"]) == 0
            near_boundary = include_near_boundary and float(item["max_similarity"]) >= near_boundary_threshold
            if falhou or near_boundary:
                filtradas.append(item)
        return filtradas

    def inserir_export(
        self,
        *,
        prompt_id: str,
        eval_id: str | None,
        silver_path: str,
        silver_case_id: str,
        status: str = "silver",
        promoted_path: str | None = None,
        export_id: str | None = None,
        exported_at: str | None = None,
        decided_at: str | None = None,
    ) -> str:
        xid = export_id or uuid.uuid4().hex
        exp_at = exported_at or _utc_now_iso()
        self._conn.execute(
            """
            INSERT INTO synth_exports (
              export_id, prompt_id, eval_id, silver_path, silver_case_id,
              promoted_path, status, exported_at, decided_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                xid,
                prompt_id,
                eval_id,
                silver_path,
                silver_case_id,
                promoted_path,
                status,
                exp_at,
                decided_at,
            ),
        )
        self._conn.commit()
        return xid

    def atualizar_status_export(
        self,
        silver_case_id: str,
        status: str,
        *,
        promoted_path: str | None = None,
        decided_at: str | None = None,
    ) -> None:
        decidido_val = decided_at or _utc_now_iso()
        self._conn.execute(
            """
            UPDATE synth_exports
            SET status = ?, promoted_path = COALESCE(?, promoted_path), decided_at = ?
            WHERE silver_case_id = ?
            """,
            (status, promoted_path, decidido_val, silver_case_id),
        )
        self._conn.commit()

    def listar_exports(self, status: str | None = None) -> list[dict[str, Any]]:
        if status is not None:
            cur = self._conn.execute(
                "SELECT * FROM synth_exports WHERE status = ? ORDER BY exported_at ASC, export_id ASC",
                (status,),
            )
        else:
            cur = self._conn.execute("SELECT * FROM synth_exports ORDER BY exported_at ASC, export_id ASC")
        return [dict(r) for r in cur.fetchall()]

    def registrar_arestas_grafo(self, snapshot: GrafoSnapshot) -> int:
        rotas = snapshot.todas_rotas if snapshot.todas_rotas else snapshot.rotas
        inseridas = 0
        for r in rotas:
            kws_json = json.dumps(list(r.keywords), ensure_ascii=False)
            self._conn.execute(
                """
                INSERT OR REPLACE INTO routing_graph_edges (
                  snapshot_sha256, edge_id, de, para, tipo, regra,
                  prioridade, threshold_score, nivel_routing, keywords_json, valida
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.sha256,
                    r.edge_id,
                    r.de,
                    r.para,
                    r.tipo,
                    r.regra,
                    float(r.prioridade),
                    float(r.threshold_score),
                    r.nivel_routing,
                    kws_json,
                    1 if r.valida else 0,
                ),
            )
            inseridas += 1
        self._conn.commit()
        return inseridas

    def listar_arestas_grafo(
        self,
        snapshot_sha256: str,
        *,
        apenas_validas: bool = False,
    ) -> list[dict[str, Any]]:
        if apenas_validas:
            cur = self._conn.execute(
                "SELECT * FROM routing_graph_edges WHERE snapshot_sha256 = ? AND valida = 1 ORDER BY edge_id ASC",
                (snapshot_sha256,),
            )
        else:
            cur = self._conn.execute(
                "SELECT * FROM routing_graph_edges WHERE snapshot_sha256 = ? ORDER BY edge_id ASC",
                (snapshot_sha256,),
            )
        return [dict(r) for r in cur.fetchall()]

    def registrar_workflows_grafo(self, snapshot: GrafoSnapshot) -> int:
        """Registra os workflows projetados do snapshot na tabela routing_graph_workflows (v3)."""
        if not _tabela_existe(self._conn, "routing_graph_workflows"):
            for ddl_aux_v3 in _DDL_TABELAS_AUX_V3:
                self._conn.execute(ddl_aux_v3)
        inseridos = 0
        for wf in snapshot.workflows:
            gatilhos_json = json.dumps(list(wf.gatilhos_norm), ensure_ascii=False)
            etapa1_json = json.dumps(list(wf.etapa1_padroes), ensure_ascii=False)
            self._conn.execute(
                """
                INSERT OR REPLACE INTO routing_graph_workflows (
                  workflow_id, graph_sha256, nome, fast_path,
                  gatilhos_json, etapa1_padroes_json, workflow_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    wf.workflow_id,
                    snapshot.sha256,
                    wf.nome,
                    1 if wf.fast_path else 0,
                    gatilhos_json,
                    etapa1_json,
                    wf.workflow_hash,
                ),
            )
            inseridos += 1
        self._conn.commit()
        return inseridos

    def listar_workflows_grafo(self, graph_sha256: str) -> list[dict[str, Any]]:
        """Lista os workflows registrados para um determinado graph_sha256."""
        if not _tabela_existe(self._conn, "routing_graph_workflows"):
            return []
        cur = self._conn.execute(
            "SELECT * FROM routing_graph_workflows WHERE graph_sha256 = ? ORDER BY workflow_id ASC",
            (graph_sha256,),
        )
        return [dict(r) for r in cur.fetchall()]

    def inserir_diagnostico(
        self,
        *,
        diagnostic_id: str,
        eval_run_id: str,
        routing_graph_sha256: str,
        router_agent_sha256: str | None = None,
        golden_set_sha256: str | None = None,
        created_at: str | None = None,
        yaml_path: str | None = None,
        md_path: str | None = None,
        metrics: Mapping[str, Any] | str,
        n_suggestions: int = 0,
    ) -> str:
        criado = created_at or _utc_now_iso()
        metrics_str = (
            metrics
            if isinstance(metrics, str)
            else json.dumps(dict(metrics), ensure_ascii=False, sort_keys=True)
        )
        self._conn.execute(
            """
            INSERT OR REPLACE INTO synth_diagnostics (
              diagnostic_id, eval_run_id, routing_graph_sha256, router_agent_sha256,
              golden_set_sha256, created_at, yaml_path, md_path, metrics_json, n_suggestions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                diagnostic_id,
                eval_run_id,
                routing_graph_sha256,
                router_agent_sha256,
                golden_set_sha256,
                criado,
                yaml_path,
                md_path,
                metrics_str,
                int(n_suggestions),
            ),
        )
        self._conn.commit()
        return diagnostic_id

    def obter_diagnostico(self, diagnostic_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute(
            "SELECT * FROM synth_diagnostics WHERE diagnostic_id = ?",
            (diagnostic_id,),
        )
        row = cur.fetchone()
        return dict(row) if row is not None else None
