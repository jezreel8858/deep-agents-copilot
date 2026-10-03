"""Testes unitarios de `config.Settings`.

Cobre o bug real de producao encontrado ao subir `docker compose --profile
lobe --profile otel up`: variaveis de ambiente Pydantic-settings do tipo
`Path | None` nao tratam string vazia (`""`) como `None` por padrao --
`Path("")` resolve para o diretorio atual (`.`), nao para `None`. Isso
bypassava o fallback de schema padrao (Q-03) e causava
`GraphValidationError: Nao foi possivel ler o schema '.': [Errno 21] Is a
directory` no lifespan do gateway (fail-fast, Q-02) mesmo com
`GOVERNANCE_GRAPH_PATH` corretamente configurado.
"""

from __future__ import annotations

from pathlib import Path

from local_chat_gateway.config import Settings


class TestGovernanceSchemaPathVazioViraNone:
    """RED: `GOVERNANCE_SCHEMA_PATH=""` deve resultar em `None`, nao em `Path('.')`."""

    def test_schema_path_string_vazia_vira_none(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.setenv(
            "GOVERNANCE_GRAPH_PATH", "/governance/.github/agents/routing-graph.yaml"
        )
        monkeypatch.setenv("GOVERNANCE_SCHEMA_PATH", "")

        settings = Settings()

        assert settings.governance_schema_path is None

    def test_graph_path_string_vazia_vira_none(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.setenv("GOVERNANCE_GRAPH_PATH", "")

        settings = Settings()

        assert settings.governance_graph_path is None

    def test_schema_path_nao_vazio_preserva_valor_real(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.setenv(
            "GOVERNANCE_GRAPH_PATH", "/governance/.github/agents/routing-graph.yaml"
        )
        monkeypatch.setenv("GOVERNANCE_SCHEMA_PATH", "/governance/schema.json")

        settings = Settings()

        assert settings.governance_schema_path == Path("/governance/schema.json")

    def test_graph_path_nao_configurado_permanece_none_sem_env(
        self, monkeypatch
    ) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.delenv("GOVERNANCE_GRAPH_PATH", raising=False)

        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        assert settings.governance_graph_path is None


# ---------------------------------------------------------------------------
# Bug real de producao (2026-10-01, Addendum 5): `governance_pipeline.
# montar_contexto` usava um default calculado de `Path(__file__).resolve()
# .parents[4]`, que resolve incorretamente para `/usr/local` dentro do
# container Docker (local de instalacao do pacote via pip, nao o volume
# real `/governance:ro`). `governance_github_dir` torna esse diretorio
# configuravel via settings, seguindo o mesmo padrao de
# `GOVERNANCE_GRAPH_PATH`/`GOVERNANCE_SCHEMA_PATH`.
# ---------------------------------------------------------------------------


class TestGovernanceGithubDir:
    def test_default_aponta_para_volume_governance_do_container(
        self, monkeypatch
    ) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.delenv("GOVERNANCE_GITHUB_DIR", raising=False)

        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        assert settings.governance_github_dir == Path("/governance/.github")

    def test_override_via_env_var_e_respeitado(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.setenv("GOVERNANCE_GITHUB_DIR", "/outro/caminho/.github")

        settings = Settings()

        assert settings.governance_github_dir == Path("/outro/caminho/.github")

    def test_string_vazia_usa_default_em_vez_de_path_atual(self, monkeypatch) -> None:
        """Mesma protecao de `governance_graph_path`: string vazia nunca deve
        colapsar para `Path('.')` -- aqui o fallback e o default real
        (`/governance/.github`), nao `None` (o campo nao e Optional)."""
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.setenv("GOVERNANCE_GITHUB_DIR", "")

        settings = Settings()

        assert settings.governance_github_dir == Path("/governance/.github")


class TestMcpServersSettings:
    """T19-T21 (bugfix 2026-10-02, RC2) -- novos campos `Settings` para os
    3 MCP servers da lista fechada (context-mode, tavily, codegraph)."""

    def test_settings_mcp_context_mode_args_default_split_correto(
        self, monkeypatch
    ) -> None:
        # Bug real investigado (2026-10-04): o default anterior usava o
        # pacote ficticio "@context-mode/mcp-server" (404 no npm). O nome
        # real (confirmado contra `.vscode/mcp.json`) e "context-mode".
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        settings = Settings()
        assert settings.mcp_context_mode_args == "-y,context-mode"
        assert settings.mcp_context_mode_args.split(",") == [
            "-y",
            "context-mode",
        ]

    def test_settings_mcp_tavily_api_key_default_none(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        # Bug real investigado (2026-10-04): `delenv(raising=False)` so
        # garante ausencia se a var NUNCA estava setada no ambiente -- em
        # maquinas de dev com `TAVILY_API_KEY` real exportada no shell/perfil
        # do usuario (fora do `.env` do projeto), o teste falhava por
        # vazamento de estado ambiental. `setenv("")` forca determinismo
        # (string vazia -> `None` via `_mcp_tavily_api_key_vazio_vira_none`),
        # independente do que estiver no ambiente real.
        monkeypatch.setenv("TAVILY_API_KEY", "")
        settings = Settings()
        assert settings.mcp_tavily_api_key is None

    def test_settings_mcp_args_string_vazia_vira_default(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.setenv("MCP_CONTEXT_MODE_ARGS", "")
        monkeypatch.setenv("MCP_CODEGRAPH_ARGS", "")
        settings = Settings()
        assert settings.mcp_context_mode_args == "-y,context-mode"
        assert settings.mcp_codegraph_args == "mcp,--multi-repo"

    def test_settings_mcp_tavily_api_key_string_vazia_vira_none(
        self, monkeypatch
    ) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.setenv("TAVILY_API_KEY", "")
        settings = Settings()
        assert settings.mcp_tavily_api_key is None


class TestGatewayLogSettings:
    """T22-T24 (Fix 3, 2026-10-04) -- novos campos `Settings` para logging
    em arquivo aditivo (ver `logging_config.py`)."""

    def test_gateway_log_file_default(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.delenv("GATEWAY_LOG_FILE", raising=False)
        settings = Settings()
        assert settings.gateway_log_file == ".tmp/gateway.log"

    def test_gateway_log_max_bytes_default(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.delenv("GATEWAY_LOG_MAX_BYTES", raising=False)
        settings = Settings()
        assert settings.gateway_log_max_bytes == 5_242_880

    def test_gateway_log_backup_count_default_e_override(self, monkeypatch) -> None:
        monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
        monkeypatch.delenv("GATEWAY_LOG_BACKUP_COUNT", raising=False)
        settings = Settings()
        assert settings.gateway_log_backup_count == 3

        monkeypatch.setenv("GATEWAY_LOG_BACKUP_COUNT", "9")
        settings_override = Settings()
        assert settings_override.gateway_log_backup_count == 9
