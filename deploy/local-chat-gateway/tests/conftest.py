"""Configurações globais e fixtures para testes de integração do local_chat_gateway."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

_repo_root = Path(__file__).resolve().parents[3]
_pkg_src = _repo_root / "deploy" / "local-chat-gateway" / "src"
_core_src = _repo_root / "src"

for p in [str(_pkg_src), str(_core_src)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import local_chat_gateway.app  # noqa: E402
import local_chat_gateway.config  # noqa: E402
import local_chat_gateway.session_store  # noqa: E402
from local_chat_gateway.config import Settings  # noqa: E402
from local_chat_gateway.session_store import SessionStore  # noqa: E402


_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
_VALID_GRAPH_PATH = _FIXTURES_DIR / "valid_graph.yaml"
# Grafo minimo valido (T2/PR-2) usado como default de nao-regressao em
# `fake_settings` -- garante que o lifespan fail-fast (Q-02) nunca aborte
# a suite de testes existente por ausencia de `governance_graph_path`.


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    """Retorna caminho para arquivo SQLite isolado em diretório temporário."""
    return tmp_path / "gateway-test.db"


@pytest.fixture
def fake_settings(tmp_db_path: Path) -> Settings:
    """Configuração de teste com chave de API válida e banco temporário isolado.

    `gateway_permission_mode="read_only"` fixado explicitamente (2026-10-01):
    sem isso, `Settings()` herda silenciosamente o `.env` REAL do
    desenvolvedor (pydantic-settings le `.env` do CWD) -- bug de
    isolamento de teste exposto quando o `.env` local foi alterado para
    `apply` (escrita real habilitada para uso do LobeChat). Testes NUNCA
    devem depender do conteudo de um arquivo `.env` nao versionado.
    """
    return Settings(
        gateway_api_key="test-real-key",
        gateway_db_path=str(tmp_db_path),
        governance_graph_path=_VALID_GRAPH_PATH,
        gateway_permission_mode="read_only",
    )


@pytest.fixture
def session_store(fake_settings: Settings) -> SessionStore:
    """Instância do SessionStore apontando para o banco de teste."""
    return local_chat_gateway.session_store.SessionStore(
        fake_settings.gateway_db_path,
        session_ttl_s=fake_settings.gateway_session_ttl_s,
        max_premium_per_day=fake_settings.gateway_max_premium_per_day,
    )


@pytest.fixture
def app(fake_settings: Settings, session_store: SessionStore) -> FastAPI:
    """Instância do FastAPI configurada com fake_settings e dependency_overrides."""
    application = local_chat_gateway.app.create_app(settings=fake_settings)
    application.dependency_overrides[local_chat_gateway.config.get_settings] = (
        lambda: fake_settings
    )
    application.dependency_overrides[
        local_chat_gateway.session_store.get_session_store
    ] = lambda: session_store
    return application


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """TestClient síncrono para validação de endpoints HTTP."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(fake_settings: Settings) -> dict[str, str]:
    """Cabeçalhos HTTP de autenticação com Bearer token válido."""
    return {"Authorization": f"Bearer {fake_settings.gateway_api_key}"}
