"""
supabase_formatter.py — Formatador de payloads de incidentes para Supabase (PostgreSQL JSONB).

Converte documentos canônicos de incidentes no formato exato esperado pela tabela
workflow_incidents do Supabase via API PostgREST.
"""
from __future__ import annotations

from typing import Any, Dict


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
    - document_payload (JSONB — documento completo para consultas analíticas)
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

