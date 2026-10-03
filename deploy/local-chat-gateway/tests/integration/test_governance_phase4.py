"""Testes de integracao da Fase 4 -- Governanca, Multi-Turno e Checkpoints.

Valida:
1. Teto diario de requisicoes premium (HTTP 429 quando esgotado).
2. Rastreamento e reuso de sessoes multi-turno (header x-session-id).
3. Invariante 11 nos endpoints (respostas vagas reemitem sem invocar o LLM).
4. Resolucao legitima de checkpoint e desbloqueio do fluxo.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from local_chat_gateway.session_store import SessionStore


def test_teto_diario_esgotado_retorna_429(
    session_store: SessionStore, client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Quando o budget diario de premium requests esta esgotado, retorna HTTP 429."""
    import time

    hoje = time.strftime("%Y-%m-%d", time.gmtime())
    # Simula esgotamento do teto diario
    session_store.register_premium_request(hoje, amount=1000)

    body = {
        "model": "deep-agents/router",
        "messages": [{"role": "user", "content": "olá"}],
        "stream": False,
    }
    response = client.post("/v1/chat/completions", json=body, headers=auth_headers)
    assert response.status_code == 429
    assert "Teto diario de requisicoes atingido" in response.text


def test_sessao_multi_turno_registrada_no_store(
    session_store: SessionStore, client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Header x-session-id cria e renova a sessao no SessionStore."""
    session_id = "sessao-teste-123"

    assert session_store.get_session(session_id) is None

    headers = {**auth_headers, "x-session-id": session_id}
    body = {
        "model": "deep-agents/router",
        "messages": [{"role": "user", "content": "olá"}],
        "stream": False,
    }
    response = client.post("/v1/chat/completions", json=body, headers=headers)
    assert response.status_code == 200

    record = session_store.get_session(session_id)
    assert record is not None
    assert record.session_id == session_id


def test_invariante_11_resposta_vaga_reemite_checkpoint_localmente(
    session_store: SessionStore, client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Resposta vaga com checkpoint aberto nao consome SDK e reemite a pergunta."""
    session_id = "sessao-cp-vaga"
    headers = {**auth_headers, "x-session-id": session_id}

    session_store.create_session(session_id)
    session_store.record_checkpoint(
        checkpoint_id="cp-9999",
        session_id=session_id,
        question="Qual banco deseja usar? 1) PostgreSQL 2) SQLite",
    )
    assert session_store.is_checkpoint_open(session_id) is True

    # Resposta vaga (Invariante 11)
    body = {
        "model": "deep-agents/router",
        "messages": [{"role": "user", "content": "prossiga"}],
        "stream": False,
    }
    response = client.post("/v1/chat/completions", json=body, headers=headers)
    assert response.status_code == 200
    conteudo = response.json()["choices"][0]["message"]["content"]

    assert "Resposta nao reconhecida para o checkpoint aberto [cp-9999]" in conteudo
    assert "Qual banco deseja usar?" in conteudo
    # Checkpoint continua aberto!
    assert session_store.is_checkpoint_open(session_id) is True


def test_invariante_11_streaming_reemite_checkpoint_via_sse(
    session_store: SessionStore, client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Em streaming, resposta vaga tambem reemite o checkpoint via SSE."""
    session_id = "sessao-cp-stream-vaga"
    headers = {**auth_headers, "x-session-id": session_id}

    session_store.create_session(session_id)
    session_store.record_checkpoint(
        checkpoint_id="cp-8888",
        session_id=session_id,
        question="Aprova o diff? 1) Sim 2) Nao",
    )

    body = {
        "model": "deep-agents/router",
        "messages": [{"role": "user", "content": "ok"}],
        "stream": True,
    }
    response = client.post("/v1/chat/completions", json=body, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    chunks = [
        line for line in response.text.split("\n\n") if line.strip().startswith("data:")
    ]
    data_payloads = [c.removeprefix("data: ").strip() for c in chunks]
    assert data_payloads[-1] == "[DONE]"

    content_chunk = json.loads(data_payloads[1])
    texto = content_chunk["choices"][0]["delta"]["content"]
    assert "cp-8888" in texto
    assert session_store.is_checkpoint_open(session_id) is True


def test_resposta_valida_resolve_checkpoint_e_prossegue(
    session_store: SessionStore, client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Resposta valida segundo a gramatica resolve o checkpoint pendente."""
    session_id = "sessao-cp-valida"
    headers = {**auth_headers, "x-session-id": session_id}

    session_store.create_session(session_id)
    session_store.record_checkpoint(
        checkpoint_id="cp-7777",
        session_id=session_id,
        question="Escolha: 1) Opcao A 2) Opcao B",
    )

    # Resposta gramaticalmente valida: opcao 1
    body = {
        "model": "deep-agents/router",
        "messages": [{"role": "user", "content": "1"}],
        "stream": False,
    }
    response = client.post("/v1/chat/completions", json=body, headers=headers)
    assert response.status_code == 200

    # O checkpoint deve ter sido resolvido no store!
    assert session_store.is_checkpoint_open(session_id) is False
