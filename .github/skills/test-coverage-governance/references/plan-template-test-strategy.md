# Template de Plano — `test-strategy`

> Referência detalhada (lazy) — carregada via `references/` por Progressive Disclosure (R-066).

## Frontmatter YAML Comum R-064 (obrigatório)

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@test-strategy"
plan_type: "test-strategy"
created_at: "AAAA-MM-DD"
related-planning-doc: "docs/plans/feature/<arquivo>.md | N/A"
review_verdict: PASS | PASS_WITH_NITS | ESCALATED_HITL
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PASS | FAIL
allowed_files:
  - "caminho/ou/glob/**"
---
```

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/test-strategy/<AAAAMMDD-HHMMSS>-<identificador>.md`.
- O agent planejador/advisor permanece **100% Read-Only**: emite o plano estruturado segundo este template; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@docs-engineer` (ou `@governance-maintainer` em plano de governança). O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

## Estrutura do Corpo

1. Escopo e riscos (matriz de cobertura por risco, §1.2)
2. Metas por tipo/ecossistema e seams pré-acordados
3. Cenários críticos por camada (unit/integration/E2E)
4. Ferramentas e comandos canônicos
5. **Alternativas Rejeitadas**
6. Critério de pronto (metas verificáveis)


## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: `PASS | FAIL`
- **Tier 2 (`@plan-critic`)**: `PASS | PASS_WITH_NITS | ESCALATED_HITL` (`review_rounds: 1..3`, Noise Budget ≤ 5 findings `BLOCKER`/`HIGH`)
- **Findings e Resoluções**: (resumo objetivo ou `Nenhum finding BLOCKER/HIGH`).

## Checklist

- [ ] Frontmatter R-064 completo (`plan_type: test-strategy`).
- [ ] `allowed_files` limita-se aos arquivos de teste planejados.
- [ ] Handoff de materialização para `@docs-engineer` declarado.

