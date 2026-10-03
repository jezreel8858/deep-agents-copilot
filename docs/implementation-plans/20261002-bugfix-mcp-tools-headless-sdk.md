# Plano de Implementacao — Bugfix: Tools MCP/IDE nao expostas na sessao headless do SDK

> Status: `PRONTO PARA EXECUCAO POR @python-bug-fixer — AGUARDANDO APROVACAO FINAL DO USUARIO (gate R-064, Etapa 3)`
> Autorado por: `@python-arch-advisor` (Etapa 3 — Plano de Implementacao)
> Baseado em: `docs/plans/20261002-bugfix-mcp-tools-headless-sdk.md` (Plano de Planejamento aprovado, RC1 + RC2 + Security Checkpoint)
> Modo: Advisory — nenhum arquivo de codigo foi alterado por este agente. Blueprint cirurgico para handoff a `@python-bug-fixer`.

---

## 0. Pre-requisitos verificados nesta auditoria

- `agent_catalog.py`: `_ALIAS_TOOLS_SDK_HEADLESS` hoje so contem `{"ask_questions": "ask_user"}`; `_traduzir_tools_para_sdk_headless` ja preserva ordem/dedup — nao precisa mudar, so o dict.
- `sdk_session.py`: 2 call-sites de `client.create_session(...)` confirmados (`on_permission_request=...` + demais kwargs), nenhum com `mcp_servers=`.
- `config.py`: `Settings(BaseSettings)` via `pydantic-settings`, `env_file=".env"`, padrao de `Field(default=..., alias="ENV_VAR")` ja estabelecido — nova estrutura de MCP servers deve seguir o MESMO padrao (sem introduzir biblioteca nova).
- `permission_policy.py`: ja possui `PermissionPolicyStub`, `tool_call_nao_escrita_e_segura`, `comando_terminal_e_seguro`, `READ_ONLY_TOOL_PREFIXES`, `_CHAVES_PARAM_COMANDO` — ponto de extensao natural para a allowlist por agent.
- Levantamento real de `.github/agents/**/*.agent.md`: agents `*-arch-advisor` (ex.: `python-arch-advisor`, `react-arch-advisor`, `ejb-arch-advisor`, `spring-boot-arch-advisor`, `spring-reactive-arch-advisor`, `struts-arch-advisor`, `angular-arch-advisor`) e `agent-router`/`governance-maintainer` mencionam `run_in_terminal` no corpo (tipicamente para PROIBI-LO) mas **NAO** declaram `terminal-governance` em `source_docs:` — confirma que a regra de allowlist (checar os DOIS sinais: tool declarada E skill vinculada) exclui corretamente esses agents consultivos read-only. Agents `*-bug-fixer`, `*-feature-developer`, `*-test-fixer`, `*-perf-tuner`, `*-integration-test-writer`, `*-unit-test-writer`, `pr-gatekeeper`, `debugger`, `code-review`, `security-reviewer`, `code-knowledge-graph`, `database-specialist`, `deep-search`, `governance-factory`, `performance-agent`, `runtime-verifier`, `bug-triage`, `workflows`, `code-style-enforcer` possuem AMBOS os sinais.
- Suite de testes existente (`deploy/local-chat-gateway/tests/`): 21 arquivos, destaques relevantes a este bugfix: `unit/test_agent_catalog.py`, `unit/test_sdk_session.py`, `unit/test_config.py`, `unit/test_permission_policy.py`.

---

## 1. Diff Cirurgico Proposto (pseudo-diff — NAO implementado)

### 1.1 `agent_catalog.py` — expansao de `_ALIAS_TOOLS_SDK_HEADLESS` + allowlist deny-by-default

```diff
--- a/deploy/local-chat-gateway/src/local_chat_gateway/agent_catalog.py
+++ b/deploy/local-chat-gateway/src/local_chat_gateway/agent_catalog.py
@@
-_ALIAS_TOOLS_SDK_HEADLESS: dict[str, str] = {
-    "ask_questions": "ask_user",
-}
+#: Mapa de alias de tools de IDE (nomes convencionais usados nos prompts dos
+#: ~100+ `.agent.md`) -> nomes NATIVOS do SDK headless `github-copilot-sdk==
+#: 1.0.16` (bash, powershell, shell, grep, create, str_replace_editor, task,
+#: web_fetch, ask_user). Tools SEM equivalente nativo no SDK (ex.: MCP tools
+#: `mcp_context-mode_*`, `mcp_tavily_*`, `mcp_codegraph_*`) NAO entram aqui —
+#: essas sao resolvidas via `mcp_servers=` em `sdk_session.create_session`
+#: (RC2) e permanecem com o NOME ORIGINAL (o SDK roteia pelo nome do MCP
+#: tool registrado pelo proprio servidor, nao por este alias estatico).
+_ALIAS_TOOLS_SDK_HEADLESS: dict[str, str] = {
+    "ask_questions": "ask_user",
+    "read_file": "str_replace_editor",
+    "insert_edit_into_file": "str_replace_editor",
+    "replace_string_in_file": "str_replace_editor",
+    "create_file": "create",
+    "grep_search": "grep",
+    "run_subagent": "task",
+    "web_search": "web_fetch",
+    "fetch_webpage": "web_fetch",
+    # "run_in_terminal" e DELIBERADAMENTE OMITIDO deste mapa estatico — ver
+    # `_resolver_alias_terminal_por_agent` abaixo (Security Checkpoint,
+    # Risco #1: allowlist deny-by-default, nao liberacao global).
+}
+
+#: Nomes de tool de IDE que representam execucao de shell real — so podem
+#: ser traduzidos para a tool nativa do SDK (`bash`/`powershell`/`shell`)
+#: quando o agent de origem estiver na allowlist (ver
+#: `_agent_autorizado_para_shell_nativo`). Fora da allowlist, a tool e
+#: OMITIDA da lista final (nao e passada ao modelo) — deny-by-default.
+_TOOLS_SHELL_NATIVAS: dict[str, str] = {
+    "run_in_terminal": "bash",
+}
+
+#: Skill cuja presenca em `source_docs:` do frontmatter autoriza o agent a
+#: usar tools de shell nativas (regra fixada pelo Security Checkpoint,
+#: Risco #1 — nao e uma liberacao global para os ~100+ agents).
+_SKILL_TERMINAL_GOVERNANCE = "terminal-governance"
+
+
+def _agent_autorizado_para_shell_nativo(frontmatter: dict[str, Any]) -> bool:
+    """Allowlist deny-by-default p/ tools de shell real (bash/powershell/shell).
+
+    Autoriza SOMENTE quando AMBOS os sinais do frontmatter estao presentes:
+      1. `tools:` ja declarava `run_in_terminal` explicitamente (intencao
+         original do autor do agent preservada, nunca AMPLIADA por este
+         bugfix); e
+      2. `source_docs:` referencia
+         `.github/skills/terminal-governance/SKILL.md` (ou skill
+         equivalente `terminal-governance`), confirmando que o agent segue
+         a allowlist de comandos seguros documentada (R-049).
+
+    Agents puramente consultivos (`*-arch-advisor`, `agent-router`,
+    `governance-maintainer`) mencionam `run_in_terminal` apenas para
+    PROIBI-LO no corpo do prompt e NAO vinculam `terminal-governance` em
+    `source_docs:` — ficam corretamente FORA da allowlist.
+    """
+    tools = frontmatter.get("tools")
+    declara_run_in_terminal = isinstance(tools, list) and "run_in_terminal" in tools
+    source_docs = frontmatter.get("source_docs")
+    vincula_skill = isinstance(source_docs, list) and any(
+        _SKILL_TERMINAL_GOVERNANCE in str(s) for s in source_docs
+    )
+    return declara_run_in_terminal and vincula_skill
 
 
-def _traduzir_tools_para_sdk_headless(tools_brutas: list[Any]) -> list[str]:
+def _traduzir_tools_para_sdk_headless(
+    tools_brutas: list[Any], *, frontmatter: dict[str, Any] | None = None
+) -> list[str]:
     """Aplica `_ALIAS_TOOLS_SDK_HEADLESS` preservando ordem e sem duplicatas.
 
+    Tools de shell real (`run_in_terminal`) so sao traduzidas para a tool
+    nativa do SDK quando `frontmatter` passa por
+    `_agent_autorizado_para_shell_nativo` (deny-by-default, Security
+    Checkpoint Risco #1); caso contrario, a entrada e OMITIDA da lista
+    final (nunca repassada ao modelo "as cegas").
+
     Args:
         tools_brutas: Lista crua de `frontmatter["tools"]` (nomes convencionais
             da IDE, ex.: `["read_file", "ask_questions", "run_subagent"]`).
+        frontmatter: Frontmatter completo do `.agent.md` (usado apenas para
+            resolver a allowlist de shell nativo). Se `None`, nenhuma tool de
+            shell real e liberada (fail-closed).
 
     Returns:
         list[str]: nomes traduzidos para o vocabulario do SDK headless
         (ex.: `["read_file", "ask_user", "run_subagent"]`), sem repetir um
         nome ja presente (caso o `.agent.md` declare as duas formas).
     """
+    autorizado_shell = frontmatter is not None and _agent_autorizado_para_shell_nativo(
+        frontmatter
+    )
     traduzidas: list[str] = []
     for t in tools_brutas:
-        nome = _ALIAS_TOOLS_SDK_HEADLESS.get(str(t), str(t))
+        bruto = str(t)
+        if bruto in _TOOLS_SHELL_NATIVAS:
+            if not autorizado_shell:
+                continue  # deny-by-default: omite a tool, nao repassa crua
+            nome = _TOOLS_SHELL_NATIVAS[bruto]
+        else:
+            nome = _ALIAS_TOOLS_SDK_HEADLESS.get(bruto, bruto)
         if nome not in traduzidas:
             traduzidas.append(nome)
     return traduzidas
```

**Ponto de chamada a ajustar** (dentro de `_agent_de_arquivo`, onde `tools` e processado):

```diff
-    tools = frontmatter.get("tools")
-    if isinstance(tools, list):
-        config["tools"] = _traduzir_tools_para_sdk_headless(tools)
+    tools = frontmatter.get("tools")
+    if isinstance(tools, list):
+        config["tools"] = _traduzir_tools_para_sdk_headless(
+            tools, frontmatter=frontmatter
+        )
```

> Nota de nao-escopo: tools MCP (`mcp_context-mode_*`, `mcp_tavily_*`,
> `mcp_codegraph_*`) passam pelo `_ALIAS_TOOLS_SDK_HEADLESS.get(bruto, bruto)`
> sem match — permanecem com o nome ORIGINAL na lista `tools`. Isso e
> intencional: o SDK resolve tools de servidores MCP anexados via
> `mcp_servers=` (RC2, ver 1.2) pelo nome exposto pelo PROPRIO servidor MCP,
> nao por este alias estatico de tools de IDE.

### 1.2 `sdk_session.py` — injecao de `mcp_servers=` nas 2 chamadas de `create_session`

```diff
--- a/deploy/local-chat-gateway/src/local_chat_gateway/sdk_session.py
+++ b/deploy/local-chat-gateway/src/local_chat_gateway/sdk_session.py
@@
+from local_chat_gateway.config import Settings, get_settings
+from local_chat_gateway.mcp_servers_catalog import construir_mcp_servers  # novo modulo, ver 1.3
@@
     async with copilot.CopilotClient(github_token=token) as client:
         async with await client.create_session(
             on_permission_request=_bridge_permissao,
             model=model,
             session_id=session_id,
             working_directory=working_directory,
             additional_directories=(
                 list(additional_directories) if additional_directories else None
             ),
+            mcp_servers=construir_mcp_servers(get_settings()),
             ...
         ) as session:
@@ (segundo call-site, stream_chat_ag_ui)
     try:
         async with copilot.CopilotClient(github_token=token) as client:
             async with await client.create_session(
                 on_permission_request=_bridge_permissao,
                 on_elicitation_request=_bridge_elicitacao,
                 on_user_input_request=_bridge_user_input,
+                mcp_servers=construir_mcp_servers(get_settings()),
                 ...
             ) as session:
```

**Observacoes de injecao de dependencia (Clean Architecture)**:
- `construir_mcp_servers(settings)` e uma FUNCAO PURA (settings -> dict), testavel isoladamente sem subir o `CopilotClient` real — evita acoplar o teste de configuracao ao SDK.
- `get_settings()` ja e o ponto unico de override em testes (factory existente, reaproveitado — nao duplicar).
- Preferir passar `settings: Settings` explicitamente como parametro de `stream_chat`/`stream_chat_ag_ui` (DI por funcao, paridade com `working_directory` ja recebido por parametro) em vez de chamar `get_settings()` direto dentro da funcao de streaming, se o padrao atual do arquivo ja injetar `Settings` via FastAPI `Depends` nas rotas — **validar isso no codigo real antes de implementar** (`@python-bug-fixer` deve confirmar se `stream_chat` ja recebe `settings` como argumento; se sim, propagar `settings.mcp_servers_config`, nao chamar `get_settings()` internamente).

### 1.3 Novo modulo `mcp_servers_catalog.py` + extensao de `config.py`

Para nao inflar `config.py` com logica de construcao de objetos do SDK (separacao Settings vs. factory), propoe-se um modulo dedicado, paralelo a `agent_catalog.py`/`projects_catalog.py` (mesmo padrao arquitetural ja estabelecido no pacote):

```diff
--- a/deploy/local-chat-gateway/src/local_chat_gateway/config.py
+++ b/deploy/local-chat-gateway/src/local_chat_gateway/config.py
@@
 class Settings(BaseSettings):
     ...
+    # ------------------------------------------------------------------
+    # MCP servers (RC2) — lista FECHADA fixada pelo Security Checkpoint:
+    # apenas context-mode, tavily, codegraph. Nenhum MCP server adicional
+    # e lido de config dinamica/arquivo externo (anti prompt-injection via
+    # registro arbitrario de processo).
+    # ------------------------------------------------------------------
+    mcp_context_mode_enabled: bool = Field(
+        default=True, alias="MCP_CONTEXT_MODE_ENABLED"
+    )
+    mcp_context_mode_command: str = Field(
+        default="npx", alias="MCP_CONTEXT_MODE_COMMAND"
+    )
+    mcp_context_mode_args: str = Field(
+        default="-y,@context-mode/mcp-server", alias="MCP_CONTEXT_MODE_ARGS"
+    )
+    mcp_tavily_enabled: bool = Field(default=True, alias="MCP_TAVILY_ENABLED")
+    mcp_tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")
+    mcp_codegraph_enabled: bool = Field(
+        default=True, alias="MCP_CODEGRAPH_ENABLED"
+    )
+    mcp_codegraph_command: str = Field(
+        default="npx", alias="MCP_CODEGRAPH_COMMAND"
+    )
+    mcp_codegraph_args: str = Field(
+        default="-y,@codegraph/mcp-server", alias="MCP_CODEGRAPH_ARGS"
+    )
+
+    @field_validator(
+        "mcp_context_mode_args", "mcp_codegraph_args", mode="before"
+    )
+    @classmethod
+    def _string_vazia_vira_default(cls, valor: object) -> object:
+        """Evita `Path("")`-like bypass silencioso (mesmo padrao de
+        `_string_vazia_vira_none` ja existente neste arquivo)."""
+        if valor == "":
+            return None
+        return valor
```

Novo arquivo `deploy/local-chat-gateway/src/local_chat_gateway/mcp_servers_catalog.py`:

```python
"""mcp_servers_catalog — traduz `Settings` na lista FECHADA de MCP servers
(context-mode, tavily, codegraph) repassada a `client.create_session(
mcp_servers=...)` (RC2).

Lista fechada fixada pelo Security Checkpoint do bugfix 2026-10-02: NENHUM
MCP server alem destes tres e registrado, independentemente de configuracao
externa — mitigacao de registro arbitrario de processo (prompt injection/
exfiltracao).

Env minimo (Security Checkpoint, mitigacao #3): cada MCP server stdio
recebe APENAS as variaveis de ambiente estritamente necessarias (nunca
`os.environ` completo do processo do gateway) — evita vazar
`GATEWAY_API_KEY`, tokens do Copilot, etc. para o subprocesso MCP.
"""
from __future__ import annotations

import os
from typing import Any

from local_chat_gateway.config import Settings


def _env_minimo(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Monta env MINIMO para subprocesso stdio (mitigacao #3).

    Inclui apenas `PATH`/`SYSTEMROOT` (necessarios para resolver o
    executavel) + variaveis explicitamente passadas em `extra` — nunca
    `dict(os.environ)` completo.
    """
    base = {"PATH": os.environ.get("PATH", "")}
    if os.name == "nt" and "SYSTEMROOT" in os.environ:
        base["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
    if extra:
        base.update(extra)
    return base


def construir_mcp_servers(settings: Settings) -> dict[str, dict[str, Any]]:
    """Constroi o dict `mcp_servers` para `create_session(mcp_servers=...)`.

    Lista FECHADA: apenas as chaves `context-mode`, `tavily`, `codegraph`
    podem aparecer no retorno — nunca um servidor arbitrario derivado de
    configuracao dinamica.
    """
    servidores: dict[str, dict[str, Any]] = {}

    if settings.mcp_context_mode_enabled:
        servidores["context-mode"] = {
            "type": "stdio",
            "command": settings.mcp_context_mode_command,
            "args": settings.mcp_context_mode_args.split(","),
            "env": _env_minimo(),
        }

    if settings.mcp_tavily_enabled:
        if not settings.mcp_tavily_api_key:
            # Fallback fixado pelo Security Checkpoint (risco #2): nunca
            # hardcode/duplica a key — se a env var nao existe, o servidor
            # Tavily simplesmente NAO e materializado (fail-closed).
            pass
        else:
            servidores["tavily"] = {
                "type": "http",
                "url": "https://mcp.tavily.com/mcp/",
                "headers": {"Authorization": f"Bearer {settings.mcp_tavily_api_key}"},
            }

    if settings.mcp_codegraph_enabled:
        servidores["codegraph"] = {
            "type": "stdio",
            "command": settings.mcp_codegraph_command,
            "args": settings.mcp_codegraph_args.split(","),
            "env": _env_minimo(),
        }

    return servidores
```

> **ATENCAO — a confirmar por `@python-bug-fixer` antes de codificar**: o
> formato EXATO de `MCPServerConfig` (chaves `type`/`command`/`args`/`env`
> para stdio; `type`/`url`/`headers` para HTTP) deve ser validado por
> introspeccao real da wheel `github_copilot_sdk==1.0.16` (mesma
> metodologia RT-01..RT-05 ja aplicada neste arquivo, ver comentarios
> historicos em `sdk_session.py`), **antes** de codificar — este pseudo-diff
> assume a forma documentada generica de MCP (`mcp.json`/Claude Desktop),
> mas o SDK pode exigir um `TypedDict`/dataclass proprio
   (`copilot.session.MCPServerConfig`). Subtask dedicada no §3.

### 1.4 `permission_policy.py` — pontos de integracao para validar tools MCP/shell

```diff
--- a/deploy/local-chat-gateway/src/local_chat_gateway/permission_policy.py
+++ b/deploy/local-chat-gateway/src/local_chat_gateway/permission_policy.py
@@
+#: Prefixos de tool MCP registrada via `mcp_servers=` (RC2) — tratados pela
+#: MESMA politica de permissao ja existente (nunca um bypass dedicado).
+#: Nomes expostos pelo SDK para tools MCP seguem o padrao
+#: `mcp_<server>_<tool>` (confirmar por introspeccao real, RT-06).
+MCP_TOOL_PREFIXES: tuple[str, ...] = (
+    "mcp_context-mode_",
+    "mcp_tavily_",
+    "mcp_codegraph_",
+)
+
+
+def tool_mcp_e_cataloga(nome_tool: str) -> bool:
+    """True se `nome_tool` pertence a um dos 3 MCP servers da lista fechada.
+
+    Usado por `routes._conservative_permission_handler`/
+    `routes._governance_permission_handler` para decidir se uma tool MCP
+    desconhecida (fora da lista fechada, ex.: um MCP server que um agent
+    tentasse invocar por nome mas que NUNCA foi registrado em
+    `mcp_servers_catalog.construir_mcp_servers`) deve ser tratada como
+    tool NAO reconhecida (nega por padrao, nunca assume seguranca).
+    """
+    return any(nome_tool.startswith(p) for p in MCP_TOOL_PREFIXES)
```

**Integracao em `tool_call_nao_escrita_e_segura`** (funcao ja existente — adicionar ramo, nao substituir logica atual):

```diff
 def tool_call_nao_escrita_e_segura(nome_tool: str, params: Mapping[str, object]) -> bool:
     ...
+    # MCP tools da lista fechada (RC2) respeitam a MESMA heuristica de
+    # comando seguro ja aplicada a shell nativo — nao ha bypass dedicado
+    # para MCP (Security Checkpoint, mitigacao #6: MCP nao pode contornar
+    # `permission_policy`).
+    if tool_mcp_e_cataloga(nome_tool):
+        comando = _extrair_comando(params)
+        if comando is not None:
+            return comando_terminal_e_seguro(comando)
+        # Sem campo de comando reconhecido (ex.: `ctx_search`, somente
+        # leitura/consulta semantica) -- tratado pelos prefixos de
+        # READ_ONLY_TOOL_PREFIXES ja existentes mais abaixo nesta funcao,
+        # sem necessidade de ramo extra.
 ...
```

> Nota: este e um ponto de integracao PROPOSTO para discussao com
> `@python-bug-fixer`; a logica exata de "o que torna uma chamada
> `ctx_execute`/`ctx_execute_file` segura" (ex.: comandos de escrita de
> arquivo via `ctx_execute_file` sao, por definicao, ESCRITA e devem cair no
> fluxo de `WriteDecision`/checkpoint humano, nao no fluxo read-only) precisa
> ser desenhada com cuidado — **nao tratar toda tool MCP como
> automaticamente segura**. Subtask dedicada no §3 para esta decisao fina.

---

## 2. Sequencia TDD Estrita (Red -> Green -> Regressao)

> Principio: cada teste novo e escrito ANTES da implementacao (Red), falha
> pelo motivo correto, so entao o diff do §1 correspondente e aplicado
> (Green). Regressao final roda a suite completa (232/233 + novos).

### 2.1 `tests/unit/test_agent_catalog.py` (RC1)

| # | Teste novo | O que valida |
|---|---|---|
| T1 | `test_traduzir_tools_mapeia_read_file_para_str_replace_editor` | `_traduzir_tools_para_sdk_headless(["read_file"])` -> `["str_replace_editor"]` |
| T2 | `test_traduzir_tools_mapeia_run_subagent_para_task` | `["run_subagent"]` -> `["task"]` |
| T3 | `test_traduzir_tools_mapeia_grep_search_para_grep` | `["grep_search"]` -> `["grep"]` |
| T4 | `test_traduzir_tools_omite_run_in_terminal_sem_allowlist` | agent SEM `source_docs: terminal-governance` -> `run_in_terminal` e OMITIDO da lista final (nao aparece, nem cru nem traduzido) |
| T5 | `test_traduzir_tools_libera_bash_com_allowlist_completa` | agent COM `tools: [run_in_terminal]` E `source_docs: [".../terminal-governance/SKILL.md"]` -> `["bash"]` |
| T6 | `test_traduzir_tools_nega_bash_so_com_tool_sem_skill` | `tools: [run_in_terminal]` mas SEM vinculo a skill -> omitido (prova que o 1o sinal sozinho nao basta) |
| T7 | `test_traduzir_tools_nega_bash_so_com_skill_sem_tool_declarada` | `source_docs` vincula skill mas `tools` nao lista `run_in_terminal` -> omitido (prova que o 2o sinal sozinho nao basta) |
| T8 | `test_traduzir_tools_preserva_nome_mcp_sem_alias` | `["mcp_context-mode_ctx_execute"]` -> permanece inalterado (nao ha match no dict de alias) |
| T9 (caracterizacao, agents reais) | `test_descobrir_custom_agents_python_bug_fixer_recebe_bash` | usando o `.agent.md` REAL de `python-bug-fixer` (tem ambos sinais), `descobrir_custom_agents` retorna `tools` contendo `"bash"` |
| T10 (caracterizacao, agents reais) | `test_descobrir_custom_agents_python_arch_advisor_nao_recebe_bash` | usando o `.agent.md` REAL de `python-arch-advisor` (so tem 1o sinal, sem skill), `tools` resultante NAO contem `"bash"`/`"powershell"`/`"shell"` |

### 2.2 `tests/unit/test_sdk_session.py` (RC2)

| # | Teste novo | O que valida |
|---|---|---|
| T11 | `test_stream_chat_passa_mcp_servers_para_create_session` | mock de `client.create_session` capturado via spy; assert `mcp_servers=` foi passado com as 3 chaves esperadas quando os 3 `*_enabled=True` |
| T12 | `test_stream_chat_ag_ui_passa_mcp_servers_para_create_session` | idem para o 2o call-site (linha ~1840) |
| T13 | `test_stream_chat_omite_tavily_sem_api_key` | `TAVILY_API_KEY` ausente -> dict `mcp_servers` resultante NAO contem chave `"tavily"` (demais 2 presentes) |
| T14 | `test_stream_chat_respeita_flags_enabled_false` | `MCP_CODEGRAPH_ENABLED=false` -> `"codegraph"` ausente do dict |

### 2.3 Novo `tests/unit/test_mcp_servers_catalog.py` (modulo novo)

| # | Teste novo | O que valida |
|---|---|---|
| T15 | `test_construir_mcp_servers_lista_fechada_3_chaves_max` | com todos `*_enabled=True` + Tavily key presente, `set(resultado.keys()) <= {"context-mode", "tavily", "codegraph"}` (nunca mais que isso, mesmo manipulando `Settings` arbitrariamente) |
| T16 | `test_construir_mcp_servers_env_minimo_nao_herda_os_environ_completo` | injeta `os.environ["SECRET_TOKEN"]="x"` no teste; assert `"SECRET_TOKEN"` NAO aparece em `servidores["context-mode"]["env"]` (mitigacao #3) |
| T17 | `test_construir_mcp_servers_tavily_usa_env_var_existente_sem_hardcode` | `Settings(mcp_tavily_api_key="abc")` -> header `Authorization` contem `"abc"`; nenhum valor fixo/hardcoded no modulo (busca estatica no source do modulo por string literal de token, se viavel) |
| T18 | `test_construir_mcp_servers_todas_flags_false_retorna_vazio` | `*_enabled=False` nos 3 -> `{}` |

### 2.4 `tests/unit/test_config.py` (novos campos de Settings)

| # | Teste novo | O que valida |
|---|---|---|
| T19 | `test_settings_mcp_context_mode_args_default_split_correto` | default `"-y,@context-mode/mcp-server"` existe e e parseavel por `.split(",")` sem erro |
| T20 | `test_settings_mcp_tavily_api_key_default_none` | sem env var, `settings.mcp_tavily_api_key is None` (nunca default hardcoded de credencial) |
| T21 | `test_settings_mcp_args_string_vazia_vira_none` | paridade com `_string_vazia_vira_none` ja testado para `governance_graph_path` — mesma garantia para os novos campos `*_args` |

### 2.5 `tests/unit/test_permission_policy.py` (integracao MCP)

| # | Teste novo | O que valida |
|---|---|---|
| T22 | `test_tool_mcp_e_cataloga_reconhece_prefixos_fechados` | `tool_mcp_e_cataloga("mcp_context-mode_ctx_execute") is True`; `tool_mcp_e_cataloga("mcp_desconhecido_xyz") is False` |
| T23 | `test_tool_call_nao_escrita_e_segura_mcp_ctx_execute_comando_perigoso_negado` | `tool_call_nao_escrita_e_segura("mcp_context-mode_ctx_execute", {"code": "rm -rf /"})` (ou campo de comando equivalente) -> `False`, provando que MCP nao bypassa a heuristica de comando perigoso |
| T24 | `test_tool_call_nao_escrita_e_segura_mcp_ctx_search_sempre_segura` | tool MCP read-only (`mcp_context-mode_ctx_search`) sem campo de comando -> cai no fluxo `READ_ONLY_TOOL_PREFIXES`/comportamento ja existente, resultado `True` |

### 2.6 Regressao obrigatoria

- `@python-bug-fixer` DEVE rodar a suite completa (`pytest deploy/local-chat-gateway/tests/ -v`) apos CADA diff do §1 aplicado incrementalmente (nao apenas no final) — ordem recomendada: 1.1 -> roda T1-T10 + regressao total; 1.3+1.2 -> roda T11-T21 + regressao total; 1.4 -> roda T22-T24 + regressao total.
- Criterio de aceite: contagem final de testes passando = `232 (baseline) + 24 (novos T1-T24) = 256`, zero regressoes nos 232 originais. Se o baseline real divergir de 232/233 no momento da execucao (`@python-bug-fixer` deve confirmar com `pytest --collect-only -q` antes de comecar), ajustar a aritmetica mas manter "zero regressoes" como gate inegociavel.

---

## 3. Subtasks Executaveis por `@python-bug-fixer`

- `[S]` T-01 — Confirmar por introspeccao real da wheel `github_copilot_sdk==1.0.16` (`python -c "import copilot, inspect; ..."`, mesma metodologia RT-01..RT-05 ja documentada em `sdk_session.py`) a assinatura EXATA de `MCPServerConfig`/`create_session(mcp_servers=...)` — formato stdio (`command`/`args`/`env`) e HTTP (`url`/`headers`), antes de escrever qualquer diff de `mcp_servers_catalog.py`. **Bloqueante para T-04/T-05.**
- `[S]` T-02 — Escrever T1-T10 (`test_agent_catalog.py`, Red) e confirmar falha pelo motivo correto (import/assert de chave ausente, nao erro de sintaxe).
- `[P]` T-03 — Aplicar diff §1.1 (`agent_catalog.py`): expandir `_ALIAS_TOOLS_SDK_HEADLESS`, adicionar `_TOOLS_SHELL_NATIVAS`, `_agent_autorizado_para_shell_nativo`, atualizar assinatura de `_traduzir_tools_para_sdk_headless` e o ponto de chamada em `_agent_de_arquivo`. Rodar T1-T10 ate Green.
- `[S]` T-04 — Escrever T15-T21 (`test_mcp_servers_catalog.py` + `test_config.py`, Red), dependente do resultado de T-01.
- `[P]` T-05 — Criar `mcp_servers_catalog.py` + aplicar diff §1.3 em `config.py` (novos campos `Settings`). Rodar T15-T21 ate Green.
- `[S]` T-06 — Escrever T11-T14 (`test_sdk_session.py`, Red) usando spy/mock em `client.create_session` (padrao ja usado nos testes existentes deste arquivo — reaproveitar fixture, nao duplicar setup).
- `[P]` T-07 — Aplicar diff §1.2 (`sdk_session.py`): injetar `mcp_servers=construir_mcp_servers(...)` nos 2 call-sites — **antes de codificar, confirmar se `stream_chat`/`stream_chat_ag_ui` ja recebem `Settings` via parametro (DI) ou se precisam chamar `get_settings()` internamente** (ver nota em §1.2). Rodar T11-T14 ate Green.
- `[S]` T-08 — Escrever T22-T24 (`test_permission_policy.py`, Red).
- `[P]` T-09 — Aplicar diff §1.4 (`permission_policy.py`): `MCP_TOOL_PREFIXES`, `tool_mcp_e_cataloga`, ramo de integracao em `tool_call_nao_escrita_e_segura`. Rodar T22-T24 ate Green.
- `[S]` T-10 — Rodar suite completa (`pytest -v`) apos T-09, confirmar 232(baseline)+24 passando, zero regressoes. Rodar `mypy --strict` sobre os 4 arquivos alterados + o novo modulo (tipagem estrita, PEP 604 `X | None` ja em uso no projeto — manter consistencia).
- `[S]` T-11 — Atualizar `.env.example` com as novas variaveis (`MCP_CONTEXT_MODE_ENABLED`, `MCP_CONTEXT_MODE_COMMAND`, `MCP_CONTEXT_MODE_ARGS`, `MCP_TAVILY_ENABLED`, `TAVILY_API_KEY` [referenciar, nao criar, se ja existir no `.env` do gateway], `MCP_CODEGRAPH_ENABLED`, `MCP_CODEGRAPH_COMMAND`, `MCP_CODEGRAPH_ARGS`) com comentarios explicando a lista fechada e o fail-closed de Tavily sem key.
- `[S]` T-12 — Atualizar `BLUEPRINT_LOCAL_CHAT_GATEWAY.md` (se existir secao de configuracao/MCP) refletindo a nova capacidade, citando RC1/RC2 e este plano como referencia historica (mesmo padrao de comentarios "Bug real corrigido em..." ja usado nos 4 arquivos).

Legenda: `[S]` = sequencial (depende do anterior); `[P]` = pode ser paralelizado com outra tarefa `[P]` do MESMO bloco TDD se `@python-bug-fixer` operar com sub-agentes adicionais, mas NUNCA paralelizar Red e Green do mesmo bloco (quebra o ciclo TDD).

---

## 4. Riscos Residuais Identificados Nesta Etapa (alem dos R1-R6 ja no plano de planejamento)

| # | Risco | Mitigacao proposta |
|---|---|---|
| R7 | Formato real de `MCPServerConfig` no SDK pode divergir da forma generica assumida em `mcp_servers_catalog.py` (pseudo-diff) | T-01 bloqueante (introspeccao real ANTES de codificar) — nao assumir forma de outros MCP clients (Claude Desktop/VS Code) sem confirmar na wheel instalada |
| R8 | `stream_chat`/`stream_chat_ag_ui` podem nao receber `Settings` via DI atualmente, forcando `get_settings()` global dentro da funcao (acoplamento oculto) | `@python-bug-fixer` deve verificar o padrao real antes de T-07 e, se necessario, propagar `settings` como parametro explicito (favorece testabilidade e Clean Architecture) |
| R9 | Allowlist de shell por `source_docs` pode falsos-negativos se algum agent vincular a skill com string ligeiramente diferente (ex.: caminho relativo vs. absoluto) | `_agent_autorizado_para_shell_nativo` usa `in` (substring match) no nome da skill, nao igualdade exata de path — tolerante a variacoes de caminho, testado em T5-T7 |

---

## 5. Pergunta de Aprovacao Final (gate R-064, Etapa 3 -> Etapa 4)

Este plano de implementacao esta pronto para handoff a `@python-bug-fixer` executar o ciclo TDD completo (T-01 a T-12). Nenhum codigo foi alterado por este agente (modo Advisory, 100% leitura via context-mode).
