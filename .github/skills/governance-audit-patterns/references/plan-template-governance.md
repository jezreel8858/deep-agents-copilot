# Template de Plano — `governance`

> Referência detalhada (lazy) — carregada via `references/` por Progressive Disclosure (R-066).

## Frontmatter YAML Comum R-064 (obrigatório)

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@agent-auditor"
plan_type: "governance"
created_at: "AAAA-MM-DD"
related-planning-doc: "N/A"
allowed_files:
  - "caminho/ou/glob/**"
---
```

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/governance/<AAAAMMDD-HHMMSS>-<identificador>.md`.
- O agent planejador/advisor permanece **100% Read-Only**: emite o plano estruturado segundo este template; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@docs-engineer` (ou `@governance-maintainer` em plano de governança). O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

## Estrutura do Corpo

1. Escopo da manutenção e achados (smells 2.x com severidade)
2. Artefatos afetados e `allowed_files`
3. Plano de correção em lote (Plan-Then-Batch)
4. **Alternativas Rejeitadas**
5. Reúso sistêmico (R-055: Q1/Q2/Q3) e sensores `tests/governance_audit/`
6. Rollback e critério de pronto

## Checklist

- [ ] Frontmatter R-064 completo (`plan_type: governance`).
- [ ] Persistência por `@governance-maintainer`/`@docs-engineer`; auditor permanece Read-Only (R-057).
- [ ] Conformidade com `docs/plans/<tipo>/` auditada (Smell 2.34).

