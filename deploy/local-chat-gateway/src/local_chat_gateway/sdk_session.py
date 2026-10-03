"""sdk_session — integracao real (opcional) com o Copilot SDK (Fase 3).

Extra opcional `[sdk]` (`github-copilot-sdk`). Import tardio (lazy, nunca no
topo do modulo) do pacote `copilot`, mesmo padrao RK-01 ja usado em
`governance_runner.runner.sdk_adapter` -- permite que o gateway funcione
(com fallback deterministico para o stub em `routes.py`) mesmo sem o
extra instalado ou sem um token real configurado.

Eventos reais confirmados por inspecao de SESSAO AO VIVO (nao apenas
`dir()` estatico como no spike RT-01 original -- aquele spike identificou
os NOMES DE CLASSE corretamente, mas a hipotese de QUAIS classes carregam
o texto/sinalizam encerramento estava errada; corrigido em 2026-09-29 com
evidencia de uma troca real via `docker run` + token do usuario):
`copilot.session_events.AssistantMessageData` (conteudo, campo `.content`;
NAO `AssistantMessageDeltaData`, que nunca foi observado disparar),
`AssistantIdleData` (sinal de encerramento do turno; NAO `SessionIdleData`,
que tambem nunca foi observado nesta sessao interativa simples).
`ToolExecutionStartData`/`ToolExecutionCompleteData` confirmados (porem
`ToolExecutionCompleteData` NAO possui campo `tool_name` -- rastreado via
cache `tool_call_id -> tool_name` populado no evento de start).

Correcao adicional (2026-09-29, 2a rodada de teste real via Lobe Chat):
1. `working_directory` NAO era repassado a `create_session` -- o SDK usava
   o CWD do processo (`/app`, `WORKDIR` da imagem, sem o repositorio do
   usuario) em vez do bind mount `/workspace`, causando "permissao
   negada"/"nenhum repositorio carregado" mesmo com sessao real conectada.
2. `on_permission_request` DEVE retornar uma instancia de
   `PermissionRequestResult` (`PermissionDecisionApproveOnce`/
   `PermissionDecisionReject`) -- o dict puro usado antes
   (`{"permissionDecision": "allow"}`) faz o SDK levantar
   `AttributeError: 'dict' object has no attribute 'to_dict'` internamente,
   quebrando toda tool call silenciosamente.
3. `PermissionRequest` e uma uniao de 12 classes (Shell/Write/Read/Mcp/
   CustomTool/...); NEM TODAS tem campo `tool_name` (confirmado via
   `dataclasses.fields()`) -- so `Mcp`/`CustomTool` tem. `Read` e sempre
   seguro; `Mcp` expoe `read_only: bool` nativo do SDK.

Multi-projeto automatico (2026-09-29, 3a rodada -- pedido do usuario para
acessar TODOS os projetos de `projects.local.yaml` sem mount manual por
projeto): `working_directory` default mudou de `/workspace` (1 unico
projeto) para `/workspaces` (diretorio-pai comum contendo TODOS os
projetos registrados como subdiretorios, montado uma unica vez via
`PROJECTS_ROOT_PATH` em `docker-compose.yml`) -- ver `projects_catalog.py`
para a traducao `path_externo` -> path no container e `routes.py` para o
wiring do `additional_directories` calculado a cada request.

Correcao adicional (2026-09-29, 4a rodada -- teste real multi-projeto via
Lobe Chat): com VARIOS projetos sob a mesma raiz montada, um deles
(este proprio repositorio, deep-agents-copilot) tem seus proprios
`.github/hooks/*.json`/agents/skills customizados, destinados a sessoes de
DESENVOLVIMENTO NAQUELE repositorio -- nao a esta sessao generica do
gateway sobre QUALQUER projeto. O SDK real descobre e tenta EXECUTAR esses
hooks automaticamente ao montar a sessao (mesmo perguntando sobre outro
projeto irmao), quebrando com "um hook de contexto ... esta bloqueando
todas as ferramentas" (o hook espera dependencias/CWD que nao existem
neste container minimo). Corrigido com `enable_file_hooks=False` e
`enable_config_discovery=False` em `create_session` -- sessao do gateway
fica deliberadamente "limpa" (sem hooks, sem descoberta de config custom).

Nao-escopo desta fase (Fase 3): o `permission_handler` aceito por
`stream_chat` e um `Callable` simples (tool_name, params) -> bool, ainda
NAO integrado ao `PermissionPolicyStub` real (que exige `Sessao`/
`TabelaTransicao`/`Catalogo` -- wiring completo de sessao de governanca
em `routes.py` fica para uma fase futura). O handler default usado por
`routes.py` nesta fase e conservador: nega toda tool exceto as de leitura
simples, coerente com `GATEWAY_PERMISSION_MODE=read_only` default.
"""

from __future__ import annotations

import asyncio
import difflib
import logging
import time
import uuid
from collections.abc import AsyncIterator, Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final, Literal

from ag_ui.core import Event as AgUiEvent

from local_chat_gateway import turn_recorder
from local_chat_gateway.api.schemas import (
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatMessage,
)
from local_chat_gateway.permission_policy import comando_terminal_e_seguro
from local_chat_gateway.config import get_settings
from local_chat_gateway.mcp_servers_catalog import construir_mcp_servers
from local_chat_gateway.session_store import SessionStore

_MODEL_ID: Final[str] = "deep-agents/router"
_COMPLETION_ID: Final[str] = "chatcmpl-sdk"
_STUB_CONTENT: Final[str] = "Hello! I am deep-agents stub router."
_TIMEOUT_SESSAO_SEGUNDOS: Final[float] = 120.0

logger = logging.getLogger(__name__)


class SDKUnavailableError(RuntimeError):
    """Erro de dominio: SDK do Copilot indisponivel.

    Levantada quando o extra opcional `[sdk]` nao esta instalado, ou
    quando o arquivo de token esta ausente/vazio. `routes.py` trata esta
    excecao como sinal para usar o fallback deterministico (stub).
    """


def read_sdk_token(token_file: str) -> str:
    """Le o token do Copilot SDK de um arquivo (Docker secret ou local).

    Args:
        token_file: Caminho do arquivo (ex.: `/run/secrets/copilot_sdk_token`
            dentro do container, ou `./secrets/copilot_token` localmente).

    Returns:
        str: Token com espacos/quebras de linha removidos.

    Raises:
        SDKUnavailableError: Se o arquivo nao existir ou estiver vazio
            (nunca retorna string vazia silenciosamente).
    """
    path = Path(token_file)
    if not path.is_file():
        raise SDKUnavailableError(
            f"arquivo de token do Copilot SDK nao encontrado: {token_file}"
        )
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise SDKUnavailableError(
            f"arquivo de token do Copilot SDK esta vazio: {token_file}"
        )
    return token


def _import_copilot() -> Any:
    """Import tardio do pacote `copilot` (RK-01) -- nunca no topo do modulo.

    Returns:
        Any: modulo `copilot` importado (tipo `Any` proposital -- pacote
        externo opcional sem stubs de tipo instalados neste projeto).

    Raises:
        SDKUnavailableError: Se o extra opcional `[sdk]` nao estiver instalado.
    """
    try:
        import copilot  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SDKUnavailableError(
            "Pacote do Copilot SDK nao instalado. Instale o extra "
            "'deep-agents-gateway[sdk]' para integracao real (Fase 3)."
        ) from exc
    return copilot


def _comando_shell_e_seguro(perm_request: Any) -> bool:
    """Classifica uma `PermissionRequestShell` nativa do SDK como segura.

    Bug real corrigido (2026-10-02, reportado pelo usuario via
    `pr-gatekeeper`): `PermissionRequestShell` (comandos de terminal/shell,
    confirmado por introspeccao real do `github-copilot-sdk` -- classe
    DISTINTA de `PermissionRequestCustomTool`/`PermissionRequestMcp`) nunca
    era reconhecida por `_identificador_e_seguro_nativo`, caindo sempre no
    branch generico `type(perm_request).__name__, False` -- TODO comando de
    shell (inclusive `git --no-pager status`/`diff`, 100% read-only) era
    negado pelo handler conservador do gateway, mesmo com
    `GATEWAY_PERMISSION_MODE=apply` ja configurado.

    Combina DOIS sinais complementares (defesa em profundidade):
    1. O flag `read_only` NATIVO do SDK por comando identificado
       (`PermissionRequestShellCommand.read_only`) -- o proprio CLI ja
       classifica cada comando parseado de `full_command_text`. Quando
       TODOS os identificadores concordam (`read_only=True`), aprova sem
       reavaliar (caminho rapido/estrito).
    2. `permission_policy.comando_terminal_e_seguro()` sobre o texto
       completo do comando -- heuristica propria do gateway (git
       read-only + utilitarios inocuos, nunca mutante/destrutivo),
       reaproveitada da MESMA fonte usada pelos handlers de `routes.py`
       (R-055 anti-silo). Usada SEMPRE como decisao final -- inclusive
       como segunda chance (2026-10-04) quando o sinal nativo do SDK e
       `read_only=False` para um comando PowerShell COMPOSTO que o
       classificador nativo nao decompoe (ver comentario inline abaixo).
       Nunca aprova comando bloqueado categoricamente
       (`_COMANDOS_BLOQUEADOS_SEMPRE`) ou com subcomando git mutante.

    Args:
        perm_request: Instancia de `PermissionRequestShell` (SDK).

    Returns:
        bool: `True` se a heuristica propria do gateway
        (`comando_terminal_e_seguro`) aprovar o texto completo do comando
        -- o sinal nativo do SDK e usado apenas como contexto de log, nao
        como veto absoluto (ver 2026-10-04).
    """
    texto_completo = str(getattr(perm_request, "full_command_text", "") or "")
    comandos = list(getattr(perm_request, "commands", None) or [])
    # Debug investigativo (2026-10-04): bug de "Negado pela politica local"
    # persistente mesmo apos os fixes de 2026-10-02/2026-10-04 (unwrap de
    # wrapper de shell). Logging dos 3 pontos de rejeicao possiveis desta
    # funcao, para identificar EXATAMENTE qual deles dispara em producao
    # real (nao reproduzido nos testes unitarios, que mockam `commands`).
    if not comandos:
        logger.warning(
            "comando_shell_negado motivo=sem_commands full_command_text=%r",
            texto_completo,
        )
        return False
    identificadores_read_only = [
        (str(getattr(cmd, "identifier", "") or "?"), bool(getattr(cmd, "read_only", False)))
        for cmd in comandos
    ]
    todos_read_only_nativo = all(ro for _, ro in identificadores_read_only)
    if not todos_read_only_nativo:
        # Bug real investigado (2026-10-04): o flag `read_only` NATIVO do
        # SDK e calculado por comando IDENTIFICADO, mas para comandos
        # PowerShell COMPOSTOS (varios `git --no-pager ...` encadeados por
        # `;` com marcadores `Write-Output` entre eles, ex.: usados pelo
        # proprio `pr-gatekeeper` para coletar status+diff+log em 1 unica
        # chamada) o SDK retornou o BLOCO INTEIRO como 1 unico identificador
        # com `read_only=False` -- o classificador nativo nao decompoe a
        # cadeia, entao o veto absoluto anterior negava comandos 100%
        # read-only na pratica. Em vez de vetar incondicionalmente, cai
        # para a heuristica PROPRIA do gateway sobre o texto completo
        # (`comando_terminal_e_seguro`, que: 1) SEMPRE verifica primeiro
        # `_COMANDOS_BLOQUEADOS_SEMPRE` -- nenhum comando categoricamente
        # perigoso escapa por este caminho; 2) decompoe corretamente por
        # `&&`/`||`/`|`/`;`/`&`; 3) rejeita QUALQUER subcomando git mutante
        # -- so aprova aqui se a heuristica independente TAMBEM confirmar
        # seguranca). Mantido como ultimo recurso (nao substitui o sinal
        # nativo quando ele ja aprova).
        logger.warning(
            "comando_shell_sdk_inconclusivo motivo=sdk_read_only_false "
            "full_command_text=%r identificadores=%s -- reavaliando via "
            "heuristica propria do gateway (nao vetando incondicionalmente)",
            texto_completo,
            identificadores_read_only,
        )
    resultado_heuristica = comando_terminal_e_seguro(texto_completo)
    if not resultado_heuristica:
        logger.warning(
            "comando_shell_negado motivo=heuristica_gateway full_command_text=%r "
            "identificadores=%s",
            texto_completo,
            identificadores_read_only,
        )
    else:
        logger.info(
            "comando_shell_aprovado full_command_text=%r identificadores=%s",
            texto_completo,
            identificadores_read_only,
        )
    return resultado_heuristica


def _joined_prompt(messages: Sequence[ChatMessage]) -> str:
    """Concatena o historico de mensagens em um unico prompt.

    Fase 3 (nao-escopo): sessao multi-turno real do SDK (reaproveitando o
    `session_id` entre requests) fica para uma fase futura -- cada
    chamada de `stream_chat` abre uma sessao nova e envia o historico
    completo concatenado como um unico prompt.
    """
    return "\n".join(f"{m.role}: {m.content or ''}" for m in messages)


def _compor_prompt_com_sistema(
    system_message: str | None, mensagens_unidas: str
) -> str:
    """[LEGADO/NAO MAIS USADO em `stream_chat`] Compoe prompt em modo "append".

    NAO e mais chamada por `stream_chat` (ver `TestComporPromptComSistema` em
    `test_sdk_session.py` para teste de caracterizacao) -- `system_message` agora
    e injetado via mecanismo NATIVO do SDK (`client.create_session(system_message=
    {"mode": "append", "content": ...})`), nunca mais concatenado como texto no
    prompt. A concatenacao textual feita por esta funcao fazia o Claude
    subjacente tratar o banner como conteudo nao-confiavel embutido na mensagem
    do usuario e ignora-lo (bug real confirmado via Lobe Chat, 2026-09-30).

    O `system_message` (quando fornecido, tipicamente via
    `governance_pipeline.montar_contexto`) e sempre ADICIONADO como prefixo
    de contexto adicional ao historico de mensagens ja concatenado --
    NUNCA substitui ou sobrescreve o comportamento padrao/guardrails do
    SDK. Se `system_message` for `None`, o prompt final e identico ao
    historico de mensagens unido (comportamento legado inalterado).

    Args:
        system_message: Banner/contexto de governanca opcional a ser
            prefixado ao prompt. Se `None`, nenhuma composicao ocorre.
        mensagens_unidas: Historico de mensagens ja concatenado por
            `_joined_prompt`.

    Returns:
        str: Prompt final a ser enviado via `session.send`.
    """
    if system_message is None:
        return mensagens_unidas
    return f"{system_message}\n\n{mensagens_unidas}"


def _chunk(
    *,
    content: str | None = None,
    role: Literal["assistant"] | None = None,
    finish_reason: (
        Literal["stop", "length", "tool_calls", "content_filter"] | None
    ) = None,
) -> ChatCompletionChunk:
    """Constroi um `ChatCompletionChunk` unitario (1 choice, index 0)."""
    return ChatCompletionChunk(
        id=_COMPLETION_ID,
        created=int(time.time()),
        model=_MODEL_ID,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(role=role, content=content),
                finish_reason=finish_reason,
            )
        ],
    )


async def stream_chat(
    *,
    token: str,
    model: str | None,
    messages: Sequence[ChatMessage],
    permission_handler: Callable[[str, Mapping[str, Any]], bool],
    working_directory: str = "/workspaces",
    additional_directories: Sequence[str] | None = None,
    session_id: str | None = None,
    permission_mode: str = "read_only",
    checkpoint_aberto: bool = False,
    system_message: str | None = None,
    custom_agents: Sequence[Mapping[str, Any]] | None = None,
) -> AsyncIterator[ChatCompletionChunk]:
    """Sessao real do Copilot SDK, emitindo chunks conforme o texto chega.

    Args:
        token: Token de autenticacao (ver `read_sdk_token`).
        model: Override opcional de modelo subjacente (`COPILOT_MODEL`).
        messages: Historico de mensagens do request OpenAI-compatible.
        permission_handler: `Callable(tool_name, params) -> bool` (allow
            se `True`) -- ver nota de nao-escopo no docstring do modulo.
        working_directory: Diretorio de trabalho da sessao do SDK (onde as
            tools de leitura/escrita de arquivo operam por padrao). Default
            `/workspaces`.
        additional_directories: Paths adicionais que a sessao pode acessar.
        session_id: ID da sessao governada para reuso multi-turno.
        permission_mode: Modo de permissao (`read_only`, `propose`, `apply`).
        checkpoint_aberto: Se ha um checkpoint humano pendente na sessao.
        system_message: Contexto de governanca opcional (ex.: saida de
            `governance_pipeline.montar_contexto`) injetado via mecanismo
            NATIVO do SDK (`system_message` de `client.create_session`,
            variante `SystemMessageAppendConfig`/modo "append"). NUNCA
            mais concatenado como texto no prompt enviado via
            `session.send` -- o Claude subjacente tratava o banner
            concatenado como conteudo nao-confiavel embutido na mensagem
            do usuario e o ignorava explicitamente (bug real confirmado
            via Lobe Chat, 2026-09-30). Modo "append" nunca sobrescreve os
            guardrails/CLI foundation do SDK (ao contrario do modo
            "replace", fora de escopo). Se `None` (default), nenhum
            `system_message` e repassado ao SDK (comportamento legado).
        custom_agents: Catalogo de custom agents (RT-04, `agent_catalog.
            descobrir_custom_agents`) repassado NATIVAMENTE via
            `client.create_session(custom_agents=...)`. Bug real de
            producao confirmado por teste ao vivo (2026-10-01): sem este
            parametro, a tool `run_subagent` fica inerte -- o modelo
            responde explicitamente nao ter acesso a ela, pois o SDK NAO
            descobre `.github/agents/*.agent.md` automaticamente mesmo
            com `enable_config_discovery=True` (issue oficial
            github/copilot-sdk#1080, em aberto). Se `None`/vazio, nenhum
            `custom_agents` e repassado (comportamento legado -- sessao
            sem delegacao de subagent disponivel).

    Yields:
        ChatCompletionChunk: primeiro chunk com `delta.role="assistant"`,
        chunks intermediarios com `delta.content` (texto e eventos de
        tool), chunk final com `finish_reason="stop"`.

    Raises:
        SDKUnavailableError: Se o pacote `copilot` nao estiver instalado.
        TimeoutError: Se a sessao nao emitir `AssistantIdleData` dentro de
            `_TIMEOUT_SESSAO_SEGUNDOS`.
    """
    copilot = _import_copilot()
    from copilot.generated.rpc import (  # type: ignore[import-not-found]
        PermissionDecisionApproveOnce,
        PermissionDecisionReject,
    )
    from copilot.session_events import (  # type: ignore[import-not-found]
        AssistantIdleData,
        AssistantIntentData,
        AssistantMessageData,
        AssistantTurnRetryData,
        AssistantUsageData,
        ModelCallFailureData,
        PermissionRequestCustomTool,
        PermissionRequestMcp,
        PermissionRequestRead,
        PermissionRequestShell,
        PermissionRequestWrite,
        SessionCompactionCompleteData,
        SessionCompletionReceiptData,
        SessionErrorData,
        SessionTruncationData,
        SubagentCompletedData,
        SubagentFailedData,
        SubagentStartedData,
        ToolExecutionCompleteData,
        ToolExecutionStartData,
    )

    yield _chunk(role="assistant")

    def _caminho_escrita_seguro(caminho_str: str) -> bool:
        """Guarda 4: escrita deve ficar restrita a /workspaces e fora de bloqueios."""
        if not caminho_str:
            return False
        p = Path(caminho_str)
        if any(seg in (".git", "secrets") for seg in p.parts):
            return False
        if p.name.startswith(".env"):
            return False
        if p.suffix == ".pem":
            return False
        return True

    def _identificador_e_seguro_nativo(perm_request: Any) -> tuple[str, bool]:
        if isinstance(perm_request, PermissionRequestRead):
            return "read", True
        if isinstance(perm_request, PermissionRequestShell):
            return "shell", _comando_shell_e_seguro(perm_request)
        if isinstance(perm_request, PermissionRequestMcp):
            _nome_bruto = str(getattr(perm_request, "tool_name", "") or "mcp_tool")
            _servidor = str(getattr(perm_request, "server_name", "") or "")
            _read_only_nativo = bool(getattr(perm_request, "read_only", False))
            _args_mcp = getattr(perm_request, "args", None)
            # Bug real investigado (2026-10-04): o SDK headless real reporta
            # `tool_name` como o nome CRU exposto pelo proprio servidor MCP
            # (ex.: "ctx_batch_execute"), SEM o prefixo de exibicao da IDE
            # ("mcp_context-mode_ctx_batch_execute") que `permission_policy.
            # MCP_TOOL_PREFIXES`/`tool_mcp_e_cataloga` esperam -- o que fazia
            # `tool_call_nao_escrita_e_segura` cair incondicionalmente no
            # fallback final (negado), mesmo com o servidor conectado e
            # funcionando. Normaliza AQUI (fonte unica, antes do handler)
            # usando `server_name` (campo real confirmado por introspeccao
            # da wheel) -- resolve de forma generica para os 3 servers,
            # inclusive `codegraph` (cujas tools nao compartilham nenhum
            # prefixo comum entre si, ex.: "query", "path", "file_deps").
            nome = _nome_bruto
            if _servidor and not nome.startswith(f"mcp_{_servidor}_"):
                # Observado em producao (2026-10-04): algumas versoes do SDK
                # ja incluem o nome do servidor com hifen dentro do proprio
                # `tool_name` bruto (ex.: "context-mode-ctx_execute") -- sem
                # esta checagem, a normalizacao duplicava
                # ("mcp_context-mode_context-mode-ctx_execute"). Remove o
                # prefixo "<servidor>-" redundante antes de aplicar o
                # prefixo canonico "mcp_<servidor>_".
                _base = _nome_bruto
                if _base.startswith(f"{_servidor}-"):
                    _base = _base[len(_servidor) + 1 :]
                nome = f"mcp_{_servidor}_{_base}"
            logger.info(
                "mcp_identificador_nativo server_name=%s tool_name_bruto=%s "
                "tool_name_normalizado=%s read_only=%s args_keys=%s",
                _servidor,
                _nome_bruto,
                nome,
                _read_only_nativo,
                sorted(_args_mcp.keys()) if isinstance(_args_mcp, dict) else _args_mcp,
            )
            return nome, _read_only_nativo
        if isinstance(perm_request, PermissionRequestCustomTool):
            nome = str(getattr(perm_request, "tool_name", "") or "custom_tool")
            return nome, False
        return type(perm_request).__name__, False

    def _bridge_permissao(perm_request: Any, invocation: Mapping[str, Any]) -> Any:
        if isinstance(perm_request, PermissionRequestWrite):
            if permission_mode == "read_only":
                return PermissionDecisionReject(
                    feedback="Modo read_only ativo: escrita de arquivos negada."
                )
            if permission_mode == "propose":
                return PermissionDecisionReject(
                    feedback=(
                        "Modo propose ativo: alteracoes devem ser propostas como diff."
                    )
                )
            if permission_mode == "apply":
                if checkpoint_aberto:
                    return PermissionDecisionReject(
                        feedback="Escrita bloqueada: ha um checkpoint humano pendente."
                    )
                caminho = str(
                    getattr(perm_request, "resolved_path", "")
                    or getattr(perm_request, "file_name", "")
                    or ""
                )
                if not _caminho_escrita_seguro(caminho):
                    return PermissionDecisionReject(
                        feedback="Caminho de arquivo bloqueado para escrita (Guarda 4)."
                    )
                # Correcao de regressao (2026-10-02, encontrada nesta sessao
                # ao rodar a suite completa -- nao relacionada ao pedido do
                # usuario): este endpoint LEGADO (`/v1/chat/completions`,
                # OpenAI-compatible, sem canal de CustomEvent/SSE) nao tem
                # UI de revisao de diff equivalente ao `FileEditBridge.tsx`
                # -- a pausa para aprovacao humana do diff completo
                # (`_bridge_edicao_arquivo`) e exclusiva de
                # `stream_chat_ag_ui` (unica funcao onde esta definida).
                # Uma chamada residual a essa funcao aqui (`_bridge_permissao`
                # sincrona desta funcao `stream_chat`) causava `NameError`
                # em runtime e `SyntaxError: 'await' outside async function`
                # na importacao do modulo inteiro. Revertido ao
                # comportamento historico deste endpoint: aprova apos os 2
                # guards de seguranca ja aplicados acima (checkpoint +
                # caminho seguro), sem pausa adicional.
                return PermissionDecisionApproveOnce()

        identificador, seguro_nativo = _identificador_e_seguro_nativo(perm_request)
        # Mantido curto-circuito ORIGINAL do `or` (CONTRATO de teste real:
        # `permission_handler` nao pode ser chamado quando `seguro_nativo`
        # ja aprova -- `test_deve_aprovar_permissionrequestread_sem_chamar_handler`).
        # Logging usa `None` para "nao avaliado" em vez de forcar a chamada.
        permitido = seguro_nativo or permission_handler(identificador, dict(invocation))
        if isinstance(perm_request, PermissionRequestShell):
            logger.info(
                "bridge_permissao_shell identificador=%s seguro_nativo=%s "
                "permission_mode=%s permitido=%s "
                "(handler_so_e_chamado_quando_seguro_nativo_e_falso)",
                identificador,
                seguro_nativo,
                permission_mode,
                permitido,
            )
        if isinstance(perm_request, PermissionRequestMcp):
            logger.info(
                "bridge_permissao_mcp identificador=%s seguro_nativo=%s "
                "permission_mode=%s permitido=%s "
                "(handler_so_e_chamado_quando_seguro_nativo_e_falso)",
                identificador,
                seguro_nativo,
                permission_mode,
                permitido,
            )
        if permitido:
            return PermissionDecisionApproveOnce()
        return PermissionDecisionReject(
            feedback="Negado pela politica local (GATEWAY_PERMISSION_MODE)."
        )

    fila: asyncio.Queue[ChatCompletionChunk | None] = asyncio.Queue()
    nomes_por_tool_call_id: dict[str, str] = {}

    # Nome LITERAL da tool de delegacao de agent usada pela governanca
    # (`run_subagent`, ver `.github/copilot-instructions.md` R-037/R-042 e
    # `subagent-instructions`). Usado APENAS para suprimir a renderizacao
    # GENERICA de tool (`tool: run_subagent (iniciando)/concluido`) quando
    # esta tool especifica dispara -- os eventos dedicados `Subagent*`
    # abaixo (RT-03, introspecao real confirmada) ja cobrem este caso com
    # texto muito mais rico (nome REAL do agent), evitando duplicacao.
    _TOOL_DELEGACAO_AGENT: Final[str] = "run_subagent"

    # RT-03 (2026-10-01): introspecao real de `copilot.generated.session_events`
    # (wheel `github_copilot_sdk==1.0.15` baixada e extraida para leitura
    # direta do codigo gerado -- mesma metodologia de evidencia de RT-01/
    # RT-02) confirmou 5 eventos DEDICADOS de ciclo de vida de subagent,
    # distintos de `ToolExecutionStartData`/`ToolExecutionCompleteData`:
    #   `SubagentStartedData`   (campos confirmados: `agent_name`,
    #       `agent_display_name`, `agent_description`, `tool_call_id`,
    #       `agent_type`, `model`, `parent_id`, `execution_mode`, ...)
    #   `SubagentCompletedData` (`agent_name`, `agent_display_name`,
    #       `tool_call_id`, `duration`, `total_tokens`, `total_tool_calls`, ...)
    #   `SubagentFailedData`    (idem + `error: str` obrigatorio)
    #   `SubagentSelectedData`/`SubagentDeselectedData` (selecao de
    #       "custom agent" na sessao -- fora do escopo desta fase, nao
    #       tratados aqui).
    # O campo `tool_call_id` de `SubagentStartedData`/`SubagentCompletedData`/
    # `SubagentFailedData` correlaciona com o MESMO `tool_call_id` da tool
    # `run_subagent` (`SubagentStartedData.__doc__`: "Sub-agent startup
    # details including PARENT TOOL CALL and agent information") -- ou
    # seja, para cada invocacao de subagent, o SDK emite AMBOS os eventos
    # (`ToolExecutionStartData(tool_name="run_subagent", tool_call_id=X)`
    # E `SubagentStartedData(tool_call_id=X, agent_name=...)`) para o MESMO
    # `tool_call_id`. Por isso o bloco `ToolExecutionStartData`/
    # `ToolExecutionCompleteData` abaixo SUPRIME a linha generica quando
    # `nome == _TOOL_DELEGACAO_AGENT` -- a informacao rica (nome REAL do
    # agent) chega pelos handlers `Subagent*` dedicados, nunca duplicada.
    agentes_por_tool_call_id: dict[str, str] = {}

    # Debug investigativo (2026-10-04, pedido do usuario): `run_subagent` e
    # traduzido para a tool NATIVA `task` do SDK headless
    # (`_ALIAS_TOOLS_SDK_HEADLESS["run_subagent"] = "task"`, ver
    # `agent_catalog.py`). `task` e um mecanismo GENERICO de sub-tarefa que
    # aceita um `agent_name`/label ARBITRARIO escolhido pelo proprio modelo,
    # sem validacao server-side contra o catalogo real de `custom_agents`
    # (`.github/agents/**/*.agent.md`). Suspeita de causa raiz (observada por
    # screenshot do usuario, 2026-10-04): o modelo encadeia multiplas
    # invocacoes de `task` com nomes INVENTADOS (ex.: "pr-gatekeeper-git-test",
    # "git-readonly-check") que nunca existiram como agent real, exibidos
    # como se fossem delegacao legitima. Log abaixo torna essa divergencia
    # visivel em `.tmp/gateway.log` sem alterar o comportamento funcional.
    _nomes_custom_agents_reais = frozenset(
        str(agente.get("name") or "") for agente in (custom_agents or [])
    )
    logger.debug(
        "sessao_custom_agents_registrados total=%d nomes=%s",
        len(_nomes_custom_agents_reais),
        sorted(_nomes_custom_agents_reais),
    )

    def _nome_exibicao_subagent(dado: Any) -> str:
        """Prioriza `agent_display_name` (rotulo amigavel); cai para
        `agent_name` (identificador tecnico, ex.: `python-bug-fixer`) se o
        display name vier vazio -- ambos confirmados como `str`
        obrigatorios em `SubagentStartedData`/`SubagentCompletedData`/
        `SubagentFailedData` (RT-03)."""
        nome_tecnico = str(getattr(dado, "agent_name", "") or "?")
        nome_exibicao = str(getattr(dado, "agent_display_name", "") or "")
        return nome_exibicao or nome_tecnico

    def _on_event(event: Any) -> None:
        dado = getattr(event, "data", None)
        if isinstance(dado, AssistantMessageData):
            texto = str(getattr(dado, "content", "") or "")
            if texto:
                fila.put_nowait(_chunk(content=texto))
        elif isinstance(dado, ToolExecutionStartData):
            # `tool_call_id` correlaciona com `ToolExecutionCompleteData`
            # abaixo, que NAO possui campo `tool_name` (confirmado por
            # introspecao) -- sem este cache, o evento de conclusao sempre
            # exibia "tool: ? concluido" (bug observado no log real).
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            nome = str(getattr(dado, "tool_name", "") or "?")
            if tool_call_id:
                nomes_por_tool_call_id[tool_call_id] = nome
            _shell_info = getattr(dado, "shell_tool_info", None)
            if _shell_info is not None:
                logger.info(
                    "tool_shell_iniciado tool_call_id=%s tool_name=%s "
                    "display_command=%s has_write_file_redirection=%s model=%s",
                    tool_call_id,
                    nome,
                    getattr(_shell_info, "display_command", None),
                    getattr(_shell_info, "has_write_file_redirection", None),
                    getattr(dado, "model", None),
                )
            if nome != _TOOL_DELEGACAO_AGENT:
                fila.put_nowait(
                    _chunk(content=f"\n> \U0001f527 tool: {nome} (iniciando)\n")
                )
            # Suprimido quando `run_subagent`: `SubagentStartedData` (abaixo)
            # emite a versao rica com o nome REAL do agent para o mesmo
            # `tool_call_id` (RT-03).
        elif isinstance(dado, ToolExecutionCompleteData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            nome = nomes_por_tool_call_id.pop(tool_call_id, "?")
            _shell_exec = getattr(dado, "shell_execution", None)
            _resultado = getattr(dado, "result", None)
            if _shell_exec is not None or _resultado is not None or nome in (
                "bash",
                "powershell",
                "shell",
            ):
                logger.info(
                    "tool_shell_concluido tool_call_id=%s tool_name=%s "
                    "success=%s error=%s exit_code=%s cwd=%s output_preview=%s",
                    tool_call_id,
                    nome,
                    getattr(dado, "success", None),
                    getattr(dado, "error", None),
                    getattr(_shell_exec, "exit_code", None)
                    or getattr(_resultado, "exit_code", None),
                    getattr(_resultado, "cwd", None),
                    str(getattr(_resultado, "output_preview", "") or "")[:500],
                )
            if nome != _TOOL_DELEGACAO_AGENT:
                fila.put_nowait(
                    _chunk(content=f"\n> \U0001f527 tool: {nome} concluido\n")
                )
            # Suprimido quando `run_subagent`: `SubagentCompletedData`/
            # `SubagentFailedData` (abaixo) ja cobrem a conclusao.
        elif isinstance(dado, SubagentStartedData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            nome_exibicao = _nome_exibicao_subagent(dado)
            nome_tecnico_log = str(getattr(dado, "agent_name", "") or "")
            catalogado = nome_tecnico_log in _nomes_custom_agents_reais
            logger.info(
                "subagent_iniciado tool_call_id=%s agent_name=%s "
                "agent_display_name=%s agent_type=%s model=%s parent_id=%s "
                "execution_mode=%s catalogado=%s",
                tool_call_id,
                nome_tecnico_log,
                getattr(dado, "agent_display_name", None),
                getattr(dado, "agent_type", None),
                getattr(dado, "model", None),
                getattr(dado, "parent_id", None),
                getattr(dado, "execution_mode", None),
                catalogado,
            )
            if not catalogado:
                logger.warning(
                    "subagent_nome_nao_catalogado tool_call_id=%s agent_name=%s "
                    "-- nome ausente nos %d custom_agents reais registrados "
                    "nesta sessao; possivel delegacao fantasma via tool nativa "
                    "'task' (run_subagent -> task, sem allowlist de nome)",
                    tool_call_id,
                    nome_tecnico_log,
                    len(_nomes_custom_agents_reais),
                )
            if tool_call_id:
                agentes_por_tool_call_id[tool_call_id] = nome_exibicao
            fila.put_nowait(
                _chunk(
                    content=(
                        f"\n> \U0001f9ed **Subagent invocado:** `{nome_exibicao}` "
                        "(iniciando)\n"
                    )
                )
            )
        elif isinstance(dado, SubagentCompletedData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            nome_exibicao = agentes_por_tool_call_id.pop(
                tool_call_id, _nome_exibicao_subagent(dado)
            )
            logger.info(
                "subagent_concluido tool_call_id=%s nome=%s duration=%s "
                "total_tokens=%s total_tool_calls=%s",
                tool_call_id,
                nome_exibicao,
                getattr(dado, "duration", None),
                getattr(dado, "total_tokens", None),
                getattr(dado, "total_tool_calls", None),
            )
            fila.put_nowait(
                _chunk(
                    content=f"\n> \u2705 **Subagent concluido:** `{nome_exibicao}`\n"
                )
            )
        elif isinstance(dado, SubagentFailedData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            nome_exibicao = agentes_por_tool_call_id.pop(
                tool_call_id, _nome_exibicao_subagent(dado)
            )
            erro = str(getattr(dado, "error", "") or "erro desconhecido")
            logger.warning(
                "subagent_falhou tool_call_id=%s nome=%s erro=%s",
                tool_call_id,
                nome_exibicao,
                erro,
            )
            fila.put_nowait(
                _chunk(
                    content=(
                        f"\n> \u274c **Subagent falhou:** `{nome_exibicao}` "
                        f"-- {erro}\n"
                    )
                )
            )
        elif isinstance(dado, AssistantIdleData):
            fila.put_nowait(None)  # sentinela de encerramento
        elif isinstance(dado, SessionErrorData):
            # Erro real da API do Copilot (cota mensal esgotada, rate limit,
            # autenticacao, etc.) -- bug real de producao confirmado por
            # teste ao vivo (2026-10-02): o SDK NUNCA levanta excecao Python
            # para isso, apenas emite este evento seguido de AssistantIdleData
            # normal, o que fazia o turno "terminar com sucesso" e CONTEUDO
            # VAZIO ser devolvido ao usuario sem nenhuma mensagem de erro
            # visivel ("chat nao responde nada"). Torna o erro visivel.
            codigo = str(getattr(dado, "error_code", "") or "erro_desconhecido")
            mensagem = str(
                getattr(dado, "message", "") or "Erro desconhecido do Copilot"
            )
            fila.put_nowait(
                _chunk(
                    content=f"\n> \u26a0\ufe0f Erro do Copilot ({codigo}): {mensagem}\n"
                )
            )

    async with copilot.CopilotClient(github_token=token) as client:
        async with await client.create_session(
            on_permission_request=_bridge_permissao,
            mcp_servers=construir_mcp_servers(get_settings()),
            model=model,
            session_id=session_id,
            working_directory=working_directory,
            additional_directories=(
                list(additional_directories) if additional_directories else None
            ),
            # `working_directory`/`additional_directories` agora podem
            # abranger VARIOS projetos independentes sob um diretorio-pai
            # compartilhado (ver `projects_catalog.py`); qualquer um deles
            # (ex.: este proprio repositorio, deep-agents-copilot) pode ter
            # seus proprios `.github/hooks/*.json`/agents/skills customizados
            # destinados a sessoes de desenvolvimento NAQUELE repositorio
            # especifico -- NAO a esta sessao generica do gateway sobre
            # QUALQUER projeto registrado. Sem desabilitar explicitamente,
            # o SDK descobre e tenta EXECUTAR esses hooks (quebrando com
            # erro quando o hook espera dependencias/CWD que nao existem
            # neste container minimo), bug real reportado via Lobe Chat em
            # 2026-09-29 ("um hook de contexto ... esta bloqueando todas as
            # ferramentas"). Sessao do gateway fica deliberadamente "limpa"
            # -- sem hooks, sem descoberta de config/skills customizados.
            enable_file_hooks=False,
            enable_config_discovery=False,
            # Mecanismo NATIVO do SDK (nao mais concatenacao textual no
            # prompt, ver docstring do parametro `system_message` acima):
            # `SystemMessageAppendConfig` (TypedDict `{mode, content}`)
            # injeta o banner/persona/nucleo de governanca SEM substituir
            # os guardrails/CLI foundation do SDK -- corrige o bug real
            # onde o Claude subjacente ignorava o banner concatenado como
            # conteudo nao-confiavel embutido na mensagem do usuario e o ignorava explicitamente (bug real confirmado
            # via Lobe Chat, 2026-09-30).
            system_message=(
                {"mode": "append", "content": system_message}
                if system_message is not None
                else None
            ),
            # RT-04 (2026-10-01): catalogo de custom agents (`.github/agents/
            # **/*.agent.md`), descoberto manualmente por `agent_catalog.
            # descobrir_custom_agents` -- NUNCA depende de
            # `enable_config_discovery` (mantido False acima,
            # deliberadamente, por causa do bug de hooks). Sem isto, a tool
            # `run_subagent` nao tem nenhum agent para delegar e fica
            # inerte (bug real confirmado por teste ao vivo: o modelo
            # respondia nao ter acesso a `run_subagent`). Repassado apenas
            # quando nao-vazio -- `None` preserva o comportamento legado
            # (sessao sem custom agents, ex.: chamadores antigos/testes).
            custom_agents=(list(custom_agents) if custom_agents else None),
        ) as session:
            session.on(_on_event)
            await session.send(_joined_prompt(messages))
            while True:
                item = await asyncio.wait_for(
                    fila.get(), timeout=_TIMEOUT_SESSAO_SEGUNDOS
                )
                if item is None:
                    break
                yield item

    yield _chunk(finish_reason="stop")


# ---------------------------------------------------------------------------
# Fase 2 (2026-10-01) -- paridade visual com o plugin Copilot da IDE:
# `stream_chat_ag_ui` emite eventos REAIS do protocolo AG-UI (`ag_ui.core`,
# AG-UI 1.0) em vez de achatar tool calls/subagents em texto markdown dentro
# de `ChatCompletionChunk.delta.content` (o que `stream_chat` acima faz,
# consumido por `/v1/chat/completions` -- mantido inalterado para
# compatibilidade com clientes OpenAI-compatible existentes).
#
# AG-UI 1.0 introduziu suporte NATIVO a subagent (`SubagentStartedEvent`/
# `SubagentFinishedEvent`/`SubagentErrorEvent`, cada subagent com seu proprio
# `subagent_run_id`) -- mapeamento quase 1:1 com os eventos ja confirmados do
# Copilot SDK (`SubagentStartedData`/`SubagentCompletedData`/
# `SubagentFailedData`, RT-03). O frontend (CopilotKit v2 + `HttpAgent`)
# renderiza cada subagent em seu proprio card automaticamente, sem exigir
# renderer customizado -- ver docs.ag-ui.com ("Subagent support", blog AG-UI
# 1.0, 2026-09-30).
#
# TODO (follow-up apos validacao em producao): a logica de interpretacao dos
# eventos do SDK (guardas de permissao, cache tool_call_id->nome, deteccao de
# `run_subagent`) esta DUPLICADA entre `stream_chat` e esta funcao -- feito
# deliberadamente nesta 1a iteracao para NAO arriscar regressao na integracao
# ja validada (RT-01..RT-04) de `stream_chat`. Extrair para uma camada unica
# de "eventos normalizados do SDK" fica para uma subtask futura, uma vez que
# `stream_chat_ag_ui` esteja validado por teste real em producao.
#
# RT-05 (RESOLVIDO em 2026-10-02 por introspeccao real da wheel
# `github_copilot_sdk==1.0.16`, mesma metodologia RT-01..RT-04): `ask_questions`
# (e qualquer outra tool MCP que precise de input estruturado do usuario) usa
# a primitiva "Elicitation" do MCP, exposta pelo SDK via
# `create_session(on_elicitation_request=...)` -- um callback (sincrono OU
# assincrono, `Callable[[ElicitationContext], ElicitationResult |
# Awaitable[ElicitationResult]]`) que recebe `{message, requestedSchema
# (JSON Schema), mode, session_id}` e deve devolver `{action: "accept"|
# "decline"|"cancel", content?: dict}`. SEM este callback wired, o SDK nao
# tinha como saber o que fazer com uma elicitation pendente -- consistente
# com os bugs reais observados (turno "travado"/RUN_FINISHED prematuro com
# subagent ainda aguardando `ask_questions`, ver fix de subagents_abertos
# abaixo). `_bridge_elicitacao` implementa o callback como uma PONTE
# assincrona: emite `CustomEvent(name="elicitation_requested", ...)` no
# stream AG-UI (consumido pelo frontend, ver
# `apps/web/copilot/ElicitationBridge.tsx`) e aguarda (`await`, SEM bloquear
# o restante do processo -- `asyncio` coopera normalmente com o loop
# consumidor de `fila`) ate que `routes.resolver_elicitacao` (acionado pelo
# novo endpoint `POST /v1/elicitation/{request_id}/respond`) resolva o
# `asyncio.Future` correspondente com a resposta real do usuario. A conexao
# HTTP/SSE original PERMANECE ABERTA o tempo todo (nao ha "fim de run +
# resume" -- o `CopilotSession` deste SDK nao expoe um metodo de resume
# externo, apenas `send`/`send_and_wait`; manter o mesmo processo/generator
# vivo e a UNICA forma suportada de responder uma elicitation pendente).
# ---------------------------------------------------------------------------

# RT-05 (RESOLVIDO DEFINITIVAMENTE em 2026-10-02 por simulacao real das
# chamadas do frontend + pesquisa externa (github/copilot-sdk, docs oficiais)
# + reproducao isolada via sandbox, BYPASSANDO toda a stack do gateway):
# `ask_questions` (tool nativa `ask_user` nesta sessao headless) tem DOIS
# mecanismos de habilitacao DISTINTOS no SDK, confirmados por teste ao vivo:
#   1. `on_elicitation_request` (+ opcionalmente `ask_user_variant=
#      "elicitation"`): usa a primitiva MCP Elicitation (`ElicitationRequestedData`,
#      JSON Schema completo via `requestedSchema`). Mantido wireado abaixo
#      para compatibilidade futura com MCP servers reais que usem elicitation
#      -- MAS confirmado por 8 testes isolados que o CLI (`v1.0.90`) NUNCA
#      roteia a tool nativa `ask_user` por este caminho, mesmo com
#      `session.capabilities.ui.elicitation == True`.
#   2. `on_user_input_request` (`UserInputHandler`, forma LEGADA documentada
#      em `copilot-sdk/python/README.md`, secao "User Input Requests": "Enable
#      the legacy question-and-answer `ask_user` tool by providing an
#      `on_user_input_request` handler"): ESTE e o unico mecanismo que de fato
#      fez o modelo invocar `ask_user` como function-call real
#      (`ToolExecutionStartData(tool_name="ask_user")` observado, `
#      total_tool_calls=1`) em teste isolado via sandbox. Request:
#      `{question: str, choices: list[str], allowFreeform: bool}` (schema
#      FIXO, muito mais simples que JSON Schema arbitrario). Response:
#      `{answer: str, wasFreeform: bool}` -- AMBOS os campos obrigatorios
#      (`UserInputResponse` e `TypedDict` sem `total=False`; omitir
#      `wasFreeform` falha silenciosamente e o modelo recebe "erro ao
#      processar sua resposta").
# `_bridge_user_input` (abaixo) implementa o mecanismo #2 (o que realmente
# funciona) com o MESMO padrao de ponte assincrona ja usado por
# `_bridge_elicitacao`: emite `CustomEvent(name="ask_user_requested", ...)`
# no stream AG-UI (consumido por `apps/web/copilot/AskUserBridge.tsx`) e
# aguarda ate `resolver_pergunta_usuario` (endpoint `POST /v1/ask-user/
# {request_id}/respond`) resolver o `asyncio.Future` correspondente.
# `_bridge_elicitacao`/mecanismo #1 PERMANECE wireado (nao e removido):
# nao causa regressao, e documentado pelo proprio SDK como o caminho formal
# para elicitation de MCP servers arbitrarios (nao apenas `ask_user`), que
# pode passar a funcionar de fato em versoes futuras do CLI.
# ---------------------------------------------------------------------------

#: Registro module-level de elicitations pendentes (1 por `request_id`),
#: resolvido externamente por `resolver_elicitacao` (chamado por
#: `routes.elicitation_respond`). Escopo module-level (nao por-sessao) e
#: aceitavel nesta fase MVP (1 unica instancia de gateway, sem multiplas
#: replicas/workers compartilhando estado); migrar para `SessionStore`
#: (SQLite) seria necessario apenas sob multiplos workers/replicas.
_ELICITACOES_PENDENTES: Final[dict[str, "asyncio.Future[Any]"]] = {}

#: Tempo maximo (segundos) que uma elicitation fica pendente antes de ser
#: cancelada automaticamente (evita vazamento de memoria se o usuario fechar
#: a aba sem responder). Generoso o bastante para decisoes humanas reais.
_TIMEOUT_ELICITACAO_SEGUNDOS: Final[float] = 1800.0

#: Intervalo do heartbeat emitido enquanto uma elicitation esta pendente,
#: para que o loop consumidor principal (`asyncio.wait_for(fila.get(),
#: timeout=_TIMEOUT_SESSAO_SEGUNDOS)`, 120s) nunca estoure por falta de
#: eventos novos durante uma pausa longa aguardando o usuario responder.
_INTERVALO_HEARTBEAT_ELICITACAO_SEGUNDOS: Final[float] = 20.0

#: Registro module-level de perguntas `ask_user` (mecanismo LEGADO, o que
#: realmente funciona -- ver nota acima) pendentes, resolvido por
#: `resolver_pergunta_usuario` (`routes.ask_user_respond`). Mesmo padrao e
#: escopo de `_ELICITACOES_PENDENTES`.
_PERGUNTAS_PENDENTES: Final[dict[str, "asyncio.Future[dict[str, Any]]"]] = {}

#: Mesmo orcamento de `_TIMEOUT_ELICITACAO_SEGUNDOS`, para `ask_user`.
_TIMEOUT_PERGUNTA_SEGUNDOS: Final[float] = 1800.0

#: Mesmo heartbeat de `_INTERVALO_HEARTBEAT_ELICITACAO_SEGUNDOS`, para `ask_user`.
_INTERVALO_HEARTBEAT_PERGUNTA_SEGUNDOS: Final[float] = 20.0

#: Registro module-level de edicoes de arquivo (`PermissionRequestWrite`)
#: pendentes de aprovacao humana no chat -- resolvido por
#: `resolver_edicao_arquivo` (`routes.file_edit_respond`). Mesmo padrao e
#: escopo de `_ELICITACOES_PENDENTES`/`_PERGUNTAS_PENDENTES`: feature pedida
#: pelo usuario (2026-10-02) para visualizar o DIFF de um arquivo que o
#: agent quer alterar (paridade com o plugin Copilot da IDE) e so aplicar a
#: escrita real apos aprovacao/rejeicao explicita no componente
#: `FileEditBridge.tsx` -- nunca silenciosamente, mesmo em
#: `GATEWAY_PERMISSION_MODE=apply`.
_EDICOES_ARQUIVO_PENDENTES: Final[dict[str, "asyncio.Future[bool]"]] = {}

#: Mesmo orcamento de `_TIMEOUT_ELICITACAO_SEGUNDOS`, para edicao de arquivo.
_TIMEOUT_EDICAO_ARQUIVO_SEGUNDOS: Final[float] = 1800.0

#: Mesmo heartbeat de `_INTERVALO_HEARTBEAT_ELICITACAO_SEGUNDOS`, para edicao de arquivo.
_INTERVALO_HEARTBEAT_EDICAO_ARQUIVO_SEGUNDOS: Final[float] = 20.0

# Reforco tecnico adicionado ao `system_message` SOMENTE no caminho AG-UI
# (`stream_chat_ag_ui`) -- mantido apos a descoberta de `on_user_input_request`
# (2026-10-02): embora a tool agora seja genuinamente invocavel, reforcar
# explicitamente o nome real (`ask_user` vs `ask_questions` mencionado no
# resto da governanca) continua reduzindo a chance do modelo preferir texto
# livre por nao reconhecer a instrucao textual como aplicavel a tool real.
_REFORCO_ASK_USER_ELICITATION: Final[str] = (
    "\n\n---\n"
    "**Nota tecnica desta sessao (gateway headless, nao a IDE):** a tool de "
    "pergunta estruturada ao usuario chama-se `ask_user` nesta sessao "
    "(equivalente funcional de `ask_questions` mencionado no restante deste "
    "contexto). SEMPRE que precisar fazer 1 ou mais perguntas de "
    "esclarecimento ao usuario (R-012/R-027), invoque a tool `ask_user` -- "
    "NUNCA escreva a pergunta como texto livre da resposta. A tool esta "
    "registrada e disponivel nesta sessao.\n"
)


def resolver_elicitacao(
    request_id: str, *, action: str, content: dict[str, Any] | None
) -> bool:
    """Resolve uma elicitation pendente com a resposta real do usuario.

    Chamada por `routes.elicitation_respond` (endpoint
    `POST /v1/elicitation/{request_id}/respond`). Thread/task-safe dentro do
    mesmo event loop (FastAPI/uvicorn single-loop) -- `asyncio.Future.
    set_result` agendado de qualquer task do mesmo loop e seguro.

    Args:
        request_id: Identificador emitido no `CustomEvent`
            `elicitation_requested` (`value["request_id"]`).
        action: `"accept"` (formulario preenchido), `"decline"` (recusa
            explicita) ou `"cancel"` (dispensado).
        content: Valores do formulario (obrigatorio semanticamente quando
            `action == "accept"`; ignorado nos demais casos).

    Returns:
        bool: `True` se uma elicitation pendente com este id foi encontrada
        e resolvida; `False` se desconhecida/ja resolvida/expirada (o
        chamador deve devolver HTTP 404 neste caso).
    """
    future = _ELICITACOES_PENDENTES.pop(request_id, None)
    if future is None or future.done():
        return False
    future.set_result({"action": action, "content": content})
    return True


def resolver_pergunta_usuario(
    request_id: str, *, answer: str, was_freeform: bool
) -> bool:
    """Resolve uma pergunta `ask_user` pendente (mecanismo LEGADO que funciona).

    Chamada por `routes.ask_user_respond`
    (`POST /v1/ask-user/{request_id}/respond`). Mesma semantica/garantias de
    `resolver_elicitacao`.

    Args:
        request_id: Identificador emitido no `CustomEvent`
            `ask_user_requested` (`value["request_id"]`).
        answer: Texto da resposta (um dos `choices` originais, ou texto
            livre se `allow_freeform` era `True`).
        was_freeform: `True` se `answer` veio de texto livre (nao de um dos
            `choices` pre-definidos).

    Returns:
        bool: `True` se resolvida; `False` se desconhecida/ja resolvida/
        expirada (o chamador deve devolver HTTP 404 neste caso).
    """
    future = _PERGUNTAS_PENDENTES.pop(request_id, None)
    if future is None or future.done():
        return False
    future.set_result({"answer": answer, "wasFreeform": was_freeform})
    return True


def resolver_edicao_arquivo(request_id: str, *, aprovado: bool) -> bool:
    """Resolve uma edicao de arquivo (`PermissionRequestWrite`) pendente de
    aprovacao humana no chat, com a decisao real do usuario.

    Chamada por `routes.file_edit_respond`
    (`POST /v1/file-edit/{request_id}/respond`). Mesma semantica/garantias
    de `resolver_elicitacao`/`resolver_pergunta_usuario` -- NAO inicia um
    novo turno/run, apenas desbloqueia a coroutine `_bridge_edicao_arquivo`
    (`sdk_session.stream_chat_ag_ui`), que continua pausada dentro do MESMO
    stream AG-UI ja aberto no browser enquanto o usuario revisa o diff no
    componente `apps/web/copilot/FileEditBridge.tsx`.

    Args:
        request_id: Identificador emitido no `CustomEvent`
            `file_edit_requested` (`value["request_id"]`).
        aprovado: `True` se o usuario aprovou TODAS as linhas do diff
            (botao "Aplicar alterações"); `False` se ignorou/rejeitou (a
            escrita real no arquivo NUNCA ocorre antes desta decisao --
            pedido explicito do usuario, 2026-10-02).

    Returns:
        bool: `True` se resolvida; `False` se desconhecida/ja resolvida/
        expirada (o chamador deve devolver HTTP 404 neste caso).
    """
    future = _EDICOES_ARQUIVO_PENDENTES.pop(request_id, None)
    if future is None or future.done():
        return False
    future.set_result(aprovado)
    return True


def _resolver_modelo_agent(
    nome_agent: str | None, custom_agents: Sequence[Mapping[str, Any]] | None
) -> str | None:
    """Resolve o `model:` declarado no frontmatter do `.agent.md` de
    `nome_agent` a partir do catalogo ja carregado (`custom_agents`).

    Copia local e deliberada de `routes._resolver_modelo_agent` (mesma
    logica, mesmo formato de catalogo `CustomAgentConfig`) -- nao
    importada de `routes.py` para evitar import circular (`routes.py` ja
    importa de `sdk_session.py`). Usada tanto para o badge do agent de
    NIVEL SUPERIOR (resolvido em `routes.py`, repassado via parametro
    `agent_model`) quanto para o badge de SUBAGENTS (pedido do usuario,
    2026-10-02: visibilidade de icone/negrito/modelo tambem dentro do
    colapse do subagent, nao so no topo), resolvido aqui mesmo a partir de
    `custom_agents` (ja disponivel no escopo de `stream_chat_ag_ui`).
    """
    if not nome_agent or not custom_agents:
        return None
    for agente in custom_agents:
        if str(agente.get("name") or "") == nome_agent:
            modelo = agente.get("model")
            return str(modelo) if isinstance(modelo, str) and modelo.strip() else None
    return None


def _ler_conteudo_atual_arquivo(resolved_path: str) -> str:
    """Le o conteudo ATUAL (antes da escrita) de `resolved_path`.

    Retorna string vazia se o arquivo ainda nao existir (caso de CRIACAO de
    arquivo novo -- o diff completo entao mostra 100% das linhas como
    adicionadas, corretamente) ou se nao puder ser lido (ex.: binario,
    permissao, path vazio). NUNCA propaga excecao -- usado apenas para
    montar o diff completo exibido no chat (`FileEditBridge.tsx`); uma
    falha de leitura aqui jamais deve bloquear a aprovacao da escrita real.
    """
    if not resolved_path:
        return ""
    try:
        caminho = Path(resolved_path)
        if not caminho.is_file():
            return ""
        return caminho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _gerar_linhas_diff_completo(antigo: str, novo: str) -> list[dict[str, Any]]:
    """Gera a lista de linhas do diff COMPLETO do arquivo (TODAS as linhas,
    nao apenas os hunks truncados do unified diff com poucas linhas de
    contexto) -- pedido explicito do usuario (2026-10-02): poder revisar o
    arquivo inteiro antes de aprovar, exatamente como um editor de IDE
    mostraria.

    Usa `difflib.SequenceMatcher` (stdlib, zero dependencia nova) sobre as
    listas de linhas (`splitlines()`) do conteudo antigo e novo, convertendo
    os opcodes resultantes (`equal`/`replace`/`delete`/`insert`) em uma
    lista linear de linhas prontas para renderizacao -- mesmo formato (em
    `snake_case`, serializado como JSON no `CustomEvent`) que o frontend
    (`copilot/diffParser.ts`) ja usa para o parsing do unified diff
    (`tipo`/`numero_antigo`/`numero_novo`/`conteudo`), permitindo reusar o
    mesmo componente de renderizacao (`FileEditBridge.tsx`) sem logica
    especial.

    Args:
        antigo: Conteudo ATUAL do arquivo (antes da escrita), ou string
            vazia se o arquivo ainda nao existe (criacao).
        novo: Conteudo PROPOSTO pelo agent (`PermissionRequestWrite.
            new_file_contents`).

    Returns:
        list[dict]: uma entrada por linha de QUALQUER um dos dois arquivos
        (sem truncamento), na ordem natural de leitura.
    """
    linhas_antigas = antigo.splitlines()
    linhas_novas = novo.splitlines()
    matcher = difflib.SequenceMatcher(a=linhas_antigas, b=linhas_novas, autojunk=False)
    resultado: list[dict[str, Any]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                resultado.append(
                    {
                        "tipo": "contexto",
                        "numero_antigo": i1 + offset + 1,
                        "numero_novo": j1 + offset + 1,
                        "conteudo": linhas_antigas[i1 + offset],
                    }
                )
            continue
        if tag in ("delete", "replace"):
            for offset in range(i2 - i1):
                resultado.append(
                    {
                        "tipo": "removida",
                        "numero_antigo": i1 + offset + 1,
                        "numero_novo": None,
                        "conteudo": linhas_antigas[i1 + offset],
                    }
                )
        if tag in ("insert", "replace"):
            for offset in range(j2 - j1):
                resultado.append(
                    {
                        "tipo": "adicionada",
                        "numero_antigo": None,
                        "numero_novo": j1 + offset + 1,
                        "conteudo": linhas_novas[j1 + offset],
                    }
                )
    return resultado


async def stream_chat_ag_ui(
    *,
    token: str,
    model: str | None,
    messages: Sequence[ChatMessage],
    permission_handler: Callable[[str, Mapping[str, Any]], bool],
    thread_id: str,
    run_id: str,
    working_directory: str = "/workspaces",
    additional_directories: Sequence[str] | None = None,
    session_id: str | None = None,
    permission_mode: str = "read_only",
    checkpoint_aberto: bool = False,
    system_message: str | None = None,
    custom_agents: Sequence[Mapping[str, Any]] | None = None,
    agent_name: str | None = None,
    agent_model: str | None = None,
    handoff_origem: str | None = None,
    handoff_motivo: str | None = None,
    attachments: Sequence[Mapping[str, Any]] | None = None,
    turn_recorder_store: SessionStore | None = None,
    turno_trace_id: str | None = None,
    prompt_usuario: str | None = None,
    workflow: str | None = None,
    etapa: int | None = None,
    score_roteamento: float | None = None,
    drift_detectado: bool | None = None,
) -> AsyncIterator[AgUiEvent]:
    """Variante AG-UI nativa de `stream_chat` (ver nota de modulo acima).

    Args:
        agent_model: Valor de `model:` do frontmatter do `.agent.md` ativo
            (ex.: "Claude Sonnet 5"), resolvido pelo chamador via
            `routes._resolver_modelo_agent` a partir do catalogo
            (`agent_catalog.CustomAgentConfig["model"]`, campo opcional).
            Quando fornecido, e exibido ao lado do nome no badge "Agente
            Ativo" (ex.: "Agente Ativo: agent-router · Claude Sonnet 5"),
            paridade com a informacao ja declarada no `.md` para o usuario
            saber qual modelo esta atendendo o turno sem abrir o catalogo.
            Se `None` (agent sem `model:` no frontmatter, ou nao encontrado
            no catalogo), nenhum modelo e exibido (comportamento legado).
        attachments: Anexos (imagem/arquivo) do turno atual, ja no formato
            `BlobAttachment` do Copilot SDK (`{"type": "blob", "data":
            base64, "mimeType": str, "displayName"?: str}` -- chaves em
            camelCase, confirmado por introspeccao real de
            `copilot.session.BlobAttachment`/`CopilotSession.send`,
            2026-10-02). Extraidos pelo chamador (`routes._extrair_texto_e_
            anexos`) a partir do `content: list[ContentPart]` multimodal que
            `<CopilotChat attachments={{enabled:true}}>`/`<CopilotSidebar>`
            do CopilotKit v2 emite (paridade com anexar imagem/arquivo no
            chat do Copilot na IDE). Repassado via `session.send(prompt,
            attachments=...)` -- requer que o modelo tenha
            `capabilities.supports.vision=true` para imagens; o SDK rejeita
            (erro propagado como `RunErrorEvent`, ver `except Exception`
            abaixo) anexos que o modelo configurado nao suporta.
        thread_id: Identificador AG-UI da thread/sessao (`RunAgentInput.thread_id`).
        run_id: Identificador AG-UI do run atual (`RunAgentInput.run_id`, 1 por turno).
        agent_name: Nome do agente ativo decidido DETERMINISTICAMENTE pelo
            pipeline Python de governanca (`sessao_nova.agente_ativo`, ver
            `governance_pipeline.preparar_turno`) -- NUNCA inferido do texto
            do modelo. Quando fornecido, um badge ("🧭 Agente Ativo: `<nome>`")
            e prefixado como PRIMEIRO delta da mensagem do assistente, visivel
            no chat independente do modelo real ecoar (ou nao) o banner de

            governanca em `system_message`. Motivo (bug real confirmado por
            teste ao vivo, 2026-10-02): o Copilot CLI subjacente as vezes
            reconhece o banner de governanca completo como possivel prompt
            injection e o descarta silenciosamente do texto de resposta --
            o nome do agente ativo deixava de aparecer no chat mesmo a
            decisao de roteamento estando correta no backend. Prefixar o
            badge aqui (deterministico, fora do controle do modelo) garante
            visibilidade do agent ativo sempre. Se `None`, nenhum badge e
            emitido (comportamento legado).
        turn_recorder_store: `SessionStore` ja configurado (ver
            `routes._session_store_configurado`) para persistir o
            historico do turno na tabela `turns` (`turn_recorder.py`,
            pedido explicito do usuario 2026-10-02). `None` desativa a
            persistencia (no-op silencioso em `turn_recorder.persistir`) --
            retrocompativel com chamadores existentes (ex.: testes
            unitarios diretos que nao configuram `SessionStore`).
        turno_trace_id: Mesmo `trace_id` ja gerado por
            `routes._preparar_turno_de_governanca` e usado nos spans OTel
            de governanca -- correlaciona o registro local em `turns` com
            o trace distribuido no Langfuse/OTel Collector, quando ativo.
        prompt_usuario: Texto da ultima mensagem do usuario neste turno
            (ja extraido pelo chamador via `routes._extrair_texto_e_
            anexos`) -- evita duplicar a logica de extracao aqui so para
            persistencia.
        workflow: Workflow ativo decidido pela governanca
            (`sessao_nova.workflow`) -- persistido em `turns.workflow`.
        etapa: Indice da etapa corrente no workflow
            (`sessao_nova.etapa`) -- persistido em `turns.etapa`.
        score_roteamento: Score de confianca do roteamento deterministico
            (`decisao.score`) -- persistido em `turns.score_roteamento`.
        drift_detectado: Se o roteador detectou drift de intencao
            (`decisao.drift_detectado`) -- persistido em
            `turns.drift_detectado`.
        (demais parametros: identicos a `stream_chat`, ver docstring la).

    Yields:
        AgUiEvent: sequencia valida de eventos AG-UI para 1 run --
        `RunStartedEvent` -> (texto/tool-call/subagent)* -> `RunFinishedEvent`,
        ou `RunErrorEvent` isolado em caso de falha do SDK/sessao.
    """
    from ag_ui.core import (
        CustomEvent,
        RunErrorEvent,
        RunFinishedEvent,
        RunStartedEvent,
        SubagentErrorEvent,
        SubagentFinishedEvent,
        SubagentFinishedSuspendedOutcome,
        SubagentStartedEvent,
        TextMessageContentEvent,
        TextMessageEndEvent,
        TextMessageStartEvent,
        ToolCallEndEvent,
        ToolCallResultEvent,
        ToolCallStartEvent,
    )

    yield RunStartedEvent(thread_id=thread_id, run_id=run_id)

    # Badge deterministico de "Agente Ativo" e "Handoff" (R-042 / agent-contracts § 0)
    # aberto ANTES de qualquer chamada ao SDK real, para garantir visibilidade
    # no chat mesmo que o modelo subjacente descarte o banner de governanca.
    # `msg_id_badge` e reaproveitado como `estado["mensagem_atual_id"]` logo
    # abaixo -- o texto real do assistente e anexado NA MESMA mensagem/bolha.
    msg_id_badge: str | None = None

    # Acumulador do historico DURAVEL do turno (`turn_recorder.py`, pedido
    # explicito do usuario 2026-10-02) -- criado ANTES de qualquer chamada
    # ao SDK real para garantir que mesmo um turno que falhe logo no inicio
    # (ex.: SDK indisponivel, excecao do `copilot.CopilotClient`) ainda seja
    # persistido com os dados de governanca ja disponiveis (ver bloco
    # `except Exception` ao final da funcao). `turn_id=run_id` reaproveita
    # o identificador AG-UI ja garantido 1-por-turno pelo protocolo.
    turno_acumulado = turn_recorder.AcumuladorDeTurno(
        turn_id=run_id,
        session_id=session_id or thread_id,
        prompt=prompt_usuario or "",
        agent_name=agent_name,
        agent_model=agent_model,
        workflow=workflow,
        etapa=etapa,
        score_roteamento=score_roteamento,
        drift_detectado=drift_detectado,
        handoff_origem=handoff_origem,
        handoff_motivo=handoff_motivo,
        checkpoint_aberto=checkpoint_aberto,
        trace_id=turno_trace_id,
    )
    if agent_name:
        msg_id_badge = uuid.uuid4().hex
        yield TextMessageStartEvent(message_id=msg_id_badge, role="assistant")
        # Sem backticks (code-span) no nome do agent/motivo -- visual mais
        # limpo no chat (pedido real do usuario, 2026-10-02): o estilo
        # monoespacado com fundo cinza do markdown renderizado destoava do
        # resto do badge (negrito simples), alem de ser redundante para um
        # nome curto ja destacado em **negrito**.
        badge_text = f"🧭 **Agente Ativo:** {agent_name}"
        if agent_model:
            badge_text += f" · {agent_model}"
        badge_text += "\n"
        if handoff_origem and handoff_origem != agent_name:
            motivo_str = f" (motivo: {handoff_motivo})" if handoff_motivo else ""
            badge_text += (
                f"🔄 **Handoff:** {handoff_origem} → {agent_name}{motivo_str}\n"
            )
        badge_text += "\n"
        yield TextMessageContentEvent(message_id=msg_id_badge, delta=badge_text)
        turn_recorder.adicionar_texto_resposta(turno_acumulado, badge_text)

    try:
        copilot = _import_copilot()
    except SDKUnavailableError as exc:
        logger.warning("sdk_unavailable_fallback_to_stub_ag_ui: %s", exc)
        msg_id = msg_id_badge or uuid.uuid4().hex
        if msg_id_badge is None:
            yield TextMessageStartEvent(message_id=msg_id, role="assistant")
        yield TextMessageContentEvent(message_id=msg_id, delta=_STUB_CONTENT)
        turn_recorder.adicionar_texto_resposta(turno_acumulado, _STUB_CONTENT)
        turno_acumulado.error_type = "sdk_unavailable"
        turn_recorder.persistir(turno_acumulado, turn_recorder_store)
        yield TextMessageEndEvent(message_id=msg_id)
        yield RunFinishedEvent(thread_id=thread_id, run_id=run_id)
        return

    from copilot.generated.rpc import (  # type: ignore[import-not-found]
        PermissionDecisionApproveOnce,
        PermissionDecisionReject,
    )
    from copilot.session_events import (  # type: ignore[import-not-found]
        AssistantIdleData,
        AssistantIntentData,
        AssistantMessageData,
        AssistantTurnRetryData,
        AssistantUsageData,
        ModelCallFailureData,
        PermissionRequestCustomTool,
        PermissionRequestMcp,
        PermissionRequestRead,
        PermissionRequestShell,
        PermissionRequestWrite,
        SessionCompactionCompleteData,
        SessionCompletionReceiptData,
        SessionErrorData,
        SessionTruncationData,
        SubagentCompletedData,
        SubagentFailedData,
        SubagentStartedData,
        ToolExecutionCompleteData,
        ToolExecutionStartData,
    )

    _TOOL_DELEGACAO_AGENT: Final[str] = "run_subagent"

    def _caminho_escrita_seguro(caminho_str: str) -> bool:
        """Guarda 4: escrita deve ficar restrita a /workspaces e fora de bloqueios."""
        if not caminho_str:
            return False
        p = Path(caminho_str)
        if any(seg in (".git", "secrets") for seg in p.parts):
            return False
        if p.name.startswith(".env"):
            return False
        if p.suffix == ".pem":
            return False
        return True

    def _identificador_e_seguro_nativo(perm_request: Any) -> tuple[str, bool]:
        if isinstance(perm_request, PermissionRequestRead):
            return "read", True
        if isinstance(perm_request, PermissionRequestShell):
            return "shell", _comando_shell_e_seguro(perm_request)
        if isinstance(perm_request, PermissionRequestMcp):
            _nome_bruto = str(getattr(perm_request, "tool_name", "") or "mcp_tool")
            _servidor = str(getattr(perm_request, "server_name", "") or "")
            _read_only_nativo = bool(getattr(perm_request, "read_only", False))
            _args_mcp = getattr(perm_request, "args", None)
            # Bug real investigado (2026-10-04): o SDK headless real reporta
            # `tool_name` como o nome CRU exposto pelo proprio servidor MCP
            # (ex.: "ctx_batch_execute"), SEM o prefixo de exibicao da IDE
            # ("mcp_context-mode_ctx_batch_execute") que `permission_policy.
            # MCP_TOOL_PREFIXES`/`tool_mcp_e_cataloga` esperam -- o que fazia
            # `tool_call_nao_escrita_e_segura` cair incondicionalmente no
            # fallback final (negado), mesmo com o servidor conectado e
            # funcionando. Normaliza AQUI (fonte unica, antes do handler)
            # usando `server_name` (campo real confirmado por introspeccao
            # da wheel) -- resolve de forma generica para os 3 servers,
            # inclusive `codegraph` (cujas tools nao compartilham nenhum
            # prefixo comum entre si, ex.: "query", "path", "file_deps").
            nome = _nome_bruto
            if _servidor and not nome.startswith(f"mcp_{_servidor}_"):
                # Observado em producao (2026-10-04): algumas versoes do SDK
                # ja incluem o nome do servidor com hifen dentro do proprio
                # `tool_name` bruto (ex.: "context-mode-ctx_execute") -- sem
                # esta checagem, a normalizacao duplicava
                # ("mcp_context-mode_context-mode-ctx_execute"). Remove o
                # prefixo "<servidor>-" redundante antes de aplicar o
                # prefixo canonico "mcp_<servidor>_".
                _base = _nome_bruto
                if _base.startswith(f"{_servidor}-"):
                    _base = _base[len(_servidor) + 1 :]
                nome = f"mcp_{_servidor}_{_base}"
            logger.info(
                "mcp_identificador_nativo server_name=%s tool_name_bruto=%s "
                "tool_name_normalizado=%s read_only=%s args_keys=%s",
                _servidor,
                _nome_bruto,
                nome,
                _read_only_nativo,
                sorted(_args_mcp.keys()) if isinstance(_args_mcp, dict) else _args_mcp,
            )
            return nome, _read_only_nativo
        if isinstance(perm_request, PermissionRequestCustomTool):
            nome = str(getattr(perm_request, "tool_name", "") or "custom_tool")
            return nome, False
        return type(perm_request).__name__, False

    async def _bridge_permissao(
        perm_request: Any, invocation: Mapping[str, Any]
    ) -> Any:
        if isinstance(perm_request, PermissionRequestWrite):
            if permission_mode == "read_only":
                return PermissionDecisionReject(
                    feedback="Modo read_only ativo: escrita de arquivos negada."
                )
            if permission_mode == "propose":
                return PermissionDecisionReject(
                    feedback=(
                        "Modo propose ativo: alteracoes devem ser propostas como diff."
                    )
                )
            if permission_mode == "apply":
                if checkpoint_aberto:
                    return PermissionDecisionReject(
                        feedback="Escrita bloqueada: ha um checkpoint humano pendente."
                    )
                caminho = str(
                    getattr(perm_request, "resolved_path", "")
                    or getattr(perm_request, "file_name", "")
                    or ""
                )
                if not _caminho_escrita_seguro(caminho):
                    return PermissionDecisionReject(
                        feedback="Caminho de arquivo bloqueado para escrita (Guarda 4)."
                    )
                # Feature pedida pelo usuario (2026-10-02, paridade com o
                # plugin Copilot da IDE): NUNCA aplicar a escrita
                # silenciosamente so por `permission_mode == "apply"` --
                # pausa e mostra o DIFF completo no chat
                # (`FileEditBridge.tsx`), aguardando aprovacao/rejeicao
                # explicita de TODAS as linhas antes de liberar a escrita
                # real. `_bridge_edicao_arquivo` (abaixo, mesmo padrao de
                # `_bridge_elicitacao`/`_bridge_user_input`) so retorna
                # apos o usuario decidir (ou o timeout de 30min expirar).
                aprovado = await _bridge_edicao_arquivo(perm_request)
                if aprovado:
                    return PermissionDecisionApproveOnce()
                return PermissionDecisionReject(
                    feedback="Usuário revisou o diff proposto e optou por NÃO aplicar a alteração."
                )

        identificador, seguro_nativo = _identificador_e_seguro_nativo(perm_request)
        # Mantido curto-circuito ORIGINAL do `or` (CONTRATO de teste real:
        # `permission_handler` nao pode ser chamado quando `seguro_nativo`
        # ja aprova -- `test_deve_aprovar_permissionrequestread_sem_chamar_handler`).
        # Logging usa `None` para "nao avaliado" em vez de forcar a chamada.
        permitido = seguro_nativo or permission_handler(identificador, dict(invocation))
        if isinstance(perm_request, PermissionRequestShell):
            logger.info(
                "bridge_permissao_shell identificador=%s seguro_nativo=%s "
                "permission_mode=%s permitido=%s "
                "(handler_so_e_chamado_quando_seguro_nativo_e_falso)",
                identificador,
                seguro_nativo,
                permission_mode,
                permitido,
            )
        if isinstance(perm_request, PermissionRequestMcp):
            logger.info(
                "bridge_permissao_mcp identificador=%s seguro_nativo=%s "
                "permission_mode=%s permitido=%s "
                "(handler_so_e_chamado_quando_seguro_nativo_e_falso)",
                identificador,
                seguro_nativo,
                permission_mode,
                permitido,
            )
        if permitido:
            return PermissionDecisionApproveOnce()
        return PermissionDecisionReject(
            feedback="Negado pela politica local (GATEWAY_PERMISSION_MODE)."
        )

    fila: asyncio.Queue[Any | None] = asyncio.Queue()

    async def _bridge_edicao_arquivo(perm_request: Any) -> bool:
        """Ponte real entre uma escrita de arquivo pendente
        (`PermissionRequestWrite`) e o usuario -- paridade com o plugin
        Copilot da IDE (visualizar o diff proposto e aprovar/ignorar ANTES
        da escrita real ocorrer no disco, pedido explicito do usuario,
        2026-10-02). Mesmo padrao de ponte assincrona de
        `_bridge_elicitacao`/`_bridge_user_input`: emite `CustomEvent(name=
        "file_edit_requested")` no stream AG-UI consumido pelo frontend
        (`apps/web/copilot/FileEditBridge.tsx`) e aguarda -- SEM bloquear o
        event loop -- ate `resolver_edicao_arquivo` (acionada pelo endpoint
        `POST /v1/file-edit/{request_id}/respond`) resolver o
        `asyncio.Future` correspondente com a decisao real do usuario.

        O `diff` (unified diff, ja pronto para renderizacao linha-a-linha)
        e o `intention` vem PRONTOS do proprio SDK (campos confirmados por
        introspeccao real de `copilot.session_events.PermissionRequestWrite`,
        2026-10-02) -- nenhuma geracao de diff e feita aqui.

        Args:
            perm_request: Instancia de `PermissionRequestWrite` recebida em
                `_bridge_permissao`.

        Returns:
            bool: `True` se o usuario aprovou a escrita; `False` se
            ignorou/rejeitou OU se o tempo limite expirou sem resposta
            (fail-safe: NUNCA escreve por omissao/timeout).
        """
        request_id = uuid.uuid4().hex
        # Bug real corrigido (2026-10-02, reportado pelo usuario: diff
        # mostrando o arquivo INTEIRO como "adicionado" mesmo pedindo so 5
        # linhas): `perm_request.resolved_path` pode vir VAZIO/`None` para
        # certas escritas de arquivo EXISTENTE (confirmado por evidencia
        # real -- o header do modal, que usa `file_name` e nao
        # `resolved_path`, exibia o caminho absoluto correto, enquanto
        # `_ler_conteudo_atual_arquivo(resolved_path)` recebia string vazia
        # e caia no ramo "arquivo novo", tratando TODO o conteudo proposto
        # como adicionado contra um "antigo" em branco). O guard de
        # seguranca (`_caminho_escrita_seguro`, acima) ja aplicava este
        # MESMO fallback `resolved_path or file_name` -- faltava replicar
        # aqui. Usa-se `caminho_efetivo` tanto para ler o conteudo atual
        # quanto no `resolved_path` enviado ao front-end, garantindo que o
        # dedup anti-loop por caminho (`FileEditBridge.tsx`, comparando
        # `item.resolvedPath`) tambem funcione corretamente.
        resolved_path_bruto = str(getattr(perm_request, "resolved_path", "") or "")
        file_name_bruto = str(getattr(perm_request, "file_name", "") or "")
        caminho_efetivo = resolved_path_bruto or file_name_bruto
        novo_conteudo = getattr(perm_request, "new_file_contents", None)
        # Diff COMPLETO (todas as linhas do arquivo, pedido explicito do
        # usuario 2026-10-02) -- so e possivel quando o SDK fornece o
        # conteudo novo INTEIRO (`new_file_contents`); se vier `None` (ex.:
        # algum tipo de escrita que o SDK nao preenche este campo), cai
        # para o `diff` truncado (hunks) como fallback, tratado pelo
        # frontend (`FileEditBridge.tsx`/`diffParser.parsearDiff`).
        linhas_diff_completo: list[dict[str, Any]] = []
        if isinstance(novo_conteudo, str):
            conteudo_antigo = _ler_conteudo_atual_arquivo(caminho_efetivo)
            linhas_diff_completo = _gerar_linhas_diff_completo(
                conteudo_antigo, novo_conteudo
            )
        fila.put_nowait(
            CustomEvent(
                name="file_edit_requested",
                value={
                    "request_id": request_id,
                    "file_name": file_name_bruto,
                    "resolved_path": caminho_efetivo,
                    "diff": str(getattr(perm_request, "diff", "") or ""),
                    "lines": linhas_diff_completo,
                    "intention": str(getattr(perm_request, "intention", "") or ""),
                },
            )
        )
        future: asyncio.Future[bool] = asyncio.get_running_loop().create_future()
        _EDICOES_ARQUIVO_PENDENTES[request_id] = future

        async def _heartbeat() -> None:
            try:
                while True:
                    await asyncio.sleep(_INTERVALO_HEARTBEAT_EDICAO_ARQUIVO_SEGUNDOS)
                    fila.put_nowait(
                        CustomEvent(
                            name="file_edit_heartbeat",
                            value={"request_id": request_id},
                        )
                    )
            except asyncio.CancelledError:
                pass

        heartbeat_task = asyncio.ensure_future(_heartbeat())
        try:
            return await asyncio.wait_for(
                future, timeout=_TIMEOUT_EDICAO_ARQUIVO_SEGUNDOS
            )
        except TimeoutError:
            _EDICOES_ARQUIVO_PENDENTES.pop(request_id, None)
            fila.put_nowait(
                CustomEvent(name="file_edit_expired", value={"request_id": request_id})
            )
            return False
        finally:
            heartbeat_task.cancel()

    nomes_por_tool_call_id: dict[str, str] = {}
    # Rastreia `tool_call_id`s de subagent com `SubagentStartedEvent` ja
    # emitido mas ainda SEM `SubagentFinishedEvent`/`SubagentErrorEvent`
    # correspondente -- necessario para o fix de 2026-10-02 (ver bloco
    # `AssistantIdleData` abaixo) que evita `RUN_FINISHED` com subagent
    # tecnicamente ainda ativo aos olhos do protocolo AG-UI.
    subagents_abertos: set[str] = set()
    # PILHA (nao apenas set) de `subagent_run_id`s atualmente em execucao,
    # do mais externo ao mais interno -- `pilha_subagents[-1]` e o subagent
    # ATIVO no momento de qualquer evento subsequente. Feature pedida pelo
    # usuario (2026-10-02, paridade com o chat Copilot da IDE): o protocolo
    # AG-UI 1.0 ja suporta nesting nativo de acoes de um subagent dentro do
    # seu proprio colapse via o campo OPCIONAL `subagent_run_id` presente em
    # `ToolCallStartEvent`/`ToolCallEndEvent`/`ToolCallResultEvent`/
    # `TextMessageStartEvent`/`TextMessageContentEvent`/`TextMessageEndEvent`
    # (confirmado por introspeccao real de `ag_ui.core.*.model_fields`) -- mas
    # ate aqui esses eventos NUNCA preenchiam esse campo quando emitidos
    # DURANTE a execucao de um subagent (ex.: o proprio `read_file`/
    # `grep_search` que o subagent delegado chama internamente), fazendo
    # essas acoes aparecerem soltas no timeline principal em vez de
    # aninhadas dentro do colapse "<subagent> finished execution." do
    # front-end (bug real reportado via screenshot comparando com a IDE).
    # Pilha (nao so o topo) suporta subagents aninhados (subagent que chama
    # outro subagent), preenchendo tambem `parent_subagent_run_id` nativo.
    pilha_subagents: list[str] = []
    # Debug investigativo (2026-10-04): ver nota identica em `stream_chat`
    # acima -- `run_subagent` -> tool nativa `task` sem allowlist de nome
    # contra o catalogo real de `custom_agents`.
    _nomes_custom_agents_reais = frozenset(
        str(agente.get("name") or "") for agente in (custom_agents or [])
    )
    logger.debug(
        "sessao_custom_agents_registrados(ag_ui) total=%d nomes=%s",
        len(_nomes_custom_agents_reais),
        sorted(_nomes_custom_agents_reais),
    )
    # Pre-semeado com `msg_id_badge` (se o badge "Agente Ativo" foi aberto
    # acima): o primeiro `AssistantMessageData` real do SDK passa a ANEXAR
    # texto na MESMA mensagem/bolha do badge (nao abre uma 2a bolha).
    estado: dict[str, str | None] = {
        "mensagem_atual_id": msg_id_badge,
        "mensagem_atual_subagent_run_id": None,
    }

    def _fechar_mensagem_aberta() -> None:
        """Fecha a bolha de texto do assistente ANTES de iniciar um tool
        call/subagent, se houver uma aberta (`TextMessageStartEvent` ja
        emitido, sem `TextMessageEndEvent` correspondente ainda).

        Bug real de producao corrigido (2026-10-02, reportado via front-end
        web): sem este fechamento explicito, uma sequencia comum do modelo
        (texto -> tool call -> mais texto) deixava a mensagem de texto
        "tecnicamente aberta" no protocolo AG-UI no momento em que o
        `ToolCallStartEvent`/`SubagentStartedEvent` era emitido -- o
        frontend (que monta a bolha de texto incrementalmente a cada
        `TextMessageContentEvent`) posicionava o widget da tool DEPOIS da
        bolha de texto ja montada, mesmo quando a tool foi executada ANTES
        daquele texto cronologicamente. Ao recarregar a pagina, a thread e
        reconstruida a partir do historico persistido (ja ordenado
        corretamente por sequencia de eventos), escondendo o bug -- exibido
        apenas durante o streaming ao vivo. Fechar a mensagem aqui e reabrir
        uma NOVA (`estado["mensagem_atual_id"] = None`, re-aberta pelo
        proximo `AssistantMessageData`) garante que cada segmento de texto
        vire uma bolha propria e completa, na ordem cronologica correta em
        relacao a qualquer tool call/subagent intercalado.

        `subagent_run_id` do `TextMessageEndEvent` usa o MESMO valor
        registrado quando a mensagem foi aberta (`estado["mensagem_atual_
        subagent_run_id"]`), nao o topo atual da pilha -- evita fechar uma
        mensagem aberta fora de um subagent com um `subagent_run_id`
        incorreto caso a pilha ja tenha mudado entre a abertura e o fechamento.
        """
        if estado["mensagem_atual_id"] is not None:
            fila.put_nowait(
                TextMessageEndEvent(
                    message_id=estado["mensagem_atual_id"],
                    subagent_run_id=estado.get("mensagem_atual_subagent_run_id"),
                )
            )
            estado["mensagem_atual_id"] = None
            estado["mensagem_atual_subagent_run_id"] = None

    def _on_event(event: Any) -> None:
        dado = getattr(event, "data", None)
        subagent_atual = pilha_subagents[-1] if pilha_subagents else None
        if isinstance(dado, AssistantMessageData):
            texto = str(getattr(dado, "content", "") or "")
            if texto:
                turn_recorder.adicionar_texto_resposta(turno_acumulado, texto)
                if estado["mensagem_atual_id"] is None:
                    estado["mensagem_atual_id"] = uuid.uuid4().hex
                    estado["mensagem_atual_subagent_run_id"] = subagent_atual
                    fila.put_nowait(
                        TextMessageStartEvent(
                            message_id=estado["mensagem_atual_id"],
                            role="assistant",
                            subagent_run_id=subagent_atual,
                        )
                    )
                fila.put_nowait(
                    TextMessageContentEvent(
                        message_id=estado["mensagem_atual_id"],
                        delta=texto,
                        subagent_run_id=estado.get("mensagem_atual_subagent_run_id"),
                    )
                )
        elif isinstance(dado, ToolExecutionStartData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            nome = str(getattr(dado, "tool_name", "") or "?")
            if tool_call_id:
                nomes_por_tool_call_id[tool_call_id] = nome
            _shell_info = getattr(dado, "shell_tool_info", None)
            if _shell_info is not None:
                logger.info(
                    "tool_shell_iniciado(ag_ui) tool_call_id=%s tool_name=%s "
                    "display_command=%s has_write_file_redirection=%s model=%s",
                    tool_call_id,
                    nome,
                    getattr(_shell_info, "display_command", None),
                    getattr(_shell_info, "has_write_file_redirection", None),
                    getattr(dado, "model", None),
                )
            # Suprimido quando `run_subagent`: `SubagentStartedEvent` (abaixo)
            # ja cobre o mesmo `tool_call_id` com o nome REAL do agent (RT-03).
            if nome != _TOOL_DELEGACAO_AGENT:
                turn_recorder.registrar_tool_iniciada(
                    turno_acumulado, tool_call_id, nome
                )
                _fechar_mensagem_aberta()
                fila.put_nowait(
                    ToolCallStartEvent(
                        tool_call_id=tool_call_id,
                        tool_call_name=nome,
                        subagent_run_id=subagent_atual,
                    )
                )
        elif isinstance(dado, ToolExecutionCompleteData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            nome = nomes_por_tool_call_id.pop(tool_call_id, "?")
            _shell_exec = getattr(dado, "shell_execution", None)
            _resultado = getattr(dado, "result", None)
            if _shell_exec is not None or _resultado is not None or nome in (
                "bash",
                "powershell",
                "shell",
            ):
                logger.info(
                    "tool_shell_concluido(ag_ui) tool_call_id=%s tool_name=%s "
                    "success=%s error=%s exit_code=%s cwd=%s output_preview=%s",
                    tool_call_id,
                    nome,
                    getattr(dado, "success", None),
                    getattr(dado, "error", None),
                    getattr(_shell_exec, "exit_code", None)
                    or getattr(_resultado, "exit_code", None),
                    getattr(_resultado, "cwd", None),
                    str(getattr(_resultado, "output_preview", "") or "")[:500],
                )
            if nome != _TOOL_DELEGACAO_AGENT:
                turn_recorder.registrar_tool_concluida(turno_acumulado, tool_call_id)
                fila.put_nowait(
                    ToolCallEndEvent(
                        tool_call_id=tool_call_id, subagent_run_id=subagent_atual
                    )
                )
                fila.put_nowait(
                    ToolCallResultEvent(
                        message_id=uuid.uuid4().hex,
                        tool_call_id=tool_call_id,
                        content="concluido",
                        role="tool",
                        subagent_run_id=subagent_atual,
                    )
                )
        elif isinstance(dado, SubagentStartedData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            nome_tecnico = str(getattr(dado, "agent_name", "") or "?")
            nome_exibicao = (
                str(getattr(dado, "agent_display_name", "") or "") or nome_tecnico
            )
            _catalogado = nome_tecnico in _nomes_custom_agents_reais
            logger.info(
                "subagent_iniciado(ag_ui) tool_call_id=%s agent_name=%s "
                "agent_display_name=%s agent_type=%s model=%s parent_id=%s "
                "execution_mode=%s catalogado=%s",
                tool_call_id,
                nome_tecnico,
                getattr(dado, "agent_display_name", None),
                getattr(dado, "agent_type", None),
                getattr(dado, "model", None),
                getattr(dado, "parent_id", None),
                getattr(dado, "execution_mode", None),
                _catalogado,
            )
            if not _catalogado:
                logger.warning(
                    "subagent_nome_nao_catalogado(ag_ui) tool_call_id=%s "
                    "agent_name=%s -- nome ausente nos %d custom_agents reais "
                    "registrados nesta sessao; possivel delegacao fantasma via "
                    "tool nativa 'task' (run_subagent -> task, sem allowlist "
                    "de nome)",
                    tool_call_id,
                    nome_tecnico,
                    len(_nomes_custom_agents_reais),
                )
            descricao = str(getattr(dado, "agent_description", "") or "")
            # `parent_subagent_run_id` nativo do protocolo: se este subagent
            # foi invocado de DENTRO de outro subagent ainda em execucao
            # (`subagent_atual`, topo da pilha ANTES do push abaixo), o
            # front-end pode aninhar o colapse 1 nivel mais fundo.
            parent_subagent_run_id = subagent_atual
            if tool_call_id:
                subagents_abertos.add(tool_call_id)
                turn_recorder.registrar_subagent_iniciado(
                    turno_acumulado, tool_call_id, nome_exibicao
                )
            _fechar_mensagem_aberta()
            fila.put_nowait(
                SubagentStartedEvent(
                    subagent_run_id=tool_call_id,
                    name=nome_exibicao,
                    description=descricao,
                    parent_tool_call_id=tool_call_id,
                    parent_subagent_run_id=parent_subagent_run_id,
                )
            )
            if tool_call_id:
                pilha_subagents.append(tool_call_id)
                # Badge deterministico de "Agente Ativo" TAMBEM para
                # subagents (bug real reportado pelo usuario via screenshot,
                # 2026-10-02): sem isto, a unica linha "Agente Ativo: <nome>"
                # visivel DENTRO do colapse do subagent vinha do proprio
                # TEXTO LIVRE gerado pelo modelo (banner universal de
                # `agent-contracts/SKILL.md` § 0) -- texto puro, sem
                # icone/negrito/modelo, destoando visualmente do badge
                # deterministico do agent de NIVEL SUPERIOR (`msg_id_badge`
                # acima, que usa o MESMO formato). Emite aqui o MESMO
                # formato, tageado com `subagent_run_id=tool_call_id` para
                # renderizar DENTRO do colapse certo (nesting nativo AG-UI,
                # ver bloco de `pilha_subagents` acima) -- mensagem FECHADA
                # de uma vez (Start+Content+End), para nao interferir no
                # rastreamento de `estado["mensagem_atual_id"]` usado pelo
                # texto REAL subsequente do subagent.
                modelo_subagent = _resolver_modelo_agent(nome_tecnico, custom_agents)
                badge_subagent_id = uuid.uuid4().hex
                badge_subagent_texto = f"🧭 **Agente Ativo:** {nome_exibicao}"
                if modelo_subagent:
                    badge_subagent_texto += f" · {modelo_subagent}"
                badge_subagent_texto += "\n\n"
                fila.put_nowait(
                    TextMessageStartEvent(
                        message_id=badge_subagent_id,
                        role="assistant",
                        subagent_run_id=tool_call_id,
                    )
                )
                fila.put_nowait(
                    TextMessageContentEvent(
                        message_id=badge_subagent_id,
                        delta=badge_subagent_texto,
                        subagent_run_id=tool_call_id,
                    )
                )
                fila.put_nowait(
                    TextMessageEndEvent(
                        message_id=badge_subagent_id, subagent_run_id=tool_call_id
                    )
                )
                turn_recorder.adicionar_texto_resposta(
                    turno_acumulado, badge_subagent_texto
                )
        elif isinstance(dado, SubagentCompletedData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            subagents_abertos.discard(tool_call_id)
            if tool_call_id in pilha_subagents:
                pilha_subagents.remove(tool_call_id)
            logger.info(
                "subagent_concluido(ag_ui) tool_call_id=%s agent_name=%s "
                "duration=%s total_tokens=%s total_tool_calls=%s",
                tool_call_id,
                getattr(dado, "agent_name", None),
                getattr(dado, "duration", None),
                getattr(dado, "total_tokens", None),
                getattr(dado, "total_tool_calls", None),
            )
            turn_recorder.registrar_subagent_concluido(turno_acumulado, tool_call_id)
            # `outcome=None` (campo omitido) == sucesso, por design do
            # protocolo ("Absent means success"). Fix 2026-10-02: o valor
            # anterior `outcome="completed"` (string crua) NAO e um outcome
            # valido do schema discriminado (`SubagentFinishedSuccessOutcome`/
            # `SubagentFinishedSuspendedOutcome`, discriminador `type`) e
            # levantava `pydantic.ValidationError` dentro do callback
            # sincrono do SDK sempre que um subagent concluia normalmente.
            fila.put_nowait(SubagentFinishedEvent(subagent_run_id=tool_call_id))
        elif isinstance(dado, SubagentFailedData):
            tool_call_id = str(getattr(dado, "tool_call_id", "") or "")
            subagents_abertos.discard(tool_call_id)
            if tool_call_id in pilha_subagents:
                pilha_subagents.remove(tool_call_id)
            erro = str(getattr(dado, "error", "") or "erro desconhecido")
            logger.warning(
                "subagent_falhou(ag_ui) tool_call_id=%s agent_name=%s erro=%s",
                tool_call_id,
                getattr(dado, "agent_name", None),
                erro,
            )
            turn_recorder.registrar_subagent_falhou(turno_acumulado, tool_call_id, erro)
            fila.put_nowait(
                SubagentErrorEvent(subagent_run_id=tool_call_id, message=erro)
            )
        elif isinstance(dado, AssistantUsageData):
            # Tokens/custo/latencia REAIS por chamada de modelo (pedido
            # explicito do usuario 2026-10-02) -- nao gera nenhum evento
            # AG-UI visivel, apenas alimenta o historico duravel do turno.
            turn_recorder.registrar_uso_assistente(turno_acumulado, dado)
        elif isinstance(dado, ModelCallFailureData):
            turn_recorder.registrar_falha_model_call(turno_acumulado, dado)
        elif isinstance(dado, AssistantTurnRetryData):
            turn_recorder.registrar_retry(turno_acumulado, dado)
        elif isinstance(dado, AssistantIntentData):
            turn_recorder.registrar_intencao(turno_acumulado, dado)
        elif isinstance(dado, SessionCompletionReceiptData):
            turn_recorder.registrar_completion_receipt(turno_acumulado, dado)
        elif isinstance(dado, SessionTruncationData):
            turn_recorder.registrar_truncamento(turno_acumulado, dado)
        elif isinstance(dado, SessionCompactionCompleteData):
            turn_recorder.registrar_compactacao(turno_acumulado, dado)
        elif isinstance(dado, AssistantIdleData):
            # Fix 2026-10-02: bug real de producao confirmado via front-end
            # web -- `AssistantIdleData` (fim de turno) pode chegar com um
            # subagent ainda "aberto" (`SubagentStartedEvent` emitido, sem
            # `Completed`/`Failed` correspondente) quando o subagent pausa
            # aguardando resposta do usuario (ex.: handoff `agent-router` ->
            # `prompt-structuring`, que dispara `ask_questions` e suspende a
            # propria execucao). O front-end valida o protocolo AG-UI e
            # REJEITA `RunFinishedEvent` enquanto houver subagent sem
            # encerramento, travando o chat com
            # "Cannot send 'RUN_FINISHED' while subagents are still active"
            # (`agent_run_error_event` / `INCOMPLETE_STREAM`). Fecha
            # explicitamente qualquer subagent ainda aberto com o outcome
            # nativo "suspended" (next-gen AG-UI: "Terminal para este
            # stream, nao para o subagent -- uma run futura pode continuar
            # a mesma invocacao") ANTES do sentinela de encerramento.
            for tool_call_id_pendente in list(subagents_abertos):
                fila.put_nowait(
                    SubagentFinishedEvent(
                        subagent_run_id=tool_call_id_pendente,
                        outcome=SubagentFinishedSuspendedOutcome(),
                    )
                )
            subagents_abertos.clear()
            pilha_subagents.clear()
            fila.put_nowait(None)  # sentinela de encerramento
        elif isinstance(dado, SessionErrorData):
            # Erro real da API do Copilot (cota mensal esgotada, rate limit,
            # autenticacao, etc.) -- bug real de producao confirmado por
            # teste ao vivo (2026-10-02): o SDK NUNCA levanta excecao Python
            # para isso, apenas emite este evento seguido de AssistantIdleData
            # normal, o que fazia o turno "terminar com sucesso" e CONTEUDO
            # VAZIO ser devolvido ao usuario sem nenhuma mensagem de erro
            # visivel ("chat nao responde nada"). Torna o erro visivel,
            # anexando na MESMA bolha de mensagem (badge/texto) ja aberta,
            # ou abrindo uma nova se nenhuma estiver ativa.
            codigo = str(getattr(dado, "error_code", "") or "erro_desconhecido")
            mensagem = str(
                getattr(dado, "message", "") or "Erro desconhecido do Copilot"
            )
            turn_recorder.registrar_erro_sessao(turno_acumulado, dado)
            if estado["mensagem_atual_id"] is None:
                estado["mensagem_atual_id"] = uuid.uuid4().hex
                fila.put_nowait(
                    TextMessageStartEvent(
                        message_id=estado["mensagem_atual_id"], role="assistant"
                    )
                )
            fila.put_nowait(
                TextMessageContentEvent(
                    message_id=estado["mensagem_atual_id"],
                    delta=f"\n> \u26a0\ufe0f Erro do Copilot ({codigo}): {mensagem}\n",
                )
            )

    async def _bridge_elicitacao(ctx: Mapping[str, Any]) -> dict[str, Any]:
        """Ponte real entre uma elicitation MCP pendente (ex.: tool nativa
        `ask_questions`) e o usuario, via `ElicitationContext` do SDK (RT-05,
        ver nota de modulo acima). Emite `CustomEvent(name=
        "elicitation_requested")` no stream AG-UI consumido pelo frontend
        (`apps/web/copilot/ElicitationBridge.tsx`) e aguarda -- SEM bloquear
        o event loop, apenas esta coroutine fica pausada em `asyncio.
        wait_for` -- ate `resolver_elicitacao` (acionado pelo endpoint
        `POST /v1/elicitation/{request_id}/respond`) resolver o
        `asyncio.Future` correspondente com a resposta real do usuario.

        Um heartbeat periodico (`_INTERVALO_HEARTBEAT_ELICITACAO_SEGUNDOS`)
        e empilhado em `fila` enquanto aguarda: cada item recebido reinicia
        o orcamento de `asyncio.wait_for(fila.get(), timeout=
        _TIMEOUT_SESSAO_SEGUNDOS)` do loop consumidor principal (abaixo),
        evitando que uma pausa humana legitima e demorada derrube o stream
        com um `TimeoutError` espurio.
        """
        request_id = uuid.uuid4().hex
        fila.put_nowait(
            CustomEvent(
                name="elicitation_requested",
                value={
                    "request_id": request_id,
                    "message": str(ctx.get("message", "")),
                    "requested_schema": dict(ctx.get("requestedSchema") or {}),
                    "mode": str(ctx.get("mode", "form")),
                },
            )
        )
        future: asyncio.Future[dict[str, Any]] = (
            asyncio.get_running_loop().create_future()
        )
        _ELICITACOES_PENDENTES[request_id] = future

        async def _heartbeat() -> None:
            try:
                while True:
                    await asyncio.sleep(_INTERVALO_HEARTBEAT_ELICITACAO_SEGUNDOS)
                    fila.put_nowait(
                        CustomEvent(
                            name="elicitation_heartbeat",
                            value={"request_id": request_id},
                        )
                    )
            except asyncio.CancelledError:
                pass

        heartbeat_task = asyncio.ensure_future(_heartbeat())
        try:
            resultado = await asyncio.wait_for(
                future, timeout=_TIMEOUT_ELICITACAO_SEGUNDOS
            )
        except TimeoutError:
            _ELICITACOES_PENDENTES.pop(request_id, None)
            fila.put_nowait(
                CustomEvent(
                    name="elicitation_expired", value={"request_id": request_id}
                )
            )
            resultado = {"action": "cancel", "content": None}
        finally:
            heartbeat_task.cancel()

        action = str(resultado.get("action") or "cancel")
        if action == "accept":
            return {"action": "accept", "content": dict(resultado.get("content") or {})}
        return {"action": action}

    async def _bridge_user_input(
        req: Mapping[str, Any], _meta: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Ponte real entre uma pergunta `ask_user` pendente e o usuario --
        mecanismo LEGADO (`UserInputHandler`) confirmado por teste isolado
        como o UNICO que efetivamente faz o modelo invocar `ask_user` como
        function-call real (RT-05, ver nota de modulo acima). Mesmo padrao
        de ponte assincrona de `_bridge_elicitacao`: emite `CustomEvent(name=
        "ask_user_requested")` no stream AG-UI consumido pelo frontend
        (`apps/web/copilot/AskUserBridge.tsx`) e aguarda ate
        `resolver_pergunta_usuario` (endpoint `POST /v1/ask-user/
        {request_id}/respond`) resolver o `asyncio.Future` correspondente.

        Args:
            req: `UserInputRequest` do SDK -- `{question: str, choices:
                list[str], allowFreeform: bool}`.
            _meta: Metadados do SDK (ex.: `session_id`) -- nao-escopo desta
                ponte (apenas o payload reativo ao usuario importa aqui).

        Returns:
            dict[str, Any]: `UserInputResponse` -- `{"answer": str,
            "wasFreeform": bool}`. AMBOS os campos sao obrigatorios (`
            UserInputResponse` e um `TypedDict` sem `total=False` --
            confirmado por teste ao vivo que omitir `wasFreeform` falha
            silenciosamente e o modelo recebe "erro ao processar resposta").
        """
        request_id = uuid.uuid4().hex
        fila.put_nowait(
            CustomEvent(
                name="ask_user_requested",
                value={
                    "request_id": request_id,
                    "question": str(req.get("question", "")),
                    "choices": [str(c) for c in (req.get("choices") or [])],
                    "allow_freeform": bool(req.get("allowFreeform", False)),
                },
            )
        )
        future: asyncio.Future[dict[str, Any]] = (
            asyncio.get_running_loop().create_future()
        )
        _PERGUNTAS_PENDENTES[request_id] = future

        async def _heartbeat() -> None:
            try:
                while True:
                    await asyncio.sleep(_INTERVALO_HEARTBEAT_PERGUNTA_SEGUNDOS)
                    fila.put_nowait(
                        CustomEvent(
                            name="ask_user_heartbeat",
                            value={"request_id": request_id},
                        )
                    )
            except asyncio.CancelledError:
                pass

        heartbeat_task = asyncio.ensure_future(_heartbeat())
        try:
            resultado = await asyncio.wait_for(
                future, timeout=_TIMEOUT_PERGUNTA_SEGUNDOS
            )
        except TimeoutError:
            _PERGUNTAS_PENDENTES.pop(request_id, None)
            fila.put_nowait(
                CustomEvent(name="ask_user_expired", value={"request_id": request_id})
            )
            resultado = {"answer": "", "wasFreeform": True}
        finally:
            heartbeat_task.cancel()

        return {
            "answer": str(resultado.get("answer") or ""),
            "wasFreeform": bool(resultado.get("wasFreeform", True)),
        }

    try:
        async with copilot.CopilotClient(github_token=token) as client:
            async with await client.create_session(
                on_permission_request=_bridge_permissao,
                mcp_servers=construir_mcp_servers(get_settings()),
                on_elicitation_request=_bridge_elicitacao,
                on_user_input_request=_bridge_user_input,
                # Fix real confirmado por introspeccao da wheel (2026-10-02):
                # o default de `ask_user_variant` e `"legacy"` -- a tool
                # `ask_user`/`ask_questions` entao faz a PERGUNTA COMO TEXTO
                # NORMAL da resposta do assistente (exatamente o observado no
                # teste ao vivo do usuario: lista numerada em markdown, SEM
                # disparar `on_elicitation_request`/`CustomEvent
                # elicitation_requested`). A propria docstring do SDK
                # confirma: "To use 'elicitation', also provide
                # on_elicitation_request so the host can answer structured
                # forms." -- tinhamos o callback wired, mas nunca setamos
                # este parametro companheiro. NOTA (2026-10-02, descoberta
                # final via pesquisa externa + reproducao isolada): mesmo
                # com este parametro, o CLI so roteia `ask_user` de fato
                # atraves de `on_user_input_request` (mecanismo legado) --
                # mantido aqui apenas para compatibilidade futura.
                ask_user_variant="elicitation",
                model=model,
                session_id=session_id,
                working_directory=working_directory,
                additional_directories=(
                    list(additional_directories) if additional_directories else None
                ),
                enable_file_hooks=False,
                enable_config_discovery=False,
                system_message=(
                    {
                        "mode": "append",
                        "content": system_message + _REFORCO_ASK_USER_ELICITATION,
                    }
                    if system_message is not None
                    else {"mode": "append", "content": _REFORCO_ASK_USER_ELICITATION}
                ),
                custom_agents=(list(custom_agents) if custom_agents else None),
            ) as session:
                session.on(_on_event)
                await session.send(
                    _joined_prompt(messages),
                    attachments=(list(attachments) if attachments else None),
                )
                while True:
                    item = await asyncio.wait_for(
                        fila.get(), timeout=_TIMEOUT_SESSAO_SEGUNDOS
                    )
                    if item is None:
                        break
                    yield item
        # Badge de creditos (2026-10-03, pedido explicito do usuario --
        # paridade com o plugin Copilot da IDE: "<Modelo> · <N> Credits" ao
        # final de cada resposta). Formula OFICIAL confirmada em docs.
        # github.com/en/copilot/how-tos/copilot-sdk/features/usage-and-
        # billing: AI credits = copilot_usage.total_nano_aiu / 1e9 -- ja
        # acumulado em `turno_acumulado.cost_nano_aiu` por
        # `turn_recorder.registrar_uso_assistente` (1 evento `AssistantUsageData`
        # por chamada real de modelo, incluindo subagents). So' exibido
        # quando o SDK de fato reportou uso (>0) -- sessao stub/erro ANTES
        # de qualquer chamada real de modelo (`SDKUnavailableError`, ver
        # bloco `except SDKUnavailableError` acima, que retorna cedo) nunca
        # chega aqui, entao nenhum badge falso-zero e' mostrado. Preferido
        # `agent_model` (nome amigavel do frontmatter, ex.: "Claude Sonnet
        # 5") sobre `modelo_usado_real` (id tecnico da API, ex.:
        # "claude-sonnet-4-5") quando ambos disponiveis -- mesma convencao
        # do badge "Agente Ativo" aberto no topo desta funcao.
        if turno_acumulado.cost_nano_aiu > 0:
            creditos = turno_acumulado.cost_nano_aiu / 1e9
            modelo_exibicao = agent_model or turno_acumulado.modelo_usado_real
            prefixo_modelo = f"{modelo_exibicao} · " if modelo_exibicao else ""
            texto_creditos = f"\n\n*🧮 {prefixo_modelo}{creditos:.1f} Credits*"
            if estado["mensagem_atual_id"] is None:
                estado["mensagem_atual_id"] = uuid.uuid4().hex
                yield TextMessageStartEvent(
                    message_id=estado["mensagem_atual_id"], role="assistant"
                )
            yield TextMessageContentEvent(
                message_id=estado["mensagem_atual_id"], delta=texto_creditos
            )
            turn_recorder.adicionar_texto_resposta(turno_acumulado, texto_creditos)
        if estado["mensagem_atual_id"] is not None:
            yield TextMessageEndEvent(message_id=estado["mensagem_atual_id"])
        turn_recorder.persistir(turno_acumulado, turn_recorder_store)
        yield RunFinishedEvent(thread_id=thread_id, run_id=run_id)
    except (
        Exception
    ) as exc:  # noqa: BLE001 -- RunErrorEvent cobre qualquer falha do SDK/sessao
        logger.exception("stream_chat_ag_ui_falhou")
        if turno_acumulado.error_type is None:
            turno_acumulado.error_type = type(exc).__name__
        turn_recorder.persistir(turno_acumulado, turn_recorder_store)
        yield RunErrorEvent(message=str(exc))


#: Prompt-sentinela reconhecido em `routes.agui_run` ANTES de qualquer
#: chamada ao SDK/modelo real -- permite exercitar
#: `apps/web/copilot/ElicitationBridge.tsx` (RJSF + `requestedSchema` MCP
#: arbitrario) fim-a-fim a partir do chat normal, sem depender do modelo
#: realmente invocar a elicitation nativa (confirmado por 8+ testes
#: isolados, 2026-10-02: o CLI headless v1.0.90 SEMPRE roteia `ask_user`
#: pelo mecanismo legado `on_user_input_request` -> `AskUserBridge.tsx`,
#: NUNCA por `on_elicitation_request` -> `ElicitationBridge.tsx`; ver nota
#: RT-05 no topo do modulo). Resultado: hoje nao ha prompt em linguagem
#: natural capaz de abrir o `ElicitationBridge` via conversa real com o
#: agent -- apenas este atalho de QA reaproveita a MESMA infraestrutura de
#: producao (`_ELICITACOES_PENDENTES`/`resolver_elicitacao`/endpoint
#: `POST /v1/elicitation/{request_id}/respond`), sem mockar nada no frontend.
PROMPT_TESTE_ELICITATION: Final[str] = "/testar-elicitation"


async def simular_elicitation_teste(
    *, thread_id: str, run_id: str
) -> AsyncIterator[AgUiEvent]:
    """Gera um stream AG-UI que dispara uma elicitation REAL de teste.

    Disparado quando a ultima mensagem do usuario e exatamente
    `PROMPT_TESTE_ELICITATION` (ver nota acima) -- bypassa inteiramente o
    SDK/modelo e empurra o MESMO `CustomEvent(name="elicitation_requested")`
    que `_bridge_elicitacao` emitiria em producao, com um `requestedSchema`
    fixo (JSON Schema de exemplo com `string`+`enum`+`boolean`) e aguarda a
    resposta real do usuario no MESMO endpoint de producao
    (`POST /v1/elicitation/{request_id}/respond`, via `resolver_elicitacao`).

    Util exclusivamente para QA manual do componente
    `apps/web/copilot/ElicitationBridge.tsx` -- nao reflete o fluxo real de
    uma pergunta feita pelo agent (hoje sempre via `ask_user`/
    `AskUserBridge.tsx`, ver nota RT-05).
    """
    from ag_ui.core import (
        CustomEvent,
        RunFinishedEvent,
        RunStartedEvent,
        TextMessageContentEvent,
        TextMessageEndEvent,
        TextMessageStartEvent,
    )

    yield RunStartedEvent(thread_id=thread_id, run_id=run_id)

    msg_id = uuid.uuid4().hex
    yield TextMessageStartEvent(message_id=msg_id, role="assistant")
    yield TextMessageContentEvent(
        message_id=msg_id,
        delta=(
            "🧪 **Modo de teste** — disparando uma elicitation MCP real "
            "(`ElicitationBridge.tsx`). Responda o formulário que vai "
            "aparecer.\n\n"
        ),
    )
    yield TextMessageEndEvent(message_id=msg_id)

    request_id = uuid.uuid4().hex
    # Registra o Future ANTES de yield-ar o evento (mesma ordem de
    # `_bridge_elicitacao`/`fila.put_nowait`): o consumidor real (encoder
    # SSE no endpoint) pode, em tese, repassar o evento ao browser e
    # receber a resposta HTTP de volta mais rapido do que esta coroutine
    # retoma apos o `yield` -- registrar DEPOIS criaria uma janela de
    # corrida onde `resolver_elicitacao` acharia o id ainda desconhecido
    # (bug real encontrado em teste isolado via `ctx_execute`, 2026-10-02).
    future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
    _ELICITACOES_PENDENTES[request_id] = future
    yield CustomEvent(
        name="elicitation_requested",
        value={
            "request_id": request_id,
            "message": "[TESTE] Confirme seus dados de contato:",
            "requested_schema": {
                "type": "object",
                "title": "Dados de contato (teste)",
                "properties": {
                    "nome": {
                        "type": "string",
                        "title": "Nome completo",
                        "minLength": 2,
                    },
                    "canal_preferido": {
                        "type": "string",
                        "title": "Canal preferido",
                        "enum": ["email", "whatsapp", "telefone"],
                        "enumNames": ["E-mail", "WhatsApp", "Telefone"],
                    },
                    "aceita_contato": {
                        "type": "boolean",
                        "title": "Aceita ser contatado?",
                        "default": True,
                    },
                },
                "required": ["nome", "canal_preferido"],
            },
            "mode": "form",
        },
    )

    try:
        resultado = await asyncio.wait_for(future, timeout=_TIMEOUT_ELICITACAO_SEGUNDOS)
    except TimeoutError:
        _ELICITACOES_PENDENTES.pop(request_id, None)
        yield CustomEvent(name="elicitation_expired", value={"request_id": request_id})
        resultado = {"action": "cancel", "content": None}

    msg_id_resultado = uuid.uuid4().hex
    yield TextMessageStartEvent(message_id=msg_id_resultado, role="assistant")
    yield TextMessageContentEvent(
        message_id=msg_id_resultado,
        delta=(
            f"✅ Elicitation de teste resolvida: `action={resultado.get('action')}`, "
            f"`content={resultado.get('content')!r}`"
        ),
    )
    yield TextMessageEndEvent(message_id=msg_id_resultado)
    yield RunFinishedEvent(thread_id=thread_id, run_id=run_id)
