# Frontmatter R-064 Comum e Taxonomia `docs/plans/<tipo>/`

> Referência detalhada (lazy) da skill `plan-conformance-patterns` (R-066).

## Frontmatter YAML Comum

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@<nome-do-agent-planejador>"
plan_type: "feature | refactor | architecture | implementation | test-strategy | bug-triage | requirements | governance"
created_at: "AAAA-MM-DD"
related-planning-doc: "docs/plans/<tipo>/<arquivo>.md | N/A"
review_verdict: PASS | PASS_WITH_NITS | NEEDS_REVISION | ESCALATED_HITL
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PASS | FAIL
session_id: "sess-20261115-r064-otel"
workflow_id: "WORKFLOW-FEATURE-DEVELOPMENT"
workflow_trace_id: "wf-feature-20261115-200000"
parent_plan_ref: "N/A — plano raiz | docs/plans/requirements/<AAAAMMDD-HHMMSS>-<slug>.md"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PASS"
  author_ref: "@<agent-planejador-ou-advisor>"
allowed_files:
  - "caminho/ou/glob/**"
---
```

| Campo | Regra |
|---|---|
| `status` | `DRAFT` até o Gate R-064; `APPROVED` após aprovação humana |
| `approved` | `false` em DRAFT; `true` somente com aprovação humana explícita |
| `author` | Agent planejador (`@nome`), não o persistidor |
| `plan_type` | Uma das 8 subpastas da taxonomia |
| `created_at` | Data ISO `AAAA-MM-DD` |
| `related-planning-doc` | Plano antecedente (ex.: blueprint → implementation) ou `N/A` |
| `allowed_files` | Allowlist de arquivos/globs usada pelo Nível 1 da conformidade |
| `lessons_extracted` | *(Opcional)* `bool` (`false \| true`); ausente ou `false` indica plano elegível na Fase 1 do `/plan-lessons-harvester`; `true` indica plano já processado e ignorado em execuções futuras |
| `lessons_applied_to` | *(Opcional)* Lista de `str` com os agents/skills blindados a partir das lições do plano (`[]` quando analisado sem ação necessária) |
| `lessons_at` | *(Opcional)* Data ISO `AAAA-MM-DD` da selagem de idempotência (gravada exclusivamente após suíte `pytest tests/governance_audit/` 100% verde) |

## Taxonomia das 8 Subpastas

| `plan_type` | Destino canônico | Planejador típico | Skill/template |
|---|---|---|---|
| `feature` | `docs/plans/feature/` | `feature-planner` | `task-decomposition-patterns` |
| `refactor` | `docs/plans/refactor/` | `refactor-planner` | `refactoring-planning-patterns` |
| `architecture` | `docs/plans/architecture/` | `tech-solution-architect`, `*-arch-advisor` | `task-decomposition-patterns` |
| `implementation` | `docs/plans/implementation/` | especialistas híbridos (Gate 2) | `specialist-hybrid-advisory-implementation-patterns` |
| `test-strategy` | `docs/plans/test-strategy/` | `test-strategy` | `test-coverage-governance` |
| `bug-triage` | `docs/plans/bug-triage/` | `bug-triage` | `code-tracing` |
| `requirements` | `docs/plans/requirements/` | `requirements-analyst` | `requirements-engineering-patterns` |
| `governance` | `docs/plans/governance/` | `agent-auditor` | `governance-audit-patterns` |

## Regras

- Planejadores/advisors são 100% Read-Only; emitem o plano e delegam a materialização `.md` a `@docs-engineer` (ou `@governance-maintainer`).
- Padrão canônico de nomenclatura de arquivo em todas as 8 subpastas: `docs/plans/<tipo>/<AAAAMMDD-HHMMSS>-<slug>.md` (e `docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md` em `implementation/`, regex `^\d{8}-\d{6}-[a-z0-9]+(-[a-z0-9]+)*\.md# Frontmatter R-064 Comum e Taxonomia `docs/plans/<tipo>/`

> Referência detalhada (lazy) da skill `plan-conformance-patterns` (R-066).

## Frontmatter YAML Comum

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@<nome-do-agent-planejador>"
plan_type: "feature | refactor | architecture | implementation | test-strategy | bug-triage | requirements | governance"
created_at: "AAAA-MM-DD"
related-planning-doc: "docs/plans/<tipo>/<arquivo>.md | N/A"
allowed_files:
  - "caminho/ou/glob/**"
---
```

| Campo | Regra |
|---|---|
| `status` | `DRAFT` até o Gate R-064; `APPROVED` após aprovação humana |
| `approved` | `false` em DRAFT; `true` somente com aprovação humana explícita |
| `author` | Agent planejador (`@nome`), não o persistidor |
| `plan_type` | Uma das 8 subpastas da taxonomia |
| `created_at` | Data ISO `AAAA-MM-DD` |
| `related-planning-doc` | Plano antecedente (ex.: blueprint → implementation) ou `N/A` |
| `allowed_files` | Allowlist de arquivos/globs usada pelo Nível 1 da conformidade |

## Taxonomia das 8 Subpastas

| `plan_type` | Destino canônico | Planejador típico | Skill/template |
|---|---|---|---|
| `feature` | `docs/plans/feature/` | `feature-planner` | `task-decomposition-patterns` |
| `refactor` | `docs/plans/refactor/` | `refactor-planner` | `refactoring-planning-patterns` |
| `architecture` | `docs/plans/architecture/` | `tech-solution-architect`, `*-arch-advisor` | `task-decomposition-patterns` |
| `implementation` | `docs/plans/implementation/` | especialistas híbridos (Gate 2) | `specialist-hybrid-advisory-implementation-patterns` |
| `test-strategy` | `docs/plans/test-strategy/` | `test-strategy` | `test-coverage-governance` |
| `bug-triage` | `docs/plans/bug-triage/` | `bug-triage` | `code-tracing` |
| `requirements` | `docs/plans/requirements/` | `requirements-analyst` | `requirements-engineering-patterns` |
| `governance` | `docs/plans/governance/` | `agent-auditor` | `governance-audit-patterns` |

## Regras

- Planejadores/advisors são 100% Read-Only; emitem o plano e delegam a materialização `.md` a `@docs-engineer` (ou `@governance-maintainer`).
). Prefixos `PLAN-`, `REQ-` ou nomes sem timestamp são estritamente proibidos.
- Divergência entre `allowed_files` e diff real reabre o Gate 2 (Plan Drift Detection).

## Metadados de Revisão Cética Pré-HITL (R-064 / ADR-0014)

Todo plano avaliado pelo Quality Gate Pré-HITL Two-Tier Hybrid registra no frontmatter:

- `review_verdict`: `PASS | PASS_WITH_NITS | NEEDS_REVISION | ESCALATED_HITL`
- `review_rounds`: `1..3` (Fast-Pass 1x se Tier 1 = PASS e 0 BLOCKER/HIGH; teto 2x padrão ou 3x em `tier: full`)
- `reviewer`: `"@plan-critic"` (subagente revisor cético 100% Read-Only sob Context Firewall)
- `review_tier1`: `PASS | FAIL` (resultado da validação estrutural determinística Tier 1)

## Campos de Correlação OTel e Telemetria do Revisor Cético (Schema v2 — R-064)

Para eliminar pontos cegos de rastreabilidade entre sessões de chat, execuções de workflow e rodadas do Revisor Cético Pré-HITL (`@plan-critic`), o Schema v2 do frontmatter R-064 introduz 6 chaves canônicas:

| Chave | Formato / Tipo | Semântica e Mapeamento Canônico |
|---|---|---|
| `session_id` | string (`^[a-z0-9][a-z0-9-]{7,95}$`) | Identificador único da sessão de chat ativa; mapeado diretamente para `gen_ai.conversation.id` (OTel GenAI Semantic Conventions). |
| `workflow_id` | enum canônico | Nome do workflow canônico em execução: `WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-BUG-FIX`, `WORKFLOW-REFACTORING`, `WORKFLOW-FRAMEWORK-MIGRATION`, `WORKFLOW-GOVERNANCE-MAINTENANCE`, `WORKFLOW-TECHNICAL-ANALYSIS`, `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION`, `WORKFLOW-RELEASE-READINESS`, `WORKFLOW-UI-LAYOUT`, `WORKFLOW-PROMPT-SYNTHESIS`. |
| `workflow_trace_id` | string (`^[a-z0-9][a-z0-9-]{7,95}$`) | Instância única de execução do workflow (`trace_id` lógico de ponta a ponta). |
| `parent_plan_ref` | string | `"N/A — plano raiz"` (para planos primários como `requirements`, `bug-triage`, `governance`) ou caminho explícito existente em `docs/plans/<tipo>/<AAAAMMDD-HHMMSS>-<slug>.md` (ex.: plano `architecture`/`feature` apontando para `requirements`). |
| `critic_rubric_gaps` | lista YAML (`list[str]`) | Lista de códigos canônicos da rubrica (`T1-1..T1-8`, `T2-1..T2-7` ou `T2-SCOPE`, `T2-YAGNI`, `T2-TRACE`, `T2-ALT`, `T2-ADR`, `T2-TEST`, `T2-SEC`) que falharam nas rodadas de revisão antes da aprovação (`[]` quando aprovado na 1ª rodada sem falhas). |
| `critic_findings_summary` | objeto YAML | Objeto estruturado `{ rounds, blockers, majors, minors, nits, last_verdict, author_ref }` consolidando a telemetria quantitativa e o autor auditado (`author_ref == author` e `reviewer != author`). |

### Política de Transição Retrocompatível (Cutoff `2026-11-15`)

- **Planos novos (`created_at >= "2026-11-15"`) ou com opt-in explícito v2**: a presença e validade das 6 chaves v2 são **100% obrigatórias** e verificadas deterministicamente no Tier 1 (`T1-8`).
- **Planos legados (`created_at <= "2026-11-14"` sem chaves v2)**: permanecem **100% válidos** sob o Schema v1 original (retrocompatibilidade estrita sem exigir migração retroativa de histórico). Se um plano legado optar por declarar qualquer chave v2 (opt-in explícito), o conjunto v2 completo passa a ser validado.
