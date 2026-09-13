"""
test_workflow_incident_persistence.py — Suíte de testes automatizados para persistência local e nuvem de incidentes.

Cobre as garantias de:
- REQ-001 / REQ-003: Validação do JSON Schema canônico de incidentes
- REQ-002 / RNF-001 / RNF-002: Persistência local em SQLite WAL com JSON1
- REQ-004: Cobertura de categorias de incidentes (Tool Failure, Circuit Breakers, etc.)
- REQ-005 / REQ-006: Outbox sync e formatação nativa para Supabase (PostgreSQL JSONB)
- REQ-007: Resiliência Fail-Safe contra falhas de banco
- RNF-004: Sanitização automática de credenciais e segredos (SecretScrubber)
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import pytest
import jsonschema
from jsonschema import Draft202012Validator

from tools.incident_recorder.incident_model import WorkflowIncident, get_incident_schema
from tools.incident_recorder.secret_scrubber import scrub_data, scrub_string
from tools.incident_recorder.sqlite_sink import SqliteIncidentSink
from tools.incident_recorder.supabase_formatter import format_for_supabase

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "workflow-incident.schema.json"


# ── Testes de Validade do Schema (REQ-003) ──────────────────────────────────

def test_workflow_incident_schema_is_valid_draft202012():
    """Valida que o schema de incidentes é um JSON Schema sintaticamente válido Draft 2020-12"""
    schema = get_incident_schema()
    Draft202012Validator.check_schema(schema)


def test_incident_model_generates_valid_schema_document():
    """Valida que um incidente padrão gerado pelo modelo passa 100% no schema"""
    incident = WorkflowIncident(
        workflow_id="WF-BUG-2026-001",
        workflow_name="WORKFLOW-BUG-FIX",
        agent_id="specialist-bug-fixer",
        step_index=4,
        step_name="Correção Cirúrgica & Diff",
        severity="HIGH",
        category="TOOL_FAILURE",
        symptom="Comando de compilação falhou com erro de sintaxe",
        error_type="CompilationError",
        error_message="Cannot find symbol: method getId()",
        stack_trace="at com.exemplo.Service.run(Service.java:42)",
        tool_call={"toolName": "run_in_terminal", "arguments": {"command": "mvn test"}, "exitCode": 1},
        target_project="meu-projeto",
        target_files=["src/main/java/Service.java"],
        active_skill="spring-boot-implementation-patterns",
        status="RETRYING",
        retry_count=1,
        action_taken="Ajustado import da classe de modelo",
    )
    # Não deve levantar jsonschema.ValidationError
    incident.validate()
    doc = incident.to_dict()
    assert doc["schemaVersion"] == "1.0.0"
    assert doc["severity"] == "HIGH"
    assert doc["category"] == "TOOL_FAILURE"
    assert doc["errorDetails"]["errorType"] == "CompilationError"


def test_incident_model_rejects_invalid_severity_or_category():
    """Valida que o schema rejeita valores inválidos de severidade ou categoria"""
    schema = get_incident_schema()
    validator = Draft202012Validator(schema)

    invalid_doc = {
        "schemaVersion": "1.0.0",
        "incidentId": "id-123",
        "timestamp": "2026-09-12T10:00:00Z",
        "workflowId": "WF-001",
        "workflowName": "WORKFLOW-BUG-FIX",
        "agentId": "bug-fixer",
        "stepIndex": 1,
        "severity": "INVALID_SEVERITY",  # Deve ser LOW/MEDIUM/HIGH/CRITICAL
        "category": "UNKNOWN_CAT",
        "symptom": "falha",
        "errorDetails": {"errorType": "Error", "message": "msg"},
        "resolution": {"status": "OPEN", "retryCount": 0},
        "syncMetadata": {"syncStatus": "PENDING_SYNC"},
    }

    errors = list(validator.iter_errors(invalid_doc))
    assert len(errors) > 0, "Documento com severidade e categoria inválidas deveria falhar"


# ── Testes de Sanitização de Segredos (RNF-004) ────────────────────────────

def test_secret_scrubber_masks_sensitive_tokens():
    """Valida que API keys, JWTs e passwords são mascarados com [REDACTED]"""
    raw_text = "Erro ao conectar com Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.abc e token sk-123456789012345678901234 e ghp_123456789012345678901234567890123456"
    sanitized = scrub_string(raw_text)
    assert "Bearer [REDACTED_JWT]" in sanitized
    assert "[REDACTED_API_KEY]" in sanitized
    assert "[REDACTED_GITHUB_TOKEN]" in sanitized
    assert "sk-123456" not in sanitized


def test_secret_scrubber_masks_dict_fields_recursively():
    """Valida mascaramento recursivo de chaves como password, secret, token em dicionários"""
    raw_dict = {
        "user": "admin",
        "password": "superSecretPassword123",
        "config": {
            "api_key": "secret-api-key-value",
            "normal_field": "public_data",
        },
        "items": [
            {"token": "my-secret-token"},
            {"safe": 42}
        ]
    }
    cleaned = scrub_data(raw_dict)
    assert cleaned["password"] == "[REDACTED]"
    assert cleaned["config"]["api_key"] == "[REDACTED]"
    assert cleaned["config"]["normal_field"] == "public_data"
    assert cleaned["items"][0]["token"] == "[REDACTED]"
    assert cleaned["items"][1]["safe"] == 42


# ── Testes de Persistência Local SQLite (REQ-002 / RNF-001 / RNF-002) ──────

def test_sqlite_sink_record_and_query_incident():
    """Valida criação do banco, inserção de incidente e consulta de pendentes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_incidents.db"
        sink = SqliteIncidentSink(db_path=db_path)

        incident = WorkflowIncident(
            workflow_id="WF-TEST-001",
            workflow_name="WORKFLOW-TECHNICAL-ANALYSIS",
            agent_id="code-knowledge-graph",
            step_index=2,
            step_name="Mapeamento de Chamadas",
            severity="MEDIUM",
            category="CIRCUIT_BREAKER",
            symptom="Ciclo de dependências complexo detectado",
            error_type="CycleException",
            error_message="Ciclo entre Pacote A e Pacote B",
        )

        success = sink.record_incident(incident)
        assert success is True
        assert sink.count_incidents("WF-TEST-001") == 1

        pending = sink.get_pending_sync(limit=10)
        assert len(pending) == 1
        assert pending[0]["incident_id"] == incident.incident_id
        assert pending[0]["document"]["workflowName"] == "WORKFLOW-TECHNICAL-ANALYSIS"


def test_sqlite_sink_outbox_mark_synced():
    """Valida atualização do status de PENDING_SYNC para SYNCED (REQ-005)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_incidents.db"
        sink = SqliteIncidentSink(db_path=db_path)

        incident = WorkflowIncident(
            workflow_id="WF-TEST-002",
            workflow_name="WORKFLOW-BUG-FIX",
            agent_id="bug-triage",
            step_index=1,
            step_name="Triagem",
            severity="LOW",
            category="RUNTIME_EXCEPTION",
            symptom="Log trace truncado",
            error_type="LogParseException",
            error_message="Timestamp inválido no log",
        )
        sink.record_incident(incident)

        pending_before = sink.get_pending_sync()
        assert len(pending_before) == 1

        # Marca como sincronizado para o Supabase
        synced = sink.mark_synced([incident.incident_id], synced_at="2026-09-12T11:00:00Z", backend="supabase")
        assert synced is True

        pending_after = sink.get_pending_sync()
        assert len(pending_after) == 0


def test_sqlite_sink_fail_safe_does_not_raise():
    """Valida que falhas internas no SQLite não lançam exception não tratada (REQ-007)"""
    # Passar caminho inválido (diretório como arquivo)
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir)  # Tentativa de usar pasta como DB file gera erro
        sink = SqliteIncidentSink(db_path=db_path)

        incident = WorkflowIncident(
            workflow_id="WF-FAILSAFE",
            workflow_name="WORKFLOW-BUG-FIX",
            agent_id="test",
            step_index=1,
            step_name="test",
            severity="LOW",
            category="TOOL_FAILURE",
            symptom="test",
            error_type="test",
            error_message="test",
        )

        # Não deve lançar exceção
        result = sink.record_incident(incident)
        assert result is False


# ── Testes de Formatação para Supabase (REQ-006) ───────────────────────────

def test_supabase_formatter_maps_jsonb_and_relational_columns():
    """Valida que format_for_supabase gera colunas relacionais + payload JSONB exato"""
    incident = WorkflowIncident(
        workflow_id="WF-SUPABASE-001",
        workflow_name="WORKFLOW-FEATURE-DEVELOPMENT",
        agent_id="tech-solution-architect",
        step_index=3,
        step_name="Blueprint",
        severity="HIGH",
        category="QUALITY_GATE_FAILURE",
        symptom="Contrato OpenAPI inválido",
        error_type="ContractValidationError",
        error_message="Missing 200 response definition",
    )
    doc_dict = incident.to_dict()
    supabase_payload = format_for_supabase(doc_dict)

    assert supabase_payload["incident_id"] == incident.incident_id
    assert supabase_payload["workflow_id"] == "WF-SUPABASE-001"
    assert supabase_payload["workflow_name"] == "WORKFLOW-FEATURE-DEVELOPMENT"
    assert supabase_payload["agent_id"] == "tech-solution-architect"
    assert supabase_payload["severity"] == "HIGH"
    assert supabase_payload["category"] == "QUALITY_GATE_FAILURE"
    assert supabase_payload["status"] == "OPEN"
    # O document_payload deve conter o documento completo em formato dict (JSONB do PostgreSQL)
    assert isinstance(supabase_payload["document_payload"], dict)
    assert supabase_payload["document_payload"]["schemaVersion"] == "1.0.0"



# ── Testes de Aprendizado com Erros e Purge de Espaço (REQ-008 / REQ-009) ───

def test_incident_model_with_lesson_learned_passes_schema():
    """Valida que o documento com lição aprendida e status RESOLVED passa no schema canônico"""
    incident = WorkflowIncident(
        workflow_id="WF-LEARN-001",
        workflow_name="WORKFLOW-FRAMEWORK-MIGRATION",
        agent_id="spring-boot-feature-developer",
        step_index=4,
        step_name="Paridade Funcional",
        severity="HIGH",
        category="TOOL_FAILURE",
        symptom="Import javax.persistence não encontrado no Spring Boot 3",
        error_type="PackageNotFoundError",
        error_message="package javax.persistence does not exist",
        status="RESOLVED",
        root_cause="Spring Boot 3 migrou para Jakarta EE 10",
        successful_patch="Substituído javax.persistence.* por jakarta.persistence.* no pom.xml e classes",
        lesson_learned="No Spring Boot 3+, use sempre jakarta.persistence em vez de javax.persistence",
    )
    incident.validate()
    doc = incident.to_dict()
    assert doc["resolution"]["status"] == "RESOLVED"
    assert doc["resolution"]["rootCause"] == "Spring Boot 3 migrou para Jakarta EE 10"
    assert "jakarta.persistence" in doc["resolution"]["lessonLearned"]


def test_sqlite_sink_resolve_and_find_lessons():
    """Valida o ciclo completo: registrar erro -> resolver com lição -> buscar preventivamente"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_learn.db"
        sink = SqliteIncidentSink(db_path=db_path)

        incident = WorkflowIncident(
            workflow_id="WF-RESOLVE-001",
            workflow_name="WORKFLOW-FRAMEWORK-MIGRATION",
            agent_id="angular-feature-developer",
            step_index=3,
            step_name="Emissão de Componente",
            severity="MEDIUM",
            category="RUNTIME_EXCEPTION",
            symptom="NG0203: inject() must be called from an injection context",
            error_type="AngularInjectionError",
            error_message="inject() called outside constructor or field initializer",
            status="OPEN",
        )
        sink.record_incident(incident)

        # Inicialmente não há lições aprendidas (status OPEN)
        lessons_initial = sink.find_lessons(workflow_name="WORKFLOW-FRAMEWORK-MIGRATION")
        assert len(lessons_initial) == 0

        # Agente corrige e resolve o incidente anexando a lição aprendida
        resolved = sink.resolve_incident(
            incident_id=incident.incident_id,
            root_cause="Chamada de inject() dentro de método assíncrono após await",
            successful_patch="Injetado serviço no topo da classe como campo final",
            lesson_learned="inject() só pode ser invocado no inicializador de campo ou construtor síncrono",
        )
        assert resolved is True

        # Agora a busca preventiva deve encontrar a lição
        lessons = sink.find_lessons(workflow_name="WORKFLOW-FRAMEWORK-MIGRATION", keyword="inject")
        assert len(lessons) == 1
        assert lessons[0]["agent_id"] == "angular-feature-developer"
        assert "construtor" in lessons[0]["lesson_learned"]


def test_sqlite_sink_purge_learned_incidents_frees_space():
    """Valida exclusão de incidentes resolvidos para liberar espaço (REQ-009)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_purge.db"
        sink = SqliteIncidentSink(db_path=db_path)

        inc1 = WorkflowIncident(
            workflow_id="WF-1",
            workflow_name="WORKFLOW-BUG-FIX",
            agent_id="fixer",
            step_index=1,
            step_name="triage",
            severity="LOW",
            category="TOOL_FAILURE",
            symptom="s1",
            error_type="e1",
            error_message="m1",
            status="OPEN",
        )
        inc2 = WorkflowIncident(
            workflow_id="WF-2",
            workflow_name="WORKFLOW-BUG-FIX",
            agent_id="fixer",
            step_index=1,
            step_name="triage",
            severity="LOW",
            category="TOOL_FAILURE",
            symptom="s2",
            error_type="e2",
            error_message="m2",
            status="OPEN",
        )
        sink.record_incident(inc1)
        sink.record_incident(inc2)
        assert sink.count_incidents() == 2

        # Resolve apenas o inc1
        sink.resolve_incident(inc1.incident_id, "root", "patch", "lesson")

        # Purgar incidentes resolvidos
        purged_ids = sink.purge_learned_incidents()
        assert inc1.incident_id in purged_ids
        assert inc2.incident_id not in purged_ids

        # Agora só inc2 permanece no banco
        assert sink.count_incidents() == 1


def test_supabase_formatter_delete_request_generation():
    """Valida geração da requisição PostgREST DELETE para purge no Supabase"""
    from tools.incident_recorder.supabase_formatter import format_supabase_delete_request

    ids_to_purge = ["uuid-1", "uuid-2", "uuid-3"]
    req = format_supabase_delete_request(ids_to_purge)

    assert req["method"] == "DELETE"
    assert req["path"] == "/rest/v1/workflow_incidents"
    assert req["params"]["incident_id"] == "in.(uuid-1,uuid-2,uuid-3)"
    assert req["headers"]["Prefer"] == "return=representation"
