"""
incident_model.py — Modelo e validador canônico de incidentes de workflows.

Converte dados brutos de erro e exceções em um documento canônico
validado contra docs/schemas/workflow-incident.schema.json.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    jsonschema = None
    Draft202012Validator = None

from tools.incident_recorder.secret_scrubber import scrub_data

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "workflow-incident.schema.json"


def get_incident_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class WorkflowIncident:
    """Representa um incidente formal de workflow com sanitização e validação."""

    def __init__(
        self,
        workflow_id: str,
        workflow_name: str,
        agent_id: str,
        step_index: int,
        step_name: str,
        severity: str,
        category: str,
        symptom: str,
        error_type: str,
        error_message: str,
        session_id: str | None = None,
        stack_trace: str | None = None,
        tool_call: dict[str, Any] | None = None,
        target_project: str | None = None,
        target_files: list[str] | None = None,
        active_skill: str | None = None,
        status: str = "OPEN",
        retry_count: int = 0,
        action_taken: str | None = None,
        root_cause: str | None = None,
        successful_patch: str | None = None,
        lesson_learned: str | None = None,
        pruned_at: str | None = None,
        incident_id: str | None = None,
        timestamp: str | None = None,
        sync_status: str = "PENDING_SYNC",
        target_backend: str = "supabase",
    ):
        self.incident_id = incident_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.session_id = session_id or "session-default"
        self.agent_id = agent_id
        self.step_index = step_index
        self.step_name = step_name
        self.severity = severity
        self.category = category
        self.symptom = symptom
        self.error_type = error_type
        self.error_message = error_message
        self.stack_trace = stack_trace
        self.tool_call = tool_call
        self.target_project = target_project
        self.target_files = target_files or []
        self.active_skill = active_skill
        self.status = status
        self.retry_count = retry_count
        self.action_taken = action_taken
        self.root_cause = root_cause
        self.successful_patch = successful_patch
        self.lesson_learned = lesson_learned
        self.pruned_at = pruned_at
        self.sync_status = sync_status
        self.target_backend = target_backend

    def to_dict(self) -> dict[str, Any]:
        """Gera o documento canônico sanitizado em formato dict."""
        doc = {
            "schemaVersion": "1.0.0",
            "incidentId": self.incident_id,
            "timestamp": self.timestamp,
            "workflowId": self.workflow_id,
            "workflowName": self.workflow_name,
            "sessionId": self.session_id,
            "agentId": self.agent_id,
            "stepIndex": self.step_index,
            "stepName": self.step_name,
            "severity": self.severity,
            "category": self.category,
            "symptom": self.symptom,
            "errorDetails": {
                "errorType": self.error_type,
                "message": self.error_message,
            },
            "resolution": {
                "status": self.status,
                "retryCount": self.retry_count,
            },
            "syncMetadata": {
                "syncStatus": self.sync_status,
                "targetBackend": self.target_backend,
            },
        }

        if self.stack_trace:
            doc["errorDetails"]["stackTrace"] = self.stack_trace
        if self.tool_call:
            doc["errorDetails"]["toolCall"] = self.tool_call
        if self.action_taken:
            doc["resolution"]["actionTaken"] = self.action_taken
        if self.root_cause:
            doc["resolution"]["rootCause"] = self.root_cause
        if self.successful_patch:
            doc["resolution"]["successfulPatch"] = self.successful_patch
        if self.lesson_learned:
            doc["resolution"]["lessonLearned"] = self.lesson_learned
        if self.pruned_at:
            doc["resolution"]["prunedAt"] = self.pruned_at

        context = {}
        if self.target_project:
            context["targetProject"] = self.target_project
        if self.target_files:
            context["targetFiles"] = self.target_files
        if self.active_skill:
            context["activeSkill"] = self.active_skill
        if context:
            doc["context"] = context

        # Aplica sanitização em todo o payload antes de retornar
        return scrub_data(doc)

    def validate(self) -> None:
        """Valida o documento contra o JSON Schema canônico."""
        if Draft202012Validator is None:
            # Fallback estrutural leve caso jsonschema não esteja instalado
            doc = self.to_dict()
            required = [
                "schemaVersion", "incidentId", "timestamp", "workflowId",
                "workflowName", "agentId", "stepIndex", "severity",
                "category", "symptom", "errorDetails", "resolution", "syncMetadata"
            ]
            for req in required:
                if req not in doc:
                    raise ValueError(f"Campo obrigatório ausente no incidente: {req}")
            return
        schema = get_incident_schema()
        validator = Draft202012Validator(schema)
        doc = self.to_dict()
        validator.validate(doc)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowIncident:
        """Reconstrói uma instância de WorkflowIncident a partir de um dicionário canônico."""
        error_details = data.get("errorDetails", {})
        resolution = data.get("resolution", {})
        context = data.get("context", {})
        sync_meta = data.get("syncMetadata", {})

        return cls(
            workflow_id=data.get("workflowId", "UNKNOWN_WORKFLOW"),
            workflow_name=data.get("workflowName", "UNKNOWN_WORKFLOW"),
            agent_id=data.get("agentId", "unknown-agent"),
            step_index=data.get("stepIndex", 0),
            step_name=data.get("stepName", "unknown-step"),
            severity=data.get("severity", "MEDIUM"),
            category=data.get("category", "RUNTIME_EXCEPTION"),
            symptom=data.get("symptom", "Sintoma não especificado"),
            error_type=error_details.get("errorType", "UnknownError"),
            error_message=error_details.get("message", "Sem mensagem de erro"),
            session_id=data.get("sessionId"),
            stack_trace=error_details.get("stackTrace"),
            tool_call=error_details.get("toolCall"),
            target_project=context.get("targetProject"),
            target_files=context.get("targetFiles"),
            active_skill=context.get("activeSkill"),
            status=resolution.get("status", "OPEN"),
            retry_count=resolution.get("retryCount", 0),
            action_taken=resolution.get("actionTaken"),
            root_cause=resolution.get("rootCause"),
            successful_patch=resolution.get("successfulPatch"),
            lesson_learned=resolution.get("lessonLearned"),
            pruned_at=resolution.get("prunedAt"),
            incident_id=data.get("incidentId"),
            timestamp=data.get("timestamp"),
            sync_status=sync_meta.get("syncStatus", "PENDING_SYNC"),
            target_backend=sync_meta.get("targetBackend", "supabase"),
        )

