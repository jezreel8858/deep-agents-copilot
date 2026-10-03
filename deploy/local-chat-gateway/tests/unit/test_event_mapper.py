"""Testes unitários de mapeamento de eventos sintéticos do Copilot SDK.

# TODO(RT-01): fixtures sintéticas — nomenclatura real do SDK ainda não
# validada por inspeção de runtime
"""

from __future__ import annotations

import pytest

from local_chat_gateway.event_mapper import (
    SDKEvent,
    SSEChunkContent,
    UnsupportedSDKEventError,
    map_sdk_event_to_chunk,
)


def test_deve_mapear_assistant_message_delta_com_sucesso():
    # Arrange
    evento = SDKEvent(type="assistant.message_delta", payload={"text": "olá"})

    # Act
    chunk = map_sdk_event_to_chunk(evento)

    # Assert
    assert chunk == SSEChunkContent(delta_content="olá")


def test_deve_mapear_tool_execution_start_com_nome_da_ferramenta():
    # Arrange
    evento = SDKEvent(type="tool.execution_start", payload={"tool_name": "read_file"})

    # Act
    chunk = map_sdk_event_to_chunk(evento)

    # Assert
    assert chunk.delta_content is not None
    assert "read_file" in chunk.delta_content
    assert "iniciando" in chunk.delta_content


def test_deve_mapear_tool_execution_complete_com_nome_e_resultado():
    # Arrange
    evento = SDKEvent(
        type="tool.execution_complete",
        payload={"tool_name": "read_file", "result": "ok"},
    )

    # Act
    chunk = map_sdk_event_to_chunk(evento)

    # Assert
    assert chunk.delta_content is not None
    assert "read_file" in chunk.delta_content
    assert "concluido" in chunk.delta_content
    assert "ok" in chunk.delta_content


def test_deve_lancar_unsupported_sdk_event_error_quando_tipo_evento_desconhecido():
    # Arrange
    # Construção com tipo inválido simulando evento inesperado do SDK
    evento_invalido = SDKEvent.__new__(SDKEvent)
    object.__setattr__(evento_invalido, "type", "unknown.event_type")
    object.__setattr__(evento_invalido, "payload", {})

    # Act & Assert
    with pytest.raises(
        UnsupportedSDKEventError,
        match="evento SDK nao suportado nesta fase: unknown.event_type",
    ):
        map_sdk_event_to_chunk(evento_invalido)
