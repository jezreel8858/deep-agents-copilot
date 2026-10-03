"""app — FastAPI app factory (`create_app()`) do local_chat_gateway."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from local_chat_gateway import governance_pipeline
from local_chat_gateway.agent_catalog import descobrir_custom_agents
from local_chat_gateway.api.routes import router
from local_chat_gateway.prompts_catalog import descobrir_comandos
from local_chat_gateway.config import Settings, get_settings
from local_chat_gateway.logging_config import configurar_logging


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Carrega o contexto de governanca (Grafo/TabelaTransicao/Catalogo) uma unica vez.

    Fail-fast (Q-02): se o grafo de roteamento for invalido,
    `governance_pipeline.carregar_contexto_governanca` loga a causa em
    nivel CRITICAL e propaga a excecao sem captura -- o servidor ASGI
    recusa o startup do gateway (sem modo degradado, sem fallback).

    RT-04 (2026-10-01): tambem descobre o catalogo de custom agents
    (`.github/agents/**/*.agent.md`) uma unica vez aqui, cacheado em
    `app.state.custom_agents` -- NUNCA reimplementa o roteamento, apenas
    disponibiliza o catalogo para `run_subagent` funcionar de fato na
    sessao real do SDK (ver `agent_catalog.py` para o porque). Falha de
    descoberta (diretorio ausente/arquivo malformado) NUNCA derruba o
    startup -- `descobrir_custom_agents` e deliberadamente tolerante
    (lista vazia e um resultado valido, apenas sem delegacao disponivel).

    Args:
        app: Instancia FastAPI com `app.state.settings` ja atribuido por
            `create_app()`.

    Yields:
        None: controle de volta ao ciclo de vida padrao do ASGI apos a
        carga do contexto de governanca.
    """
    settings: Settings = app.state.settings
    contexto = governance_pipeline.carregar_contexto_governanca(settings)
    app.state.grafo = contexto.grafo
    app.state.tabela_transicao = contexto.tabela_transicao
    app.state.catalogo = contexto.catalogo
    app.state.custom_agents = descobrir_custom_agents(
        settings.governance_github_dir / "agents"
    )
    # Picker `/` do composer (pedido explicito do usuario, 2026-10-02):
    # catalogo unificado de prompts + skills, descoberto 1 unica vez aqui
    # (mesmo padrao tolerante de `custom_agents` -- falha de descoberta
    # NUNCA derruba o startup, lista vazia e um resultado valido).
    app.state.commands_catalog = descobrir_comandos(settings.governance_github_dir)
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    """Constroi a aplicacao FastAPI, validando a configuracao de startup.

    Args:
        settings: Configuracao a usar (injecao explicita em testes); se
            omitido, chama `get_settings()`.

    Returns:
        FastAPI: aplicacao pronta para servir, com `app.state.settings`
        exposto para uso pelos handlers/dependencias. No startup do ASGI
        (lifespan), `app.state.grafo`, `app.state.tabela_transicao` e
        `app.state.catalogo` sao populados uma unica vez (cache imutavel).

    Raises:
        InvalidGatewayConfigurationError: Se `settings.gateway_api_key`
            ainda for `"change-me"` (recusa de startup).
        governance_pipeline.GovernanceGraphPathNaoConfiguradoError: Se
            `settings.governance_graph_path` nao for informado (levantado
            no startup do lifespan, nao na chamada de `create_app`).
        governance.GraphValidationError: Se o grafo de roteamento for
            invalido (fail-fast Q-02, levantado no startup do lifespan).
    """
    resolved_settings = settings if settings is not None else get_settings()
    resolved_settings.validate_startup()

    # Fix 3 (2026-10-04): logging em arquivo aditivo -- nunca substitui o
    # StreamHandler/stdout default do uvicorn (ver `logging_config.py`).
    configurar_logging(
        resolved_settings.gateway_log_file,
        max_bytes=resolved_settings.gateway_log_max_bytes,
        backup_count=resolved_settings.gateway_log_backup_count,
    )

    # `telemetry={"auto_configure": False}`: o FastAPI 0.142+ tenta configurar
    # OpenTelemetry automaticamente no startup, exigindo o extra opcional
    # `fastapi[opentelemetry]`/`fastapi[standard]` (nao instalado -- imagem
    # minima, ver Dockerfile). Este gateway ja tem sua propria camada OTel
    # opcional (Secao 9 do blueprint, via OTEL_EXPORTER_OTLP_ENDPOINT +
    # otel-collector), entao a auto-configuracao nativa do FastAPI e
    # explicitamente desligada aqui para nao falhar o startup sem o extra.
    app = FastAPI(
        title="Deep Agents Gateway",
        version="0.1.0",
        telemetry={"auto_configure": False},
        lifespan=_lifespan,
    )
    app.state.settings = resolved_settings
    app.include_router(router)
    return app
