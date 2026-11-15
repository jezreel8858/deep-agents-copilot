---
status: APPROVED
approved: true
author: "@requirements-analyst"
plan_type: "requirements"
created_at: "2026-11-14"
related-planning-doc: "N/A — plano raiz"
session_id: "sess-20261114-200000-r064-otel"
workflow_id: "WORKFLOW-FEATURE-DEVELOPMENT"
workflow_trace_id: "wf-20261114-200000-feat-r064-otel-correlation"
parent_plan_ref: "N/A — plano raiz"
allowed_files:
  - ".github/skills/plan-conformance-patterns/SKILL.md"
  - ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md"
  - ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
  - ".github/skills/code-tracing/references/plan-template-bug-triage.md"
  - ".github/skills/governance-audit-patterns/references/plan-template-governance.md"
  - ".github/skills/refactoring-planning-patterns/references/plan-template-refactor.md"
  - ".github/skills/requirements-engineering-patterns/references/plan-template-requirements.md"
  - ".github/skills/specialist-hybrid-advisory-implementation-patterns/references/plan-template-implementation.md"
  - ".github/skills/task-decomposition-patterns/references/plan-template-feature.md"
  - ".github/skills/test-coverage-governance/references/plan-template-test-strategy.md"
  - ".github/skills/agent-observability-otel/SKILL.md"
  - ".github/skills/langfuse-observability/SKILL.md"
  - ".github/skills/handoff-governance/SKILL.md"
  - ".github/skills/handoff-governance/references/detailed-patterns-and-examples.md"
  - ".github/agents/plan-critic.agent.md"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/requirements-analyst.agent.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/feature-planner.agent.md"
  - "docs/plans/README.md"
  - "tests/governance_audit/test_universal_plan_materialization_governance.py"
  - "tests/governance_audit/test_template_sections.py"
critic_rubric_gaps:
  - "T1-8"
  - "T2-SCOPE"
  - "T2-SEC"
  - "T2-COH"
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 2
  minors: 2
  nits: 3
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@requirements-analyst"
review_verdict: PASS_WITH_NITS
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: PASS
lessons_extracted: true
lessons_applied_to: ["@requirements-analyst", "plan-conformance-patterns"]
lessons_at: "2026-11-15"
---

# Especificação de Requisitos — Correlação OTel e Telemetria Estruturada do `@plan-critic` no Frontmatter R-064

## 1. Contexto, Stakeholders e Decisão de Escopo

### 1.1 Contexto Operacional
O contrato de materialização universal de planos (**R-064**, definido em `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` e auditado segundo `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`) governa os 8 diretórios de `docs/plans/` (`architecture`, `bug-triage`, `feature`, `governance`, `implementation`, `refactor`, `requirements`, `test-strategy`). Atualmente, o frontmatter YAML comum R-064 registra metadados básicos de revisão (`review_verdict`, `review_rounds`, `reviewer`, `review_tier1`) e um único vínculo documental (`related-planning-doc`), mas carece de:
1. **Rastreabilidade distribuída fim-a-fim (OTel GenAI Semconv v1.41+)**: ausência de correlação explícita entre o artefato físico `.md` e a sessão de execução (`session_id`), o workflow canônico (`workflow_id`), o trace de orquestração (`workflow_trace_id`) e a árvore genealógica de planos (`parent_plan_ref`).
2. **Telemetria estruturada do `@plan-critic`**: ausência de códigos canônicos de rubrica para falhas recorrentes (`critic_rubric_gaps`) e sumário quantitativo por severidade (`critic_findings_summary`), impedindo agregação analítica determinística sem parsing heurístico de prosa Markdown.
3. **Alinhamento estrito de ciclo de vida pré-revisão**: necessidade de suportar `review_verdict: PENDING` e `review_rounds: 0` no instante em que o plano `DRAFT` é persistido fisicamente para inspeção pelo `@plan-critic`, antes da conclusão do Round 1.

### 1.2 Stakeholders Impactados
- **`@plan-critic`**: consome o plano `DRAFT` persistido em disco, valida determinismo Tier 1 (T1-1 a T1-8) e emite códigos estruturados de lacunas de rubrica e sumário quantitativo de findings.
- **Planejadores e Advisors Read-Only (`@requirements-analyst`, `@tech-solution-architect`, `@feature-planner`, `@refactor-planner`, `@bug-triager`, `@test-Engineer` em modo estratégia, `@agent-auditor`)**: produzem os metadados de correlação e handoff de persistência.
- **Agentes Persistidores (`@docs-engineer`, `@governance-maintainer`)**: materializam fisicamente os planos `DRAFT` e atualizam os metadados após o parecer do `@plan-critic` e após o Gate HITL R-064.
- **`@agent-router`**: valida o Gate Pré-HITL R-064, propaga `session_id`, `workflow_id` e `workflow_trace_id` nos handoffs (`[HANDOFF]` / `telemetry_entry`) e bloqueia transições ilegais.
- **Suíte de Auditoria Determinística (`pytest tests/governance_audit/`)**: valida o contrato de frontmatter e retrocompatibilidade com planos legados.

### 1.3 Decisão de Escopo (In-Scope vs. Out-of-Scope) & Portão de Reúso Sistêmico (R-055 — Q1, Q2, Q3)
- **In-Scope**:
  - Extensão do schema de frontmatter R-064 v2 com 4 campos de correlação OTel (`session_id`, `workflow_id`, `workflow_trace_id`, `parent_plan_ref`) e 2 campos de telemetria do `@plan-critic` (`critic_rubric_gaps`, `critic_findings_summary`).
  - Preservação integral da numeração vigente `T1-1` a `T1-7` da rubrica `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` e adição estritamente aditiva do código `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico) (campos v2 de correlação OTel e telemetria do `@plan-critic`), além dos 6 códigos de Tier 2 (`T2-COMP`, `T2-SEC`, `T2-PERF`, `T2-TEST`, `T2-BACK`, `T2-SCOPE`).
  - Mitigação explícita de **OWASP Agentic Top 10 (ASI06 — Memory & Context Poisoning)** no ciclo de feedback `critic_rubric_gaps` / `critic_findings_summary` → evolução do agent planejador (`author`), exigindo tratamento como dados inertes, escrita exclusiva por `@docs-engineer` / `@governance-maintainer` (`@plan-critic` read-only) e aprovação humana obrigatória via `ask_questions` (HITL) com rastreio de proveniência antes de qualquer mutação em `.github/agents/*.agent.md` ou `.github/skills/**/SKILL.md`.
- **Portão de Reúso Sistêmico (R-055 — Q1, Q2, Q3)**:
  - **Q1 (Impacto em Artefatos Irmãos / Peers)**: Sincronização atômica dos **24 arquivos explícitos** listados em `allowed_files` (100% paritário com o Blueprint Arquitetural), abrangendo `plan-conformance-patterns`, skills de observabilidade (`agent-observability-otel`, `langfuse-observability`), protocolo de handoff (`handoff-governance`), os 7 agentes participantes do ciclo R-064 (`plan-critic`, `agent-router`, `docs-engineer`, `governance-maintainer`, `requirements-analyst`, `tech-solution-architect`, `feature-planner`), `docs/plans/README.md` e a suíte `tests/governance_audit/`.
  - **Q2 (Atualização de Templates Canônicos)**: Existem exatamente **7 arquivos `plan-template-*.md`** físicos em `.github/skills/*/references/` (`plan-template-bug-triage.md`, `plan-template-governance.md`, `plan-template-refactor.md`, `plan-template-requirements.md`, `plan-template-implementation.md`, `plan-template-feature.md`, `plan-template-test-strategy.md`), enquanto a **8ª categoria (`architecture`)** utiliza a seção canônica em `docs/plans/README.md` e `plan-frontmatter-r064.md` (sem referenciar um `blueprint-template.md` inexistente).
  - **Q3 (Testes Determinísticos no `pytest`)**: Expansão dos arquivos existentes `tests/governance_audit/test_universal_plan_materialization_governance.py` e `tests/governance_audit/test_template_sections.py` para validar `T1-1` a `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico), `T2-COMP` a `T2-SCOPE`, o schema v2 (com corte em `2026-11-14` e opt-in explícito) e a proteção anti-ASI06/HITL.
- **Out-of-Scope**:
  - Reescrita retroativa dos 29 planos históricos existentes em `docs/plans/` com `created_at <= "2026-11-14"` que não declararem opt-in v2.
  - Acoplamento de rede em tempo de execução da suíte `pytest` com servidores externos de observabilidade.

---

## 2. Alternativas Rejeitadas

| Alternativa Avaliada | Motivo Técnico da Rejeição |
|---|---|
| **A1. Extrair métricas do `@plan-critic` via Regex sobre a seção Markdown `## Parecer do Revisor Cético Pré-HITL`** | Frágil e propenso a quebras diante de variações estilísticas de prosa Markdown; viola o determinismo exigido em `REQ-NF-002`. |
| **A2. Armazenar a telemetria de revisão exclusivamente no SQLite do `context-mode` (`ctx_index`) sem persistir no frontmatter do plano** | O índice SQLite de sessão é efêmero e local à máquina; persistir no frontmatter YAML garante rastreabilidade versionada no Git junto ao artefato R-064. |
| **A3. Tornar os novos campos obrigatórios retroativamente para todos os planos existentes sem corte temporal (`cutoff date`)** | Quebraria os 29 planos legados já homologados e encerrados no repositório, poluindo o histórico Git sem ganho analítico real. |

---

## 3. Modelagem de Ameaças & Requisitos de Segurança Shift-Left (STRIDE / OWASP LLM & Agentic)

| ID Ameaça | Categoria STRIDE / OWASP | Vetor de Ataque / Risco nos Planos R-064 | Mitigação Shift-Left Exigida |
|---|---|---|---|
| **THR-001** | **Tampering / OWASP Agentic Top 10 (ASI06 — Memory & Context Poisoning)** | Envenenamento ou manipulação de `critic_rubric_gaps` / `critic_findings_summary` para induzir auto-mutação maliciosa nas instruções de `.github/agents/*.agent.md` ou `.github/skills/**/SKILL.md` durante ciclos de evolução dos agents planejadores (`author`). | **REQ-010 / RN-010**: (1) Campos gravados exclusivamente por `@docs-engineer` / `@governance-maintainer` (mantendo `@plan-critic` 100% read-only) e tratados como dados analíticos inertes; (2) `critic_rubric_gaps` restrito ao enum fechado `T1-1..T1-8` e `T2-*`; (3) proibição absoluta de auto-aplicação ou mutação em runtime de `.github/agents/*.agent.md` ou `.github/skills/**/SKILL.md` sem aprovação humana explícita via `ask_questions` (HITL) e rastreio de proveniência (`session_id`, `workflow_trace_id`, `plan_path`, `author`). |
| **THR-002** | **Information Disclosure / PII & Secret Leakage** (OWASP LLM06 / CWE-200) | Vazamento de tokens, credenciais ou dados sensíveis dentro das strings `session_id` ou `workflow_trace_id`. | **REQ-002 / RN-001**: Restrição estrita por regex canônico SSoT `^[a-z0-9][a-z0-9-]{7,95}---
status: DRAFT
approved: false
author: "@requirements-analyst"
plan_type: "requirements"
created_at: "2026-11-14"
related-planning-doc: "N/A — plano raiz"
session_id: "sess-20261114-200000-r064-otel"
workflow_id: "WORKFLOW-FEATURE-DEVELOPMENT"
workflow_trace_id: "wf-20261114-200000-feat-r064-otel-correlation"
parent_plan_ref: "N/A — plano raiz"
allowed_files:
  - ".github/skills/plan-conformance-patterns/SKILL.md"
  - ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md"
  - ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
  - ".github/skills/code-tracing/references/plan-template-bug-triage.md"
  - ".github/skills/governance-audit-patterns/references/plan-template-governance.md"
  - ".github/skills/refactoring-planning-patterns/references/plan-template-refactor.md"
  - ".github/skills/requirements-engineering-patterns/references/plan-template-requirements.md"
  - ".github/skills/specialist-hybrid-advisory-implementation-patterns/references/plan-template-implementation.md"
  - ".github/skills/task-decomposition-patterns/references/plan-template-feature.md"
  - ".github/skills/test-coverage-governance/references/plan-template-test-strategy.md"
  - ".github/skills/agent-observability-otel/SKILL.md"
  - ".github/skills/langfuse-observability/SKILL.md"
  - ".github/skills/handoff-governance/SKILL.md"
  - ".github/skills/handoff-governance/references/detailed-patterns-and-examples.md"
  - ".github/agents/plan-critic.agent.md"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/requirements-analyst.agent.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/feature-planner.agent.md"
  - "docs/plans/README.md"
  - "tests/governance_audit/test_universal_plan_materialization_governance.py"
  - "tests/governance_audit/test_template_sections.py"
critic_rubric_gaps:
  - "T1-8"
  - "T2-SCOPE"
  - "T2-SEC"
  - "T2-COH"
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 2
  minors: 3
  nits: 0
  last_verdict: "NEEDS_REVISION"
  author_ref: "@requirements-analyst"
review_verdict: PENDING
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PENDING
---

# Especificação de Requisitos — Correlação OTel e Telemetria Estruturada do `@plan-critic` no Frontmatter R-064

## 1. Contexto, Stakeholders e Decisão de Escopo

### 1.1 Contexto Operacional
O contrato de materialização universal de planos (**R-064**, definido em `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` e auditado segundo `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`) governa os 8 diretórios de `docs/plans/` (`architecture`, `bug-triage`, `feature`, `governance`, `implementation`, `refactor`, `requirements`, `test-strategy`). Atualmente, o frontmatter YAML comum R-064 registra metadados básicos de revisão (`review_verdict`, `review_rounds`, `reviewer`, `review_tier1`) e um único vínculo documental (`related-planning-doc`), mas carece de:
1. **Rastreabilidade distribuída fim-a-fim (OTel GenAI Semconv v1.41+)**: ausência de correlação explícita entre o artefato físico `.md` e a sessão de execução (`session_id`), o workflow canônico (`workflow_id`), o trace de orquestração (`workflow_trace_id`) e a árvore genealógica de planos (`parent_plan_ref`).
2. **Telemetria estruturada do `@plan-critic`**: ausência de códigos canônicos de rubrica para falhas recorrentes (`critic_rubric_gaps`) e sumário quantitativo por severidade (`critic_findings_summary`), impedindo agregação analítica determinística sem parsing heurístico de prosa Markdown.
3. **Alinhamento estrito de ciclo de vida pré-revisão**: necessidade de suportar `review_verdict: PENDING` e `review_rounds: 0` no instante em que o plano `DRAFT` é persistido fisicamente para inspeção pelo `@plan-critic`, antes da conclusão do Round 1.

### 1.2 Stakeholders Impactados
- **`@plan-critic`**: consome o plano `DRAFT` persistido em disco, valida determinismo Tier 1 (T1-1 a T1-8) e emite códigos estruturados de lacunas de rubrica e sumário quantitativo de findings.
- **Planejadores e Advisors Read-Only (`@requirements-analyst`, `@tech-solution-architect`, `@feature-planner`, `@refactor-planner`, `@bug-triager`, `@test-Engineer` em modo estratégia, `@agent-auditor`)**: produzem os metadados de correlação e handoff de persistência.
- **Agentes Persistidores (`@docs-engineer`, `@governance-maintainer`)**: materializam fisicamente os planos `DRAFT` e atualizam os metadados após o parecer do `@plan-critic` e após o Gate HITL R-064.
- **`@agent-router`**: valida o Gate Pré-HITL R-064, propaga `session_id`, `workflow_id` e `workflow_trace_id` nos handoffs (`[HANDOFF]` / `telemetry_entry`) e bloqueia transições ilegais.
- **Suíte de Auditoria Determinística (`pytest tests/governance_audit/`)**: valida o contrato de frontmatter e retrocompatibilidade com planos legados.

 (apenas letras minúsculas, dígitos e hífens, 8 a 96 caracteres). |
| **THR-003** | **Repudiation / Audit Bypass** (STRIDE Repudiation / Elevation of Privilege) | Aprovação de plano no Gate HITL R-064 (`status: APPROVED` ou `approved: true`) mantendo `review_verdict: PENDING`, `review_tier1: PENDING/FAIL` ou `review_rounds: 0`. | **REQ-005 / RN-004**: Bloqueio determinístico fail-closed na validação Tier 1 e na suíte `pytest tests/governance_audit/`. |
| **THR-004** | **Tampering / Path Traversal & Unsafe YAML** (CWE-22 / CWE-502) | Uso de `../`, caminhos absolutos ou âncoras YAML maliciosas em `parent_plan_ref`, `allowed_files` e frontmatter. | **REQ-003 / REQ-NF-003 / REQ-NF-009**: Normalização POSIX sem `..` ou drive letters, verificação física em disco e parsing exclusivo via `yaml.safe_load`. |

---

## 4. Regras de Negócio (RN-001 a RN-011)

- **RN-001 (Invariante de Correlação de Sessão e Workflow)**: Todo plano R-064 novo (`created_at > "2026-11-14"` ou com opt-in explícito de chaves v2 em `created_at <= "2026-11-14"`) deve declarar `session_id`, `workflow_id`, `workflow_trace_id` e `parent_plan_ref`, sendo `session_id` e `workflow_trace_id` validados pelo regex canônico SSoT `^[a-z0-9][a-z0-9-]{7,95}---
status: DRAFT
approved: false
author: "@requirements-analyst"
plan_type: "requirements"
created_at: "2026-11-14"
related-planning-doc: "N/A — plano raiz"
session_id: "sess-20261114-200000-r064-otel"
workflow_id: "WORKFLOW-FEATURE-DEVELOPMENT"
workflow_trace_id: "wf-20261114-200000-feat-r064-otel-correlation"
parent_plan_ref: "N/A — plano raiz"
allowed_files:
  - ".github/skills/plan-conformance-patterns/SKILL.md"
  - ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md"
  - ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
  - ".github/skills/code-tracing/references/plan-template-bug-triage.md"
  - ".github/skills/governance-audit-patterns/references/plan-template-governance.md"
  - ".github/skills/refactoring-planning-patterns/references/plan-template-refactor.md"
  - ".github/skills/requirements-engineering-patterns/references/plan-template-requirements.md"
  - ".github/skills/specialist-hybrid-advisory-implementation-patterns/references/plan-template-implementation.md"
  - ".github/skills/task-decomposition-patterns/references/plan-template-feature.md"
  - ".github/skills/test-coverage-governance/references/plan-template-test-strategy.md"
  - ".github/skills/agent-observability-otel/SKILL.md"
  - ".github/skills/langfuse-observability/SKILL.md"
  - ".github/skills/handoff-governance/SKILL.md"
  - ".github/skills/handoff-governance/references/detailed-patterns-and-examples.md"
  - ".github/agents/plan-critic.agent.md"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/requirements-analyst.agent.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/feature-planner.agent.md"
  - "docs/plans/README.md"
  - "tests/governance_audit/test_universal_plan_materialization_governance.py"
  - "tests/governance_audit/test_template_sections.py"
critic_rubric_gaps:
  - "T1-8"
  - "T2-SCOPE"
  - "T2-SEC"
  - "T2-COH"
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 2
  minors: 3
  nits: 0
  last_verdict: "NEEDS_REVISION"
  author_ref: "@requirements-analyst"
review_verdict: PENDING
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PENDING
---

# Especificação de Requisitos — Correlação OTel e Telemetria Estruturada do `@plan-critic` no Frontmatter R-064

## 1. Contexto, Stakeholders e Decisão de Escopo

### 1.1 Contexto Operacional
O contrato de materialização universal de planos (**R-064**, definido em `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` e auditado segundo `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`) governa os 8 diretórios de `docs/plans/` (`architecture`, `bug-triage`, `feature`, `governance`, `implementation`, `refactor`, `requirements`, `test-strategy`). Atualmente, o frontmatter YAML comum R-064 registra metadados básicos de revisão (`review_verdict`, `review_rounds`, `reviewer`, `review_tier1`) e um único vínculo documental (`related-planning-doc`), mas carece de:
1. **Rastreabilidade distribuída fim-a-fim (OTel GenAI Semconv v1.41+)**: ausência de correlação explícita entre o artefato físico `.md` e a sessão de execução (`session_id`), o workflow canônico (`workflow_id`), o trace de orquestração (`workflow_trace_id`) e a árvore genealógica de planos (`parent_plan_ref`).
2. **Telemetria estruturada do `@plan-critic`**: ausência de códigos canônicos de rubrica para falhas recorrentes (`critic_rubric_gaps`) e sumário quantitativo por severidade (`critic_findings_summary`), impedindo agregação analítica determinística sem parsing heurístico de prosa Markdown.
3. **Alinhamento estrito de ciclo de vida pré-revisão**: necessidade de suportar `review_verdict: PENDING` e `review_rounds: 0` no instante em que o plano `DRAFT` é persistido fisicamente para inspeção pelo `@plan-critic`, antes da conclusão do Round 1.

### 1.2 Stakeholders Impactados
- **`@plan-critic`**: consome o plano `DRAFT` persistido em disco, valida determinismo Tier 1 (T1-1 a T1-8) e emite códigos estruturados de lacunas de rubrica e sumário quantitativo de findings.
- **Planejadores e Advisors Read-Only (`@requirements-analyst`, `@tech-solution-architect`, `@feature-planner`, `@refactor-planner`, `@bug-triager`, `@test-Engineer` em modo estratégia, `@agent-auditor`)**: produzem os metadados de correlação e handoff de persistência.
- **Agentes Persistidores (`@docs-engineer`, `@governance-maintainer`)**: materializam fisicamente os planos `DRAFT` e atualizam os metadados após o parecer do `@plan-critic` e após o Gate HITL R-064.
- **`@agent-router`**: valida o Gate Pré-HITL R-064, propaga `session_id`, `workflow_id` e `workflow_trace_id` nos handoffs (`[HANDOFF]` / `telemetry_entry`) e bloqueia transições ilegais.
- **Suíte de Auditoria Determinística (`pytest tests/governance_audit/`)**: valida o contrato de frontmatter e retrocompatibilidade com planos legados.

.
- **RN-002 (Enumeração Canônica de `workflow_id`)**: O campo `workflow_id` aceita exclusivamente os 11 identificadores canônicos de workflows registrados na governança (`WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-BUG-RESOLUTION`, `WORKFLOW-CODE-REFACTORING`, `WORKFLOW-GOVERNANCE-MAINTENANCE`, `WORKFLOW-GOVERNANCE-FACTORY`, `WORKFLOW-SECURITY-AUDIT`, `WORKFLOW-TEST-AUTOMATION`, `WORKFLOW-MIGRATION`, `WORKFLOW-PERFORMANCE-TUNING`, `WORKFLOW-DOCUMENTATION`, `WORKFLOW-STANDALONE`).
- **RN-003 (Integridade Genealógica de `parent_plan_ref` e `related-planning-doc`)**: Planos raiz devem declarar `"N/A — plano raiz"` (ou `"N/A"`); planos derivados devem declarar um caminho POSIX relativo existente fisicamente em `docs/plans/`.
- **RN-004 (Ciclo de Vida de `review_verdict`, `review_tier1` e `review_rounds`)**:
  - Na materialização inicial do `DRAFT` ou aguardando nova rodada do `@plan-critic`: `status: DRAFT`, `approved: false`, `review_verdict: PENDING`, `review_tier1: PENDING` (vedado autodeclarar `review_tier1: PASS` antes do parecer final da rodada vigente).
  - Após o parecer final aprobatório/escalado do `@plan-critic`: `review_verdict` assume `PASS | PASS_WITH_NITS | ESCALATED_HITL`, `review_tier1` assume `PASS` e `review_rounds` assume inteiro em `1..3`.
  - Na aprovação humana pós-HITL: `status: APPROVED`, `approved: true`, sendo proibido aprovar com `review_verdict: PENDING`, `review_tier1: PENDING/FAIL` ou `review_rounds: 0`.
- **RN-005 (Taxonomia Fechada de `critic_rubric_gaps` — Preservação de `T1-1` a `T1-7` Vigentes + `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico) Aditivo)**: O array `critic_rubric_gaps` aceita exclusivamente um subconjunto ordenado e sem duplicatas dos **14 códigos canônicos**, preservando **exatamente a numeração e ordem vigentes** em `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`:
  - **Tier 1 (Determinístico — `T1-1` a `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico))**:
    - `T1-1`: Nomenclatura e diretório (`docs/plans/<categoria>/<AAAAMMDD-HHMMSS>-<slug>.md`)
    - `T1-2`: Frontmatter obrigatório (`status`, `approved`, `author`, `plan_type`, `created_at`, `allowed_files`, `related-planning-doc`, `review_verdict`, `review_rounds`, `reviewer`, `review_tier1`)
    - `T1-3`: Coerência `plan_type` vs subpasta
    - `T1-4`: Campos específicos de `implementation` (`specialist_agent`, `delegated_by`, `scope_complexity`, `tier1_Skip_eligible`)
    - `T1-5`: Grounding de `allowed_files` (caminhos explícitos verificados em disco, sem globs)
    - `T1-6`: Seções obrigatórias do template da categoria
    - `T1-7` (Ausência de placeholders não resolvidos (`TODO`, `TBD`, `FIXME`, `<...>`) no plano)
    - `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico) *(novo, aditivo)*: Campos v2 de correlação OTel (`session_id`, `workflow_id`, `workflow_trace_id`, `parent_plan_ref`) e telemetria do `@plan-critic` (`critic_rubric_gaps`, `critic_findings_summary`)
  - **Tier 2 (Semântico Cético — `T2-COMP` a `T2-SCOPE`)**:
    - `T2-COMP` (Completude & Edge Cases), `T2-SEC` (Segurança Shift-Left & OWASP ASI06), `T2-PERF` (Performance & N+1), `T2-TEST` (Testabilidade & Critérios de Aceite), `T2-BACK` (Backward Compatibility & Rollback), `T2-SCOPE` (Aderência ao Escopo & Portão R-055).
- **RN-006 (Consistência Matemática de `critic_findings_summary`)**: O objeto `critic_findings_summary` contém obrigatoriamente as chaves `rounds`, `blockers`, `majors`, `minors`, `nits`, `last_verdict` (`null | "NEEDS_REVISION" | "PASS" | "PASS_WITH_NITS" | "ESCALATED_HITL"`) e `author_ref` (idêntico a `author`).
- **RN-007 (Noise Budget do `@plan-critic`)**: Em conformidade com a rubrica Pré-HITL, a soma `blockers + majors` reportada em cada rodada do `@plan-critic` respeita o teto de foco cético.
- **RN-008 (Corte de Retrocompatibilidade — Cutoff Date & Opt-in v2)**: Planos com `created_at <= "2026-11-14"` que não declararem nenhuma chave v2 permanecem isentos de `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico); planos com `created_at <= "2026-11-14"` que declararem qualquer chave v2 (opt-in explícito, como os 2 planos desta entrega) são validados integralmente pelas regras do schema R-064 v2 (`T1-8`).
- **RN-009 (Proibição de Placeholders e Globs Indevidos)**: Nenhum plano R-064 pode conter marcadores de incompletude (`TODO`, `TBD`) ou globs em `allowed_files`.
- **RN-010 (Mitigação de OWASP Agentic Top 10 ASI06 — Memory & Context Poisoning + HITL Obrigatório)**: Os campos `critic_rubric_gaps` e `critic_findings_summary` são gravados exclusivamente por `@docs-engineer` / `@governance-maintainer` (mantendo `@plan-critic` 100% read-only) e tratados como dados inertes. É terminantemente proibida qualquer auto-aplicação ou mutação em runtime de `.github/agents/*.agent.md` ou `.github/skills/**/SKILL.md` a partir de `critic_rubric_gaps` / `critic_findings_summary` sem aprovação humana explícita via `ask_questions` (HITL) e rastreio de proveniência (`session_id`, `workflow_trace_id`, `plan_path`, `author`).
- **RN-011 (Sincronização dos 7 Templates `plan-template-*.md` e Categoria `architecture`)**: Existem **7 arquivos `plan-template-*.md`** em `.github/skills/*/references/`, enquanto a 8ª categoria (`architecture`) utiliza a seção canônica em `docs/plans/README.md` e `plan-frontmatter-r064.md` (sem referenciar um `blueprint-template.md` inexistente). Planejadores (`@requirements-analyst`, `@tech-solution-architect`, `@feature-planner`, `@plan-critic`) permanecem 100% Read-Only.

---

## 5. Requisitos Funcionais (REQ-001 a REQ-013 — Notação EARS & Gherkin)

### REQ-001 — Metadados de Correlação OTel no Frontmatter R-064
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` e `.github/skills/agent-observability-otel/SKILL.md`
- **Declaração EARS**: **Ubiquitous** — O schema canônico de frontmatter R-064 shall incluir os campos `session_id`, `workflow_id`, `workflow_trace_id` e `parent_plan_ref` em todos os novos planos gerados sob o contrato R-064 v2.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Validação de campos de correlação OTel em novo plano R-064
    Given um plano Markdown recém-materializado em "docs/plans/" sob o schema R-064 v2
    When o validador Tier 1 inspeciona o bloco YAML de frontmatter
    Then os campos "session_id", "workflow_id", "workflow_trace_id" e "parent_plan_ref" devem estar presentes como strings não vazias
    And "workflow_id" deve pertencer à enumeração canônica de workflows do repositório
  ```

### REQ-002 — Formato Determinístico de `session_id` e `workflow_trace_id`
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/skills/handoff-governance/SKILL.md` (§ 2.4 Telemetria de Handoff)
- **Declaração EARS**: **When** um plano R-064 declara `session_id` e `workflow_trace_id`, o validador Tier 1 shall verificar que ambos obedecem ao padrão seguro ASCII `^[a-z0-9][a-z0-9-]{7,95}$` sem espaços ou caracteres especiais.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Rejeição de identificadores de correlação malformados
    Given um plano R-064 com "session_id" contendo espaços ou caracteres fora de "[a-zA-Z0-9_-]"
    When a validação determinística Tier 1 é executada
    Then o validador deve reportar falha no código "T1-1"
  ```

### REQ-003 — Validação de Existência Física de `parent_plan_ref`
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` (Item 6 do Tier 1)
- **Declaração EARS**: **If** o campo `parent_plan_ref` (ou `related-planning-doc`) for diferente de `"N/A"` e `"N/A — plano raiz"`, **then** o validador Tier 1 shall comprovar que o caminho referenciado existe fisicamente em `docs/plans/`.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Verificação de plano pai existente em plano de arquitetura derivado
    Given um plano em "docs/plans/architecture/" que declara "parent_plan_ref" apontando para um plano em "docs/plans/requirements/"
    When o validador Tier 1 verifica a árvore genealógica de planos
    Then o arquivo referenciado em "parent_plan_ref" deve existir fisicamente no disco
    And o valor de "parent_plan_ref" deve ser consistente com "related-planning-doc"
  ```

### REQ-004 — Suporte ao Estado Inicial `PENDING` e `review_rounds: 0` em Planos `DRAFT`
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/agents/plan-critic.agent.md` e `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`
- **Declaração EARS**: **While** um plano estiver em `status: DRAFT` e `approved: false` aguardando a primeira inspeção do `@plan-critic`, o schema R-064 shall permitir `review_verdict: PENDING` e `review_rounds: 0`.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Materialização física de plano DRAFT antes da revisão do @plan-critic
    Given um plano recém-criado com "status: DRAFT" e "approved: false"
    When o frontmatter declara "review_verdict: PENDING" e "review_rounds: 0"
    Then o validador Tier 1 deve aceitar o estado inicial sem erro de schema
  ```

### REQ-005 — Bloqueio Fail-Closed de Aprovação com `review_verdict: PENDING`
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/agents/agent-router.agent.md` (Gate R-064)
- **Declaração EARS**: **If** um plano declarar `status: APPROVED` ou `approved: true` enquanto `review_verdict` for `PENDING` ou `review_rounds` for `0` ou `review_tier1` for `FAIL`, **then** o validador de conformidade R-064 shall rejeitar o artefato com erro bloqueante (`T1-1`).
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Tentativa de aprovar plano sem conclusão da revisão cética
    Given um plano com "status: APPROVED" ou "approved: true"
    And "review_verdict: PENDING" ou "review_rounds: 0"
    When a validação de governança R-064 é executada
    Then a validação deve falhar imediatamente bloqueando a transição
  ```

### REQ-006 — Codificação Canônica `T1-1` a `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico) (Preservando `T1-1` a `T1-7` Vigentes) e `T2-COMP` a `T2-SCOPE` na Rubrica
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`
- **Declaração EARS**: **Ubiquitous** — A referência `pre-hitl-skeptical-review-rubric.md` **shall** preservar intacta a ordem vigente das 7 verificações `T1-1` a `T1-7`, adicionar `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico) para os campos v2 de correlação OTel e telemetria do `@plan-critic`, e identificar cada dimensão do Tier 2 pelos códigos `T2-COMP`, `T2-SEC`, `T2-PERF`, `T2-TEST`, `T2-BACK` e `T2-SCOPE`.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Preservação de T1-1 a T1-7 e adição de T1-8 na rubrica de revisão cética
    Given o arquivo ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
    When auditado pela suíte de testes de governança
    Then os códigos "T1-1" a "T1-7" devem preservar exatamente sua ordem e semântica vigentes
    And o código aditivo "T1-8" deve documentar a validação dos campos v2 de correlação OTel e telemetria do "@plan-critic"
    And os 6 códigos Tier 2 ("T2-COMP" a "T2-SCOPE") devem estar documentados
  ```

### REQ-007 — Campo `critic_rubric_gaps` no Frontmatter R-064
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`
- **Declaração EARS**: **When** o plano utiliza o schema R-064 v2 com telemetria do `@plan-critic`, o frontmatter shall conter a lista `critic_rubric_gaps` (vazia `[]` quando sem gaps ou populada exclusivamente com códigos canônicos `T1-*` / `T2-*`).
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Validação de códigos em critic_rubric_gaps
    Given um plano R-064 v2 contendo o campo "critic_rubric_gaps"
    When os elementos da lista são validados
    Then cada item deve pertencer ao conjunto fechado de 14 códigos canônicos (`T1-1` a `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico) e `T2-COMP` a `T2-SCOPE`) da rubrica e não conter duplicatas
  ```

### REQ-008 — Objeto `critic_findings_summary` no Frontmatter R-064
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` e `.github/agents/plan-critic.agent.md`
- **Declaração EARS**: **When** o plano utiliza o schema R-064 v2 com telemetria do `@plan-critic`, o frontmatter shall declarar o mapa `critic_findings_summary` com as chaves `rounds`, `blockers`, `majors`, `minors`, `nits`, `last_verdict` e `author_ref`.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Estrutura obrigatória de critic_findings_summary
    Given um plano R-064 v2 com "critic_findings_summary"
    When o parser valida os tipos das chaves internas
    Then "rounds", "blockers", "majors", "minors" e "nits" devem ser inteiros >= 0
    And "last_verdict" deve ser null (em DRAFT pré-revisão) ou um veredito válido ("PASS", "PASS_WITH_NITS", "ESCALATED_HITL")
    And "author_ref" deve coincidir com o campo "author" do frontmatter
  ```

### REQ-009 — Coerência entre `review_verdict` e Contadores de `critic_findings_summary`
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`
- **Declaração EARS**: **If** `review_verdict` for `PASS`, **then** `critic_findings_summary` shall registrar `blockers: 0`, `majors: 0` e `nits: 0`; **if** `review_verdict` for `PASS_WITH_NITS`, **then** `critic_findings_summary` shall registrar `blockers: 0`, `majors: 0` e `minors + nits >= 1`.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Detecção de contradição entre veredito PASS e contagem de blockers
    Given um plano com "review_verdict: PASS"
    And "critic_findings_summary.blockers" igual a 1
    When o validador de integridade R-064 executa
    Then uma violação de consistência deve ser lançada
  ```

### REQ-010 — Proteção contra Memory & Context Poisoning (OWASP Agentic Top 10 ASI06) e Obrigatoriedade de HITL na Evolução de Agentes (`MUST`)
- **Declaração EARS**: **While** os campos `critic_rubric_gaps` e `critic_findings_summary` forem consumidos para diagnóstico de qualidade ou melhoria contínua dos agents planejadores (`author`), the system **shall** tratar seus valores exclusivamente como dados inertes gravados por `@docs-engineer` ou `@governance-maintainer` (preservando `@plan-critic` 100% read-only), and **If** qualquer ajuste em `.github/agents/*.agent.md` ou `.github/skills/**/SKILL.md` for proposto a partir dessa telemetria, **then** the system **shall** bloquear qualquer auto-aplicação ou mutação em runtime sem aprovação humana explícita via `ask_questions` (HITL) e rastreio completo de proveniência (`session_id`, `workflow_trace_id`, `plan_path`, `author`), mitigando **OWASP Agentic Top 10 (ASI06 — Memory & Context Poisoning)**.
- **Prioridade MoSCoW**: `MUST`
- **Fonte Canônica**: OWASP Agentic Top 10 2026 (ASI06 — Memory & Context Poisoning), `.github/agents/plan-critic.agent.md` e `copilot-instructions.md` (R-064).
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Bloqueio de auto-mutação de instruções de agentes via telemetria (OWASP ASI06)
    Given um conjunto de planos R-064 v2 contendo "critic_rubric_gaps" e "critic_findings_summary"
    When um fluxo de manutenção analisa reincidências por "author_ref" para propor melhorias em ".github/agents/*.agent.md" ou ".github/skills/**/SKILL.md"
    Then os campos de telemetria devem ser processados exclusivamente como dados inertes (nunca executados ou concatenados automaticamente em prompts de sistema em runtime)
    And a gravação física no frontmatter do plano deve ser restrita a "@docs-engineer" e "@governance-maintainer" (mantendo "@plan-critic" read-only)
    And nenhuma modificação em ".github/agents/*.agent.md" ou ".github/skills/**/SKILL.md" pode ocorrer sem aprovação humana explícita via "ask_questions" (HITL) e registro de proveniência ("session_id", "workflow_trace_id", "plan_path", "author")
  ```

### REQ-011 — Preservação de Retrocompatibilidade com Planos Legados (`created_at <= 2026-11-14`)
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `tests/governance_audit/test_universal_plan_materialization_governance.py`
- **Declaração EARS**: **Where** um plano existente em `docs/plans/` possuir `created_at <= "2026-11-14"` e não declarar os campos da extensão v2, a suíte de validação R-064 shall aplicar as regras do schema base v1 sem falhar retroativamente.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Execução do pytest sobre os 29 planos legados do repositório
    Given os 29 planos existentes em "docs/plans/" com "created_at" até "2026-11-14"
    When a suíte "pytest tests/governance_audit/" é executada
    Then nenhum plano legado deve falhar por ausência dos novos campos v2
    And planos de "2026-11-14" que optarem por declarar os campos v2 devem ser validados com sucesso
  ```

### REQ-012 — Emissão de Telemetria pelo `@plan-critic` no Contrato do Agente
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `.github/agents/plan-critic.agent.md`
- **Declaração EARS**: **When** o `@plan-critic` conclui uma rodada de avaliação Pré-HITL, o agente shall retornar em seu parecer estruturado os valores exatos de `critic_rubric_gaps` e `critic_findings_summary` para persistência pelo agente gravador (`@docs-engineer` ou `@governance-maintainer`).
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Output estruturado do @plan-critic pronto para persistência
    Given um plano DRAFT submetido ao "@plan-critic"
    When o "@plan-critic" emite seu parecer final
    Then o output deve conter explicitamente "review_tier1", "review_verdict", "review_rounds", "critic_rubric_gaps" e "critic_findings_summary"
  ```

### REQ-013 — Cobertura de Testes Automatizados Determinísticos (`pytest`)
- **Prioridade MoSCoW**: Must Have
- **Fonte**: `tests/governance_audit/test_universal_plan_materialization_governance.py` e `tests/governance_audit/test_template_sections.py`
- **Declaração EARS**: **Ubiquitous** — A suíte `tests/governance_audit/` shall conter testes unitários determinísticos validando os códigos `T1-1` a `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico), `T2-COMP` a `T2-SCOPE`, a consistência de `critic_findings_summary`, a correlação `session_id`/`workflow_id`/`workflow_trace_id`/`parent_plan_ref` e a regra de cutoff de retrocompatibilidade.
- **Critério de Aceite (Gherkin)**:
  ```gherkin
  Scenario: Execução da suíte de testes de auditoria de governança
    Given a suíte de testes em "tests/governance_audit/"
    When executado o comando "pytest tests/governance_audit/"
    Then 100% dos testes novos e existentes devem passar com código de saída 0
  ```

---

## 6. Requisitos Não-Funcionais (REQ-NF-001 a REQ-NF-009 — Taxonomia FURPS+)

| ID | Categoria FURPS+ | Prioridade | Declaração EARS & Métrica Objetiva | Critério de Aceite (Gherkin Resumido) | Fonte |
|---|---|---|---|---|---|
| **REQ-NF-001** | **Performance** | Must Have | **When** a suíte de testes valida todos os arquivos em `docs/plans/`, o tempo total de parsing e verificação do frontmatter R-064 shall ser inferior a **500 ms** em execução local. | `Given` ~35 planos em `docs/plans/`, `When` validados em lote, `Then` a execução conclui em `< 500ms`. | `tests/governance_audit/` |
| `T1-8` | Segregação `reviewer != author` e integridade dos novos campos v2 de correlação OTel (`session_id`, `workflow_trace_id` com regex `^[a-z0-9][a-z0-9-]{7,95}$`) e telemetria estruturada do `@plan-critic` (`critic_rubric_gaps` subset fechado e `critic_findings_summary` com contagens inteiras `>= 0`, `rounds == review_rounds` e `last_verdict == review_verdict`) |
| **REQ-NF-003** | **Security (Safe Parsing)** | Must Have | **Ubiquitous** — Todo carregamento de frontmatter YAML em scripts e testes shall utilizar exclusivamente `yaml.safe_load` (Python) ou parser sem execução arbitrária. | `Given` os testes em `tests/governance_audit/`, `When` inspecionado o uso de PyYAML, `Then` inexiste `yaml.load` inseguro. | OWASP / CWE-502 |
| **REQ-NF-004** | **Usability (Legibilidade Humana)** | Should Have | **Ubiquitous** — O bloco de frontmatter R-064 estendido shall manter estrutura plana/rasa (máximo 2 níveis de aninhamento YAML, restrito a `allowed_files`, `critic_rubric_gaps` e `critic_findings_summary`). | `Given` o frontmatter R-064 v2, `When` inspecionada a profundidade da árvore YAML, `Then` profundidade máxima `<= 2`. | `plan-frontmatter-r064.md` |
| **REQ-NF-005** | **Supportability (Retrocompatibilidade)** | Must Have | **Where** `created_at <= "2026-11-14"` e sem campos v2, o validador shall preservar 100% de compatibilidade com os 29 planos históricos sem exigir migração manual. | `Given` os 29 planos legados, `When` rodado `pytest`, `Then` 0 regressões ocorrem. | RN-008 |
| **REQ-NF-006** | **Maintainability (Single Source of Truth)** | Must Have | **Ubiquitous** — A definição canônica do schema R-064 v2 shall residir em `plan-frontmatter-r064.md` e na rubrica `pre-hitl-skeptical-review-rubric.md`, evitando duplicação divergente em múltiplos agents (R-066 Progressive Disclosure). | `Given` as skills e agents, `When` auditados, `Then` apontam para a referência central em `plan-conformance-patterns`. | R-066 / `SKILL.md` |
| **REQ-NF-007** | ** + Constraints (Context Firewall)** | Must Have | **While** o `@plan-critic` audita um plano `DRAFT`, o subagente shall operar sob Context Firewall estrito (recebendo apenas o caminho do plano, template/rubrica e arquivos listados no plano, sem histórico de raciocínio do autor). | `Given` o contrato em `plan-critic.agent.md`, `When` acionado pelo router, `Then` opera 100% Read-Only e isolado. | ADR-0014 / R-064 |
| **REQ-NF-008** | ** + Observability (OTel Semconv Alignment)** | Should Have | **Ubiquitous** — Os nomes e formatos de `session_id`, `workflow_id` e `workflow_trace_id` shall manter compatibilidade semântica com os atributos de span e eventos `[HANDOFF]` `telemetry_entry` da skill `agent-observability-otel`. | `Given` um evento `[HANDOFF]` e o plano gerado na sessão, `When` comparados, `Then` compartilham a mesma chave `session_id`. | `agent-observability-otel/SKILL.md` |
| **REQ-NF-009** | ** + Portability (Cross-Platform Path Format)** | Must Have | **Ubiquitous** — Todos os caminhos registrados em `allowed_files`, `related-planning-doc` e `parent_plan_ref` shall utilizar separador POSIX (`/`) relativo à raiz do repositório, mesmo quando gerados no Windows. | `Given` qualquer caminho no frontmatter, `When` validado no Windows/Linux, `Then` não contém `\` nem drive letters (`D:`). | `T1-2` / `T1-5` |

---

## 7. Matriz de Rastreabilidade (RN ↔ REQ ↔ REQ-NF ↔ Artefatos & Testes)

| Regra de Negócio | Requisitos Funcionais | Requisitos Não-Funcionais | Artefato Canônico Alvo | Teste Automatizado de Verificação |
|---|---|---|---|---|
| **RN-001, RN-002** | REQ-001, REQ-002 | REQ-NF-008 | `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` | `tests/governance_audit/test_universal_plan_materialization_governance.py` |
| **RN-003** | REQ-003 | REQ-NF-009 | `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` | `tests/governance_audit/test_universal_plan_materialization_governance.py` |
| **RN-004** | REQ-004, REQ-005 | REQ-NF-002 | `.github/agents/agent-router.agent.md`, `.github/agents/plan-critic.agent.md` | `tests/governance_audit/test_universal_plan_materialization_governance.py` |
| **RN-005** | REQ-006, REQ-007 | REQ-NF-006 | `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` | `tests/governance_audit/test_template_sections.py` |
| **RN-006, RN-007** | REQ-008, REQ-009, REQ-012 | REQ-NF-003, REQ-NF-004, REQ-NF-007 | `.github/agents/plan-critic.agent.md`, `.github/agents/docs-engineer.agent.md` | `tests/governance_audit/test_universal_plan_materialization_governance.py` |
| **RN-008** | REQ-011, REQ-013 | REQ-NF-001, REQ-NF-005 | `tests/governance_audit/test_universal_plan_materialization_governance.py` | `tests/governance_audit/test_universal_plan_materialization_governance.py` |
| **RN-009, RN-010, RN-011** | REQ-010, REQ-012 | REQ-NF-002, REQ-NF-009 | `.github/skills/requirements-engineering-patterns/references/plan-template-requirements.md` | `tests/governance_audit/test_template_sections.py` |

---

## 8. Evidências Verificadas no Repositório

1. **`plan-frontmatter-r064.md`** (`.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`): atualmente define `status`, `approved`, `author`, `plan_type`, `created_at`, `related-planning-doc`, `allowed_files` e os 4 metadados de revisão (`review_verdict`, `review_rounds`, `reviewer`, `review_tier1`).
2. **`pre-hitl-skeptical-review-rubric.md`** (`.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`): enumera 7 itens no Tier 1 e 6 dimensões no Tier 2, além da tabela de decisão de vereditos (`PASS`, `PASS_WITH_NITS`, `ESCALATED_HITL`), porém ainda sem os rótulos explícitos `T1-1 a T1-7` e `T2-COMP a T2-SCOPE` nem o mapeamento para `critic_rubric_gaps` e `critic_findings_summary`.
3. **Inventário de Planos Legados em `docs/plans/`**: verificados 29 arquivos de planos existentes distribuídos nas subpastas de `docs/plans/`, com datas `created_at` compreendidas entre `2026-08-30` e `2026-11-14`.
4. **Suíte de Testes de Governança**: `tests/governance_audit/test_universal_plan_materialization_governance.py` e `tests/governance_audit/test_template_sections.py` validam a presença das referências R-064 e seções obrigatórias dos templates.

---

## 9. Lacunas, Ambiguidades Resolvidas e Perguntas em Aberto

- **Ambiguidade Resolvida 1 (Estado do Plano no Disco Antes do `@plan-critic`)**: Como o `@plan-critic` audita o arquivo físico já gravado em `docs/plans/`, o plano nasce no disco com `status: DRAFT`, `approved: false`, `review_verdict: PENDING` e `review_rounds: 0`. Após o parecer do `@plan-critic`, passa para `PASS | PASS_WITH_NITS | ESCALATED_HITL` e `review_rounds: 1 a 3`.
- **Ambiguidade Resolvida 2 (Compatibilidade com Planos de `2026-11-14`)**: O corte de obrigatoriedade estrita aplica-se a `created_at >= "2026-11-15"`, mas qualquer plano com `created_at == "2026-11-14"` que já declare `session_id` / `critic_findings_summary` (opt-in da própria entrega) tem seus novos campos validados integralmente.
- **Perguntas em Aberto para o Usuário**: Nenhuma pergunta bloqueante pendente; requisitos 100% fechados e prontos para o Blueprint Arquitetural e revisão do `@plan-critic`.

---

## 10. Parecer do Revisor Cético Pré-HITL (R-064)

### Resumo Executivo do Veredito (Rodada 2 — Final)

| Campo | Valor |
|---|---|
| **`review_verdict`** | `PASS_WITH_NITS` |
| **`review_rounds`** | `2` |
| **`reviewer`** | `"@plan-critic"` |
| **`review_tier1`** | `PASS` |
| **`status` / `approved`** | `DRAFT` / `false` (aguardando aprovação humana via `ask_questions` no Gate HITL R-064) |

### Verificação de Resolução dos 5 Achados da Rodada 1 (`NEEDS_REVISION` → `PASS_WITH_NITS`)

| # | Severidade / Código (R1) | Achado da Rodada 1 | Status na Rodada 2 | Evidência de Resolução Verificada pelo `@plan-critic` |
|---|---|---|---|---|
| 1 | `HIGH` (`T2-SEC`) | Ameaça `THR-001` sem citação explícita de OWASP Agentic Top 10 2026 ASI06 e travas de governança no loop `critic_rubric_gaps` → evolução do planejador | **RESOLVIDO (`PASS`)** | `THR-001` cita explicitamente **OWASP Agentic Top 10 2026 — ASI06 (Memory & Context Poisoning)**, dados inertes, escrita exclusiva por `@docs-engineer` / `@governance-maintainer`, proibição de mutação sem HITL (`ask_questions`) e invariante em `tests/governance_audit/`. |
| 2 | `HIGH` (`T2-SCOPE`) | Menção a `blueprint-template.md` inexistente na árvore física e ausente de `allowed_files` | **RESOLVIDO (`PASS`)** | Zero ocorrências de `blueprint-template.md`; referenciados apenas os 7 templates reais `plan-template-*.md` + `docs/plans/README.md` + `plan-frontmatter-r064.md` (100% contidos nos 24 `allowed_files`). |
| 3 | `MEDIUM` (`T2-CONS`) | Divergência de regex para `session_id` / `workflow_trace_id` entre planos e seções | **RESOLVIDO (`PASS`)** | Regex canônico SSoT único `^[a-z0-9][a-z0-9-]{7,95}$` (minúsculas, dígitos e hífens, 8 a 96 chars) unificado em 100% de ambos os planos. |
| 4 | `MEDIUM` (`T1-8`) | Autoatestado prévio de aprovação na §10 antes da conclusão do crítico e ausência de dogfooding da Rodada 1 | **RESOLVIDO (`PASS`)** | Autoatestado prévio removido; dogfooding real da Rodada 1 e parecer oficial da Rodada 2 registrados com segregação estrita `@requirements-analyst != @plan-critic`. |
| 5 | `LOW` (`T2-TEST`) | Ausência de cenário Gherkin explícito para o caso de borda de opt-in v2 (`created_at <= "2026-11-14"` com chaves v2 presentes) | **RESOLVIDO (`PASS`)** | Cenário Gherkin explícito de opt-in v2 incluído (em `RF-05` no Plano 1 e na decisão `L4` no Plano 2), garantindo validação integral `T1-8` quando qualquer chave v2 é declarada. |

### NITs da Rodada 2 Endereçados (`nits: 3` acumulados)

| NIT | Código | Descrição e Endereçamento |
|---|---|---|
| **NIT #1** | `T1-8` | **Sincronização do frontmatter pós-Rodada 2**: `review_verdict: PASS_WITH_NITS`, `review_rounds: 2`, `review_tier1: PASS` e `critic_findings_summary` (`rounds: 2`, `nits: 3`, `last_verdict: "PASS_WITH_NITS"`) persistidos mantendo `status: DRAFT` e `approved: false` até a resposta humana do `ask_questions`. |
| **NIT #2** | `T2-CONS` | **Precisão descritiva de `T1-7` vs `T1-8`**: `T1-7` mantido estritamente como `"Ausência de placeholders não resolvidos (TODO, TBD, FIXME, <...>) no plano"` (idêntico à rubrica vigente) e validação de segregação `reviewer != author` alocada junto a `T1-8` (junto às invariantes dos novos campos v2 / telemetria do crítico). |

## Checklist de Conformidade R-064
- [x] Frontmatter R-064 v2 completo (`plan_type: requirements`) com correlação OTel e dogfooding real de `critic_rubric_gaps` e `critic_findings_summary` da Rodada 1.
- [x] `allowed_files` sincronizado com os 24 arquivos reais verificados fisicamente no repositório (zero globs).
- [x] Todo requisito singular, testável (EARS + Gherkin), com prioridade MoSCoW, incluindo mitigação explícita OWASP ASI06 + HITL (`REQ-010` / `RN-010`) e preservação de `T1-1` a `T1-7` + `T1-8` (incluindo segregação `reviewer != author` e invariantes dos novos campos v2 / telemetria do crítico) (`RN-005`).
- [x] Handoff de materialização e correção em lote executado via `@governance-maintainer` preservando `@requirements-analyst` e `@plan-critic` 100% Read-Only.
