# Plano de Planejamento — Bugfix: Tools MCP/IDE não expostas na sessão headless do SDK

> Status: `APROVADO COM RESSALVAS (WF1_SECURITY_CHECKPOINT concluído) — AGUARDANDO GATE R-064 (aprovação do usuário)`
> Gerado por: `@bug-triage` (Etapa 2 — R-064, Plano de Planejamento)
> Origem: RCA consolidada em sessão anterior (RC1 + RC2)

## 1. Contexto do Bug

O gateway headless (`local-chat-gateway`) executa agents via `github-copilot-sdk==1.0.16` sem o runtime do VS Code. Ferramentas nativas de IDE e servidores MCP configurados (`context-mode`, `tavily`, `codegraph`) não chegam ao modelo nas sessões headless: o catálogo de agents só reconhece nomes de tools do IDE, e a sessão SDK nunca registra os servidores MCP configurados em `.vscode/mcp.json` (que é lido apenas pelo VS Code, não pelo processo Python).

**Sintoma observado:** agents que dependem de `mcp_context-mode_*`, `mcp_tavily_*`, `mcp_codegraph_*`, `run_in_terminal`, `list_dir`, `run_subagent`, `read_file`, `grep_search`, `insert_edit_into_file`, `replace_string_in_file` falham silenciosamente ou caem em fallback degradado quando executados via gateway headless.

## 2. Causa Raiz (RCA consolidada)

### RC1 — `agent_catalog.py:71-93` (`_ALIAS_TOOLS_SDK_HEADLESS`)
Mapa de alias de tools só traduz `ask_questions` → `ask_user`. Nomes nativos disponíveis no SDK: `bash`, `powershell`, `shell`, `grep`, `create`, `str_replace_editor`, `task`, `web_fetch`, `ask_user`. Não existe alias para as tools de IDE/MCP usadas pelos prompts dos ~100+ agents do catálogo.

### RC2 — `sdk_session.py:577` e `:1840` (`client.create_session(...)`)
Nenhuma das duas chamadas passa o parâmetro `mcp_servers=`, suportado nativamente pelo SDK (`client.py:2355/2806/3153`). Resultado: servidores MCP nunca são anexados à sessão headless, independentemente do que está configurado em `.vscode/mcp.json` (arquivo que, de qualquer forma, só é consumido pelo VS Code — não pelo processo Python do gateway).

## 3. Escopo da Correção

**Arquivos candidatos a alteração:**
- `deploy/local-chat-gateway/src/local_chat_gateway/agent_catalog.py` — expandir `_ALIAS_TOOLS_SDK_HEADLESS` cobrindo 100% dos nomes de tools de IDE usados nos prompts dos agents, mapeando para os nomes nativos do SDK (`bash`/`powershell`/`shell`/`grep`/`create`/`str_replace_editor`/`task`/`web_fetch`).
- `deploy/local-chat-gateway/src/local_chat_gateway/sdk_session.py` — passar `mcp_servers=` nas duas chamadas de `client.create_session(...)` (linhas 577 e 1840), construindo a lista a partir de uma fonte de configuração própria do gateway (não do `.vscode/mcp.json`).
- `deploy/local-chat-gateway/src/local_chat_gateway/config.py` — **somente leitura de referência a variáveis de ambiente já existentes** para credenciais de MCP servers (Tavily etc.), nunca hardcode ou duplicação de secret.
- `deploy/local-chat-gateway/src/local_chat_gateway/permission_policy.py` — **possível** extensão de allowlist por agent para as novas tools liberadas (bash/powershell/shell reais) e para os MCP servers stdio — a confirmar no Security Checkpoint (ver §5).

**Fora de escopo (bloquear deriva de intenção):**
- Qualquer refatoração do catálogo de agents além do mapa de aliases.
- Qualquer alteração em prompts de agents individuais.
- Qualquer alteração em `.vscode/mcp.json` (não é consumido pelo processo headless; não resolve RC2).

## 4. Critérios de Aceitação Objetivos

- [ ] A sessão headless do gateway expõe `mcp_servers` para `context-mode`, `tavily` e `codegraph` (verificável via novo teste de integração/unitário em `sdk_session.py`).
- [ ] 100% dos aliases de tools referenciados no catálogo de agents (`agent_catalog.py`) resolvem para um nome nativo válido do SDK `github-copilot-sdk==1.0.16` (sem `KeyError`/fallback silencioso).
- [ ] 232/233 testes existentes (`test_sdk_session.py` + `test_permission_policy.py`) continuam verdes.
- [ ] Novo red-test cobrindo RC1 (alias ausente) e RC2 (`mcp_servers` ausente na chamada) fica verde após a correção.
- [ ] Nenhuma credencial de MCP server (ex.: Tavily API key) aparece hardcoded ou duplicada em `config.py` — validado por leitura exclusiva de variável de ambiente já existente.
- [ ] `permission_policy.py` possui decisão explícita (allowlist ou liberação justificada) para as tools `bash`/`powershell`/`shell` nativas e para os MCP servers stdio recém-anexados, por agent.

## 5. Riscos (incluindo Security Checkpoint do @tech-solution-architect)

| # | Risco | Origem | Mitigação proposta | [fallback] |
|---|---|---|---|---|
| 1 | Novos aliases liberam `bash`/`powershell`/`shell` reais para 100+ agents headless sem filtro | @tech-solution-architect (WF1_SECURITY_CHECKPOINT) | **DECISÃO FIXADA:** allowlist explícita por agent em `permission_policy.py`, negação por padrão (deny-by-default). Agents só de leitura/planejamento (architect, planners, triage, reviewers) NÃO recebem shell. Tool sem mapeamento gera negação explícita registrada em log — fallback silencioso proibido. | [fallback: nenhum — negação por padrão já é o comportamento seguro, não há fallback degradado aceitável aqui] |
| 2 | Duplicação/hardcode de API key (Tavily e demais credenciais MCP) em `config.py` | @tech-solution-architect | Referenciar exclusivamente variável de ambiente já existente no `.env`/secrets do gateway; nunca copiar valor literal | [fallback: se variável não existir ainda, bloquear a materialização do MCP server correspondente e abrir subtask de provisionamento de secret, não hardcodar] |
| 3 | MCP servers stdio registrados via `mcp_servers=` podem executar processo externo arbitrário | @tech-solution-architect | **DECISÃO FIXADA (regra principal, não fallback):** lista fechada — apenas `context-mode`, `tavily`, `codegraph` são permitidos. Comando/binário/versão fixos (caminho absoluto ou pacote com versão travada); `npx -y <pkg>@latest` proibido (risco de cadeia de suprimentos). Novo servidor exige alteração de código + novo Security Checkpoint. Acesso por servidor também respeita allowlist por agent (ex.: `codegraph` restrito a `@codegraph-engine` — R-045; Tavily restrito a `@deep-search`). | [fallback: nenhum — registro dinâmico de novos stdio servers permanece proibido indefinidamente até revisão explícita] |
| 4 | Blast Radius sistêmico (🔴) — mudança compartilhada por ~100+ agents sem safety net suficiente | RCA (bug-triage) | Rodar suíte completa `test_sdk_session.py` + `test_permission_policy.py` (232/233) como safety net antes/depois; não prosseguir para implementação sem gate de segurança aprovado | [fallback: rollout faseado — habilitar primeiro em ambiente de homolog/dev, validar telemetria de erros por N dias antes de prod] |

| R1 | Aliases de tools só-leitura mapeados para tool de execução ampliariam privilégio indevidamente | @tech-solution-architect (ressalva pós-checkpoint) | `read_file`/`list_dir`/`grep_search` NUNCA mapeiam para `bash`/`shell`; mapear para equivalente nativo de leitura (ex.: `grep`) ou negar. Novo teste automatizado garante que nenhum alias de leitura resolve para tool de execução. | [fallback: se não houver equivalente nativo de leitura, negar o alias e documentar limitação ao agent dependente] |
| R2 | `context-mode` (`ctx_execute`/`ctx_batch_execute`) equivale a shell arbitrário e não pode ser tratado como "tool de leitura" | @tech-solution-architect (ressalva pós-checkpoint) | Incluir `context-mode` na mesma matriz de permissão de execução que `bash`/`powershell`/`shell`, sujeito à mesma allowlist deny-by-default | [fallback: nenhum — tratar como execução é obrigatório, não opcional] |
| R3 | `run_subagent`→`task` poderia permitir escalonamento de privilégio ou recursão descontrolada | @tech-solution-architect (ressalva pós-checkpoint) | Subagent nunca pode ter mais permissões que o agent criador; limitar profundidade e número de criações de subagents | [fallback: circuit breaker de profundidade/contagem já previsto no protocolo de execução (R-060) deve cobrir este caso] |
| R4 | Processos MCP stdio herdando o ambiente completo do gateway vazariam secrets não relacionados | @tech-solution-architect (ressalva pós-checkpoint) | Cada servidor MCP recebe `env` mínimo e explícito, somente com as variáveis necessárias — nunca herança total do ambiente do processo pai | [fallback: nenhum — herança total de env é proibida sem exceção] |
| R5 | Cadeia de exfiltração/prompt injection via conteúdo externo (`web_fetch`/Tavily) combinado com shell/escrita em arquivo | @tech-solution-architect (ressalva pós-checkpoint) | Restringir `web_fetch` aos agents de pesquisa; mascarar (redact) secrets em logs/telemetria de argumentos de tools; limitar diretório de trabalho do shell à raiz do workspace | [fallback: se redaction automática não estiver disponível, bloquear logging de payload bruto de `web_fetch` até implementação] |
| R6 | Baseline "232/233 testes" ambíguo — 1 teste já falha antes da mudança, podendo mascarar regressão | @tech-solution-architect (ressalva pós-checkpoint) | Identificar nominalmente o teste falho pré-existente e justificar por que falha, antes de atribuir qualquer nova falha à mudança proposta | [fallback: se causa do teste pré-existente não puder ser determinada rapidamente, isolar via `skip` documentado e abrir rastreio separado] |

**Blast Radius:** 🔴 Sistêmico (compartilhado por ~100+ agents) — change control reforçado obrigatório.
**Safety net:** `test_sdk_session.py` + `test_permission_policy.py` (232/233 testes) executados antes e depois da mudança.

## 6. Rollback Plan

1. Reverter o diff de `agent_catalog.py` (mapa `_ALIAS_TOOLS_SDK_HEADLESS`) para o estado anterior (apenas `ask_questions`→`ask_user`).
2. Reverter o diff de `sdk_session.py` removendo o parâmetro `mcp_servers=` das duas chamadas de `client.create_session(...)` (linhas 577 e 1840).
3. Reverter qualquer alteração em `config.py` relativa a leitura de variáveis de ambiente de MCP servers.
4. Reverter eventual alteração em `permission_policy.py` (allowlist nova).
5. Re-executar `test_sdk_session.py` + `test_permission_policy.py` para confirmar retorno ao baseline 232/233 verde.
6. [fallback: se rollback via revert de diff não for suficiente (ex.: estado de sessão já persistido com mcp_servers), invalidar/expirar sessões headless ativas via `session_store.py` e forçar recriação.]

## 7. Plano de Implementação — Subtasks [S]

- [S] **Subtask 0 (paralela, não bloqueante para escrita, bloqueante para implementação):** reacionar `@tech-solution-architect` em modo `WF1_SECURITY_CHECKPOINT` com este rascunho de plano, ANTES do gate de aprovação R-064 final.
- [S] Subtask 1: Testes de caracterização (safety net) para `agent_catalog.py` e `sdk_session.py` — garantir cobertura do comportamento atual dos ~100+ agents antes de alterar.
- [S] Subtask 2: Red test isolado reproduzindo RC1 (alias ausente para tool de IDE/MCP) e RC2 (`mcp_servers` ausente na chamada `create_session`).
- [S] Subtask 3: Correção cirúrgica em `agent_catalog.py` (expansão do mapa de aliases) + `sdk_session.py` (parâmetro `mcp_servers=`) + `config.py` (leitura de env var existente, sem duplicação de secret).
- [S] Subtask 4: Implementar allowlist deny-by-default em `permission_policy.py` por agent (tools nativas de execução + lista fechada de MCP stdio servers homologados: context-mode/tavily/codegraph), incorporando R1-R5 (sem mapear tools de leitura para execução, tratando context-mode como execução, limitando escalonamento via run_subagent, env mínimo por servidor stdio, redaction de logs).
- [S] Subtask 5: Validação de não-regressão — suíte completa (232/233 + novos red-tests verdes).

## 8. Gate de Aprovação (R-064)

Este plano NÃO avança para implementação sem:
1. Parecer de segurança do `@tech-solution-architect` (WF1_SECURITY_CHECKPOINT) incorporado (ver §9).
2. Aprovação explícita do usuário via `ask_questions` (conduzida pelo `@bug-triage` após o parecer).

## 9. Parecer de Segurança (WF1_SECURITY_CHECKPOINT)

**Emitido por:** `@tech-solution-architect` (modo WF1_SECURITY_CHECKPOINT)

### Veredito do Checkpoint
- **Status**: **APROVADO COM RESSALVAS.** O plano pode seguir para o Gate R-064 depois que as ressalvas R1–R6 forem incorporadas ao texto (já incorporadas nesta revisão, ver §5 e Subtask 4).
- **Escopo analisado**: `agent_catalog.py` (`_ALIAS_TOOLS_SDK_HEADLESS`), `sdk_session.py:577/:1840` (`mcp_servers=`), `config.py` (leitura de credenciais) e `permission_policy.py`.
- **Superfície de risco**: os ~100+ agents headless passam a ter execução real de shell, novos processos stdio, saída para a rede (`web_fetch`/Tavily) e criação de subagents (`task`).

### Cobertura dos 4 riscos originalmente levantados

| # | Risco | Coberto? | Observação |
|---|---|---|---|
| 1 | `bash`/`powershell`/`shell` liberados para todos os agents | **Sim (após revisão)** | Decisão fixada: allowlist deny-by-default em `permission_policy.py`. |
| 2 | Credencial hardcoded ou duplicada em `config.py` | **Sim** | Critério de aceite e fallback (bloquear servidor se env var não existir) adequados. |
| 3 | Servidores MCP stdio executando processo arbitrário | **Sim (após revisão)** | Lista fechada (context-mode/tavily/codegraph) promovida a regra principal, não mais fallback. |
| 4 | Subtask 0 reacionando este checkpoint | **Sim** | Incluída na §7, bloqueante para a implementação. |

### Decisões fixadas
- **Risco 1:** allowlist por agent, negando tudo por padrão. Agents só de leitura/planejamento (architect, planners, triage, reviewers) não recebem shell. Tool sem mapeamento gera negação explícita e registrada em log.
- **Risco 3:** lista fechada de servidores homologados — apenas `context-mode`, `tavily`, `codegraph`. Comando/binário/versão fixos; `npx -y <pkg>@latest` proibido. Novo servidor exige novo Security Checkpoint. `codegraph` restrito a `@codegraph-engine` (R-045); Tavily restrito a `@deep-search`.

### Ressalvas adicionais incorporadas (R1–R6)
Ver tabela de riscos na §5 (linhas R1 a R6): aliases de leitura não podem escalar para execução; `context-mode` deve ser tratado como execução (equivalente a shell); `run_subagent`→`task` não pode escalar privilégio além do agent criador; processos stdio recebem `env` mínimo explícito (sem herança total); mitigação de cadeia de exfiltração/prompt injection (`web_fetch`/Tavily + shell/escrita); baseline "232/233" exige identificação nominal do teste pré-existente que falha.

### Próximo Passo
Devolver ao `@bug-triage` (motivo: "checkpoint_concluido") para conduzir o Gate R-064 (aprovação do usuário via `ask_questions`) com o plano já revisado.
