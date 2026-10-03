"""mcp_servers_catalog — traduz `Settings` na lista FECHADA de MCP servers
(context-mode, tavily, codegraph) repassada a `client.create_session(
mcp_servers=...)` (RC2).

Lista fechada fixada pelo Security Checkpoint do bugfix 2026-10-02: NENHUM
MCP server alem destes tres e registrado, independentemente de configuracao
externa -- mitigacao de registro arbitrario de processo (prompt injection/
exfiltracao).

Env minimo (Security Checkpoint, mitigacao #3): cada MCP server stdio
recebe APENAS as variaveis de ambiente estritamente necessarias (nunca
`os.environ` completo do processo do gateway) -- evita vazar
`GATEWAY_API_KEY`, tokens do Copilot, etc. para o subprocesso MCP.

Formato confirmado por introspeccao real da wheel `github_copilot_sdk==
1.0.16` (T-01, 2026-10-02): `MCPStdioServerConfig`/`MCPHTTPServerConfig`
sao `TypedDict` com `total=False` -- dict literal simples e suficiente,
sem exigir dataclass/construtor proprio do SDK.
"""

from __future__ import annotations

import os
from typing import Any

from local_chat_gateway.config import Settings


def _env_minimo(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Monta env MINIMO para subprocesso stdio (mitigacao #3).

    Inclui apenas `PATH`/`SYSTEMROOT` (necessarios para resolver o
    executavel) + variaveis explicitamente passadas em `extra` -- nunca
    `dict(os.environ)` completo (evitaria vazar segredos do processo pai
    para o subprocesso MCP).
    """
    base = {"PATH": os.environ.get("PATH", "")}
    if os.name == "nt" and "SYSTEMROOT" in os.environ:
        base["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
    if extra:
        base.update(extra)
    return base


def _comando_e_args_stdio(command: str, args: list[str]) -> tuple[str, list[str]]:
    """Resolve `command`/`args` finais de um MCP server stdio, por SO.

    Bug real investigado (2026-10-04): no Windows, `npx` (e outros binarios
    globais do npm, como `codegraph`) sao scripts `.cmd`/`.ps1`, nao
    executaveis nativos -- spawnar o processo passando `command="npx"`
    diretamente (sem shell) falha silenciosamente ou nao resolve o PATH
    corretamente dependendo do mecanismo de subprocess da SDK. A config ja
    FUNCIONAL da propria IDE (`.vscode/mcp.json`) confirma o padrao
    necessario no Windows: envolver com `cmd.exe /c <command> <args...>`.
    Em outros SOs (Linux/Docker, onde o gateway tambem roda), `command` e
    executado diretamente, sem wrapper.
    """
    if os.name == "nt":
        return "cmd.exe", ["/c", command, *args]
    return command, args


def construir_mcp_servers(settings: Settings) -> dict[str, dict[str, Any]]:
    """Constroi o dict `mcp_servers` para `create_session(mcp_servers=...)`.

    Lista FECHADA: apenas as chaves `context-mode`, `tavily`, `codegraph`
    podem aparecer no retorno -- nunca um servidor arbitrario derivado de
    configuracao dinamica externa.

    Args:
        settings: Instancia de `Settings` (ver `config.get_settings`).

    Returns:
        dict[str, dict[str, Any]]: mapa `nome -> MCPServerConfig` (stdio ou
        http), pronto para `client.create_session(mcp_servers=...)`.
    """
    servidores: dict[str, dict[str, Any]] = {}

    if settings.mcp_context_mode_enabled:
        comando, args = _comando_e_args_stdio(
            settings.mcp_context_mode_command,
            settings.mcp_context_mode_args.split(","),
        )
        servidores["context-mode"] = {
            "type": "stdio",
            "command": comando,
            "args": args,
            "env": _env_minimo(),
        }

    if settings.mcp_tavily_enabled and settings.mcp_tavily_api_key:
        # Fallback fixado pelo Security Checkpoint (risco #2): nunca
        # hardcode/duplica a key -- se a env var nao existe, o servidor
        # Tavily simplesmente NAO e materializado (fail-closed).
        servidores["tavily"] = {
            "type": "http",
            "url": "https://mcp.tavily.com/mcp/",
            "headers": {"Authorization": f"Bearer {settings.mcp_tavily_api_key}"},
        }

    if settings.mcp_codegraph_enabled:
        comando, args = _comando_e_args_stdio(
            settings.mcp_codegraph_command,
            settings.mcp_codegraph_args.split(","),
        )
        servidores["codegraph"] = {
            "type": "stdio",
            "command": comando,
            "args": args,
            "env": _env_minimo(),
        }

    return servidores
