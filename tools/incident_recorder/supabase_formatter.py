"""
supabase_formatter.py — Formatador de payloads de incidentes para Supabase (PostgreSQL JSONB).

Converte documentos canônicos de incidentes no formato exato esperado pela tabela
workflow_incidents do Supabase via API PostgREST, incluindo suporte a inserção e exclusão (purge).
"""
from __future__ import annotations

from typing import Any, Dict, List


def format_for_supabase(incident_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeia o documento canônico da IR de incidente para as colunas da tabela Supabase:
    - incident_id (UUID)
    - workflow_id (TEXT)
    - workflow_name (TEXT)
    - session_id (TEXT)
    - agent_id (TEXT)
    - step_index (INTEGER)
    - step_name (TEXT)
    - severity (TEXT)
    - category (TEXT)
    - status (TEXT)
    - created_at (TIMESTAMPTZ)
    - document_payload (JSONB — documento completo com rootCause e lessonLearned)
    """
    return {
        "incident_id": incident_dict["incidentId"],
        "workflow_id": incident_dict["workflowId"],
        "workflow_name": incident_dict["workflowName"],
        "session_id": incident_dict.get("sessionId", "session-default"),
        "agent_id": incident_dict["agentId"],
        "step_index": incident_dict["stepIndex"],
        "step_name": incident_dict["stepName"],
        "severity": incident_dict["severity"],
        "category": incident_dict["category"],
        "status": incident_dict["resolution"]["status"],
        "created_at": incident_dict["timestamp"],
        "document_payload": incident_dict,  # Salvo diretamente como JSONB no PostgreSQL
    }


def format_supabase_delete_request(incident_ids: List[str]) -> Dict[str, Any]:
    """
    Gera a especificação da requisição PostgREST para exclusão em lote no Supabase:
    DELETE /rest/v1/workflow_incidents?incident_id=in.(id1,id2,...)
    Permite liberar espaço excluindo incidentes cujas lições já foram assimiladas.
    """
    ids_param = f"in.({','.join(incident_ids)})"
    return {
        "method": "DELETE",
        "path": "/rest/v1/workflow_incidents",
        "params": {"incident_id": ids_param},
        "headers": {
            "Prefer": "return=representation",
        },
    }
