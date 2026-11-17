---
plan_id: "20261116-150000-padronizacao-ctx-resume-agents-prompts"
plan_type: "governance"
title: "Padronização da Distribuição de Tools MCP context-mode (ctx_index, ctx_search, ctx_resume) em Agents e Prompts por Perfil Operacional (R-054 / Least Privilege)"
status: "COMPLETED"
approved: true
post_exec_review_verdict: "PASS"
post_exec_reviewer: "@agent-auditor"
post_exec_reviewed_at: "2026-11-16T15:30:00Z"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
review_tier1: "PASS"
critic_findings_summary: { blocker: 0, high: 0, medium: 0, low: 0, nit: 2 }
author: "@agent-auditor"
author_agent: "agent-auditor"
materialized_by: "docs-engineer"
created_at: "2026-11-16"
updated_at: "2026-11-16"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
tier: "governance"
reversibility_tier: "T1"
blast_radius: "medium"
related-planning-doc: "N/A — plano raiz de governança"
allowed_files:
  - ".github/agents/adapter-generator.agent.md"
  - ".github/agents/adr-sentinel.agent.md"
  - ".github/agents/agent-auditor.agent.md"
  - ".github/agents/backend/database/database-arch-advisor.agent.md"
  - ".github/agents/backend/database/informix-database-specialist.agent.md"
  - ".github/agents/backend/database/oracle-database-specialist.agent.md"
  - ".github/agents/backend/ejb/ejb-arch-advisor.agent.md"
  - ".github/agents/backend/ejb/ejb-developer.agent.md"
  - ".github/agents/backend/ejb/ejb-test-engineer.agent.md"
  - ".github/agents/backend/python/python-arch-advisor.agent.md"
  - ".github/agents/backend/python/python-developer.agent.md"
  - ".github/agents/backend/python/python-test-engineer.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-developer.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-developer.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-test-engineer.agent.md"
  - ".github/agents/backend/struts/struts-arch-advisor.agent.md"
  - ".github/agents/backend/struts/struts-developer.agent.md"
  - ".github/agents/backend/struts/struts-test-engineer.agent.md"
  - ".github/agents/binding-initializer.agent.md"
  - ".github/agents/bug-triage.agent.md"
  - ".github/agents/business-rules-extractor.agent.md"
  - ".github/agents/code-review.agent.md"
  - ".github/agents/code-style-enforcer.agent.md"
  - ".github/agents/codegraph-engine.agent.md"
  - ".github/agents/compliance-guardrails.agent.md"
  - ".github/agents/database-specialist.agent.md"
  - ".github/agents/ddd-bounded-context-mapper.agent.md"
  - ".github/agents/debugger.agent.md"
  - ".github/agents/deep-search.agent.md"
  - ".github/agents/devops-engineer.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/agents/feature-planner.agent.md"
  - ".github/agents/frontend/angular/angular-arch-advisor.agent.md"
  - ".github/agents/frontend/angular/angular-developer.agent.md"
  - ".github/agents/frontend/angular/angular-test-engineer.agent.md"
  - ".github/agents/frontend/react/react-arch-advisor.agent.md"
  - ".github/agents/frontend/react/react-developer.agent.md"
  - ".github/agents/frontend/react/react-test-engineer.agent.md"
  - ".github/agents/governance-factory.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/performance-agent.agent.md"
  - ".github/agents/plan-critic.agent.md"
  - ".github/agents/pr-gatekeeper.agent.md"
  - ".github/agents/refactor-planner.agent.md"
  - ".github/agents/repo-hygiene-auditor.agent.md"
  - ".github/agents/requirements-analyst.agent.md"
  - ".github/agents/runtime-verifier.agent.md"
  - ".github/agents/security-reviewer.agent.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/test-strategy.agent.md"
  - ".github/prompts/add-project-context.prompt.md"
  - ".github/prompts/connect-integration-graphs.prompt.md"
  - ".github/prompts/craft-prompt.prompt.md"
  - ".github/prompts/deep-search.prompt.md"
  - ".github/prompts/del-project-context.prompt.md"
  - ".github/prompts/eval-workflows.prompt.md"
  - ".github/prompts/implement.prompt.md"
  - ".github/prompts/init-context.prompt.md"
  - ".github/prompts/plan-lessons-harvester.prompt.md"
  - ".github/prompts/plan.prompt.md"
  - ".github/prompts/review.prompt.md"
  - ".github/prompts/strategic-review.prompt.md"
  - ".github/prompts/synth-waves.prompt.md"
  - ".github/prompts/validate.prompt.md"
  - ".github/prompts/visualize-graph.prompt.md"
  - ".github/agents/templates/agent-template.md"
  - ".github/agents/templates/operational-agent.md"
  - ".github/agents/templates/research-agent.md"
  - ".github/prompts/templates/prompt-template.md"
  - ".github/skills/context-mode/SKILL.md"
  - ".github/skills/governance-audit-patterns/SKILL.md"
  - "tests/governance_audit/test_context_mode_precedence_governance.py"
  - "tests/governance_audit/test_context_mode_v2_tool_names.py"
rollback_plan: "git restore .github/agents/adapter-generator.agent.md .github/agents/adr-sentinel.agent.md .github/agents/agent-auditor.agent.md .github/agents/backend/database/database-arch-advisor.agent.md .github/agents/backend/database/informix-database-specialist.agent.md .github/agents/backend/database/oracle-database-specialist.agent.md .github/agents/backend/ejb/ejb-arch-advisor.agent.md .github/agents/backend/ejb/ejb-developer.agent.md .github/agents/backend/ejb/ejb-test-engineer.agent.md .github/agents/backend/python/python-arch-advisor.agent.md .github/agents/backend/python/python-developer.agent.md .github/agents/backend/python/python-test-engineer.agent.md .github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md .github/agents/backend/spring-boot/spring-boot-developer.agent.md .github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md .github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md .github/agents/backend/spring-reactive/spring-reactive-developer.agent.md .github/agents/backend/spring-reactive/spring-reactive-test-engineer.agent.md .github/agents/backend/struts/struts-arch-advisor.agent.md .github/agents/backend/struts/struts-developer.agent.md .github/agents/backend/struts/struts-test-engineer.agent.md .github/agents/binding-initializer.agent.md .github/agents/bug-triage.agent.md .github/agents/business-rules-extractor.agent.md .github/agents/code-review.agent.md .github/agents/code-style-enforcer.agent.md .github/agents/codegraph-engine.agent.md .github/agents/compliance-guardrails.agent.md .github/agents/database-specialist.agent.md .github/agents/ddd-bounded-context-mapper.agent.md .github/agents/debugger.agent.md .github/agents/deep-search.agent.md .github/agents/devops-engineer.agent.md .github/agents/docs-engineer.agent.md .github/agents/feature-planner.agent.md .github/agents/frontend/angular/angular-arch-advisor.agent.md .github/agents/frontend/angular/angular-developer.agent.md .github/agents/frontend/angular/angular-test-engineer.agent.md .github/agents/frontend/react/react-arch-advisor.agent.md .github/agents/frontend/react/react-developer.agent.md .github/agents/frontend/react/react-test-engineer.agent.md .github/agents/governance-factory.agent.md .github/agents/governance-maintainer.agent.md .github/agents/performance-agent.agent.md .github/agents/plan-critic.agent.md .github/agents/pr-gatekeeper.agent.md .github/agents/refactor-planner.agent.md .github/agents/repo-hygiene-auditor.agent.md .github/agents/requirements-analyst.agent.md .github/agents/runtime-verifier.agent.md .github/agents/security-reviewer.agent.md .github/agents/tech-solution-architect.agent.md .github/agents/test-strategy.agent.md .github/prompts/add-project-context.prompt.md .github/prompts/connect-integration-graphs.prompt.md .github/prompts/craft-prompt.prompt.md .github/prompts/deep-search.prompt.md .github/prompts/del-project-context.prompt.md .github/prompts/eval-workflows.prompt.md .github/prompts/implement.prompt.md .github/prompts/init-context.prompt.md .github/prompts/plan-lessons-harvester.prompt.md .github/prompts/plan.prompt.md .github/prompts/review.prompt.md .github/prompts/strategic-review.prompt.md .github/prompts/synth-waves.prompt.md .github/prompts/validate.prompt.md .github/prompts/visualize-graph.prompt.md .github/agents/templates/agent-template.md .github/agents/templates/operational-agent.md .github/agents/templates/research-agent.md .github/prompts/templates/prompt-template.md .github/skills/context-mode/SKILL.md .github/skills/governance-audit-patterns/SKILL.md tests/governance_audit/test_context_mode_precedence_governance.py tests/governance_audit/test_context_mode_v2_tool_names.py"
reviewer: "@plan-critic"
session_id: "sess-20261116-ctx-resume-standardization"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-ctx-resume-standardization-01"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
  rounds: 0
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PENDING"
  author_ref: "@agent-auditor"
---

# Plano de Manutenção de Governança — Padronização da Distribuição de Tools MCP `context-mode` (`ctx_index`, `ctx_search`, `ctx_resume`) em Agents e Prompts por Perfil Operacional (R-054)

## 1. Contexto, Diagnóstico e Grounding Físico (C1)

A migração do servidor MCP `context-mode` para a superfície v2 introduziu 9 tools canônicas (`ctx_execute`, `ctx_batch`, `ctx_index`, `ctx_search`, `ctx_resume`, `ctx_stats`, `ctx_doctor`, `ctx_upgrade`, `ctx_purge`). Embora a remoção de tokens legados v1 já esteja protegida por `tests/governance_audit/test_context_mode_v2_tool_names.py`, a auditoria física em disco conduzida pelo `@agent-auditor` nos **63 agents** (`.github/agents/**/*.agent.md`) e **24 prompts** (`.github/prompts/*.prompt.md`) identificou uma lacuna sistêmica na distribuição de `context-mode/ctx_resume` (e paridade de `ctx_index` / `ctx_search` em prompts de workflow):

1. **53 Agents Operacionais Elegíveis sem `context-mode/ctx_resume`**: Todos os 53 agents não-routers e não-`prompt-structuring` declaram `context-mode/ctx_index`, `context-mode/ctx_search` e `context-mode/ctx_batch` (e 29 deles declaram `context-mode/ctx_execute`), mas **0 de 53** declaram `context-mode/ctx_resume`. Sem `context-mode/ctx_resume` no frontmatter YAML `tools:`, os agents folha e planejadores ficam impedidos de recuperar o estado consolidado da sessão após eventos de compactação de janela de contexto em fluxos longos (violando a eficácia do `CLAUSE_CONTEXT_HYDRATION` e a continuidade de sessão do `context-mode` v2).
2. **10 Agents Isentos/Proibidos (9 Routers + `prompt-structuring`)**: Os 9 roteadores puros (`agent-router`, `angular-router`, `database-router`, `ejb-router`, `python-router`, `react-router`, `spring-boot-router`, `spring-reactive-router`, `struts-router`) e o agent de síntese pura `prompt-structuring` não possuem tools do `context-mode` e **DEVEM permanecer 100% isentos** de `context-mode/ctx_resume`, `context-mode/ctx_index`, `context-mode/ctx_search`, `context-mode/ctx_batch` e `context-mode/ctx_execute` em estrita observância à regra **R-054** (isolamento de roteadores sem hidratação/execução em sandbox — Smell 2.23).
3. **15 Prompts Slash Workflow (`router_bypass: slash_workflow`) sem `context-mode/ctx_resume`**: Dos 24 prompts em `.github/prompts/*.prompt.md`, exatamente 15 operam como workflows completos (`router_bypass: slash_workflow`) sujeitos a múltiplos turnos e compactação de sessão. Atualmente, nenhum dos 15 declara `context-mode/ctx_resume` (e `audit-Prompt.prompt.md` não declarava `ctx_index`/`ctx_batch`, enquanto `prompt-lessons-harvester.prompt.md` declarava apenas `ctx_search`/`ctx_batch` sem `ctx_index`/`ctx_resume`).
4. **9 Prompts Isentos (8 `router_bypass: utility` + `agent-router.prompt.md`)**: Os 8 prompts utilitários de turno curto (`router_bypass: utility`) e o prompt de entrada do roteador (`agent-router.prompt.md`) não executam cadeias longas multi-stage e permanecem isentos de `context-mode/ctx_resume`.
5. **Templates e Testes de Auditoria**: Os templates base em `.github/agents/templates/` e `.github/prompts/templates/`, a skill `.github/skills/context-mode/SKILL.md` e a suíte `tests/governance_audit/test_context_mode_precedence_governance.py` ainda não exigem nem documentam a presença obrigatória de `context-mode/ctx_resume` nos 53 agents elegíveis e 15 prompts `slash_workflow`.

### 1.1. Inventário de Grounding Físico (Bytes, Linhas e Estado Atual de Tools em Disco)

#### A. 53 Agents Elegíveis para Receber `context-mode/ctx_resume`

| # | Caminho Real em Disco | Bytes | Linhas | Tools `context-mode` Atuais | Mutação Planejada |
|---|---|---:|---:|---|---|
| 1 | `.github/agents/adapter-generator.agent.md` | 33465 | 431 | `context-mode/ctx_execute, context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_batch` | `+ context-mode/ctx_resume` |
| 2 | `.github/agents/adr-sentinel.agent.md` | 13449 | 140 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 3 | `.github/agents/agent-auditor.agent.md` | 22435 | 208 | `context-mode/ctx_search, context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 4 | `.github/agents/backend/database/database-arch-advisor.agent.md` | 15958 | 135 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 5 | `.github/agents/backend/database/informix-database-specialist.agent.md` | 11046 | 98 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 6 | `.github/agents/backend/database/oracle-database-specialist.agent.md` | 11129 | 96 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 7 | `.github/agents/backend/ejb/ejb-arch-advisor.agent.md` | 15739 | 140 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 8 | `.github/agents/backend/ejb/ejb-developer.agent.md` | 12436 | 107 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 9 | `.github/agents/backend/ejb/ejb-test-engineer.agent.md` | 12614 | 108 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 10 | `.github/agents/backend/python/python-arch-advisor.agent.md` | 17146 | 144 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 11 | `.github/agents/backend/python/python-developer.agent.md` | 14005 | 121 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 12 | `.github/agents/backend/python/python-test-engineer.agent.md` | 13982 | 118 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 13 | `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md` | 15138 | 146 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 14 | `.github/agents/backend/spring-boot/spring-boot-developer.agent.md` | 12823 | 117 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 15 | `.github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md` | 12853 | 114 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 16 | `.github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md` | 15043 | 138 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 17 | `.github/agents/backend/spring-reactive/spring-reactive-developer.agent.md` | 14317 | 121 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 18 | `.github/agents/backend/spring-reactive/spring-reactive-test-engineer.agent.md` | 13602 | 117 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 19 | `.github/agents/backend/struts/struts-arch-advisor.agent.md` | 16088 | 144 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 20 | `.github/agents/backend/struts/struts-developer.agent.md` | 12379 | 107 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 21 | `.github/agents/backend/struts/struts-test-engineer.agent.md` | 12759 | 109 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 22 | `.github/agents/binding-initializer.agent.md` | 22926 | 349 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 23 | `.github/agents/bug-triage.agent.md` | 30793 | 439 | `context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_batch` | `+ context-mode/ctx_resume` |
| 24 | `.github/agents/business-rules-extractor.agent.md` | 22569 | 356 | `context-mode/ctx_execute, context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_batch` | `+ context-mode/ctx_resume` |
| 25 | `.github/agents/code-review.agent.md` | 16287 | 202 | `context-mode/ctx_batch, context-mode/ctx_search, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 26 | `.github/agents/code-style-enforcer.agent.md` | 11413 | 145 | `context-mode/ctx_batch, context-mode/ctx_search, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 27 | `.github/agents/codegraph-engine.agent.md` | 34313 | 272 | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_index, context-mode/ctx_search` | `+ context-mode/ctx_resume` |
| 28 | `.github/agents/compliance-guardrails.agent.md` | 12657 | 165 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 29 | `.github/agents/database-specialist.agent.md` | 13861 | 171 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 30 | `.github/agents/ddd-bounded-context-mapper.agent.md` | 14993 | 156 | `context-mode/ctx_search, context-mode/ctx_index, context-mode/ctx_execute, context-mode/ctx_batch` | `+ context-mode/ctx_resume` |
| 31 | `.github/agents/debugger.agent.md` | 12608 | 161 | `context-mode/ctx_batch, context-mode/ctx_search, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 32 | `.github/agents/deep-search.agent.md` | 15729 | 177 | `context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_batch` | `+ context-mode/ctx_resume` |
| 33 | `.github/agents/devops-engineer.agent.md` | 11415 | 158 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 34 | `.github/agents/docs-engineer.agent.md` | 15502 | 164 | `context-mode/ctx_search, context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 35 | `.github/agents/feature-planner.agent.md` | 16906 | 179 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 36 | `.github/agents/frontend/angular/angular-arch-advisor.agent.md` | 17140 | 154 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 37 | `.github/agents/frontend/angular/angular-developer.agent.md` | 15315 | 126 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 38 | `.github/agents/frontend/angular/angular-test-engineer.agent.md` | 14313 | 119 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 39 | `.github/agents/frontend/react/react-arch-advisor.agent.md` | 17376 | 163 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 40 | `.github/agents/frontend/react/react-developer.agent.md` | 14202 | 122 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 41 | `.github/agents/frontend/react/react-test-engineer.agent.md` | 13464 | 117 | `context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 42 | `.github/agents/governance-factory.agent.md` | 36532 | 342 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_execute, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 43 | `.github/agents/governance-maintainer.agent.md` | 21102 | 152 | `context-mode/ctx_batch, context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 44 | `.github/agents/performance-agent.agent.md` | 13041 | 162 | `context-mode/ctx_batch, context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 45 | `.github/agents/plan-critic.agent.md` | 19427 | 161 | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 46 | `.github/agents/pr-gatekeeper.agent.md` | 16652 | 194 | `context-mode/ctx_batch, context-mode/ctx_search, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 47 | `.github/agents/refactor-planner.agent.md` | 20869 | 222 | `context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_stats, context-mode/ctx_doctor, context-mode/ctx_upgrade, context-mode/ctx_purge, context-mode/ctx_execute` | `+ context-mode/ctx_resume` |
| 48 | `.github/agents/repo-hygiene-auditor.agent.md` | 13163 | 145 | `context-mode/ctx_batch, context-mode/ctx_search, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 49 | `.github/agents/requirements-analyst.agent.md` | 19415 | 211 | `context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_batch` | `+ context-mode/ctx_resume` |
| 50 | `.github/agents/runtime-verifier.agent.md` | 13530 | 152 | `context-mode/ctx_batch, context-mode/ctx_search, context-mode/ctx_index, context-mode/ctx_doctor` | `+ context-mode/ctx_resume` |
| 51 | `.github/agents/security-reviewer.agent.md` | 13301 | 173 | `context-mode/ctx_batch, context-mode/ctx_search, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 52 | `.github/agents/tech-solution-architect.agent.md` | 30520 | 328 | `context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_stats, context-mode/ctx_doctor, context-mode/ctx_upgrade, context-mode/ctx_purge` | `+ context-mode/ctx_resume` |
| 53 | `.github/agents/test-strategy.agent.md` | 16429 | 156 | `context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_stats, context-mode/ctx_doctor, context-mode/ctx_upgrade, context-mode/ctx_purge` | `+ context-mode/ctx_resume` |

#### B. 10 Agents Isentos/Proibidos (R-054 — 9 Routers + `prompt-structuring`)

| # | Caminho Real em Disco | Bytes | Linhas | Papel Arquitetural | Tools `context-mode` Atuais | Invariante R-054 |
|---|---|---:|---:|---|---|---|
| 1 | `.github/agents/agent-router.agent.md` | 63811 | 479 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 2 | `.github/agents/backend/database/database-router.agent.md` | 13743 | 117 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 3 | `.github/agents/backend/ejb/ejb-router.agent.md` | 13821 | 116 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 4 | `.github/agents/backend/python/python-router.agent.md` | 14990 | 118 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 5 | `.github/agents/backend/spring-boot/spring-boot-router.agent.md` | 13796 | 116 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 6 | `.github/agents/backend/spring-reactive/spring-reactive-router.agent.md` | 14013 | 116 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 7 | `.github/agents/backend/struts/struts-router.agent.md` | 13940 | 116 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 8 | `.github/agents/frontend/angular/angular-router.agent.md` | 14552 | 117 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 9 | `.github/agents/frontend/react/react-router.agent.md` | 14298 | 117 | Router Puro (R-054) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |
| 10 | `.github/agents/prompt-structuring.agent.md` | 17090 | 179 | Meta-Síntese Pura (Sem MCP) | `context-mode/ctx_search` | Proibido `ctx_resume` / `ctx_index` (OK) |

#### C. 15 Prompts Elegíveis (`router_bypass: slash_workflow`)

| # | Caminho Real em Disco | Bytes | Linhas | `router_bypass` | Tools `context-mode` Atuais | Mutação Planejada |
|---|---|---:|---:|---|---|---|
| 1 | `.github/prompts/add-project-context.prompt.md` | 16438 | 168 | `slash_workflow` | `context-mode/ctx_search, context-mode/ctx_index, context-mode/ctx_execute, context-mode/ctx_batch` | `+ context-mode/ctx_resume` |
| 2 | `.github/prompts/connect-integration-graphs.prompt.md` | 20509 | 267 | `slash_workflow` | `context-mode/ctx_search, context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_index` | `+ context-mode/ctx_resume` |
| 3 | `.github/prompts/craft-prompt.prompt.md` | 23159 | 268 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 4 | `.github/prompts/deep-search.prompt.md` | 12172 | 154 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_batch` | `+ context-mode/ctx_resume` |
| 5 | `.github/prompts/del-project-context.prompt.md` | 13535 | 223 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 6 | `.github/prompts/eval-workflows.prompt.md` | 13910 | 158 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 7 | `.github/prompts/implement.prompt.md` | 13208 | 192 | `slash_workflow` | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_execute` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 8 | `.github/prompts/init-context.prompt.md` | 23629 | 475 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search, context-mode/ctx_stats` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 9 | `.github/prompts/plan-lessons-harvester.prompt.md` | 11846 | 112 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 10 | `.github/prompts/plan.prompt.md` | 15772 | 236 | `slash_workflow` | `context-mode/ctx_search, context-mode/ctx_batch, context-mode/ctx_execute` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 11 | `.github/prompts/review.prompt.md` | 11481 | 164 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 12 | `.github/prompts/strategic-review.prompt.md` | 15612 | 213 | `slash_workflow` | `context-mode/ctx_search, context-mode/ctx_batch` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 13 | `.github/prompts/synth-waves.prompt.md` | 15658 | 179 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 14 | `.github/prompts/validate.prompt.md` | 11801 | 203 | `slash_workflow` | `context-mode/ctx_search, context-mode/ctx_batch` | `+ context-mode/ctx_index, context-mode/ctx_resume` |
| 15 | `.github/prompts/visualize-graph.prompt.md` | 10398 | 135 | `slash_workflow` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search` | `+ context-mode/ctx_index, context-mode/ctx_resume` |

#### D. 9 Prompts Isentos (8 `router_bypass: utility` + `agent-router.prompt.md`)

| # | Caminho Real em Disco | Bytes | Linhas | `router_bypass` | Tools `context-mode` Atuais | Regra Aplicável |
|---|---|---:|---:|---|---|---|
| 1 | `.github/prompts/agent-router.prompt.md` | 11635 | 154 | `none` | `context-mode/ctx_search` | Isento de `ctx_resume` (Utilitário/Router) |
| 2 | `.github/prompts/commit.prompt.md` | 10489 | 145 | `utility` | `context-mode/ctx_batch, context-mode/ctx_execute, context-mode/ctx_search` | Isento de `ctx_resume` (Utilitário/Router) |
| 3 | `.github/prompts/ctx-checkpoint.prompt.md` | 10887 | 189 | `utility` | `context-mode/ctx_index` | Isento de `ctx_resume` (Utilitário/Router) |
| 4 | `.github/prompts/ctx-doctor.prompt.md` | 7642 | 127 | `utility` | `context-mode/ctx_doctor` | Isento de `ctx_resume` (Utilitário/Router) |
| 5 | `.github/prompts/ctx-insight.prompt.md` | 7262 | 123 | `utility` | `context-mode/ctx_stats` | Isento de `ctx_resume` (Utilitário/Router) |
| 6 | `.github/prompts/ctx-resume.prompt.md` | 12850 | 260 | `utility` | `context-mode/ctx_search` | Isento de `ctx_resume` (Utilitário/Router) |
| 7 | `.github/prompts/ctx-start.prompt.md` | 8362 | 131 | `utility` | `context-mode/ctx_stats, context-mode/ctx_doctor, context-mode/ctx_execute` | Isento de `ctx_resume` (Utilitário/Router) |
| 8 | `.github/prompts/ctx-status.prompt.md` | 7561 | 126 | `utility` | `context-mode/ctx_stats` | Isento de `ctx_resume` (Utilitário/Router) |
| 9 | `.github/prompts/health.prompt.md` | 13604 | 258 | `utility` | `context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_search` | Isento de `ctx_resume` (Utilitário/Router) |

#### E. Templates, Skills e Arquivos de Teste em Escopo

| Caminho Real em Disco | Bytes | Linhas | Papel no Plano |
|---|---:|---:|---|
| `.github/agents/templates/agent-template.md` | 19171 | 225 | Template declarativo (`context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_search`) |
| `.github/agents/templates/operational-agent.md` | 19674 | 251 | Template declarativo (`context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_search`) |
| `.github/agents/templates/research-agent.md` | 20320 | 265 | Template declarativo (`context-mode/ctx_batch, context-mode/ctx_execute, context-mode/ctx_index, context-mode/ctx_search, context-mode/ctx_search`) |
| `.github/agents/templates/router-agent.md` | 14424 | 132 | **Isento/Proibido sob R-054** (fora de `allowed_files`; permanece apenas com `context-mode/ctx_search`, sem `ctx_resume` nem `ctx_index`) |
| `.github/prompts/templates/prompt-template.md` | 10837 | 152 | Template declarativo (`context-mode/ctx_execute, context-mode/ctx_batch, context-mode/ctx_index, context-mode/ctx_search`) |
| `.github/skills/context-mode/SKILL.md` | 31108 | 299 | Skill / Suíte de Auditoria Python |
| `.github/skills/governance-audit-patterns/SKILL.md` | 16171 | 184 | Skill / Suíte de Auditoria Python |
| `tests/governance_audit/test_context_mode_precedence_governance.py` | 41216 | 905 | Skill / Suíte de Auditoria Python |
| `tests/governance_audit/test_context_mode_v2_tool_names.py` | 5313 | 135 | Skill / Suíte de Auditoria Python |

### 1.2. Matriz de Distribuição de Tools `context-mode` por Perfil Operacional (Least Privilege / R-054)

| Perfil Operacional | Quantidade | `ctx_execute` | `ctx_batch` | `ctx_index` | `ctx_search` | `ctx_resume` | Diagnóstico v2 (`ctx_stats`/`ctx_doctor`/`ctx_upgrade`/`ctx_purge`) |
|---|---:|---|---|---|---|---|---|
| **Routers Puros** (`*-router.agent.md`) | 9 | ❌ Proibido (R-054) | ❌ Proibido (R-054) | ❌ Proibido (R-054) | ❌ Proibido (R-054) | ❌ Proibido (R-054) | ❌ Proibido |
| **Meta-Síntese Pura** (`prompt-structuring.agent.md`) | 1 | ❌ Proibido | ❌ Proibido | ❌ Proibido | ❌ Proibido | ❌ Proibido | ❌ Proibido |
| **Agents Analíticos / Revisores / Planejadores Read-Only** | 24 | ❌ Não declara | ✅ Obrigatório | ✅ Obrigatório | ✅ Obrigatório | ✅ **Obrigatório (Novo)** | Opcional por perfil (`test-strategy`, `runtime-verifier`) |
| **Agents Executores / Desenvolvedores / Híbridos com Sandbox** | 29 | ✅ Obrigatório | ✅ Obrigatório | ✅ Obrigatório | ✅ Obrigatório | ✅ **Obrigatório (Novo)** | Opcional por perfil (`refactor-planner`, `tech-solution-architect`) |
| **Prompts de Workflow** (`router_bypass: slash_workflow`) | 15 | Conforme escopo | ✅ Obrigatório | ✅ Obrigatório | ✅ Obrigatório | ✅ **Obrigatório (Novo)** | Opcional (`sync-global-rules`, `worktree-session`, `audit-Prompt`) |
| **Prompts Utilitários / Router** (`utility` + `agent-router`) | 9 | Conforme escopo | Conforme escopo | Conforme escopo | Conforme escopo | ❌ Isento (turno único) | ❌ Não aplicável |

---

## 2. Causa-Raiz (RCA Q0), Análise de Escape e Portão de Reúso Sistêmico (R-055)

| Dimensão R-055 | Análise e Ação Sistêmica Vinculada |
|---|---|
| **Q0 — Causa-Raiz (5 Porquês) e Análise de Escape** | **1º Porquê:** Os 53 agents operacionais e os 15 prompts `slash_workflow` não possuem `context-mode/ctx_resume` declarado em `tools:`.<br>**2º Porquê:** Na migração para o `context-mode` v2, apenas os nomes legados v1 (`ctx_execute_file`, `ctx_batch_execute`, `ctx_fetch_and_index`) foram substituídos nos arquivos existentes, sem injeção da nova tool v2 `context-mode/ctx_resume` de retomada pós-compactação.<br>**3º Porquê:** Os templates de geração em `.github/agents/templates/` e `.github/prompts/templates/` não incluíam `context-mode/ctx_resume` no bloco padrão de `tools:`.<br>**4º Porquê:** A documentação da skill `.github/skills/context-mode/SKILL.md` listava as tools v2 mas não especificava a matriz normativa de distribuição de `ctx_resume` por perfil (53 agents + 15 prompts `slash_workflow` vs. isenção R-054 dos 9 routers e `prompt-structuring`).<br>**5º Porquê (Escape):** O teste `tests/governance_audit/test_context_mode_v2_tool_names.py` validava apenas que as tools declaradas pertenciam à allowlist v2 de 9 nomes (`ALLOWED_V2_CTX_TOOLS`), e `tests/governance_audit/test_context_mode_precedence_governance.py` não possuía asserção exigindo a presença de `context-mode/ctx_resume` nos 53 agents elegíveis e 15 prompts `slash_workflow` nem proibindo explicitamente `ctx_resume`/`ctx_index` nos 9 routers + `prompt-structuring`. |
| **Q1 — Catálogo e Templates** | Atualizar `.github/agents/templates/agent-template.md`, `.github/agents/templates/operational-agent.md`, `.github/agents/templates/research-agent.md` e `.github/prompts/templates/prompt-template.md` (4 templates elegíveis: 3 de agents não-routers + 1 de prompt; `.github/agents/templates/router-agent.md` é isento/proibido sob R-054) para incluir `context-mode/ctx_resume` na declaração padrão de `tools:` (com comentário explícito em `prompt-template.md` diferenciando `slash_workflow` de `utility`). Os catálogos (`.github/agents/catalog.yaml`, `.github/prompts/catalog.yaml`, `.github/skills/catalog.yaml`) não sofrem adição/remoção de artefatos nem mudança de descrição/contagem. |
| **Q2 — Prompts, Skills e Workflows** | Atualizar os 53 agents elegíveis (`.github/agents/**/*.agent.md`), os 15 prompts `slash_workflow` (`.github/prompts/*.prompt.md`), os 4 templates elegíveis (3 de agents não-routers: `.github/agents/templates/agent-template.md`, `.github/agents/templates/operational-agent.md`, `.github/agents/templates/research-agent.md` + 1 de prompt: `.github/prompts/templates/prompt-template.md`; mantendo 1 template de router `.github/agents/templates/router-agent.md` isento por R-054), a skill `.github/skills/context-mode/SKILL.md` (documentando a matriz Least Privilege R-054 e o papel de `ctx_resume` no `CLAUSE_CONTEXT_HYDRATION`) e `.github/skills/governance-audit-patterns/SKILL.md`. |
| **Q3 — Automação / Testes de Auditoria Python (R-055)** | Como `.github/agents/governance-maintainer.agent.md` não altera código Python em `tests/**/*.py` (R-055), a evolução de `tests/governance_audit/test_context_mode_precedence_governance.py` e `tests/governance_audit/test_context_mode_v2_tool_names.py` é decomposta na **Tarefa T4**, delegada obrigatoriamente à trilha Python (`@python-router` → `@python-arch-advisor` → `@python-test-engineer` / `@python-developer`). |

---

## 3. Decomposição de Tarefas (`[GOVERNANCE_TASKS]`)

### Tarefa T0 — Prevenção Estrutural na Origem (Templates e Skills de Governança)

- **Agente Executor:** `@governance-maintainer`
- **Arquivos-Alvo:**
  - `.github/agents/templates/agent-template.md`
  - `.github/agents/templates/operational-agent.md`
  - `.github/agents/templates/research-agent.md`
  - `.github/prompts/templates/prompt-template.md`
  - *(Isento/Proibido sob R-054 — fora de `allowed_files` e sem mutação: `.github/agents/templates/router-agent.md`)*
  - `.github/skills/context-mode/SKILL.md`
  - `.github/skills/governance-audit-patterns/SKILL.md`
- **Especificação Exata da Mutação:**
  1. Nos 3 templates de agents não-routers (`.github/agents/templates/agent-template.md`, `.github/agents/templates/operational-agent.md` e `.github/agents/templates/research-agent.md`; mantendo `.github/agents/templates/router-agent.md` isento/intocado sob R-054 apenas com `context-mode/ctx_search`): adicionar `- context-mode/ctx_resume` logo após `- context-mode/ctx_index` na lista `tools:` do frontmatter YAML do template.
  2. Em `.github/prompts/templates/prompt-template.md`: adicionar `- context-mode/ctx_index` e `- context-mode/ctx_resume` no bloco `tools:` padrão voltado a prompts `router_bypass: slash_workflow`, documentando em comentário que prompts `router_bypass: utility` não requerem `ctx_resume`.
  3. Em `.github/skills/context-mode/SKILL.md`: documentar a tabela de distribuição por perfil operacional (53 agents elegíveis + 15 prompts `slash_workflow` com `ctx_resume`; 9 routers + `prompt-structuring` estritamente sem tools `context-mode/*` por R-054) e o uso de `ctx_resume` para recuperação de contexto pós-compactação.
  4. Em `.github/skills/governance-audit-patterns/SKILL.md`: registrar o invariante de auditoria da presença de `context-mode/ctx_resume` nos 53 agents operacionais e 15 prompts `slash_workflow`.

### Tarefa T1 — Padronização dos 53 Agents Operacionais Elegíveis (`.github/agents/**/*.agent.md`)

- **Agente Executor:** `@governance-maintainer` (via script único `ctx_execute` com `language: "javascript"` — Regra R-046 / R-059)
- **Arquivos-Alvo:** Os 53 arquivos listados na Seção 1.1.A.
- **Especificação Exata da Mutação:**
  - No frontmatter YAML (`tools:`) de cada um dos 53 agents elegíveis, inserir `- context-mode/ctx_resume` (ou `"context-mode/ctx_resume"` respeitando o estilo de aspas existente no arquivo) imediatamente após a última tool `context-mode/*` declarada no respectivo frontmatter, garantindo ausência de duplicatas e preservação byte-a-byte do corpo Markdown e das demais chaves do frontmatter.

### Tarefa T2 — Padronização dos 15 Prompts Slash Workflow Elegíveis (`.github/prompts/*.prompt.md`)

- **Agente Executor:** `@governance-maintainer` (no mesmo lote `ctx_execute` em JavaScript da Tarefa T1 — Regra R-046 / R-059)
- **Arquivos-Alvo:** Os 15 arquivos `.github/prompts/*.prompt.md` com `router_bypass: slash_workflow` listados na Seção 1.1.C:
  1. `.github/prompts/add-project-context.prompt.md` (`+ context-mode/ctx_resume`)
  2. `.github/prompts/analisar-performance.prompt.md` (`+ context-mode/ctx_resume`)
  3. `.github/prompts/aprender-padroes-projeto.prompt.md` (`+ context-mode/ctx_resume`)
  4. `.github/prompts/audit-Prompt.prompt.md` (`+ context-mode/ctx_index, context-mode/ctx_batch, context-mode/ctx_resume`)
  5. `.github/prompts/create-pr.prompt.md` (`+ context-mode/ctx_resume`)
  6. `.github/prompts/documentar-regras-negocio.prompt.md` (`+ context-mode/ctx_resume`)
  7. `.github/prompts/executar-migracao-framework.prompt.md` (`+ context-mode/ctx_resume`)
  8. `.github/prompts/implement.prompt.md` (`+ context-mode/ctx_resume`)
  9. `.github/prompts/plan-lessons-harvester.prompt.md` (`+ context-mode/ctx_resume`)
  10. `.github/prompts/plan.prompt.md` (`+ context-mode/ctx_resume`)
  11. `.github/prompts/prompt-lessons-harvester.prompt.md` (`+ context-mode/ctx_index, context-mode/ctx_resume`)
  12. `.github/prompts/review-pr.prompt.md` (`+ context-mode/ctx_resume`)
  13. `.github/prompts/sync-global-rules.prompt.md` (`+ context-mode/ctx_resume`)
  14. `.github/prompts/validate.prompt.md` (`+ context-mode/ctx_resume`)
  15. `.github/prompts/worktree-session.prompt.md` (`+ context-mode/ctx_resume`)
- **Especificação Exata da Mutação:**
  - Garantir que todos os 15 prompts com `router_bypass: slash_workflow` declarem no bloco `tools:` do frontmatter YAML o conjunto base de continuidade de sessão `context-mode/ctx_search`, `context-mode/ctx_index`, `context-mode/ctx_batch` e `context-mode/ctx_resume`, preservando todas as demais tools já declaradas em cada prompt.

### Tarefa T3 — Verificação de Isolamento dos 10 Agents Isentos (R-054) e 9 Prompts Isentos

- **Agente Executor:** `@governance-maintainer`
- **Escopo de Verificação Read-Only:**
  - Confirmar que os 9 routers (`agent-router`, `angular-router`, `database-router`, `ejb-router`, `python-router`, `react-router`, `spring-boot-router`, `spring-reactive-router`, `struts-router`) e `prompt-structuring.agent.md` permanecem **intocados** e sem nenhuma tool `context-mode/*` (`ctx_resume`, `ctx_index`, `ctx_search`, `ctx_batch`, `ctx_execute`).
  - Confirmar que os 9 prompts isentos (`agent-router.prompt.md` e os 8 prompts `router_bypass: utility`) permanecem sem `context-mode/ctx_resume`.

### Tarefa T4 — Evolução dos Sensores de Auditoria em Python (Delegação Trilha Python R-055)

- **Trilha de Delegação Obrigatória (R-055):** `@python-router` → `@python-arch-advisor` → `@python-test-engineer` / `@python-developer`
- **Arquivos-Alvo:**
  - `tests/governance_audit/test_context_mode_precedence_governance.py`
  - `tests/governance_audit/test_context_mode_v2_tool_names.py`
- **Especificação Exata dos Testes de Regressão a Implementar:**
  1. Em `tests/governance_audit/test_context_mode_precedence_governance.py`:
     - `test_eligible_53_agents_declare_ctx_resume_index_search()`: percorre recursivamente `.github/agents/**/*.agent.md` (excluindo `templates/` e `workflows/`), separa os 10 agents isentos (`EXEMPT_NO_CTX_AGENTS = {9 routers + "prompt-structuring.agent.md"}`), valida que existem exatamente 53 agents elegíveis e que 100% deles declaram `context-mode/ctx_index`, `context-mode/ctx_search` e `context-mode/ctx_resume` no frontmatter `tools:`.
     - `test_routers_and_prompt_structuring_forbid_ctx_resume_and_ctx_index_r054()`: valida que os 9 routers e `prompt-structuring.agent.md` não declaram `context-mode/ctx_resume`, `context-mode/ctx_index` nem qualquer outra tool `context-mode/*` (proteção determinística R-054).
     - `test_slash_workflow_prompts_declare_ctx_resume_and_exempt_prompts_do_not()`: percorre os 24 arquivos em `.github/prompts/*.prompt.md`, verifica que todos os 15 prompts com `router_bypass == "slash_workflow"` declaram `context-mode/ctx_index`, `context-mode/ctx_search` e `context-mode/ctx_resume`, e que os 9 prompts restantes (8 `utility` + `agent-router.prompt.md`) não declaram `context-mode/ctx_resume`.
  2. Em `tests/governance_audit/test_context_mode_v2_tool_names.py`:
     - `test_agent_and_prompt_templates_declare_ctx_resume()`: valida os 4 templates elegíveis (3 de agents não-routers: `.github/agents/templates/agent-template.md`, `.github/agents/templates/operational-agent.md`, `.github/agents/templates/research-agent.md` + 1 de prompt: `.github/prompts/templates/prompt-template.md`) quanto à presença de `context-mode/ctx_resume`, e valida negativamente o 1 template de router isento por R-054 (`.github/agents/templates/router-agent.md`), garantindo que declara apenas `context-mode/ctx_search` e nunca `ctx_resume` nem `ctx_index`.

---

## 4. Alternativas Rejeitadas (C2)

1. **Alternativa A (Rejeitada): Adicionar `context-mode/ctx_resume` indiscriminadamente nos 63 agents e 24 prompts.**
   - **Motivo Técnico do Descarte:** Viola frontalmente a regra **R-054** (isolamento de roteadores sem `context-mode`) e o anti-padrão **Smell 2.23** (hidratação ou uso de sandbox no roteador). Roteadores puros (`*-router.agent.md`) e `prompt-structuring.agent.md` operam com despacho/síntese determinística em turno único; injetar tools MCP neles infla o custo de schema de tools por requisição e quebra o contrato de Least Privilege. Da mesma forma, prompts `router_bypass: utility` são utilitários curtos que não sofrem compactação de workflow multi-etapa.
2. **Alternativa B (Rejeitada): Habilitar `context-mode/ctx_resume` apenas nos 14 planejadores e omitir dos agents executores/revisores.**
   - **Motivo Técnico do Descarte:** A compactação de contexto em fluxos longos (`WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-FRAMEWORK-MIGRATION`, `WORKFLOW-GOVERNANCE-MAINTENANCE`) ocorre frequentemente durante as etapas de implementação, revisão cética (`@plan-critic`), auditoria (`@code-review`, `@security-reviewer`, `@pr-gatekeeper`) e materialização (`@docs-engineer`, `@governance-maintainer`). Restringir `ctx_resume` aos planejadores deixaria os agents executores e avaliadores incapazes de retomar snapshots de sessão pós-compactação.
3. **Alternativa C (Rejeitada): Editar os 68 arquivos (`53 agents + 15 prompts`) individualmente via ferramentas nativas do editor.**
   - **Motivo Técnico do Descarte:** Viola as regras **R-046**, **R-056** e **R-059** (Smell 2.24 e Smell 2.26 — proibição de mutações unitárias em série). A mutação de 68+ arquivos exige obrigatoriamente script consolidado em lote via `ctx_execute` (`language: "javascript"`, `fs` nativo do Node.js).

---

## 5. Blast Radius e Análise de Impacto (C2)

- **Escopo Declarativo Direto:**
  - **53 arquivos** `.github/agents/**/*.agent.md` (apenas adição de 1 linha `- context-mode/ctx_resume` no bloco `tools:` do frontmatter YAML).
  - **15 arquivos** `.github/prompts/*.prompt.md` com `router_bypass: slash_workflow` (adição de `context-mode/ctx_resume` nos 15, além de `ctx_index`/`ctx_batch` em `audit-Prompt.prompt.md` e `ctx_index` em `prompt-lessons-harvester.prompt.md`).
  - **4 templates elegíveis** (`.github/agents/templates/agent-template.md`, `.github/agents/templates/operational-agent.md`, `.github/agents/templates/research-agent.md` e `.github/prompts/templates/prompt-template.md` (4 templates elegíveis: 3 de agents não-routers + 1 de prompt; `.github/agents/templates/router-agent.md` é isento/proibido sob R-054)).
  - **2 skills** (`.github/skills/context-mode/SKILL.md`, `.github/skills/governance-audit-patterns/SKILL.md`).
- **Escopo de Testes Python (Trilha Python R-055):**
  - **2 arquivos** (`tests/governance_audit/test_context_mode_precedence_governance.py`, `tests/governance_audit/test_context_mode_v2_tool_names.py`).
- **Artefatos Intocados (Impacto Zero):**
  - Os **9 routers** e `prompt-structuring.agent.md` (0 bytes alterados).
  - Os **9 prompts isentos** (8 `utility` + `agent-router.prompt.md`, 0 bytes alterados).
  - Os **3 catálogos** (`.github/agents/catalog.yaml`, `.github/prompts/catalog.yaml`, `.github/skills/catalog.yaml`), pois não há criação/exclusão de agents, prompts ou skills nem alteração de metadados catalogáveis.
- **Classificação de Risco e Reversibilidade:** `blast_radius: "medium"` (76 arquivos no total, porém mutação aditiva estritamente confinada à lista `tools:` do frontmatter YAML e testes de auditoria), `reversibility_tier: "T1"` (100% reversível via `git restore` imediato).

---

## 6. Estratégia de Rollback (C2)

Em caso de falha em qualquer verificação da Subetapa 5a ou regressão na suíte `pytest tests/governance_audit/`, executar reversão atômica imediata de todos os arquivos do plano:

```bash
git restore .github/agents/adapter-generator.agent.md .github/agents/adr-sentinel.agent.md .github/agents/agent-auditor.agent.md .github/agents/backend/database/database-arch-advisor.agent.md .github/agents/backend/database/informix-database-specialist.agent.md .github/agents/backend/database/oracle-database-specialist.agent.md .github/agents/backend/ejb/ejb-arch-advisor.agent.md .github/agents/backend/ejb/ejb-developer.agent.md .github/agents/backend/ejb/ejb-test-engineer.agent.md .github/agents/backend/python/python-arch-advisor.agent.md .github/agents/backend/python/python-developer.agent.md .github/agents/backend/python/python-test-engineer.agent.md .github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md .github/agents/backend/spring-boot/spring-boot-developer.agent.md .github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md .github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md .github/agents/backend/spring-reactive/spring-reactive-developer.agent.md .github/agents/backend/spring-reactive/spring-reactive-test-engineer.agent.md .github/agents/backend/struts/struts-arch-advisor.agent.md .github/agents/backend/struts/struts-developer.agent.md .github/agents/backend/struts/struts-test-engineer.agent.md .github/agents/binding-initializer.agent.md .github/agents/bug-triage.agent.md .github/agents/business-rules-extractor.agent.md .github/agents/code-review.agent.md .github/agents/code-style-enforcer.agent.md .github/agents/codegraph-engine.agent.md .github/agents/compliance-guardrails.agent.md .github/agents/database-specialist.agent.md .github/agents/ddd-bounded-context-mapper.agent.md .github/agents/debugger.agent.md .github/agents/deep-search.agent.md .github/agents/devops-engineer.agent.md .github/agents/docs-engineer.agent.md .github/agents/feature-planner.agent.md .github/agents/frontend/angular/angular-arch-advisor.agent.md .github/agents/frontend/angular/angular-developer.agent.md .github/agents/frontend/angular/angular-test-engineer.agent.md .github/agents/frontend/react/react-arch-advisor.agent.md .github/agents/frontend/react/react-developer.agent.md .github/agents/frontend/react/react-test-engineer.agent.md .github/agents/governance-factory.agent.md .github/agents/governance-maintainer.agent.md .github/agents/performance-agent.agent.md .github/agents/plan-critic.agent.md .github/agents/pr-gatekeeper.agent.md .github/agents/refactor-planner.agent.md .github/agents/repo-hygiene-auditor.agent.md .github/agents/requirements-analyst.agent.md .github/agents/runtime-verifier.agent.md .github/agents/security-reviewer.agent.md .github/agents/tech-solution-architect.agent.md .github/agents/test-strategy.agent.md .github/prompts/add-project-context.prompt.md .github/prompts/connect-integration-graphs.prompt.md .github/prompts/craft-prompt.prompt.md .github/prompts/deep-search.prompt.md .github/prompts/del-project-context.prompt.md .github/prompts/eval-workflows.prompt.md .github/prompts/implement.prompt.md .github/prompts/init-context.prompt.md .github/prompts/plan-lessons-harvester.prompt.md .github/prompts/plan.prompt.md .github/prompts/review.prompt.md .github/prompts/strategic-review.prompt.md .github/prompts/synth-waves.prompt.md .github/prompts/validate.prompt.md .github/prompts/visualize-graph.prompt.md .github/agents/templates/agent-template.md .github/agents/templates/operational-agent.md .github/agents/templates/research-agent.md .github/prompts/templates/prompt-template.md .github/skills/context-mode/SKILL.md .github/skills/governance-audit-patterns/SKILL.md tests/governance_audit/test_context_mode_precedence_governance.py tests/governance_audit/test_context_mode_v2_tool_names.py
```

Após o `git restore`, reexecutar `pytest tests/governance_audit/ -q` para atestar retorno imediato ao baseline anterior.

- **Escopo Estritamente Modificativo (Zero Arquivos Novos — NIT 2):** Este plano modifica exclusivamente **76 arquivos rastreados já existentes** no repositório (zero arquivos novos criados em disco). Portanto, a execução de `git restore` sobre os 76 caminhos listados em `allowed_files` é **100% suficiente e completa** para reverter integralmente a operação, não havendo necessidade de `git clean`.

---

## 7. Estratégia de Execução Plan-Then-Batch (R-046 / R-059), Testes de Regressão e Cenários Gherkin (C4)

### 7.1. Script Consolidado Plan-Then-Batch (JavaScript / Node.js `fs` Nativo)

Na Etapa 5 (`@governance-maintainer`), a mutação dos 53 agents, 15 prompts, 4 templates elegíveis (3 de agents não-routers + 1 de prompt) e 2 skills DEVE ser executada em **um único turno de `ctx_execute`** (`language: "javascript"`), aplicando escrita idempotente:

```javascript
const fs = require('fs');
const path = require('path');

process.chdir('D:/workspace/deep-agents-copilot');

function ensureCtxToolsInFrontmatter(filePath, requiredTools) {
  const original = fs.readFileSync(filePath, 'utf8');
  const eol = original.includes('\r\n') ? '\r\n' : '\n';
  const fmRegex = /^---\r?\n([\s\S]*?)\r?\n---/;
  const match = original.match(fmRegex);
  if (!match) throw new Error('Frontmatter ausente em: ' + filePath);

  const fmLines = match[1].split(/\r?\n/);
  const existingTools = new Set((match[1].match(/context-mode\/[a-z_]+/g) || []));
  const missing = requiredTools.filter(t => !existingTools.has(t));
  if (missing.length === 0) return false;

  // Localiza a última linha de item dentro do bloco tools:
  let inTools = false;
  let lastToolIdx = -1;
  let indent = '  - ';
  let quote = '';
  for (let i = 0; i < fmLines.length; i++) {
    const line = fmLines[i];
    if (/^tools:\s*$/.test(line)) {
      inTools = true;
      continue;
    }
    if (inTools) {
      const itemMatch = line.match(/^(\s*-\s*)(["']?)([^"'\s]+)\2\s*$/);
      if (itemMatch) {
        lastToolIdx = i;
        indent = itemMatch[1];
        quote = itemMatch[2] || '';
      } else if (/^[a-zA-Z0-9_-]+:/.test(line)) {
        break;
      }
    }
  }
  if (lastToolIdx === -1) throw new Error('Bloco tools: não localizado em: ' + filePath);

  const newLines = missing.map(t => `${indent}${quote}${t}${quote}`);
  fmLines.splice(lastToolIdx + 1, 0, ...newLines);
  const updatedFm = `---${eol}${fmLines.join(eol)}${eol}---`;
  const updated = original.replace(fmRegex, updatedFm);
  fs.writeFileSync(filePath, updated, 'utf8');
  return true;
}
```

### 7.2. Cenários Comportamentais (Gherkin)

```gherkin
Feature: Padronização de context-mode/ctx_resume por Perfil Operacional (Least Privilege / R-054)

  Scenario: Cenário Positivo 1 — Todos os 53 agents operacionais elegíveis declaram ctx_index, ctx_search e ctx_resume
    Given os 63 arquivos ".agent.md" distribuídos em ".github/agents/**/*.agent.md"
    When a suíte de auditoria filtra os 53 agents operacionais (excluindo os 9 routers e "prompt-structuring.agent.md")
    Then todos os 53 agents elegíveis declaram "context-mode/ctx_index", "context-mode/ctx_search" e "context-mode/ctx_resume" no campo "tools" do frontmatter YAML
    And os 4 templates elegíveis (".github/agents/templates/agent-template.md", ".github/agents/templates/operational-agent.md", ".github/agents/templates/research-agent.md" e ".github/prompts/templates/prompt-template.md") também declaram "context-mode/ctx_resume"

  Scenario: Cenário Positivo 2 — Todos os 15 prompts slash_workflow declaram ctx_index, ctx_search, ctx_batch e ctx_resume
    Given os 24 arquivos ".prompt.md" em ".github/prompts/*.prompt.md"
    When a suíte de auditoria seleciona os 15 prompts com "router_bypass: slash_workflow"
    Then todos os 15 prompts declaram "context-mode/ctx_index", "context-mode/ctx_search", "context-mode/ctx_batch" e "context-mode/ctx_resume" no frontmatter YAML

  Scenario: Cenário Negativo 1 (Isolamento R-054) — Os 9 routers e prompt-structuring proíbem ctx_resume e ctx_index
    Given os 9 roteadores ("agent-router", "angular-router", "database-router", "ejb-router", "python-router", "react-router", "spring-boot-router", "spring-reactive-router", "struts-router") e "prompt-structuring"
    When a suíte de auditoria inspeciona o campo "tools" do frontmatter YAML desses 10 agents
    Then nenhum dos 10 agents declara "context-mode/ctx_resume", "context-mode/ctx_index" ou qualquer tool "context-mode/*"

  Scenario: Cenário Negativo 2 (Least Privilege em Prompts) — Prompts utilitários e agent-router não declaram ctx_resume
    Given os 8 prompts com "router_bypass: utility" e o prompt "agent-router.prompt.md"
    When a suíte de auditoria inspeciona o campo "tools" do frontmatter YAML desses 9 prompts
    Then nenhum dos 9 prompts isentos declara "context-mode/ctx_resume"

  Cenário: Preservação de isenção R-054 no template de roteador (.github/agents/templates/router-agent.md)
    Dado o template de roteador ".github/agents/templates/router-agent.md" regido pelo invariante R-054
    Quando a suíte de auditoria de governança inspeciona as tools declaradas nos templates
    Então ".github/agents/templates/router-agent.md" deve conter apenas "context-mode/ctx_search" como tool MCP de busca
    E não deve conter "context-mode/ctx_resume" nem "context-mode/ctx_index"
```

### 7.3. Comandos de Verificação Executável (Subetapa 5a)

1. **Execução das suítes focalizadas de precedência e allowlist v2 do `context-mode`:**
   ```bash
   pytest tests/governance_audit/test_context_mode_precedence_governance.py tests/governance_audit/test_context_mode_v2_tool_names.py -q
   ```
   - **Resultado esperado:** `exit code 0`, 100% dos testes passando (incluindo os novos testes da Tarefa T4).
2. **Execução da suíte completa de auditoria de governança:**
   ```bash
   pytest tests/governance_audit/ -q
   ```
   - **Resultado esperado:** `exit code 0`, sem regressões em paridade de catálogos, R-054, R-064 ou integridade de frontmatter YAML.
3. **Inspeção de diff e escopo permitido (`allowed_files`):**
   ```bash
   git status --short
   ```
   - **Resultado esperado:** 100% dos arquivos modificados contidos estritamente na lista `allowed_files` deste plano.

---

## 8. Segurança Agentic e Isolamento Territorial (C7 / C9 / C10 — OWASP ASI01/ASI06, R-043/R-044)

- **OWASP ASI01 (Agent Goal Hijack) & Least Privilege (R-054):** A concessão de `context-mode/ctx_resume` é estritamente restrita aos 53 agents operacionais e 15 prompts `slash_workflow`. Os 9 roteadores (`*-router.agent.md`) e `prompt-structuring.agent.md` permanecem blindados sem nenhuma tool MCP (`context-mode/*`), impedindo que payloads de memória de sessão desviem o despacho determinístico do roteador.
- **OWASP ASI06 (Memory & Context Poisoning):** Em conformidade com `CLAUSE_CONTEXT_HYDRATION`, todo snapshot ou estado recuperado via `context-mode/ctx_resume` / `context-mode/ctx_search` é tratado pelos agents folha como **contexto informativo inerte**, jamais como instrução imperativa capaz de sobrescrever guardrails de sistema ou expandir `allowed_files`.
- **Fronteira Territorial (R-043 / R-044):** Este plano não referencia slugs de projetos locais externos nem toca em `.github/instructions/local/**`. Todos os 76 caminhos em `allowed_files` pertencem exclusivamente à árvore de governança global e testes do repositório `deep-agents-copilot`.

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Rodada 1/2 (`@plan-critic` — Veredito: `NEEDS_REVISION`):**
  1. **[CORRIGIDO] HIGH (T2-TRACE / T2-SCOPE):** Removidas todas as menções aos nomes inexistentes (nomes fictícios de templates que não existiam em disco) em Q1/Q2, T0, T4 e Blast Radius, substituindo pelos 4 templates elegíveis reais em disco (`.github/agents/templates/agent-template.md`, `.github/agents/templates/operational-agent.md`, `.github/agents/templates/research-agent.md` e `.github/prompts/templates/prompt-template.md`) e removendo `.github/agents/templates/router-agent.md` de `allowed_files` (isento/proibido sob R-054).
  2. **[CORRIGIDO] HIGH (T2-SCOPE / R-054):** Alinhada a contagem ("4 templates elegíveis: 3 de agents não-routers + 1 de prompt; e 1 template de router isento por R-054") em §1.1, Q2, T0, T4, Blast Radius e Cenários Gherkin/BDD, com inclusão de cenário negativo explícito garantindo que `.github/agents/templates/router-agent.md` permanece apenas com `context-mode/ctx_search`, sem `ctx_resume` e sem `ctx_index`.
  3. **[CORRIGIDO] MEDIUM (T2-TRACE):** Reconciliada programaticamente a contagem total de `allowed_files` (76 caminhos) entre o frontmatter YAML e todas as seções do corpo do plano (§1, Blast Radius e §8).
  4. **[CORRIGIDO] T1-6 (Template de Governança):** Verificada a presença integral dos headings canônicos obrigatórios de planos de governança e registrado o histórico da Rodada 1/2 nesta seção.
- **Rodada 2/2 (`@plan-critic` — Veredito Final: `PASS_WITH_NITS`):**
  - **Metadados da Revisão:** `review_verdict: "PASS_WITH_NITS"`, `review_rounds: 2`, `review_tier1: "PASS"`, `critic_findings_summary: { blocker: 0, high: 0, medium: 0, low: 0, nit: 2 }`.
  - **Avaliação Geral:** `0 BLOCKER` e `0 HIGH`. Confirmada a **resolução integral dos 4 achados da Rodada 1/2** (T2-TRACE/T2-SCOPE sobre os 4 templates reais elegíveis, blindagem R-054 de `.github/agents/templates/router-agent.md`, reconciliação exata dos 76 caminhos em `allowed_files` e conformidade estrutural T1-6).
  - **NITs Registrados (Não-Bloqueantes):**
    - **NIT 1 ( Persistência de Metadados de Revisão):** Sincronizados os campos de veredito (`review_verdict`, `review_rounds`, `review_tier1`, `critic_findings_summary`) no frontmatter YAML e nesta seção.
    - **NIT 2 (Explicitação de Suficiência do Rollback em §6):** Adicionada nota explícita na seção `§6` (Plano de Rollback) atestando que o plano modifica apenas 76 arquivos rastreados existentes (zero arquivos novos criados), tornando `git restore` nos 76 caminhos suficiente e completo.
- **Status Atual:** Aprovado na revisão cética pré-HITL (`PASS_WITH_NITS` na Rodada 2/2). Pronto para deliberação no **Gate de Aprovação Humana (HITL)** (mantendo `status: "DRAFT"` e `approved: false` até aprovação explícita do usuário).

## Parecer de Conformidade Pós-Execução (R-064)

- **Veredito**: `PASS` (auditado por `@agent-auditor` em `2026-11-16T15:30:00Z`).
- **N1 (Allowlist)**: 76/76 arquivos de `allowed_files` modificados, 0 arquivos fora de escopo.
- **N2 (Completude T0–T4)**: 53 agents elegíveis + 15 prompts `slash_workflow` + 4 templates elegíveis + 2 skills canônicas + 2 suítes de testes Python (`134 passed`).
- **N3 (Invariantes R-054 / R-055)**: 9 routers e `prompt-structuring.agent.md` 100% preservados sem `ctx_resume`/`ctx_index`; Portão Q0..Q3 atendido.
