"""Testes de contrato para esquemas Pydantic v2 do local_chat_gateway.

Valida a estrutura do schema JSON de ChatMessage, ChatCompletionRequest,
ChatCompletion, ChatCompletionChunk, Error e Model conforme contrato OpenAI.
"""

from __future__ import annotations

import pytest

from local_chat_gateway.api.schemas import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatMessage,
    Error,
    Model,
)


def test_deve_respeitar_contrato_chat_message():
    schema = ChatMessage.model_json_schema()
    propriedades = schema["properties"]

    assert "role" in propriedades
    assert "content" in propriedades
    # `content` e opcional desde a migracao LobeChat -> CopilotKit (D4-rev):
    # mensagens `assistant` com apenas `tool_calls` e mensagens `tool` nao
    # tem texto. `tool_calls`/`tool_call_id`/`name` tambem sao opcionais.
    assert schema.get("required") == ["role"]
    assert "tool_calls" in propriedades
    assert "tool_call_id" in propriedades


def test_deve_respeitar_contrato_chat_completion_request():
    schema = ChatCompletionRequest.model_json_schema()
    propriedades = schema["properties"]

    assert "model" in propriedades
    assert "messages" in propriedades
    assert "stream" in propriedades


def test_deve_respeitar_contrato_chat_completion():
    schema = ChatCompletion.model_json_schema()
    propriedades = schema["properties"]

    for campo in ["id", "object", "created", "model", "choices"]:
        assert campo in propriedades, f"Campo {campo} ausente em ChatCompletion"


def test_deve_respeitar_contrato_chat_completion_chunk():
    schema = ChatCompletionChunk.model_json_schema()
    propriedades = schema["properties"]

    for campo in ["id", "object", "created", "model", "choices"]:
        assert campo in propriedades, f"Campo {campo} ausente em ChatCompletionChunk"


def test_deve_respeitar_contrato_error_e_subtipos_permitidos():
    schema = Error.model_json_schema()
    propriedades = schema["properties"]

    assert "error" in propriedades

    defs = schema.get("$defs", {})
    assert "ErrorDetail" in defs
    error_detail_schema = defs["ErrorDetail"]
    detail_props = error_detail_schema["properties"]

    assert "message" in detail_props
    assert "type" in detail_props
    assert "code" in detail_props

    enum_valores = set(detail_props["type"]["enum"])
    esperados = {
        "authentication_error",
        "invalid_request_error",
        "rate_limit_error",
        "governance_error",
        "timeout_error",
        "server_error",
    }
    assert enum_valores == esperados


def test_deve_respeitar_contrato_model_id_router():
    schema = Model.model_json_schema()
    propriedades = schema["properties"]

    assert "id" in propriedades
    id_prop = propriedades["id"]

    # Pydantic v2 gera 'const' para Literal com único elemento
    id_esperado = "deep-agents/router"
    if "const" in id_prop:
        assert id_prop["const"] == id_esperado
    elif "enum" in id_prop:
        assert id_prop["enum"] == [id_esperado]
    else:
        pytest.fail(f"Nem 'const' nem 'enum' encontrados para o campo 'id': {id_prop}")
