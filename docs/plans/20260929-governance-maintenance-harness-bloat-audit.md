# Plano de Planejamento — Auditoria e Poda de Harness Bloat na Governança

> **Workflow Canônico**: `WORKFLOW-GOVERNANCE-MAINTENANCE` (R-050.5)
> **Gerado via**: `/strategic-review` (prompt chaining — R-033), 3 etapas sequenciais validadas
> **Data**: 2026-09-29
> **Autoria da cadeia**: `@deep-search` (pesquisa) → `@agent-auditor` (diagnóstico) → `@refactor-planner` (plano faseado)
> **Materialização**: Root Orchestrator (R-064-d), pois os 3 agents da cadeia são Read-Only/Advisory
> **Status**: 🟡 Aguardando aprovação humana explícita (nenhuma fase iniciada, nenhum arquivo tocado)

---

## 1) Objetivo e Motivação

Endereçar 4 riscos estruturais identificados na avaliação estratégica do framework de governança `deep-agents-copilot`:

1. **Bloat normativo sem medição empírica** — 64 regras (`R-001..R-064`) + 36+ agents + 69 skills, sem nenhum mecanismo que meça quantas regras são efetivamente citadas/violadas em sessões reais versus apenas declaradas (risco de degradação de compliance sob pressão de contexto — "context rot").
2. **Sync de metadados incompleto entre agents homogêneos** — 3 ferramentas de sincronização existem e têm gate `--check` cablado em CI, mas cobrem campos parciais e não compartilham fonte de verdade única.
3. **Enforcement de regras críticas (R-053/R-062/R-063) é 100% textual**, sem verificação mecânica real no hook `context-mode.json` — dependente de disciplina do modelo, não de bloqueio determinístico.
4. **Evals rotulados como "behavioral" são na prática checagem de schema/substring**, e não há evidência de que algum ciclo real de poda de regras (`R-061(d)` "Delete e Observe") já foi executado — o histórico normativo é 100% aditivo.

**Motivação de negócio**: modelos mais fracos (ou fortes sob pressão) degradam compliance com volume normativo alto; a própria base já documenta esse risco (R-021.1, R-061, skill `harness-engineering-patterns`) mas nunca mediu nem podou empiricamente — há lacuna entre diagnóstico declarado e ação executada.

---

## 2) Escopo Delimitado e Artefatos Impactados

| Frente | Artefatos-alvo | Blast Radius Estimado |
|---|---|---|
| **A — Telemetria de citação R-xxx** | `tools/otel-langfuse/*`, `tests/governance_audit/*` | Médio (novo mecanismo, sem tocar runtime existente) |
| **B — Sync de metadados** | `tools/agent_protocol_sync/`, `tools/agent_source_docs_sync/`, `tools/agentcard_exporter/`, `.github/workflows/routing-quality-gate.yml`, 22 arquivos `.prompt.md` | Pequeno a médio (novo script + linha de CI) |
| **C — Enforcement mecânico vs. textual** | `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/hooks/context-mode.json`, `tests/governance_audit/test_context_mode_precedence_governance.py`, `test_root_agent_impersonation_governance.py` | Crítico (>120 arquivos dependem de `CLAUDE.md`) — mas fases desta frente são documentais/ADR, não mutação de hook |
| **D — Evals behaviorais + lifecycle** | `tests/evals/`, `tests/routing_unit/`, `tests/operational_flow/`, `CHANGELOG.md` | Pequeno a grande (relocação de 4 arquivos + novos fixtures + ciclo de GC) |

**Fonte de verdade da evidência**: diagnóstico read-only do `@agent-auditor` (Seção 4 deste documento) com referência `arquivo:linha` para cada achado.

---

## 3) Não-Escopo Explícito

- ❌ Não cria nenhum agent novo (avaliado e rejeitado previamente — ver `strategic-review.prompt.md`).
- ❌ Não fixa `model:` premium permanente em nenhum catálogo (R-021).
- ❌ Não implementa migração do enforcement para o hook (`.github/hooks/context-mode.json`) nesta rodada — apenas produz o ADR de viabilidade (Fase 6). Implementação real, se aprovada, é um novo ciclo de planejamento.
- ❌ Não consolida os 3 sincronizadores em manifesto único nesta rodada — apenas produz o ADR de avaliação (Fase 4).
- ❌ Não remove nenhuma regra `R-xxx` nesta rodada — a remoção real (Fase 12) só ocorre após aprovação humana explícita da lista de candidatas gerada pela Fase 11, com tag de contingência de 30 dias.
- ❌ Nenhuma fase é executada automaticamente após aprovação deste documento — cada fase exige liberação explícita adicional (ver Seção 7).

---

## 4) Achados de Diagnóstico (Passo 2 — `@agent-auditor`, Read-Only)

| # | Achado | Evidência | Severidade |
|---|---|---|---|
| 1 | Gap de telemetria de disparo real — nenhum mecanismo mede citação/violação de regra em sessão real | `tools/otel-langfuse/*` (0 ocorrências de `R-\d{3}`); `CLAUDE.md` 351 linhas/64 regras únicas/195 menções; `.github/copilot-instructions.md` 462 linhas/36 regras/113 menções — apenas declaração estática | **Crítico** |
| 2 | "Evals" rotulados como behaviorais são checagem de substring/schema | `tests/evals/test_tool_selection_evals.py:1-23` (`assert "R-008" in claude_md`); `tests/evals/test_routing_accuracy_evals.py:1-41` (shape de dataset YAML) | **Alto** |
| 3 | `tests/routing_unit/` vazia apesar do nome sugerir suíte dedicada | `tests/routing_unit/__init__.py` (8 linhas, sem testes) | **Alto** |
| 4 | Enforcement mecânico do hook não verificável — decisão real está em binário externo opaco | `.github/hooks/context-mode.json` (0 refs a R-053/R-062/R-063); testes existentes validam apenas presença de string em `CLAUDE.md` | **Alto** |
| 5 | Campo `argument-hint` (`.prompt.md`) fora do escopo dos 3 sincronizadores | `tools/agent_protocol_sync/`, `tools/agent_source_docs_sync/`, `tools/agentcard_exporter/` — nenhum referencia `argument-hint` | **Médio** |
| 6 | Ausência de manifesto agregador único — 3 sync tools com fontes de verdade isoladas | `protocol_roles.json`, `required_source_docs_rules.json`, schema de agentcard separado | **Médio** |
| 7 | Ciclo de vida de regras 100% aditivo — 0 gaps em `R-001..R-064`, 0 testes de lifecycle | `CLAUDE.md` (range fechado sem remoção); `tests/governance_audit/*` (0 hits para `lifecycle\|orphan rule\|unused rule`) | **Médio** |

**Contraponto positivo constatado**: `CHANGELOG.md` linha ~889 mostra que poda real de **artefatos** (agents/prompts, ~1350 linhas removidas) já ocorreu — a prática de poda existe, mas nunca foi aplicada às **regras normativas** (`R-xxx`) propriamente ditas.

---

## 5) Grounding de Mercado (Passo 1 — `@deep-search`)

| Tema | Padrão de mercado consolidado | Fonte |
|---|---|---|
| Context/instruction bloat | "Context rot" — degradação por lost-in-the-middle; medição por telemetria de disparo real (não contagem de declaração); classificação estático vs. sob-demanda | Redis "Context rot explained" (2025); Liu et al. "Lost in the Middle" (TACL 2023/2024) |
| Sync de metadados entre agents homogêneos | Schema único (Agent Card) + manifesto agregador + validação de schema como **gate obrigatório de CI** | A2A Protocol "AgentCard"; Palo Alto Networks "A2A Protocol Security Guide" (2025) |
| Enforcement mecânico vs. textual | Prompt textual ≈ 95% compliance (probabilístico); hooks/permission handlers = 100% determinístico. Heurística: risco de consequência real não deve depender só de prompting | OWASP GenAI "Top 10 for Agentic Applications 2026"; Anthropic Claude Code "Hooks reference" |
| Golden dataset / behavioral evals | Cenário + outcome esperado avaliado via LLM-as-judge; dataset "vivo" curado de traces reais; gate de CI a cada mudança de prompt/chain/skill | DeepEval "AI Agent Evaluation Quickstart"; MLflow "Building Agent & LLM Evaluation Datasets" |
| Rule garbage collection | Regras versionadas como código: ciclo criação→revisão→deprecação→remoção; linter periódico sinalizando itens órfãos; Chesterton's Fence (registrar rationale antes de remover) | Unblocked "Rules-File Rot" (2026); Wire Blog citando estudo MSR 2026 (50% dos AGENTS.md nunca atualizados) |

**Lacunas reconhecidas pela pesquisa**: nenhum estudo peer-reviewed específico sobre "regras normativas de governança de agentes que nunca disparam" — extrapolação de padrões gerais de context/rules rot.

---

## 6) Plano Faseado (Passo 3 — `@refactor-planner`, DAG de 12 Fases)

**Estratégia**: Mikado Method (dependências entre telemetria/sync/evals) + Expand & Contract (relocação de testes mal localizados). Nenhuma Characterization Test nova é pré-requisito — os artefatos-alvo já têm cobertura declarativa; a lacuna é comportamental, não estrutural.

### FRENTE A — Telemetria de citação R-xxx

| Fase | Ação | Tipo | Depende de | Executor | Esforço | Prioridade |
|---|---|---|---|---|---|---|
| **1** | Especificar mecanismo de telemetria de citação `R-xxx` (design doc: enricher OTel vs. parser estático) | `[S]` | — | `@governance-factory` | Médio | Alta |
| **2** | Criar `tests/governance_audit/test_rule_citation_audit.py` — audit dedicado que lista regras com 0 citações fora de `CLAUDE.md`/`copilot-instructions.md` | `[S]` | Fase 1 | `@governance-factory` | Médio | Alta |

### FRENTE B — Cobertura de sync automatizado

| Fase | Ação | Tipo | Depende de | Executor | Esforço | Prioridade |
|---|---|---|---|---|---|---|
| **3** | Criar `tools/agent_prompt_sync/sync_argument_hint.py` (mesmo contrato `--check`/`--apply`); cablar em `routing-quality-gate.yml` | `[P]` | — | `@governance-factory` | Pequeno | Média |
| **4** | ADR de avaliação de consolidação em manifesto/schema único (go/no-go, sem implementar) | `[S]` | Fase 3 | `@governance-factory` | Grande | Baixa |

### FRENTE C — Enforcement mecânico vs. textual

| Fase | Ação | Tipo | Depende de | Executor | Esforço | Prioridade |
|---|---|---|---|---|---|---|
| **5** | Documentar explicitamente em `CLAUDE.md` + `copilot-instructions.md` (espelhado) que R-053/R-062/R-063 são enforcement textual/CI-time, não mecânico/runtime | `[P]` | — | `@governance-factory` | Pequeno | Alta |
| **6** | ADR de viabilidade técnica de enforcement mecânico real no hook (`context-mode.json`) | `[S]` | Fase 5 | `@governance-factory` | Grande | Média |

### FRENTE D — Evals behaviorais + lifecycle de regras

| Fase | Ação | Tipo | Depende de | Executor | Esforço | Prioridade |
|---|---|---|---|---|---|---|
| **7** | Mover `test_tool_selection_evals.py` e `test_routing_accuracy_evals.py` de `tests/evals/` → `tests/governance_audit/` (renomear para refletir natureza estática) | `[S]` | — | `@governance-maintainer` | Pequeno | Média |
| **8** | Mover `workflow_eval_simulator.py` + `test_workflow_trajectories.py` de `tests/operational_flow/` → `tests/evals/`; atualizar path no CI gate | `[S]` | Fase 7 | `@governance-maintainer` | Pequeno | Alta |
| **9** | Remover `tests/routing_unit/` (esqueleto vazio, fan-in=0/fan-out=0 confirmado pelo grafo) | `[P]` | — | `@governance-maintainer` | Pequeno | Baixa |
| **10** | Expandir `tests/evals/` com 1-2 fixtures golden reais por workflow (repositório real anonimizado, R-044-safe) | `[S]` | Fase 8 | `@governance-factory` | Grande | Média |
| **11** | Criar `tests/governance_audit/test_rule_lifecycle.py` — modo report-only, sinaliza regras candidatas a deprecação | `[S]` | Fase 2 | `@governance-factory` | Médio | Alta |
| **12** | Executar 1 ciclo real de "governance garbage collection" (skill `continuous-garbage-collection-patterns`) — poda/deprecação em lote das candidatas aprovadas | `[S]` | Fases 4, 10, 11 | `@governance-maintainer` | Grande | Alta (mas só executável ao final) |

---

## 7) Matriz de Risco e Mitigação

| Risco | Severidade | Mitigação |
|---|---|---|
| Modificar `CLAUDE.md`/`copilot-instructions.md` sem espelhar o outro | Alta | Gate Out obrigatório nas Fases 5 e 12 exige diff simétrico validado por `tests/governance_audit` |
| Teste de lifecycle (Fase 11) virar gate bloqueante prematuro | Média | Modo report-only inicial; só bloqueante após ciclo de GC (Fase 12) validado por decisão humana |
| CI quebrar durante relocação de arquivos (Fases 7-8) | Média | Sequenciamento estrito + atualização do `routing-quality-gate.yml` no mesmo commit atômico |
| Manifesto único (Fase 4) criar acoplamento excessivo entre 4 ferramentas hoje independentes | Média | Tratado como ADR não-vinculante; migração real exige novo ciclo de planejamento dedicado |
| Fixtures golden (Fase 10) vazarem dado real não anonimizado | Alta | Gate In explícito de validação R-044-safe antes de aceitar a fixture |
| Ciclo de GC (Fase 12) remover regra ainda referenciada indiretamente | Alta | Tag pré-GC + janela de contingência de 30 dias + dependência estrita das Fases 4/10/11 |

---

## 8) Critério de Aceite e Definition of Done

- [ ] Cada fase liberada individualmente via aprovação humana explícita (`ask_questions`) antes do handoff ao executor correspondente.
- [ ] Nenhuma fase avança sem seu Gate In satisfeito (dependências declaradas na Seção 6).
- [ ] Toda fase que toca `CLAUDE.md` ou `copilot-instructions.md` mantém ambos espelhados (validado por `tests/governance_audit`).
- [ ] CI (`routing-quality-gate.yml`) permanece 100% verde após cada fase.
- [ ] Fase 12 (GC real) só é executada após Fases 4, 10 e 11 concluídas e lista de poda aprovada explicitamente.
- [ ] `CHANGELOG.md` recebe entrada explícita registrando o ciclo de GC ao final da Fase 12.

---

## 9) Próximo Passo Mínimo

Este documento consolida a cadeia `/strategic-review` completa (pesquisa → diagnóstico → plano). **Nenhuma fase foi iniciada.**

Aguardando decisão humana via `ask_questions` (Passo 4 do `/strategic-review`):
- Aprovar integralmente as 12 fases (execução ainda exige liberação individual por fase);
- Aprovar parcialmente (selecionar frentes A/B/C/D ou fases específicas);
- Rejeitar e encerrar o ciclo aqui.

