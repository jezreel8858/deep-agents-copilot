# Template de Plano — `implementation` (Gate 2)

> Referência detalhada (lazy) — carregada via `references/` por Progressive Disclosure (R-066).

## Frontmatter YAML Comum R-064 (obrigatório)

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@<stack>-arch-advisor | @<stack>-developer (modo advisory)"
plan_type: "implementation"
created_at: "AAAA-MM-DD"
related-planning-doc: "docs/plans/architecture/<arquivo>.md | N/A"
allowed_files:
  - "caminho/ou/glob/**"
---
```

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/implementation/<AAAAMMDD-HHMMSS>-<identificador>.md`.
- O agent planejador/advisor permanece **100% Read-Only**: emite o plano estruturado segundo este template; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@docs-engineer` (ou `@governance-maintainer` em plano de governança). O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

## Destinos

- Gate 2: `docs/plans/implementation/`.
- Modo arquitetural/migração: `docs/plans/architecture/` (`plan_type: architecture`).

## Estrutura do Corpo

1. Resumo e escopo/não-escopo
2. Checklist GFM de passos executáveis (obrigatório em implementação)
3. `allowed_files` e blast radius
4. Estratégia de testes (Testing-First)
5. Rollback (`tier`: full | light | governance; `rollback_plan`)

## Checklist

- [ ] Frontmatter R-064 completo.
- [ ] Passos mapeados em `allowed_files`.
- [ ] Handoff de materialização para `@docs-engineer` declarado.

