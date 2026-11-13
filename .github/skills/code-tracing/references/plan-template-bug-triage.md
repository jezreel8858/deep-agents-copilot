# Template de Plano — `bug-triage`

> Referência detalhada (lazy) — carregada via `references/` por Progressive Disclosure (R-066).

## Frontmatter YAML Comum R-064 (obrigatório)

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@bug-triage"
plan_type: "bug-triage"
created_at: "AAAA-MM-DD"
related-planning-doc: "N/A"
allowed_files:
  - "caminho/ou/glob/**"
---
```

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/bug-triage/<AAAAMMDD-HHMMSS>-<identificador>.md`.
- O agent planejador/advisor permanece **100% Read-Only**: emite o plano estruturado segundo este template; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@docs-engineer` (ou `@governance-maintainer` em plano de governança). O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

## Estrutura do Corpo

1. Sintoma normalizado e reprodução (Feedback Loop First)
2. Evidências de Rastreio (call chain, arquivo:linha)
3. Hipótese(s) com classificação de confiança
4. Causa raiz provável e correção proposta
5. **Alternativas Rejeitadas**
6. Plano de teste de regressão

## Checklist

- [ ] Frontmatter R-064 completo (`plan_type: bug-triage`).
- [ ] Segredos redigidos nas evidências.
- [ ] Handoff de materialização para `@docs-engineer` declarado.

