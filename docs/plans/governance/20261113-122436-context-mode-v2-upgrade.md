---
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-13"
related-planning-doc: "N/A"
allowed_files:
  - ".github/agents/*.agent.md"
  - ".github/agents/templates/*.md"
  - ".github/prompts/*.prompt.md"
  - ".github/prompts/templates/*.md"
  - ".github/skills/context-mode/**"
  - ".github/skills/{agent-contracts,code-tracing,efficient-batch-code-modification,embedded-runtime-governance,git-governance,governance-audit-patterns,governance-factory-patterns,integration-contract-analysis,project-scanner,task-decomposition-patterns,tavily,terminal-governance}/**"
  - ".github/skills/.index.json"
  - ".github/copilot-instructions.md"
  - ".github/hooks/**"
  - ".config/*.json"
  - ".aiassistant/rules/00-copilot-bridge.md"
  - ".a2a/agentcards/*.agentcard.json"
  - "CLAUDE.md"
  - "AGENTS.md"
  - "README.md"
  - "CHANGELOG.md"
  - "docs/agent-context/context-mode.md"
  - "docs/context/setup-context-mode-intellij.md"
  - "docs/architecture/{BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER,EVALS_TEST_STRATEGY}.md"
  - "tests/governance_audit/**"
  - "tools/agent_protocol_sync/**"
  - "tools/context-insight-visualizer/generator/insights_engine.py"
  - "apps/web/copilot/toolLabels.ts"
  - "deploy/local-chat-gateway/src/local_chat_gateway/{permission_policy,sdk_session}.py"
  - "deploy/local-chat-gateway/tests/unit/test_{permission_policy,sdk_session}.py"
---

# Plano de Governança — Upgrade context-mode v1 → v2.1.10

## 1. Escopo da manutenção e achados

**Contexto**: context-mode v2.1.10 operacional (ctx_doctor: D1/D2/D5/D5b/D6–D11 PASS; D3 FAIL; D4 WARN). Tools v1→v2: `ctx_execute_file`→`ctx_execute(file=…)` (CTX_FILE); `ctx_batch_execute`→`ctx_batch`; `ctx_fetch_and_index`→`ctx_index(url=…)`; `ctx_search` exige `queries: [...]`; novas `ctx_resume`, `ctx_doctor`, `ctx_upgrade`, `ctx_purge`. Env: `CONTEXT_MODE_DATA_DIR` substitui `CONTEXT_MODE_DIR`/`INSIGHT_SESSION_DIR`/`INSIGHT_CONTENT_DIR`/`CONTEXT_MODE_PROJECT_DIR`. `server.mjs` exige `--agent <id>`.

### 1.1 Diagnóstico D3 (host config) e D4 — evidência (inspeção read-only de `~/.copilot`; `setup --print` não executado)
- `~/.copilot/mcp-config.json` contém apenas o server `code-review-graph` → **sem entrada MCP context-mode** para o host `copilot-cli` ("wrong: MCP entry").
- `~/.copilot/jetbrains-copilot-hooks.json` sem referência a context-mode; único hook existente é `~/.copilot/hooks/context-mode-vscode.json` (SessionStart etc. via `hook.mjs --agent vscode`, formato v1) → **sem hooks `copilot-cli` v2** ("wrong: hook entries").
- Em outras palavras: o D3 avalia o *host* `copilot-cli` (arquivos em `~/.copilot`), não o IntelliJ/JetBrains `mcp.json` (que funciona, D6 PASS). Fix oficial: `context-mode setup --agents copilot-cli` (idealmente precedido de `--print` para revisar o diff). Ação fora do repo, executada pelo usuário/humano com aprovação (não é edição de artefato do catálogo).
- D4 WARN: `~/.copilot/context-mode/{content,sessions}` = data dir v1; migrar/limpar via `ctx_purge`/`ctx_upgrade` após confirmar que `~/.context-mode` (CONTEXT_MODE_DATA_DIR) está ativo. Nota: `D:\Dev\...\context-mode\hook.mjs --agent vscode` coexiste; validar double-fire (D5b PASS hoje).

### 1.2 Inventário de referências legadas (214 arquivos com algum hit; escopo textual .md/.py/.json/.ts/.ps1/.sh)
| Grupo | Arquivos | Legado encontrado |
|---|---|---|
| `.github/agents/*.agent.md` | 30 de 30 (frontmatter `tools:` + corpo) | `context-mode/ctx_batch_execute`, `ctx_execute_file`, `ctx_fetch_and_index` |
| `.github/agents/templates/` | agent-template, operational-agent, research-agent, router-agent | idem (Q2) |
| `.github/prompts/*.prompt.md` | 22 de 22 (add-project-context, agent-router, commit, connect-integration-graphs, craft-prompt, ctx-checkpoint, ctx-doctor, ctx-insight, ctx-resume, ctx-start, ctx-status, deep-search, del-project-context, eval-workflows, health, implement, init-context, plan, review, strategic-review, validate, visualize-graph) + `prompts/templates/prompt-template.md` | idem |
| `.github/skills/` (20 arquivos) | context-mode/{SKILL.md (11/27/8 ocorrências), examples/hierarquia-ferramentas.md, references/detailed-patterns-and-examples.md}; efficient-batch-code-modification (SKILL + references); governance-audit-patterns (SKILL + references/smells-catalog-detailed.md); terminal-governance (SKILL + references); code-tracing; tavily (SKILL + examples); agent-contracts; embedded-runtime-governance; git-governance; governance-factory-patterns/references; integration-contract-analysis; project-scanner; task-decomposition-patterns; `.index.json` | idem |
| Instruções raiz | `.github/copilot-instructions.md` (2/8), `CLAUDE.md` (2/10), `AGENTS.md`, `README.md`, `CHANGELOG.md` (histórico: **não reescrever**, apenas adicionar entrada), `.aiassistant/rules/00-copilot-bridge.md` | idem |
| `.github/hooks/` | `ctx-sequence-guard.ps1`, `ctx-sequence-guard.sh`, `README.md` | nomes de tools no guard de sequência (**impacto funcional**: hook pode deixar de detectar `ctx_batch`) |
| `.a2a/agentcards/` | 52 agentcards JSON | skills/tools declaradas com nomes v1 (derivados dos agents — regenerar, não editar à mão) |
| `docs/` | `docs/agent-context/context-mode.md`; `docs/context/setup-context-mode-intellij.md` (**único** com `CONTEXT_MODE_DIR`, `INSIGHT_SESSION_DIR`, `INSIGHT_CONTENT_DIR`, `CONTEXT_MODE_PROJECT_DIR`; sem `--agent`); `architecture/BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md`; `architecture/EVALS_TEST_STRATEGY.md`; `docs/plans/**` (12 planos — **histórico imutável**, excluir) | idem |
| Runtime/apps | `apps/web/copilot/toolLabels.ts` (rótulos já incluem doctor/upgrade/purge; faltam `ctx_batch`, `ctx_resume`); `deploy/local-chat-gateway/.../permission_policy.py`, `sdk_session.py` (+2 testes unit: allowlist/payload de `ctx_execute_file`(`path`) e `ctx_batch_execute`) | **impacto funcional**: política de permissão pode negar `ctx_batch` e o parâmetro `file` |
| `tools/` | `agent_protocol_sync/{sync_execution_protocol.py, _execution-protocol-fragment.md, README.md}`; `context-insight-visualizer/generator/insights_engine.py` | cláusulas `CLAUSE_BATCH_OR_EXEC`/`CLAUSE_GATHER_ONLY` hardcoded com `ctx_batch_execute` (**gerador Q2**) |
| Config antiga | `server.mjs` sem `--agent`: 0 ocorrências no repo; env v1 apenas em `setup-context-mode-intellij.md` | — |

### 1.3 Smells (governance-audit-patterns § 2)
| Smell | Local(is) | Severidade | Agent |
|---|---|---|---|
| 2.26 (MCP Tool Chaining) — enforcement ancorado em nome de tool inexistente na v2 | agents ×30, templates ×4, skills, `sync_execution_protocol.py`, `ctx-sequence-guard.*` | **Bloqueador** (tool `ctx_batch_execute`/`ctx_execute_file` não existe mais; frontmatter `tools:` não resolve) | @governance-factory |
| 2.24 / R-008 / R-056 (context-mode obrigatório) — frontmatter com tools inválidas rebaixa para fallback nativo | agents ×30 | **Bloqueador** | @governance-factory |
| Drift doc↔runtime (config v1 em guia de setup) | `docs/context/setup-context-mode-intellij.md`, `docs/agent-context/context-mode.md` | **Alto** | @docs-engineer |
| Drift runtime gateway/UI | `permission_policy.py`, `sdk_session.py`, `toolLabels.ts` | **Alto** | @governance-maintainer |
| Testes governança travados no nome v1 (falso-verde/falso-vermelho) | `tests/governance_audit/*` ×6 | **Alto** | @governance-maintainer |
| 2.12 (duplicação cross-artefato dos nomes) | skills/agents/prompts/instructions | Sugestão (reduzir hardcode via skill context-mode como fonte única) | @governance-factory |
| Agentcards derivados | `.a2a/agentcards` ×52 | Sugestão (regenerar) | @governance-maintainer |

## 2. Artefatos afetados e `allowed_files`
Ver frontmatter. Exclusões explícitas: `docs/plans/**` (histórico), entradas antigas de `CHANGELOG.md`, qualquer arquivo em `~/.copilot` e `mcp.json` do IDE (fora do repo).

## 3. Plano de correção em lote (Plan-Then-Batch, R-046/R-059)
**Mapa canônico de substituição** (fonte única: `.github/skills/context-mode/SKILL.md`):
| v1 | v2 |
|---|---|
| `ctx_execute_file(path, language, code)` | `ctx_execute({language, code, file})` (acesso via `CTX_FILE`) |
| `ctx_batch_execute(commands, queries)` | `ctx_batch` (validar assinatura com `ctx_batch` schema real antes de reescrever cláusulas) |
| `ctx_fetch_and_index(url)` | `ctx_index({url})` |
| `ctx_search(query/queries)` | `ctx_search({queries:[…], scope?, sort?, source?})` |
| — | `ctx_resume`, `ctx_doctor`, `ctx_upgrade`, `ctx_purge` (documentar; `ctx_stats` mantido) |
| `CONTEXT_MODE_DIR`/`INSIGHT_*`/`CONTEXT_MODE_PROJECT_DIR` | `CONTEXT_MODE_DATA_DIR` (padrão `~/.context-mode`) |
| `server.mjs` | `server.mjs --agent copilot-cli` + `cd /d <workspace>` no JetBrains |

Ondas (aprovação item a item, R-033/R-031; cada onda = UMA chamada `ctx_execute` JS em lote, limiar ≥2 arquivos):
1. **Onda 0 (pré-requisito, humano)**: `context-mode setup --print copilot-cli` → `setup --agents copilot-cli`; confirmar D3 PASS; tratar D4. Confirmar nomes/assinaturas reais via `ctx_doctor`/schema MCP (sem assumir `ctx_batch`).
2. **Onda 1 — Fonte única (@governance-factory)**: `skills/context-mode/**` + `efficient-batch-code-modification`, `terminal-governance`, `governance-audit-patterns` (+ smells catalog; adicionar novo critério em 2.26 para nomes v2), demais skills do inventário.
3. **Onda 2 — Geradores/templates (Q2) (@governance-factory)**: `agents/templates/*`, `prompts/templates/prompt-template.md`, `tools/agent_protocol_sync/{sync_execution_protocol.py,_execution-protocol-fragment.md,README.md}` → rodar o sync para propagar às cláusulas (cuidado: cláusulas hardcoded com `ctx_batch_execute`).
4. **Onda 3 — Peers (Q1) (@governance-factory)**: 30 agents (frontmatter `tools:`: `context-mode/ctx_batch`, remover `ctx_execute_file`/`ctx_fetch_and_index`, avaliar adicionar `ctx_resume` apenas onde cabível) + 22 prompts (`ctx-doctor`, `ctx-resume`, `ctx-status`, `ctx-start`, `ctx-checkpoint`, `ctx-insight` requerem revisão semântica) + `copilot-instructions.md`, `CLAUDE.md`, `AGENTS.md`, `.aiassistant/rules`; regenerar `.a2a/agentcards` e `.index.json`.
5. **Onda 4 — Docs (@docs-engineer)**: reescrever `setup-context-mode-intellij.md` (`--agent copilot-cli`, `CONTEXT_MODE_DATA_DIR`, remover 3 vars legadas), `agent-context/context-mode.md`, 2 docs de arquitetura, `README.md`; `CHANGELOG.md` nova entrada.
6. **Onda 5 — Runtime e sensores (@governance-maintainer)**: `.github/hooks/ctx-sequence-guard.{ps1,sh}` + README; `permission_policy.py`, `sdk_session.py` + testes unit; `toolLabels.ts` (`ctx_batch`, `ctx_resume`); `insights_engine.py`; testes governance_audit (Onda 6).
7. **Onda 6 — Testes (Q3)**: ver §5.

Compatibilidade: avaliar janela dual (aceitar v1+v2 nos sensores) apenas se algum host (ex.: VS Code com `hook.mjs --agent vscode` v1) ainda expuser tools v1; decisão humana.

## 4. Alternativas Rejeitadas
- **Alias v1 mantido em agents/tools**: rejeitado — tools inexistentes na v2 quebram o frontmatter e o enforcement R-008/R-056.
- **sed/replace global cego**: rejeitado — `ctx_execute_file`→`ctx_execute` exige mudança semântica (param `file`), `ctx_search` exige `queries[]`, `ctx_batch` pode ter assinatura distinta; reescrever cláusulas hardcoded no gerador.
- **Editar `docs/plans/**` e CHANGELOG histórico**: rejeitado (imutabilidade histórica).
- **Editar `~/.copilot` manualmente**: rejeitado — usar `context-mode setup` (R-057: o auditor não terceiriza edição de artefatos do catálogo; este passo é de ambiente do host).
- **Downgrade para v1**: rejeitado — v2 operacional e doctor majoritariamente PASS.

## 5. Reúso sistêmico (R-055) e sensores
- **Q1 (Peers)**: aplica-se a todos os 30 agents, 22 prompts, 20 skills, 52 agentcards, hooks, instruções raiz, docs e runtime (§1.2).
- **Q2 (Templates/geradores)**: atualizar `agents/templates/{agent-template,operational-agent,research-agent,router-agent}.md`, `prompts/templates/prompt-template.md`, `skills/templates` (se citar), `sync_execution_protocol.py` (constantes CLAUSE_*), `_execution-protocol-fragment.md`.
- **Q3 (Testes pytest)**: atualizar `tests/governance_audit/{test_context_mode_precedence_governance,test_ctx_execute_capability_profile,test_governance_smells,test_router_agents,test_sync_execution_protocol_invariants,test_database_consolidation_governance}.py` (asserts literais de `ctx_batch_execute`/`ctx_execute_file` — hoje ~40 ocorrências); `deploy/local-chat-gateway/tests/unit/test_{permission_policy,sdk_session}.py`; `tests/evals/test_tool_selection_evals.py` (revisar `ctx_execute`). **Criar novo teste** `tests/governance_audit/test_context_mode_v2_tool_names.py`: (a) nenhum agent/prompt/skill/template/instrução (exceto `docs/plans/**`, CHANGELOG) contém `ctx_execute_file|ctx_batch_execute|ctx_fetch_and_index|CONTEXT_MODE_DIR|INSIGHT_(SESSION|CONTENT)_DIR`; (b) toda tool `context-mode/ctx_*` em `tools:` ∈ allowlist v2 de 9; (c) agent com `ctx_execute` declara `ctx_batch`; (d) setup doc contém `--agent copilot-cli` e `CONTEXT_MODE_DATA_DIR`.

## 6. Rollback e critério de pronto
- **Rollback**: `git revert` por onda (commits atômicos por onda); `context-mode setup` é reversível via `ctx_upgrade`/backup dos arquivos de `~/.copilot` antes da Onda 0.
- **Pronto**: grep por termos legados = 0 fora das exclusões; `pytest tests/governance_audit deploy/local-chat-gateway/tests/unit` verde; `sync_execution_protocol.py` sem diff após rodar; `ctx_doctor` D3 PASS e D4 sem WARN; `toolLabels.ts` compila.

## Checklist
- [x] Frontmatter R-064 completo (`plan_type: governance`).
- [x] Persistência por executor; auditor Read-Only (R-057) — **ver nota**.
- [x] Conformidade com `docs/plans/<tipo>/` auditada (Smell 2.34).
- [x] Aprovação humana (Gate R-064) → `status: APPROVED`.

> Nota: materialização feita sob autorização explícita do usuário neste turno (R-064 hard-stop); ondas de mutação aguardam aprovação.
