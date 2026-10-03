"""Testes de integracao da Fase 5 (T6/PR-6 e T8/PR-8) -- Wiring de governanca e telemetria.

Valida:
1. Sessao nova com prompt canonico aciona `preparar_turno`/`avaliar_transicao`
   e persiste workflow/agente via `session_store.atualizar_estado_governanca`.
2. Segundo turno da mesma sessao, sem deriva, NAO re-chama `governance.rotear`
   (reuso do workflow persistido -- CA-04).
3. `TransicaoInvalidaError` (via `ResultadoTransicao(sucesso=False, ...)`)
   nunca gera HTTP 500 -- sempre HTTP 200 com texto controlado (CA-05).
4. Com `gateway_governance_permissions=False` (default): `permission_handler`
   repassado a `_real_or_stub_completion`/`_real_or_stub_stream` continua
   sendo `_conservative_permission_handler` (RK-06).
5. Com `gateway_governance_permissions=True`: `permission_handler` passa a ser
   um wrapper distinto que delega a `PermissionPolicyStub.autorizar_escrita`.
6. Spans `governance.route` e `governance.workflow_transition` emitidos em sessao nova.
7. Banner 'Agente Ativo:' presente no system_message repassado ao SDK (e2e).
8. Telemetria e2e: 3 spans emitidos com `gen_ai.agent.name` dinamico correspondente ao agente roteado.
9. CA-03: span `governance.route` com atributos nao-nulos por workflow.
10. CA-09: Fail-fast no startup com grafo invalido (log CRITICAL + GraphValidationError)
    e inicializacao normal com grafo valido.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import local_chat_gateway.api.routes as routes_module
import local_chat_gateway.app as app_module
import local_chat_gateway.config as config_module
import local_chat_gateway.governance as governance
import local_chat_gateway.governance_pipeline as governance_pipeline
import local_chat_gateway.session_store as session_store_module
from local_chat_gateway.api.schemas import ChatCompletion, ChatCompletionChoice, ChatMessage, Usage
from local_chat_gateway.config import Settings
from local_chat_gateway.governance import GraphValidationError
from local_chat_gateway.session_store import SessionStore

_PROMPT_BUG = "Tenho um bug no sistema, pode me ajudar?"


def _stub_completion() -> ChatCompletion:
    return ChatCompletion(
        id="chatcmpl-test",
        created=0,
        model="deep-agents/router",
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content="ok"),
                finish_reason="stop",
            )
        ],
        usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
    )


@pytest.fixture
def telemetry_settings(fake_settings: Settings) -> Settings:
    """Configuracao com endpoint de telemetria ativo para testes OTLP."""
    return fake_settings.model_copy(
        update={"otel_exporter_otlp_endpoint": "http://otel-collector:4318"}
    )


@pytest.fixture
def telemetry_app(
    telemetry_settings: Settings, session_store: SessionStore
) -> FastAPI:
    """FastAPI app configurada com telemetria ativa."""
    application = app_module.create_app(settings=telemetry_settings)
    application.dependency_overrides[config_module.get_settings] = (
        lambda: telemetry_settings
    )
    application.dependency_overrides[
        session_store_module.get_session_store
    ] = lambda: session_store
    return application


@pytest.fixture
def telemetry_client(telemetry_app: FastAPI) -> Generator[TestClient, None, None]:
    """TestClient com telemetria ativada."""
    with TestClient(telemetry_app) as test_client:
        yield test_client


def test_sessao_nova_prompt_canonico_roteia_e_persiste(
    client: TestClient,
    session_store: SessionStore,
    auth_headers: dict[str, str],
) -> None:
    """(a) Sessao nova + prompt canonico -> DecisaoTurno nao nula, workflow persistido."""
    body = {"model": "deep-agents/router", "messages": [{"role": "user", "content": _PROMPT_BUG}], "stream": False}
    response = client.post(
        "/v1/chat/completions", json=body, headers={**auth_headers, "x-session-id": "sess-a"}
    )

    assert response.status_code == 200
    record = session_store.get_session("sess-a")
    assert record is not None
    assert record.workflow == "WORKFLOW-BUG-FIX"
    assert record.agente_ativo == "bug-triage"
    assert record.fase == "em_workflow"


def test_segundo_turno_sem_deriva_nao_roteia_novamente(
    client: TestClient,
    session_store: SessionStore,
    auth_headers: dict[str, str],
) -> None:
    """(b) 2o turno da mesma sessao, sem deriva -> governance.rotear NAO e chamado de novo."""
    headers = {**auth_headers, "x-session-id": "sess-b"}
    body = {"model": "deep-agents/router", "messages": [{"role": "user", "content": _PROMPT_BUG}], "stream": False}

    first = client.post("/v1/chat/completions", json=body, headers=headers)
    assert first.status_code == 200

    first_record = session_store.get_session("sess-b")
    assert first_record is not None
    assert first_record.workflow == "WORKFLOW-BUG-FIX"

    with patch(
        "local_chat_gateway.governance.rotear", wraps=governance.rotear
    ) as mock_rotear:
        second = client.post("/v1/chat/completions", json=body, headers=headers)
        assert second.status_code == 200
        mock_rotear.assert_not_called()


def test_transicao_invalida_retorna_200_texto_controlado(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """(c) TransicaoInvalidaError (via ResultadoTransicao.sucesso=False) -> HTTP 200, nunca 500."""
    body = {"model": "deep-agents/router", "messages": [{"role": "user", "content": _PROMPT_BUG}], "stream": False}

    with patch(
        "local_chat_gateway.governance_pipeline.avaliar_transicao",
        return_value=governance_pipeline.ResultadoTransicao(
            sucesso=False, sessao_atualizada=None, erro="transicao simulada invalida"
        ),
    ):
        response = client.post(
            "/v1/chat/completions", json=body, headers={**auth_headers, "x-session-id": "sess-c"}
        )

    assert response.status_code == 200
    payload = response.json()
    assert "transicao simulada invalida" in payload["choices"][0]["message"]["content"]


def test_permission_handler_conservador_quando_flag_off(
    app: FastAPI,
    auth_headers: dict[str, str],
) -> None:
    """(d) gateway_governance_permissions=False (default) -> permission_handler inalterado."""
    with TestClient(app) as client:
        captured: dict[str, Any] = {}

        async def _fake_completion(*args: Any, **kwargs: Any) -> ChatCompletion:
            captured.update(kwargs)
            return _stub_completion()

        body = {"model": "deep-agents/router", "messages": [{"role": "user", "content": _PROMPT_BUG}], "stream": False}
        with patch.object(routes_module, "_real_or_stub_completion", new=AsyncMock(side_effect=_fake_completion)):
            response = client.post(
                "/v1/chat/completions", json=body, headers={**auth_headers, "x-session-id": "sess-d"}
            )

        assert response.status_code == 200
        assert captured["permission_handler"] is routes_module._conservative_permission_handler


def test_permission_handler_governanca_quando_flag_on(
    fake_settings: Settings,
    session_store: SessionStore,
    auth_headers: dict[str, str],
) -> None:
    """(e) gateway_governance_permissions=True -> permission_handler delega a PermissionPolicyStub."""
    settings_on = fake_settings.model_copy(update={"gateway_governance_permissions": True})
    application = app_module.create_app(settings=settings_on)
    application.dependency_overrides[config_module.get_settings] = lambda: settings_on
    application.dependency_overrides[session_store_module.get_session_store] = (
        lambda: session_store
    )

    with TestClient(application) as client:
        captured: dict[str, Any] = {}

        async def _fake_completion(*args: Any, **kwargs: Any) -> ChatCompletion:
            captured.update(kwargs)
            return _stub_completion()

        body = {"model": "deep-agents/router", "messages": [{"role": "user", "content": _PROMPT_BUG}], "stream": False}
        with patch.object(routes_module, "_real_or_stub_completion", new=AsyncMock(side_effect=_fake_completion)):
            response = client.post(
                "/v1/chat/completions", json=body, headers={**auth_headers, "x-session-id": "sess-e"}
            )

        assert response.status_code == 200
        handler = captured["permission_handler"]
        assert handler is not routes_module._conservative_permission_handler
        # Leitura continua liberada incondicionalmente (mesma allowlist read-only).
        assert handler("read_file", {}) is True
        # Escrita bloqueada em modo read_only (default) -- 4 guardas de PermissionPolicyStub.
        assert handler("write_file", {"path": str(Path(settings_on.projects_root_path or "/workspaces") / "x.py")}) is False


# --- Novos testes Fase 5 (T8/PR-8) ---


def test_sessao_nova_emite_spans_route_e_workflow_transition(
    telemetry_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """1. Sessao nova emite spans governance.route e governance.workflow_transition."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        body = {
            "model": "deep-agents/router",
            "messages": [{"role": "user", "content": _PROMPT_BUG}],
            "stream": False,
        }
        response = telemetry_client.post(
            "/v1/chat/completions",
            json=body,
            headers={**auth_headers, "x-session-id": "sess-spans-route-wf"},
        )
        assert response.status_code == 200

        deadline = time.time() + 1.0
        while mock_dispatch.call_count < 2 and time.time() < deadline:
            time.sleep(0.01)

        span_names: set[str] = set()
        deep_agents_attrs: dict[str, dict[str, Any]] = {}

        for call in mock_dispatch.call_args_list:
            payload = call[0][1]
            resource_spans = payload.get("resourceSpans", [])
            for rs in resource_spans:
                for ss in rs.get("scopeSpans", []):
                    for sp in ss.get("spans", []):
                        name = sp.get("name")
                        if name in {"governance.route", "governance.workflow_transition"}:
                            span_names.add(name)
                            attrs = {
                                attr["key"]: attr["value"]
                                for attr in sp.get("attributes", [])
                                if attr.get("key", "").startswith("deep_agents.")
                            }
                            deep_agents_attrs[name] = attrs

        assert {"governance.route", "governance.workflow_transition"}.issubset(span_names)
        assert len(deep_agents_attrs.get("governance.route", {})) > 0
        assert len(deep_agents_attrs.get("governance.workflow_transition", {})) > 0

        for span_name, attrs in deep_agents_attrs.items():
            for key, val in attrs.items():
                assert val is not None, f"Atributo {key} em {span_name} e nulo"


def test_montar_contexto_banner_presente_no_system_message_e2e(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """2. Banner 'Agente Ativo:' presente no system_message repassado ao SDK."""
    captured: dict[str, Any] = {}

    async def _fake_completion(*args: Any, **kwargs: Any) -> ChatCompletion:
        captured.update(kwargs)
        return _stub_completion()

    body = {
        "model": "deep-agents/router",
        "messages": [{"role": "user", "content": _PROMPT_BUG}],
        "stream": False,
    }
    with patch.object(
        routes_module, "_real_or_stub_completion", new=AsyncMock(side_effect=_fake_completion)
    ):
        response = client.post(
            "/v1/chat/completions",
            json=body,
            headers={**auth_headers, "x-session-id": "sess-banner"},
        )

    assert response.status_code == 200
    assert "system_message" in captured
    system_msg = captured["system_message"]
    assert isinstance(system_msg, str)
    assert "Agente Ativo:" in system_msg


def test_telemetria_e2e_tres_spans_mais_invoke_agent_com_agent_name_dinamico(
    telemetry_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """3. Telemetria e2e: 3 spans no lote com gen_ai.agent.name dinamico igual ao roteado."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        body = {
            "model": "deep-agents/router",
            "messages": [{"role": "user", "content": _PROMPT_BUG}],
            "stream": False,
        }
        response = telemetry_client.post(
            "/v1/chat/completions",
            json=body,
            headers={**auth_headers, "x-session-id": "sess-telemetry-e2e"},
        )
        assert response.status_code == 200

        deadline = time.time() + 1.0
        while mock_dispatch.call_count < 3 and time.time() < deadline:
            time.sleep(0.01)

        captured_spans: list[dict[str, Any]] = []
        for call in mock_dispatch.call_args_list:
            payload = call[0][1]
            for rs in payload.get("resourceSpans", []):
                for ss in rs.get("scopeSpans", []):
                    captured_spans.extend(ss.get("spans", []))

        span_names = {sp.get("name") for sp in captured_spans}
        assert "governance.route" in span_names
        assert "governance.workflow_transition" in span_names

        chat_spans = [
            sp for sp in captured_spans
            if sp.get("name") == "chat: deep-agents/router"
        ]
        assert len(chat_spans) >= 1
        chat_span = chat_spans[0]
        attrs = {
            attr["key"]: attr["value"].get("stringValue")
            for attr in chat_span.get("attributes", [])
        }
        # O prompt de bug roteia para "bug-triage", nao para "agent-router"
        assert attrs.get("gen_ai.agent.name") == "bug-triage"


@pytest.mark.parametrize(
    ("prompt", "workflow_esperado", "agente_esperado"),
    [
        ("Tenho um bug no sistema", "WORKFLOW-BUG-FIX", "bug-triage"),
        ("Preciso de analise tecnica de arquitetura", "WORKFLOW-TECHNICAL-ANALYSIS", "deep-search"),
    ],
)
def test_ca03_span_route_atributos_nao_nulos_por_workflow(
    telemetry_client: TestClient,
    auth_headers: dict[str, str],
    prompt: str,
    workflow_esperado: str,
    agente_esperado: str,
) -> None:
    """CA-03: span governance.route com atributos nao-nulos por workflow.

    Nota: Subconjunto representativo da fixture reduzida de teste valid_graph.yaml
    ('WORKFLOW-BUG-FIX' e 'WORKFLOW-TECHNICAL-ANALYSIS'), nao os 8 workflows canonicos completos.
    """
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        body = {
            "model": "deep-agents/router",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        session_id = f"sess-ca03-{workflow_esperado.lower()}"
        response = telemetry_client.post(
            "/v1/chat/completions",
            json=body,
            headers={**auth_headers, "x-session-id": session_id},
        )
        assert response.status_code == 200

        deadline = time.time() + 1.0
        while mock_dispatch.call_count < 1 and time.time() < deadline:
            time.sleep(0.01)

        route_spans: list[dict[str, Any]] = []
        for call in mock_dispatch.call_args_list:
            payload = call[0][1]
            for rs in payload.get("resourceSpans", []):
                for ss in rs.get("scopeSpans", []):
                    for sp in ss.get("spans", []):
                        if sp.get("name") == "governance.route":
                            route_spans.append(sp)

        assert len(route_spans) >= 1
        route_span = route_spans[0]
        attrs = {
            attr["key"]: (
                attr["value"].get("stringValue")
                if "stringValue" in attr["value"]
                else attr["value"].get("doubleValue", attr["value"].get("boolValue"))
            )
            for attr in route_span.get("attributes", [])
        }

        assert attrs.get("deep_agents.routing.workflow") == workflow_esperado
        assert attrs.get("deep_agents.routing.escolhido") == agente_esperado
        assert attrs.get("deep_agents.routing.nivel") is not None
        assert attrs.get("deep_agents.routing.score") is not None
        assert attrs.get("deep_agents.routing.drift_detectado") is not None


def test_create_app_fail_fast_grafo_invalido(
    fake_settings: Settings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """CA-09: Fail-fast de startup com grafo invalido e log estruturado CRITICAL."""
    fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"
    grafo_invalido = fixtures_dir / "grafo_invalido_aresta_no_inexistente.yaml"

    settings_invalid = fake_settings.model_copy(
        update={"governance_graph_path": grafo_invalido}
    )
    application = app_module.create_app(settings=settings_invalid)

    with caplog.at_level(logging.CRITICAL):
        with pytest.raises(GraphValidationError) as exc_info:
            with TestClient(application):
                pass

    assert "no-fantasma" in str(exc_info.value)
    matching_records = [
        rec for rec in caplog.records
        if "graph_path=" in rec.message and "schema_path=" in rec.message and "causa=" in rec.message
    ]
    assert len(matching_records) >= 1
    assert any(rec.levelno >= logging.ERROR for rec in matching_records)


def test_create_app_startup_ok_com_grafo_valido(
    fake_settings: Settings,
) -> None:
    """CA-09: Startup bem-sucedido com grafo valido popula app.state."""
    fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"
    grafo_valido = fixtures_dir / "valid_graph.yaml"

    settings_valid = fake_settings.model_copy(
        update={"governance_graph_path": grafo_valido}
    )
    application = app_module.create_app(settings=settings_valid)

    with TestClient(application):
        assert application.state.grafo is not None
        assert application.state.tabela_transicao is not None
        assert application.state.catalogo is not None
