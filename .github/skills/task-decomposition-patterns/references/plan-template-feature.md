# Template de Plano — `feature` e `architecture`

> Referência detalhada (lazy) — carregada via `references/` por Progressive Disclosure (R-066).

## Frontmatter YAML Comum R-064 (obrigatório)

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@feature-planner | @tech-solution-architect"
plan_type: "feature | architecture"
created_at: "AAAA-MM-DD"
related-planning-doc: "docs/plans/requirements/<AAAAMMDD-HHMMSS>-<modulo>.md | N/A"
allowed_files:
  - "caminho/ou/glob/**"
---
```

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/feature | architecture/<AAAAMMDD-HHMMSS>-<identificador>.md`.
- O agent planejador/advisor permanece **100% Read-Only**: emite o plano estruturado segundo este template; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@docs-engineer` (ou `@governance-maintainer` em plano de governança). O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

## Destinos

| `plan_type` | Destino | Autor |
|---|---|---|
| `feature` | `docs/plans/feature/` | `@feature-planner` |
| `architecture` | `docs/plans/architecture/` | `@tech-solution-architect`, `<stack>-arch-advisor` |

## Estrutura do Corpo

1. Contexto/Problema
2. Opções consideradas
3. Decisão
4. **Alternativas Rejeitadas** (obrigatória)
5. Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)
6. Subtasks (DAG com [P]/[S], tracer-bullet, blocking edges — ver SKILL.md §3.1/§5)
7. Convergência e Definition of Done
8. Reversibility Tier (T1/T2/T3) e Rollback

## Checklist

- [ ] Frontmatter R-064 completo e `plan_type` correto.
- [ ] `allowed_files` cobre todos os arquivos das subtasks.
- [ ] Handoff de materialização para `@docs-engineer` declarado.

