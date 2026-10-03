"""agent_catalog — descoberta de custom agents (`.github/agents/**/*.agent.md`)
para wiring manual no Copilot SDK real via `custom_agents=` (RT-04).

Contexto (pesquisa externa, 2026-10-01): o GitHub Copilot SDK NAO descobre
automaticamente `.github/agents/*.agent.md` mesmo com
`enable_config_discovery=True` -- confirmado pela issue oficial do
mantenedor (github/copilot-sdk#1080, "Support discovering
.github/agents/*.agent.md via enableConfigDiscovery", em aberto). A
abordagem oficialmente documentada como workaround e fazer o parsing
manual (glob + YAML frontmatter) e repassar via `custom_agents=` no
`create_session(...)` -- exatamente o que este modulo implementa.

Bug real de producao confirmado por teste ao vivo (2026-10-01, via
curl contra o gateway real com token real): sem este modulo, o modelo
respondia literalmente "I don't have access to tools like ... run_subagent
... I'm GitHub Copilot and only use the tools actually available to me
(bash, grep, view, edit, etc.)" -- ou seja, o banner de governanca
injetado via `system_message` (texto puro) NUNCA concedeu a tool
`run_subagent`; sem `custom_agents` explicito, nao ha catalogo para
delegar e a tool fica efetivamente inerte.

Isto e DELIBERADAMENTE distinto de `enable_file_hooks`
(`.github/hooks/*.json`, comandos de SHELL executados em pontos do ciclo
de vida da sessao -- docs oficiais: "File hooks run commands as the user
that runs your application. They aren't gated by on_permission_request
or other tool-approval callbacks"). Este gateway mantem
`enable_file_hooks=False` deliberadamente (ver `sdk_session.py`):
`custom_agents` resolve o caso de uso real (orquestracao multi-agent via
`run_subagent`, paridade com o plugin da IDE) sem reintroduzir o vetor
de risco de execucao de shell nao gated por permissao.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, TypedDict

import yaml

logger = logging.getLogger(__name__)

# Orcamento de bytes por agent (mesmo padrao de `governance_pipeline.
# montar_contexto`) -- evita que um unico `.agent.md` anormalmente grande
# estoure o payload de `create_session(custom_agents=[...])`.
#
# Bug real investigado (2026-10-04): o valor original de 16 KiB truncava
# SILENCIOSAMENTE (sem nenhum log) 9 dos 95 agents reais do catalogo --
# incluindo o proprio `agent-router.agent.md` (49 999 bytes, 67% do conteudo
# descartado) e `pr-gatekeeper.agent.md` (28 647 bytes, 43% descartado,
# cortando justamente a secao "Anti-padroes" e "Quando Delegar" apos uma
# correcao aplicada para o incidente de cascata de subagents fantasmas --
# ver `terminal-governance/SKILL.md` § 5.3). O maior agent real hoje
# (`agent-router.agent.md`) tem 48.8 KiB; o novo orcamento cobre 100% dos
# 95 agents atuais com ~25% de margem, somando ~1 MiB de payload total
# (vs. os 1005.6 KiB reais sem nenhum corte) -- aceitavel para
# `create_session(custom_agents=[...])`, sem limite documentado da SDK que
# justifique um teto tao agressivo quanto 16 KiB.
_ORCAMENTO_BYTES_PROMPT = 64 * 1024
_MARCADOR_TRUNCAMENTO = "\n[... truncado por orcamento de contexto ...]"
_ORCAMENTO_BYTES_DESCRICAO = 500

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)

# Bug real confirmado por introspecao ao vivo da wheel `github_copilot_sdk
# ==1.0.16` (2026-10-02): a tool NATIVA do SDK headless para pergunta
# estruturada ao usuario e `ask_user` (`copilot.BUILTIN_TOOLS_ISOLATED`
# contem literalmente `['ask_user', 'task_complete', 'exit_plan_mode',
# 'task', 'read_agent', 'write_agent', 'list_agents', 'send_inbox',
# 'context_board', 'skill']` -- NUNCA `ask_questions`). Todo `.agent.md`
# deste repositorio de governanca declara `ask_questions` em `tools:`
# (nome convencional do catalogo de tools do PLUGIN da IDE — VSCode/
# JetBrains Copilot Chat), nome que o SDK headless simplesmente nao
# reconhece. Resultado observado em teste ao vivo: a allowlist de tools
# do custom agent (`CustomAgentConfig["tools"]`) continha uma entrada
# que nao correspondia a NENHUMA tool real, entao o modelo respondia
# literalmente "Não tenho `ask_questions` disponível nesta sessão" e
# perguntava em texto puro -- mesmo com `ask_user_variant="elicitation"`
# e `on_elicitation_request` corretamente wireados em `sdk_session.py`.
# Este alias traduz o nome convencional da IDE para o nome real do SDK
# headless SEM exigir editar os ~100+ arquivos `.agent.md` do catalogo
# (que permanecem corretos para consumo pelo PLUGIN real da IDE).
#: Mapa de alias de tools de IDE (nomes convencionais usados nos prompts dos
#: ~100+ `.agent.md`) -> nomes NATIVOS do SDK headless `github-copilot-sdk==
#: 1.0.16` (bash, powershell, shell, grep, create, str_replace_editor, task,
#: web_fetch, ask_user). Tools SEM equivalente nativo no SDK (ex.: MCP tools
#: `mcp_context-mode_*`, `mcp_tavily_*`, `mcp_codegraph_*`) NAO entram aqui --
#: essas sao resolvidas via `mcp_servers=` em `sdk_session.create_session`
#: (RC2) e permanecem com o NOME ORIGINAL (o SDK roteia pelo nome do MCP
#: tool registrado pelo proprio servidor, nao por este alias estatico).
_ALIAS_TOOLS_SDK_HEADLESS: dict[str, str] = {
    "ask_questions": "ask_user",
    "read_file": "str_replace_editor",
    "insert_edit_into_file": "str_replace_editor",
    "replace_string_in_file": "str_replace_editor",
    "create_file": "create",
    "grep_search": "grep",
    "web_search": "web_fetch",
    "fetch_webpage": "web_fetch",
    # "run_in_terminal" e DELIBERADAMENTE OMITIDO deste mapa estatico -- ver
    # `_agent_autorizado_para_shell_nativo` abaixo (Security Checkpoint,
    # Risco #1: allowlist deny-by-default, nao liberacao global).
    #
    # "run_subagent" -> "task" foi REMOVIDO deste mapa (bug real investigado
    # 2026-10-04): a tool nativa `task` do SDK e um spawner GENERICO de
    # sub-tarefa (aceita qualquer `agent_name`/label livre escolhido pelo
    # proprio modelo, SEM validacao contra `custom_agents`), nao um
    # mecanismo de delegacao para um agent NOMEADO e existente do catalogo
    # -- confirmado por evidencia real de producao: toda invocacao aninhada
    # de `run_subagent` resolvia para `agent_name=task`/`general-purpose`
    # com um modelo auxiliar PROPRIO (`gpt-5.6-luna`/`gpt-5.4`, nunca o
    # modelo do agent real), gerando cascatas recursivas de "subagents
    # fantasmas" (`git-readonly-check`, `coleta-git-status`, etc.) --
    # observado ate 8 invocacoes encadeadas (~175 mil tokens, ~2 min) so
    # para confirmar 3 comandos git read-only triviais que o agent de
    # origem ja tinha permissao de executar via `run_in_terminal`. Em um
    # caso, a sub-tarefa `task` chegou a responder "Please provide the task
    # or command you'd like me to execute" -- evidencia de que o schema de
    # argumentos de `run_subagent` (IDE) nao e compativel com o schema
    # nativo de `task` (SDK), so o NOME da tool era traduzido, nao os
    # argumentos. O handoff real entre agents (R-042, banner "Handoff: X ->
    # Y") NAO depende desta tool -- e decidido por `routes.py`/
    # `governance_pipeline` a cada novo turno (parsing de texto + estado de
    # sessao persistido), entao remover este alias nao quebra delegacao
    # legitima entre turnos. Com o alias removido, `run_subagent` permanece
    # SEM TRADUCAO (nome literal, nao reconhecido pelo SDK) e portanto fica
    # INERTE -- restaura o comportamento documentado como aceitavel ANTES
    # de `custom_agents` existir ("sessao sem delegacao de subagent
    # disponivel", ver docstring de `sdk_session.stream_chat`), forcando o
    # modelo a usar `run_in_terminal`/tools reais diretamente em vez de
    # tentar "delegar para testar".
}

#: Nomes de tool de IDE que representam execucao de shell real -- so podem
#: ser traduzidos para a tool nativa do SDK (`bash`/`powershell`/`shell`)
#: quando o agent de origem estiver na allowlist (ver
#: `_agent_autorizado_para_shell_nativo`). Fora da allowlist, a tool e
#: OMITIDA da lista final (nao e passada ao modelo) -- deny-by-default.
_TOOLS_SHELL_NATIVAS: dict[str, str] = {
    "run_in_terminal": "bash",
}

#: Skill cuja presenca em `source_docs:` do frontmatter autoriza o agent a
#: usar tools de shell nativas (regra fixada pelo Security Checkpoint,
#: Risco #1 -- nao e uma liberacao global para os ~100+ agents).
_SKILL_TERMINAL_GOVERNANCE = "terminal-governance"


def _agent_autorizado_para_shell_nativo(frontmatter: dict[str, Any]) -> bool:
    """Allowlist deny-by-default p/ tools de shell real (bash/powershell/shell).

    Autoriza SOMENTE quando AMBOS os sinais do frontmatter estao presentes:
      1. `tools:` ja declarava `run_in_terminal` explicitamente; e
      2. `source_docs:` referencia a skill `terminal-governance`
         (R-049).

    Agents puramente consultivos (`*-arch-advisor`, `agent-router`,
    `governance-maintainer`) mencionam `run_in_terminal` apenas para
    PROIBI-LO no corpo do prompt e NAO vinculam `terminal-governance` em
    `source_docs:` -- ficam corretamente FORA da allowlist.
    """
    tools = frontmatter.get("tools")
    declara_run_in_terminal = isinstance(tools, list) and "run_in_terminal" in tools
    source_docs = frontmatter.get("source_docs")
    vincula_skill = isinstance(source_docs, list) and any(
        _SKILL_TERMINAL_GOVERNANCE in str(s) for s in source_docs
    )
    return declara_run_in_terminal and vincula_skill


def _traduzir_tools_para_sdk_headless(
    tools_brutas: list[Any], *, frontmatter: dict[str, Any] | None = None
) -> list[str]:
    """Aplica `_ALIAS_TOOLS_SDK_HEADLESS` preservando ordem e sem duplicatas.

    Tools de shell real (`run_in_terminal`) so sao traduzidas para a tool
    nativa do SDK quando `frontmatter` passa por
    `_agent_autorizado_para_shell_nativo` (deny-by-default, Security
    Checkpoint Risco #1); caso contrario, a entrada e OMITIDA da lista
    final (nunca repassada ao modelo "as cegas").

    Args:
        tools_brutas: Lista crua de `frontmatter["tools"]` (nomes convencionais
            da IDE, ex.: `["read_file", "ask_questions", "run_subagent"]`).
        frontmatter: Frontmatter completo do `.agent.md` (usado apenas para
            resolver a allowlist de shell nativo). Se `None`, nenhuma tool de
            shell real e liberada (fail-closed).

    Returns:
        list[str]: nomes traduzidos para o vocabulario do SDK headless
        (ex.: `["read_file", "ask_user", "run_subagent"]`), sem repetir um
        nome ja presente (caso o `.agent.md` declare as duas formas).
    """
    autorizado_shell = frontmatter is not None and _agent_autorizado_para_shell_nativo(
        frontmatter
    )
    traduzidas: list[str] = []
    for t in tools_brutas:
        bruto = str(t)
        if bruto in _TOOLS_SHELL_NATIVAS:
            if not autorizado_shell:
                continue  # deny-by-default: omite a tool, nao repassa crua
            nome = _TOOLS_SHELL_NATIVAS[bruto]
        else:
            nome = _ALIAS_TOOLS_SDK_HEADLESS.get(bruto, bruto)
        if nome not in traduzidas:
            traduzidas.append(nome)
    return traduzidas


class CustomAgentConfig(TypedDict, total=False):
    """Espelho tipado minimo de `copilot.session.CustomAgentConfig` (RT-04).

    Campos confirmados por introspecao real de `copilot/session.py` na
    wheel `github_copilot_sdk==1.0.15`: `name` e `prompt` sao os unicos
    obrigatorios; os demais sao `NotRequired`.
    """

    name: str
    display_name: str
    description: str
    tools: list[str] | None
    prompt: str
    infer: bool
    model: str


def _parse_frontmatter(texto: str) -> tuple[dict[str, Any], str]:
    """Separa frontmatter YAML (`--- ... ---`) do corpo Markdown restante.

    Args:
        texto: Conteudo bruto UTF-8 do arquivo `.agent.md`.

    Returns:
        tuple[dict, str]: `(frontmatter_parseado, corpo_markdown)`. Se nao
        houver frontmatter valido (ou o parsing YAML falhar), retorna
        `({}, texto)` inalterado -- nunca propaga excecao.
    """
    match = _FRONTMATTER_RE.match(texto)
    if not match:
        return {}, texto
    bruto_frontmatter, corpo = match.groups()
    try:
        frontmatter = yaml.safe_load(bruto_frontmatter) or {}
    except yaml.YAMLError as exc:
        logger.warning("agent_catalog: frontmatter invalido ignorado: %s", exc)
        return {}, texto
    if not isinstance(frontmatter, dict):
        return {}, texto
    return frontmatter, corpo


def _truncar(texto: str, orcamento_bytes: int, marcador: str) -> str:
    """Trunca `texto` em `orcamento_bytes` UTF-8, preservando corte seguro."""
    codificado = texto.encode("utf-8")
    if len(codificado) <= orcamento_bytes:
        return texto
    marcador_bytes = marcador.encode("utf-8")
    limite = max(orcamento_bytes - len(marcador_bytes), 0)
    return codificado[:limite].decode("utf-8", errors="ignore") + marcador


def _agent_de_arquivo(caminho: Path, leitor_arquivo: Any) -> CustomAgentConfig | None:
    """Converte um unico `.agent.md` em `CustomAgentConfig`, ou `None` se invalido.

    Args:
        caminho: Caminho absoluto do arquivo `.agent.md`.
        leitor_arquivo: `Callable[[Path], str]` injetavel (produção ou mock).

    Returns:
        CustomAgentConfig | None: `None` quando o arquivo nao pode ser lido
        ou nao possui `name` valido no frontmatter (ignorado silenciosamente
        com log de warning -- nunca derruba o carregamento dos demais).
    """
    try:
        texto = leitor_arquivo(caminho)
    except OSError as exc:
        logger.warning("agent_catalog: falha ao ler %s: %s", caminho, exc)
        return None

    frontmatter, corpo = _parse_frontmatter(texto)
    nome = str(frontmatter.get("name") or "").strip()
    if not nome:
        logger.warning(
            "agent_catalog: '%s' sem 'name' valido no frontmatter — ignorado", caminho
        )
        return None

    corpo_bruto = corpo.strip()
    corpo_truncado = _truncar(
        corpo_bruto, _ORCAMENTO_BYTES_PROMPT, _MARCADOR_TRUNCAMENTO
    )
    if len(corpo_bruto.encode("utf-8")) > _ORCAMENTO_BYTES_PROMPT:
        logger.warning(
            "agent_catalog: '%s' TRUNCADO de %d para %d bytes (orcamento=%d) "
            "-- conteudo apos o corte NUNCA chega ao modelo",
            caminho,
            len(corpo_bruto.encode("utf-8")),
            len(corpo_truncado.encode("utf-8")),
            _ORCAMENTO_BYTES_PROMPT,
        )
    if not corpo_truncado:
        logger.warning("agent_catalog: '%s' sem corpo (prompt) — ignorado", caminho)
        return None

    config: CustomAgentConfig = {
        "name": nome,
        "description": str(frontmatter.get("description") or "")[
            :_ORCAMENTO_BYTES_DESCRICAO
        ],
        "prompt": corpo_truncado,
        "infer": True,
    }
    modelo = frontmatter.get("model")
    if isinstance(modelo, str) and modelo.strip():
        config["model"] = modelo.strip()
    tools = frontmatter.get("tools")
    if isinstance(tools, list):
        config["tools"] = _traduzir_tools_para_sdk_headless(
            tools, frontmatter=frontmatter
        )
    display_name = frontmatter.get("display_name")
    if isinstance(display_name, str) and display_name.strip():
        config["display_name"] = display_name.strip()

    return config


def descobrir_custom_agents(
    agents_dir: Path, *, leitor_arquivo: Any | None = None
) -> list[CustomAgentConfig]:
    """Descobre e parseia `.github/agents/**/*.agent.md` em `CustomAgentConfig`.

    NUNCA le `.github/hooks/` -- o glob e restrito ao diretorio `agents_dir`
    (tipicamente `<governance_github_dir>/agents`), um irmao de `hooks/`,
    nao um ancestral; nao ha superposicao de caminho possivel (RK-03
    continua sendo responsabilidade exclusiva de
    `governance_pipeline.montar_contexto`, que le arquivos individuais por
    allowlist, nao faz `rglob`).

    Args:
        agents_dir: Diretorio raiz de agents (ex.: `/governance/.github/agents`).
        leitor_arquivo: Funcao injetavel `Callable[[Path], str]` para leitura
            de cada arquivo; se omitida, usa `Path.read_text` real. Permite
            mock em testes sem tocar o filesystem.

    Returns:
        list[CustomAgentConfig]: catalogo ordenado deterministicamente
        (ordem alfabetica de caminho), com nomes duplicados descartados
        (mantendo a primeira ocorrencia) e arquivos invalidos ignorados.
    """
    leitor = (
        leitor_arquivo
        if leitor_arquivo is not None
        else (lambda p: p.read_text(encoding="utf-8"))
    )

    if not agents_dir.is_dir():
        logger.warning("agent_catalog: diretorio nao encontrado: %s", agents_dir)
        return []

    agentes: list[CustomAgentConfig] = []
    nomes_vistos: set[str] = set()
    for caminho in sorted(agents_dir.rglob("*.agent.md")):
        agente = _agent_de_arquivo(caminho, leitor)
        if agente is None:
            continue
        nome = agente["name"]
        if nome in nomes_vistos:
            logger.warning(
                "agent_catalog: nome duplicado ignorado: %s (%s)", nome, caminho
            )
            continue
        nomes_vistos.add(nome)
        agentes.append(agente)

    logger.info(
        "agent_catalog: %d custom agents descobertos em %s", len(agentes), agents_dir
    )
    return agentes
