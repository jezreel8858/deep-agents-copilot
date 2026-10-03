"""config — Settings do gateway via pydantic-settings, lidas de .env.

Espelha exatamente as variaveis documentadas em `.env.example` (Secao 3.2 do
BLUEPRINT_LOCAL_CHAT_GATEWAY.md).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PermissionMode = Literal["read_only", "propose", "apply"]

FORBIDDEN_GATEWAY_API_KEY = "change-me"


class InvalidGatewayConfigurationError(RuntimeError):
    """Erro de dominio: configuracao de startup do gateway e insegura ou invalida."""


class Settings(BaseSettings):
    """Configuracao do `local_chat_gateway`, lida de variaveis de ambiente/.env."""

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", populate_by_name=True
    )

    gateway_api_key: str = Field(
        default=FORBIDDEN_GATEWAY_API_KEY, alias="GATEWAY_API_KEY"
    )
    gateway_bind: str = Field(default="127.0.0.1", alias="GATEWAY_BIND")
    gateway_port: int = Field(default=8080, alias="GATEWAY_PORT")
    # Diretorio-pai comum (path do HOST) contendo TODOS os projetos
    # registrados em `projects_local_yaml` -- montado uma unica vez em
    # `/workspaces` (docker-compose.yml). Ver `projects_catalog.py` para a
    # traducao automatica `path_externo` -> path no container. Substitui o
    # antigo `WORKSPACE_PATH` (mount de 1 unico projeto).
    projects_root_path: str | None = Field(default=None, alias="PROJECTS_ROOT_PATH")
    projects_local_yaml: str = Field(
        default="/governance/.github/projects.local.yaml",
        alias="PROJECTS_LOCAL_YAML",
    )
    gateway_permission_mode: PermissionMode = Field(
        default="read_only", alias="GATEWAY_PERMISSION_MODE"
    )
    # T6/PR-6 (Q-04): feature flag default OFF -- quando False, o `permission_handler`
    # de `stream_chat` permanece o `_conservative_permission_handler` read-only atual
    # (sem alteracao de comportamento); quando True, delega a `PermissionPolicyStub`.
    gateway_governance_permissions: bool = Field(
        default=False, alias="GATEWAY_GOVERNANCE_PERMISSIONS"
    )
    gov_max_premium_requests: int = Field(default=15, alias="GOV_MAX_PREMIUM_REQUESTS")
    gateway_max_premium_per_day: int = Field(
        default=100, alias="GATEWAY_MAX_PREMIUM_PER_DAY"
    )
    gateway_request_timeout_s: int = Field(
        default=300, alias="GATEWAY_REQUEST_TIMEOUT_S"
    )
    gateway_session_ttl_s: int = Field(default=1800, alias="GATEWAY_SESSION_TTL_S")
    # Fix 3 (2026-10-04): logging em arquivo aditivo (ver `logging_config.py`)
    # -- gap de observabilidade, logs dependiam 100% do stdout do uvicorn,
    # perdidos ao fechar o terminal/sessao de `dev_watch.py`.
    gateway_log_file: str = Field(
        default=".tmp/gateway.log", alias="GATEWAY_LOG_FILE"
    )
    gateway_log_max_bytes: int = Field(
        default=5_242_880, alias="GATEWAY_LOG_MAX_BYTES"
    )
    gateway_log_backup_count: int = Field(
        default=3, alias="GATEWAY_LOG_BACKUP_COUNT"
    )
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    copilot_model: str | None = Field(default=None, alias="COPILOT_MODEL")
    copilot_sdk_token_file: str = Field(
        default="./secrets/copilot_token", alias="COPILOT_SDK_TOKEN_FILE"
    )
    gateway_db_path: str = Field(
        default="/app/data/gateway.db", alias="GATEWAY_DB_PATH"
    )
    # Diretorio de trabalho repassado a `client.create_session(working_directory=...)`
    # (sdk_session.stream_chat). Default "/workspaces" preserva o comportamento
    # de producao (bind mount do docker-compose.yml). Bug real corrigido em
    # 2026-10-01: antes este valor era hardcoded direto em `stream_chat()` (sem
    # passar por Settings), entao rodar o gateway fora do Docker (`uvicorn`
    # local, sem o bind mount) sempre falhava no startup da sessao com
    # "session construction failed: Directory does not exist or cannot be
    # accessed: /workspaces". Agora e configuravel via env var para permitir
    # execucao local apontando para um diretorio real do host.
    gateway_workspace_dir: str = Field(
        default="/workspaces", alias="GATEWAY_WORKSPACE_DIR"
    )
    # Caminhos do grafo de roteamento/governanca (Q-02/Q-03 -- ver
    # docs/plans/20261001-feature-development-governance-runner-sdk-integration.md).
    # `governance_graph_path` NAO tem default de producao aqui -- o lifespan
    # de `app.py` falha explicitamente (fail-fast) se nao for informado, pois
    # carregar um grafo valido e pre-requisito obrigatorio de startup do
    # gateway (ver `governance_pipeline.carregar_contexto_governanca`).
    # `governance_schema_path=None` -> usa o schema JSON embutido no pacote
    # `governance_runner.routing` (schema padrao, Q-03), resolvido por
    # `governance_pipeline._resolver_schema_padrao()`.
    governance_graph_path: Path | None = Field(
        default=None, alias="GOVERNANCE_GRAPH_PATH"
    )
    governance_schema_path: Path | None = Field(
        default=None, alias="GOVERNANCE_SCHEMA_PATH"
    )
    # Raiz de `.github/` usada por `governance_pipeline.montar_contexto` para
    # ler persona/nucleo (Addendum 5, bug real de producao 2026-10-01):
    # o default antigo era calculado de `Path(__file__).resolve().parents[4]`,
    # que resolve para o local de INSTALACAO do pacote (`/usr/local/lib/
    # python3.12/site-packages/...` dentro do container Docker) em vez do
    # volume real do repositorio de governanca (`/governance:ro`, montado em
    # `docker-compose.yml`). Default aqui ja aponta para o caminho correto
    # dentro do container -- normalmente nao precisa ser alterado.
    governance_github_dir: Path = Field(
        default=Path("/governance/.github"), alias="GOVERNANCE_GITHUB_DIR"
    )

    @field_validator("governance_graph_path", "governance_schema_path", mode="before")
    @classmethod
    def _string_vazia_vira_none(cls, valor: object) -> object:
        """Normaliza string vazia (comum em `.env`/docker-compose sem valor) para `None`.

        Pydantic-settings NAO trata `""` como ausencia de valor para campos
        `Path | None` -- `Path("")` resolve para o diretorio atual (`.`), que
        e um valor "configurado" valido do ponto de vista do tipo, mas bypassa
        silenciosamente os fallbacks de fail-fast (Q-02) e schema padrao
        (Q-03), causando `GraphValidationError: Nao foi possivel ler o
        schema '.': [Errno 21] Is a directory` no lifespan do gateway.
        """
        if isinstance(valor, str) and valor.strip() == "":
            return None
        return valor

    @field_validator("governance_github_dir", mode="before")
    @classmethod
    def _github_dir_vazio_usa_default(cls, valor: object) -> object:
        """Normaliza string vazia para o default real (bug real de producao,
        2026-10-01, Addendum 5).

        Diferente de `governance_graph_path`/`governance_schema_path` (campos
        `Path | None`, onde string vazia vira `None`), `governance_github_dir`
        e `Path` simples (nao-Optional) -- string vazia aqui deve reaplicar o
        default real (`/governance/.github`) diretamente, nunca `Path('.')`
        nem `None`.
        """
        if isinstance(valor, str) and valor.strip() == "":
            return Path("/governance/.github")
        return valor

    # ------------------------------------------------------------------
    # MCP servers (RC2, bugfix 2026-10-02) — lista FECHADA fixada pelo
    # Security Checkpoint: apenas context-mode, tavily, codegraph. Nenhum
    # MCP server adicional e lido de config dinamica/arquivo externo
    # (mitigacao de registro arbitrario de processo). Credenciais (ex.:
    # Tavily) sao lidas EXCLUSIVAMENTE de variavel de ambiente ja existente
    # -- nunca hardcoded/duplicadas aqui (ver mcp_servers_catalog.py).
    # ------------------------------------------------------------------
    mcp_context_mode_enabled: bool = Field(
        default=True, alias="MCP_CONTEXT_MODE_ENABLED"
    )
    mcp_context_mode_command: str = Field(
        default="npx", alias="MCP_CONTEXT_MODE_COMMAND"
    )
    # Bug real investigado (2026-10-04): o default anterior
    # ("-y,@context-mode/mcp-server") usava um nome de pacote FICTICIO
    # (`@context-mode/mcp-server` retorna HTTP 404 no registry do npm --
    # nunca existiu). O nome REAL, confirmado contra `.vscode/mcp.json`
    # (configuracao ja funcional da propria IDE para este mesmo servidor
    # MCP), e simplesmente "context-mode" (sem escopo `@.../`).
    mcp_context_mode_args: str = Field(
        default="-y,context-mode", alias="MCP_CONTEXT_MODE_ARGS"
    )
    mcp_tavily_enabled: bool = Field(default=True, alias="MCP_TAVILY_ENABLED")
    mcp_tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")
    mcp_codegraph_enabled: bool = Field(default=True, alias="MCP_CODEGRAPH_ENABLED")
    # Bug real investigado (2026-10-04): o default anterior
    # (command="npx", args="-y,@codegraph/mcp-server") tambem usava um
    # pacote FICTICIO (404 no npm) E um mecanismo de invocacao errado --
    # `.vscode/mcp.json` confirma que `codegraph` e um binario CLI
    # instalado diretamente (nao via `npx`), invocado como
    # `codegraph mcp --multi-repo`.
    mcp_codegraph_command: str = Field(
        default="codegraph", alias="MCP_CODEGRAPH_COMMAND"
    )
    mcp_codegraph_args: str = Field(
        default="mcp,--multi-repo", alias="MCP_CODEGRAPH_ARGS"
    )

    @field_validator("mcp_context_mode_args", mode="before")
    @classmethod
    def _mcp_context_mode_args_vazio_usa_default(cls, valor: object) -> object:
        """Paridade com `_github_dir_vazio_usa_default`: string vazia reaplica
        o default real, nunca vira lista vazia apos `.split(",")`."""
        if isinstance(valor, str) and valor.strip() == "":
            return "-y,context-mode"
        return valor

    @field_validator("mcp_codegraph_args", mode="before")
    @classmethod
    def _mcp_codegraph_args_vazio_usa_default(cls, valor: object) -> object:
        if isinstance(valor, str) and valor.strip() == "":
            return "mcp,--multi-repo"
        return valor

    @field_validator("mcp_tavily_api_key", mode="before")
    @classmethod
    def _mcp_tavily_api_key_vazio_vira_none(cls, valor: object) -> object:
        """Nunca hardcoda a key -- string vazia (comum em .env sem valor
        preenchido) vira `None`, disparando o fail-closed de
        `mcp_servers_catalog.construir_mcp_servers` (servidor Tavily
        simplesmente nao e materializado sem credencial real)."""
        if isinstance(valor, str) and valor.strip() == "":
            return None
        return valor

    def validate_startup(self) -> None:
        """Recusa o startup se `gateway_api_key` ainda for o placeholder inseguro.

        Raises:
            InvalidGatewayConfigurationError: Se `gateway_api_key == "change-me"`.
        """
        if self.gateway_api_key == FORBIDDEN_GATEWAY_API_KEY:
            raise InvalidGatewayConfigurationError(
                "GATEWAY_API_KEY nao pode ser 'change-me' — defina um valor "
                "real no .env antes de subir o gateway."
            )


def get_settings() -> Settings:
    """Factory de `Settings` — ponto unico de override em testes (FastAPI Depends)."""
    return Settings()
