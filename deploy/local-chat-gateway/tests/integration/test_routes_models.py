"""Testes de integração para endpoints /v1/models e /v1/chat/completions."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient


def test_get_models_without_auth_returns_401(client: TestClient) -> None:
    """GET /v1/models sem header Authorization retorna HTTP 401."""
    response = client.get("/v1/models")
    assert response.status_code == 401
    assert response.json() == {"detail": "missing or malformed Authorization header"}


def test_get_models_with_invalid_token_returns_401(client: TestClient) -> None:
    """GET /v1/models com Authorization Bearer incorreto retorna HTTP 401."""
    headers = {"Authorization": "Bearer token-invalido"}
    response = client.get("/v1/models", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid bearer token"}


def test_get_models_with_valid_auth_returns_models(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """GET /v1/models com auth_headers válidos retorna HTTP 200 e deep-agents/router."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["object"] == "list"
    assert len(payload["data"]) == 1
    assert payload["data"][0]["id"] == "deep-agents/router"
    assert payload["data"][0]["owned_by"] == "deep-agents"


def test_chat_completions_without_auth_fails_before_body_parsing(
    client: TestClient,
) -> None:
    """POST /v1/chat/completions sem Authorization retorna 401
    mesmo com corpo JSON inválido."""
    # Corpo deliberadamente inválido/incompleto (esperaria 422 se avaliado antes)
    invalid_body = {"model": "modelo-invalido", "messages": "nao-eh-lista"}
    response = client.post("/v1/chat/completions", json=invalid_body)
    assert response.status_code == 401
    assert response.json() == {"detail": "missing or malformed Authorization header"}


def test_chat_completions_non_streaming_success(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """POST /v1/chat/completions com auth válido e stream=False
    retorna HTTP 200 e stub response."""
    body = {
        "model": "deep-agents/router",
        "messages": [{"role": "user", "content": "oi"}],
        "stream": False,
    }
    response = client.post("/v1/chat/completions", json=body, headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "chatcmpl-stub"
    assert payload["object"] == "chat.completion"
    assert payload["model"] == "deep-agents/router"
    assert len(payload["choices"]) == 1
    choice = payload["choices"][0]
    assert choice["index"] == 0
    assert choice["message"]["role"] == "assistant"
    assert choice["finish_reason"] == "stop"
    assert (
        "stub: SDK real do Copilot ainda nao integrado" in choice["message"]["content"]
    )


def test_chat_completions_streaming_returns_sse_chunks(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """POST /v1/chat/completions com stream=True retorna SSE stub
    (3 chunks + [DONE]), nunca mais 501 (Fase 2 — streaming stub)."""
    body = {
        "model": "deep-agents/router",
        "messages": [{"role": "user", "content": "oi"}],
        "stream": True,
    }
    response = client.post("/v1/chat/completions", json=body, headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    raw_events = [
        line for line in response.text.split("\n\n") if line.strip().startswith("data:")
    ]
    assert len(raw_events) == 4  # role + content + stop + [DONE]

    data_payloads = [event.removeprefix("data: ").strip() for event in raw_events]
    assert data_payloads[-1] == "[DONE]"

    role_chunk = json.loads(data_payloads[0])
    assert role_chunk["object"] == "chat.completion.chunk"
    assert role_chunk["model"] == "deep-agents/router"
    assert role_chunk["choices"][0]["delta"]["role"] == "assistant"
    assert role_chunk["choices"][0]["finish_reason"] is None

    content_chunk = json.loads(data_payloads[1])
    assert (
        "stub: SDK real do Copilot ainda nao integrado"
        in content_chunk["choices"][0]["delta"]["content"]
    )
    assert content_chunk["choices"][0]["finish_reason"] is None

    stop_chunk = json.loads(data_payloads[2])
    assert stop_chunk["choices"][0]["finish_reason"] == "stop"
    assert stop_chunk["choices"][0]["delta"].get("content") is None
