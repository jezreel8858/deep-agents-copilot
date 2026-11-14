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
review_verdict: PASS | PASS_WITH_NITS | ESCALATED_HITL
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PASS | FAIL
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

- `review_verdict`: `PASS | PASS_WITH_NITS | ESCALATED_HITL`
- `review_rounds`: `1..3` (Fast-Pass 1x se Tier 1 = PASS e 0 BLOCKER/HIGH; teto 2x padrão ou 3x em `tier: full`)
- `reviewer`: `"@plan-critic"` (subagente revisor cético 100% Read-Only sob Context Firewall)
- `review_tier1`: `PASS | FAIL` (resultado da validação estrutural determinística Tier 1)
