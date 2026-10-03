"""Testes unitários para `sdk_session` (Fase 3 — integração real com o SDK).

Usa injeção de módulo falso via `monkeypatch.setitem(sys.modules, ...)`
para exercitar o caminho real de `stream_chat` sem exigir o pacote
`github-copilot-sdk` instalado (extra opcional `[sdk]`).
"""

from __future__ import annotations

import asyncio
import sys
import types
from collections.abc import (  # noqa: F401 - kept for type-hints in docstrings
    AsyncIterator,
    Mapping,
)
from pathlib import Path
from typing import Any

import pytest

from local_chat_gateway.sdk_session import (
    SDKUnavailableError,
    _compor_prompt_com_sistema,
    read_sdk_token,
    stream_chat,
    stream_chat_ag_ui,
)


class TestReadSdkToken:
    """Testes de `read_sdk_token` (leitura de arquivo de token)."""

    def test_deve_levantar_erro_quando_arquivo_nao_existe(self, tmp_path: Path) -> None:
        caminho_inexistente = tmp_path / "nao-existe"
        with pytest.raises(SDKUnavailableError, match="nao encontrado"):
            read_sdk_token(str(caminho_inexistente))

    def test_deve_levantar_erro_quando_arquivo_esta_vazio(self, tmp_path: Path) -> None:
        arquivo_vazio = tmp_path / "token-vazio"
        arquivo_vazio.write_text("   \n", encoding="utf-8")
        with pytest.raises(SDKUnavailableError, match="esta vazio"):
            read_sdk_token(str(arquivo_vazio))

    def test_deve_retornar_token_sem_espacos_quando_arquivo_valido(
        self, tmp_path: Path
    ) -> None:
        arquivo = tmp_path / "token-valido"
        arquivo.write_text("  meu-token-secreto  \n", encoding="utf-8")
        assert read_sdk_token(str(arquivo)) == "meu-token-secreto"


class TestComporPromptComSistema:
    """Testes unitários puros de `_compor_prompt_com_sistema` (sem SDK)."""

    def test_deve_retornar_mensagens_unidas_inalteradas_quando_system_message_for_none(
        self,
    ) -> None:
        mensagens = "user: ola mundo\nassistant: como posso ajudar?"
        resultado = _compor_prompt_com_sistema(None, mensagens)
        assert resultado == mensagens

    def test_deve_prefixar_system_message_em_modo_append_quando_fornecido(
        self,
    ) -> None:
        mensagens = "user: ola mundo\nassistant: como posso ajudar?"
        system = "banner de teste"
        resultado = _compor_prompt_com_sistema(system, mensagens)
        assert resultado == f"banner de teste\n\n{mensagens}"


def _registrar_placeholders_novos_eventos_turn_recorder(
    fake_session_events: Any,
) -> None:
    """Registra placeholders dos eventos novos consumidos por
    `turn_recorder.py` (`AssistantUsageData`/`ModelCallFailureData`/
    `AssistantTurnRetryData`/`AssistantIntentData`/
    `SessionCompletionReceiptData`/`SessionTruncationData`/
    `SessionCompactionCompleteData`) E de `PermissionRequestShell` (bug real
    corrigido em 2026-10-02 -- `_identificador_e_seguro_nativo` passou a
    reconhecer nativamente comandos de shell/terminal via
    `isinstance(perm_request, PermissionRequestShell)`, ver
    `sdk_session._comando_shell_e_seguro`) no modulo falso `copilot.
    session_events` -- necessario APENAS para que o `import` dentro de
    `stream_chat`/`stream_chat_ag_ui` nao falhe com `ImportError`; nenhum
    destes testes legados exercita o conteudo real desses eventos (ver
    `TestStreamChatAgUiSubagentNesting`/`TestBridgeEdicaoArquivoFallback
    ResolvedPath` para os testes dedicados de `turn_recorder`, e
    `TestPermissionRequestShell` para os testes dedicados do reconhecimento
    nativo de comandos de shell).

    `AssistantUsageData` e' um placeholder construtivel de verdade (nao
    apenas `type(nome, (), {})` vazio) -- `TestStreamChatAgUiCreditsBadge`
    (2026-10-03) o instancia de fato via `_instalar_copilot_falso(...,
    usage_total_nano_aiu=...)` para exercitar o badge real de creditos
    ("<Modelo> · <N> Credits"); os demais eventos desta lista permanecem
    placeholders vazios -- nenhum teste alem deste exercita seu conteudo."""

    class AssistantUsageData:
        """Fake minimo e' suficiente: `turn_recorder.registrar_uso_assistente`
        so' le atributos via `getattr(dado, nome, None)` (duck typing),
        nunca isinstance/dataclass real."""

        def __init__(self, **kwargs: Any) -> None:
            for chave, valor in kwargs.items():
                setattr(self, chave, valor)

    class SessionUsageInfoData:
        """Fake construtivel (2026-10-03) -- mesma razao de
        `AssistantUsageData` acima: `turn_recorder.registrar_info_contexto`
        le `current_tokens`/`token_limit` via `getattr` (duck typing).
        `TestStreamChatAgUiContextWindowBadge` instancia de fato via
        `_instalar_copilot_falso(..., context_current_tokens=...,
        context_token_limit=...)` para exercitar o badge real de
        context-window ("N% contexto (X/Y tokens)")."""

        def __init__(self, **kwargs: Any) -> None:
            for chave, valor in kwargs.items():
                setattr(self, chave, valor)

    setattr(fake_session_events, "AssistantUsageData", AssistantUsageData)
    setattr(fake_session_events, "SessionUsageInfoData", SessionUsageInfoData)
    for nome in (
        "ModelCallFailureData",
        "AssistantTurnRetryData",
        "AssistantIntentData",
        "SessionCompletionReceiptData",
        "SessionTruncationData",
        "SessionCompactionCompleteData",
        "PermissionRequestShell",
    ):
        setattr(fake_session_events, nome, type(nome, (), {}))


def _instalar_copilot_falso(
    monkeypatch: pytest.MonkeyPatch,
    *,
    eventos_disparados: list[str],
    tool_name_esperado: str = "read_file",
    tipo_permission_request: str = "custom_tool",
    caminho_escrita: str = "/workspaces/app/main.py",
    subagent_agent_name: str = "python-bug-fixer",
    subagent_display_name: str = "Python Bug Fixer",
    subagent_falha: bool = False,
    subagent_erro: str = "falha simulada",
    shell_full_command_text: str = "git --no-pager status",
    shell_read_only: bool = True,
    mcp_tool_name: str = "ctx_batch_execute",
    mcp_server_name: str = "context-mode",
    mcp_read_only: bool = False,
    usage_total_nano_aiu: float | None = None,
    usage_model: str | None = None,
    context_current_tokens: int | None = None,
    context_token_limit: int | None = None,
) -> None:
    """Injeta um `copilot` falso em `sys.modules` simulando 1 sessao real.

    Simula: 2 eventos de texto (`AssistantMessageData`), 1 par
    start/complete de tool call (disparando o permission_handler via
    `PermissionRequestCustomTool`, ou aprovado nativamente sem consultar o
    handler via `PermissionRequestRead` -- controlado por
    `tipo_permission_request`), cujo retorno DEVE ser uma instancia tipada
    de `PermissionRequestResult` -- `PermissionDecisionApproveOnce`/
    `PermissionDecisionReject` -- e nao um dict puro, que faz o SDK real
    levantar `AttributeError: 'dict' object has no attribute 'to_dict'`,
    bug real reportado via Lobe Chat em 2026-09-29. Finaliza com
    `AssistantIdleData` -- nomes de evento reais, corrigidos via inspecao
    de uma sessao real com token do usuario (a hipotese original do spike
    RT-01 usava `AssistantMessageDeltaData`/`SessionIdleData`, que nunca
    sao emitidos nesta troca simples).
    """

    class AssistantMessageData:
        def __init__(self, content: str) -> None:
            self.content = content

    class ToolExecutionStartData:
        def __init__(self, tool_call_id: str, tool_name: str) -> None:
            self.tool_call_id = tool_call_id
            self.tool_name = tool_name

    class ToolExecutionCompleteData:
        # Nao tem campo `tool_name` na API real (confirmado por
        # `dataclasses.fields`) -- apenas `tool_call_id`, usado para
        # correlacionar com o nome capturado no evento de start.
        def __init__(self, tool_call_id: str) -> None:
            self.tool_call_id = tool_call_id

    class SubagentStartedData:
        """Fake de `SubagentStartedData` (RT-03, introspecao real via wheel
        `github_copilot_sdk==1.0.15`) -- campos confirmados minimos usados
        por `sdk_session._on_event`."""

        def __init__(
            self, *, tool_call_id: str, agent_name: str, agent_display_name: str = ""
        ) -> None:
            self.tool_call_id = tool_call_id
            self.agent_name = agent_name
            self.agent_display_name = agent_display_name

    class SubagentCompletedData:
        def __init__(
            self, *, tool_call_id: str, agent_name: str, agent_display_name: str = ""
        ) -> None:
            self.tool_call_id = tool_call_id
            self.agent_name = agent_name
            self.agent_display_name = agent_display_name

    class SubagentFailedData:
        def __init__(
            self,
            *,
            tool_call_id: str,
            agent_name: str,
            error: str,
            agent_display_name: str = "",
        ) -> None:
            self.tool_call_id = tool_call_id
            self.agent_name = agent_name
            self.agent_display_name = agent_display_name
            self.error = error

    class AssistantIdleData:
        pass

    class SessionErrorData:
        """Fake de `SessionErrorData` (bug real de producao, 2026-10-02):
        erro real da API do Copilot (cota mensal esgotada, rate limit,
        autenticacao) -- o SDK emite este evento em vez de levantar excecao
        Python, seguido de `AssistantIdleData` normal."""

        def __init__(self, *, error_code: str = "", message: str = "") -> None:
            self.error_code = error_code
            self.message = message

    class PermissionRequestRead:
        def __init__(self, path: str = "") -> None:
            self.path = path

    class PermissionRequestWrite:
        def __init__(self, file_name: str = "", resolved_path: str = "") -> None:
            self.file_name = file_name
            self.resolved_path = resolved_path

    class PermissionRequestMcp:
        def __init__(
            self, tool_name: str, read_only: bool = False, server_name: str = ""
        ) -> None:
            self.tool_name = tool_name
            self.read_only = read_only
            self.server_name = server_name

    class PermissionRequestCustomTool:
        def __init__(self, tool_name: str) -> None:
            self.tool_name = tool_name

    class PermissionRequestShell:
        """Fake de `PermissionRequestShell` (bug real corrigido, 2026-10-02 --
        ver `TestPermissionRequestShell`/`sdk_session._comando_shell_e_seguro`)."""

        def __init__(self, full_command_text: str, commands: list[Any]) -> None:
            self.full_command_text = full_command_text
            self.commands = commands

    class PermissionDecisionApproveOnce:
        pass

    class PermissionDecisionReject:
        def __init__(self, feedback: str | None = None) -> None:
            self.feedback = feedback

    class _Evento:
        def __init__(self, data: Any) -> None:
            self.data = data

    def _construir_permission_request() -> Any:
        if tipo_permission_request == "read":
            return PermissionRequestRead(path="/workspace/README.md")
        if tipo_permission_request == "write":
            return PermissionRequestWrite(resolved_path=caminho_escrita)
        if tipo_permission_request == "shell":
            return PermissionRequestShell(
                full_command_text=shell_full_command_text,
                commands=[
                    types.SimpleNamespace(
                        identifier=shell_full_command_text, read_only=shell_read_only
                    )
                ],
            )
        if tipo_permission_request == "mcp":
            return PermissionRequestMcp(
                tool_name=mcp_tool_name,
                read_only=mcp_read_only,
                server_name=mcp_server_name,
            )
        return PermissionRequestCustomTool(tool_name_esperado)

    class _FakeSession:
        def __init__(self, on_permission_request: Any) -> None:
            self._on_permission_request = on_permission_request
            self._callback: Any = None
            self.prompt_recebido: str | None = None

        def on(self, callback: Any) -> None:
            self._callback = callback

        async def send(
            self, prompt: str, *, attachments: Any = None
        ) -> None:
            assert prompt  # prompt concatenado nao deve ser vazio
            self.prompt_recebido = prompt
            decisao = self._on_permission_request(
                _construir_permission_request(),
                {"toolName": tool_name_esperado},
            )
            tipo_decisao = (
                "allow"
                if isinstance(decisao, PermissionDecisionApproveOnce)
                else "deny"
            )
            eventos_disparados.append(f"permission:{tipo_decisao}")

            assert self._callback is not None
            self._callback(_Evento(AssistantMessageData("ola ")))
            self._callback(
                _Evento(ToolExecutionStartData("call-1", tool_name_esperado))
            )
            # Simula o comportamento real confirmado (RT-03): quando a tool
            # e `run_subagent`, o SDK TAMBEM emite `SubagentStartedData`/
            # `SubagentCompletedData` para o MESMO `tool_call_id` -- ver
            # docstring de `sdk_session.stream_chat` sobre supressao da
            # linha generica neste caso.
            if tool_name_esperado == "run_subagent":
                self._callback(
                    _Evento(
                        SubagentStartedData(
                            tool_call_id="call-1",
                            agent_name=subagent_agent_name,
                            agent_display_name=subagent_display_name,
                        )
                    )
                )
            self._callback(_Evento(ToolExecutionCompleteData("call-1")))
            if tool_name_esperado == "run_subagent":
                if subagent_falha:
                    self._callback(
                        _Evento(
                            SubagentFailedData(
                                tool_call_id="call-1",
                                agent_name=subagent_agent_name,
                                agent_display_name=subagent_display_name,
                                error=subagent_erro,
                            )
                        )
                    )
                else:
                    self._callback(
                        _Evento(
                            SubagentCompletedData(
                                tool_call_id="call-1",
                                agent_name=subagent_agent_name,
                                agent_display_name=subagent_display_name,
                            )
                        )
                    )
            self._callback(_Evento(AssistantMessageData("mundo")))
            if usage_total_nano_aiu is not None:
                # `AssistantUsageData` real (2026-10-03, badge de creditos):
                # referenciada via `fake_session_events.AssistantUsageData`
                # (nao como nome solto) -- a classe construtivel real e'
                # definida em `_registrar_placeholders_novos_eventos_turn_
                # recorder`, fora do escopo lexico desta funcao/metodo.
                # `copilot_usage` e' um objeto SIMPLES com `.total_nano_aiu`
                # (duck typing -- `turn_recorder.registrar_uso_assistente`
                # nunca faz isinstance contra o tipo real do SDK).
                self._callback(
                    _Evento(
                        fake_session_events.AssistantUsageData(
                            model=usage_model,
                            copilot_usage=types.SimpleNamespace(
                                total_nano_aiu=usage_total_nano_aiu
                            ),
                        )
                    )
                )
            if context_current_tokens is not None or context_token_limit is not None:
                # `SessionUsageInfoData` real (2026-10-03, badge de
                # context-window): mesmo padrao de `AssistantUsageData`
                # acima -- referenciada via `fake_session_events.
                # SessionUsageInfoData`, nunca como nome solto.
                self._callback(
                    _Evento(
                        fake_session_events.SessionUsageInfoData(
                            current_tokens=context_current_tokens,
                            token_limit=context_token_limit,
                        )
                    )
                )
            self._callback(_Evento(AssistantIdleData()))

        async def __aenter__(self) -> "_FakeSession":
            return self

        async def __aexit__(self, *exc: object) -> None:
            return None

    class _FakeClient:
        ultima_instancia: "_FakeClient | None" = None

        def __init__(self, github_token: str) -> None:
            self.github_token = github_token
            self.working_directory_recebido: str | None = None
            self.additional_directories_recebido: list[str] | None = None
            self.enable_file_hooks_recebido: bool | None = None
            self.enable_config_discovery_recebido: bool | None = None
            self.system_message_recebido: Any = None
            self.custom_agents_recebido: Any = None
            self.ultima_sessao: "_FakeSession | None" = None
            type(self).ultima_instancia = self

        async def create_session(
            self,
            *,
            on_permission_request: Any,
            model: str | None,
            session_id: str | None = None,
            working_directory: str | None = None,
            additional_directories: list[str] | None = None,
            enable_file_hooks: bool | None = None,
            enable_config_discovery: bool | None = None,
            system_message: Any = None,
            custom_agents: Any = None,
            mcp_servers: Any = None,
            excluded_tools: Any = None,
            # Aceitos apenas para compatibilidade com `stream_chat_ag_ui`
            # (RT-05) -- esta fake nao exercita elicitation/`ask_user`,
            # apenas precisa nao quebrar com `TypeError: unexpected keyword
            # argument` quando reusada por testes de `stream_chat_ag_ui`
            # (ex.: `TestStreamChatAgUiCreditsBadge`, 2026-10-03).
            on_elicitation_request: Any = None,
            on_user_input_request: Any = None,
            ask_user_variant: str | None = None,
        ) -> _FakeSession:
            self.session_id_recebido = session_id
            self.working_directory_recebido = working_directory
            self.additional_directories_recebido = additional_directories
            self.enable_file_hooks_recebido = enable_file_hooks
            self.enable_config_discovery_recebido = enable_config_discovery
            self.system_message_recebido = system_message
            self.custom_agents_recebido = custom_agents
            self.mcp_servers_recebido = mcp_servers
            self.excluded_tools_recebido = excluded_tools
            sessao = _FakeSession(on_permission_request)
            self.ultima_sessao = sessao
            return sessao

        async def __aenter__(self) -> "_FakeClient":
            return self

        async def __aexit__(self, *exc: object) -> None:
            return None

    fake_copilot = types.ModuleType("copilot")
    fake_copilot.CopilotClient = _FakeClient  # type: ignore[attr-defined]
    fake_copilot.FakeClientRef = _FakeClient  # type: ignore[attr-defined]

    fake_session_events = types.ModuleType("copilot.session_events")
    setattr(fake_session_events, "AssistantMessageData", AssistantMessageData)
    setattr(fake_session_events, "ToolExecutionStartData", ToolExecutionStartData)
    setattr(fake_session_events, "ToolExecutionCompleteData", ToolExecutionCompleteData)
    setattr(fake_session_events, "SubagentStartedData", SubagentStartedData)
    setattr(fake_session_events, "SubagentCompletedData", SubagentCompletedData)
    setattr(fake_session_events, "SubagentFailedData", SubagentFailedData)
    setattr(fake_session_events, "AssistantIdleData", AssistantIdleData)
    setattr(fake_session_events, "SessionErrorData", SessionErrorData)
    setattr(fake_session_events, "PermissionRequestRead", PermissionRequestRead)
    setattr(fake_session_events, "PermissionRequestWrite", PermissionRequestWrite)
    setattr(fake_session_events, "PermissionRequestMcp", PermissionRequestMcp)
    setattr(
        fake_session_events, "PermissionRequestCustomTool", PermissionRequestCustomTool
    )
    _registrar_placeholders_novos_eventos_turn_recorder(fake_session_events)
    # Sobrescreve o placeholder generico com a classe real definida acima --
    # PRECISA vir DEPOIS da chamada acima, que tambem registra um placeholder
    # vazio para "PermissionRequestShell" (necessario apenas para o `import`
    # nao falhar nas outras fixtures deste modulo que nao exercitam Shell).
    setattr(fake_session_events, "PermissionRequestShell", PermissionRequestShell)

    fake_rpc = types.ModuleType("copilot.generated.rpc")
    setattr(fake_rpc, "PermissionDecisionApproveOnce", PermissionDecisionApproveOnce)
    setattr(fake_rpc, "PermissionDecisionReject", PermissionDecisionReject)

    monkeypatch.setitem(sys.modules, "copilot", fake_copilot)
    monkeypatch.setitem(sys.modules, "copilot.session_events", fake_session_events)
    monkeypatch.setitem(sys.modules, "copilot.generated.rpc", fake_rpc)


class TestStreamChat:
    """Testes de `stream_chat` com um `copilot` falso injetado em sys.modules."""

    async def test_deve_levantar_sdk_unavailable_quando_pacote_nao_instalado(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delitem(sys.modules, "copilot", raising=False)

        from local_chat_gateway.api.schemas import ChatMessage

        with pytest.raises(SDKUnavailableError, match="nao instalado"):
            async for _ in stream_chat(
                token="tok",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: False,
            ):
                pass

    async def test_deve_emitir_chunks_na_ordem_correta_quando_sdk_real_simulado(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from local_chat_gateway.api.schemas import ChatMessage

        eventos_disparados: list[str] = []
        _instalar_copilot_falso(monkeypatch, eventos_disparados=eventos_disparados)

        permissoes_recebidas: list[tuple[str, dict[str, Any]]] = []

        def handler(tool_name: str, params: Mapping[str, Any]) -> bool:
            permissoes_recebidas.append((tool_name, dict(params)))
            return tool_name == "read_file"

        chunks = [
            chunk
            async for chunk in stream_chat(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=handler,
            )
        ]

        # 1 (role) + 4 (2 texto + start + complete) + 1 (stop) = 6
        assert len(chunks) == 6
        assert chunks[0].choices[0].delta.role == "assistant"
        assert chunks[0].choices[0].delta.content is None

        assert chunks[1].choices[0].delta.content == "ola "
        assert "iniciando" in (chunks[2].choices[0].delta.content or "")
        assert "concluido" in (chunks[3].choices[0].delta.content or "")
        assert chunks[4].choices[0].delta.content == "mundo"

        assert chunks[5].choices[0].finish_reason == "stop"
        assert chunks[5].choices[0].delta.content is None

        # Permission handler foi chamado com o tool_name correto e a decisao
        # (True -> "allow") foi corretamente traduzida para o bridge do SDK.
        assert permissoes_recebidas == [("read_file", {"toolName": "read_file"})]
        assert eventos_disparados == ["permission:allow"]

    async def test_deve_exibir_nome_real_do_subagent_e_suprimir_linha_generica(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """RT-03: quando a tool e `run_subagent`, o SDK real emite TAMBEM os
        eventos dedicados `SubagentStartedData`/`SubagentCompletedData`
        (confirmados por introspecao da wheel `github_copilot_sdk==1.0.15`)
        -- o stream deve exibir o NOME REAL do agent (`agent_display_name`)
        e suprimir a linha generica "tool: run_subagent (iniciando)/concluido"
        para nao duplicar a informacao. Pedido real do usuario: visibilidade
        de QUAL agent foi invocado no stream da LobeChat (nao so que uma
        delegacao ocorreu)."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=[],
            tool_name_esperado="run_subagent",
        )

        chunks = [
            chunk
            async for chunk in stream_chat(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
            )
        ]

        conteudo_inicio = chunks[2].choices[0].delta.content or ""
        conteudo_fim = chunks[3].choices[0].delta.content or ""

        assert "Subagent invocado" in conteudo_inicio
        assert "Python Bug Fixer" in conteudo_inicio
        assert "iniciando" in conteudo_inicio
        assert "tool: run_subagent" not in conteudo_inicio

        assert "Subagent concluido" in conteudo_fim
        assert "Python Bug Fixer" in conteudo_fim
        assert "tool: run_subagent" not in conteudo_fim

    async def test_deve_usar_agent_name_quando_display_name_vazio(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`agent_display_name` pode vir vazio -- deve cair para `agent_name`
        (identificador tecnico, ex.: `python-bug-fixer`) em vez de exibir
        string vazia."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=[],
            tool_name_esperado="run_subagent",
            subagent_agent_name="python-bug-fixer",
            subagent_display_name="",
        )

        chunks = [
            chunk
            async for chunk in stream_chat(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
            )
        ]

        conteudo_inicio = chunks[2].choices[0].delta.content or ""
        assert "python-bug-fixer" in conteudo_inicio

    async def test_deve_exibir_erro_quando_subagent_falha(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`SubagentFailedData` (RT-03, campo `error: str` obrigatorio)
        deve ser renderizado com o nome do agent + mensagem de erro --
        util para o usuario identificar NO PROPRIO STREAM qual agent
        falhou durante uma delegacao, sem depender apenas do Langfuse."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=[],
            tool_name_esperado="run_subagent",
            subagent_agent_name="python-feature-developer",
            subagent_display_name="",
            subagent_falha=True,
            subagent_erro="timeout apos 120s",
        )

        chunks = [
            chunk
            async for chunk in stream_chat(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
            )
        ]

        conteudo_fim = chunks[3].choices[0].delta.content or ""
        assert "Subagent falhou" in conteudo_fim
        assert "python-feature-developer" in conteudo_fim
        assert "timeout apos 120s" in conteudo_fim

    async def test_deve_usar_workspaces_como_working_directory_padrao(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`working_directory="/workspaces"` (default) DEVE ser repassado ao
        `create_session` do SDK real -- sem isso, o SDK usa o CWD do
        processo (`/app`, o `WORKDIR` da imagem, read-only e sem nenhum
        repositorio do usuario), causando "permissao negada"/"nenhum
        repositorio carregado" mesmo com a sessao real conectada (bug
        real reportado via Lobe Chat em 2026-09-29). O default mudou de
        `/workspace` (1 unico projeto) para `/workspaces` (diretorio-pai
        comum de TODOS os projetos registrados -- pedido do usuario para
        acesso automatico multi-projeto)."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.working_directory_recebido == "/workspaces"
        assert instancia.additional_directories_recebido is None

    async def test_deve_desabilitar_hooks_e_descoberta_de_config_por_padrao(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`enable_file_hooks=False`/`enable_config_discovery=False` DEVEM
        ser repassados ao `create_session` -- sem isso, o SDK descobre e
        tenta EXECUTAR hooks/config customizados de QUALQUER projeto sob
        `working_directory` (ex.: `.github/hooks/*.json` deste proprio
        repositorio, deep-agents-copilot), quebrando com "um hook de
        contexto ... esta bloqueando todas as ferramentas" mesmo ao
        perguntar sobre um projeto IRMAO (bug real reportado via Lobe Chat
        em 2026-09-29, 4a rodada)."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.enable_file_hooks_recebido is False
        assert instancia.enable_config_discovery_recebido is False

    async def test_deve_repassar_additional_directories_ao_create_session(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`additional_directories` (paths de projetos fora de
        `working_directory`) DEVE ser repassado como lista ao SDK real."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
            additional_directories=["/outros/projeto-x", "/outros/projeto-y"],
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.additional_directories_recebido == [
            "/outros/projeto-x",
            "/outros/projeto-y",
        ]

    async def test_deve_aprovar_permissionrequestread_sem_chamar_handler(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`PermissionRequestRead` e sempre seguro (leitura pura) -- deve ser
        aprovado nativamente pela ponte, sem sequer consultar o
        `permission_handler` do chamador."""
        from local_chat_gateway.api.schemas import ChatMessage

        eventos_disparados: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="read",
        )

        handler_foi_chamado = False

        def handler_que_nunca_deveria_ser_chamado(
            tool_name: str, params: Mapping[str, Any]
        ) -> bool:
            nonlocal handler_foi_chamado
            handler_foi_chamado = True
            return False  # se o handler for chamado, forcaria "deny"

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=handler_que_nunca_deveria_ser_chamado,
        ):
            pass

        assert not handler_foi_chamado
        assert eventos_disparados == ["permission:allow"]

    async def test_deve_repassar_session_id_ao_create_session(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`session_id` deve ser repassado ao `create_session` do SDK real."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
            session_id="minha-sessao-persistida-456",
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.session_id_recebido == "minha-sessao-persistida-456"

    async def test_deve_rejeitar_escrita_em_modo_read_only(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Em modo `read_only`, tentativas de escrita sao sempre negadas."""
        from local_chat_gateway.api.schemas import ChatMessage

        eventos: list[str] = []
        _instalar_copilot_falso(
            monkeypatch, eventos_disparados=eventos, tipo_permission_request="write"
        )

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="escreva")],
            permission_handler=lambda *_: True,
            permission_mode="read_only",
        ):
            pass

        assert eventos == ["permission:deny"]

    async def test_deve_rejeitar_escrita_em_modo_propose(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Em modo `propose`, alteracoes sao negadas com instrucao de diff."""
        from local_chat_gateway.api.schemas import ChatMessage

        eventos: list[str] = []
        _instalar_copilot_falso(
            monkeypatch, eventos_disparados=eventos, tipo_permission_request="write"
        )

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="escreva")],
            permission_handler=lambda *_: True,
            permission_mode="propose",
        ):
            pass

        assert eventos == ["permission:deny"]

    async def test_deve_rejeitar_escrita_em_modo_apply_se_checkpoint_aberto(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Em modo `apply`, escrita e bloqueada se houver checkpoint pendente."""
        from local_chat_gateway.api.schemas import ChatMessage

        eventos: list[str] = []
        _instalar_copilot_falso(
            monkeypatch, eventos_disparados=eventos, tipo_permission_request="write"
        )

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="escreva")],
            permission_handler=lambda *_: True,
            permission_mode="apply",
            checkpoint_aberto=True,
        ):
            pass

        assert eventos == ["permission:deny"]

    async def test_deve_rejeitar_escrita_em_modo_apply_se_caminho_bloqueado(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Guarda 4: escrita em `.env`, `.git` ou `.pem` e rejeitada."""
        from local_chat_gateway.api.schemas import ChatMessage

        eventos: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos,
            tipo_permission_request="write",
            caminho_escrita="/workspaces/app/.env.local",
        )

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="escreva")],
            permission_handler=lambda *_: True,
            permission_mode="apply",
            checkpoint_aberto=False,
        ):
            pass

        assert eventos == ["permission:deny"]

    async def test_deve_aprovar_escrita_em_modo_apply_se_caminho_seguro(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Em modo `apply`, caminho valido sem checkpoint aberto e aprovado."""
        from local_chat_gateway.api.schemas import ChatMessage

        eventos: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos,
            tipo_permission_request="write",
            caminho_escrita="/workspaces/app/src/index.ts",
        )

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="escreva")],
            permission_handler=lambda *_: True,
            permission_mode="apply",
            checkpoint_aberto=False,
        ):
            pass

        assert eventos == ["permission:allow"]

    async def test_deve_repassar_system_message_nativo_ao_create_session(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`system_message` DEVE ir via mecanismo NATIVO do SDK
        (`client.create_session(system_message={"mode": "append", ...})`),
        NUNCA mais concatenado como texto no prompt de `session.send` --
        o Claude subjacente ignorava o banner concatenado como conteudo
        nao-confiavel do usuario (bug real via Lobe Chat, 2026-09-30)."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
            system_message="banner de teste",
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.system_message_recebido == {
            "mode": "append",
            "content": "banner de teste",
        }
        assert instancia.ultima_sessao is not None
        assert instancia.ultima_sessao.prompt_recebido == "user: oi"

    async def test_deve_enviar_prompt_sem_prefixo_quando_system_message_for_omitido(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regressao: chamada sem system_message produz prompt legado sem prefixo."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.ultima_sessao is not None
        assert instancia.ultima_sessao.prompt_recebido == "user: oi"
        assert instancia.system_message_recebido is None

    async def test_deve_enviar_prompt_sem_prefixo_quando_system_message_for_none_explicito(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regressao: chamada com system_message=None explicito produz prompt legado."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
            system_message=None,
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.ultima_sessao is not None
        assert instancia.ultima_sessao.prompt_recebido == "user: oi"

    async def test_deve_repassar_custom_agents_ao_create_session(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """RT-04: `custom_agents` (catalogo de `.github/agents/*.agent.md`,
        descoberto por `agent_catalog.descobrir_custom_agents`) DEVE ser
        repassado NATIVAMENTE ao `create_session` -- sem isso, `run_subagent`
        fica inerte (bug real confirmado por teste ao vivo: o modelo
        respondia nao ter acesso a `run_subagent`, pois o SDK nao descobre
        `.github/agents/*.agent.md` automaticamente mesmo com
        `enable_config_discovery=True`, issue github/copilot-sdk#1080)."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        catalogo_fake = [
            {
                "name": "python-bug-fixer",
                "description": "Especialista em bugs Python",
                "prompt": "Voce e especialista em bugs Python.",
                "infer": True,
            }
        ]

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
            custom_agents=catalogo_fake,
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.custom_agents_recebido == catalogo_fake

    async def test_deve_repassar_custom_agents_none_quando_catalogo_vazio(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lista vazia (ou `None`) NAO deve virar `[]` no `create_session` --
        preserva o comportamento legado de "nenhum custom agent"."""
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
            custom_agents=[],
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.custom_agents_recebido is None


class TestStreamChatAgUiSubagentNesting:
    """Testes de `stream_chat_ag_ui` para o aninhamento nativo AG-UI de
    acoes (tool calls/texto) de um subagent dentro do seu proprio colapse
    no front-end, via o campo `subagent_run_id` (pedido real do usuario,
    2026-10-02, paridade com o chat Copilot da IDE -- ver screenshot
    comparando "agent-router finished execution." colapsavel com as acoes
    aninhadas).

    Cada evento relevante do protocolo AG-UI (`ToolCallStartEvent`/
    `ToolCallEndEvent`/`ToolCallResultEvent`/`TextMessageStartEvent`/
    `TextMessageContentEvent`/`TextMessageEndEvent`) possui um campo
    OPCIONAL `subagent_run_id` (confirmado por introspecao real de
    `ag_ui.core.*.model_fields`) que o front-end usa para agrupar a acao
    dentro do colapse certo. Antes desta correcao, `sdk_session._on_event`
    NUNCA preenchia esse campo -- toda tool call/texto emitido DURANTE a
    execucao de um subagent aparecia solto no timeline principal.
    """

    def _instalar_copilot_falso_com_tool_aninhada(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fake minimo e dedicado (nao reaproveita `_instalar_copilot_falso`,
        cuja sequencia fixa nao simula uma tool call ACONTECENDO DENTRO de
        um subagent): simula 1 tool call de NIVEL SUPERIOR (`read_file`,
        FORA de qualquer subagent) seguida de 1 `run_subagent` cuja propria
        execucao interna dispara outra tool call (`grep_search`, DENTRO do
        subagent) antes de concluir.
        """

        class AssistantMessageData:
            def __init__(self, content: str) -> None:
                self.content = content

        class ToolExecutionStartData:
            def __init__(self, tool_call_id: str, tool_name: str) -> None:
                self.tool_call_id = tool_call_id
                self.tool_name = tool_name

        class ToolExecutionCompleteData:
            def __init__(self, tool_call_id: str) -> None:
                self.tool_call_id = tool_call_id

        class SubagentStartedData:
            def __init__(
                self,
                *,
                tool_call_id: str,
                agent_name: str,
                agent_display_name: str = "",
            ) -> None:
                self.tool_call_id = tool_call_id
                self.agent_name = agent_name
                self.agent_display_name = agent_display_name

        class SubagentCompletedData:
            def __init__(
                self,
                *,
                tool_call_id: str,
                agent_name: str,
                agent_display_name: str = "",
            ) -> None:
                self.tool_call_id = tool_call_id
                self.agent_name = agent_name
                self.agent_display_name = agent_display_name

        class AssistantIdleData:
            pass

        class PermissionRequestCustomTool:
            def __init__(self, tool_name: str) -> None:
                self.tool_name = tool_name

        class PermissionDecisionApproveOnce:
            pass

        class PermissionDecisionReject:
            def __init__(self, feedback: str | None = None) -> None:
                self.feedback = feedback

        class _Evento:
            def __init__(self, data: Any) -> None:
                self.data = data

        class _FakeSession:
            def __init__(self, on_permission_request: Any) -> None:
                self._on_permission_request = on_permission_request
                self._callback: Any = None

            def on(self, callback: Any) -> None:
                self._callback = callback

            async def send(self, prompt: str, attachments: Any = None) -> None:
                assert self._callback is not None
                # `_bridge_permissao` em `stream_chat_ag_ui` e ASSINCRONO --
                # o SDK real suporta `Awaitable[...]` no callback
                # `on_permission_request`; aqui simula o mesmo contrato.
                resultado = self._on_permission_request(
                    PermissionRequestCustomTool("read_file"), {"toolName": "read_file"}
                )
                if asyncio.iscoroutine(resultado):
                    await resultado
                # 1) Tool call de NIVEL SUPERIOR -- fora de qualquer subagent.
                self._callback(_Evento(ToolExecutionStartData("call-top", "read_file")))
                self._callback(_Evento(ToolExecutionCompleteData("call-top")))
                # 2) `run_subagent` -- abre o subagent "call-sub".
                self._callback(
                    _Evento(ToolExecutionStartData("call-sub", "run_subagent"))
                )
                self._callback(
                    _Evento(
                        SubagentStartedData(
                            tool_call_id="call-sub", agent_name="bug-triage"
                        )
                    )
                )
                # 3) Tool call DENTRO do subagent -- deve carregar
                #    `subagent_run_id="call-sub"` em start/end/result.
                self._callback(
                    _Evento(ToolExecutionStartData("call-nested", "grep_search"))
                )
                self._callback(_Evento(ToolExecutionCompleteData("call-nested")))
                # 4) Fecha o subagent e a tool call `run_subagent` original.
                self._callback(_Evento(ToolExecutionCompleteData("call-sub")))
                self._callback(
                    _Evento(
                        SubagentCompletedData(
                            tool_call_id="call-sub", agent_name="bug-triage"
                        )
                    )
                )
                self._callback(_Evento(AssistantMessageData("concluido")))
                self._callback(_Evento(AssistantIdleData()))

            async def __aenter__(self) -> "_FakeSession":
                return self

            async def __aexit__(self, *exc: object) -> None:
                return None

        class _FakeClient:
            def __init__(self, github_token: str) -> None:
                self.github_token = github_token

            async def create_session(
                self, *, on_permission_request: Any, **_kwargs: Any
            ) -> _FakeSession:
                return _FakeSession(on_permission_request)

            async def __aenter__(self) -> "_FakeClient":
                return self

            async def __aexit__(self, *exc: object) -> None:
                return None

        fake_copilot = types.ModuleType("copilot")
        fake_copilot.CopilotClient = _FakeClient  # type: ignore[attr-defined]

        fake_session_events = types.ModuleType("copilot.session_events")
        setattr(fake_session_events, "AssistantMessageData", AssistantMessageData)
        setattr(fake_session_events, "ToolExecutionStartData", ToolExecutionStartData)
        setattr(
            fake_session_events, "ToolExecutionCompleteData", ToolExecutionCompleteData
        )
        setattr(fake_session_events, "SubagentStartedData", SubagentStartedData)
        setattr(fake_session_events, "SubagentCompletedData", SubagentCompletedData)
        setattr(
            fake_session_events,
            "SubagentFailedData",
            type("SubagentFailedData", (), {}),
        )
        setattr(fake_session_events, "AssistantIdleData", AssistantIdleData)
        setattr(
            fake_session_events, "SessionErrorData", type("SessionErrorData", (), {})
        )
        setattr(
            fake_session_events,
            "PermissionRequestRead",
            type("PermissionRequestRead", (), {}),
        )
        setattr(
            fake_session_events,
            "PermissionRequestWrite",
            type("PermissionRequestWrite", (), {}),
        )
        setattr(
            fake_session_events,
            "PermissionRequestMcp",
            type("PermissionRequestMcp", (), {}),
        )
        setattr(
            fake_session_events,
            "PermissionRequestCustomTool",
            PermissionRequestCustomTool,
        )
        _registrar_placeholders_novos_eventos_turn_recorder(fake_session_events)

        fake_rpc = types.ModuleType("copilot.generated.rpc")
        setattr(
            fake_rpc, "PermissionDecisionApproveOnce", PermissionDecisionApproveOnce
        )
        setattr(fake_rpc, "PermissionDecisionReject", PermissionDecisionReject)

        monkeypatch.setitem(sys.modules, "copilot", fake_copilot)
        monkeypatch.setitem(sys.modules, "copilot.session_events", fake_session_events)
        monkeypatch.setitem(sys.modules, "copilot.generated.rpc", fake_rpc)

    async def test_deve_marcar_subagent_run_id_apenas_em_acoes_dentro_do_subagent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._instalar_copilot_falso_com_tool_aninhada(monkeypatch)

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
            )
        ]

        from ag_ui.core import (
            SubagentStartedEvent,
            ToolCallEndEvent,
            ToolCallResultEvent,
            ToolCallStartEvent,
        )

        inicios_tool = {
            e.tool_call_id: e.subagent_run_id
            for e in eventos
            if isinstance(e, ToolCallStartEvent)
        }
        fins_tool = {
            e.tool_call_id: e.subagent_run_id
            for e in eventos
            if isinstance(e, ToolCallEndEvent)
        }
        resultados_tool = {
            e.tool_call_id: e.subagent_run_id
            for e in eventos
            if isinstance(e, ToolCallResultEvent)
        }
        subagent_started = next(
            e for e in eventos if isinstance(e, SubagentStartedEvent)
        )

        # Tool call de NIVEL SUPERIOR (fora do subagent): sem `subagent_run_id`.
        assert inicios_tool["call-top"] is None
        assert fins_tool["call-top"] is None
        assert resultados_tool["call-top"] is None

        # Tool call DENTRO do subagent: `subagent_run_id` == id do subagent.
        assert inicios_tool["call-nested"] == "call-sub"
        assert fins_tool["call-nested"] == "call-sub"
        assert resultados_tool["call-nested"] == "call-sub"

        # O proprio `run_subagent` (tool_call_id "call-sub") e suprimido do
        # fluxo generico de ToolCall (coberto pelo `SubagentStartedEvent`).
        assert "call-sub" not in inicios_tool
        assert subagent_started.subagent_run_id == "call-sub"

    async def test_deve_emitir_badge_deterministico_de_agente_ativo_para_subagent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Bug real reportado pelo usuario via screenshot (2026-10-02): o
        badge "Agente Ativo" dentro do colapse de um subagent aparecia como
        texto puro (sem icone/negrito/modelo) -- gerado pelo proprio modelo
        do subagent seguindo o banner universal de `agent-contracts/SKILL.md`
        § 0, inconsistente com o badge deterministico do agent de NIVEL
        SUPERIOR. Agora `SubagentStartedData` TAMBEM emite um badge
        deterministico (mesmo formato: icone 🧭 + negrito + `· <modelo>`),
        tageado com `subagent_run_id` para renderizar dentro do colapse
        certo."""
        self._instalar_copilot_falso_com_tool_aninhada(monkeypatch)

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
                custom_agents=[{"name": "bug-triage", "model": "Claude Opus 5.5"}],
            )
        ]

        from ag_ui.core import TextMessageContentEvent

        conteudos_do_subagent = [
            e.delta
            for e in eventos
            if isinstance(e, TextMessageContentEvent)
            and e.subagent_run_id == "call-sub"
        ]
        assert (
            conteudos_do_subagent
        ), "nenhum TextMessageContentEvent tageado com o subagent"

        badge = conteudos_do_subagent[0]
        assert "🧭" in badge
        assert "**Agente Ativo:**" in badge
        assert "bug-triage" in badge
        assert "Claude Opus 5.5" in badge

    async def test_nao_deve_quebrar_quando_subagent_sem_model_no_catalogo(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Agent sem `model:` no frontmatter (campo opcional) ou ausente do
        catalogo -- o badge do subagent deve degradar graciosamente (sem
        `· <modelo>`), igual ao comportamento ja estabelecido para o badge
        do agent de nivel superior."""
        self._instalar_copilot_falso_com_tool_aninhada(monkeypatch)

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
                custom_agents=None,
            )
        ]

        from ag_ui.core import TextMessageContentEvent

        conteudos_do_subagent = [
            e.delta
            for e in eventos
            if isinstance(e, TextMessageContentEvent)
            and e.subagent_run_id == "call-sub"
        ]
        badge = conteudos_do_subagent[0]
        assert "🧭" in badge
        assert "bug-triage" in badge
        assert "·" not in badge


class TestBridgeEdicaoArquivoFallbackResolvedPath:
    """Bug real corrigido (2026-10-02, reportado pelo usuario via screenshot):
    pedir para alterar poucas linhas de um arquivo EXISTENTE fazia o
    `FileEditBridge.tsx` mostrar o arquivo INTEIRO como "adicionado" (ex.:
    "+423 -0" num README com ~424 linhas, sem nenhuma remocao). Causa raiz:
    `perm_request.resolved_path` vem VAZIO para esse tipo de escrita --
    `_ler_conteudo_atual_arquivo("")` cai no ramo "arquivo ainda nao existe"
    e retorna `""`, fazendo `_gerar_linhas_diff_completo` comparar o
    conteudo proposto inteiro contra um "antigo" em branco. O guard de
    seguranca (`_caminho_escrita_seguro`) ja aplicava o fallback correto
    (`resolved_path or file_name`); faltava replicar em `_bridge_edicao_
    arquivo`. Este teste prova, com um arquivo REAL em disco (`tmp_path`),
    que o conteudo antigo agora e lido corretamente via fallback para
    `file_name` quando `resolved_path` vem vazio.
    """

    async def test_deve_usar_file_name_como_fallback_quando_resolved_path_vazio(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        from local_chat_gateway.sdk_session import (
            _EDICOES_ARQUIVO_PENDENTES,
            resolver_edicao_arquivo,
            stream_chat_ag_ui,
        )

        arquivo = tmp_path / "README.md"
        conteudo_atual = "linha1\nlinha2\nlinha3\n"
        arquivo.write_text(conteudo_atual, encoding="utf-8")
        conteudo_novo = "linha1\nlinha2 MODIFICADA\nlinha3\n"

        class PermissionRequestWrite:
            def __init__(
                self, *, file_name: str, resolved_path: str, new_file_contents: str
            ) -> None:
                self.file_name = file_name
                self.resolved_path = resolved_path  # vazio -- reproduz o bug real.
                self.new_file_contents = new_file_contents
                self.diff = ""
                self.intention = "teste de fallback resolved_path -> file_name"

        class AssistantIdleData:
            pass

        class _PlaceholderVazio:
            pass

        class _Evento:
            def __init__(self, data: Any) -> None:
                self.data = data

        class _FakeSession:
            def __init__(self, on_permission_request: Any) -> None:
                self._on_permission_request = on_permission_request
                self._callback: Any = None

            def on(self, callback: Any) -> None:
                self._callback = callback

            async def send(self, prompt: str, attachments: Any = None) -> None:
                assert self._callback is not None
                perm_request = PermissionRequestWrite(
                    file_name=str(arquivo),
                    resolved_path="",
                    new_file_contents=conteudo_novo,
                )
                tarefa_permissao = asyncio.ensure_future(
                    self._on_permission_request(perm_request, {})
                )
                # `_bridge_edicao_arquivo` enfileira o `CustomEvent` e SO
                # ENTAO registra o Future pendente -- aguarda ate aparecer
                # em `_EDICOES_ARQUIVO_PENDENTES` (sem depender do timeout
                # real de 30min) e resolve com "reject" (decisao irrelevante
                # para este teste, que valida apenas o payload do diff).
                for _ in range(1000):
                    if _EDICOES_ARQUIVO_PENDENTES:
                        break
                    await asyncio.sleep(0)
                assert (
                    _EDICOES_ARQUIVO_PENDENTES
                ), "CustomEvent nao foi enfileirado a tempo"
                request_id = next(iter(_EDICOES_ARQUIVO_PENDENTES))
                resolver_edicao_arquivo(request_id, aprovado=False)
                await tarefa_permissao
                self._callback(_Evento(AssistantIdleData()))

            async def __aenter__(self) -> "_FakeSession":
                return self

            async def __aexit__(self, *exc: object) -> None:
                return None

        class _FakeClient:
            def __init__(self, github_token: str) -> None:
                pass

            async def create_session(
                self, *, on_permission_request: Any, **_kwargs: Any
            ) -> _FakeSession:
                return _FakeSession(on_permission_request)

            async def __aenter__(self) -> "_FakeClient":
                return self

            async def __aexit__(self, *exc: object) -> None:
                return None

        fake_copilot = types.ModuleType("copilot")
        fake_copilot.CopilotClient = _FakeClient  # type: ignore[attr-defined]

        fake_session_events = types.ModuleType("copilot.session_events")
        setattr(fake_session_events, "AssistantMessageData", _PlaceholderVazio)
        setattr(fake_session_events, "ToolExecutionStartData", _PlaceholderVazio)
        setattr(fake_session_events, "ToolExecutionCompleteData", _PlaceholderVazio)
        setattr(fake_session_events, "SubagentStartedData", _PlaceholderVazio)
        setattr(fake_session_events, "SubagentCompletedData", _PlaceholderVazio)
        setattr(fake_session_events, "SubagentFailedData", _PlaceholderVazio)
        setattr(fake_session_events, "AssistantIdleData", AssistantIdleData)
        setattr(fake_session_events, "SessionErrorData", _PlaceholderVazio)
        setattr(fake_session_events, "PermissionRequestRead", _PlaceholderVazio)
        setattr(fake_session_events, "PermissionRequestWrite", PermissionRequestWrite)
        setattr(fake_session_events, "PermissionRequestMcp", _PlaceholderVazio)
        setattr(fake_session_events, "PermissionRequestCustomTool", _PlaceholderVazio)
        _registrar_placeholders_novos_eventos_turn_recorder(fake_session_events)

        fake_rpc = types.ModuleType("copilot.generated.rpc")
        setattr(
            fake_rpc,
            "PermissionDecisionApproveOnce",
            type("PermissionDecisionApproveOnce", (), {}),
        )
        setattr(
            fake_rpc,
            "PermissionDecisionReject",
            type(
                "PermissionDecisionReject",
                (),
                {
                    "__init__": lambda self, feedback=None: setattr(
                        self, "feedback", feedback
                    )
                },
            ),
        )

        monkeypatch.setitem(sys.modules, "copilot", fake_copilot)
        monkeypatch.setitem(sys.modules, "copilot.session_events", fake_session_events)
        monkeypatch.setitem(sys.modules, "copilot.generated.rpc", fake_rpc)

        from ag_ui.core import CustomEvent

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
                permission_mode="apply",
            )
        ]

        evento_pedido = next(
            e
            for e in eventos
            if isinstance(e, CustomEvent) and e.name == "file_edit_requested"
        )
        linhas = evento_pedido.value["lines"]
        tipos = [linha["tipo"] for linha in linhas]

        # Com o fallback correto (`file_name`), o diff deve mostrar a MAIORIA
        # das linhas como "contexto" (inalteradas) e so a linha 2 alterada --
        # NAO o arquivo inteiro como "adicionada" (bug original).
        assert tipos.count("contexto") == 2  # linha1 e linha3 inalteradas.
        assert tipos.count("removida") == 1  # linha2 antiga.
        assert tipos.count("adicionada") == 1  # linha2 nova.
        assert evento_pedido.value["resolved_path"] == str(arquivo)


class TestPermissionRequestShell:
    """Testes de `_comando_shell_e_seguro` -- bug real corrigido (2026-10-02,
    reportado pelo usuario via `pr-gatekeeper`): `PermissionRequestShell`
    (comandos de terminal/shell) nunca era reconhecida por
    `_identificador_e_seguro_nativo`, caindo sempre no branch generico
    (`seguro_nativo=False`) -- TODO comando de shell (inclusive
    `git --no-pager status`/`diff`, 100% read-only) era negado pelo handler
    conservador do gateway, mesmo com `GATEWAY_PERMISSION_MODE=apply`.
    """

    class _FakeShellCommand:
        def __init__(self, identifier: str, read_only: bool) -> None:
            self.identifier = identifier
            self.read_only = read_only

    class _FakePermissionRequestShell:
        def __init__(self, full_command_text: str, commands: list[Any]) -> None:
            self.full_command_text = full_command_text
            self.commands = commands

    def test_deve_autorizar_quando_sdk_marca_read_only_e_comando_e_git_seguro(
        self,
    ) -> None:
        from local_chat_gateway.sdk_session import _comando_shell_e_seguro

        perm_request = self._FakePermissionRequestShell(
            full_command_text="git --no-pager status",
            commands=[self._FakeShellCommand("git status", read_only=True)],
        )
        assert _comando_shell_e_seguro(perm_request) is True

    def test_deve_negar_quando_sdk_marca_read_only_mas_heuristica_propria_discorda(
        self,
    ) -> None:
        """Defesa em profundidade: mesmo que o SDK (hipoteticamente)
        classifique um comando mutante como `read_only=True`, a heuristica
        propria do gateway (`comando_terminal_e_seguro`) ainda bloqueia."""
        from local_chat_gateway.sdk_session import _comando_shell_e_seguro

        perm_request = self._FakePermissionRequestShell(
            full_command_text="git commit -m 'teste'",
            commands=[self._FakeShellCommand("git commit", read_only=True)],
        )
        assert _comando_shell_e_seguro(perm_request) is False

    def test_deve_negar_quando_sdk_marca_algum_comando_como_nao_read_only(
        self,
    ) -> None:
        from local_chat_gateway.sdk_session import _comando_shell_e_seguro

        perm_request = self._FakePermissionRequestShell(
            full_command_text="git --no-pager status && git push origin main",
            commands=[
                self._FakeShellCommand("git status", read_only=True),
                self._FakeShellCommand("git push", read_only=False),
            ],
        )
        assert _comando_shell_e_seguro(perm_request) is False

    def test_deve_negar_quando_lista_de_commands_esta_vazia(self) -> None:
        from local_chat_gateway.sdk_session import _comando_shell_e_seguro

        perm_request = self._FakePermissionRequestShell(
            full_command_text="git --no-pager status", commands=[]
        )
        assert _comando_shell_e_seguro(perm_request) is False

    def test_deve_autorizar_comando_composto_quando_sdk_nativo_e_inconclusivo(
        self,
    ) -> None:
        """Bug real investigado (2026-10-04): comando PowerShell COMPOSTO
        (varios `git --no-pager` encadeados por `;` com marcadores
        `Write-Output` entre eles) foi classificado pelo SDK como 1 UNICO
        identificador com `read_only=False` (classificador nativo nao
        decompoe a cadeia) -- negava o comando INTEIRO mesmo sendo 100%
        read-only. Apos o fix, quando o sinal nativo e inconclusivo, a
        heuristica propria do gateway (`comando_terminal_e_seguro`, que
        decompoe corretamente por `;` e reconhece `write-output` como
        utilitario inocuo) decide -- e aprova."""
        from local_chat_gateway.sdk_session import _comando_shell_e_seguro

        texto = (
            'git --no-pager status; Write-Output "---DIFF-STAT---"; '
            'git --no-pager diff --stat; Write-Output "---LOG---"; '
            "git --no-pager log --oneline -5"
        )
        perm_request = self._FakePermissionRequestShell(
            full_command_text=texto,
            commands=[self._FakeShellCommand(texto, read_only=False)],
        )
        assert _comando_shell_e_seguro(perm_request) is True

    def test_deve_negar_comando_composto_inconclusivo_se_contiver_mutacao_git(
        self,
    ) -> None:
        """Defesa em profundidade preservada: o fallback para a heuristica
        propria NAO abre excecao para subcomandos git mutantes escondidos
        dentro de um comando composto que o SDK nao decompos."""
        from local_chat_gateway.sdk_session import _comando_shell_e_seguro

        texto = 'git --no-pager status; Write-Output "---PUSH---"; git push origin main'
        perm_request = self._FakePermissionRequestShell(
            full_command_text=texto,
            commands=[self._FakeShellCommand(texto, read_only=False)],
        )
        assert _comando_shell_e_seguro(perm_request) is False

    def test_identificador_e_seguro_nativo_reconhece_shell_via_stream_chat(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Teste de integracao fim-a-fim: uma `PermissionRequestShell` com
        comando git read-only deve ser aprovada SEM consultar o
        `permission_handler` do gateway (paridade com `PermissionRequestRead`)."""
        eventos_disparados: list[str] = []
        handler_chamado: list[tuple[str, Mapping[str, Any]]] = []

        def _permission_handler(tool_name: str, params: Mapping[str, Any]) -> bool:
            handler_chamado.append((tool_name, dict(params)))
            return False  # Handler sempre nega -- aprovacao deve vir do sinal nativo.

        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="shell",
        )

        from local_chat_gateway.api.schemas import ChatMessage

        async def _consumir() -> None:
            async for _ in stream_chat(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="rode git status")],
                permission_handler=_permission_handler,
                permission_mode="read_only",
            ):
                pass

        asyncio.run(_consumir())

        assert handler_chamado == []  # Nunca consultado -- sinal nativo bastou.

    def test_identificador_e_seguro_nativo_normaliza_tool_name_mcp_sem_prefixo(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Bug real investigado (2026-10-04): o SDK headless real reporta
        `PermissionRequestMcp.tool_name` como o nome CRU exposto pelo
        servidor MCP (ex.: "ctx_batch_execute"), SEM o prefixo de exibicao
        da IDE ("mcp_context-mode_ctx_batch_execute") esperado por
        `permission_policy.tool_mcp_e_cataloga`. Isso negava `context-mode`/
        `codegraph`/`tavily` mesmo com o servidor MCP conectado e
        funcionando. O fix normaliza o identificador usando `server_name`
        (campo real confirmado por introspeccao da wheel) ANTES de
        repassar ao `permission_handler` -- este teste trava que o
        identificador chega la JA normalizado."""
        eventos_disparados: list[str] = []
        handler_chamado: list[tuple[str, Mapping[str, Any]]] = []

        def _permission_handler(tool_name: str, params: Mapping[str, Any]) -> bool:
            handler_chamado.append((tool_name, dict(params)))
            return True

        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="mcp",
            mcp_tool_name="ctx_batch_execute",
            mcp_server_name="context-mode",
            mcp_read_only=False,
        )

        from local_chat_gateway.api.schemas import ChatMessage

        async def _consumir() -> None:
            async for _ in stream_chat(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="leia alguns arquivos")],
                permission_handler=_permission_handler,
                permission_mode="apply",
            ):
                pass

        asyncio.run(_consumir())

        assert len(handler_chamado) == 1
        identificador_recebido, _ = handler_chamado[0]
        assert identificador_recebido == "mcp_context-mode_ctx_batch_execute"


class TestStreamChatMcpServers:
    """T11/T12 (bugfix 2026-10-02, RC2) -- `mcp_servers=` deve ser repassado
    a AMBOS os call-sites de `client.create_session` (`stream_chat` e
    `stream_chat_ag_ui`), construido via
    `mcp_servers_catalog.construir_mcp_servers`. A logica de QUAIS
    servidores aparecem no dict (flags/credenciais) e coberta isoladamente
    em `test_mcp_servers_catalog.py` -- aqui validamos apenas a integracao
    (wiring) nos 2 pontos de chamada."""

    async def test_deve_repassar_mcp_servers_ao_create_session_stream_chat(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        chamada_espiao: dict[str, Any] = {}
        sentinela = {"context-mode": {"type": "stdio"}}

        def _construir_mcp_servers_espiao(settings: Any) -> dict[str, Any]:
            chamada_espiao["settings"] = settings
            return sentinela

        monkeypatch.setattr(
            "local_chat_gateway.sdk_session.construir_mcp_servers",
            _construir_mcp_servers_espiao,
        )

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
        ):
            pass

        assert "settings" in chamada_espiao  # construir_mcp_servers foi chamado
        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.mcp_servers_recebido == sentinela

    async def test_deve_repassar_mcp_servers_ao_create_session_stream_chat_ag_ui(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fake minimo e dedicado (2o call-site, `stream_chat_ag_ui`,
        linha ~1840) -- nao reaproveita o fixture de `stream_chat`, que
        instala um `_FakeClient` com assinatura keyword-only estrita
        incompatível com os parametros extras de `stream_chat_ag_ui`
        (`on_elicitation_request`/`on_user_input_request`/etc.)."""
        from local_chat_gateway.api.schemas import ChatMessage

        chamada_espiao: dict[str, Any] = {}
        sentinela = {"context-mode": {"type": "stdio"}}

        def _construir_mcp_servers_espiao(settings: Any) -> dict[str, Any]:
            chamada_espiao["settings"] = settings
            return sentinela

        monkeypatch.setattr(
            "local_chat_gateway.sdk_session.construir_mcp_servers",
            _construir_mcp_servers_espiao,
        )

        class _PlaceholderVazioLocal:
            pass

        class AssistantIdleDataLocal:
            pass

        class _FakeSessionLocal:
            def __init__(self, on_permission_request: Any) -> None:
                self._on_permission_request = on_permission_request
                self._callback: Any = None

            def on(self, callback: Any) -> None:
                self._callback = callback

            async def send(self, prompt: str, attachments: Any = None) -> None:
                self._callback(types.SimpleNamespace(data=AssistantIdleDataLocal()))

            async def __aenter__(self) -> "_FakeSessionLocal":
                return self

            async def __aexit__(self, *exc: object) -> None:
                return None

        class _FakeClientLocal:
            ultima_instancia: "_FakeClientLocal | None" = None

            def __init__(self, github_token: str) -> None:
                type(self).ultima_instancia = self
                self.mcp_servers_recebido: Any = None
                self.excluded_tools_recebido: Any = None

            async def create_session(
                self,
                *,
                on_permission_request: Any,
                mcp_servers: Any = None,
                excluded_tools: Any = None,
                **_kw: Any,
            ) -> _FakeSessionLocal:
                self.mcp_servers_recebido = mcp_servers
                self.excluded_tools_recebido = excluded_tools
                return _FakeSessionLocal(on_permission_request)

            async def __aenter__(self) -> "_FakeClientLocal":
                return self

            async def __aexit__(self, *exc: object) -> None:
                return None

        fake_copilot = types.ModuleType("copilot")
        fake_copilot.CopilotClient = _FakeClientLocal  # type: ignore[attr-defined]

        fake_session_events = types.ModuleType("copilot.session_events")
        for nome in (
            "AssistantMessageData",
            "ToolExecutionStartData",
            "ToolExecutionCompleteData",
            "SubagentStartedData",
            "SubagentCompletedData",
            "SubagentFailedData",
            "SessionErrorData",
            "PermissionRequestRead",
            "PermissionRequestWrite",
            "PermissionRequestMcp",
            "PermissionRequestCustomTool",
            "PermissionRequestShell",
        ):
            setattr(fake_session_events, nome, _PlaceholderVazioLocal)
        setattr(fake_session_events, "AssistantIdleData", AssistantIdleDataLocal)
        _registrar_placeholders_novos_eventos_turn_recorder(fake_session_events)

        fake_rpc = types.ModuleType("copilot.generated.rpc")
        setattr(fake_rpc, "PermissionDecisionApproveOnce", type("PDA", (), {}))
        setattr(
            fake_rpc,
            "PermissionDecisionReject",
            type("PDR", (), {"__init__": lambda self, feedback=None: None}),
        )

        monkeypatch.setitem(sys.modules, "copilot", fake_copilot)
        monkeypatch.setitem(sys.modules, "copilot.session_events", fake_session_events)
        monkeypatch.setitem(sys.modules, "copilot.generated.rpc", fake_rpc)

        async for _ in stream_chat_ag_ui(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: True,
            thread_id="t1",
            run_id="r1",
        ):
            pass

        assert "settings" in chamada_espiao  # construir_mcp_servers foi chamado
        assert _FakeClientLocal.ultima_instancia is not None
        assert _FakeClientLocal.ultima_instancia.mcp_servers_recebido == sentinela


class TestPermissionRequestShellWrapperUnwrap:
    """T13 (Fix 2, bug real 2026-10-04): o unwrap de shell wrapper em
    `permission_policy.comando_terminal_e_seguro` propaga automaticamente
    para `_comando_shell_e_seguro` por composicao de funcao ja existente
    (R-055) -- nenhuma alteracao necessaria neste modulo."""

    def test_deve_autorizar_comando_git_envolto_em_powershell_quando_sdk_marca_read_only(
        self,
    ) -> None:
        from local_chat_gateway.sdk_session import _comando_shell_e_seguro

        perm_request = TestPermissionRequestShell._FakePermissionRequestShell(
            full_command_text='powershell -Command "git --no-pager status"',
            commands=[
                TestPermissionRequestShell._FakeShellCommand(
                    "git status", read_only=True
                )
            ],
        )
        assert _comando_shell_e_seguro(perm_request) is True


class TestStreamChatAgUiCreditsBadge:
    """Badge de creditos ao final do turno (2026-10-03, pedido explicito do
    usuario -- paridade com o plugin Copilot da IDE: "<Modelo> · <N>
    Credits"). Formula oficial confirmada em docs.github.com/en/copilot/
    how-tos/copilot-sdk/features/usage-and-billing: AI credits =
    `copilot_usage.total_nano_aiu / 1e9`."""

    async def test_deve_exibir_badge_de_creditos_quando_sdk_reporta_uso_real(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        eventos_disparados: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="read",  # aprovado nativamente, sem handler
            usage_total_nano_aiu=1_924_000_000.0,  # 1.924e9 nano-AIU == 1.9 credits
            usage_model="claude-sonnet-4-5",
        )

        from ag_ui.core import TextMessageContentEvent
        from local_chat_gateway.api.schemas import ChatMessage

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
                agent_model="Claude Sonnet 5",
            )
        ]

        texto_completo = "".join(
            e.delta
            for e in eventos
            if isinstance(e, TextMessageContentEvent) and e.subagent_run_id is None
        )
        # agent_model (nome amigavel) tem precedencia sobre usage_model (id
        # tecnico da API) na exibicao -- mesma convencao do badge "Agente Ativo".
        assert "Claude Sonnet 5 · 1.9 Credits" in texto_completo

    async def test_nao_deve_exibir_badge_quando_sdk_nao_reporta_nenhum_uso(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comportamento legado (sem `usage_total_nano_aiu`): nenhum badge
        falso-zero e' mostrado -- cobre o caso real de sessao stub/erro
        ANTES de qualquer chamada de modelo."""
        eventos_disparados: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="read",
        )

        from ag_ui.core import TextMessageContentEvent
        from local_chat_gateway.api.schemas import ChatMessage

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
                agent_model="Claude Sonnet 5",
            )
        ]

        texto_completo = "".join(
            e.delta for e in eventos if isinstance(e, TextMessageContentEvent)
        )
        assert "Credits" not in texto_completo

    async def test_deve_usar_modelo_tecnico_quando_agent_model_ausente(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Sem `agent_model` (agent sem `model:` no frontmatter), cai para
        o id tecnico reportado pela ULTIMA `AssistantUsageData` do turno."""
        eventos_disparados: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="read",
            usage_total_nano_aiu=500_000_000.0,  # 0.5 credits
            usage_model="claude-sonnet-4-5",
        )

        from ag_ui.core import TextMessageContentEvent
        from local_chat_gateway.api.schemas import ChatMessage

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
            )
        ]

        texto_completo = "".join(
            e.delta for e in eventos if isinstance(e, TextMessageContentEvent)
        )
        assert "claude-sonnet-4-5 · 0.5 Credits" in texto_completo


class TestStreamChatAgUiContextWindowBadge:
    """Badge de context-window ao final do turno (2026-10-03, pedido
    explicito do usuario: "conseguimos no front do chat mostrar o
    context-window do copilot?"). Confirmado via introspeccao real da
    wheel (`github_copilot_sdk==1.0.16`, `copilot.generated.session_events.
    SessionUsageInfoData`, docstring: "Current context window usage
    statistics including token and message counts") que o SDK emite este
    evento nativo com `current_tokens`/`token_limit` -- combinado no MESMO
    badge de creditos ja existente (`TestStreamChatAgUiCreditsBadge`), cada
    pedaco aparecendo de forma independente conforme o SDK reportar."""

    async def test_deve_exibir_percentual_de_contexto_quando_sdk_reporta_uso(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        eventos_disparados: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="read",
            context_current_tokens=84_200,
            context_token_limit=200_000,
        )

        from ag_ui.core import TextMessageContentEvent
        from local_chat_gateway.api.schemas import ChatMessage

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
            )
        ]

        texto_completo = "".join(
            e.delta for e in eventos if isinstance(e, TextMessageContentEvent)
        )
        # 84200 / 200000 = 42.1% -> arredondado para 42%; notacao compacta
        # de tokens (84.2k/200.0k) evita "84200/200000 tokens" ilegivel.
        assert "42% contexto (84.2k/200.0k tokens)" in texto_completo

    async def test_deve_combinar_creditos_e_contexto_no_mesmo_badge(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        eventos_disparados: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="read",
            usage_total_nano_aiu=1_924_000_000.0,
            usage_model="claude-sonnet-4-5",
            context_current_tokens=50_000,
            context_token_limit=200_000,
        )

        from ag_ui.core import TextMessageContentEvent
        from local_chat_gateway.api.schemas import ChatMessage

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
                agent_model="Claude Sonnet 5",
            )
        ]

        texto_completo = "".join(
            e.delta
            for e in eventos
            if isinstance(e, TextMessageContentEvent) and e.subagent_run_id is None
        )
        assert (
            "*🧮 Claude Sonnet 5 · 1.9 Credits · 25% contexto (50.0k/200.0k tokens)*"
            in texto_completo
        )

    async def test_nao_deve_exibir_contexto_quando_sdk_nao_reporta_token_limit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Guarda contra divisao por zero/dado incompleto: so' exibe o
        percentual quando AMBOS `current_tokens` e `token_limit` (> 0)
        estao disponiveis."""
        eventos_disparados: list[str] = []
        _instalar_copilot_falso(
            monkeypatch,
            eventos_disparados=eventos_disparados,
            tipo_permission_request="read",
            context_current_tokens=50_000,
            context_token_limit=None,
        )

        from ag_ui.core import TextMessageContentEvent
        from local_chat_gateway.api.schemas import ChatMessage

        eventos = [
            evento
            async for evento in stream_chat_ag_ui(
                token="tok-valido",
                model=None,
                messages=[ChatMessage(role="user", content="oi")],
                permission_handler=lambda *_: True,
                thread_id="thread-1",
                run_id="run-1",
            )
        ]

        texto_completo = "".join(
            e.delta for e in eventos if isinstance(e, TextMessageContentEvent)
        )
        assert "contexto" not in texto_completo


class TestStreamChatExcludedToolsBloqueiaTaskFantasma:
    """Bug real investigado 2026-10-03 (log `.tmp/gateway.log` linha
    9739-9778): a tool nativa `task` (`copilot.BUILTIN_TOOLS_ISOLATED`,
    SEMPRE exposta independente do `tools:` do agent) foi invocada
    diretamente pelo modelo com `agent_name=task` e um label livre
    ("Run session_store tests") como `agent_display_name` -- nome ausente
    nos custom_agents reais (badge "Agente Ativo: Run session_store tests"
    exibido na UI, nome que nao existe no catalogo), consumindo 332554
    tokens / 9 tool calls so para uma delegacao fantasma. A instrucao
    textual `_NOTA_GATEWAY_HEADLESS` (soft) ja orientava o modelo a nao
    usar `run_subagent`/`task`, mas foi ignorada -- `excluded_tools=["task"]`
    e o bloqueio DURO via SDK (remove a tool do catalogo repassado ao
    modelo), validado aqui nos 2 call-sites de `client.create_session`
    (`stream_chat` e `stream_chat_ag_ui`), mesmo padrao de cobertura de
    `TestStreamChatMcpServers` (T11/T12)."""

    async def test_deve_repassar_excluded_tools_task_ao_create_session_stream_chat(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from local_chat_gateway.api.schemas import ChatMessage

        _instalar_copilot_falso(monkeypatch, eventos_disparados=[])

        async for _ in stream_chat(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: False,
        ):
            pass

        fake_copilot_module = sys.modules["copilot"]
        classe_cliente = getattr(fake_copilot_module, "FakeClientRef")
        instancia = classe_cliente.ultima_instancia
        assert instancia is not None
        assert instancia.excluded_tools_recebido == ["task"]

    async def test_deve_repassar_excluded_tools_task_ao_create_session_stream_chat_ag_ui(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fake minimo e dedicado (2o call-site, `stream_chat_ag_ui`),
        espelhando `test_deve_repassar_mcp_servers_ao_create_session_
        stream_chat_ag_ui` -- nao reaproveita o fixture de `stream_chat`
        (assinatura keyword-only incompativel com os parametros extras de
        `stream_chat_ag_ui`)."""
        from local_chat_gateway.api.schemas import ChatMessage

        class _PlaceholderVazioLocal2:
            pass

        class AssistantIdleDataLocal2:
            pass

        class _FakeSessionLocal2:
            def __init__(self, on_permission_request: Any) -> None:
                self._on_permission_request = on_permission_request
                self._callback: Any = None

            def on(self, callback: Any) -> None:
                self._callback = callback

            async def send(self, prompt: str, attachments: Any = None) -> None:
                self._callback(
                    types.SimpleNamespace(data=AssistantIdleDataLocal2())
                )

            async def __aenter__(self) -> "_FakeSessionLocal2":
                return self

            async def __aexit__(self, *exc: object) -> None:
                return None

        class _FakeClientLocal2:
            ultima_instancia: "_FakeClientLocal2 | None" = None

            def __init__(self, github_token: str) -> None:
                type(self).ultima_instancia = self
                self.excluded_tools_recebido: Any = None

            async def create_session(
                self,
                *,
                on_permission_request: Any,
                excluded_tools: Any = None,
                **_kw: Any,
            ) -> _FakeSessionLocal2:
                self.excluded_tools_recebido = excluded_tools
                return _FakeSessionLocal2(on_permission_request)

            async def __aenter__(self) -> "_FakeClientLocal2":
                return self

            async def __aexit__(self, *exc: object) -> None:
                return None

        fake_copilot = types.ModuleType("copilot")
        fake_copilot.CopilotClient = _FakeClientLocal2  # type: ignore[attr-defined]

        fake_session_events = types.ModuleType("copilot.session_events")
        for nome in (
            "AssistantMessageData",
            "ToolExecutionStartData",
            "ToolExecutionCompleteData",
            "SubagentStartedData",
            "SubagentCompletedData",
            "SubagentFailedData",
            "SessionErrorData",
            "PermissionRequestRead",
            "PermissionRequestWrite",
            "PermissionRequestMcp",
            "PermissionRequestCustomTool",
            "PermissionRequestShell",
        ):
            setattr(fake_session_events, nome, _PlaceholderVazioLocal2)
        setattr(fake_session_events, "AssistantIdleData", AssistantIdleDataLocal2)
        _registrar_placeholders_novos_eventos_turn_recorder(fake_session_events)

        fake_rpc = types.ModuleType("copilot.generated.rpc")
        setattr(fake_rpc, "PermissionDecisionApproveOnce", type("PDA2", (), {}))
        setattr(
            fake_rpc,
            "PermissionDecisionReject",
            type("PDR2", (), {"__init__": lambda self, feedback=None: None}),
        )

        monkeypatch.setitem(sys.modules, "copilot", fake_copilot)
        monkeypatch.setitem(sys.modules, "copilot.session_events", fake_session_events)
        monkeypatch.setitem(sys.modules, "copilot.generated.rpc", fake_rpc)

        async for _ in stream_chat_ag_ui(
            token="tok-valido",
            model=None,
            messages=[ChatMessage(role="user", content="oi")],
            permission_handler=lambda *_: True,
            thread_id="t1",
            run_id="r1",
        ):
            pass

        assert _FakeClientLocal2.ultima_instancia is not None
        assert _FakeClientLocal2.ultima_instancia.excluded_tools_recebido == ["task"]
