---
status: APPROVED
approved: true
author: "@tech-solution-architect"
plan_type: "governance"
created_at: "2026-11-14"
related-planning-doc: "N/A — plano raiz"
review_verdict: PASS
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PASS
allowed_files:
  - "docs/adr/0014-quality-gate-revisor-cetico-universal-pre-hitl-r064.md"
  - "docs/plans/governance/20261114-120000-revisor-cetico-universal-pre-hitl-r064.md"
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/agents/catalog.yaml"
  - ".github/agents/routing-graph.yaml"
  - ".github/agents/workflows.md"
  - ".github/agents/workflows/*.md"
  - ".github/agents/*.agent.md"
  - ".github/skills/plan-conformance-patterns/**"
  - ".github/skills/reflection-self-critique-patterns/**"
  - ".github/skills/governance-audit-patterns/**"
  - ".github/skills/task-decomposition-patterns/**"
  - ".github/skills/refactoring-planning-patterns/**"
  - ".github/skills/requirements-engineering-patterns/**"
  - ".github/skills/test-coverage-governance/**"
  - ".github/skills/specialist-hybrid-advisory-implementation-patterns/**"
  - ".github/skills/code-tracing/**"
  - "tests/governance_audit/test_pre_hitl_skeptical_plan_gate.py"
  - "tests/governance_audit/test_universal_plan_materialization_governance.py"
  - "tests/governance_audit/test_planning_doc_template_governance.py"
---

# Plano de Governança Arquitetural: Quality Gate Universal de Revisão Cética Pré-HITL (R-064)

## 1. Contexto, Motivação e Escopo

A Regra **R-064** instituiu a Persistência Física Universal de Planos em `docs/plans/` (nas 8 subpastas canônicas: `feature`, `refactor`, `architecture`, `implementation`, `test-strategy`, `bug-triage`, `requirements` e `governance`) antes do Gate de Aprovação Humana (HITL). Entre a gravação física do plano `DRAFT` pelo `@docs-engineer` (ou `@governance-maintainer`) e o acionamento de `ask_questions`, falta um **Quality Gate Universal de Revisão Cética Independente Pré-HITL**.

Sem esse Gate, o aprovador humano fica exposto a: (1) **Fadiga de Revisão Humana (HITL Fatigue)** por omissões em `allowed_files`, quebras de limites arquiteturais (DDD/Clean/Hexagonal) ou lacunas no Portão R-055; (2) **Viés de Auto-Confirmação (Self-Preference & Sycophancy)** quando o autor avalia o próprio plano na mesma janela; e (3) **Assimetria entre Gate 1 (Plano Macro de Escopo/Negócio) e Gate 2 (Plano Técnico de Implementação por Stack)**. Este plano institui o Quality Gate Two-Tier Hybrid universal pré-HITL sob **R-055**, **R-060** (≤ 5 tool turns) e **R-065** (guardrail anti-loop).

## 2. Estudo de Viabilidade e Benchmark de Mercado (AI Engineering)

| Referência / Benchmark | Conceito-Chave | Aplicação no Quality Gate Pré-HITL (R-064) |
| :--- | :--- | :--- |
| **Anthropic Evaluator-Optimizer (2024)** | Separação explícita entre gerador (*Generator*) e avaliador cético (*Evaluator*). | Invariante `reviewer != author` desacoplando autor intelectual e revisor cético. |
| **Anthropic Demystifying Evals (2025)** | Combinação de *graders* determinísticos em código com *graders* LLM baseados em rubrica. | Arquitetura **Two-Tier Hybrid**: Tier 1 determinístico precedendo o Tier 2 semântico isolado. |
| **CONSENSAGENT (ACL 2025)** | Mitigação de *sycophancy* multi-agente via *persona adversarial* sem histórico apologético do autor. | O revisor examina apenas o artefato físico `.md` em disco contra o código real do repositório. |
| **Silicon Mirror (arXiv:2604.00478, 2026)** | *Fresh Context Window & Epistemic Isolation*: auto-correção na mesma janela falha por ancoragem. | Revisão executada em janela de contexto limpa e isolada do turno gerador. |
| **DEV/AWS & Datadog Two-Tier LLM-as-a-Judge** | Filtro estrutural de custo zero (Tier 1) bloqueando chamadas caras de LLM (Tier 2) em falhas formais. | Tier 1 valida YAML R-064, caminhos e higiene léxica em lote antes de acionar o Tier 2. |
| **LangChain Align Evaluator** | Julgamento em dimensões ortogonais com veredito discreto e crítica ancorada (*grounded critique*). | Rubrica modular: Núcleo R-064/R-055 + 8 categorias de `plan_type` + Adapter de Stack/Local (R-043). |
| **LLMs-as-Judges Survey (arXiv:2411.15287)** | Mitigação de *verbosity bias* e *self-enhancement bias* via checklists discretos verificáveis. | Vereditos discretos (`PASS`, `PASS_WITH_WARNINGS`, `FAIL_REVISION_REQUIRED`, `ESCALATED_HITL`). |
| **AdversarialMAS (2026)** | Controle de *over-criticism loop* e *Token Tax* via *Noise Budget* e limite rígido de rodadas. | **Noise Budget ≤ 5** achados críticos, **Fast-Pass** e **Max 1 ciclo crítica-correção (R-065)**. |

- **Mitigação de Sycophancy**: Matriz `reviewer != author` e isolamento epistêmico (*Fresh Context Window*).
- **Mitigação de Latency/Token Tax**: Tier 1 determinístico em lote único (`ctx_batch`) + **Fast-Pass** para planos triviais (≤ 3 arquivos em `allowed_files` sem impacto em segurança, schemas ou contratos públicos).
- **Mitigação de Over-Criticism Loop**: **Noise Budget ≤ 5** apontamentos bloqueantes/altos e teto **R-065** de no máximo 1 ciclo de correção antes de escalar via `ESCALATED_HITL`.

## 3. Matriz Comparativa de Arquitetura no Projeto (Opções A, B e C)

| Critério | Opção A: Extensão Isolada sem Revisor Cruzado | Opção B: Novo Subagente `@plan-critic` | Opção C (Recomendada): Híbrida Enxuta sob R-055 e R-060 |
| :--- | :--- | :--- | :--- |
| **Arquitetura** | Auto-crítica interna pelo próprio autor na mesma janela. | Criação de um novo agente `.github/agents/plan-critic.agent.md`. | Gate Two-Tier em `plan-conformance-patterns` e `reflection-self-critique-patterns` + Revisão Cruzada (`reviewer != author`) entre agentes read-only existentes. |
| **Anti-Sycophancy** | Baixa — sofre de *self-preference bias*. | Alta — contexto e persona isolados. | Alta — *Fresh Context* e `reviewer != author`. |
| **Portão R-055** | Alta — zero novos agentes. | **Viola R-055** — infla o catálogo de agentes. | **Máxima** — reutiliza agentes consultivos read-only existentes. |
| **R-047 / R-060** | Alta — sem handoff extra. | Baixa — subagente extra até para falhas formais. | **Otimizada** — topologia plana no `@agent-router`, Tier 1 gratuito e Fast-Pass. |
| **Decisão** | Rejeitada. | Rejeitada (viola R-055). | **Selecionada (Recomendada)**. |

## 4. Desenho Operacional Completo do Quality Gate Pré-HITL (Two-Tier Hybrid & Duplo Gate R-064)

### 4.1 Dupla Lente (Gate 1 & Gate 2), Tier 1 Determinístico e Tier 2 Semântico Isolado
- **Lente Gate 1 (Plano Macro/Escopo/Negócio)**: Avalia planos em `feature`, `refactor`, `requirements`, `bug-triage`, `test-strategy`, `governance` e `architecture` focando em invariantes de negócio, Portão R-055 (Q1/Q2/Q3), precisão de `allowed_files` e fatiamento.
- **Lente Gate 2 (Plano Técnico/Implementação por Stack)**: Avalia planos em `docs/plans/implementation/` emitidos pelos `*-arch-advisor` focando em Arquitetura Local Descoberta (R-043), isolamento de camadas (DDD/Clean/Hexagonal), contratos, segurança Shift-Left e regressão.
- **Tier 1 Determinístico**: Valida em lote o frontmatter YAML R-064 (`status: DRAFT`, `approved: false`, `author`, `plan_type`, `created_at`, `related-planning-doc`, `allowed_files` não-vazio), ausência de placeholders proibidos, coerência de caminhos e presença da seção de parecer cético. Falha no Tier 1 bloqueia o Tier 2.
- **Tier 2 Semântico Isolado — Matriz de Revisor Cruzado (`reviewer != author`)**:
  - `feature` (`@feature-planner`) → Revisor: `@tech-solution-architect` ou `*-arch-advisor` (Fallback: `@code-reviewer`)
  - `refactor` (`@refactor-planner`) → Revisor: `@tech-solution-architect` ou `*-arch-advisor` (Fallback: `@code-reviewer`)
  - `architecture` (`@tech-solution-architect`) → Revisor: `*-arch-advisor` da stack ou `@agent-auditor` (Fallback: `@code-reviewer`)
  - `implementation` (`*-arch-advisor`) → Revisor: `@tech-solution-architect` ou `@test-strategy` (Fallback: `@code-reviewer`)
  - `test-strategy` (`@test-strategy`) → Revisor: `*-arch-advisor` ou `@code-reviewer` (Fallback: `@tech-solution-architect`)
  - `bug-triage` (`@bug-triage`) → Revisor: `*-arch-advisor` ou `@test-strategy` (Fallback: `@code-reviewer`)
  - `requirements` (`@requirements-analyst`) → Revisor: `@feature-planner` ou `@tech-solution-architect` (Fallback: `@business-rules-extractor`)
  - `governance` (`@agent-auditor` ou `@tech-solution-architect`) → Revisão cruzada recíproca entre `@agent-auditor` e `@tech-solution-architect` (Fallback: `@code-reviewer`)

### 4.2 Rubrica Modular nas 8 Categorias + Adapters R-043, Convergência R-065 e Seção Auditável
- **Rubrica Modular**: (1) Núcleo Universal R-064/R-055; (2) Lentes das 8 categorias (`feature`: critérios de aceitação e fatiamento; `refactor`: preservação estrita de comportamento; `architecture`: trade-offs, acoplamento e ADRs; `implementation`: assinaturas, transações e tratamento de erros; `test-strategy`: pirâmide de testes, bordas e determinismo; `bug-triage`: causa-raiz reproduzível, *blast radius* e teste de regressão; `requirements`: rastreabilidade RN e atores; `governance`: sincronia entre instruções, workflows, agents, skills e testes); e (3) Adapter de Stack e Arquitetura Local Descoberta (R-043).
- **Controle de Convergência, Fast-Pass, Noise Budget ≤ 5, R-065 e Topologia Plana (R-047/R-054)**: Coordenação 100% plana via `@agent-router`. Limite de 5 apontamentos críticos por revisão e máximo de 1 ciclo de correção; persistindo divergência, registra-se `ESCALATED_HITL` na seção `## Parecer do Revisor Cético Pré-HITL (R-064)` do plano e aciona-se o humano via `ask_questions`.

## 5. Portão de Reúso Sistêmico (R-055 — Q1, Q2, Q3)

- **Q1 (Peers, Workflows e Agentes)**: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`, os 11 workflows em `.github/agents/workflows/` (`WORKFLOW-FEATURE.md`, `WORKFLOW-REFACTOR.md`, `WORKFLOW-BUG-FIX.md`, `WORKFLOW-TECH-DEBT.md`, `WORKFLOW-TECHNICAL-ANALYSIS.md`, `WORKFLOW-CODE-REVIEW.md`, `WORKFLOW-GOVERNANCE-AUDIT.md`, `WORKFLOW-DOCUMENTATION.md`, `WORKFLOW-PERFORMANCE-TUNING.md`, `WORKFLOW-RELEASE-DEPLOY.md`, `WORKFLOW-SECURITY-HARDENING.md`), agentes planejadores/revisores/materializadores em `.github/agents/*.agent.md` e as skills `plan-conformance-patterns` e `reflection-self-critique-patterns`.
- **Q2 (Os 8 Templates Especializados Reais Verificados em `test_universal_plan_materialization_governance.py` + Frontmatter R-064)**:
  0. Contrato Frontmatter R-064: `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`
  1. `feature`: `.github/skills/task-decomposition-patterns/references/planning-doc-template.md`
  2. `refactor`: `.github/skills/refactoring-planning-patterns/references/refactor-plan-template.md`
  3. `architecture`: `.github/skills/plan-conformance-patterns/references/architecture-plan-template.md`
  4. `implementation`: `.github/skills/specialist-hybrid-advisory-implementation-patterns/references/implementation-plan-template.md`
  5. `test-strategy`: `.github/skills/test-coverage-governance/references/test-strategy-plan-template.md`
  6. `bug-triage`: `.github/skills/code-tracing/references/bug-triage-plan-template.md`
  7. `requirements`: `.github/skills/requirements-engineering-patterns/references/requirements-plan-template.md`
  8. `governance`: `.github/skills/governance-audit-patterns/references/governance-plan-template.md`
- **Q3 (Testes Pytest em `tests/governance_audit/`)**: `tests/governance_audit/test_pre_hitl_skeptical_plan_gate.py` (novo), `tests/governance_audit/test_universal_plan_materialization_governance.py` e `tests/governance_audit/test_planning_doc_template_governance.py`.

## 6. Modelagem de Ameaças (Shift-Left Security) e Estratégia de Rollback

- **Modelagem de Ameaças**: (1) *Indirect Prompt Injection* mitigado por validação determinística Tier 1 e avaliação em janela isolada no Tier 2; (2) *Scope Creep* em `allowed_files` mitigado por auditoria cruzada contra R-055; (3) *Infinite Critique Loop / Denial of Wallet* mitigado por R-060 (≤ 5 turns), Noise Budget ≤ 5 e R-065 (`ESCALATED_HITL` após 1 ciclo); (4) *Violação Read-Only (R-025)* prevenida mantendo revisores sem permissão de escrita e persistência restrita ao `@docs-engineer` / `@governance-maintainer`.
- **Estratégia de Rollback**: Reversão atômica via Git sobre os arquivos declarativos em `allowed_files` e fallback automático para `ESCALATED_HITL` em caso de indisponibilidade transitória de subagente.

## 7. Especificação da Minuta do ADR-0014 (docs/adr/0014-quality-gate-revisor-cetico-universal-pre-hitl-r064.md)

- **Arquivo**: `docs/adr/0014-quality-gate-revisor-cetico-universal-pre-hitl-r064.md` | **Status**: Aceito | **Data**: 2026-11-14 | **Regras**: R-025, R-043, R-047, R-054, R-055, R-060, R-064, R-065.
- **Contexto**: Necessidade de revisão cética independente entre a persistência física do plano R-064 e o Gate Humano (Gates 1 e 2) sem violar o Portão de Reúso Sistêmico (R-055).
- **Decisão**: Instituir o Quality Gate Two-Tier Hybrid (Opção C) com Tier 1 determinístico em lote, Tier 2 semântico isolado com revisão cruzada (`reviewer != author`) entre agentes read-only existentes, rubrica modular nas 8 categorias + Adapter R-043, Fast-Pass, Noise Budget ≤ 5 e escalada `ESCALATED_HITL` após 1 ciclo (R-065).
- **Consequências**: Redução de fadiga humana no HITL, eliminação de *sycophancy*, zero inflação de agentes e rastreabilidade auditável via `pytest`.

## Parecer do Revisor Cético Pré-HITL (R-064)
- **Tier 1 (Determinístico)**: PASS (Frontmatter R-064 completo, `allowed_files` válido, zero placeholders proibidos).
- **Tier 2 (Semântico Isolado)**: PASS (Conformidade integral com R-047, R-055, R-060, R-064 e R-065).
- **Revisor Cruzado (`reviewer != author`)**: `@agent-auditor` | **Modo**: FULL_REVIEW | **Ciclos**: 1/1
- **Apontamentos (Noise Budget ≤ 5)**: Nenhum bloqueio pendente; 8 templates e 11 workflows verificados contra o repositório real.

## 8. Checklist de Aceitação e Conformidade R-064

- [x] Frontmatter YAML R-064 estrito (`status: DRAFT`, `approved: false`, `author: "@tech-solution-architect"`, `plan_type: "governance"`, `created_at: "2026-11-14"`, `related-planning-doc` e `allowed_files`).
- [x] Estudo de viabilidade e benchmark de mercado (8 fontes técnicas) e mitigação de *sycophancy*, *latency/token tax* e *over-criticism loop*.
- [x] Matriz comparativa das Opções A, B e C justificando a Opção C sob R-055 e R-060.
- [x] Desenho operacional cobrindo Gate 1 e Gate 2, Tier 1 Determinístico, Tier 2 Semântico (`reviewer != author`), Rubrica Modular nas 8 categorias + R-043, Fast-Pass, Noise Budget ≤ 5 e `ESCALATED_HITL`.
- [x] Portão R-055 (Q1, Q2, Q3) mapeado com os 8 templates reais verificados e suíte `pytest`.
- [x] Modelagem de ameaças Shift-Left, estratégia de rollback e especificação do ADR-0014 incluídas.


## Decisão Aprovada no HITL (R-064)
- **Opção Aprovada**: Opção B — Novo Subagente `@plan-critic` Read-Only + Tier 1 Determinístico (Hybrid Two-Tier Pre-HITL Gate).
- **Política de Iteração**: Fast-Pass 1x + Teto 2x (3x em `tier: full`), com Noise Budget ≤ 5 findings `BLOCKER`/`HIGH` (R-065) e escalada `ESCALATED_HITL`.
