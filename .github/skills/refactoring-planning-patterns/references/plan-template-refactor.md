# Template de Plano — `refactor`

> Referência detalhada (lazy) — carregada via `references/` por Progressive Disclosure (R-066).

## Frontmatter YAML Comum R-064 (obrigatório)

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@refactor-planner"
plan_type: "refactor"
created_at: "AAAA-MM-DD"
related-planning-doc: "docs/plans/architecture/<arquivo>.md | N/A"
allowed_files:
  - "caminho/ou/glob/**"
---
```

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/refactor/<AAAAMMDD-HHMMSS>-<identificador>.md`.
- O agent planejador/advisor permanece **100% Read-Only**: emite o plano estruturado segundo este template; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@docs-engineer` (ou `@governance-maintainer` em plano de governança). O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

## Estrutura do Corpo

1. Contexto e motivação (hotspots, acoplamento)
2. Estratégia (Mikado / Branch by Abstraction / Strangler Fig)
3. Safety Net (testes de caracterização)
4. DAG de tarefas atômicas (dependências e paralelismo)
5. **Alternativas Rejeitadas**
6. Matriz de Rollback multicamada e Reversibility Tier
7. Definition of Done

## Checklist

- [ ] Frontmatter R-064 completo (`plan_type: refactor`).
- [ ] `allowed_files` reflete o blast radius do DAG.
- [ ] Handoff de materialização para `@docs-engineer` declarado.

