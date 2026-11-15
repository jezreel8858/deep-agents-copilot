# Template de Plano — `requirements`

> Referência detalhada (lazy) — carregada via `references/` por Progressive Disclosure (R-066).

## Frontmatter YAML Comum R-064 (obrigatório)

```yaml
---
status: DRAFT | APPROVED
approved: false | true
author: "@requirements-analyst"
plan_type: "requirements"
created_at: "AAAA-MM-DD"
related-planning-doc: "N/A"
review_verdict: PASS | PASS_WITH_NITS | NEEDS_REVISION | ESCALATED_HITL
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PASS | FAIL
session_id: "sess-20261115-exemplo"
workflow_id: "WORKFLOW-FEATURE-DEVELOPMENT"
workflow_trace_id: "wf-trace-20261115-000001"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PASS"
  author_ref: "@requirements-analyst"
allowed_files:
  - "caminho/ou/glob/**"
---
```

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/requirements/<AAAAMMDD-HHMMSS>-<identificador>.md`.
- O agent planejador/advisor permanece **100% Read-Only**: emite o plano estruturado segundo este template; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@docs-engineer` (ou `@governance-maintainer` em plano de governança). O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

## Destino Canônico

`docs/plans/requirements/<AAAAMMDD-HHMMSS>-<modulo>.md`.

## Estrutura do Corpo

1. Contexto e stakeholders
2. Lista de requisitos `REQ-NNN` (funcional/não-funcional), notação EARS
3. Critério de aceite Gherkin por requisito
4. Prioridade MoSCoW e citação de fonte (anti-alucinação)
5. Perguntas em aberto
6. **Alternativas Rejeitadas**


## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: `PASS | FAIL`
- **Tier 2 (`@plan-critic`)**: `PASS | PASS_WITH_NITS | ESCALATED_HITL` (`review_rounds: 1..3`, Noise Budget ≤ 5 findings `BLOCKER`/`HIGH`)
- **Findings e Resoluções**: (resumo objetivo ou `Nenhum finding BLOCKER/HIGH`).

## Checklist

- [ ] Frontmatter R-064 completo (`plan_type: requirements`).
- [ ] Todo requisito singular, testável e com fonte.
- [ ] Handoff de materialização para `@docs-engineer` declarado.

