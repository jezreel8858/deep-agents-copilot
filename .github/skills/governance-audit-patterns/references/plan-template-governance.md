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
review_verdict: PASS | PASS_WITH_NITS | NEEDS_REVISION | ESCALATED_HITL
post_exec_review_verdict: null # PASS | PASS_WITH_WARNINGS | FAIL (preenchido na Etapa 5b por @agent-auditor)
post_exec_reviewer: "@agent-auditor"
post_exec_reviewed_at: null # YYYY-MM-DD
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PASS | FAIL
session_id: "sess-20261115-exemplo"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
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
  author_ref: "@agent-auditor"
allowed_files:
  - "caminho/ou/glob/**"
---
```

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/governance/<AAAAMMDD-HHMMSS>-<identificador>.md`.
- O agent planejador/advisor permanece **100% Read-Only**: emite o plano estruturado segundo este template; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@docs-engineer` (ou `@governance-maintainer` em plano de governança). O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

## Estrutura do Corpo

1. Escopo da manutenção e achados (smells 2.x com severidade) + **Diagnóstico Forense (Q0)**: `intencao_plano: corretivo | remediativo | hibrido | evolutivo`
2. Artefatos afetados e `allowed_files`
3. Plano de correção em lote (Plan-Then-Batch)
4. **Alternativas Rejeitadas**
5. Reúso sistêmico (R-055: **Q0**/Q1/Q2/Q3) e sensores `tests/governance_audit/`
6. Rollback e critério de pronto


## Diagnóstico Forense — RCA Upstream (R-055 Q0)

- **Classificação de Intenção**: `corretivo | remediativo | hibrido | evolutivo`
- **Isenção Greenfield** (somente se `evolutivo`): `N/A — plano puramente evolutivo/greenfield` (com justificativa de 1 linha).

| Dimensão Q0 | Análise Obrigatória (planos `corretivo`, `remediativo` ou `hibrido`) |
|---|---|
| Origem Upstream (Fonte Geradora) | Qual script (`tools/**`), template SSOT, instrução conflitante ou agente gerou/induziu o defeito |
| Análise de Escape (Falha de Contenção) | Qual sensor (`tests/governance_audit/`), pre-commit hook ou gate falhou em bloquear antes do disco |
| Neutralização na Fonte | Tarefa explícita do plano que corrige o mecanismo gerador/indutor (não apenas o artefato onde o sintoma apareceu) |

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: `PASS | FAIL`
- **Tier 2 (`@plan-critic`)**: `PASS | PASS_WITH_NITS | ESCALATED_HITL` (`review_rounds: 1..3`, Noise Budget ≤ 5 findings `BLOCKER`/`HIGH`)
- **Findings e Resoluções**: (resumo objetivo ou `Nenhum finding BLOCKER/HIGH`).


---

## Parecer de Conformidade Pós-Execução (R-064 / § 10.9)

- **Post-Exec Reviewer**: `@agent-auditor`
- **Post-Exec Review Verdict**: `PENDING | PASS | PASS_WITH_WARNINGS | FAIL`
- **Post-Exec Reviewed At**: `YYYY-MM-DD`
- **Auditoria em 3 Níveis (`plan-conformance-patterns`)**:
  - **N1 (Escopo Territorial `allowed_files` e Frontmatter R-064)**: Pendente de execução.
  - **N2 (Completude 1:1 de Tasks `[GOVERNANCE_TASKS]` e Sensor Q3)**: Pendente de execução.
  - **N3 (Aderência Semântica, Paridade de Catálogos e Invariantes)**: Pendente de execução.

## Checklist

- [ ] Frontmatter R-064 completo (`plan_type: governance`).
- [ ] Persistência por `@governance-maintainer`/`@docs-engineer`; auditor permanece Read-Only (R-057).
- [ ] Conformidade com `docs/plans/<tipo>/` auditada (Smell 2.34).

## Idempotência Pós-Revisão (`/plan-lessons-harvester`)

- Chaves opcionais no frontmatter YAML: `lessons_extracted` (`bool`), `lessons_applied_to` (`list[str]`, `[]` quando analisado sem ação) e `lessons_at` (`AAAA-MM-DD` ISO), gravadas somente após `pytest tests/governance_audit/` verde.
