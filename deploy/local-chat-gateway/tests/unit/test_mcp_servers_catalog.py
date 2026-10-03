"""Testes unitarios de `mcp_servers_catalog.construir_mcp_servers` (RC2).

T15-T18 do Plano de Implementacao (bugfix 2026-10-02): lista fechada de MCP
servers (context-mode, tavily, codegraph), env minimo (nunca herda
`os.environ` completo) e fail-closed de Tavily sem API key.
"""

from __future__ import annotations


import pytest

from local_chat_gateway.config import Settings
from local_chat_gateway.mcp_servers_catalog import construir_mcp_servers


def _settings_tudo_habilitado(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
    monkeypatch.setenv("TAVILY_API_KEY", "chave-tavily-de-teste")
    return Settings()


def test_construir_mcp_servers_lista_fechada_3_chaves_max(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _settings_tudo_habilitado(monkeypatch)
    resultado = construir_mcp_servers(settings)
    assert set(resultado.keys()) <= {"context-mode", "tavily", "codegraph"}
    assert set(resultado.keys()) == {"context-mode", "tavily", "codegraph"}


def test_construir_mcp_servers_env_minimo_nao_herda_os_environ_completo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SECRET_TOKEN", "x")
    settings = _settings_tudo_habilitado(monkeypatch)
    resultado = construir_mcp_servers(settings)
    assert "SECRET_TOKEN" not in resultado["context-mode"]["env"]
    assert "SECRET_TOKEN" not in resultado["codegraph"]["env"]


def test_construir_mcp_servers_tavily_usa_env_var_existente_sem_hardcode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
    monkeypatch.setenv("TAVILY_API_KEY", "abc123")
    settings = Settings()
    resultado = construir_mcp_servers(settings)
    assert resultado["tavily"]["headers"]["Authorization"] == "Bearer abc123"

    import inspect

    from local_chat_gateway import mcp_servers_catalog

    fonte = inspect.getsource(mcp_servers_catalog)
    assert "abc123" not in fonte  # nenhum valor literal de credencial no modulo


def test_construir_mcp_servers_todas_flags_false_retorna_vazio(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
    monkeypatch.setenv("MCP_CONTEXT_MODE_ENABLED", "false")
    monkeypatch.setenv("MCP_TAVILY_ENABLED", "false")
    monkeypatch.setenv("MCP_CODEGRAPH_ENABLED", "false")
    settings = Settings()
    assert construir_mcp_servers(settings) == {}


def test_construir_mcp_servers_omite_tavily_sem_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GATEWAY_API_KEY", "token-real-de-teste")
    # Bug real investigado (2026-10-04): `delenv(raising=False)` nao isola
    # de uma `TAVILY_API_KEY` real ja exportada no ambiente do desenvolvedor
    # (fora do `.env` do projeto) -- `setenv("")` forca ausencia
    # deterministica via `_mcp_tavily_api_key_vazio_vira_none`.
    monkeypatch.setenv("TAVILY_API_KEY", "")
    settings = Settings()
    resultado = construir_mcp_servers(settings)
    assert "tavily" not in resultado
    assert "context-mode" in resultado
    assert "codegraph" in resultado


def test_construir_mcp_servers_usa_nomes_de_pacote_reais_nao_ficticios(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bug real investigado (2026-10-04): defaults anteriores usavam
    "@context-mode/mcp-server"/"@codegraph/mcp-server" -- ambos HTTP 404 no
    npm, nunca existiram. Os nomes reais (confirmados contra
    `.vscode/mcp.json`, config ja funcional da IDE) sao "context-mode"
    (sem escopo) e o binario CLI direto "codegraph" (nao via npx)."""
    settings = _settings_tudo_habilitado(monkeypatch)
    resultado = construir_mcp_servers(settings)

    def _args_sem_wrapper_windows(args: list[str]) -> list[str]:
        # Em teste rodando no Windows, o primeiro elemento real fica apos
        # o wrapper `cmd.exe /c`; normaliza para comparar so os args finais.
        return args[2:] if args[:1] == ["/c"] else args

    context_mode_args = _args_sem_wrapper_windows(resultado["context-mode"]["args"])
    assert "@context-mode/mcp-server" not in " ".join(context_mode_args)
    assert "context-mode" in context_mode_args

    codegraph_args = _args_sem_wrapper_windows(resultado["codegraph"]["args"])
    assert "@codegraph/mcp-server" not in " ".join(codegraph_args)
    assert "mcp" in codegraph_args
    codegraph_command = resultado["codegraph"]["command"]
    assert codegraph_command in ("codegraph", "cmd.exe")


def test_construir_mcp_servers_windows_envolve_com_cmd_exe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No Windows (`os.name == "nt"`), o comando real e envolvido com
    `cmd.exe /c <command> <args...>` -- paridade exata com
    `.vscode/mcp.json` (scripts .cmd/.ps1 do npm nao sao executaveis
    nativos)."""
    monkeypatch.setattr("local_chat_gateway.mcp_servers_catalog.os.name", "nt")
    settings = _settings_tudo_habilitado(monkeypatch)
    resultado = construir_mcp_servers(settings)

    assert resultado["context-mode"]["command"] == "cmd.exe"
    assert resultado["context-mode"]["args"] == ["/c", "npx", "-y", "context-mode"]
    assert resultado["codegraph"]["command"] == "cmd.exe"
    assert resultado["codegraph"]["args"] == ["/c", "codegraph", "mcp", "--multi-repo"]


def test_construir_mcp_servers_posix_nao_envolve_com_cmd_exe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Em Linux/Docker (`os.name == "posix"`), nenhum wrapper e aplicado --
    comando roda direto."""
    monkeypatch.setattr("local_chat_gateway.mcp_servers_catalog.os.name", "posix")
    settings = _settings_tudo_habilitado(monkeypatch)
    resultado = construir_mcp_servers(settings)

    assert resultado["context-mode"]["command"] == "npx"
    assert resultado["context-mode"]["args"] == ["-y", "context-mode"]
    assert resultado["codegraph"]["command"] == "codegraph"
    assert resultado["codegraph"]["args"] == ["mcp", "--multi-repo"]

