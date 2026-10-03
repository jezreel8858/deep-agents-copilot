"""event_mapper — stub SDK -> `chat.completion.chunk`, eventos confirmados (RT-01).

Spike de nomenclatura RT-01 concluido por inspecao de runtime real
(`pip install github-copilot-sdk==1.0.15` em venv isolado + introspeccao
via `dir(copilot)` / `dir(copilot.session_events)`). Os 3 valores de
`SDKEventType` abaixo correspondem exatamente aos valores de
`copilot.SessionEventType` confirmados: `SessionEventType.ASSISTANT_MESSAGE_DELTA`
== "assistant.message_delta", `SessionEventType.TOOL_EXECUTION_START`
== "tool.execution_start", `SessionEventType.TOOL_EXECUTION_COMPLETE`
== "tool.execution_complete". As classes de payload reais (para a Fase 1
de integracao com o SDK real, fora do escopo desta fase de fixtures) sao
`copilot.session_events.AssistantMessageDeltaData`,
`copilot.session_events.ToolExecutionStartData` e
`copilot.session_events.ToolExecutionCompleteData`
(BLUEPRINT_LOCAL_CHAT_GATEWAY.md Secao 4.1 e 14.2).

Apenas os 3 eventos confirmados pelo spike RT-01 sao tipados/mapeados
nesta fase. Nenhuma integracao real com o SDK do Copilot ocorre aqui —
apenas fixtures sinteticas nos testes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SDKEventType = Literal[
    "assistant.message_delta",
    "tool.execution_start",
    "tool.execution_complete",
]


class UnsupportedSDKEventError(ValueError):
    """Erro de dominio: tipo de evento do SDK nao suportado por esta fase (RT-01)."""


@dataclass(frozen=True)
class SDKEvent:
    """Evento sintetico do SDK do Copilot (fixture, nao o SDK real)."""

    type: SDKEventType
    payload: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SSEChunkContent:
    """Conteudo minimo de um chunk SSE mapeado a partir de um `SDKEvent`."""

    delta_content: str | None
    finish_reason: Literal["stop"] | None = None


def map_sdk_event_to_chunk(event: SDKEvent) -> SSEChunkContent:
    """Mapeia um `SDKEvent` sintetico para o conteudo de um chunk SSE.

    Args:
        event: Evento sintetico (fixture) do SDK.

    Returns:
        SSEChunkContent: conteudo de `delta.content` a ser emitido.

    Raises:
        UnsupportedSDKEventError: Se `event.type` nao for um dos 3 eventos
            confirmados pelo spike RT-01.
    """
    if event.type == "assistant.message_delta":
        return SSEChunkContent(delta_content=event.payload.get("text", ""))
    if event.type == "tool.execution_start":
        nome = event.payload.get("tool_name", "?")
        return SSEChunkContent(
            delta_content=f"\n> \U0001f527 tool: {nome} (iniciando)\n"
        )
    if event.type == "tool.execution_complete":
        nome = event.payload.get("tool_name", "?")
        resultado = event.payload.get("result", "")
        return SSEChunkContent(
            delta_content=f"\n> \U0001f527 tool: {nome} concluido: {resultado}\n"
        )
    raise UnsupportedSDKEventError(f"evento SDK nao suportado nesta fase: {event.type}")
