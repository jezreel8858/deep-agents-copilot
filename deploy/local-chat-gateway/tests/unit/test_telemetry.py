"""Testes unitários para `telemetry` (emissão OTLP GenAI Semconv v1.41+)."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

from local_chat_gateway.telemetry import (
    _build_otlp_payload,
    emit_chat_trace,
    emit_governance_health_check_span,
    emit_governance_route_span,
    emit_governance_workflow_transition_span,
)


def test_build_otlp_payload_estrutura_semconv() -> None:
    """Valida geracao correta de payload OTLP JSON com Semconv v1.41+."""
    payload = _build_otlp_payload(
        trace_id="trace123",
        root_span_id="span123",
        session_id="session-test",
        prompt="Pergunta do usuario",
        response_text="Resposta do modelo",
        tools_executed=["view", "grep"],
        start_time_ns=1000,
        end_time_ns=2000,
    )

    resource_spans = payload["resourceSpans"]
    assert len(resource_spans) == 1
    spans = resource_spans[0]["scopeSpans"][0]["spans"]

    # 1 root span (chat) + 2 child spans (view, grep) = 3 spans
    assert len(spans) == 3

    # Root span
    root = spans[0]
    assert root["name"] == "chat: deep-agents/router"
    attrs = {a["key"]: a["value"]["stringValue"] for a in root["attributes"]}
    assert attrs["gen_ai.operation.name"] == "chat"
    assert attrs["gen_ai.conversation.id"] == "session-test"
    assert attrs["gen_ai.agent.name"] == "agent-router"
    assert attrs["gen_ai.provider.name"] == "github-copilot"

    # Child spans de tool
    tool_view = spans[1]
    assert tool_view["name"] == "execute_tool: view"
    assert tool_view["parentSpanId"] == "span123"
    view_attrs = {a["key"]: a["value"]["stringValue"] for a in tool_view["attributes"]}
    assert view_attrs["gen_ai.tool.name"] == "view"

    tool_grep = spans[2]
    assert tool_grep["name"] == "execute_tool: grep"
    assert tool_grep["parentSpanId"] == "span123"


@pytest.mark.asyncio
async def test_emit_chat_trace_noop_quando_endpoint_vazio() -> None:
    """Quando endpoint e None ou vazio, emit_chat_trace nao faz nada."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_chat_trace(
            None,
            session_id="sessao",
            prompt="oi",
            response_text="ola",
            tools_executed=[],
            start_time_ns=1000,
        )
        mock_dispatch.assert_not_called()


@pytest.mark.asyncio
async def test_emit_chat_trace_dispara_quando_endpoint_presente() -> None:
    """Quando endpoint esta configurado, despacha payload para o worker."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_chat_trace(
            "http://otel-collector:4318",
            session_id="sessao",
            prompt="oi",
            response_text="ola",
            tools_executed=["view"],
            start_time_ns=1000,
        )
        # Permite que o executor do event loop rode
        await asyncio.sleep(0.01)
        mock_dispatch.assert_called_once()
        args = mock_dispatch.call_args[0]
        assert args[0] == "http://otel-collector:4318"
        assert "resourceSpans" in args[1]


def test_resolve_candidate_endpoints_traduz_localhost() -> None:
    """Valida resolucao de 127.0.0.1 para otel-collector e host.docker.internal."""
    from local_chat_gateway.telemetry import _resolve_candidate_endpoints

    cand = _resolve_candidate_endpoints("http://127.0.0.1:4318")
    assert cand == [
        "http://otel-collector:4318",
        "http://host.docker.internal:4318",
        "http://127.0.0.1:4318",
    ]

    cand_ext = _resolve_candidate_endpoints("https://meu-coletor.remoto:4318")
    assert cand_ext == ["https://meu-coletor.remoto:4318"]


def test_build_otlp_payload_usa_agent_name_dinamico_quando_fornecido() -> None:
    """T7/PR-7: `agent_name` parametrizavel substitui o hard-code de
    `gen_ai.agent.name`."""
    payload = _build_otlp_payload(
        trace_id="trace123",
        root_span_id="span123",
        session_id="session-test",
        prompt="Pergunta do usuario",
        response_text="Resposta do modelo",
        tools_executed=[],
        start_time_ns=1000,
        end_time_ns=2000,
        agent_name="python-feature-developer",
    )

    root = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    attrs = {a["key"]: a["value"]["stringValue"] for a in root["attributes"]}
    assert attrs["gen_ai.agent.name"] == "python-feature-developer"


def test_build_otlp_payload_default_agent_name_preserva_regressao() -> None:
    """Regressao (T7/PR-7): sem `agent_name`, o default continua "agent-router"."""
    payload = _build_otlp_payload(
        trace_id="trace123",
        root_span_id="span123",
        session_id="session-test",
        prompt="oi",
        response_text="ola",
        tools_executed=[],
        start_time_ns=1000,
        end_time_ns=2000,
    )

    root = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    attrs = {a["key"]: a["value"]["stringValue"] for a in root["attributes"]}
    assert attrs["gen_ai.agent.name"] == "agent-router"


@pytest.mark.asyncio
async def test_emit_chat_trace_repassa_agent_name_dinamico() -> None:
    """T7/PR-7: `emit_chat_trace` aceita `agent_name` e propaga ao payload."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_chat_trace(
            "http://otel-collector:4318",
            session_id="sessao",
            prompt="oi",
            response_text="ola",
            tools_executed=[],
            start_time_ns=1000,
            agent_name="security-reviewer",
        )
        await asyncio.sleep(0.01)
        mock_dispatch.assert_called_once()
        payload = mock_dispatch.call_args[0][1]
        root = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
        attrs = {a["key"]: a["value"]["stringValue"] for a in root["attributes"]}
        assert attrs["gen_ai.agent.name"] == "security-reviewer"


# ---------------------------------------------------------------------------
# T7/PR-7 — spans customizados de governanca (deep_agents.*)
# ---------------------------------------------------------------------------


def _atributos_do_unico_span(payload: dict[str, object]) -> dict[str, object]:
    resource_spans = payload["resourceSpans"]
    span = resource_spans[0]["scopeSpans"][0]["spans"][0]  # type: ignore[index]
    return {a["key"]: a["value"] for a in span["attributes"]}


@pytest.mark.asyncio
async def test_emit_governance_health_check_span_emite_atributos_deep_agents() -> None:
    """Valida atributos `deep_agents.health.*` do span `governance.health_check`."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_governance_health_check_span(
            "http://otel-collector:4318",
            session_id="healthz",
            graph_ok=True,
            sdk_token_ok=False,
            collector_ok=True,
            budget_ok=True,
        )
        await asyncio.sleep(0.01)
        mock_dispatch.assert_called_once()
        payload = mock_dispatch.call_args[0][1]
        span = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
        assert span["name"] == "governance.health_check"
        attrs = _atributos_do_unico_span(payload)
        assert attrs["deep_agents.health.graph_ok"] == {"boolValue": True}
        assert attrs["deep_agents.health.sdk_token_ok"] == {"boolValue": False}
        assert attrs["deep_agents.health.collector_ok"] == {"boolValue": True}
        assert attrs["deep_agents.health.budget_ok"] == {"boolValue": True}


@pytest.mark.asyncio
async def test_emit_governance_route_span_emite_atributos_deep_agents() -> None:
    """Valida atributos `deep_agents.routing.*` do span `governance.route`."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_governance_route_span(
            "http://otel-collector:4318",
            session_id="sessao-1",
            escolhido="python-feature-developer",
            workflow="WORKFLOW-FEATURE-DEVELOPMENT",
            nivel="rule_based",
            score=0.95,
            drift_detectado=False,
        )
        await asyncio.sleep(0.01)
        mock_dispatch.assert_called_once()
        payload = mock_dispatch.call_args[0][1]
        span = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
        assert span["name"] == "governance.route"
        attrs = _atributos_do_unico_span(payload)
        assert attrs["deep_agents.routing.escolhido"] == {
            "stringValue": "python-feature-developer"
        }
        assert attrs["deep_agents.routing.workflow"] == {
            "stringValue": "WORKFLOW-FEATURE-DEVELOPMENT"
        }
        assert attrs["deep_agents.routing.nivel"] == {"stringValue": "rule_based"}
        assert attrs["deep_agents.routing.score"] == {"doubleValue": 0.95}
        assert attrs["deep_agents.routing.drift_detectado"] == {"boolValue": False}


@pytest.mark.asyncio
async def test_emit_governance_route_span_omite_nivel_score_quando_none() -> None:
    """Quando nao houve re-roteamento, `nivel`/`score` (`None`) sao omitidos."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_governance_route_span(
            "http://otel-collector:4318",
            session_id="sessao-1",
            escolhido="python-feature-developer",
            workflow=None,
            nivel=None,
            score=None,
            drift_detectado=False,
        )
        await asyncio.sleep(0.01)
        payload = mock_dispatch.call_args[0][1]
        attrs = _atributos_do_unico_span(payload)
        assert "deep_agents.routing.nivel" not in attrs
        assert "deep_agents.routing.score" not in attrs
        assert "deep_agents.routing.workflow" not in attrs


@pytest.mark.asyncio
async def test_emit_workflow_transition_span_atributos_deep_agents() -> None:
    """Valida atributos `deep_agents.workflow.*` do span
    `governance.workflow_transition`."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_governance_workflow_transition_span(
            "http://otel-collector:4318",
            session_id="sessao-1",
            fase_origem="router",
            fase_destino="em_workflow",
            etapa=1,
            aprovacao_checkpoint=False,
        )
        await asyncio.sleep(0.01)
        mock_dispatch.assert_called_once()
        payload = mock_dispatch.call_args[0][1]
        span = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
        assert span["name"] == "governance.workflow_transition"
        attrs = _atributos_do_unico_span(payload)
        assert attrs["deep_agents.workflow.fase_origem"] == {"stringValue": "router"}
        assert attrs["deep_agents.workflow.fase_destino"] == {
            "stringValue": "em_workflow"
        }
        assert attrs["deep_agents.workflow.etapa"] == {"intValue": "1"}
        assert attrs["deep_agents.workflow.aprovacao_checkpoint"] == {
            "boolValue": False
        }
        assert "error.type" not in attrs


@pytest.mark.asyncio
async def test_emit_workflow_transition_span_inclui_error_type_na_falha() -> None:
    """Quando a transicao falha, `error.type` (namespace padrao OTel) e incluido."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_governance_workflow_transition_span(
            "http://otel-collector:4318",
            session_id="sessao-1",
            fase_origem="em_workflow",
            fase_destino="em_workflow",
            etapa=2,
            aprovacao_checkpoint=False,
            error_type="TransicaoInvalidaError",
        )
        await asyncio.sleep(0.01)
        payload = mock_dispatch.call_args[0][1]
        attrs = _atributos_do_unico_span(payload)
        assert attrs["error.type"] == {"stringValue": "TransicaoInvalidaError"}


@pytest.mark.asyncio
async def test_emit_governance_health_check_span_noop_quando_endpoint_vazio() -> None:
    """Sem `endpoint` configurado, nenhum span customizado e despachado (no-op)."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_governance_health_check_span(
            None,
            session_id="healthz",
            graph_ok=True,
            sdk_token_ok=True,
            collector_ok=True,
            budget_ok=True,
        )
        mock_dispatch.assert_not_called()


# ---------------------------------------------------------------------------
# Bug real de producao (2026-10-01): "muitos dados ausentes no Langfuse" —
# spans customizados (scope.name="local_chat_gateway") apareciam com
# Input/Output/Cost/Provided Model Name sempre "—" no dashboard, enquanto o
# span nativo do SDK (scope.name="github.copilot") exibia esses dados
# corretamente. Causa raiz confirmada via pesquisa da documentacao oficial
# do Langfuse (OTel ingestion v4, langfuse.com/integrations/native/
# opentelemetry): (1) `gen_ai.prompt`/`gen_ai.completion` como string plana
# NAO e o formato que o parser `extractInputAndOutput` reconhece (ele espera
# `gen_ai.prompt.<n>.*` indexado, convencao OpenLLMetry/Traceloop, ou os
# atributos nativos Langfuse); (2) sem `gen_ai.request.model`, o span nunca e
# classificado como "generation" (fica como "span" generico, sem Cost/Model);
# (3) para instrumentacao MANUAL (nosso caso), a documentacao recomenda
# explicitamente `langfuse.observation.input`/`langfuse.observation.output`/
# `langfuse.observation.type` -- atributos que SEMPRE tem precedencia sobre
# as convencoes `gen_ai.*` genericas.
# ---------------------------------------------------------------------------


def test_build_otlp_payload_inclui_atributos_langfuse_observation_no_root() -> None:
    """Root span (chat) inclui `langfuse.observation.input/output/type` e
    `gen_ai.request.model`/`gen_ai.response.finish_reason` -- necessarios
    para o Langfuse classificar o span como Generation com Input/Output/
    Model Name populados."""
    payload = _build_otlp_payload(
        trace_id="trace123",
        root_span_id="span123",
        session_id="session-test",
        prompt="Pergunta do usuario",
        response_text="Resposta do modelo",
        tools_executed=[],
        start_time_ns=1000,
        end_time_ns=2000,
        model="claude-sonnet-5",
    )

    root = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    attrs = {a["key"]: a["value"] for a in root["attributes"]}
    assert attrs["langfuse.observation.type"] == {"stringValue": "generation"}
    assert attrs["langfuse.observation.input"] == {
        "stringValue": "Pergunta do usuario"
    }
    assert attrs["langfuse.observation.output"] == {
        "stringValue": "Resposta do modelo"
    }
    assert attrs["gen_ai.request.model"] == {"stringValue": "claude-sonnet-5"}
    assert attrs["gen_ai.response.finish_reason"] == {"stringValue": "stop"}


def test_build_otlp_payload_model_default_quando_nao_informado() -> None:
    """Sem `model` explicito (SDK usa default interno), `gen_ai.request.model`
    e emitido como "auto" -- nunca omitido (precisamos do marcador de
    Generation mesmo sem saber o modelo real resolvido pelo SDK)."""
    payload = _build_otlp_payload(
        trace_id="trace123",
        root_span_id="span123",
        session_id="session-test",
        prompt="oi",
        response_text="ola",
        tools_executed=[],
        start_time_ns=1000,
        end_time_ns=2000,
    )
    root = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    attrs = {a["key"]: a["value"] for a in root["attributes"]}
    assert attrs["gen_ai.request.model"] == {"stringValue": "auto"}


def test_build_otlp_payload_tool_spans_marcados_como_tool_type() -> None:
    """Spans filhos de tool recebem `langfuse.observation.type=tool`."""
    payload = _build_otlp_payload(
        trace_id="trace123",
        root_span_id="span123",
        session_id="session-test",
        prompt="oi",
        response_text="ola",
        tools_executed=["view"],
        start_time_ns=1000,
        end_time_ns=2000,
    )
    tool_span = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][1]
    attrs = {a["key"]: a["value"] for a in tool_span["attributes"]}
    assert attrs["langfuse.observation.type"] == {"stringValue": "tool"}


@pytest.mark.asyncio
async def test_emit_chat_trace_repassa_model_para_payload() -> None:
    """`emit_chat_trace` aceita `model` e propaga a `gen_ai.request.model`."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_chat_trace(
            "http://otel-collector:4318",
            session_id="sessao",
            prompt="oi",
            response_text="ola",
            tools_executed=[],
            start_time_ns=1000,
            model="claude-sonnet-5",
        )
        await asyncio.sleep(0.01)
        mock_dispatch.assert_called_once()
        payload = mock_dispatch.call_args[0][1]
        root = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
        attrs = {a["key"]: a["value"] for a in root["attributes"]}
        assert attrs["gen_ai.request.model"] == {"stringValue": "claude-sonnet-5"}


def test_governance_custom_spans_marcados_como_event_type() -> None:
    """Spans customizados de governanca (`_build_custom_span_payload`) recebem
    `langfuse.observation.type=event` -- decisoes instantaneas, nao generations
    nem spans de duracao real."""
    from local_chat_gateway.telemetry import _build_custom_span_payload

    payload = _build_custom_span_payload(
        trace_id="trace123",
        span_id="span123",
        session_id="sessao-1",
        span_name="governance.route",
        attributes=[],
        start_time_ns=1000,
        end_time_ns=1000,
    )
    span = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
    attrs = {a["key"]: a["value"] for a in span["attributes"]}
    assert attrs["langfuse.observation.type"] == {"stringValue": "event"}


# ---------------------------------------------------------------------------
# Bug real de producao (2026-10-01, Addendum 4): spans emitidos a partir de
# requisicoes REAIS via /v1/chat/completions (governance.route/workflow_
# transition/chat root) eram perdidos de forma intermitente -- testes
# manuais isolados (script asyncio.run() dedicado, fora do processo Uvicorn)
# sempre funcionavam, mas o mesmo codigo rodando dentro do servidor
# persistente falhava sem erro visivel. Causa suspeita: `loop.run_in_
# executor(...)` descartado sem nenhuma referencia mantida (anti-padrao
# documentado do proprio asyncio -- "the event loop only keeps a weak
# reference"; Future pode ser coletado pelo GC antes de concluir). Corrigido
# com `_schedule_background_dispatch`, que retem o Future em um set
# module-level ate sua conclusao (`add_done_callback`).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_emit_chat_trace_retem_referencia_forte_do_future_ate_concluir() -> None:
    """`emit_chat_trace` mantem o Future do despacho em `_background_dispatch_
    tasks` ate sua conclusao (nunca descartado sem referencia, eliminando risco
    de coleta prematura pelo GC)."""
    from local_chat_gateway import telemetry as telemetry_module

    telemetry_module._background_dispatch_tasks.clear()

    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        mock_dispatch.return_value = None
        await emit_chat_trace(
            "http://otel-collector:4318",
            session_id="sessao",
            prompt="oi",
            response_text="ola",
            tools_executed=[],
            start_time_ns=1000,
        )
        # Imediatamente apos o await, o Future deve estar retido no set
        # (ainda nao concluido -- a thread do executor roda em paralelo).
        assert len(telemetry_module._background_dispatch_tasks) == 1

        await asyncio.sleep(0.05)
        # Apos a conclusao, o callback deve te-lo removido do set (sem
        # vazamento de memoria indefinido).
        assert len(telemetry_module._background_dispatch_tasks) == 0


@pytest.mark.asyncio
async def test_emit_governance_route_span_retem_referencia_forte_do_future() -> None:
    """Mesma protecao de retencao de referencia aplicada aos spans
    customizados de governanca (`_emit_custom_governance_span`)."""
    from local_chat_gateway import telemetry as telemetry_module

    telemetry_module._background_dispatch_tasks.clear()

    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        mock_dispatch.return_value = None
        await emit_governance_route_span(
            "http://otel-collector:4318",
            session_id="sessao-1",
            escolhido="bug-triage",
            workflow="WORKFLOW-BUG-FIX",
            nivel="rule_based",
            score=0.9,
            drift_detectado=False,
        )
        assert len(telemetry_module._background_dispatch_tasks) == 1
        await asyncio.sleep(0.05)
        assert len(telemetry_module._background_dispatch_tasks) == 0




# ---------------------------------------------------------------------------
# Addendum 8 (2026-10-01) — bug real de producao: cada funcao de emissao de
# span (`emit_chat_trace`/`_emit_custom_governance_span`) gerava seu PROPRIO
# `trace_id = uuid.uuid4().hex`, fragmentando um unico turno de usuario em
# ate 4 traces desconectados no Langfuse (o span com input/output real do
# prompt, `chat: deep-agents/router`, ficava isolado numa arvore orfa,
# desconectado de `governance.route`/`governance.workflow_transition`).
# Correcao: `trace_id` passa a ser parametro OPCIONAL repassavel pelo
# chamador (gerado uma unica vez por turno em `routes.chat_completions`),
# com fallback para gerar um novo UUID quando nao fornecido (compatibilidade
# retroativa com chamadores existentes, ex.: os testes acima deste modulo).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_caracterizacao_emit_chat_trace_sem_trace_id_gera_ids_distintos() -> None:
    """Teste de caracterizacao (safety net): SEM `trace_id` explicito, duas
    chamadas distintas de `emit_chat_trace` continuam gerando `trace_id`
    diferentes entre si (fallback de compatibilidade retroativa preservado)."""
    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_chat_trace(
            "http://otel-collector:4318",
            session_id="sessao",
            prompt="oi",
            response_text="ola",
            tools_executed=[],
            start_time_ns=1000,
        )
        await emit_chat_trace(
            "http://otel-collector:4318",
            session_id="sessao",
            prompt="oi de novo",
            response_text="ola de novo",
            tools_executed=[],
            start_time_ns=2000,
        )
        await asyncio.sleep(0.01)
        assert mock_dispatch.call_count == 2
        payload_1 = mock_dispatch.call_args_list[0][0][1]
        payload_2 = mock_dispatch.call_args_list[1][0][1]
        trace_id_1 = payload_1["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["traceId"]
        trace_id_2 = payload_2["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["traceId"]
        assert trace_id_1 != trace_id_2


@pytest.mark.asyncio
async def test_emit_chat_trace_e_governance_spans_compartilham_trace_id_do_turno() -> None:
    """Red -> Green (Addendum 8): quando `emit_chat_trace`,
    `emit_governance_route_span` e `emit_governance_workflow_transition_span`
    sao chamadas para o MESMO turno com o MESMO `trace_id` explicito, o
    `traceId` despachado nos 3 payloads OTLP deve ser identico -- unificando
    a arvore de trace no Langfuse."""
    turno_trace_id = "turno-unificado-" + "a" * 16

    with patch("local_chat_gateway.telemetry._dispatch_http") as mock_dispatch:
        await emit_governance_route_span(
            "http://otel-collector:4318",
            session_id="sessao-turno",
            escolhido="python-feature-developer",
            workflow="WORKFLOW-FEATURE-DEVELOPMENT",
            nivel="rule_based",
            score=0.95,
            drift_detectado=False,
            trace_id=turno_trace_id,
        )
        await emit_governance_workflow_transition_span(
            "http://otel-collector:4318",
            session_id="sessao-turno",
            fase_origem="router",
            fase_destino="em_workflow",
            etapa=1,
            aprovacao_checkpoint=False,
            trace_id=turno_trace_id,
        )
        await emit_chat_trace(
            "http://otel-collector:4318",
            session_id="sessao-turno",
            prompt="oi",
            response_text="ola",
            tools_executed=[],
            start_time_ns=1000,
            trace_id=turno_trace_id,
        )
        await asyncio.sleep(0.01)
        assert mock_dispatch.call_count == 3

        trace_ids = set()
        for chamada in mock_dispatch.call_args_list:
            payload = chamada[0][1]
            span = payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
            trace_ids.add(span["traceId"])

        assert trace_ids == {turno_trace_id}
