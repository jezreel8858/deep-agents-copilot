"""Testes de integracao para `GET /v1/workspace/commands` (picker `/` do
composer -- prompts + skills, paridade com o plugin Copilot da IDE, pedido
explicito do usuario 2026-10-02)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_list_workspace_commands_sem_auth_retorna_401(client: TestClient) -> None:
    """GET /v1/workspace/commands sem Authorization retorna HTTP 401."""
    response = client.get("/v1/workspace/commands")
    assert response.status_code == 401


def test_list_workspace_commands_retorna_catalogo_descoberto_no_lifespan(
    app: FastAPI, auth_headers: dict[str, str]
) -> None:
    """Devolve o mesmo catalogo ja cacheado em `app.state.commands_catalog`,
    ignorando entradas sem `name` valido (mesmo padrao de
    `list_workspace_agents`/`app.state.custom_agents`)."""
    with TestClient(app) as test_client:
        # `app.state.commands_catalog` so existe apos o lifespan de startup
        # (acionado ao entrar no `with TestClient(...)`) -- sobrescrito aqui
        # para isolar o teste da descoberta real de `.github/prompts`/
        # `.github/skills`.
        app.state.commands_catalog = [
            {"name": "commit", "kind": "prompt", "description": "Gera commit."},
            {"name": "context-mode", "kind": "skill", "description": "Boas praticas."},
            {"description": "sem campo name -- deve ser ignorado"},
        ]
        response = test_client.get("/v1/workspace/commands", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["commands"] == [
        {"name": "commit", "kind": "prompt", "description": "Gera commit."},
        {"name": "context-mode", "kind": "skill", "description": "Boas praticas."},
    ]


def test_list_workspace_commands_retorna_vazio_quando_catalogo_ausente(
    app: FastAPI, auth_headers: dict[str, str]
) -> None:
    """Sem `app.state.commands_catalog` (nunca deveria ocorrer em producao,
    pois o lifespan sempre popula -- ao menos lista vazia), o endpoint
    degrada graciosamente para lista vazia, nunca HTTP 500."""
    with TestClient(app) as test_client:
        app.state.commands_catalog = None
        response = test_client.get("/v1/workspace/commands", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"commands": []}
