# Plano de Implementação — Context Insight Visualizer

## Pré-Voo de Execução

- **Escopo**: implementar `tools/context-insight-visualizer/` — dashboard standalone (schema + generator Python + template Angular Material 3) que transforma os dados locais do Context Mode (`~/.claude/context-mode/sessions/*.db`, `stats-pid-*.json`, `~/.claude/context-mode/content/*.db`) em KPIs e cards de insight, replicando o padrão arquitetural validado de `tools/codegraph-visualizer/` (generator/ → schemas/ → template/ → dist/, bundler com placeholders `__INJECT_*__`).

- **Achados relevantes**: não existe `package.json` na raiz nem em `tools/`; `codegraph-visualizer` também não usa npm (100% Python + HTML/JS puro) — integração npm tratada como opcional/N-A. Não existe `tools/README.md` central — governança de tools é feita via `README.md`/`PLAN.md`/`ROADMAP.md` locais de cada ferramenta.

- **R-038/R-043/R-044 aplicam-se integralmente**: `dist/` e dados locais nunca commitados; exemplos genéricos; caminhos absolutos nunca hardcoded em doc.

- **Critério de falha tolerável**: banco SQLite ausente/corrompido, `stats-pid-*.json` ausente, plataforma sem `~/.claude` (Windows/JetBrains) → emitir warning em `meta.warnings[]` e prosseguir com dataset parcial. Nunca abortar por fonte de dados ausente.

- **Bloqueantes absolutos**: exposição de conteúdo real de prompts/arquivos do usuário em artefato commitável (R-044), commit autônomo (R-003), credenciais (R-010).

## Estrutura de Fases & Ações

### Fase 0 — Scaffolding

- [x] **`S`** Etapa 0.1: Criar estrutura `tools/context-insight-visualizer/{schemas,generator,template/{styles,scripts},dist}/` + `.gitignore` (isola `dist/*.html`, `*.local.*`).  
  *(fallback: se pasta já existir parcialmente, mesclar sem sobrescrever arquivos presentes)*
### Fase 1 — Contrato de Dados (fundação, bloqueia Fases 2 e 3)

- [x] **`S`** Etapa 1.1: `schemas/insight-data.schema.json` (JSON Schema draft 2020-12): `version`, `meta{generatedAt, sourcePaths[], warnings[]}`, `kpis{sessionsCount, readWriteRatio, compactRate, errorRatePct, promptsPerSession}`, `sessions[]`, `timeSeries[]`, `insightsActions[]{severity: FYI|NICE|HEADS_UP, title, description, metricRef, recommendation}`.  
  *(fallback: publicar v1.0.0 mínima só com kpis core; expandir `sessions[]/timeSeries[]` em iteração seguinte)*
### Fase 2 — Generator Backend **`P`** (paralelo à Fase 3; ambas dependem só da Fase 1)

- [x] **`P`** Etapa 2.1.a: Sub-reader `session_events/session_meta/tool_calls` (multi-DB glob `sessions/*.db`).  
  *(fallback: caminho `~/.claude` ausente → tentar `~/.config/JetBrains/**/context-mode`; se nenhum existir, retornar `[]` + warning)*
- [x] **`P`** Etapa 2.1.b: Sub-reader `stats-pid-*.json` (snapshots de processo).  
  *(fallback: JSON malformado → pular arquivo individualmente, não abortar o glob)*
- [x] **`P`** Etapa 2.1.c: Sub-reader `content/*.db` (bases de chunks, somente metadados agregados — contagem/tamanho, nunca conteúdo bruto por R-044).  
  *(fallback: schema de tabela divergente → tentar introspecção via `PRAGMA table_info` antes de query fixa)*
- [x] **`S`** Etapa 2.1.d: Agregador de convergência (`extractor.py::extract()`), depende de 2.1.a/b/c.  
  *(fallback: fonte parcial ausente → preencher campo com `null`/`0` e registrar em `meta.warnings`, nunca lançar exceção não tratada)*
- [x] **`S`** Etapa 2.2: `insights_engine.py` — cálculo determinístico de KPIs (Sessions, Read:Write ratio, Compact Rate, Error Rate, Prompts/session) + regras de negócio dos cards FYI/NICE/HEADS UP com thresholds documentados.  
  *(fallback: threshold não configurável externamente → hardcode com constante nomeada + comentário, documentar em README)*
- [x] **`S`** Etapa 2.3: `template_bundler.py` — compilador que injeta CSS/JS/dados no template (replica padrão `codegraph-visualizer/generator/template_bundler.py`: ordem fixa de concatenação + placeholders `__INJECT_BUNDLE_STYLES__`/`__INJECT_BUNDLE_SCRIPTS__`/`__INJECT_RAW_*__`).  
  *(fallback: arquivo `styles/scripts` individual ausente → pular com warning, não interromper bundle)*
- [x] **`S`** Etapa 2.4: `generate.py` — CLI entrypoint (`--output dist/context-insight.html`, `--serve`, `--port 4747`).  
  *(fallback: porta 4747 ocupada → incrementar porta automaticamente e avisar no stdout)*
### Fase 3 — Template Frontend **`P`** (paralelo à Fase 2)

- [x] **`S`** Etapa 3.1: `template/index.html` — shell Angular Material 3 (Navigation Rail, AppBar, Top Cards, Panels de gráfico, cards Insights & Actions) com placeholders de injeção.  
  *(fallback: sem acesso à CDN de Material Symbols/Roboto offline → fallback de fonte de sistema declarado em CSS)*
- [x] **`P`** Etapa 3.2: `template/styles/*.css` (tokens M3, main, cards, charts, dark-theme).  
  *(fallback: token M3 específico ausente na spec → usar valor aproximado documentado com comentário)*
- [x] **`P`** Etapa 3.3: `template/scripts/*.js` — renderizadores Canvas/SVG/DOM puro sem npm pesado (`state.js`, `charts.js`, `insights.js`, `table.js`, `app.js`).  
  *(fallback: Canvas não suportado no ambiente → degradar para tabela HTML simples equivalente)*
### Fase 4 — Documentação (sequencial, depende de Fases 1–3)

- [x] **`S`** Etapa 4.1: `README.md` — objetivo, arquitetura, estrutura do módulo, comandos, fontes de dados suportadas e fallbacks de plataforma.  
  *(fallback: comando ainda não implementado → marcar explicitamente como "planejado")*
- [x] **`S`** Etapa 4.2: `PLAN.md` consolidado (este documento), com fases marcáveis `[x]` conforme execução.

### Fase 5 — Governança & Integração

- [x] **`S`** Etapa 5.1: Registro em governança — entrada mencionando a ferramenta no `CHANGELOG.md` raiz (não há `tools/README.md` centralizado hoje).  
  *(fallback: se necessário índice central de tools, oferecer via `ask_questions` antes de criar `tools/README.md` novo — R-009)*
- [x] **`S`** Etapa 5.2: Integração npm — sem precedente de `package.json` no repo; manter `python generate.py` como interface oficial; não criar `package.json` sem confirmação explícita.  
  *(fallback: se confirmado, tratar como nova subtask fora deste plano)*
### Fase 6 — Validação (sequencial, depende de tudo)

- [x] **`S`** Etapa 6.1: Teste end-to-end com dados reais locais (`~/.claude/context-mode/...`) gerando `dist/context-insight.html` e abrindo via `file://`.  
  *(fallback: sem dados reais na máquina → gerar fixtures sintéticas mínimas em `tests/fixtures/` para smoke test)*
- [x] **`S`** Etapa 6.2: Validação round-trip do schema (extractor → schema → bundler) com dataset mínimo e máximo.  
  *(fallback: lib de validação JSON Schema indisponível → validação manual campo a campo documentada)*
- [x] **`S`** Etapa 6.3: Checklist R-038 (genericidade) + R-044 (anonimização) aplicado a README/PLAN antes do fechamento.  
  *(fallback: caminho absoluto real encontrado em doc → substituir por placeholder genérico)*
## Critério de Pronto (Definition of Done)

- [x] `python generate.py` produz `dist/context-insight.html` executável standalone via `file://`, sem erros de console.
- [x] KPIs (Sessions, Read:Write ratio, Compact Rate, Error Rate, Prompts/session) aparecem com valores numéricos reais quando há ≥1 sessão válida.
- [x] Cards Insights & Actions renderizam corretamente por severidade (FYI/NICE/HEADS UP/FIX THIS) conforme regras determinísticas.
- [x] `schemas/insight-data.schema.json` valida sem erro contra saída real do `extractor.py`.
- [x] Fallbacks de caminho (`~/.claude` vs `~/.config/JetBrains`) testados (real ou mock).
- [x] `generate.py` suporta `--output`, `--serve`, `--port` sem exceção não tratada.
- [x] `README.md`/`PLAN.md` presentes, em PT-BR, aprovados no checklist R-038/R-044.
- [x] Nenhuma escrita de `package.json` ou registro central novo sem confirmação explícita (R-009).

## Estimativa de Risco

| Item | Risco | Justificativa | Mitigação |
|---|---|---|---|
| Sub-readers multi-fonte (SQLite/JSON) | Médio | Schemas de DB podem variar entre versões do Context Mode | Introspecção via `PRAGMA table_info` antes de query fixa |
| Regras de insight (insights_engine) | Médio | Thresholds de negócio são subjetivos sem doc formal prévia | Documentar constantes no README, revisável |
| Frontend vanilla (template) | Baixo | Padrão já validado em `codegraph-visualizer` | Reuso direto do bundler |
| Integração npm | Baixo (evitado) | Sem precedente no repo | Não implementar sem confirmação |
| Anonimização de doc | Médio | Fácil vazar caminho absoluto real em exemplo | Checklist obrigatório antes do fechamento |

## Atualização Arquitetural — `context-mode` v2.1.10
- Suporte completo ao banco unificado `projects/<projectKey>/context.db` (schema v6: `events`, `sources`, `chunks` FTS5, `meta`).
- Cálculo de economia de tokens/bytes via `sandbox_bytes` e `returned_bytes`.
- Filtro automático de sessões sintéticas do `context-mode doctor`.
- Retrocompatibilidade preservada via `--legacy-v1`.
