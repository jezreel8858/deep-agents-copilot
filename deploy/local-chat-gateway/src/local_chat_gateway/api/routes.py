"""routes — `/healthz`, `/v1/models`, `/v1/chat/completions`.

Fase 3: integracao real (opcional) com o SDK do Copilot via
`sdk_session.stream_chat`, com fallback automatico para o stub
deterministico (Fase 1) quando o extra `[sdk]` nao esta instalado ou o
token nao esta configurado (`SDKUnavailableError`). Lobe Chat
envia `stream=true` por padrao -- ambos os caminhos (real e stub)
suportam streaming SSE.

Multi-projeto automatico: a cada request, `_diretorios_de_projetos_registrados`
traduz `projects.local.yaml` (via `projects_catalog.carregar_projetos`)
para os paths de container correspondentes e os repassa como
`additional_directories` ao SDK real -- nenhuma edicao de
`docker-compose.yml`/codigo e necessaria ao registrar um novo projeto
(desde que ele viva sob o mesmo `PROJECTS_ROOT_PATH`).
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from collections.abc import AsyncIterator, Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from local_chat_gateway import governance, governance_pipeline
from local_chat_gateway.api.schemas import (
    AgentCatalogItem,
    AgentCatalogResponse,
    ChatCompletion,
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatCompletionRequest,
    ChatMessage,
    CommandCatalogItem,
    CommandCatalogResponse,
    Model,
    ModelList,
    Usage,
    WorkspaceFileItem,
    WorkspaceFilesResponse,
)
from local_chat_gateway.auth import require_bearer_token
from local_chat_gateway.checkpoint_engine import parse_checkpoint_response
from local_chat_gateway.config import Settings, get_settings
from local_chat_gateway.permission_policy import (
    READ_ONLY_TOOL_PREFIXES,
    PermissionMode,
    PermissionPolicyStub,
    tool_call_nao_escrita_e_segura,
)
from local_chat_gateway.projects_catalog import carregar_projetos
from local_chat_gateway.sdk_session import (
    PROMPT_TESTE_ELICITATION,
    SDKUnavailableError,
    read_sdk_token,
    resolver_edicao_arquivo,
    resolver_elicitacao,
    resolver_pergunta_usuario,
    simular_elicitation_teste,
    stream_chat,
    stream_chat_ag_ui,
)
from local_chat_gateway.session_store import (
    SessionRecord,
    SessionStore,
    get_session_store,
)
from local_chat_gateway.telemetry import (
    emit_chat_trace,
    emit_governance_health_check_span,
    emit_governance_route_span,
    emit_governance_workflow_transition_span,
)
from local_chat_gateway.workspace_catalog import listar_arquivos_workspace

router = APIRouter()
logger = logging.getLogger(__name__)

_MODEL_ID: Final[Literal["deep-agents/router"]] = "deep-agents/router"
_STUB_CONTENT: Final[str] = (
    "stub: SDK real do Copilot ainda nao integrado nesta fase (RT-01)."
)
_STUB_COMPLETION_ID: Final[str] = "chatcmpl-stub"

# Handler de permissao conservador desta fase (nao-escopo -- ver docstring
# de `sdk_session.stream_chat`): nega toda tool exceto leitura simples e
# tools/comandos classificados como seguros por `permission_policy.
# tool_call_nao_escrita_e_segura` (ex.: `git --no-pager status/diff/log`
# via `run_in_terminal`), coerente com GATEWAY_PERMISSION_MODE=read_only
# default. Wiring completo com `PermissionPolicyStub` real (sessao/
# checkpoint) fica para fase futura.
#
# Bug real corrigido (2026-10-02): `pr-gatekeeper` (e qualquer outro agent
# que precise inspecionar o repositorio via `run_in_terminal`, ex.:
# `git --no-pager diff`/`git --no-pager log`) recebia "Negado pela politica
# local (GATEWAY_PERMISSION_MODE)." mesmo com `GATEWAY_PERMISSION_MODE=apply`
# no `.env` -- este handler so liberava tools cujo NOME comecasse com os
# prefixos de leitura abaixo, nunca inspecionando o COMANDO de uma tool de
# shell. A logica de classificacao foi centralizada (R-055) em
# `permission_policy.tool_call_nao_escrita_e_segura`, reaproveitada aqui E
# por `_governance_permission_handler`, para que a correcao beneficie
# TODOS os agents (nao apenas `pr-gatekeeper`) que dependam de
# `run_in_terminal` para operacoes read-only (git, ls, cat, etc.).
_READ_ONLY_TOOL_PREFIXES: Final[tuple[str, ...]] = READ_ONLY_TOOL_PREFIXES
"""Alias retrocompativel -- fonte real agora e
`permission_policy.READ_ONLY_TOOL_PREFIXES`."""


def _conservative_permission_handler(tool_name: str, params: Mapping[str, Any]) -> bool:
    """Handler de permissao conservador (Fase 3) -- leitura + comandos seguros."""
    return tool_call_nao_escrita_e_segura(tool_name, params)


# Marcador textual emitido por `sdk_session.stream_chat` quando o evento
# dedicado `SubagentStartedData` (RT-03, introspecao real confirmada via
# wheel `github_copilot_sdk==1.0.15`) dispara -- carrega o NOME REAL do
# agent invocado (`agent_display_name`/`agent_name`, ex.: `python-bug-fixer`),
# nao mais o nome literal da tool `run_subagent`. `_extrair_nome_tool_do_delta`
# precisa reconhecer este padrao para que `tools_executed` (telemetria
# `emit_chat_trace`) registre QUAL agent foi delegado, nao apenas que uma
# delegacao ocorreu.
_MARCADOR_SUBAGENT_INVOCADO: Final[str] = "**Subagent invocado:** `"
_PREFIXO_TELEMETRIA_SUBAGENT: Final[str] = "subagent:"


def _extrair_nome_tool_do_delta(delta: str) -> str | None:
    """Extrai o nome da tool/agent de um delta de inicio de execucao, se houver.

    Reconhece 2 padroes emitidos por `sdk_session.stream_chat`:
    1. Generico: `"tool: <nome> (iniciando)"` (`ToolExecutionStartData`) --
       retorna `<nome>` sem prefixo.
    2. Delegacao de agent: `"**Subagent invocado:** `<nome>`"`
       (`SubagentStartedData`, RT-03) -- retorna `"subagent:<nome>"`
       (prefixado) para que `tools_executed` distinga na telemetria um
       handoff de agent real (ex.: `subagent:python-bug-fixer`) de uma
       tool comum, sem perder QUAL agent foi invocado.

    Args:
        delta: Fragmento de texto (`delta.content`) recebido de `stream_chat`.

    Returns:
        str | None: Nome extraido (com prefixo `subagent:` no caso 2), ou
        `None` se `delta` nao for um evento de inicio reconhecido.
    """
    if _MARCADOR_SUBAGENT_INVOCADO in delta:
        resto = delta.split(_MARCADOR_SUBAGENT_INVOCADO, 1)[1]
        nome_agent = resto.split("`", 1)[0].strip()
        if nome_agent:
            return f"{_PREFIXO_TELEMETRIA_SUBAGENT}{nome_agent}"
        return None
    if "tool:" in delta and "(iniciando)" in delta:
        partes = delta.split("tool:")
        if len(partes) > 1:
            nome = partes[1].split("(")[0].strip()
            return nome or None
    return None


_AGENTE_ROUTER_PADRAO: Final[str] = "agent-router"


def _sessao_atual(record: SessionRecord | None) -> governance.Sessao:
    """Reconstroi a `governance.Sessao` imutavel a partir do `SessionRecord` persistido (T6/PR-6).

    Sessao sem registro ainda persistido (1o turno) ou sem `workflow` comeca
    sempre na `Fase.ROUTER` (AD-01) -- unica origem legal de um workflow (R-037).

    Guarda de invariante auto-corretiva (RK-06, bug real de producao
    2026-10-01, Addendum 7): `Fase.ROUTER` SEMPRE implica `workflow=None`
    (unica origem legal de workflow -- `_transicionar_a_partir_do_router`
    nunca retorna `Fase.ROUTER` com workflow preenchido). Linhas gravadas
    em `sessions` ANTES do fix do Addendum 6 (ou por qualquer outra via
    nao antecipada) podem conter `fase='router'` com `workflow`/`etapa`/
    `agente_ativo` residuais de um turno anterior -- um estado que o
    `governance_pipeline.preparar_turno` interpreta como "workflow ja
    ativo" (pois so checa `sessao.workflow is None`), gerando
    `TipoEvento.AVANCO_ETAPA` em vez de `DECISAO_ROTEAMENTO` e sendo
    rejeitado por `TransicaoInvalidaError` (R-037: "a partir da
    Fase.ROUTER so e aceita uma decisao de roteamento explicita").
    Sessoes com esse estado ficam travadas indefinidamente: como o TTL e
    renovado a cada `touch_session` (toda nova tentativa do usuario),
    `create_session` (que agora reseta corretamente) nunca e re-invocado
    enquanto a sessao continuar "viva". Esta funcao corrige a leitura
    (sem exigir migracao de dados) forcando `workflow=None`/`etapa=0`/
    `agente_ativo=padrao` sempre que `fase` resolver para `Fase.ROUTER`,
    independentemente do que estiver persistido no banco.
    """
    if record is None:
        return governance.Sessao(
            fase=governance.Fase.ROUTER,
            workflow=None,
            etapa=0,
            agente_ativo=_AGENTE_ROUTER_PADRAO,
        )
    try:
        fase = governance.Fase(record.fase)
    except ValueError:
        fase = governance.Fase.ROUTER

    if fase is governance.Fase.ROUTER:
        return governance.Sessao(
            fase=governance.Fase.ROUTER,
            workflow=None,
            etapa=0,
            agente_ativo=_AGENTE_ROUTER_PADRAO,
            aprovacoes=frozenset((record.aprovacoes or {}).keys()),
        )

    workflow: governance.Workflow | None = None
    if record.workflow is not None:
        try:
            workflow = governance.Workflow(record.workflow)
        except ValueError:
            workflow = None
    return governance.Sessao(
        fase=fase,
        workflow=workflow,
        etapa=record.etapa or 0,
        agente_ativo=record.agente_ativo or _AGENTE_ROUTER_PADRAO,
        aprovacoes=frozenset((record.aprovacoes or {}).keys()),
    )


def _governance_permission_handler(
    *,
    sessao: governance.Sessao,
    evento: governance.Evento,
    tabela: governance.TabelaTransicao,
    catalogo: governance.Catalogo,
    checkpoint_aberto: bool,
    workspace_root: Path,
    permission_mode: str,
) -> Callable[[str, Mapping[str, Any]], bool]:
    """Adapta `PermissionPolicyStub.autorizar_escrita` ao contrato do SDK (Q-04).

    So usado quando `settings.gateway_governance_permissions` e `True` -- leitura
    simples e comandos classificados como seguros (`permission_policy.
    tool_call_nao_escrita_e_segura` -- mesma fonte usada por
    `_conservative_permission_handler`, R-055) continuam liberados
    incondicionalmente; qualquer tentativa de escrita de arquivo e avaliada
    pelas 4 guardas de `PermissionPolicyStub` antes de autorizar.
    """
    policy = PermissionPolicyStub(
        mode=PermissionMode(permission_mode), workspace_root=workspace_root
    )

    def _handler(tool_name: str, params: Mapping[str, Any]) -> bool:
        if tool_call_nao_escrita_e_segura(tool_name, params):
            return True
        caminho_bruto = params.get("path") or params.get("file_path")
        if not caminho_bruto:
            return False
        decisao = policy.autorizar_escrita(
            sessao=sessao,
            evento=evento,
            tabela=tabela,
            catalogo=catalogo,
            checkpoint_aberto=checkpoint_aberto,
            caminho_destino=Path(str(caminho_bruto)),
        )
        return decisao.allowed

    return _handler


def _diretorios_de_projetos_registrados(settings: Settings) -> list[str]:
    """Descobre TODOS os projetos de `projects.local.yaml` acessiveis no container.

    Le `settings.projects_local_yaml` (default: repositorio de governanca
    inteiro ja montado em `/governance:ro`) e traduz cada `path_externo`
    para o path correspondente dentro do container, assumindo que todos os
    projetos vivem sob `settings.projects_root_path` (montado uma unica vez
    em `/workspaces`). Nao levanta excecao -- retorna lista vazia se
    `PROJECTS_ROOT_PATH` nao estiver configurado ou o YAML nao existir
    (comportamento equivalente a antes desta feature: apenas o
    `working_directory` default `/workspaces` fica disponivel).
    """
    projetos = carregar_projetos(
        projects_yaml_path=settings.projects_local_yaml,
        projects_root_path_host=settings.projects_root_path,
    )
    return [p.path_container for p in projetos]


def _session_store_configurado(
    settings: Settings = Depends(get_settings),
) -> SessionStore:
    """Dependencia FastAPI que instancia o `SessionStore` com os valores REAIS
    de `Settings` (`gateway_db_path`, `gateway_session_ttl_s`,
    `gateway_max_premium_per_day`).

    Bug real de producao encontrado em 2026-10-02: os 3 endpoints usavam
    `Depends(get_session_store)` DIRETO -- FastAPI invoca a dependencia sem
    nenhum argumento quando ela nao declara seus proprios `Depends(...)`,
    entao `get_session_store()` SEMPRE caia nos defaults hardcoded da
    funcao (`db_path=None` -> `/app/data/gateway.db`, `max_premium_per_day=
    100`), IGNORANDO silenciosamente `GATEWAY_DB_PATH`/
    `GATEWAY_SESSION_TTL_S`/`GATEWAY_MAX_PREMIUM_PER_DAY` configurados via
    `.env`/`dev_watch.py`. No Windows, o path hardcoded `/app/data/
    gateway.db` resolve (via `pathlib`) para `<DRIVE_ATUAL>:\\app\\data\\
    gateway.db` -- um banco SQLite paralelo, nunca limpo entre sessoes de
    teste, que acumulava o teto diario (`budget_daily`) de TODAS as
    execucoes anteriores do dia, até estourar `GATEWAY_MAX_PREMIUM_PER_DAY`
    e devolver 429 ("Teto diario de requisicoes atingido") mesmo em uma
    instancia de gateway recem-reiniciada -- o chat "nao respondia nada"
    silenciosamente. Esta funcao fecha o wiring: o `SessionStore` agora
    sempre usa o `db_path`/TTL/teto diario resolvidos de `Settings`.
    """
    return get_session_store(
        settings.gateway_db_path,
        session_ttl_s=settings.gateway_session_ttl_s,
        max_premium_per_day=settings.gateway_max_premium_per_day,
    )


@router.get("/healthz")
async def healthz(
    request: Request,
    settings: Settings = Depends(get_settings),
    session_store: SessionStore = Depends(_session_store_configurado),
) -> dict[str, str]:
    """Healthcheck sem autenticacao — nunca chama o Copilot SDK.

    T7/PR-7: emite (fire-and-forget, nao bloqueia a resposta) o span
    customizado `governance.health_check` com os 4 sinais de saude agregados
    (`deep_agents.health.*`): grafo de roteamento carregado, token do SDK
    legivel, coletor OTel configurado e teto diario nao esgotado.
    """
    graph_ok = getattr(request.app.state, "grafo", None) is not None
    sdk_token_ok = False
    try:
        read_sdk_token(settings.copilot_sdk_token_file)
        sdk_token_ok = True
    except Exception:
        sdk_token_ok = False
    collector_ok = bool(settings.otel_exporter_otlp_endpoint)
    hoje = time.strftime("%Y-%m-%d", time.gmtime())
    budget_ok = not session_store.is_daily_budget_exhausted(hoje)
    await emit_governance_health_check_span(
        settings.otel_exporter_otlp_endpoint,
        session_id="healthz",
        graph_ok=graph_ok,
        sdk_token_ok=sdk_token_ok,
        collector_ok=collector_ok,
        budget_ok=budget_ok,
    )
    return {"status": "ok"}


@router.get("/v1/models", dependencies=[Depends(require_bearer_token)])
async def list_models() -> ModelList:
    """Lista apenas `deep-agents/router` (R-037 — sem modelo por agent)."""
    return ModelList(data=[Model(id=_MODEL_ID)])


_LIMITE_ARQUIVOS_PADRAO: Final[int] = 30
_LIMITE_ARQUIVOS_MAXIMO: Final[int] = 200


@router.get("/v1/workspace/files", dependencies=[Depends(require_bearer_token)])
async def list_workspace_files(
    q: str = "",
    limit: int = _LIMITE_ARQUIVOS_PADRAO,
    settings: Settings = Depends(get_settings),
) -> WorkspaceFilesResponse:
    """Picker `#` do composer (paridade com "Select File, Folder or Tool" da
    IDE) -- lista arquivos do(s) projeto(s) registrados em
    `projects.local.yaml`, com fallback para `gateway_workspace_dir` quando
    nenhum projeto esta registrado (mesmo fallback de
    `_diretorios_de_projetos_registrados`).
    """
    projetos = carregar_projetos(
        projects_yaml_path=settings.projects_local_yaml,
        projects_root_path_host=settings.projects_root_path,
    )
    raizes: list[tuple[str, Path]] = [
        (p.nome, Path(p.path_container)) for p in projetos
    ] or [("workspace", Path(settings.gateway_workspace_dir))]
    limite_seguro = max(1, min(limit, _LIMITE_ARQUIVOS_MAXIMO))
    arquivos, truncado = listar_arquivos_workspace(
        raizes=raizes, query=q, limit=limite_seguro
    )
    return WorkspaceFilesResponse(
        files=[
            WorkspaceFileItem(path=a.path, project=a.project, name=a.name)
            for a in arquivos
        ],
        truncated=truncado,
    )


@router.get("/v1/workspace/agents", dependencies=[Depends(require_bearer_token)])
async def list_workspace_agents(request: Request) -> AgentCatalogResponse:
    """Picker `@` do composer (paridade com a listagem de agents da IDE) --
    devolve o mesmo catalogo de custom agents ja descoberto no lifespan
    (`app.state.custom_agents`, ver `agent_catalog.descobrir_custom_agents`)
    para que o frontend monte a lista de mencoes sem duplicar a descoberta.
    """
    custom_agents = getattr(request.app.state, "custom_agents", None) or []
    return AgentCatalogResponse(
        agents=[
            AgentCatalogItem(
                name=str(agente.get("name") or ""),
                display_name=agente.get("display_name"),
                description=agente.get("description"),
            )
            for agente in custom_agents
            if agente.get("name")
        ]
    )


_LIMITE_TURNS_PADRAO: Final[int] = 50
_LIMITE_TURNS_MAXIMO: Final[int] = 500


_LIMITE_COMANDOS_PADRAO: int = 200


@router.get("/v1/workspace/commands", dependencies=[Depends(require_bearer_token)])
async def list_workspace_commands(request: Request) -> CommandCatalogResponse:
    """Picker `/` do composer (paridade com o picker de slash commands/prompts
    da IDE, pedido explicito do usuario 2026-10-02) -- devolve o catalogo de
    prompts (`.github/prompts/*.prompt.md`) e skills (`.github/skills/**/
    SKILL.md`) ja descoberto no lifespan (`app.state.commands_catalog`, ver
    `prompts_catalog.descobrir_comandos`) para que o frontend monte a lista
    sem duplicar a descoberta nem reimplementar o parsing de frontmatter.
    """
    comandos = getattr(request.app.state, "commands_catalog", None) or []
    return CommandCatalogResponse(
        commands=[
            CommandCatalogItem(
                name=str(comando.get("name") or ""),
                kind=comando.get("kind", "prompt"),
                description=comando.get("description"),
            )
            for comando in comandos[:_LIMITE_COMANDOS_PADRAO]
            if comando.get("name")
        ]
    )


@router.get("/v1/turns", dependencies=[Depends(require_bearer_token)])
async def list_turns(
    session_id: str | None = None,
    limit: int = _LIMITE_TURNS_PADRAO,
    session_store: SessionStore = Depends(_session_store_configurado),
) -> list[dict[str, Any]]:
    """Historico DURAVEL de turnos (tabela `turns`, `turn_recorder.py`) --
    insumo de analise continua de melhoria de workflow/agent (pedido
    explicito do usuario, 2026-10-02).

    Read-only: consumido por `tests/evals`/`agent-evals-lab` (fechamento do
    loop "trace real -> dataset de avaliacao -> regressao") ou por
    consulta manual/dashboard externo. Cada registro contem prompt/
    resposta, agent/workflow/etapa/score de roteamento, tools/subagents
    executados, retries, falhas de model call, tokens/custo reais e sinais
    de estouro de contexto (truncamento/compactacao) -- ver
    `session_store.TurnRecord` para o schema completo.

    Args:
        session_id: Filtra por 1 sessao especifica; `None` lista de TODAS
            as sessoes (mais recentes primeiro).
        limit: Teto de registros retornados (capado em
            `_LIMITE_TURNS_MAXIMO` para evitar payloads descontrolados).

    Returns:
        list[dict]: 1 entrada por turno, serializado via `dataclasses.
        asdict` (mesmos campos de `TurnRecord`).
    """
    limite_seguro = max(1, min(limit, _LIMITE_TURNS_MAXIMO))
    registros = session_store.get_turns(session_id, limit=limite_seguro)
    return [asdict(registro) for registro in registros]


async def _stub_stream_chunks() -> AsyncIterator[str]:
    """Gera os chunks SSE do stub deterministico (fallback sem SDK real).

    Yields:
        str: linhas `data: <json>\\n\\n` no formato `ChatCompletionChunk`,
        encerrando com `data: [DONE]\\n\\n`.
    """
    created = int(time.time())
    role_chunk = ChatCompletionChunk(
        id=_STUB_COMPLETION_ID,
        created=created,
        model=_MODEL_ID,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(role="assistant"),
                finish_reason=None,
            )
        ],
    )
    yield f"data: {role_chunk.model_dump_json()}\n\n"

    content_chunk = ChatCompletionChunk(
        id=_STUB_COMPLETION_ID,
        created=created,
        model=_MODEL_ID,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(content=_STUB_CONTENT),
                finish_reason=None,
            )
        ],
    )
    yield f"data: {content_chunk.model_dump_json()}\n\n"

    stop_chunk = ChatCompletionChunk(
        id=_STUB_COMPLETION_ID,
        created=created,
        model=_MODEL_ID,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(),
                finish_reason="stop",
            )
        ],
    )
    yield f"data: {stop_chunk.model_dump_json()}\n\n"

    yield "data: [DONE]\n\n"


async def _local_text_stream(texto: str) -> AsyncIterator[str]:
    """Emite texto local via SSE sem chamar o SDK (Invariante 11 / custo zero)."""
    created = int(time.time())
    role_chunk = ChatCompletionChunk(
        id="chatcmpl-checkpoint",
        created=created,
        model=_MODEL_ID,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(role="assistant"),
                finish_reason=None,
            )
        ],
    )
    yield f"data: {role_chunk.model_dump_json()}\n\n"

    content_chunk = ChatCompletionChunk(
        id="chatcmpl-checkpoint",
        created=created,
        model=_MODEL_ID,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(content=texto),
                finish_reason=None,
            )
        ],
    )
    yield f"data: {content_chunk.model_dump_json()}\n\n"

    stop_chunk = ChatCompletionChunk(
        id="chatcmpl-checkpoint",
        created=created,
        model=_MODEL_ID,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(),
                finish_reason="stop",
            )
        ],
    )
    yield f"data: {stop_chunk.model_dump_json()}\n\n"

    yield "data: [DONE]\n\n"


def _local_text_completion(texto: str) -> ChatCompletion:
    """Retorna resposta nao-streaming para mensagem local (custo zero)."""
    return ChatCompletion(
        id="chatcmpl-checkpoint",
        created=int(time.time()),
        model=_MODEL_ID,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content=texto),
                finish_reason="stop",
            )
        ],
        usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
    )


async def _real_or_stub_stream(
    payload: ChatCompletionRequest,
    settings: Settings,
    *,
    session_id: str,
    checkpoint_aberto: bool,
    permission_handler: Callable[[str, Mapping[str, Any]], bool],
    system_message: str | None = None,
    agent_name: str = _AGENTE_ROUTER_PADRAO,
    trace_id: str | None = None,
    custom_agents: list[Mapping[str, Any]] | None = None,
) -> AsyncIterator[str]:
    """Tenta o SDK real; recua para o stub em `SDKUnavailableError`."""
    start_time_ns = int(time.time() * 1_000_000_000)
    prompt_texto = (payload.messages[-1].content or "") if payload.messages else ""
    conteudo_acumulado = ""
    tools_executadas: list[str] = []

    try:
        token = read_sdk_token(settings.copilot_sdk_token_file)
        async for chunk in stream_chat(
            token=token,
            model=settings.copilot_model,
            messages=payload.messages,
            permission_handler=permission_handler,
            working_directory=settings.gateway_workspace_dir,
            additional_directories=_diretorios_de_projetos_registrados(settings),
            session_id=session_id,
            permission_mode=settings.gateway_permission_mode,
            checkpoint_aberto=checkpoint_aberto,
            system_message=system_message,
            custom_agents=custom_agents,
        ):
            delta = chunk.choices[0].delta.content or ""
            if delta:
                conteudo_acumulado += delta
                nome_tool = _extrair_nome_tool_do_delta(delta)
                if nome_tool and nome_tool not in tools_executadas:
                    tools_executadas.append(nome_tool)
            yield f"data: {chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
        await emit_chat_trace(
            settings.otel_exporter_otlp_endpoint,
            session_id=session_id,
            prompt=prompt_texto,
            response_text=conteudo_acumulado,
            tools_executed=tools_executadas,
            start_time_ns=start_time_ns,
            agent_name=agent_name,
            model=settings.copilot_model,
            trace_id=trace_id,
        )
    except SDKUnavailableError as exc:
        logger.warning("sdk_unavailable_fallback_to_stub: %s", exc)
        async for line in _stub_stream_chunks():
            yield line
        await emit_chat_trace(
            settings.otel_exporter_otlp_endpoint,
            session_id=session_id,
            prompt=prompt_texto,
            response_text=_STUB_CONTENT,
            tools_executed=[],
            start_time_ns=start_time_ns,
            agent_name=agent_name,
            model=settings.copilot_model,
            trace_id=trace_id,
        )


async def _real_or_stub_completion(
    payload: ChatCompletionRequest,
    settings: Settings,
    *,
    session_id: str,
    checkpoint_aberto: bool,
    permission_handler: Callable[[str, Mapping[str, Any]], bool],
    system_message: str | None = None,
    agent_name: str = _AGENTE_ROUTER_PADRAO,
    trace_id: str | None = None,
    custom_agents: list[Mapping[str, Any]] | None = None,
) -> ChatCompletion:
    """Versao nao-streaming: acumula os deltas do SDK real ou usa o stub."""
    start_time_ns = int(time.time() * 1_000_000_000)
    prompt_texto = (payload.messages[-1].content or "") if payload.messages else ""
    conteudo = ""
    tools_executadas: list[str] = []
    try:
        token = read_sdk_token(settings.copilot_sdk_token_file)
        async for chunk in stream_chat(
            token=token,
            model=settings.copilot_model,
            messages=payload.messages,
            permission_handler=permission_handler,
            working_directory=settings.gateway_workspace_dir,
            additional_directories=_diretorios_de_projetos_registrados(settings),
            session_id=session_id,
            permission_mode=settings.gateway_permission_mode,
            checkpoint_aberto=checkpoint_aberto,
            system_message=system_message,
            custom_agents=custom_agents,
        ):
            delta = chunk.choices[0].delta.content or ""
            if delta:
                conteudo += delta
                nome_tool = _extrair_nome_tool_do_delta(delta)
                if nome_tool and nome_tool not in tools_executadas:
                    tools_executadas.append(nome_tool)
        await emit_chat_trace(
            settings.otel_exporter_otlp_endpoint,
            session_id=session_id,
            prompt=prompt_texto,
            response_text=conteudo,
            tools_executed=tools_executadas,
            start_time_ns=start_time_ns,
            agent_name=agent_name,
            model=settings.copilot_model,
            trace_id=trace_id,
        )
        return ChatCompletion(
            id="chatcmpl-sdk",
            created=int(time.time()),
            model=_MODEL_ID,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=conteudo),
                    finish_reason="stop",
                )
            ],
            usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )
    except SDKUnavailableError as exc:
        logger.warning("sdk_unavailable_fallback_to_stub: %s", exc)
        await emit_chat_trace(
            settings.otel_exporter_otlp_endpoint,
            session_id=session_id,
            prompt=prompt_texto,
            response_text=_STUB_CONTENT,
            tools_executed=[],
            start_time_ns=start_time_ns,
            agent_name=agent_name,
            model=settings.copilot_model,
            trace_id=trace_id,
        )
        reply = ChatMessage(role="assistant", content=_STUB_CONTENT)
        choice = ChatCompletionChoice(index=0, message=reply, finish_reason="stop")
        return ChatCompletion(
            id=_STUB_COMPLETION_ID,
            created=int(time.time()),
            model=_MODEL_ID,
            choices=[choice],
            usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )


@dataclass(frozen=True)
class _ContextoTurno:
    """Resultado da preparacao de governanca de 1 turno (Fase 2 -- AG-UI).

    Extraido de `chat_completions` (T6/PR-6) para ser reaproveitado pelo novo
    endpoint AG-UI nativo (`agui_run`) sem duplicar roteamento/transicao/
    checkpoint/budget (R-046 -- composicao, nao reimplementacao).
    """

    system_message: str
    permission_handler: Callable[[str, Mapping[str, Any]], bool]
    agent_name: str
    agent_name_exibido: str
    checkpoint_aberto: bool
    custom_agents: list[Mapping[str, Any]] | None
    handoff_origem: str | None = None
    handoff_motivo: str | None = None
    # Campos aditivos (pedido do usuario, 2026-10-02): dados de governanca
    # ja calculados aqui, repassados a `stream_chat_ag_ui` para persistir o
    # historico duravel do turno na tabela `turns` (`turn_recorder.py`) sem
    # duplicar a logica de roteamento/transicao de workflow.
    workflow: str | None = None
    etapa: int | None = None
    score_roteamento: float | None = None
    drift_detectado: bool | None = None


async def _preparar_turno_de_governanca(
    *,
    request: Request,
    settings: Settings,
    session_store: SessionStore,
    session_id: str,
    mensagem_atual: str,
    turno_trace_id: str,
) -> _ContextoTurno | str:
    """Budget diario, checkpoint humano, roteamento/transicao e `system_message`.

    Returns:
        _ContextoTurno: pronto para dispatch real/stub (stream ou nao).
        str: texto controlado a devolver IMEDIATAMENTE (sem tocar o SDK) --
        reemissao de checkpoint nao resolvido OU transicao de governanca
        invalida (CA-05: nunca HTTP 500, sempre 200 com texto).

    Raises:
        HTTPException: 429 se `GATEWAY_MAX_PREMIUM_PER_DAY` foi atingido.
    """
    hoje = time.strftime("%Y-%m-%d", time.gmtime())
    if session_store.is_daily_budget_exhausted(hoje):
        raise HTTPException(
            status_code=429,
            detail="Teto diario de requisicoes atingido (GATEWAY_MAX_PREMIUM_PER_DAY)",
        )
    session_store.register_premium_request(hoje, amount=1)

    if session_store.is_session_expired(session_id):
        session_store.create_session(session_id)
    else:
        session_store.touch_session(session_id)

    checkpoint = session_store.get_open_checkpoint(session_id)
    checkpoint_aberto = checkpoint is not None
    if checkpoint is not None:
        res = parse_checkpoint_response(
            mensagem_atual, checkpoint_id_aberto=checkpoint.checkpoint_id
        )
        if not res.resolved:
            return (
                f"[CHECKPOINT] Resposta nao reconhecida para o checkpoint "
                f"aberto [{checkpoint.checkpoint_id}]:\n\n"
                f"{checkpoint.question}\n\n"
                f"Por favor responda com o numero da opcao (ex: '1', '2') "
                f"ou '0: sua resposta'."
            )
        session_store.resolve_checkpoint(checkpoint.checkpoint_id)
        checkpoint_aberto = False

    grafo = request.app.state.grafo
    tabela_transicao = request.app.state.tabela_transicao
    catalogo = request.app.state.catalogo
    sessao_atual = _sessao_atual(session_store.get_session(session_id))
    decisao = governance_pipeline.preparar_turno(
        sessao_atual, mensagem_atual, grafo, tabela_transicao
    )
    await emit_governance_route_span(
        settings.otel_exporter_otlp_endpoint,
        session_id=session_id,
        escolhido=decisao.agente_escolhido,
        workflow=decisao.workflow.value if decisao.workflow is not None else None,
        nivel=decisao.nivel,
        score=decisao.score,
        drift_detectado=decisao.drift_detectado,
        trace_id=turno_trace_id,
    )
    if decisao.workflow is None and sessao_atual.fase is governance.Fase.ROUTER:
        # Permanece no agent-router em Fase.ROUTER (intake / saudacao) sem transicionar workflow
        sessao_nova = sessao_atual
        evento_turno = governance.Evento(
            origem="chat_completions",
            turno=governance.Turno(texto=mensagem_atual),
            tipo=governance.TipoEvento.AVANCO_ETAPA,
            agente_solicitado=decisao.agente_escolhido,
            workflow_solicitado=None,
        )
    else:
        evento_turno = governance.Evento(
            origem="chat_completions",
            turno=governance.Turno(texto=mensagem_atual),
            tipo=(
                governance.TipoEvento.DECISAO_ROTEAMENTO
                if decisao.roteou_novamente
                else governance.TipoEvento.AVANCO_ETAPA
            ),
            agente_solicitado=decisao.agente_escolhido,
            workflow_solicitado=decisao.workflow if decisao.roteou_novamente else None,
        )
        resultado_transicao = governance_pipeline.avaliar_transicao(
            sessao_atual, evento_turno, tabela_transicao
        )
        await emit_governance_workflow_transition_span(
            settings.otel_exporter_otlp_endpoint,
            session_id=session_id,
            fase_origem=sessao_atual.fase.value,
            fase_destino=(
                resultado_transicao.sessao_atualizada.fase.value
                if resultado_transicao.sucesso
                and resultado_transicao.sessao_atualizada is not None
                else sessao_atual.fase.value
            ),
            etapa=(
                resultado_transicao.sessao_atualizada.etapa
                if resultado_transicao.sucesso
                and resultado_transicao.sessao_atualizada is not None
                else sessao_atual.etapa
            ),
            aprovacao_checkpoint=evento_turno.aprovacao_concedida,
            error_type=resultado_transicao.erro_tipo,
            trace_id=turno_trace_id,
        )
        if not resultado_transicao.sucesso:
            return (
                "[GOVERNANCA] Nao foi possivel avancar o turno de governanca "
                f"(sessao preservada no estado anterior): {resultado_transicao.erro}"
            )

        sessao_nova = resultado_transicao.sessao_atualizada
        assert (
            sessao_nova is not None
        )  # garantido por `sucesso=True` em ResultadoTransicao
    session_store.atualizar_estado_governanca(
        session_id,
        fase=sessao_nova.fase.value,
        workflow=(
            sessao_nova.workflow.value if sessao_nova.workflow is not None else None
        ),
        etapa=sessao_nova.etapa,
        agente_ativo=sessao_nova.agente_ativo,
        aprovacoes={nome: True for nome in sessao_nova.aprovacoes},
    )

    system_message = governance_pipeline.montar_contexto(
        decisao.agente_exibido or sessao_nova.agente_ativo,
        sessao_nova.workflow,
        sessao_nova.etapa,
        github_dir=settings.governance_github_dir,
    )

    permission_handler: Callable[[str, Mapping[str, Any]], bool]
    if settings.gateway_governance_permissions:
        permission_handler = _governance_permission_handler(
            sessao=sessao_nova,
            evento=evento_turno,
            tabela=tabela_transicao,
            catalogo=catalogo,
            checkpoint_aberto=checkpoint_aberto,
            workspace_root=Path(settings.projects_root_path or "/workspaces"),
            permission_mode=settings.gateway_permission_mode,
        )
    else:
        permission_handler = _conservative_permission_handler

    custom_agents = getattr(request.app.state, "custom_agents", None)

    return _ContextoTurno(
        system_message=system_message,
        permission_handler=permission_handler,
        agent_name=sessao_nova.agente_ativo,
        agent_name_exibido=decisao.agente_exibido or sessao_nova.agente_ativo,
        checkpoint_aberto=checkpoint_aberto,
        custom_agents=custom_agents,
        handoff_origem=decisao.handoff_origem,
        handoff_motivo=decisao.handoff_motivo,
        workflow=(
            sessao_nova.workflow.value if sessao_nova.workflow is not None else None
        ),
        etapa=sessao_nova.etapa,
        score_roteamento=decisao.score,
        drift_detectado=decisao.drift_detectado,
    )


@router.post(
    "/v1/chat/completions",
    dependencies=[Depends(require_bearer_token)],
    response_model=None,
)
async def chat_completions(
    payload: ChatCompletionRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
    session_store: SessionStore = Depends(_session_store_configurado),
) -> ChatCompletion | StreamingResponse:
    """Integracao real com governanca multi-turno, checkpoint engine e teto diario."""
    # 1. Identificacao da sessao (header ou hash da 1a mensagem)
    session_id = (
        request.headers.get("x-session-id")
        or request.headers.get("x-conversation-id")
        or (
            hashlib.sha256(
                (payload.messages[0].content or "").encode("utf-8")
            ).hexdigest()[:16]
            if payload.messages
            else "default-session"
        )
    )

    # 1b. Addendum 8 -- trace_id UNICO por turno (bug: cada span de
    # telemetria gerava seu proprio trace_id, fragmentando o turno em ate
    # 4 traces desconectados no Langfuse). Gerado uma unica vez aqui e
    # repassado a todas as funcoes de emissao de span deste turno.
    turno_trace_id = uuid.uuid4().hex
    mensagem_atual = (payload.messages[-1].content or "") if payload.messages else ""

    contexto = await _preparar_turno_de_governanca(
        request=request,
        settings=settings,
        session_store=session_store,
        session_id=session_id,
        mensagem_atual=mensagem_atual,
        turno_trace_id=turno_trace_id,
    )
    if isinstance(contexto, str):
        if payload.stream:
            return StreamingResponse(
                _local_text_stream(contexto), media_type="text/event-stream"
            )
        return _local_text_completion(contexto)

    if payload.stream:
        return StreamingResponse(
            _real_or_stub_stream(
                payload,
                settings,
                session_id=session_id,
                checkpoint_aberto=contexto.checkpoint_aberto,
                permission_handler=contexto.permission_handler,
                system_message=contexto.system_message,
                agent_name=contexto.agent_name,
                trace_id=turno_trace_id,
                custom_agents=contexto.custom_agents,
            ),
            media_type="text/event-stream",
        )
    return await _real_or_stub_completion(
        payload,
        settings,
        session_id=session_id,
        checkpoint_aberto=contexto.checkpoint_aberto,
        permission_handler=contexto.permission_handler,
        system_message=contexto.system_message,
        agent_name=contexto.agent_name,
        trace_id=turno_trace_id,
        custom_agents=contexto.custom_agents,
    )


def _resolver_modelo_agent(
    nome_agent: str | None, custom_agents: list[Mapping[str, Any]] | None
) -> str | None:
    """Resolve o `model:` declarado no frontmatter do `.agent.md` ativo.

    Usado para exibir o modelo (ex.: "Claude Sonnet 5") ao lado do nome do
    agent no badge "Agente Ativo" do chat (`sdk_session.stream_chat_ag_ui`,
    parametro `agent_model`) -- paridade com a informacao ja disponivel no
    catalogo (`agent_catalog.CustomAgentConfig["model"]`, campo opcional
    `NotRequired`) sem reimplementar o parsing de frontmatter aqui.

    Args:
        nome_agent: Nome tecnico do agent ativo (`sessao_nova.agente_ativo`,
            equivalente ao `name:` do frontmatter, ex.: "agent-router").
        custom_agents: Catalogo ja carregado em `request.app.state.
            custom_agents` (lista de `CustomAgentConfig`, ver
            `agent_catalog.descobrir_custom_agents`).

    Returns:
        str | None: valor de `model` do agent correspondente, ou `None` se
        o agent nao foi encontrado no catalogo ou nao declara `model:` no
        frontmatter (campo opcional).
    """
    if not nome_agent or not custom_agents:
        return None
    for agente in custom_agents:
        if str(agente.get("name") or "") == nome_agent:
            modelo = agente.get("model")
            return str(modelo) if isinstance(modelo, str) and modelo.strip() else None
    return None


def _extrair_texto_e_anexos(mensagem: Any) -> tuple[str, list[dict[str, Any]]]:
    """Extrai texto plano + anexos (imagem/documento/audio/video) de 1
    mensagem AG-UI (`ag_ui.core.UserMessage.content: str | list[ContentPart]`).

    Suporte a anexos (imagens/arquivos no chat, paridade com o Copilot IDE):
    o `<CopilotChat attachments={{enabled:true}}>`/`<CopilotSidebar>` do
    CopilotKit v2 le cada arquivo anexado pelo usuario como base64 e monta
    `content: [{"type":"text",...}, {"type":"image"|"document"|...,
    "source":{"type":"data","value":base64,"mimeType":...}}, ...]`
    (ver docs.copilotkit.ai/multimodal-attachments) -- exatamente o shape
    `ImagePart`/`DocumentPart`/`AudioPart`/`VideoPart` com `source:
    DataSource` ja validado por `ag_ui.core.UserMessage` (introspeccao real
    via `ctx_execute`, 2026-10-02). Cada parte de midia e convertida para o
    formato `BlobAttachment` aceito por `CopilotSession.send(attachments=
    [...])` do Copilot SDK (`{"type": "blob", "data": base64, "mimeType":
    str, "displayName"?: str}` -- chaves EM camelCase, confirmado por
    introspecao real de `copilot.session.BlobAttachment`).

    Fontes `UrlSource` (`onUpload` customizado devolvendo URL em vez de
    base64 inline) NAO sao suportadas nesta fase (o gateway nao faz
    download de URL remota) -- um aviso textual e anexado ao prompt para o
    modelo/usuario entenderem que o arquivo nao foi processado.

    Returns:
        tuple[str, list[dict]]: texto plano (para `mensagem_atual`/governanca
        e para o historico `_joined_prompt`) + lista de `BlobAttachment`
        prontos para `stream_chat_ag_ui(attachments=...)`.
    """
    conteudo = getattr(mensagem, "content", None)
    if conteudo is None or isinstance(conteudo, str):
        return (conteudo or ""), []

    textos: list[str] = []
    anexos: list[dict[str, Any]] = []
    avisos: list[str] = []
    for parte in conteudo:
        tipo = str(getattr(parte, "type", ""))
        if tipo == "text":
            textos.append(str(getattr(parte, "text", "")))
            continue
        if tipo not in ("image", "document", "audio", "video"):
            continue
        origem = getattr(parte, "source", None)
        origem_tipo = str(getattr(origem, "type", "")) if origem is not None else ""
        if origem_tipo != "data":
            avisos.append(
                f"[anexo '{tipo}' via origem '{origem_tipo or 'desconhecida'}' "
                "nao suportado nesta fase -- apenas anexos em base64 inline]"
            )
            continue
        metadata = getattr(parte, "metadata", None)
        nome_arquivo = (
            metadata.get("filename") if isinstance(metadata, Mapping) else None
        )
        anexo: dict[str, Any] = {
            "type": "blob",
            "data": str(getattr(origem, "value", "")),
            "mimeType": str(
                getattr(origem, "mime_type", None) or "application/octet-stream"
            ),
        }
        if nome_arquivo:
            anexo["displayName"] = str(nome_arquivo)
        anexos.append(anexo)

    texto_final = " ".join(t for t in textos if t).strip()
    if avisos:
        texto_final = (texto_final + "\n" + "\n".join(avisos)).strip()
    if not texto_final and anexos:
        texto_final = "(arquivo anexado sem comentário adicional)"
    return texto_final, anexos


@router.post(
    "/v2/agent",
    dependencies=[Depends(require_bearer_token)],
    response_model=None,
)
async def agui_run(
    payload: dict[str, Any],
    request: Request,
    settings: Settings = Depends(get_settings),
    session_store: SessionStore = Depends(_session_store_configurado),
) -> StreamingResponse:
    """Endpoint AG-UI nativo (Fase 2 -- paridade visual com o plugin Copilot da IDE).

    Aceita um `RunAgentInput` (protocolo AG-UI -- docs.ag-ui.com) e devolve um
    stream SSE de eventos REAIS do protocolo (`RunStartedEvent`,
    `TextMessageStart/Content/EndEvent`, `ToolCallStart/End/ResultEvent`,
    `SubagentStarted/Finished/ErrorEvent` -- AG-UI 1.0) via
    `sdk_session.stream_chat_ag_ui`, em vez do texto markdown achatado de
    `/v1/chat/completions` -- permite que o frontend (CopilotKit v2 +
    `HttpAgent`, ver `apps/web/app/api/copilotkit/[[...path]]/route.ts`)
    renderize subagent como card nativo (AG-UI 1.0 "subagent support") e tool
    calls estruturados, em vez de texto literal.

    `payload` e tipado como `dict[str, Any]` (nao `RunAgentInput` diretamente)
    para tolerar campos adicionais que o CopilotKit `HttpAgent` possa enviar
    sem quebrar o parse -- validado manualmente via `RunAgentInput(**payload)`
    logo abaixo, com o mesmo efeito de uma dependencia FastAPI tipada.

    Nao-escopo desta 1a iteracao (RT-05, spike pendente): `ask_questions`
    como `useHumanInTheLoop` real no frontend -- requer introspeccao do
    mecanismo exato pelo qual o SDK real expoe a tool nativa `ask_questions`
    em sessao headless (sem TTY), ainda nao confirmada por teste ao vivo
    (mesma metodologia RT-01..RT-04 ja usada para `run_subagent`/subagent
    events). Ate la, `ask_questions` continua fluindo como texto normal do
    assistente (sem pausa real de turno) -- mesmo comportamento de hoje.
    """
    from ag_ui.core import RunAgentInput, RunErrorEvent
    from ag_ui.encoder import EventEncoder

    run_input = RunAgentInput(**payload)
    session_id = run_input.thread_id or run_input.run_id
    mensagem_atual, anexos_turno_atual = next(
        (
            _extrair_texto_e_anexos(m)
            for m in reversed(run_input.messages)
            if m.role == "user"
        ),
        ("", []),
    )
    turno_trace_id = uuid.uuid4().hex

    encoder = EventEncoder(accept=request.headers.get("accept"))

    if mensagem_atual.strip() == PROMPT_TESTE_ELICITATION:
        # Atalho de QA (ver nota em `sdk_session.PROMPT_TESTE_ELICITATION`):
        # bypassa SDK/modelo e dispara uma elicitation REAL de teste, para
        # exercitar `ElicitationBridge.tsx` fim-a-fim a partir do proprio
        # chat -- hoje o modelo NUNCA invoca a elicitation nativa (sempre
        # usa `ask_user`/`AskUserBridge.tsx`, ver RT-05).
        async def _gerar_teste_elicitation() -> AsyncIterator[str]:
            async for ag_ui_event in simular_elicitation_teste(
                thread_id=session_id, run_id=run_input.run_id
            ):
                yield encoder.encode(ag_ui_event)

        return StreamingResponse(
            _gerar_teste_elicitation(), media_type=encoder.get_content_type()
        )

    contexto = await _preparar_turno_de_governanca(
        request=request,
        settings=settings,
        session_store=session_store,
        session_id=session_id,
        mensagem_atual=mensagem_atual,
        turno_trace_id=turno_trace_id,
    )

    async def _gerar() -> AsyncIterator[str]:
        if isinstance(contexto, str):
            # Checkpoint nao resolvido / transicao invalida -- devolve texto
            # controlado como 1 unica mensagem AG-UI (sem tocar o SDK),
            # preservando CA-05 (nunca falha o run, sempre texto controlado).
            from ag_ui.core import (
                RunFinishedEvent,
                RunStartedEvent,
                TextMessageContentEvent,
                TextMessageEndEvent,
                TextMessageStartEvent,
            )

            msg_id = uuid.uuid4().hex
            yield encoder.encode(
                RunStartedEvent(thread_id=session_id, run_id=run_input.run_id)
            )
            yield encoder.encode(
                TextMessageStartEvent(message_id=msg_id, role="assistant")
            )
            yield encoder.encode(
                TextMessageContentEvent(message_id=msg_id, delta=contexto)
            )
            yield encoder.encode(TextMessageEndEvent(message_id=msg_id))
            yield encoder.encode(
                RunFinishedEvent(thread_id=session_id, run_id=run_input.run_id)
            )
            return

        try:
            token = read_sdk_token(settings.copilot_sdk_token_file)
        except SDKUnavailableError as exc:
            yield encoder.encode(RunErrorEvent(message=str(exc)))
            return

        async for ag_ui_event in stream_chat_ag_ui(
            token=token,
            model=settings.copilot_model,
            messages=[
                ChatMessage(role=m.role, content=_extrair_texto_e_anexos(m)[0])
                for m in run_input.messages
            ],
            attachments=anexos_turno_atual or None,
            permission_handler=contexto.permission_handler,
            thread_id=session_id,
            run_id=run_input.run_id,
            working_directory=settings.gateway_workspace_dir,
            additional_directories=_diretorios_de_projetos_registrados(settings),
            session_id=session_id,
            permission_mode=settings.gateway_permission_mode,
            checkpoint_aberto=contexto.checkpoint_aberto,
            system_message=contexto.system_message,
            custom_agents=contexto.custom_agents,
            agent_name=contexto.agent_name_exibido,
            agent_model=_resolver_modelo_agent(
                contexto.agent_name, contexto.custom_agents
            ),
            handoff_origem=contexto.handoff_origem,
            handoff_motivo=contexto.handoff_motivo,
            turn_recorder_store=session_store,
            turno_trace_id=turno_trace_id,
            prompt_usuario=mensagem_atual,
            workflow=contexto.workflow,
            etapa=contexto.etapa,
            score_roteamento=contexto.score_roteamento,
            drift_detectado=contexto.drift_detectado,
        ):
            yield encoder.encode(ag_ui_event)

    return StreamingResponse(_gerar(), media_type=encoder.get_content_type())


_ACOES_ELICITACAO_VALIDAS: Final[frozenset[str]] = frozenset(
    {"accept", "decline", "cancel"}
)


@router.post(
    "/v1/elicitation/{request_id}/respond",
    dependencies=[Depends(require_bearer_token)],
)
async def elicitation_respond(
    request_id: str, payload: dict[str, Any]
) -> dict[str, str]:
    """Resolve uma elicitation MCP pendente (ex.: `ask_questions`) com a
    resposta real do usuario (RT-05 -- ver nota de modulo em
    `sdk_session.stream_chat_ag_ui`).

    Chamado pelo frontend (`apps/web/app/api/elicitation/[requestId]/route.ts`
    -> `apps/web/copilot/ElicitationBridge.tsx`) apos o usuario preencher (ou
    cancelar) o formulario renderizado a partir do `CustomEvent(name=
    "elicitation_requested")` recebido no stream AG-UI. NAO inicia um novo
    turno/run -- apenas desbloqueia a coroutine `_bridge_elicitacao`, que
    continua pausada dentro do MESMO stream AG-UI ja aberto no browser.

    Args:
        request_id: Identificador recebido em `CustomEvent.value.request_id`.
        payload: `{"action": "accept"|"decline"|"cancel", "content"?: dict}`.

    Returns:
        dict[str, str]: `{"status": "ok"}` em caso de sucesso.

    Raises:
        HTTPException: 400 se `action` ausente/invalida; 404 se `request_id`
        desconhecido, ja resolvido ou expirado (o usuario demorou demais).
    """
    action = str(payload.get("action") or "")
    if action not in _ACOES_ELICITACAO_VALIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"action invalida: {action!r} (esperado um de {sorted(_ACOES_ELICITACAO_VALIDAS)})",
        )
    content = payload.get("content")
    resolvido = resolver_elicitacao(
        request_id,
        action=action,
        content=dict(content) if isinstance(content, Mapping) else None,
    )
    if not resolvido:
        raise HTTPException(
            status_code=404,
            detail="elicitation desconhecida, ja resolvida ou expirada",
        )
    return {"status": "ok"}


@router.post(
    "/v1/ask-user/{request_id}/respond",
    dependencies=[Depends(require_bearer_token)],
)
async def ask_user_respond(request_id: str, payload: dict[str, Any]) -> dict[str, str]:
    """Resolve uma pergunta `ask_user` pendente com a resposta real do usuario
    (RT-05 -- mecanismo LEGADO confirmado como o unico funcional por teste
    isolado via sandbox, 2026-10-02; ver nota de modulo em
    `sdk_session.stream_chat_ag_ui`).

    Chamado pelo frontend (`apps/web/app/api/ask-user/[requestId]/route.ts`
    -> `apps/web/copilot/AskUserBridge.tsx`) apos o usuario escolher uma
    opcao (ou responder em texto livre) para o `CustomEvent(name=
    "ask_user_requested")` recebido no stream AG-UI. NAO inicia um novo
    turno/run -- apenas desbloqueia a coroutine `_bridge_user_input`, que
    continua pausada dentro do MESMO stream AG-UI ja aberto no browser.

    Args:
        request_id: Identificador recebido em `CustomEvent.value.request_id`.
        payload: `{"answer": str, "was_freeform"?: bool}`. `was_freeform`
            default `False` (resposta veio de uma das `choices` oferecidas).

    Returns:
        dict[str, str]: `{"status": "ok"}` em caso de sucesso.

    Raises:
        HTTPException: 400 se `answer` ausente/vazia; 404 se `request_id`
        desconhecido, ja resolvido ou expirado (o usuario demorou demais).
    """
    answer = str(payload.get("answer") or "")
    if not answer:
        raise HTTPException(
            status_code=400, detail="answer e obrigatoria e nao pode ser vazia"
        )
    resolvido = resolver_pergunta_usuario(
        request_id,
        answer=answer,
        was_freeform=bool(payload.get("was_freeform", False)),
    )
    if not resolvido:
        raise HTTPException(
            status_code=404,
            detail="pergunta ask_user desconhecida, ja resolvida ou expirada",
        )
    return {"status": "ok"}


_ACOES_EDICAO_ARQUIVO_VALIDAS: Final[frozenset[str]] = frozenset({"approve", "reject"})


@router.post(
    "/v1/file-edit/{request_id}/respond",
    dependencies=[Depends(require_bearer_token)],
)
async def file_edit_respond(request_id: str, payload: dict[str, Any]) -> dict[str, str]:
    """Resolve uma edicao de arquivo pendente de aprovacao humana no chat
    (`PermissionRequestWrite`) com a decisao real do usuario -- feature
    pedida explicitamente pelo usuario (2026-10-02) para visualizar o DIFF
    de um arquivo que o agent quer alterar (paridade com o plugin Copilot
    da IDE) ANTES da escrita real ocorrer no disco (ver nota de modulo em
    `sdk_session.stream_chat_ag_ui`, bloco `_bridge_edicao_arquivo`).

    Chamado pelo frontend (`apps/web/app/api/file-edit/[requestId]/route.ts`
    -> `apps/web/copilot/FileEditBridge.tsx`) apos o usuario revisar TODAS
    as linhas do diff renderizado a partir do `CustomEvent(name=
    "file_edit_requested")` recebido no stream AG-UI, e clicar em "Aplicar
    alterações" ou "Ignorar". NAO inicia um novo turno/run -- apenas
    desbloqueia a coroutine `_bridge_edicao_arquivo`, que continua pausada
    dentro do MESMO stream AG-UI ja aberto no browser.

    Args:
        request_id: Identificador recebido em `CustomEvent.value.request_id`.
        payload: `{"action": "approve"|"reject"}`.

    Returns:
        dict[str, str]: `{"status": "ok"}` em caso de sucesso.

    Raises:
        HTTPException: 400 se `action` ausente/invalida; 404 se `request_id`
        desconhecido, ja resolvido ou expirado (o usuario demorou demais --
        fail-safe: a escrita e tratada como rejeitada neste caso).
    """
    action = str(payload.get("action") or "")
    if action not in _ACOES_EDICAO_ARQUIVO_VALIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"action invalida: {action!r} (esperado um de {sorted(_ACOES_EDICAO_ARQUIVO_VALIDAS)})",
        )
    resolvido = resolver_edicao_arquivo(request_id, aprovado=(action == "approve"))
    if not resolvido:
        raise HTTPException(
            status_code=404,
            detail="edicao de arquivo desconhecida, ja resolvida ou expirada",
        )
    return {"status": "ok"}
