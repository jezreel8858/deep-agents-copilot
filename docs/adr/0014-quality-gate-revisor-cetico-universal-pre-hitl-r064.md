---
id: ADR-0014
title: "Quality Gate Universal de Revisão Cética Pré-HITL (R-064) via @plan-critic"
status: Aceito
date: 2026-11-14
decision-makers:
  - governance-maintainer
  - tech-solution-architect
consulted:
  - agent-auditor
  - deep-search
informed:
  - adr-sentinel
  - pr-gatekeeper
type: architectural-decision
diataxis: explanation
---
# ADR-0014: Quality Gate Universal de Revisão Cética Pré-HITL (R-064) via @plan-critic
## 1. Contexto e Declaração do Problema
O R-064 persiste planos nas 8 subpastas de `docs/plans/<tipo>/` antes do Gate de Aprovação Humana. Hoje o humano recebe o plano sem filtro independente: defeitos objetivos (frontmatter inválido, `allowed_files` inexistentes, placeholders) e falhas semânticas (scope creep, violação de ADR, rollback inexequível) consomem atenção humana e aumentam o risco de aprovação por fadiga. A autocrítica do próprio planejador sofre de viés de autopreferência e sicofancia.
## 2. Drivers de Decisão
- Independência do revisor em relação ao autor (Context Firewall).
- Custo mínimo: verificações determinísticas sem tokens LLM sempre que possível.
- Convergência previsível (Fast-Pass + teto de iterações) e ruído limitado.
- Compatibilidade com R-025 (read-only), R-043 (adapters), R-047/R-054 (topologia plana), R-050.4/R-060 (tetos) e R-065 (guard de severidade).
## 3. Benchmark de Mercado
| Fonte | Achado aplicável |
|---|---|
| Anthropic — Evaluator-Optimizer (2024) | Loop gerador/avaliador com critérios explícitos e critério de parada |
| Anthropic — Demystifying Evals (2025) | Preferir graders determinísticos; usar LLM-judge apenas onde necessário |
| CONSENSAGENT (ACL 2025) | Mitigação de sicofancia em debate multiagente |
| Silicon Mirror (arXiv:2604.00478, 2026) | Revisores herdam e espelham o raciocínio do autor quando o contexto é compartilhado |
| AWS / Datadog — LLM-as-a-Judge | Rubricas estruturadas, evidência obrigatória, calibração e controle de viés |
| LangChain | Padrões de reflexão/crítica e avaliação offline/online de agentes |
## 4. Matriz Comparativa
| Critério | A — Autocrítica no planejador | B — @plan-critic Read-Only + Tier 1 | C — Painel multiagente de revisores |
|---|---|---|---|
| Independência | Baixa | Alta (Context Firewall) | Alta |
| Custo de tokens | Baixo | Baixo-médio (Tier 1 = 0) | Alto |
| Convergência | Imprevisível | Fast-Pass + teto | Difícil (debate) |
| Aderência R-047/R-054 | Sim | Sim (plano) | Risco de aninhamento |
| Complexidade | Baixa | Média | Alta |
| Veredito | Rejeitada | **Escolhida** | Rejeitada (YAGNI R-011) |
## 5. Decisão
Aprovada no HITL a **Opção B**: novo subagente `@plan-critic` Read-Only combinado ao **Tier 1 Determinístico**, com política **Fast-Pass 1x + Teto 2x (3x em `tier: full`)**.
## 6. Desenho Operacional
1. **Two-Tier Hybrid**: Tier 1 (frontmatter R-064, nomenclatura, grounding de `allowed_files`, seções do template, placeholders) e Tier 2 semântico isolado recebendo só `{plan_path, requisitos_originais, adapters_r043}`.
2. **Dupla Lente**: Gate 1 (domínio, categorias não-implementation) e Gate 2 (código, `implementation`).
3. **Rubrica modular R-043**: Núcleo Comum + critérios das 8 categorias + adapters de stack e de projeto local (`pre-hitl-skeptical-review-rubric.md`).
4. **Severidade**: `BLOCKER`/`HIGH` bloqueantes; `MEDIUM`/`LOW`/`NIT` sob Noise Budget <= 5; Guard R-065 preservado.
5. **Convergência**: Fast-Pass em 1 rodada; teto 2x (3x em tier full); remanescente => `ESCALATED_HITL` com tabela de divergências via `ask_questions`.
6. **Metadados**: `review_verdict`, `review_rounds`, `reviewer`, `review_tier1` e seção `## Parecer do Revisor Cético Pré-HITL (R-064)` nos templates.
7. **Topologia Plana**: `@plan-critic` retorna ao `@agent-router`; `@docs-engineer`/`@governance-maintainer` persistem a seção.
8. **Verificação**: `tests/governance_audit/test_pre_hitl_skeptical_plan_gate.py`.
## 7. Consequências
- ✅ Menor carga e risco de fadiga no Gate Humano; defeitos objetivos barrados a custo zero de LLM.
- ✅ Independência e rastreabilidade do parecer (evidência obrigatória).
- ⚠️ +1 agent no catálogo e +1 passo pré-HITL nos workflows (latência); mitigado por Fast-Pass.
- ⚠️ Manutenção da rubrica e dos 4 metadados nos templates; mitigada por teste determinístico.
- ❌ Não substitui a aprovação humana nem decide mérito de negócio.
## 8. Referências
- `docs/plans/governance/20261114-120000-revisor-cetico-universal-pre-hitl-r064.md`
- `.github/agents/plan-critic.agent.md`
- `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`
- ADR-0012, ADR-0013 (formato e convenções de ADR).
