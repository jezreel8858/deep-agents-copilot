"""
sqlite_sink.py — Driver de persistência local em SQLite com suporte a JSON1.

Implementa gravação de incidentes com isolamento transacional, pragmas WAL
e padrão Fail-Safe (nunca interrompe o fluxo do agente em caso de erro de disco).
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Any, Dict, Generator, List, Optional

from tools.incident_recorder.incident_model import WorkflowIncident

DEFAULT_DB_DIR = Path(".workflow-db")
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "incidents.db"
FALLBACK_LOG_PATH = DEFAULT_DB_DIR / "fallback.log"


class SqliteIncidentSink:
    """Repositório local SQLite para gravação de incidentes de workflows."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Gerencia abertura e fechamento estrito de conexões (essencial para Windows)."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Inicializa diretório, arquivo SQLite e DDL com modo WAL."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with self._connection() as conn:
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA synchronous = NORMAL;")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_incidents (
                        incident_id TEXT PRIMARY KEY,
                        workflow_id TEXT NOT NULL,
                        workflow_name TEXT NOT NULL,
                        session_id TEXT,
                        agent_id TEXT NOT NULL,
                        step_index INTEGER NOT NULL,
                        step_name TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        category TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        sync_status TEXT NOT NULL DEFAULT 'PENDING_SYNC',
                        synced_at TEXT,
                        target_backend TEXT DEFAULT 'supabase',
                        document_payload TEXT NOT NULL
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_incidents_workflow ON workflow_incidents(workflow_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_incidents_agent ON workflow_incidents(agent_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_incidents_sync ON workflow_incidents(sync_status);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_incidents_severity ON workflow_incidents(severity);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_incidents_created ON workflow_incidents(created_at);")
                conn.commit()
        except Exception as e:
            self._log_fallback(f"Falha na inicialização do SQLite Sink: {e}")

    def record_incident(self, incident: WorkflowIncident) -> bool:
        """
        Persiste um incidente no banco local.
        Aplica Fail-Safe: retorna True se gravado, False se caiu em fallback.
        """
        try:
            incident.validate()
            payload_dict = incident.to_dict()
            payload_json = json.dumps(payload_dict, ensure_ascii=False)

            with self._connection() as conn:
                conn.execute("""
                    INSERT INTO workflow_incidents (
                        incident_id, workflow_id, workflow_name, session_id,
                        agent_id, step_index, step_name, severity, category,
                        status, created_at, sync_status, target_backend, document_payload
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    incident.incident_id,
                    incident.workflow_id,
                    incident.workflow_name,
                    incident.session_id,
                    incident.agent_id,
                    incident.step_index,
                    incident.step_name,
                    incident.severity,
                    incident.category,
                    incident.status,
                    incident.timestamp,
                    incident.sync_status,
                    incident.target_backend,
                    payload_json
                ))
                conn.commit()
            return True
        except Exception as e:
            self._log_fallback(f"Erro ao registrar incidente {getattr(incident, 'incident_id', 'unknown')}: {e}")
            return False

    def get_pending_sync(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Recupera registros com sync_status = 'PENDING_SYNC'."""
        try:
            with self._connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT incident_id, workflow_id, document_payload
                    FROM workflow_incidents
                    WHERE sync_status = 'PENDING_SYNC'
                    ORDER BY created_at ASC
                    LIMIT ?;
                """, (limit,))
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "incident_id": row["incident_id"],
                        "workflow_id": row["workflow_id"],
                        "document": json.loads(row["document_payload"]),
                    })
                return results
        except Exception as e:
            self._log_fallback(f"Erro ao consultar pendências de sync: {e}")
            return []

    def mark_synced(self, incident_ids: List[str], synced_at: str, backend: str = "supabase") -> bool:
        """Atualiza os registros após sincronização bem-sucedida com a nuvem."""
        if not incident_ids:
            return True
        try:
            with self._connection() as conn:
                placeholders = ",".join("?" for _ in incident_ids)
                conn.execute(f"""
                    UPDATE workflow_incidents
                    SET sync_status = 'SYNCED',
                        synced_at = ?,
                        target_backend = ?
                    WHERE incident_id IN ({placeholders});
                """, [synced_at, backend, *incident_ids])
                conn.commit()
            return True
        except Exception as e:
            self._log_fallback(f"Erro ao marcar sincronizados: {e}")
            return False

    def count_incidents(self, workflow_id: Optional[str] = None) -> int:
        """Retorna o total de incidentes gravados."""
        try:
            with self._connection() as conn:
                if workflow_id:
                    cursor = conn.execute("SELECT count(*) FROM workflow_incidents WHERE workflow_id = ?;", (workflow_id,))
                else:
                    cursor = conn.execute("SELECT count(*) FROM workflow_incidents;")
                return cursor.fetchone()[0]
        except Exception as e:
            self._log_fallback(f"Erro ao contar incidentes: {e}")
            return 0

    def _log_fallback(self, msg: str) -> None:
        """Escreve em arquivo de fallback sem lançar exception (Fail-Safe)."""
        try:
            FALLBACK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(FALLBACK_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[FALLBACK LOG] {msg}\n")
        except Exception:
            pass
