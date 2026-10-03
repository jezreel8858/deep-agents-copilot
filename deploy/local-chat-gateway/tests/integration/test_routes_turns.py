"""Testes de integração para o endpoint read-only `GET /v1/turns`.

Historico DURAVEL por turno (tabela `turns`, `turn_recorder.py`) -- pedido
explicito do usuario (2026-10-02): insumo de analise continua de melhoria
de workflow/agent, consultavel independente de qualquer observability
stack externo (OTel Collector/Langfuse) estar configurado.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from local_chat_gateway.session_store import SessionStore, TurnRecord


def test_get_turns_sem_auth_retorna_401(client: TestClient) -> None:
    """GET /v1/turns sem header Authorization retorna HTTP 401."""
    response = client.get("/v1/turns")
    assert response.status_code == 401


def test_get_turns_vazio_quando_nenhum_turno_persistido(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """GET /v1/turns sem nenhum turno gravado retorna lista vazia (200)."""
    response = client.get("/v1/turns", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_turns_retorna_turnos_persistidos_mais_recentes_primeiro(
    client: TestClient,
    auth_headers: dict[str, str],
    session_store: SessionStore,
) -> None:
    """Turnos gravados via `SessionStore.record_turn` (mesmo mecanismo de
    `turn_recorder.persistir`) aparecem no endpoint, ordenados do mais
    recente para o mais antigo, com todos os campos do `TurnRecord`."""
    session_store.record_turn(
        TurnRecord(
            turn_id="turn-antigo",
            session_id="sessao-1",
            created_at=1000,
            agent_name="agent-router",
            workflow=None,
        )
    )
    session_store.record_turn(
        TurnRecord(
            turn_id="turn-recente",
            session_id="sessao-1",
            created_at=2000,
            agent_name="bug-triage",
            workflow="WORKFLOW-BUG-FIX",
            tokens_input=100,
            tokens_output=50,
            retries_count=1,
            retry_reasons=["timeout"],
        )
    )

    response = client.get("/v1/turns", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert [t["turn_id"] for t in payload] == ["turn-recente", "turn-antigo"]
    assert payload[0]["agent_name"] == "bug-triage"
    assert payload[0]["workflow"] == "WORKFLOW-BUG-FIX"
    assert payload[0]["tokens_input"] == 100
    assert payload[0]["retry_reasons"] == ["timeout"]


def test_get_turns_filtra_por_session_id_via_query_param(
    client: TestClient,
    auth_headers: dict[str, str],
    session_store: SessionStore,
) -> None:
    """`?session_id=...` filtra apenas os turnos daquela sessao."""
    session_store.record_turn(
        TurnRecord(turn_id="turn-a", session_id="sessao-a", created_at=1000)
    )
    session_store.record_turn(
        TurnRecord(turn_id="turn-b", session_id="sessao-b", created_at=1000)
    )

    response = client.get(
        "/v1/turns", params={"session_id": "sessao-a"}, headers=auth_headers
    )
    assert response.status_code == 200
    payload = response.json()
    assert [t["turn_id"] for t in payload] == ["turn-a"]


def test_get_turns_respeita_limit_via_query_param(
    client: TestClient,
    auth_headers: dict[str, str],
    session_store: SessionStore,
) -> None:
    """`?limit=N` limita a quantidade de turnos retornados."""
    for i in range(5):
        session_store.record_turn(
            TurnRecord(turn_id=f"turn-{i}", session_id="sessao-x", created_at=1000 + i)
        )

    response = client.get(
        "/v1/turns",
        params={"session_id": "sessao-x", "limit": 2},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert [t["turn_id"] for t in payload] == ["turn-4", "turn-3"]

