"""telemetry — Emissao OTLP GenAI Semconv v1.41+ para o OTel Collector / Langfuse.

Envia traces assincronos nao-bloqueantes para `OTEL_EXPORTER_OTLP_ENDPOINT`
(/v1/traces). Se o endpoint nao estiver configurado, opera em modo no-op
com zero overhead.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

logger = logging.getLogger(__name__)


def _build_otlp_payload(
    *,
    trace_id: str,
    root_span_id: str,
    session_id: str,
    prompt: str,
    response_text: str,
    tools_executed: list[str],
    start_time_ns: int,
    end_time_ns: int,
    agent_name: str = "agent-router",
    model: str | None = None,
) -> dict[str, Any]:
    """Constroi o payload OTLP JSON (resourceSpans) conforme GenAI Semconv v1.41+.

    Bug real de producao (2026-10-01): adicionado `langfuse.observation.
    input/output/type` -- a documentacao oficial do Langfuse (OTel ingestion
    v4) recomenda esses atributos EXPLICITAMENTE para instrumentacao manual
    (nosso caso), pois eles tem precedencia sobre as convencoes `gen_ai.*`
    genericas e sao a forma garantida de popular Input/Output no dashboard.
    `gen_ai.request.model` tambem e obrigatorio para o span ser classificado
    como "generation" (sem ele, vira um "span" generico sem Cost/Model Name).
    """
    model_atributo = model if model is not None else "auto"
    root_span: dict[str, Any] = {
        "traceId": trace_id,
        "spanId": root_span_id,
        "name": "chat: deep-agents/router",
        "kind": 1,  # SPAN_KIND_INTERNAL
        "startTimeUnixNano": str(start_time_ns),
        "endTimeUnixNano": str(end_time_ns),
        "attributes": [
            {"key": "gen_ai.operation.name", "value": {"stringValue": "chat"}},
            {"key": "gen_ai.agent.name", "value": {"stringValue": agent_name}},
            {"key": "gen_ai.provider.name", "value": {"stringValue": "github-copilot"}},
            {"key": "gen_ai.conversation.id", "value": {"stringValue": session_id}},
            {"key": "gen_ai.request.model", "value": {"stringValue": model_atributo}},
            {
                "key": "gen_ai.response.finish_reason",
                "value": {"stringValue": "stop"},
            },
            {"key": "session.id", "value": {"stringValue": session_id}},
            {"key": "langfuse.session.id", "value": {"stringValue": session_id}},
            {"key": "dac.session_id", "value": {"stringValue": session_id}},
            {
                "key": "langfuse.observation.type",
                "value": {"stringValue": "generation"},
            },
            {"key": "langfuse.observation.input", "value": {"stringValue": prompt[:500]}},
            {
                "key": "langfuse.observation.output",
                "value": {"stringValue": response_text[:1000]},
            },
            {"key": "gen_ai.prompt", "value": {"stringValue": prompt[:500]}},
            {
                "key": "gen_ai.completion",
                "value": {"stringValue": response_text[:1000]},
            },
        ],
        "status": {"code": 1},  # STATUS_CODE_OK
    }

    spans = [root_span]
    span_offset_ns = 50_000_000  # 50ms offset sintético para spans de tool
    for i, tool_name in enumerate(tools_executed):
        tool_span_id = uuid.uuid4().hex[:16]
        t_start = start_time_ns + (i + 1) * span_offset_ns
        t_end = min(t_start + span_offset_ns, end_time_ns)
        spans.append(
            {
                "traceId": trace_id,
                "spanId": tool_span_id,
                "parentSpanId": root_span_id,
                "name": f"execute_tool: {tool_name}",
                "kind": 1,
                "startTimeUnixNano": str(t_start),
                "endTimeUnixNano": str(t_end),
                "attributes": [
                    {
                        "key": "gen_ai.operation.name",
                        "value": {"stringValue": "execute_tool"},
                    },
                    {"key": "gen_ai.tool.name", "value": {"stringValue": tool_name}},
                    {"key": "gen_ai.tool.type", "value": {"stringValue": "mcp"}},
                    {
                        "key": "langfuse.observation.type",
                        "value": {"stringValue": "tool"},
                    },
                    {
                        "key": "tool.execution.status",
                        "value": {"stringValue": "success"},
                    },
                    {
                        "key": "gen_ai.conversation.id",
                        "value": {"stringValue": session_id},
                    },
                ],
                "status": {"code": 1},
            }
        )

    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {"stringValue": "deep-agents-copilot"},
                        },
                        {
                            "key": "telemetry.sdk.name",
                            "value": {"stringValue": "deep-agents-gateway"},
                        },
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {"name": "local_chat_gateway", "version": "0.1.0"},
                        "spans": spans,
                    }
                ],
            }
        ]
    }


def _resolve_candidate_endpoints(endpoint: str) -> list[str]:
    """Resolve endpoints candidatos em ambiente containerizado.

    Se configurado como 127.0.0.1 ou localhost, dentro do container
    essas URLs apontam para o proprio container (Connection Refused).
    Tenta sequencialmente:
    1. http://otel-collector:4318 (rede do compose com --profile otel)
    2. http://host.docker.internal:4318 (coletor rodando no host da maquina)
    3. URL original configurada
    """
    clean = endpoint.rstrip("/")
    if "127.0.0.1" in clean or "localhost" in clean:
        port = clean.split(":")[-1] if ":" in clean.split("/")[-1] else "4318"
        return [
            f"http://otel-collector:{port}",
            f"http://host.docker.internal:{port}",
            clean,
        ]
    return [clean]


def _dispatch_http(endpoint: str, payload: dict[str, Any]) -> None:
    """Disparo síncrono de HTTP POST em worker thread com fallback em cascata."""
    candidates = _resolve_candidate_endpoints(endpoint)
    data = json.dumps(payload).encode("utf-8")

    for base_url in candidates:
        target_url = f"{base_url.rstrip('/')}/v1/traces"
        req = urllib.request.Request(
            target_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=2.5) as res:
                if res.status < 300:
                    logger.info(
                        "otel_export_success: url=%s status=%s", target_url, res.status
                    )
                    return
                logger.warning(
                    "otel_export_http_status: %s url=%s", res.status, target_url
                )
        except Exception as exc:
            logger.debug("otel_candidate_failed: %s url=%s", exc, target_url)


# Conjunto module-level de referencias fortes aos Futures de despacho em
# background (bug real de producao, 2026-10-01): `loop.run_in_executor(...)`
# retorna um `asyncio.Future` que, se descartado sem nenhuma referencia
# mantida, fica sujeito a coleta precoce pelo garbage collector -- padrao
# explicitamente desaconselhado pela documentacao oficial do asyncio
# ("Save a reference to the result... the event loop only keeps a weak
# reference"). Em requisicoes reais via `/v1/chat/completions` (span
# `governance.route`/`governance.workflow_transition`/`chat: deep-agents/
# router`), spans eram perdidos silenciosamente de forma intermitente --
# testes manuais isolados (script `asyncio.run()` dedicado) sempre
# funcionavam, mas o mesmo codigo rodando dentro do processo Uvicorn
# persistente falhava de forma nao-deterministica. Mantemos cada Future
# vivo neste set ate sua conclusao (via `add_done_callback`), eliminando
# qualquer possibilidade de perda por GC, independente da causa exata.
_background_dispatch_tasks: set[Any] = set()


def _schedule_background_dispatch(endpoint: str, payload: dict[str, Any]) -> None:
    """Agenda `_dispatch_http` em thread de background com referencia forte.

    Args:
        endpoint: URL base do OTel Collector (ja resolvida, nao vazia).
        payload: Payload OTLP/JSON construido por `_build_otlp_payload`/
            `_build_custom_span_payload`.
    """
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(None, _dispatch_http, endpoint, payload)
    _background_dispatch_tasks.add(future)
    future.add_done_callback(_background_dispatch_tasks.discard)


async def emit_chat_trace(
    endpoint: str | None,
    *,
    session_id: str,
    prompt: str,
    response_text: str,
    tools_executed: list[str],
    start_time_ns: int,
    agent_name: str = "agent-router",
    model: str | None = None,
    trace_id: str | None = None,
) -> None:
    """Despacha spans de chat para o coletor OTel se `endpoint` estiver ativo."""
    if not endpoint:
        return

    end_time_ns = int(time.time() * 1_000_000_000)
    # Unifica o trace do turno completo (Addendum 8 -- bug de 4 traces
    # desconectados no Langfuse): usa `trace_id` recebido do chamador
    # (gerado uma unica vez em `routes.chat_completions`), com fallback
    # para gerar um novo UUID quando nao fornecido (compatibilidade
    # retroativa com chamadores existentes, ex.: testes unitarios diretos).
    trace_id_efetivo = trace_id if trace_id is not None else uuid.uuid4().hex
    root_span_id = uuid.uuid4().hex[:16]

    payload = _build_otlp_payload(
        trace_id=trace_id_efetivo,
        root_span_id=root_span_id,
        session_id=session_id,
        prompt=prompt,
        response_text=response_text,
        tools_executed=tools_executed,
        start_time_ns=start_time_ns,
        end_time_ns=end_time_ns,
        agent_name=agent_name,
        model=model,
    )

    try:
        _schedule_background_dispatch(endpoint, payload)
    except Exception as exc:
        logger.debug("emit_chat_trace_dispatch_error: %s", exc)

# ---------------------------------------------------------------------------
# T7/PR-7 — spans customizados de governanca (namespace deep_agents.*).
# Hierarquia esperada por turno: invoke_agent (root) > governance.health_check /
# governance.route / governance.workflow_transition > invoke_agent downstream
# (gen_ai.agent.name dinamico, acima). Helper unico de construcao de atributos
# (`_deep_agents_attributes`) evita divergencia de nomenclatura entre os 3 spans
# novos (Refactor do ciclo TDD desta etapa).
# ---------------------------------------------------------------------------


def _attr_value(value: Any) -> dict[str, Any]:
    """Serializa `value` no formato de valor de atributo OTLP apropriado.

    `bool` antes de `int` (todo `bool` tambem e `int` em Python) -- produz
    `boolValue`; `float` produz `doubleValue`; `int` produz `intValue`
    (como string, conforme exigido pelo schema OTLP/JSON); qualquer outro
    tipo (tipicamente `str`) produz `stringValue`.
    """
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, int):
        return {"intValue": str(value)}
    return {"stringValue": str(value)}


def _deep_agents_attributes(namespace: str, **kwargs: Any) -> list[dict[str, Any]]:
    """Constroi atributos `deep_agents.<namespace>.<chave>` (namespace custom).

    Helper unico reaproveitado pelos 3 novos spans de governanca (T7/PR-7) para
    evitar divergencia de nomenclatura entre eles. Chaves cujo valor e `None`
    sao omitidas do payload (ex.: `nivel`/`score` quando nao houve roteamento
    neste turno).

    Args:
        namespace: Sufixo do namespace customizado (ex.: `"health"`,
            `"routing"`, `"workflow"`).
        **kwargs: Pares chave/valor a serem emitidos como
            `deep_agents.<namespace>.<chave>`.

    Returns:
        list[dict[str, Any]]: Lista de atributos no formato OTLP/JSON.
    """
    attrs: list[dict[str, Any]] = []
    for key, value in kwargs.items():
        if value is None:
            continue
        attrs.append(
            {
                "key": f"deep_agents.{namespace}.{key}",
                "value": _attr_value(value),
            }
        )
    return attrs


def _build_custom_span_payload(
    *,
    trace_id: str,
    span_id: str,
    session_id: str,
    span_name: str,
    attributes: list[dict[str, Any]],
    start_time_ns: int,
    end_time_ns: int,
) -> dict[str, Any]:
    """Constroi o payload OTLP JSON de um unico span customizado
    (`operation.name=custom`).

    Reaproveita a mesma estrutura `resourceSpans`/`scopeSpans` de
    `_build_otlp_payload`, mas com um unico span (sem spans filhos de tool)
    carregando `deep_agents.*` + `gen_ai.conversation.id`.
    """
    span: dict[str, Any] = {
        "traceId": trace_id,
        "spanId": span_id,
        "name": span_name,
        "kind": 1,  # SPAN_KIND_INTERNAL
        "startTimeUnixNano": str(start_time_ns),
        "endTimeUnixNano": str(end_time_ns),
        "attributes": [
            {"key": "gen_ai.operation.name", "value": {"stringValue": "custom"}},
            {
                "key": "gen_ai.conversation.id",
                "value": {"stringValue": session_id},
            },
            {"key": "session.id", "value": {"stringValue": session_id}},
            # Decisao instantanea de governanca (health check/roteamento/
            # transicao de workflow) -- tipo "event" no modelo de dados do
            # Langfuse (ponto instantaneo, nao Generation nem Span de
            # duracao real; ver langfuse-observability SKILL.md Secao 2).
            {"key": "langfuse.observation.type", "value": {"stringValue": "event"}},
            *attributes,
        ],
        "status": {"code": 1},  # STATUS_CODE_OK
    }
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {"stringValue": "deep-agents-copilot"},
                        },
                        {
                            "key": "telemetry.sdk.name",
                            "value": {"stringValue": "deep-agents-gateway"},
                        },
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {"name": "local_chat_gateway", "version": "0.1.0"},
                        "spans": [span],
                    }
                ],
            }
        ]
    }


async def _emit_custom_governance_span(
    endpoint: str | None,
    *,
    span_name: str,
    session_id: str,
    attributes: list[dict[str, Any]],
    trace_id: str | None = None,
) -> None:
    """Despacha um span customizado de governanca se `endpoint` estiver ativo."""
    if not endpoint:
        return

    start_time_ns = int(time.time() * 1_000_000_000)
    end_time_ns = start_time_ns
    trace_id_efetivo = trace_id if trace_id is not None else uuid.uuid4().hex
    span_id = uuid.uuid4().hex[:16]

    payload = _build_custom_span_payload(
        trace_id=trace_id_efetivo,
        span_id=span_id,
        session_id=session_id,
        span_name=span_name,
        attributes=attributes,
        start_time_ns=start_time_ns,
        end_time_ns=end_time_ns,
    )

    try:
        _schedule_background_dispatch(endpoint, payload)
    except Exception as exc:
        logger.debug("emit_custom_governance_span_dispatch_error: %s", exc)


async def emit_governance_health_check_span(
    endpoint: str | None,
    *,
    session_id: str,
    graph_ok: bool,
    sdk_token_ok: bool,
    collector_ok: bool,
    budget_ok: bool,
    trace_id: str | None = None,
) -> None:
    """Emite o span `governance.health_check` (atributos `deep_agents.health.*`)."""
    attributes = _deep_agents_attributes(
        "health",
        graph_ok=graph_ok,
        sdk_token_ok=sdk_token_ok,
        collector_ok=collector_ok,
        budget_ok=budget_ok,
    )
    await _emit_custom_governance_span(
        endpoint,
        span_name="governance.health_check",
        session_id=session_id,
        attributes=attributes,
        trace_id=trace_id,
    )


async def emit_governance_route_span(
    endpoint: str | None,
    *,
    session_id: str,
    escolhido: str,
    workflow: str | None,
    nivel: str | None,
    score: float | None,
    drift_detectado: bool,
    trace_id: str | None = None,
) -> None:
    """Emite o span `governance.route` (atributos `deep_agents.routing.*`)."""
    attributes = _deep_agents_attributes(
        "routing",
        escolhido=escolhido,
        workflow=workflow,
        nivel=nivel,
        score=score,
        drift_detectado=drift_detectado,
    )
    await _emit_custom_governance_span(
        endpoint,
        span_name="governance.route",
        session_id=session_id,
        attributes=attributes,
        trace_id=trace_id,
    )


async def emit_governance_workflow_transition_span(
    endpoint: str | None,
    *,
    session_id: str,
    fase_origem: str,
    fase_destino: str,
    etapa: int,
    aprovacao_checkpoint: bool,
    error_type: str | None = None,
    trace_id: str | None = None,
) -> None:
    """Emite o span `governance.workflow_transition` (`deep_agents.workflow.*`).

    `error.type` (namespace padrao OTel, fora de `deep_agents.*`) so e incluido
    quando `error_type` nao e `None` (transicao invalida capturada por
    `governance_pipeline.avaliar_transicao`).
    """
    attributes = _deep_agents_attributes(
        "workflow",
        fase_origem=fase_origem,
        fase_destino=fase_destino,
        etapa=etapa,
        aprovacao_checkpoint=aprovacao_checkpoint,
    )
    if error_type is not None:
        attributes.append(
            {"key": "error.type", "value": {"stringValue": error_type}}
        )
    await _emit_custom_governance_span(
        endpoint,
        span_name="governance.workflow_transition",
        session_id=session_id,
        attributes=attributes,
        trace_id=trace_id,
    )
