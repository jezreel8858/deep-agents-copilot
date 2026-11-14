---
status: "APPROVED"
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-13"
related-planning-doc: "docs/plans/governance/20261113-122436-context-mode-v2-upgrade.md"
blast_radius: "tools/context-insight-visualizer/** + tests/context_insight_visualizer/** (isolado; sem impacto em .github/ catálogo, exceto hook declarado em .github/hooks/subagent-telemetry.json — somente verificação)"
allowed_files:
  - "tools/context-insight-visualizer/generator/extractor.py"
  - "tools/context-insight-visualizer/generator/generate.py"
  - "tools/context-insight-visualizer/generator/insights_engine.py"
  - "tools/context-insight-visualizer/hooks/record-subagent.js"
  - "tools/context-insight-visualizer/schemas/insight-data.schema.json"
  - "tools/context-insight-visualizer/template/scripts/*.js"
  - "tools/context-insight-visualizer/README.md"
  - "tools/context-insight-visualizer/PLAN.md"
  - "tests/context_insight_visualizer/**"
---

# Plano — Compatibilidade do context-insight-visualizer com context-mode v2.1.10

## 1. Escopo e achados

Fonte v2.1.10: `<repo-context-mode>\src\core\{store/schema.ts,contracts/constants.ts,project/config-dir.ts}`. Dados reais: `~/.context-mode/projects/1e8c9d7dc9a7925b/context.db` e `~/.config/JetBrains/context-mode/projects/{15fda5f3183577b8,1e8c9d7dc9a7925b,5f68bef7a6c66194,7bd000c8739f0783,fdf3c29fe281eebc}/context.db` (`PRAGMA user_version = 6`).

### 1.1 Descoberta de diretórios (Bloqueador)
| v1 (extractor.py L91-141, generate.py) | v2.1.10 |
|---|---|
| `~/.claude/context-mode/sessions/*.db` e `content/*.db` (+ variantes AppData\Roaming/Local\JetBrains) | Raiz de dados única: `$CONTEXT_MODE_DATA_DIR` (se não vazio, `resolve()`) senão `<home>/.context-mode` (`dataRootOf`, config-dir.ts) |
| Um .db por sessão/conteúdo | **Um SQLite por projeto**: `<DATA_ROOT>/projects/<projectKey>/context.db` (`PROJECTS_DIR_NAME`, `DB_FILE_NAME`); `projectKey` = 16 hex de sha256(realpath do git common dir) (`PROJECT_KEY_HEX_LEN=16`) — não deriva de `project_dir` |
| Sem `CONTEXT_MODE_DATA_DIR` | Variável obrigatória na descoberta |
| `sessions/stats-pid-*.json` | **Não existe em v2**; usar `events` kind `cost` e `meta` |
| — | Artefatos extras a ignorar: `context.db-wal`/`-shm` (abrir com `mode=ro` mantém leitura consistente do WAL; não copiar só o .db), `owners/*.pid`, `backups/`, `reports/doctor-*.md`, `plugins/`, `insight-cache/` (UI React da v1 em backups `v1-aside-*`) |
| JetBrains: `~/.config/JetBrains/context-mode/` contém **v2** (`projects/*`, `reports/`) e dados v1 em `backups/v1-aside-2026-11-13T21-40-52-883Z` | Descoberta deve excluir `backups/**` |

Observação: 6 DBs reais; 3 são amostras sintéticas do `ctx_doctor` (session_id `context-mode-doctor-hook-runs`, worktree em `%TEMP%\cm-doctor-runs-*`) e devem ser filtrados dos KPIs.

### 1.2 Schema SQLite (Bloqueador)
v2 (schema.ts, migrações 1→6): tabelas `events`, `sources`, `chunks` (FTS5), `chunks_tri` (FTS5 trigram contentless), `chunks_vocab` (fts5vocab), `line_units` (FTS5), `meta`, `sqlite_sequence`.

| Esperado pela v1 no extractor | Realidade v2.1.10 | Efeito |
|---|---|---|
| `session_meta(session_id, project_dir, started_at, last_event_at, event_count, compact_count)` | **Ausente**. Sessão = `DISTINCT events.session_id`; `worktree` substitui `project_dir`; início/fim = MIN/MAX(`created_at`) (epoch ms INTEGER, não ISO); `event_count` = COUNT; **sem `compact_count`** | `sessions` fica vazio (extractor só avisa) |
| `session_events(id,type,category,priority,data,created_at,session_id)` | `events(seq,session_id,worktree,agent,kind,tool,key,path,ok,exit_code,bytes,body,turn,sandbox_bytes,returned_bytes,created_at,accessed_at)`; `kind` ∈ {prompt,edit,cmd,toolerr,index,cost,decision}; sem `type`/`category`/`priority`/`data` | Perda de decisions, agent invocations, reads/writes, errors, prompts |
| `ev_type` (`decision`, `file_glob`, `find_files`, `file_read`, ...) | Mapear: `decision`→kind `decision` (body = resposta; tool `AskUserQuestion`, key `answers`/`option`); `prompt`→kind `prompt`; `edit`→kind `edit` (path); `cmd`→kind `cmd` (tool + key `Tool:cmd`); erros→`toolerr`/`ok=0`; leituras/globs → kind `cmd` com `tool` Read/Glob (verificar em dados reais) | Reescrita da classificação |
| `tool_calls(tool,calls,bytes_returned)` | **Ausente**. Agregar `events` por `tool`: COUNT, SUM(`returned_bytes`), SUM(`sandbox_bytes`) | `mcpTools` zerado |
| `sources(id,label,chunk_count,code_chunk_count,indexed_at,file_path)` | `sources(id,session_id,worktree,agent,kind[path/content/url],label,bytes_total,chunk_count,created_ts,created_at TEXT ISO,accessed_ts)`; sem `code_chunk_count`/`indexed_at`/`file_path` (usar `label` quando kind=path; labels path normalizados com `/` — migração v6) | SELECT quebra (coluna inexistente) → warning |
| `chunks(source_id,title,content_type,content)` | `chunks` FTS5: `source_id,session_id,worktree,agent,ord,body,title`; sem `content_type`/`content` (usar `body`); `length(body)`; **não** usar `chunks_vocab/chunks_tri` | SELECT quebra |
| Descoberta de tabelas via `sqlite_master type='table'` | Tabelas virtuais FTS5 aparecem como `table` com sombras `_data/_idx/_docsize/_config/_content` | Filtrar sombras |
| FTS5 | Python `sqlite3` precisa de FTS5 compilado para `SELECT` em `chunks` (usar `PRAGMA table_info` e leitura simples; em falha, degradar com warning) | Verificar |

### 1.3 Formato de eventos reais (amostra)
- `events.kind='cmd'`: `tool='ctx_execute'|'ctx_doctor'|'Bash'`, `key='ctx_execute:<código>'`, `agent='copilot-cli'`, `session_id='mcp:<uuid>'`, `body` truncado, `created_at` epoch ms.
- Contagem real (`1e8c9d7dc9a7925b` em ~/.context-mode): 23 `cmd` (sandbox_bytes 763.875 / returned_bytes 97.162) e 2 `toolerr`; **0 prompt/edit/decision/cost** → KPIs de prompts/decisões/economia ficarão vazios mesmo após migração (limitação da fonte, não bug; documentar).
- `worktree` pode ser `C:\Windows\System32` (cwd do servidor MCP) — não é confiável como projeto; fallback por `session_id` prefixo `mcp:`.
- Economia de tokens: derivar de `sandbox_bytes - returned_bytes` (≈ bytes/4 para tokens); `tokensSavedLifetime`/`dollarsSavedLifetime` não persistidos em v2. Formato do corpo de `cost` não observado em dados reais — **a validar** em `src/core/store/events`/hooks antes de implementar.

### 1.4 Demais componentes
| Arquivo | Achado | Severidade |
|---|---|---|
| `generator/extractor.py` (≈45 KB) | Todos os leitores v1 (`_read_session_databases`, `_read_stats`, `_read_content_databases`, L190-860) quebram. `subagent-telemetry.jsonl` em `~/.context-mode` (L448) não é escrito pela v2; manter só o JSONL do repo | Bloqueador |
| `generator/generate.py` | CLI `--sessions-dir/--content-dir` e help `~/.claude/context-mode/sessions` obsoletos; `meta.contentDbsCount` impresso | Alto |
| `generator/insights_engine.py` | Consome `statsPid.tokensSavedLifetime/dollarsSavedLifetime`, `session.compactCount`, `eventsSummary.*` — contrato interno; **preservar chaves** e alimentar do novo extractor; `compactCount` sempre 0 (insight de compactação deve degradar) | Alto |
| `hooks/record-subagent.js` | **Compatível**: independente do context-mode (stdin → JSONL em `logs/`). Pendência: confirmar payload JetBrains/Copilot CLI (`tool_name`/`toolName`), já tratado; sugestão de incluir `CONTEXT_MODE_DATA_DIR` não necessária | Sugestão |
| `otel-collector/receiver.py` | Sem dependência de context-mode; manter | N/A |
| `schemas/insight-data.schema.json` | Chaves top-level mantidas; ajustar `meta` (adicionar `contextModeVersion`, `dataRoot`, `projectKeys[]`, `schemaVersion`) e permitir `sessions[].compactCount` = 0 e `sources[].codeChunkCount` opcional | Alto |
| `generator/template_bundler.py` | Sem acesso a DB; sem mudança | N/A |
| `template/scripts/*.js` | `knowledge.js`/`search-view.js`/`sessions-view.js` usam `codeChunkCount`, `contentType`, `compactCount`, `projectName`; renderizar vazio/“n/d” em vez de quebrar; ocultar visões dependentes de dados ausentes | Alto |
| `README.md`/`PLAN.md` | Documentam diretórios v1 e `stats-pid` | Alto |
| `tests/context_insight_visualizer/test_agent_invocations.py` | Só cobre hook JSONL, bundler, padrões de agente e matriz Jira/MCP; **sem fixtures SQLite** — nenhuma cobertura de extração v1 nem v2 (gap) | Alto |

## 2. Artefatos afetados e allowed_files
Ver frontmatter. Nenhum arquivo do catálogo `.github/agents|skills|prompts` é alterado.

## 3. Plano de correção em lote (Plan-Then-Batch) — executor: @governance-maintainer
Aplicar tudo em **um único** `ctx_execute` (javascript, fs) all-or-nothing e `get_errors` agrupado ao final.

1. **extractor.py**
   - Substituir `resolve_default_directories` por `resolve_data_roots(custom_data_dir)`: ordem `--data-dir` > `$CONTEXT_MODE_DATA_DIR` > `~/.context-mode` > `~/.config/JetBrains/context-mode` (+ AppData JetBrains); retornar lista de `projects/*/context.db`, excluindo `backups`, `node_modules`.
   - Novo `_open_ro(db)` (`file:...?mode=ro` URI, `PRAGMA query_only=1`, `busy_timeout`), checar `PRAGMA user_version` (>=6 → v2; ausência de `events` → ignorar com warning).
   - `_read_events_v2`: sessões via GROUP BY `session_id` (min/max `created_at` ms → ISO UTC; `event_count`; `compactCount=0`; `projectName`=sanitize(`worktree`)); eventos por `kind`; decisões de `kind='decision'`; `toolUsage/mcpTools` por `tool`; erros por `ok=0`/`toolerr`; hourly por `created_at`.
   - `_read_cost_v2`: substitui `stats-pid` (sandbox_bytes/returned_bytes/tokens estimados), preenchendo `statsPid` com mesmas chaves.
   - `_read_content_v2`: `sources`(`label,kind,chunk_count,bytes_total,created_at`) e `chunks`(`source_id,title,length(body),substr(body,1,280)`, LIMIT 800) com try/except por FTS5.
   - Filtrar sessões de sanidade do doctor (`context-mode-doctor-hook-runs`, worktree sob `cm-doctor-runs-`).
   - Manter leitores v1 como fallback `legacy` (flag `--legacy-v1`) para não quebrar dados antigos em `backups/v1-aside-*`.
   - Preencher `meta`: `contextModeVersion` ("2.1.10"/"legacy"), `dataRoots`, `dbCount`, `schemaVersion`.
2. **generate.py**: adicionar `--data-dir`; manter `--sessions-dir/--content-dir` como alias deprecated (`--legacy-v1`); atualizar help e prints (`dbsFound`).
3. **insights_engine.py**: ler `meta.contextModeVersion`; degradar insights de compactação/economia quando dados ausentes; sem mudança de chaves.
4. **schemas/insight-data.schema.json**: novos campos de `meta`; `additionalProperties` conforme existente.
5. **template/scripts/*.js**: guardas para `undefined` em `codeChunkCount`, `contentType`, `compactCount`; badge de versão em `app.js`.
6. **hooks/record-subagent.js**: sem mudança funcional; adicionar comentário/README de independência de versão.
7. **README.md / PLAN.md**: documentar descoberta v2, `CONTEXT_MODE_DATA_DIR`, limitações (cost/prompt vazios) e `--legacy-v1`.

## 4. Plano de testes (@governance-maintainer cria; execução `pytest tests/context_insight_visualizer`)
- `conftest.py` com fixture que cria `projects/<key>/context.db` v2 (DDL de schema.ts v1-v6 simplificada; FTS5 `chunks` com `title`) populado com `cmd`, `toolerr`, `decision`, `prompt`, `edit`, `cost`.
- `test_v2_discovery.py`: `CONTEXT_MODE_DATA_DIR` (monkeypatch), fallback `~/.context-mode` e JetBrains, exclusão de `backups/`, WAL.
- `test_v2_events.py`: sessões, decisões, mcpTools, hourly, filtro do doctor, epoch ms→ISO.
- `test_v2_content.py`: sources/chunks (`body`/`title`), degradação sem FTS5.
- `test_v2_cost.py`: estimativa de tokens a partir de bytes.
- `test_legacy_v1.py`: fixture v1 mínima (`session_meta`/`session_events`/`stats-pid`) garantindo `--legacy-v1`.
- `test_schema_contract.py`: payload gerado valida contra `insight-data.schema.json` (jsonschema) para v2 e v1.
- Smoke manual: `python generator/generate.py --data-dir C:\Users\<user>\.context-mode` e JetBrains; conferir `meta.dbCount` = 1 e 5(−3 doctor).
- Manter testes atuais verdes.

## 5. Alternativas Rejeitadas
- Adapter que converte v2→tabelas v1 em SQLite temporário: duplica estado e perde `kind`.
- Apenas ajustar caminhos mantendo SQL v1: colunas/tabelas inexistentes.
- Consumir `ctx_stats` via MCP: não offline/determinístico.
- Remover suporte v1: perde dados de `backups/v1-aside-*`.

## 6. Reúso sistêmico (R-055)
- Q1: peers — outros consumidores de `~/.claude/context-mode`/`stats-pid`/`session_events` no repo (rodar grep na Etapa de execução, incl. `docs/`, `.github/skills/*context*`, `tests/governance_audit/`).
- Q2: N/A (ferramenta isolada, sem template canônico).
- Q3: criar testes pytest acima; considerar sensor em `tests/governance_audit/` que falhe se docs citarem `stats-pid`/`content/*.db` como layout atual.

## 7. Rollback e critério de pronto
- Rollback: `git checkout -- tools/context-insight-visualizer tests/context_insight_visualizer` (alterações restritas à allowlist).
- Pronto: pytest verde; `generate.py` gera `dist/context-insight.html` com ≥1 sessão e `meta.contextModeVersion` v2 nos dados reais; JSON valida no schema; docs atualizados; sem referência a layout v1 como padrão.

## Checklist
- [x] Frontmatter R-064 (`plan_type: governance`, DRAFT, approved false).
- [x] Persistência por @governance-maintainer/@docs-engineer; auditor Read-Only.
- [x] Aprovação humana (Gate R-064) concedida.
