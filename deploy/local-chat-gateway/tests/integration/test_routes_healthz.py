"""Testes de integração para endpoint GET /healthz."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz_without_auth_returns_ok(client: TestClient) -> None:
    """GET /healthz sem nenhum header Authorization retorna HTTP 200 com status ok."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
