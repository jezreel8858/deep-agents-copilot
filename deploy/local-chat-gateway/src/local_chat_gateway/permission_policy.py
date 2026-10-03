"""permission_policy — stub read_only/propose/apply + 4 guardas de escrita.

Contrato (BLUEPRINT_LOCAL_CHAT_GATEWAY.md Secao 6). Composto AO LADO do
handler read-only ja existente em `governance_runner.runner.sdk_adapter`
(`construir_permission_handler_read_only`) — nunca o altera.

Nome explicito `PermissionPolicyStub` (R-CODE-06): esta e uma
implementacao de MVP/fase 1, sem integracao real com o SDK do Copilot
ainda (bloqueado por RT-01). Nao deve ser interpretada como a politica de
seguranca final de producao.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from local_chat_gateway.governance import (
    Catalogo,
    Evento,
    Sessao,
    TabelaTransicao,
    TransicaoInvalidaError,
    detectar_deriva,
    transicionar,
)

# Segmentos/sufixos de caminho categoricamente bloqueados para escrita em
# modo "apply" (guarda 4), mesmo dentro do workspace montado.
_BLOCKED_PATH_SEGMENTS: tuple[str, ...] = (".git", "secrets")
_BLOCKED_SUFFIXES: tuple[str, ...] = (".pem",)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bug real corrigido (2026-10-02): tools que NAO sao `PermissionRequestWrite`
# nativo (ex.: Shell/CustomTool de `run_in_terminal`, MCP `context-mode/
# ctx_execute`) eram negadas por `routes._conservative_permission_handler`
# independentemente de `GATEWAY_PERMISSION_MODE=apply` -- o modo so afetava
# escritas de arquivo. Resultado reportado ao vivo: o agent `pr-gatekeeper`
# (que so precisa de `git --no-pager status/diff/log` READ-ONLY para montar
# a mensagem de commit/PR, nunca `git commit`/`git push` -- R-031) recebia
# "Negado pela politica local (GATEWAY_PERMISSION_MODE)." mesmo em modo
# `apply`. Esta secao centraliza (R-055 anti-silo) a heuristica de
# comando/tool seguro reaproveitada por TODOS os handlers de permissao do
# gateway (`routes._conservative_permission_handler` e
# `routes._governance_permission_handler`), nao apenas pelo caminho de
# `pr-gatekeeper`.
# ---------------------------------------------------------------------------

#: Prefixos de nome de tool tratados como leitura incondicional (paridade
#: com `routes._READ_ONLY_TOOL_PREFIXES`, movido para ca como fonte unica).
READ_ONLY_TOOL_PREFIXES: tuple[str, ...] = (
    "read_",
    "ler_",
    "grep_",
    "list_",
    "file_search",
)

#: Chaves de parametro onde o SDK pode expor a linha de comando bruta de uma
#: tool de execucao de shell (`run_in_terminal`/`PermissionRequestShell` ou
#: equivalente) -- o nome LITERAL da tool/classe varia entre versoes do SDK
#: (ver `sdk_session._identificador_e_seguro_nativo`), entao a deteccao e
#: feita pelo FORMATO do parametro, nunca pelo nome da tool.
_CHAVES_PARAM_COMANDO: tuple[str, ...] = ("command", "cmd", "commandLine", "script")

#: Subcomandos git de LEITURA (nunca alteram o repositorio) -- liberados
#: mesmo sem `GATEWAY_GOVERNANCE_PERMISSIONS=true`.
_GIT_SUBCOMANDOS_LEITURA: tuple[str, ...] = (
    "status",
    "diff",
    "log",
    "show",
    "branch",
    "fetch",
    "rev-parse",
    "rev-list",
    "remote",
    "tag",
    "ls-files",
    "blame",
    "describe",
    "stash list",
    "config --get",
    "config --list",
)

#: Subcomandos git MUTANTES -- bloqueados SEMPRE, mesmo em modo `apply`
#: (defesa em profundidade, R-031: nenhum agent executa commit/push
#: autonomo; aqui reforcado na infraestrutura do gateway).
_GIT_SUBCOMANDOS_MUTACAO: tuple[str, ...] = (
    "commit",
    "push",
    "add",
    "reset",
    "rebase",
    "merge",
    "cherry-pick",
    "checkout",
    "clean",
    "filter-branch",
    "gc",
    "stash pop",
    "stash apply",
    "stash drop",
    "branch -d",
    "branch -D",
    "tag -d",
    "rm",
    "mv",
    "config --unset",
    "config --replace-all",
    "init",
)

#: Comandos utilitarios inocuos (nao-git) liberados por prefixo exato.
_COMANDOS_SEGUROS_NAO_GIT: tuple[str, ...] = (
    "ls",
    "pwd",
    "cat",
    "echo",
    # Bug real investigado (2026-10-04): comandos PowerShell compostos
    # (ex.: `git --no-pager status; Write-Output "---LOG---"; git --no-pager
    # log --oneline -5`) usam `Write-Output`/`Write-Host` como marcadores de
    # secao entre chamadas git read-only encadeadas -- equivalente PowerShell
    # de `echo` (ja presente acima para POSIX/bash). Sem este par, qualquer
    # segmento `write-output "..."` dentro do encadeamento falhava a
    # heuristica (nao e git, nao estava na allowlist), negando o comando
    # INTEIRO mesmo quando todos os subcomandos git eram 100% read-only.
    "write-output",
    "write-host",
    "find",
    "head",
    "tail",
    "mkdir",
    "cd",
    "which",
    "whoami",
    "wc",
    "grep",
    "tree",
    "type",
    "npm install",
    "npm ci",
    "pip install",
)

#: Padroes categoricamente bloqueados, independente de contexto (shell
#: destrutivo/escalada de privilegio/download remoto nao auditavel).
_COMANDOS_BLOQUEADOS_SEMPRE: tuple[str, ...] = (
    "rm -rf",
    "sudo",
    "curl ",
    "wget ",
    "chmod 777",
    "dd if=",
    ":(){",
)

#: Padroes equivalentes a `_COMANDOS_BLOQUEADOS_SEMPRE` em outras linguagens
#: aceitas pelo payload `language` de `ctx_execute`/`ctx_execute_file`
#: (python/javascript/typescript/rust/...) -- achado code-review 🔴 (iteracao
#: final 3/3): a denylist textual original so cobria shell, permitindo
#: bypass total via `shutil.rmtree(...)`, `fs.rmSync(...)`,
#: `requests.post(...)` etc. Defesa em profundidade BEST-EFFORT por
#: substring -- NAO e um sandboxer/parser AST e nao cobre ofuscacao
#: (concatenacao de string, encoding). A garantia primaria de isolamento e
#: o proprio sandbox de subprocesso isolado do `ctx_execute` (ver descricao
#: da tool MCP).
_PADROES_PERIGOSOS_MULTI_LINGUAGEM: tuple[str, ...] = (
    "shutil.rmtree",
    "os.remove",
    "os.system",
    "subprocess.run",
    "subprocess.popen",
    "subprocess.call",
    "eval(",
    "exec(",
    "child_process",
    "execsync",
    "spawnsync",
    "fs.rmsync",
    "fs.unlinksync",
    "requests.post",
    "urllib.request.urlopen",
    "fetch(",
    "axios.",
)


#: Invólucros comuns de shell nativo detectados ANTES da checagem de
#: encadeamento (`&&`/`||`/`|`/`;`) -- bug real investigado (2026-10-04):
#: o SDK/`pr-gatekeeper` frequentemente envia o comando efetivo embrulhado
#: por um shell nativo (`powershell -Command "..."`, `cmd /c "..."`,
#: `bash -lc "..."`), que nao e reconhecido por nenhum prefixo de
#: `_COMANDOS_SEGUROS_NAO_GIT` nem pelo branch `git `, caindo sempre no
#: fallback final (negado) mesmo quando o comando interno e 100% read-only
#: (ex.: "Negado pela politica local" para `git --no-pager status` via
#: PowerShell). Cada padrao captura o comando interno no grupo 1.
_PADROES_WRAPPER_SHELL: tuple[re.Pattern[str], ...] = (
    re.compile(r'^powershell(?:\.exe)?\s+-command\s+"(.+)"$', re.IGNORECASE),
    re.compile(r'^cmd(?:\.exe)?\s+/c\s+"(.+)"$', re.IGNORECASE),
    re.compile(r'^cmd(?:\.exe)?\s+/c\s+(.+)$', re.IGNORECASE),
    re.compile(r"^bash\s+-lc\s+\"(.+)\"$", re.IGNORECASE),
    re.compile(r"^bash\s+-c\s+\"(.+)\"$", re.IGNORECASE),
    re.compile(r"^bash\s+-c\s+'(.+)'$", re.IGNORECASE),
)


def _desembrulhar_shell_wrapper(normalizado: str) -> str | None:
    """Retorna o comando interno de um invólucro de shell reconhecido, ou `None`.

    Args:
        normalizado: Comando ja normalizado (`strip().lower()`) por
            `comando_terminal_e_seguro`.

    Returns:
        str | None: Comando interno (ainda nao normalizado alem do que ja
        veio de `normalizado`), ou `None` se nenhum padrao de invólucro
        reconhecido casar.
    """
    for padrao in _PADROES_WRAPPER_SHELL:
        match = padrao.match(normalizado)
        if match:
            return match.group(1).strip()
    return None


_SEPARADORES_ENCADEAMENTO: tuple[str, ...] = ("&&", "||", "|", ";", "&")


def comando_terminal_e_seguro(comando: str) -> bool:
    """Classifica heuristicamente um comando de shell como seguro (read-only).

    Replica, na infraestrutura do gateway, a mesma allowlist ja documentada
    para os agents deste repositorio (`.github/copilot-instructions.md`
    secao 2.1 e `.github/skills/terminal-governance/SKILL.md`): comandos
    git READ-ONLY (`status`/`diff`/`log`/`show`/`fetch`/`rev-parse`/...) e
    utilitarios inocuos (`ls`, `pwd`, `cat`, `mkdir`, instaladores de
    dependencia) sao liberados; qualquer subcomando git MUTANTE
    (`commit`/`push`/`add`/`reset`/...) ou comando potencialmente
    destrutivo (`rm -rf`, `sudo`, `curl`, `wget`, fork bomb, etc.)
    permanece bloqueado SEMPRE -- defesa em profundidade alinhada a R-031.

    Args:
        comando: Linha de comando bruta recebida do SDK (ex.:
            `params["command"]`).

    Returns:
        bool: `True` se o comando inteiro (e todos os segmentos
        encadeados por `&&`/`||`/`|`/`;`) e classificado como seguro.
    """
    normalizado = (comando or "").strip().lower()
    if not normalizado:
        return False
    if any(bloqueado in normalizado for bloqueado in _COMANDOS_BLOQUEADOS_SEMPRE):
        return False
    interno = _desembrulhar_shell_wrapper(normalizado)
    if interno is not None:
        return comando_terminal_e_seguro(interno)
    if any(sep in normalizado for sep in _SEPARADORES_ENCADEAMENTO):
        segmentos = [normalizado]
        for separador in _SEPARADORES_ENCADEAMENTO:
            proximos: list[str] = []
            for segmento in segmentos:
                proximos.extend(segmento.split(separador))
            segmentos = proximos
        return all(
            comando_terminal_e_seguro(segmento.strip())
            for segmento in segmentos
            if segmento.strip()
        )
    if normalizado.startswith("git "):
        resto = normalizado[len("git ") :].strip().replace("--no-pager ", "")

        def _bate_subcomando(sub: str) -> bool:
            return resto == sub or resto.startswith(f"{sub} ")

        if any(_bate_subcomando(sub) for sub in _GIT_SUBCOMANDOS_MUTACAO):
            return False
        return any(_bate_subcomando(sub) for sub in _GIT_SUBCOMANDOS_LEITURA)
    return any(
        normalizado == seguro or normalizado.startswith(f"{seguro} ")
        for seguro in _COMANDOS_SEGUROS_NAO_GIT
    )


def _extrair_comando(params: Mapping[str, object]) -> str | None:
    """Extrai a linha de comando bruta de `params`, se presente.

    A deteccao e feita pelo FORMATO do parametro (`command`/`cmd`/
    `commandLine`/`script`), nunca pelo nome literal da tool -- o SDK pode
    rotear tools de shell por classes/nomes distintos entre versoes (ver
    `sdk_session._identificador_e_seguro_nativo`).
    """
    for chave in _CHAVES_PARAM_COMANDO:
        valor = params.get(chave)
        if valor:
            return str(valor)
    return None


#: Campo onde tools MCP de execucao de codigo (`mcp_context-mode_ctx_execute`/
#: `ctx_execute_file`) expoem o payload real -- schema `language` + `code`,
#: nunca `command`/`cmd`/`commandLine`/`script` (bug real 2026-10-03: isso
#: causava bypass total da heuristica de comando perigoso para MCP).
_CHAVES_PARAM_CODIGO_MCP: tuple[str, ...] = ("code",)


def _extrair_codigo_mcp(params: Mapping[str, object]) -> str | None:
    """Extrai o campo `code` de params de tools MCP de execucao, se houver."""
    for chave in _CHAVES_PARAM_CODIGO_MCP:
        valor = params.get(chave)
        if valor:
            return str(valor)
    return None


def _codigo_mcp_e_perigoso(codigo: str) -> bool:
    """Denylist (nao allowlist) para o conteudo livre do campo `code` MCP.

    Independente de `language`: `os.system`/`subprocess`/`child_process.exec`
    perigosos podem aparecer em shell/python/js igualmente. Normaliza
    (lowercase + colapso de espacos) antes do match para reduzir
    falso-negativo trivial por espacamento -- NAO protege contra
    ofuscacao via concatenacao de string ou encoding (defesa em
    profundidade best-effort, nao um parser AST).
    """
    normalizado = " ".join((codigo or "").strip().lower().split())
    padroes = _COMANDOS_BLOQUEADOS_SEMPRE + _PADROES_PERIGOSOS_MULTI_LINGUAGEM
    return any(bloqueado in normalizado for bloqueado in padroes)


#: Chaves de parametro onde tools MCP de execucao podem expor um caminho de
#: sistema de arquivos arbitrario -- `path` em `ctx_execute_file` (leitura
#: arbitraria), `cwd` em `ctx_execute` (diretorio de execucao arbitrario).
#: Achado code-review 🟠 #1 (iteracao final 3/3): `_CHAVES_PARAM_CODIGO_MCP`
#: so cobria `code`.
_CHAVES_PARAM_PATH_MCP: tuple[str, ...] = ("path", "cwd")

#: Segmentos categoricamente suspeitos para `path`/`cwd` de tools MCP --
#: travessia de diretorio ou diretorios de sistema sensiveis. Heuristica
#: simples (nao exaustiva), defesa em profundidade best-effort.
_SEGMENTOS_PATH_SUSPEITOS: tuple[str, ...] = (
    "..",
    "/etc",
    "/root",
    "c:\\windows",
    "c:/windows",
    "/proc",
    "/sys",
)


def _extrair_paths_mcp(params: Mapping[str, object]) -> list[str]:
    """Extrai valores de `path`/`cwd` de params de tools MCP, se houver."""
    return [
        str(params[chave])
        for chave in _CHAVES_PARAM_PATH_MCP
        if params.get(chave)
    ]


def _caminho_mcp_e_suspeito(valor: str) -> bool:
    """True se `path`/`cwd` de uma tool MCP parecer travessia ou dir sensivel."""
    normalizado = (valor or "").strip().lower()
    return any(segmento in normalizado for segmento in _SEGMENTOS_PATH_SUSPEITOS)


#: Chave de parametro onde tools MCP de execucao em lote
#: (`mcp_context-mode_ctx_batch_execute`) expoem a lista de comandos --
#: achado code-review (4a iteracao, pos-esgotamento do teto de 3):
#: nenhuma extracao existente reconhecia o formato array
#: `commands=[{"label": ..., "command": ...}]`, e o fallback final
#: "nenhum campo reconhecido => seguro" liberava incondicionalmente comandos
#: destrutivos passados via batch (fail-open total).
_CHAVE_PARAM_COMANDOS_BATCH = "commands"


def _comando_batch_item_e_seguro(item: object) -> bool:
    """Classifica um item de `commands` de `ctx_batch_execute` como seguro.

    Fail-closed: itens que nao sejam `dict` com uma chave `command`
    textual nao-vazia sao tratados como perigosos (nunca ignorados
    silenciosamente). O campo `label` (se presente) e usado apenas para
    contexto/log, nunca para a checagem de seguranca.
    """
    if not isinstance(item, Mapping):
        return False
    comando = item.get("command")
    if not isinstance(comando, str) or not comando.strip():
        return False
    return comando_terminal_e_seguro(comando) or not _codigo_mcp_e_perigoso(comando)


def _extrair_comandos_batch(params: Mapping[str, object]) -> list[object] | None:
    """Extrai a lista bruta de `commands` de params, se presente.

    Retorna `None` quando `commands` nao esta presente ou nao e uma lista
    (nenhum campo reconhecido -- segue para as demais extracoes). Quando
    presente, cada item e validado individualmente por
    `_comando_batch_item_e_seguro` -- QUALQUER item perigoso ou malformado
    nega o batch inteiro (fail-closed no agregado).
    """
    valor = params.get(_CHAVE_PARAM_COMANDOS_BATCH)
    if not isinstance(valor, list):
        return None
    return valor

#: Prefixos de nome de tool MCP registrada via `mcp_servers=` (RC2) -- tratados
#: pela MESMA politica de permissao ja existente (nunca um bypass dedicado).
#: Lista fechada fixada pelo Security Checkpoint do bugfix 2026-10-02: apenas
#: os 3 MCP servers homologados (context-mode, tavily, codegraph).
MCP_TOOL_PREFIXES: tuple[str, ...] = (
    "mcp_context-mode_",
    "mcp_tavily_",
    "mcp_codegraph_",
)


def tool_mcp_e_cataloga(nome_tool: str) -> bool:
    """True se `nome_tool` pertence a um dos 3 MCP servers da lista fechada.

    Usado por `tool_call_nao_escrita_e_segura` para decidir se uma tool MCP
    deve respeitar a MESMA heuristica de comando seguro (nunca um bypass
    dedicado para MCP -- Security Checkpoint, mitigacao #6).
    """
    return any(nome_tool.startswith(p) for p in MCP_TOOL_PREFIXES)


def tool_call_nao_escrita_e_segura(
    tool_name: str, params: Mapping[str, object]
) -> bool:
    """Decisao central e reutilizavel para tools que NAO sao `PermissionRequestWrite`.

    Usada por `routes._conservative_permission_handler` (default, sem
    `GATEWAY_GOVERNANCE_PERMISSIONS`) e por `routes._governance_permission_handler`
    (quando a feature flag esta ativa) -- fonte unica (R-055) para evitar
    que a mesma heuristica de comando/tool seguro fique duplicada/divergente
    entre os dois handlers.

    Args:
        tool_name: Identificador da tool (nome literal, ex.: `"read_file"`,
            ou nome da classe do `PermissionRequest` quando o SDK nao expoe
            `tool_name`, ex.: `"PermissionRequestShell"`).
        params: Parametros de invocacao da tool (`invocation` do SDK).

    Returns:
        bool: `True` se a tool deve ser autorizada sem exigir path de
        escrita (leitura nativa, comando de shell classificado como
        seguro, ou prefixo de tool explicitamente liberado).
    """
    if tool_name.lower().startswith(READ_ONLY_TOOL_PREFIXES):
        return True
    if tool_mcp_e_cataloga(tool_name):
        # MCP tools da lista fechada (RC2) respeitam a MESMA heuristica de
        # comando seguro ja aplicada a shell nativo -- nao ha bypass
        # dedicado para MCP (Security Checkpoint, mitigacao #6: MCP nao
        # pode contornar `permission_policy`).
        comando = _extrair_comando(params)
        if comando is not None:
            return comando_terminal_e_seguro(comando)
        # Bug real corrigido (2026-10-03): `code` (+ `language`) e o payload
        # real de `ctx_execute`/`ctx_execute_file` -- avaliado por denylist,
        # nao pelo allowlist de `comando_terminal_e_seguro` (que rejeitaria
        # codigo legitimo em JS/Python que nao seja um comando de shell).
        # `path`/`cwd` suspeitos (achado 🟠 #1) sao verificados ANTES do
        # retorno, mesmo quando ha `code` valido, pois podem acompanhar o
        # payload (ex.: `cwd` em `ctx_execute`).
        if any(_caminho_mcp_e_suspeito(valor) for valor in _extrair_paths_mcp(params)):
            return False
        # Achado code-review (4a iteracao): `ctx_batch_execute` expoe
        # `commands` (lista de `{label, command}`), formato nao coberto por
        # nenhuma extracao anterior -- verificado ANTES do fallback final
        # para eliminar o fail-open de comandos destrutivos via batch.
        comandos_batch = _extrair_comandos_batch(params)
        if comandos_batch is not None:
            return all(
                _comando_batch_item_e_seguro(item) for item in comandos_batch
            )
        codigo = _extrair_codigo_mcp(params)
        if codigo is not None:
            return not _codigo_mcp_e_perigoso(codigo)
        # Sem campo de comando/codigo/path reconhecido (ex.: `ctx_search`,
        # tool somente leitura/consulta semantica do servidor homologado) --
        # tratado como seguro por definicao de catalogo fechado (nunca um
        # tool arbitrario fora dos 3 servers homologados).
        #
        # RISCO ACEITO DOCUMENTADO (achado 🟠 #2, analise deterministica do
        # @code-knowledge-graph, sem LLM): `mcp_codegraph_*` e 100%
        # read-only/offline contra `.codegraph/graph.db` -- zero risco de
        # RCE/FS arbitrario/SSRF, tratado como seguro sem denylist adicional.
        # `mcp_tavily_search`/`tavily_research` processam apenas strings de
        # busca (seguras). `tavily_extract`/`tavily_crawl`/`tavily_map`
        # aceitam `urls`/`url` arbitrarios -- risco e SSRF/exfiltracao via
        # URL processada pelos servidores da Tavily (nao RCE local neste
        # gateway). A mitigacao correta e allowlist de AGENT (somente
        # `@deep-search` pode chamar `mcp_tavily_*`), nao denylist de
        # conteudo/parsing de URL aqui.
        return True
    comando = _extrair_comando(params)
    if comando is not None:
        return comando_terminal_e_seguro(comando)
    # Debug investigativo (2026-10-04): bug real de MCP tools (context-mode)
    # negadas mesmo apos o servidor conectar com sucesso. Suspeita: o SDK
    # real reporta `tool_name` como nome CRU exposto pelo proprio servidor
    # MCP (ex.: "ctx_batch_execute"), SEM o prefixo de exibicao da IDE
    # ("mcp_context-mode_ctx_batch_execute") que `tool_mcp_e_cataloga`/
    # `MCP_TOOL_PREFIXES` espera -- mesma classe de bug ja confirmada em
    # `mcp_servers_catalog.py` (nomes de pacote assumidos sem validar
    # contra o comportamento real do SDK). Log abaixo expoe exatamente o
    # `tool_name` recebido e as chaves de `params`, para confirmar/refutar.
    logger.warning(
        "tool_call_negado_fallback tool_name=%r cataloga_mcp=%s "
        "params_keys=%s -- nenhum comando/codigo/batch reconhecido, "
        "negado por fallback final (possivel tool_name sem prefixo mcp_)",
        tool_name,
        tool_mcp_e_cataloga(tool_name),
        sorted(params.keys()) if isinstance(params, Mapping) else params,
    )
    return False


class PermissionMode(StrEnum):
    """Os 3 modos de permissao de escrita do gateway (Secao 6 do blueprint)."""

    READ_ONLY = "read_only"
    PROPOSE = "propose"
    APPLY = "apply"


@dataclass(frozen=True)
class WriteDecision:
    """Decisao estruturada de uma tentativa de escrita.

    Attributes:
        allowed: `True` somente em modo `apply` com as 4 guardas satisfeitas.
        reason: Motivo estavel e testavel da decisao (ex.: `"read_only_mode"`,
            `"propose_mode_diff_only"`, `"phase_forbids_write"`,
            `"drift_detected"`, `"checkpoint_open"`, `"path_blocked"`,
            `"guards_passed"`).
    """

    allowed: bool
    reason: str


class PermissionPolicyStub:
    """Politica de permissao de escrita do gateway — 3 modos + 4 guardas em `apply`."""

    def __init__(self, mode: PermissionMode, workspace_root: Path) -> None:
        """Inicializa a politica.

        Args:
            mode: Modo de permissao configurado (`GATEWAY_PERMISSION_MODE`).
            workspace_root: Raiz do workspace montado (`WORKSPACE_PATH`),
                usada pela guarda 4 para validar o caminho de destino.
        """
        self._mode = mode
        self._workspace_root = workspace_root.resolve()

    @property
    def mode(self) -> PermissionMode:
        """Modo de permissao configurado para esta instancia."""
        return self._mode

    def autorizar_escrita(
        self,
        *,
        sessao: Sessao,
        evento: Evento,
        tabela: TabelaTransicao,
        catalogo: Catalogo,
        checkpoint_aberto: bool,
        caminho_destino: Path,
    ) -> WriteDecision:
        """Avalia se uma escrita em `caminho_destino` e autorizada.

        Em `read_only`, nega sempre. Em `propose`, nunca executa a
        escrita real (o chamador deve gerar um diff como checkpoint). Em
        `apply`, aplica as 4 guardas na ordem do contrato:
            1. Fase atual permite escrita (via `transicionar`, R-050).
            2. `detectar_deriva(...).houve is False` (R-042).
            3. Nenhum checkpoint aberto (R-027).
            4. Caminho resolvido dentro do workspace, fora de bloqueios.

        Args:
            sessao: Estado atual da sessao de governanca.
            evento: Evento que originaria a transicao de escrita.
            tabela: Tabela de transicao compilada (`graph_loader`).
            catalogo: Catalogo de agentes usado por `detectar_deriva`.
            checkpoint_aberto: Se ha um checkpoint humano ainda nao resolvido.
            caminho_destino: Caminho de destino da escrita pretendida.

        Returns:
            WriteDecision: decisao com motivo estavel para teste/observabilidade.
        """
        if self._mode is PermissionMode.READ_ONLY:
            return self._decidir(allowed=False, reason="read_only_mode")
        if self._mode is PermissionMode.PROPOSE:
            return self._decidir(allowed=False, reason="propose_mode_diff_only")

        # Modo apply — 4 guardas, nesta ordem exata.
        try:
            transicionar(sessao, evento, tabela)
        except TransicaoInvalidaError:
            return self._decidir(allowed=False, reason="phase_forbids_write")

        deriva = detectar_deriva(sessao, evento.turno, catalogo)
        if deriva.houve:
            return self._decidir(allowed=False, reason="drift_detected")

        if checkpoint_aberto:
            return self._decidir(allowed=False, reason="checkpoint_open")

        if not self._caminho_permitido(caminho_destino):
            return self._decidir(allowed=False, reason="path_blocked")

        return self._decidir(allowed=True, reason="guards_passed")

    def _decidir(self, *, allowed: bool, reason: str) -> WriteDecision:
        """Registra (log estruturado) e retorna a decisao de escrita.

        Args:
            allowed: Resultado final da avaliacao das guardas/modo.
            reason: Motivo estavel da decisao (ver `WriteDecision.reason`).

        Returns:
            WriteDecision: mesma decisao recebida, apos logging.
        """
        if allowed:
            logger.info(
                "write_decision: allowed=True reason=%s mode=%s",
                reason,
                self._mode.value,
            )
        else:
            logger.warning(
                "write_decision: allowed=False reason=%s mode=%s",
                reason,
                self._mode.value,
            )
        return WriteDecision(allowed=allowed, reason=reason)

    def _caminho_permitido(self, caminho: Path) -> bool:
        """Guarda 4: `caminho` deve resolver dentro do workspace, fora de bloqueios."""
        resolved = caminho.resolve()
        try:
            resolved.relative_to(self._workspace_root)
        except ValueError:
            return False
        if any(segment in _BLOCKED_PATH_SEGMENTS for segment in resolved.parts):
            return False
        if resolved.name.startswith(".env"):
            return False
        if resolved.suffix in _BLOCKED_SUFFIXES:
            return False
        return True
