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

    def resolve_incident(
        self,
        incident_id: str,
        root_cause: str,
        successful_patch: str,
        lesson_learned: str,
    ) -> bool:
        """
        Marca um incidente como RESOLVED e anexa a lição aprendida.
        Atualiza o payload JSON e define sync_status = 'PENDING_SYNC' para propagar ao Supabase.
        """
        try:
            with self._connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT document_payload FROM workflow_incidents WHERE incident_id = ?;", (incident_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                doc = json.loads(row["document_payload"])
                doc["resolution"]["status"] = "RESOLVED"
                doc["resolution"]["rootCause"] = root_cause
                doc["resolution"]["successfulPatch"] = successful_patch
                doc["resolution"]["lessonLearned"] = lesson_learned
                doc["syncMetadata"]["syncStatus"] = "PENDING_SYNC"

                conn.execute("""
                    UPDATE workflow_incidents
                    SET status = 'RESOLVED',
                        sync_status = 'PENDING_SYNC',
                        document_payload = ?
                    WHERE incident_id = ?;
                """, (json.dumps(doc, ensure_ascii=False), incident_id))
                conn.commit()
            return True
        except Exception as e:
            self._log_fallback(f"Erro ao resolver incidente {incident_id}: {e}")
            return False

    def find_lessons(
        self,
        category: Optional[str] = None,
        workflow_name: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Recupera lições aprendidas de incidentes resolvidos para injeção preventiva.
        Permite que o agente consulte erros passados antes de cometer a mesma falha.
        """
        try:
            with self._connection() as conn:
                conn.row_factory = sqlite3.Row
                query = "SELECT incident_id, workflow_name, agent_id, category, document_payload FROM workflow_incidents WHERE status = 'RESOLVED'"
                params: List[Any] = []

                if category:
                    query += " AND category = ?"
                    params.append(category)
                if workflow_name:
                    query += " AND workflow_name = ?"
                    params.append(workflow_name)

                query += " ORDER BY created_at DESC LIMIT ?;"
                params.append(limit * 2)  # busca margem maior para filtrar keyword

                cursor = conn.execute(query, params)
                lessons = []
                for row in cursor.fetchall():
                    doc = json.loads(row["document_payload"])
                    resolution = doc.get("resolution", {})
                    lesson_text = resolution.get("lessonLearned")
                    if not lesson_text:
                        continue

                    # Filtro opcional de keyword na mensagem ou lição
                    if keyword:
                        err_msg = doc.get("errorDetails", {}).get("message", "")
                        if keyword.lower() not in lesson_text.lower() and keyword.lower() not in err_msg.lower():
                            continue

                    lessons.append({
                        "incident_id": row["incident_id"],
                        "category": row["category"],
                        "agent_id": row["agent_id"],
                        "symptom": doc.get("symptom"),
                        "root_cause": resolution.get("rootCause"),
                        "lesson_learned": lesson_text,
                        "successful_patch": resolution.get("successfulPatch"),
                    })
                    if len(lessons) >= limit:
                        break
                return lessons
        except Exception as e:
            self._log_fallback(f"Erro ao buscar lições aprendidas: {e}")
            return []

    def purge_learned_incidents(self, incident_ids: Optional[List[str]] = None) -> List[str]:
        """
        Exclui incidentes resolvidos para liberar espaço em disco no SQLite e no Supabase.
        Executa VACUUM no SQLite para desfragmentar e recuperar espaço físico.
        Retorna a lista de IDs purgados para que o adapter envie a exclusão ao Supabase.
        """
        purged_ids: List[str] = []
        try:
            with self._connection() as conn:
                conn.row_factory = sqlite3.Row
                if incident_ids:
                    placeholders = ",".join("?" for _ in incident_ids)
                    cursor = conn.execute(f"SELECT incident_id FROM workflow_incidents WHERE incident_id IN ({placeholders}) AND status = 'RESOLVED';", incident_ids)
                else:
                    # Purga todos os incidentes que já foram resolvidos
                    cursor = conn.execute("SELECT incident_id FROM workflow_incidents WHERE status = 'RESOLVED';")

                purged_ids = [row["incident_id"] for row in cursor.fetchall()]

                if purged_ids:
                    del_placeholders = ",".join("?" for _ in purged_ids)
                    conn.execute(f"DELETE FROM workflow_incidents WHERE incident_id IN ({del_placeholders});", purged_ids)
                    conn.commit()

            # Executa VACUUM para recuperar espaço no arquivo físico
            if purged_ids:
                with self._connection() as conn:
                    conn.execute("VACUUM;")
                    conn.commit()

            return purged_ids
        except Exception as e:
            self._log_fallback(f"Erro ao purgar incidentes resolvidos: {e}")
            return []
