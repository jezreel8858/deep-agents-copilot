"""governance_pipeline — composicao pura sobre `governance.py` (Q-02/Q-03).

Carrega o contexto imutavel de governanca (Grafo + TabelaTransicao +
Catalogo) exigido pelo `lifespan` de `app.py`. Este modulo NUNCA
reimplementa logica de roteamento -- apenas orquestra chamadas a
`governance.carregar_grafo` / `governance.compilar_tabela_transicao`
(R-046). Validavel via:
    grep -r "def rotear" OR "def transicionar" em deploy/local-chat-gateway/src/local_chat_gateway/governance_pipeline.py

Nesta etapa (T3/PR-3), alem de `carregar_contexto_governanca` (T2),
tres novas funcoes publicas de composicao pura sao adicionadas:
`preparar_turno`, `avaliar_transicao` e `montar_contexto`. Nenhuma
delas reimplementa logica de roteamento/transicao/deriva -- apenas
compoem chamadas a `governance.rotear` / `governance.transicionar` /
`governance.detectar_deriva` (CA-01).
"""

from __future__ import annotations

import logging
import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import governance_runner.routing as _routing_facade

from local_chat_gateway import governance
from local_chat_gateway.config import Settings

logger = logging.getLogger(__name__)

_SCHEMA_FILENAME = "routing-graph.schema.json"

# --- T3: injecao de contexto `.github/` (Secao 4 do Plano de Planejamento) ---
# Raiz do repositorio calculada a partir deste arquivo:
#   .../deploy/local-chat-gateway/src/local_chat_gateway/governance_pipeline.py
# parents[0]=local_chat_gateway, [1]=src, [2]=local-chat-gateway, [3]=deploy, [4]=raiz.
_RAIZ_REPOSITORIO = Path(__file__).resolve().parents[4]
_GITHUB_DIR = _RAIZ_REPOSITORIO / ".github"
_ORCAMENTO_BYTES_CONTEXTO = 32 * 1024
_MARCADOR_TRUNCAMENTO = "\n[... truncado por orcamento de contexto ...]"
_SEGMENTO_PROIBIDO = "hooks"
# RK-03: `.github/hooks/` NUNCA e lido por `montar_contexto` -- causa raiz
# do bug de injecao cruzada de contexto de 2026-09-29. Qualquer caminho cujo
# segmento resolvido contenha "hooks" e bloqueado por `_caminho_contexto_seguro`
# antes de qualquer chamada ao `leitor_arquivo` injetavel.


class GovernanceGraphPathNaoConfiguradoError(RuntimeError):
    """Erro de dominio: `settings.governance_graph_path` ausente no startup.

    O lifespan do gateway exige um `routing-graph.yaml` valido para
    compilar a `TabelaTransicao` consumida pelo roteamento -- sem este
    caminho configurado (`GOVERNANCE_GRAPH_PATH`), o startup e recusado
    (fail-fast, mesma politica de Q-02).
    """


@dataclass(frozen=True)
class ContextoGovernanca:
    """Contexto imutavel de governanca, carregado uma unica vez no lifespan.

    Attributes:
        grafo: Grafo dirigido compilado por `governance.carregar_grafo`.
            Tipado como `Any` porque `Grafo` ainda nao faz parte da
            fachada publica `governance_runner.routing` (R-046) -- apenas
            `TabelaTransicao`/`Catalogo` sao reexportados.
        tabela_transicao: Tabela imutavel `(Workflow, etapa) -> EtapaSpec`.
        catalogo: Vista tipada de `catalog.yaml` (agentes, tools).
    """

    grafo: Any
    tabela_transicao: governance.TabelaTransicao
    catalogo: governance.Catalogo


def _resolver_schema_padrao() -> Path:
    """Resolve o schema JSON embutido no pacote `governance_runner.routing` (Q-03).

    Returns:
        Path: caminho absoluto de `routing-graph.schema.json`, co-localizado
        com o pacote de roteamento (nunca um submodulo interno -- apenas o
        `__file__` do pacote-fachada `governance_runner.routing`).
    """
    pacote_dir = Path(_routing_facade.__file__).resolve().parent
    return pacote_dir / _SCHEMA_FILENAME


def carregar_contexto_governanca(settings: Settings) -> ContextoGovernanca:
    """Carrega Grafo + TabelaTransicao + Catalogo uma unica vez (lifespan).

    Comportamento fail-fast (Q-02): se `carregar_grafo` levantar
    `GraphValidationError`, a mensagem estruturada e logada em nivel
    CRITICAL (com `graph_path`, `schema_path` e a causa original) e a
    excecao propaga sem captura -- o gateway NAO sobe em modo degradado.

    Args:
        settings: Configuracao resolvida do gateway (`Settings`).

    Returns:
        ContextoGovernanca: contexto imutavel pronto para `app.state`.

    Raises:
        GovernanceGraphPathNaoConfiguradoError: Se
            `settings.governance_graph_path` for `None`.
        governance.GraphValidationError: Se o grafo for invalido (fail-fast).
    """
    if settings.governance_graph_path is None:
        raise GovernanceGraphPathNaoConfiguradoError(
            "GOVERNANCE_GRAPH_PATH nao configurado -- settings.governance_graph_path "
            "e obrigatorio para o lifespan do gateway carregar o grafo de roteamento."
        )

    graph_path = Path(settings.governance_graph_path)
    schema_path = (
        Path(settings.governance_schema_path)
        if settings.governance_schema_path is not None
        else _resolver_schema_padrao()
    )

    try:
        grafo = governance.carregar_grafo(graph_path, schema_path)
        tabela_transicao = governance.compilar_tabela_transicao(grafo)
    except governance.GraphValidationError as exc:
        logger.critical(
            "Fail-fast (Q-02): grafo de governanca invalido no startup do gateway "
            "-- graph_path=%s schema_path=%s causa=%s",
            graph_path,
            schema_path,
            exc,
        )
        raise

    return ContextoGovernanca(
        grafo=grafo,
        tabela_transicao=tabela_transicao,
        catalogo=tabela_transicao.catalogo,
    )


# ---------------------------------------------------------------------------
# T3 — preparar_turno: decide se chama `rotear()` ou reaproveita o workflow
# persistido na sessao (AD-01, mitigacao de RK-01 -- "nao re-rotear a cada
# turno"). Composicao pura: nenhuma logica de roteamento propria (CA-01).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DecisaoTurno:
    """Resultado de `preparar_turno` -- decisao de roteamento do turno atual.

    Attributes:
        workflow: Workflow ativo para o turno (persistido ou recem-roteado).
        agente_escolhido: Agente que deve atender o turno.
        roteou_novamente: `True` se `governance.rotear` foi chamado neste
            turno (sessao nova ou deriva detectada); `False` quando o
            workflow persistido na sessao foi reaproveitado (AD-01).
        nivel: Nivel da politica de cascata (`DecisaoRota.nivel.value`) usado
            quando `roteou_novamente=True`; `None` quando o turno reaproveitou
            o workflow persistido (T7/PR-7 -- telemetria do span
            `governance.route`).
        score: Score de confianca do roteamento (`DecisaoRota.score`) usado
            quando `roteou_novamente=True`; `None` caso contrario (T7/PR-7).
        drift_detectado: `True` quando o re-roteamento foi causado por deriva
            de intencao (`governance.detectar_deriva`); `False` no turno
            inicial (sessao sem workflow) ou quando nao houve re-roteamento
            (T7/PR-7).
    """

    workflow: governance.Workflow | None
    agente_escolhido: str
    roteou_novamente: bool
    nivel: str | None = None
    score: float | None = None
    drift_detectado: bool = False
    agente_exibido: str | None = None
    """Nome do agente a EXIBIR no badge "Agente Ativo" da UI (ver `routes.py`
    `agui_run`/`sdk_session.stream_chat_ag_ui`). Normalmente identico a
    `agente_escolhido` -- diverge apenas em overrides ou intake."""
    handoff_origem: str | None = None
    """Nome do agente de origem quando houve handoff/transicao neste turno
    (R-042 / `agent-contracts` § 0: `Handoff: <origem> -> <destino>`)."""
    handoff_motivo: str | None = None
    """Motivo do handoff para exibicao transparente no chat (R-042)."""


_SAUDACOES_PURAS: frozenset[str] = frozenset({
    "oi", "ola", "hello", "hi", "hey", "bom dia", "boa tarde", "boa noite",
    "e ai", "fala", "saudacoes", "opa", "salve", "help", "ajuda", "inicio",
    "comecar", "start",
})

_PADRAO_PERGUNTA_ROUTER = re.compile(
    r"^(oi|ola|hello|hi|hey|bom dia|boa tarde|boa noite|opa)?[\s,!?-]*"
    r"("
    r"(o que|oque)\s+(voce|vc)\s+(faz|sabe fazer|pode fazer)"
    r"|como\s+(voce|vc)\s+(funciona|opera)"
    r"|quem\s+e\s+(voce|vc)"
    r"|qual\s+(e\s+o\s+)?seu\s+papel"
    r"|quais\s+(sao\s+os\s+)?agentes"
    r")",
    re.IGNORECASE,
)

_TERMOS_TECNICOS_OU_DEMANDA: frozenset[str] = frozenset({
    "projeto", "codigo", "bug", "erro", "feature", "tela", "banco", "schema",
    "maturidade", "refatorar", "refatoracao", "teste", "testes", "deploy",
    "ci/cd", "pipeline", "service", "componente", "api", "endpoint", "classe",
})


def _normalizar_texto(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.lower().strip()


def eh_intake_ou_saudacao_router(mensagem: str) -> bool:
    """Identifica se a mensagem e uma saudacao ou pergunta geral de intake ao router.

    Mensagens que nao possuem demanda tecnica de desenvolvimento (ex.: "oi",
    "oi, o que vc faz?", "bom dia", "quem e voce?") devem manter o agent-router
    ativo no turno inicial sem abrir prematuramente workflows em especialistas.
    """
    norm = _normalizar_texto(mensagem)
    norm_clean = re.sub(r"[!?,.]+$", "", norm).strip()

    palavras = set(re.findall(r"\b\w+\b", norm_clean))
    if palavras & _TERMOS_TECNICOS_OU_DEMANDA:
        return False

    if norm_clean in _SAUDACOES_PURAS:
        return True
    if _PADRAO_PERGUNTA_ROUTER.search(norm_clean):
        return True
    return False


# Bug real de produção (2026-10-01): mensagens sem NENHUM sinal técnico (ex.:
# pedidos abertos como "faca uma analise") são classificadas `NivelRouting.OUT_OF_DOMAIN`
# por `governance.rotear` (nenhuma keyword casa). O fallback cego de `_escolher_fallback`
# escolhia diretamente um especialista caro -- `tech-solution-architect`.
# `.github/copilot-instructions.md` (R-041) determina o destino correto para
# pedido ambíguo/não-estruturado MID-WORKFLOW (drift detectado a partir de um
# especialista, origem != agent-router): `@prompt-structuring` (etapa 1 de
# `WORKFLOW-PROMPT-SYNTHESIS`), com exibicao de handoff transparente ao usuario.
_WORKFLOW_FALLBACK_AMBIGUO = governance.Workflow.PROMPT_SYNTHESIS
_AGENTE_FALLBACK_AMBIGUO = "prompt-structuring"
# Entry point canônico (routing-graph.yaml `nos[0].id`, `tipo: entry_point`,
# "nunca é destino, apenas origem") -- usado no router intake e em handoffs.
_AGENTE_ROUTER_ID = "agent-router"


def _destino_ambiguo_disponivel(tabela: governance.TabelaTransicao) -> bool:
    """Confirma que `_WORKFLOW_FALLBACK_AMBIGUO`/`_AGENTE_FALLBACK_AMBIGUO`
    existem de fato na `TabelaTransicao` compilada antes de usá-los como
    override (defensivo): fixtures reduzidas de teste (ex.:
    `tests/fixtures/valid_graph.yaml`) podem modelar apenas um subconjunto
    dos 9 workflows canônicos, sem declarar `WORKFLOW-PROMPT-SYNTHESIS` --
    nesse caso o override é pulado e `decisao_rota.escolhido`/`.workflow`
    originais (resolvidos por `_escolher_fallback`) são preservados, evitando
    uma transição de estado inválida (`TransicaoInvalidaError`) contra um
    workflow inexistente naquele grafo.
    """
    etapa_spec = tabela.etapas.get((_WORKFLOW_FALLBACK_AMBIGUO, 1))
    return etapa_spec is not None and _AGENTE_FALLBACK_AMBIGUO in etapa_spec.agent_permitidos


def _resolver_decisao_rota(
    decisao_rota: governance.DecisaoRota,
    tabela: governance.TabelaTransicao,
    *,
    drift_detectado: bool,
    origem_agente: str = _AGENTE_ROUTER_ID,
) -> DecisaoTurno:
    """Converte uma `DecisaoRota` crua em `DecisaoTurno`.

    Bug real de produção (2026-10-02): mensagens de triagem/meta ao próprio
    router (ex.: "qual a sua funcao?") classificadas `OUT_OF_DOMAIN` (nenhuma
    keyword técnica casa) eram sempre forçadas para `prompt-structuring` --
    um especialista NUNCA pedido, divergindo do comportamento do plugin
    Copilot da IDE (onde o próprio modelo, com a persona completa do
    agent-router + tool `run_subagent`, responde diretamente ou delega por
    conta própria). Pesquisa (Tavily, 2026-10-02) confirma o padrão correto:
    Anthropic "Building Effective Agents" (workflow de Routing), OpenAI
    Agents SDK ("Handoffs" representados como tool-call do próprio modelo) e
    a documentação OFICIAL do GitHub Copilot CLI/SDK ("the main agent
    decide[s] when to delegate... reading each agent's description field")
    convergem: quando o classificador determinístico NÃO tem confiança
    suficiente (`OUT_OF_DOMAIN`) NO TURNO INICIAL (`origem_agente ==
    agent-router`), a decisão correta é NÃO adivinhar um especialista fixo
    -- é permanecer no `agent-router`, deixando o MODELO REAL (persona +
    `run_subagent` + catálogo de `custom_agents`, já wireados em
    `sdk_session.py`/RT-04) decidir se/para onde delegar, exatamente como no
    plugin oficial.

    O fallback histórico para `prompt-structuring` é preservado APENAS para
    o caso mid-workflow (`origem_agente != agent-router`, i.e. deriva de
    intenção detectada a partir de um especialista já ativo sem uma
    reclassificação confiável) -- retornar ao `agent-router` nesse ponto
    exigiria modelar uma transição de "abort" ainda não coberta pela máquina
    de estados R-050, fora de escopo desta correção cirúrgica.
    """
    if decisao_rota.nivel is governance.NivelRouting.OUT_OF_DOMAIN:
        if origem_agente == _AGENTE_ROUTER_ID:
            return DecisaoTurno(
                workflow=None,
                agente_escolhido=_AGENTE_ROUTER_ID,
                roteou_novamente=False,
                nivel=decisao_rota.nivel.value,
                score=decisao_rota.score,
                drift_detectado=drift_detectado,
                agente_exibido=_AGENTE_ROUTER_ID,
                handoff_origem=None,
                handoff_motivo=None,
            )
        if _destino_ambiguo_disponivel(tabela):
            handoff_origem = origem_agente if origem_agente != _AGENTE_FALLBACK_AMBIGUO else None
            handoff_motivo = (
                "solicitação ampla ou aberta — refinamento estruturado de prompt"
                if handoff_origem
                else None
            )
            return DecisaoTurno(
                workflow=_WORKFLOW_FALLBACK_AMBIGUO,
                agente_escolhido=_AGENTE_FALLBACK_AMBIGUO,
                roteou_novamente=True,
                nivel=decisao_rota.nivel.value,
                score=decisao_rota.score,
                drift_detectado=drift_detectado,
                agente_exibido=_AGENTE_FALLBACK_AMBIGUO,
                handoff_origem=handoff_origem,
                handoff_motivo=handoff_motivo,
            )

    handoff_origem = origem_agente if origem_agente != decisao_rota.escolhido else None
    handoff_motivo = None
    if handoff_origem:
        if drift_detectado:
            handoff_motivo = "deriva de intenção detectada"
        elif origem_agente == _AGENTE_ROUTER_ID:
            handoff_motivo = f"triagem inicial — delegação para {decisao_rota.escolhido}"
        else:
            handoff_motivo = f"handoff para {decisao_rota.escolhido}"

    return DecisaoTurno(
        workflow=decisao_rota.workflow,
        agente_escolhido=decisao_rota.escolhido,
        roteou_novamente=True,
        nivel=decisao_rota.nivel.value,
        score=decisao_rota.score,
        drift_detectado=drift_detectado,
        agente_exibido=decisao_rota.escolhido,
        handoff_origem=handoff_origem,
        handoff_motivo=handoff_motivo,
    )


def preparar_turno(
    sessao: governance.Sessao,
    mensagem: str,
    grafo: Any,
    tabela: governance.TabelaTransicao,
) -> DecisaoTurno:
    """Decide se o turno atual exige novo roteamento ou reaproveita a sessao.

    Regra (AD-01, RK-01): `governance.rotear` so e chamado quando a
    `Sessao` ainda nao tem `workflow` definido (turno inicial) OU quando
    `governance.detectar_deriva` sinaliza deriva de intencao explicita.
    Nos demais turnos, o workflow/agente ja persistidos na sessao sao
    reaproveitados sem reinvocar o roteador (evita sticky-agent quebrado
    por re-roteamento a cada mensagem).

    Se a mensagem no router for uma saudacao ou intake inicial (ex.: "oi",
    "oi, o que vc faz?"), o agent-router responde sem transicionar para
    nenhum workflow, permanecendo em Fase.ROUTER.

    Args:
        sessao: Estado imutavel da sessao de governanca no turno atual.
        mensagem: Texto bruto do turno do usuario (input do roteador/deriva).
        grafo: Grafo dirigido compilado (`governance.carregar_grafo`),
            tipado como `Any` pelo mesmo motivo documentado em
            `ContextoGovernanca.grafo`.
        tabela: `TabelaTransicao` compilada, cujo `.catalogo` alimenta
            `governance.detectar_deriva`.

    Returns:
        DecisaoTurno: workflow/agente a usar neste turno e se houve
        re-roteamento.
    """
    if sessao.workflow is None:
        if eh_intake_ou_saudacao_router(mensagem):
            return DecisaoTurno(
                workflow=None,
                agente_escolhido=_AGENTE_ROUTER_ID,
                roteou_novamente=False,
                nivel="router_intake",
                score=1.0,
                drift_detectado=False,
                agente_exibido=_AGENTE_ROUTER_ID,
                handoff_origem=None,
                handoff_motivo=None,
            )
        decisao_rota = governance.rotear(mensagem, grafo)
        return _resolver_decisao_rota(
            decisao_rota,
            tabela,
            drift_detectado=False,
            origem_agente=sessao.agente_ativo or _AGENTE_ROUTER_ID,
        )

    turno = governance.Turno(texto=mensagem)
    deriva = governance.detectar_deriva(sessao, turno, tabela.catalogo)
    if deriva.houve:
        decisao_rota = governance.rotear(mensagem, grafo)
        return _resolver_decisao_rota(
            decisao_rota,
            tabela,
            drift_detectado=True,
            origem_agente=sessao.agente_ativo,
        )

    return DecisaoTurno(
        workflow=sessao.workflow,
        agente_escolhido=sessao.agente_ativo,
        roteou_novamente=False,
        nivel=None,
        score=None,
        drift_detectado=False,
        agente_exibido=sessao.agente_ativo,
    )


# ---------------------------------------------------------------------------
# T3 — avaliar_transicao: wrapper fino e nao-excecional sobre
# `governance.transicionar`, para `routes.py` (T6) decidir a resposta HTTP
# controlada sem try/except espalhado (CA-05).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResultadoTransicao:
    """Resultado tipado (nao-excecional) de `avaliar_transicao`.

    Attributes:
        sucesso: `True` se `governance.transicionar` concluiu sem levantar
            `TransicaoInvalidaError`.
        sessao_atualizada: Nova `Sessao` apos a transicao, ou `None` em
            caso de falha.
        erro: Mensagem de `TransicaoInvalidaError` capturada, ou `None`
            em caso de sucesso.
        erro_tipo: Nome da classe da excecao capturada (ex.:
            `"TransicaoInvalidaError"`), ou `None` em caso de sucesso
            (T7/PR-7 -- atributo `error.type` do span
            `governance.workflow_transition`).
    """

    sucesso: bool
    sessao_atualizada: governance.Sessao | None
    erro: str | None
    erro_tipo: str | None = None


def avaliar_transicao(
    sessao: governance.Sessao,
    evento: governance.Evento,
    tabela: governance.TabelaTransicao,
) -> ResultadoTransicao:
    """Avalia uma transicao de estado sem propagar excecao ao chamador.

    Captura `governance.TransicaoInvalidaError` e converte em um
    `ResultadoTransicao` tipado, permitindo que `routes.py` decida a
    resposta HTTP controlada (sempre 200 com texto, nunca 500) sem
    try/except espalhado pelos handlers.

    Args:
        sessao: Estado atual da sessao de governanca.
        evento: Evento de entrada que dispara a tentativa de transicao.
        tabela: `TabelaTransicao` compilada usada para validar a transicao.

    Returns:
        ResultadoTransicao: `sucesso=True` com `sessao_atualizada`
        preenchida, ou `sucesso=False` com `erro` preenchido.
    """
    try:
        nova_sessao = governance.transicionar(sessao, evento, tabela)
    except governance.TransicaoInvalidaError as exc:
        return ResultadoTransicao(
            sucesso=False,
            sessao_atualizada=None,
            erro=str(exc),
            erro_tipo=type(exc).__name__,
        )
    return ResultadoTransicao(
        sucesso=True, sessao_atualizada=nova_sessao, erro=None, erro_tipo=None
    )


# ---------------------------------------------------------------------------
# T3 — montar_contexto: injecao explicita e deterministica de contexto
# `.github/` (allowlist fixa -- Secao 4 do Plano de Planejamento). NUNCA lê
# `.github/hooks/` (RK-03).
# ---------------------------------------------------------------------------


def _ler_arquivo_real(caminho: Path) -> str:
    """Leitor de arquivo real (default de `montar_contexto`).

    Args:
        caminho: Caminho absoluto do arquivo Markdown a ler.

    Returns:
        str: Conteudo UTF-8 do arquivo.
    """
    return caminho.read_text(encoding="utf-8")


def _caminho_contexto_seguro(caminho: Path, github_dir: Path) -> bool:
    """Guarda de allowlist: `caminho` deve resolver dentro de `github_dir` e
    nunca conter o segmento `hooks` (RK-03), reaproveitando o mesmo padrao
    de path traversal seguro de `sdk_session._caminho_escrita_seguro` /
    `permission_policy._caminho_permitido`.

    Args:
        caminho: Caminho candidato (ainda nao lido) a validar.
        github_dir: Raiz de `.github/` efetivamente usada nesta chamada
            (settings.governance_github_dir em producao, ou `_GITHUB_DIR`
            como fallback de ultimo recurso -- ver `montar_contexto`).

    Returns:
        bool: `True` se o caminho e seguro para leitura via allowlist.
    """
    resolvido = caminho.resolve()
    try:
        resolvido.relative_to(github_dir.resolve())
    except ValueError:
        return False
    if _SEGMENTO_PROIBIDO in resolvido.parts:
        return False
    return True


def _ler_artefato_allowlist(
    caminho: Path, leitor_arquivo: Callable[[Path], str], github_dir: Path
) -> str:
    """Le um artefato da allowlist `.github/` se e somente se for seguro.

    Args:
        caminho: Caminho candidato do artefato (persona ou nucleo).
        leitor_arquivo: Funcao injetavel de leitura (produção ou mock).
        github_dir: Raiz de `.github/` efetivamente usada nesta chamada.

    Returns:
        str: Conteudo lido, ou string vazia se o caminho for bloqueado pela
        allowlist (RK-03) ou o arquivo nao existir.
    """
    if not _caminho_contexto_seguro(caminho, github_dir):
        logger.warning(
            "montar_contexto: caminho bloqueado pela allowlist (RK-03): %s", caminho
        )
        return ""
    try:
        return leitor_arquivo(caminho)
    except FileNotFoundError:
        logger.warning("montar_contexto: artefato nao encontrado: %s", caminho)
        return ""


def montar_contexto(
    agente: str,
    workflow: governance.Workflow | str | None,
    etapa: int,
    leitor_arquivo: Callable[[Path], str] | None = None,
    github_dir: Path | None = None,
) -> str:
    """Monta o `system_message` injetavel via allowlist deterministica.

    Allowlist fixa (Secao 4 do Plano de Planejamento):
        1. `.github/agents/<agente>.agent.md` (persona do agente).
        2. `.github/copilot-instructions.md` (nucleo).

    Banner R-042 sempre presente no inicio do retorno:
        `Agente Ativo: <agente>\n[WORKFLOW: <workflow> / ETAPA: <etapa>]\n\n`

    Orcamento de bytes: o resultado e truncado em 32 KB (UTF-8), com
    marcador de truncamento explicito ao final.

    Limitacao documentada (RK-02): nesta etapa (T3), as skills referenciadas
    no frontmatter `skills:` do `.agent.md` NAO sao incluidas -- apenas a
    persona + nucleo. Incluir skills fica para uma subtask futura, se o
    orcamento/tempo permitir.

    RK-03 (critico): `.github/hooks/` NUNCA e lido -- `_caminho_contexto_seguro`
    bloqueia qualquer caminho resolvido cujo segmento contenha `hooks` antes
    de qualquer chamada a `leitor_arquivo`.

    Bug real de producao (2026-10-01, Addendum 5): `github_dir` existe
    precisamente porque o antigo default `_GITHUB_DIR` (calculado de
    `Path(__file__).resolve().parents[4]`) resolve para o local de
    INSTALACAO do pacote -- correto em dev local (instalacao editavel), mas
    incorreto dentro do container Docker (`/usr/local/lib/python3.12/
    site-packages/...` em vez do volume real `/governance:ro`). Chamadores
    de producao (`routes.py`) DEVEM propagar `settings.governance_github_dir`
    explicitamente; o fallback para `_GITHUB_DIR` existe apenas para
    compatibilidade com chamadas antigas/testes que nao fornecem o parametro.

    Args:
        agente: Identificador do agente ativo (ex.: `python-feature-developer`).
        workflow: Workflow ativo (enum `governance.Workflow` ou `str`), ou
            `None` se a sessao ainda estiver no router.
        etapa: Numero da etapa atual dentro do workflow.
        leitor_arquivo: Funcao injetavel `Callable[[Path], str]` usada para
            ler cada artefato da allowlist; se omitida, usa leitura real de
            arquivo (`Path.read_text`). Permite mock em testes sem tocar o
            filesystem real.
        github_dir: Raiz de `.github/` a usar nesta chamada (ex.:
            `/governance/.github` dentro do container). Se omitido, usa o
            fallback `_GITHUB_DIR` (apenas para compatibilidade retroativa).

    Returns:
        str: `system_message` pronto para injecao via `stream_chat`, com
        banner + persona + nucleo, truncado em 32 KB se necessario.
    """
    leitor = leitor_arquivo if leitor_arquivo is not None else _ler_arquivo_real
    base_github = github_dir if github_dir is not None else _GITHUB_DIR

    banner = f"Agente Ativo: {agente}\n[WORKFLOW: {workflow} / ETAPA: {etapa}]\n\n"

    # Nota especifica deste gateway headless (incidente real investigado
    # 2026-10-04): a governanca universal (`agent-router.agent.md` e
    # `copilot-instructions.md`, escritos para o plugin REAL da IDE)
    # instrui o "Orquestrador Raiz" a despachar a Delegacao Plana via UMA
    # chamada de `run_subagent` apos a decisao do router. No VS Code/
    # JetBrains real isso funciona porque o orquestrador da IDE tem
    # mecanismo proprio de delegacao com tools completas. Neste SDK
    # headless, porem, qualquer invocacao de agent NESTED (mid-turn, via
    # tool nativa `task` -- presente em `copilot.BUILTIN_TOOLS_ISOLATED`
    # e SEMPRE disponivel, independente do `tools:` configurado por
    # agent) resulta em toolset RESTRITO para o agent delegado (confirmado
    # em producao: `pr-gatekeeper` relatou ter apenas `grep`/`file_search`
    # quando invocado assim, 0 tool calls, retorno imediato). Isso NAO e
    # falta de ferramentas -- e uma limitacao arquitetural do mecanismo de
    # sub-tarefa do SDK. Instrucao valida APENAS para este ambiente:
    _NOTA_GATEWAY_HEADLESS = (
        "\n> ⚠️ **Nota especifica deste ambiente (gateway headless, nao a "
        "IDE)**: NUNCA use `run_subagent`/a tool nativa `task` para "
        "despachar a Delegacao Plana apos a decisao do router. Isso "
        "resulta em toolset RESTRITO (confirmado: apenas grep/busca) para "
        "o agent delegado, nao falta real de permissao. Em vez disso, "
        "apenas emita o bloco de decisao textual (`Agente Ativo`/"
        "`Delegado: @<agent>`) e PARE -- este gateway roteia "
        "automaticamente o PROXIMO turno para o agent escolhido, com "
        "acesso total as tools configuradas. Se precisar executar "
        "`git`/terminal voce mesmo (como `pr-gatekeeper`), use "
        "`run_in_terminal` diretamente -- nunca delegue para "
        "testar/confirmar o que voce mesmo ja pode executar.\n\n"
    )
    partes_iniciais = [banner, _NOTA_GATEWAY_HEADLESS]

    caminho_persona = base_github / "agents" / f"{agente}.agent.md"
    caminho_nucleo = base_github / "copilot-instructions.md"

    partes = list(partes_iniciais)
    for caminho in (caminho_persona, caminho_nucleo):
        conteudo = _ler_artefato_allowlist(caminho, leitor, base_github)
        if conteudo:
            partes.append(conteudo)
            partes.append("\n\n")

    texto = "".join(partes)
    return _truncar_por_orcamento(texto)


def _truncar_por_orcamento(texto: str) -> str:
    """Trunca `texto` em `_ORCAMENTO_BYTES_CONTEXTO` bytes UTF-8.

    Args:
        texto: Texto completo (banner + artefatos concatenados).

    Returns:
        str: `texto` inalterado se couber no orcamento, ou a versao truncada
        com `_MARCADOR_TRUNCAMENTO` ao final.
    """
    codificado = texto.encode("utf-8")
    if len(codificado) <= _ORCAMENTO_BYTES_CONTEXTO:
        return texto

    marcador_bytes = _MARCADOR_TRUNCAMENTO.encode("utf-8")
    limite = max(_ORCAMENTO_BYTES_CONTEXTO - len(marcador_bytes), 0)
    truncado = codificado[:limite].decode("utf-8", errors="ignore")
    return truncado + _MARCADOR_TRUNCAMENTO
