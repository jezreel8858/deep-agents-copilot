---
plan_id: "gov-20261115-123014-plan-critic-lessons-shielding"
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
created_at: "2026-11-15"
updated_at: "2026-11-15"
related-planning-doc: "N/A"
review_verdict: PASS_WITH_NITS
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: PASS
session_id: "sess-20261115-plan-critic-lessons"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-gov-20261115-123014"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 0
  minors: 0
  nits: 2
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
rollback_plan: "1) git restore --source=HEAD -- .github/agents/agent-auditor.agent.md .github/agents/tech-solution-architect.agent.md .github/agents/bug-triage.agent.md .github/agents/requirements-analyst.agent.md .github/agents/governance-factory.agent.md .github/agents/backend/python/python-arch-advisor.agent.md .github/prompts/catalog.yaml .github/prompts/README.md .github/prompts/QUICK-START.md .github/skills/plan-conformance-patterns/SKILL.md .github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md .github/skills/governance-audit-patterns/references/plan-template-governance.md tests/governance_audit/test_template_sections.py tests/governance_audit/test_utility_slash_prompts_bypass.py tests/governance_audit/test_planning_doc_template_governance.py; 2) git clean -fd -- .github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md .github/prompts/plan-lessons-harvester.prompt.md tests/governance_audit/test_plan_lessons_harvester_governance.py; 3) git restore --source=HEAD -- docs/plans/architecture/20261114-200500-feature-r064-otel-correlation-critic-telemetry.md docs/plans/architecture/20261115-100000-synth-routing-eval-sqlite.md docs/plans/architecture/20261115-140000-synth-routing-graph-diagnostics.md docs/plans/architecture/20261115-170000-synth-workflow-triggers-diagnostics.md docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md docs/plans/bug-triage/20261114-184500-correcao-ci-subprojects-emnapi-governance-runner.md docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md docs/plans/governance/20260420-183000-router-header-line-breaks.md docs/plans/governance/20261114-120000-plan-critic-mermaid-counts-sync-enforcement.md docs/plans/governance/20261114-120000-revisor-cetico-universal-pre-hitl-r064.md docs/plans/governance/20261114-143000-evolucao-skills-guardrails-plan-critic-r067.md docs/plans/governance/20261114-210000-governance-maintenance-otel-handoff-hydration.md docs/plans/governance/20261115-160000-routing-graph-drift-and-gaps-remediation.md docs/plans/governance/20261115-183000-synth-waves-prompt.md docs/plans/implementation/20261114-181500-bug-fix-correcao-falhas-github-actions-ci.md docs/plans/implementation/20261114-190000-bug-fix-ci-subprojects-emnapi-governance-runner.md docs/plans/implementation/20261115-110000-feature-synth-routing-eval-sqlite.md docs/plans/implementation/20261115-150000-feature-synth-routing-graph-diagnostics.md docs/plans/implementation/20261115-173000-feature-synth-workflow-triggers-diagnostics.md docs/plans/requirements/20261114-200000-r064-otel-correlation-critic-telemetry.md"
allowed_files:
  - ".github/prompts/plan-lessons-harvester.prompt.md"
  - ".github/prompts/catalog.yaml"
  - ".github/prompts/README.md"
  - ".github/prompts/QUICK-START.md"
  - ".github/skills/plan-conformance-patterns/SKILL.md"
  - ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md"
  - ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md"
  - ".github/skills/governance-audit-patterns/references/plan-template-governance.md"
  - ".github/agents/agent-auditor.agent.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/bug-triage.agent.md"
  - ".github/agents/requirements-analyst.agent.md"
  - ".github/agents/governance-factory.agent.md"
  - ".github/agents/backend/python/python-arch-advisor.agent.md"
  - "tests/governance_audit/test_template_sections.py"
  - "tests/governance_audit/test_utility_slash_prompts_bypass.py"
  - "tests/governance_audit/test_planning_doc_template_governance.py"
  - "tests/governance_audit/test_plan_lessons_harvester_governance.py"
  - "docs/plans/architecture/20261114-200500-feature-r064-otel-correlation-critic-telemetry.md"
  - "docs/plans/architecture/20261115-100000-synth-routing-eval-sqlite.md"
  - "docs/plans/architecture/20261115-140000-synth-routing-graph-diagnostics.md"
  - "docs/plans/architecture/20261115-170000-synth-workflow-triggers-diagnostics.md"
  - "docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md"
  - "docs/plans/bug-triage/20261114-184500-correcao-ci-subprojects-emnapi-governance-runner.md"
  - "docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md"
  - "docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md"
  - "docs/plans/governance/20260420-183000-router-header-line-breaks.md"
  - "docs/plans/governance/20261114-120000-plan-critic-mermaid-counts-sync-enforcement.md"
  - "docs/plans/governance/20261114-120000-revisor-cetico-universal-pre-hitl-r064.md"
  - "docs/plans/governance/20261114-143000-evolucao-skills-guardrails-plan-critic-r067.md"
  - "docs/plans/governance/20261114-210000-governance-maintenance-otel-handoff-hydration.md"
  - "docs/plans/governance/20261115-160000-routing-graph-drift-and-gaps-remediation.md"
  - "docs/plans/governance/20261115-183000-synth-waves-prompt.md"
  - "docs/plans/implementation/20261114-181500-bug-fix-correcao-falhas-github-actions-ci.md"
  - "docs/plans/implementation/20261114-190000-bug-fix-ci-subprojects-emnapi-governance-runner.md"
  - "docs/plans/implementation/20261115-110000-feature-synth-routing-eval-sqlite.md"
  - "docs/plans/implementation/20261115-150000-feature-synth-routing-graph-diagnostics.md"
  - "docs/plans/implementation/20261115-173000-feature-synth-workflow-triggers-diagnostics.md"
  - "docs/plans/requirements/20261114-200000-r064-otel-correlation-critic-telemetry.md"
---
# Plano de Governança — Blindagem Anti-Reincidência dos Achados do `@plan-critic` e Slash Prompt `/plan-lessons-harvester`

> DRAFT materializado por `@docs-engineer`/`@governance-maintainer` a partir da emissão do `@agent-auditor` (100% Read-Only, R-064/R-057). Parecer do `@plan-critic` ainda NÃO emitido: `review_*` permanecem `PENDING` (sem autoatestado, lição T1-8).

## 1. Escopo da Manutenção e Achados

Varredura: `docs/plans/**` = 71 planos; 71 sem `lessons_extracted` (nenhum selado); 22 citam `@plan-critic` (14 com parecer estruturado). Histórico de sessão `context-mode` consultado (`BLOCKER/HIGH/…/REVISE_REQUIRED`): sem veredito divergente dos planos.

### 1.1 Matriz Consolidada de Achados do `@plan-critic` por plano e por `author`

| Plano (docs/plans/…) | `author` | Veredito / rodadas | Achados (classe) |
|---|---|---|---|
| governance/20260420-183000-router-header-line-breaks | @agent-auditor | PASS_WITH_NITS / 2 | HIGH: sem teste determinístico do regex do extrator B2 (C4); 1 NIT |
| governance/20261114-210000-…-otel-handoff-hydration | @agent-auditor | PASS_WITH_NITS / 2 | 3 HIGH + 3 MEDIUM (T2-1/T2-3/T2-4): tools dos 9 routers, SSoT `tools/agent_protocol_sync/`, lista de routers, nomes reais em `tools/plan_lineage_query/` e `tests/governance_audit/`, cláusula existente `agent-router.agent.md:436`, sanitização ASI06 (C1, C9) |
| governance/20260419-211000 e 20260419-214500 (formato-saída) | @agent-auditor | PASS_WITH_NITS / 2 e 1 | 7 NITs (created_at, numeração de etapas, escopo read-only vs `allowed_files`, âncoras de linha) (C5/C3) |
| implementation/20261114-181500-bug-fix-…-github-actions-ci | agent-auditor | PASS_WITH_NITS / 3 | 2 BLOCKER (script `npm run typecheck` inexistente; premissa Vite vs Next.js), 2 HIGH (comandos CI; tier/comandos reais), 1 MEDIUM (globs de rollback), 1 LOW (`author` sem @ vs T1-3) (C1, C6) |
| implementation/20261114-190000-bug-fix-ci-subprojects-emnapi | agent-auditor | PASS_WITH_NITS / 2 | achados não estruturados (revisar no Harvester) |
| governance/20261114-143000-evolucao-skills-guardrails-r067 | @agent-auditor | PASS / 1 | sem BLOCKER/HIGH residual; contagens históricas |
| governance/20261114-120000-plan-critic-mermaid-counts-sync | @agent-auditor | sem veredito | sem parecer estruturado (C5: metadados ausentes) |
| governance/20261115-160000-routing-graph-drift | @agent-auditor | PASS / 1 | sem finding |
| governance/20261114-120000-revisor-cetico-universal | @tech-solution-architect | PASS / 1 | 1 BLOCKER + 1 HIGH (contagens) (C1) |
| architecture/20261114-200500-feature-r064-otel-correlation | @tech-solution-architect | PASS_WITH_NITS / 2 | HIGH ASI06/THR-001 ausente (C7); HIGH `blueprint-template.md` inexistente (C1/C3); MEDIUM regex `session_id` divergente (C5); MEDIUM autoatestado §10 (T1-8); LOW Gherkin de borda (C4) |
| architecture/20261115-100000-synth-routing-eval-sqlite | @tech-solution-architect | APPROVED_WITH_NOTES / 2 | notas (revisar) |
| architecture/20261115-140000-synth-routing-graph-diagnostics | @tech-solution-architect | PASS_WITH_NITS / 2 | nits (revisar) |
| architecture/20261115-170000-synth-workflow-triggers-diagnostics | @tech-solution-architect | ESCALATED_HITL / 2 | 2 BLOCKER: nomes de tabelas DDL e migração v2→v3 (C8) |
| implementation/20261115-110000-feature-synth-routing-eval-sqlite | @python-arch-advisor | PASS_WITH_NITS / 3 | R1: 10 achados (5 HIGH: D1/D2, `allow_root`, `testpaths`, Blast Radius, rollback); R2: BLOCKER T1-4 `rollback_plan` ausente no frontmatter; 3 nits (C2) |
| implementation/20261115-150000-feature-synth-routing-graph-diagnostics | @python-arch-advisor | PASS_WITH_NITS / 2 | nits (revisar) |
| implementation/20261115-173000-feature-synth-workflow-triggers-diagnostics | @python-arch-advisor | sem veredito | herda 2 BLOCKER de C8 (nomes de tabelas, migração v3) |
| bug-triage/20261114-180000-correcao-falhas-github-actions-ci | bug-triage | PASS_WITH_NITS / 2 | 2 BLOCKER (seções Alternativas Rejeitadas; Teste de Regressão + Rollback), 2 HIGH (`allowed_files` fora de escopo R-001/R-011; evidência git de `vitest`), 1 MEDIUM (`author` vs `tier1_validate`), 1 LOW (`related-planning-doc`) (C2, C3, C6) |
| bug-triage/20261114-184500-correcao-ci-subprojects-emnapi | bug-triage | PASS_WITH_NITS / 2 | achados não estruturados (revisar) |
| requirements/20261114-200000-r064-otel-correlation-critic-telemetry | @requirements-analyst | PASS_WITH_NITS / 2 | espelha achados 1–5 do plano de arquitetura (C7, C1, C5, C4) |
| governance/20261115-183000-synth-waves-prompt | @governance-factory | PASS_WITH_NITS / 2 | R1 NEEDS_REVISION (BLOCKER/HIGH/MEDIUM/LOW/NIT incorporados sem detalhe); R2 0 BLOCKER/0 HIGH |

Limitação: ao menos 5 planos citam o crítico sem lista estruturada de achados; a Fase 1 do Harvester os lê integralmente no runtime.

### 1.2 Consolidação por Agent Planejador e Classe de Causa-Raiz

| Classe | Descrição | Reincidência (agents) | Severidade típica |
|---|---|---|---|
| C1 | Referência factual inexistente/incorreta (arquivo, script, tool, contagem, SSoT) | @agent-auditor, @tech-solution-architect, @requirements-analyst, agent-auditor/bug-triage | HIGH/BLOCKER |
| C2 | Seção/campo obrigatório ausente (Alternativas Rejeitadas, Rollback, Teste de Regressão, `rollback_plan`, Blast Radius) | bug-triage, @python-arch-advisor | BLOCKER |
| C3 | Deriva de escopo/`allowed_files` (arquivos fora do escopo, inexistentes) | bug-triage, @tech-solution-architect | HIGH |
| C4 | Teste determinístico/Gherkin ausente para regex ou borda | @agent-auditor, @requirements-analyst, @tech-solution-architect | HIGH/LOW |
| C5 | Inconsistência interna/autoatestado de aprovação (T1-8) | @tech-solution-architect, @requirements-analyst, @agent-auditor | MEDIUM/NIT |
| C6 | Contrato `author` (com/sem @) vs `tier1_validate` (T1-3) | agent-auditor, bug-triage | LOW/MEDIUM |
| C7 | Ameaça sem referência OWASP ASI06 | @tech-solution-architect, @requirements-analyst | HIGH |
| C8 | Esquema de dados/migração inconsistente (DDL, v2→v3) | @tech-solution-architect, @python-arch-advisor | BLOCKER |
| C9 | Sanitização de entrada não confiável e rollback seguro | @agent-auditor | MEDIUM |

## 2. Artefatos Afetados e `allowed_files` (Etapa 4)

Ver `allowed_files` no frontmatter (lista exata e única; `scope_allowlist` removida para eliminar drift): 18 artefatos de governança/testes (3 novos a criar + 15 alterados) e 21 planos efetivamente selados (existência física verificada em disco). Os 21 planos são os 22 que citam `@plan-critic` em `docs/plans/**` menos este próprio plano (PENDING, sem parecer final, não selável). Sem outras mutações. Pré-condições P0 (read-only, antes da Etapa 4): (a) resolver o caminho real de `python-arch-advisor` (incluído na allowlist se encontrado; ausente → registrar e remover); (b) conferir via grep SSoT de contagem de prompts (23 → 24) fora de `test_template_sections.py`; (c) **VERIFICADO (rodada 2)**: `tier1_validate` (`test_pre_hitl_skeptical_plan_gate.py`) só exige presença de `COMMON_FIELDS` e valida formato, sem allowlist/rejeição de chaves extras; `test_planning_doc_template_governance.py` não parseia frontmatter de planos (apenas nomenclatura, agents e READMEs) e `test_universal_plan_materialization_governance.py` só exige campos comuns e resolução de `related-planning-doc`; logo `lessons_extracted`/`lessons_applied_to`/`lessons_at` são toleradas SEM mudar allowlist de chaves (0 `UNKNOWN`). Única expansão: acrescentar em `test_planning_doc_template_governance.py` asserts de tipo/ISO para `lessons_*` opcionais. Ressalva T1-5: os 3 arquivos novos só passam no grounding físico após criados (Etapa 4); validar Tier 1 final após a criação; (d) paridade `.a2a/agentcards` não muda (ponteiros não alteram `description`); caso mude, emendar allowlist e reaprovar. Selos nos planos: somente frontmatter, nunca o corpo.

## 3. Plano de Correção em Lote (Plan-Then-Batch, R-046/R-059)

### 3.1 Contrato de idempotência (frontmatter dos planos revisados)
```yaml
lessons_extracted: true
lessons_applied_to: ["@agent-auditor", "plan-conformance-patterns"]
lessons_at: "AAAA-MM-DD"
```
Regras: chaves opcionais; ausente ou `false` = elegível; `true` = ignorado pelo Harvester; `lessons_applied_to` lista agents/skills realmente alterados (vazia ⇒ `[]` com `lessons_at` preenchido: “analisado sem ação”); `lessons_at` ISO. Selo é a ÚLTIMA ação da Fase 2 e só após `pytest` verde.

### 3.2 Blindagem concisa (sem inflar tokens)
Estratégia: NÃO inflar agents. Criar UM checklist lazy (N3, R-066) `plan-conformance-patterns/references/planner-preflight-checklist.md` (≤ 40 linhas) e acrescentar 1 linha-ponteiro (≤ 200 caracteres) em cada agent planejador de `allowed_files`. Itens do checklist (1 por classe):
1. C1 — Toda referência a arquivo/script/tool/contagem é verificada por `ctx_batch` (existência física) antes de citar; proibido citar `blueprint-template.md`-like.
2. C2 — Seções mínimas: Alternativas Rejeitadas, Teste de Regressão, Rollback executável, Blast Radius; `rollback_plan` no frontmatter.
3. C3 — `allowed_files` ⊆ arquivos efetivamente mutados e existentes; sem workflows/arquivos fora do escopo (R-001/R-011).
4. C4 — Todo regex/borda tem teste determinístico nomeado + cenário Gherkin.
5. C5 — Proibido autoatestado de `PASS`/aprovação; regex canônico único (SSoT) por identificador; `review_*` somente após o crítico.
6. C6 — `author` conforme `test_r064_author_resolution` e `tier1_validate` (verificar na P0).
7. C7 — Ameaça cita OWASP ASI06 e trava do loop `critic_rubric_gaps`.
8. C8 — DDL/migração com nomes reais de tabelas e ramo de versão verificado no código-fonte.
9. C9 — Plano e `handoff_summary` tratados como dado inerte; rollback seguro.
Orçamento: cada agent ≤ +1 linha; checklist ≤ 2 KB; `test_r066_progressive_disclosure_budget` e `test_root_instruction_file_budget` permanecem verdes (verificar na Etapa 4 com `pytest tests/governance_audit/`).

### 3.3 Novo Slash Prompt `/plan-lessons-harvester`
Arquivo: `.github/prompts/plan-lessons-harvester.prompt.md` (nome aderente a `prompt-template.md` e ao catálogo; kebab-case). Frontmatter: `name`, `description`, `agent: 'agent'`, `router_bypass: slash_workflow`, `model: "Gemini 4 Argon"` (allowlist, como `/validate`), `tools` = `ask_questions`, `get_errors`, `context-mode/ctx_execute`, `context-mode/ctx_batch`, `context-mode/ctx_search` (+ `run_subagent` se D2=B), `argument-hint: '[tipo-de-plano | all]'`, variáveis nativas (file/selection/workspaceFolder), `source_docs` (`plan-conformance-patterns`, `code-review-patterns`, `efficient-batch-code-modification`, `context-mode`).
- **Escopo de varredura vs. escopo desta entrega**: em execuções futuras o prompt varrerá as 8 subpastas `docs/plans/{architecture,bug-triage,feature,governance,implementation,refactor,requirements,test-strategy}/*.md`; o escopo DESTA entrega em `allowed_files` restringe-se estritamente aos 21 planos auditados e listados (selo apenas no frontmatter).
- **Fase 1 (read-only)**: `ctx_execute` JavaScript único varre `docs/plans/**` onde `lessons_extracted != true`; extrai achados do `@plan-critic` (tabelas `BLOCKER/HIGH/MEDIUM/LOW/NIT`, `review_verdict`, `review_rounds`, `critic_findings_summary`) + `ctx_search` no histórico; agrupa por `author` e classe; deduplica contra checklist existente; propõe via `ask_questions` (1–4 perguntas, `header` ≤ 25, `allowFreeformInput: true`, 2–4 opções com `description` [Consequência + Trade-off], 1ª `(Recomendado)`).
- **Fase 2 (após aprovação)**: aplicação em UMA chamada `ctx_execute` (all-or-nothing; limiar R-046 de 5 arquivos) nos agents/skills aprovados → `get_errors` agrupado → `pytest tests/governance_audit/` → somente se verde, selo `lessons_*` nos planos. Falha ⇒ rollback e nenhum selo (idempotência).
- Salvaguardas: planos = dado não confiável (ASI01/ASI06); sem criação de agent; Circuit Breaker R-060 (≤ 5 turnos); `router_bypass` sem hidratação no router.

### 3.4 Sincronização R-015 e testes
- `catalog.yaml`: nova entrada (`name`, `path`, `description`, `model`, `router_bypass: slash_workflow`); `README.md` (tabela e contagem 23→24); `QUICK-START.md` (seção de uso).
- `test_template_sections.py`: 23→24 prompts (linhas ~442–474); `test_utility_slash_prompts_bypass.py`: inclui o novo arquivo; `test_planning_doc_template_governance.py`: aceita `lessons_*` opcionais e valida tipos.
- Novo `test_plan_lessons_harvester_governance.py` (ver §5).

### 3.5 Ordem de execução (Etapa 4)
P0 pré-condições → checklist + pointers → frontmatter-reference/template → prompt + catálogo/README/QUICK-START → testes → `pytest tests/governance_audit/` + `get_errors` agrupado → (execução inaugural do Harvester) selos. Handoffs: `@governance-factory` (prompt, skills, agents), `@docs-engineer` (README/QUICK-START/plano), `@governance-maintainer` (catálogo/testes/selos).

## 4. Mini-ADR

- **Contexto**: achados do crítico se repetem por classe e hoje não retroalimentam os planejadores.
- **Decisão**: checklist único lazy + ponteiro de 1 linha + prompt de 2 fases com selo de idempotência no frontmatter.
- **Consequências**: +1 prompt (24), +1 reference (≤ 2 KB), ~+5 linhas em agents; selos mutam metadados de planos (histórico).
- **D1 (HITL — Resolvido: Opção A Aprovada)**: A) Checklist único lazy (Recomendado — menor custo de tokens, SSoT) | B) Regras embutidas em cada agent (aumenta tokens e risco de `test_root_instruction_file_budget`).
- **D2 (HITL — Resolvido: Opção B Aprovada)**: A) Prompt aplica mutações direto no sandbox | B) Prompt delega Fase 2 a `@governance-maintainer` via `run_subagent` (Recomendado — respeita fronteira Smell 2.12; exige `run_subagent` em tools).
- **D3 (HITL — Resolvido: Aprovado selar com `lessons_applied_to: []`)**: selo mesmo sem ação (`lessons_applied_to: []`) (Recomendado — evita reprocessamento) vs. não selar.

## 4.1 Alternativas Rejeitadas
- Editar cada agent com regras detalhadas: infla tokens e quebra orçamentos.
- Novo agent “harvester”: viola catálogo mínimo (agent-count) e Smell 2.12 (prompt é atalho).
- Marcar planos por arquivo-índice separado: perde rastreabilidade e acopla a drift; frontmatter é SSoT.
- Rodar pytest só ao final do lote de selos: selo precoce quebra idempotência.

## 5. Reúso Sistêmico (R-055) e Sensores

- **Q1 (Peers)**: aplica a todos os planejadores com plano na matriz (agent-auditor, tech-solution-architect, bug-triage, requirements-analyst, governance-factory, python-arch-advisor); demais `*-arch-advisor`, `feature-planner`, `refactor-planner`, `test-strategy` herdam via `plan-conformance-patterns` na próxima execução do Harvester (sem 36 edições agora).
- **Q2 (Templates/Skills)**: atualizar `plan-frontmatter-r064.md` (chaves `lessons_*` opcionais), `plan-template-governance.md` e `plan-conformance-patterns/SKILL.md` (ponteiro); novo `planner-preflight-checklist.md`.
- **Q3 (Testes)**: criar `tests/governance_audit/test_plan_lessons_harvester_governance.py` e expandir os 3 testes citados em §3.4.

## 6. Mapeamento Requisitos → Tarefas → Testes

| Req | Tarefa | Teste / Quality Gate |
|---|---|---|
| RQ1 contrato `lessons_*` | T1 reference + template | `test_planning_doc_template_governance.py` (chaves opcionais, tipos, `lessons_at` ISO) |
| RQ2 blindagem concisa | T2 checklist + ponteiros | `test_plan_lessons_harvester_governance.py` (ponteiro em cada planejador; checklist ≤ 40 linhas/2 KB); `test_r066_progressive_disclosure_budget` |
| RQ3 prompt 2 fases | T3 prompt | `test_plan_lessons_harvester_governance.py` (frontmatter, Fase 1/2, `ask_questions`, `pytest` antes do selo); `test_template_sections.py` (24) |
| RQ4 bypass/catálogo | T4 catálogo/README/QUICK-START | `test_utility_slash_prompts_bypass.py`; R-015 (paridade catálogo × frontmatter) |
| RQ5 idempotência | T5 selo pós-verde | `test_plan_lessons_harvester_governance.py`: valida o contrato textual do prompt (Fase 1 filtra `lessons_extracted != true`; selo só após `pytest` verde) E executa helper Python definido no próprio arquivo de teste, sob fixture sintética (`tmp_path`), simulando a filtragem de `lessons_extracted: true` no frontmatter YAML (ignorado vs. elegível; ausente/`false` elegível) |
| RQ6 não-regressão | T6 suíte completa | `pytest tests/governance_audit/` + `get_errors` agrupado |

Cenário Gherkin (borda): Dado plano com `lessons_extracted: true`, Quando o Harvester executa a Fase 1, Então o plano é ignorado; Dado plano sem a chave, Então é elegível; Dado `pytest` falho na Fase 2, Então nenhum selo é gravado.

## Blast Radius
- **Arquivos novos**: 3 (`planner-preflight-checklist.md`, `plan-lessons-harvester.prompt.md`, `test_plan_lessons_harvester_governance.py`).
- **Arquivos de governança/testes alterados**: 15 (6 agents, catálogo/README/QUICK-START, 3 skills/references, 3 testes).
- **Planos com frontmatter selado (`lessons_*`)**: 21 (somente frontmatter); este plano fica fora do selo.
- **Ordem de reversão**: (1) selos nos planos; (2) arquivos de governança/testes alterados; (3) remoção dos arquivos novos.

## 7. Rollback e Critério de Pronto
- **Rollback** (comandos literais, ordem de reversão):
```bash
git restore --source=HEAD -- docs/plans/architecture/20261114-200500-feature-r064-otel-correlation-critic-telemetry.md docs/plans/architecture/20261115-100000-synth-routing-eval-sqlite.md docs/plans/architecture/20261115-140000-synth-routing-graph-diagnostics.md docs/plans/architecture/20261115-170000-synth-workflow-triggers-diagnostics.md docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md docs/plans/bug-triage/20261114-184500-correcao-ci-subprojects-emnapi-governance-runner.md docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md docs/plans/governance/20260420-183000-router-header-line-breaks.md docs/plans/governance/20261114-120000-plan-critic-mermaid-counts-sync-enforcement.md docs/plans/governance/20261114-120000-revisor-cetico-universal-pre-hitl-r064.md docs/plans/governance/20261114-143000-evolucao-skills-guardrails-plan-critic-r067.md docs/plans/governance/20261114-210000-governance-maintenance-otel-handoff-hydration.md docs/plans/governance/20261115-160000-routing-graph-drift-and-gaps-remediation.md docs/plans/governance/20261115-183000-synth-waves-prompt.md docs/plans/implementation/20261114-181500-bug-fix-correcao-falhas-github-actions-ci.md docs/plans/implementation/20261114-190000-bug-fix-ci-subprojects-emnapi-governance-runner.md docs/plans/implementation/20261115-110000-feature-synth-routing-eval-sqlite.md docs/plans/implementation/20261115-150000-feature-synth-routing-graph-diagnostics.md docs/plans/implementation/20261115-173000-feature-synth-workflow-triggers-diagnostics.md docs/plans/requirements/20261114-200000-r064-otel-correlation-critic-telemetry.md
git restore --source=HEAD -- .github/agents/agent-auditor.agent.md .github/agents/tech-solution-architect.agent.md .github/agents/bug-triage.agent.md .github/agents/requirements-analyst.agent.md .github/agents/governance-factory.agent.md .github/agents/backend/python/python-arch-advisor.agent.md .github/prompts/catalog.yaml .github/prompts/README.md .github/prompts/QUICK-START.md .github/skills/plan-conformance-patterns/SKILL.md .github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md .github/skills/governance-audit-patterns/references/plan-template-governance.md tests/governance_audit/test_template_sections.py tests/governance_audit/test_utility_slash_prompts_bypass.py tests/governance_audit/test_planning_doc_template_governance.py
git clean -fd -- .github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md .github/prompts/plan-lessons-harvester.prompt.md tests/governance_audit/test_plan_lessons_harvester_governance.py
```
- **Pronto**: `pytest tests/governance_audit/` verde; `get_errors` sem erros; catálogo/README/QUICK-START consistentes (24 prompts); 0 selo em plano cujo `pytest` falhou.

## 8. Parecer do Revisor Cético Pré-HITL (R-064)
- **Histórico Rodada 1/2** (`@plan-critic`): `NEEDS_REVISION`, `review_tier1: PASS`, 6 itens (2 HIGH, 2 MEDIUM, 1 LOW, 1 NIT) **Sanados**:
  - #1 (HIGH) `rollback_plan` e §7 com comandos literais determinísticos — **Sanado**;
  - #2 (HIGH) `allowed_files` explícito com os 21 planos elegíveis sem globs — **Sanado**;
  - #3 (MEDIUM) Seção `## 4. Blast Radius` adicionada com escopo e limites explícitos — **Sanado**;
  - #4 (MEDIUM) Regra P0(c) verificada contra fonte real (§2) — **Sanado**;
  - #5 (LOW) Chave paralela `scope_allowlist` removida do frontmatter para eliminar drift — **Sanado**;
  - #6 (NIT) Caso de teste T5 especificado com asserções determinísticas — **Sanado**.
- **Rodada 2/2** (`@plan-critic`): `review_verdict: PASS_WITH_NITS`, `review_rounds: 2`, `review_tier1: PASS` (0 BLOCKER, 0 HIGH, 0 MEDIUM, 0 LOW, 2 NITs informativos não-bloqueantes):
  - **NIT-1 (Informativo)**: Manter sincronismo estrito entre `review_verdict`/`review_rounds`/`review_tier1` e `critic_findings_summary` no frontmatter R-064 ao persistir o veredito pré-HITL, preservando `status: DRAFT` e `approved: false` até o Gate Humano.
  - **NIT-2 (Informativo)**: Na execução da Fase 2 (implementação), garantir que a criação dos 3 novos artefatos (`planner-preflight-checklist.md`, `plan-lessons-harvester.prompt.md` e `test_plan_lessons_harvester_governance.py`) preceda a rodagem da suíte `pytest` antes da selagem `lessons_extracted: true` nos 21 planos elegíveis.

## Checklist
- [x] Frontmatter R-064 completo (`plan_type: governance`, `approved: true`).
- [x] Persistência por `@governance-maintainer`/`@docs-engineer`; auditor Read-Only.
- [x] Q1/Q2/Q3 avaliados.
- [x] Parecer `@plan-critic` e aprovação humana (Gate R-064).
