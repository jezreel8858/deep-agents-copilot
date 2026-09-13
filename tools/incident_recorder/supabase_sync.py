"""
supabase_sync.py — Worker de sincronização e purge de incidentes com Supabase.

Utiliza a biblioteca padrão do Python (urllib) para comunicação com a API REST PostgREST,
garantindo portabilidade sem dependências adicionais (zero pip installs externos).
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request

from tools.incident_recorder.sqlite_sink import SqliteIncidentSink
from tools.incident_recorder.supabase_formatter import format_for_supabase, format_supabase_delete_request

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"


def load_env_file() -> None:
    """Lê variáveis do arquivo .env caso existam e não estejam no os.environ."""
    if not ENV_FILE.exists():
        return
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val
    except Exception:
        pass


def get_supabase_config() -> tuple[Optional[str], Optional[str]]:
    """Recupera URL e API Key do Supabase do ambiente ou .env."""
    load_env_file()
    url = os.environ.get("SUPABASE_URL")
    key = (
            os.environ.get("SUPABASE_KEY")
            or os.environ.get("SUPABASE_ANON_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    )
    return url, key


class SupabaseSyncClient:
    """Cliente de sincronização Outbox entre o SQLite local e o Supabase."""

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        sink: Optional[SqliteIncidentSink] = None,
    ):
        env_url, env_key = get_supabase_config()
        resolved_url = env_url if supabase_url is None else supabase_url
        resolved_key = env_key if supabase_key is None else supabase_key
        self.url = (resolved_url or "").rstrip("/")
        self.key = resolved_key or ""
        self.sink = sink or SqliteIncidentSink()

    @property
    def is_configured(self) -> bool:
        """Indica se as credenciais do Supabase estão configuradas."""
        return bool(self.url and self.key)

    def sync_pending(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Lê incidentes com sync_status = 'PENDING_SYNC' do SQLite local e transmite para o Supabase.
        Retorna relatório da sincronização.
        """
        if not self.is_configured:
            return {
                "success": False,
                "synced_count": 0,
                "error": "Supabase não configurado. Defina SUPABASE_URL e SUPABASE_KEY no .env",
            }

        pending = self.sink.get_pending_sync(limit=batch_size)
        if not pending:
            return {"success": True, "synced_count": 0, "message": "Nenhum incidente pendente de sync."}

        # Formata o lote para as colunas relacionais + JSONB do Supabase
        payload_batch = [format_for_supabase(item["document"]) for item in pending]
        incident_ids = [item["incident_id"] for item in pending]

        endpoint = f"{self.url}/rest/v1/workflow_incidents"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",  # Upsert idempotente no Supabase
        }

        try:
            req_data = json.dumps(payload_batch, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(endpoint, data=req_data, headers=headers, method="POST")

            with urllib.request.urlopen(req, timeout=10) as resp:
                status_code = resp.getcode()
                if status_code in (200, 201):
                    synced_at = datetime.now(timezone.utc).isoformat()
                    self.sink.mark_synced(incident_ids, synced_at=synced_at, backend="supabase")
                    return {
                        "success": True,
                        "synced_count": len(incident_ids),
                        "incident_ids": incident_ids,
                        "synced_at": synced_at,
                    }
                else:
                    return {
                        "success": False,
                        "synced_count": 0,
                        "error": f"Supabase retornou HTTP {status_code}",
                    }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            return {"success": False, "synced_count": 0, "error": f"HTTP {e.code}: {err_body}"}
        except Exception as e:
            return {"success": False, "synced_count": 0, "error": str(e)}

    def purge_from_supabase(self, incident_ids: List[str]) -> Dict[str, Any]:
        """
        Envia requisição DELETE para liberar espaço no Supabase para incidentes já resolvidos.
        """
        if not self.is_configured:
            return {"success": False, "purged_count": 0, "error": "Supabase não configurado."}

        if not incident_ids:
            return {"success": True, "purged_count": 0, "message": "Nenhum ID para purgar."}

        req_spec = format_supabase_delete_request(incident_ids)
        endpoint = f"{self.url}{req_spec['path']}?{urllib.parse.urlencode(req_spec['params'])}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Prefer": req_spec["headers"]["Prefer"],
        }

        try:
            req = urllib.request.Request(endpoint, headers=headers, method="DELETE")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {
                    "success": True,
                    "purged_count": len(incident_ids),
                    "status_code": resp.getcode(),
                }
        except Exception as e:
            return {"success": False, "purged_count": 0, "error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI de Sincronização de Incidentes com Supabase")
    parser.add_argument("--status", action="store_true", help="Exibe status da configuração e pendências")
    parser.add_argument("--sync", action="store_true", help="Executa sincronização em lote de incidentes pendentes")
    parser.add_argument("--purge", action="store_true", help="Purga incidentes resolvidos localmente e no Supabase")
    args = parser.parse_args()

    client = SupabaseSyncClient()

    if args.status or (not args.sync and not args.purge):
        url, key = get_supabase_config()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 Status da Sincronização Supabase")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Configurado: {'✅ Sim' if client.is_configured else '❌ Não'}")
        print(f"Supabase URL: {url or 'Não definida'}")
        print(f"API Key: {'[CONFIGURADA]' if key else 'Não definida'}")
        sink = SqliteIncidentSink()
        pending = sink.get_pending_sync()
        total = sink.count_incidents()
        print(f"Incidentes locais: {total}")
        print(f"Pendentes de sync: {len(pending)}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if args.sync:
        print("🚀 Sincronizando incidentes com Supabase...")
        res = client.sync_pending()
        print(json.dumps(res, indent=2, ensure_ascii=False))

    if args.purge:
        print("🧹 Purgando incidentes resolvidos para liberar espaço...")
        purged_ids = client.sink.purge_learned_incidents()
        print(f"Incidentes purgados do SQLite: {len(purged_ids)}")
        if purged_ids and client.is_configured:
            res_remote = client.purge_from_supabase(purged_ids)
            print("Purge no Supabase:", json.dumps(res_remote, indent=2))


if __name__ == "__main__":
    main()

