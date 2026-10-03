"""Testes de integração para `/v1/workspace/files` e `/v1/workspace/agents`
(pickers `#`/`@` do composer -- paridade com o plugin Copilot da IDE)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from local_chat_gateway.config import Settings, get_settings


def test_list_workspace_files_sem_auth_retorna_401(client: TestClient) -> None:
    """GET /v1/workspace/files sem Authorization retorna HTTP 401."""
    response = client.get("/v1/workspace/files")
    assert response.status_code == 401


def test_list_workspace_files_retorna_vazio_quando_workspace_nao_existe(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Sem projetos registrados e sem `gateway_workspace_dir` real (default
    `/workspaces`, inexistente fora do container), retorna lista vazia --
    nunca HTTP 500 (`listar_arquivos_workspace` e tolerante a raiz ausente)."""
    response = client.get("/v1/workspace/files", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["files"] == []
    assert payload["truncated"] is False


def test_list_workspace_files_descobre_arquivos_reais_e_aplica_query(
    app: FastAPI,
    fake_settings: Settings,
    auth_headers: dict[str, str],
    tmp_path: Path,
) -> None:
    """Com `gateway_workspace_dir` apontando para um diretorio real, o
    endpoint descobre arquivos, ignora `node_modules/` e aplica `?q=`."""
    workspace_dir = tmp_path / "workspace-real"
    (workspace_dir / "src").mkdir(parents=True)
    (workspace_dir / "src" / "page.tsx").write_text("x", encoding="utf-8")
    (workspace_dir / "node_modules").mkdir()
    (workspace_dir / "node_modules" / "ignorado.js").write_text("x", encoding="utf-8")

    settings_customizado = fake_settings.model_copy(
        update={"gateway_workspace_dir": str(workspace_dir)}
    )
    app.dependency_overrides[get_settings] = lambda: settings_customizado

    with TestClient(app) as test_client:
        response = test_client.get(
            "/v1/workspace/files",
            headers=auth_headers,
            params={"q": "page"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert [f["path"] for f in payload["files"]] == ["src/page.tsx"]
    assert payload["files"][0]["project"] == "workspace"
    assert payload["truncated"] is False


def test_list_workspace_agents_sem_auth_retorna_401(client: TestClient) -> None:
    """GET /v1/workspace/agents sem Authorization retorna HTTP 401."""
    response = client.get("/v1/workspace/agents")
    assert response.status_code == 401


def test_list_workspace_agents_retorna_catalogo_descoberto_no_lifespan(
    app: FastAPI, auth_headers: dict[str, str]
) -> None:
    """Devolve o mesmo catalogo ja cacheado em `app.state.custom_agents`
    (RT-04), ignorando entradas sem `name` valido."""
    with TestClient(app) as test_client:
        # `app.state.custom_agents` so existe apos o lifespan de startup
        # (acionado ao entrar no `with TestClient(...)`) -- sobrescrito aqui
        # para isolar o teste da descoberta real de `.github/agents/`.
        app.state.custom_agents = [
            {
                "name": "python-bug-fixer",
                "display_name": "Python Bug Fixer",
                "description": "Corrige bugs em Python.",
            },
            {"description": "sem campo name -- deve ser ignorado"},
        ]
        response = test_client.get("/v1/workspace/agents", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["agents"] == [
        {
            "name": "python-bug-fixer",
            "display_name": "Python Bug Fixer",
            "description": "Corrige bugs em Python.",
        }
    ]

