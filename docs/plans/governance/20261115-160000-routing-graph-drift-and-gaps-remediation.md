---
status: "APPROVED"
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-15"
review_verdict: PASS
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PASS
allowed_files:
  - "docs/plans/governance/20261115-160000-routing-graph-drift-and-gaps-remediation.md"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/evals/casos-roteamento.yaml"
  - "tools/headless-governance-runner/src/governance_runner/synth/routing_graph.py"
  - "tools/headless-governance-runner/src/governance_runner/synth/golden.py"
  - "tools/headless-governance-runner/tests/routing_unit/test_TC05_state_machine_valid_transitions.py"
  - "tools/headless-governance-runner/tests/routing_unit/test_TC06_state_machine_illegal_transition.py"
  - "tools/headless-governance-runner/tests/routing_unit/test_state_machine_idempotency.py"
  - ".github/agents/evals/synthetic/diagnostic-52e57357-a4e7-4034-8a6e-7bc56047597d.yaml"
  - ".github/agents/evals/synthetic/diagnostic-52e57357-a4e7-4034-8a6e-7bc56047597d.md"
lessons_extracted: true
lessons_applied_to: []
lessons_at: "2026-11-15"
related-planning-doc: "docs/architecture/BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md"
session_id: "sess-20261115-160000-routing-drift-remediation"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-20261115-160000-routing-graph-drift-and-gaps"
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
---

# Plano de Manutenção de Governança — Remediação de Drift e Cobertura de Arestas (`diag-fca52925eb24`)

## 1. Contexto e Motivação
Remediação estrutural aprovada pelo usuário (`"prossiga opcao 2 depois opcao 1"`) a partir do diagnóstico empírico `diag-fca52925eb24` (`eval_run_id: e11afb8e-199d-42fd-80c7-940b2fa93504`), eliminando:
1. **Drift documental em `.github/agents/agent-router.agent.md`** (`SUG-0029`, `nos_nao_citados: ['plan-critic']`).
2. **Gaps de cobertura no Golden Set (`.github/agents/evals/casos-roteamento.yaml`)** para as **9 arestas órfãs** (`SUG-0020` a `SUG-0028`: `e-0deda784e717`, `e-29a82d8c7294`, `e-31998f180c47`, `e-4b90caff6f5c`, `e-562a6ca3b730`, `e-56a9fbad60e1`, `e-597778e57b18`, `e-c8da7cb5f0d9`, `e-e6f649fa9331`), elevando `cobertura_arestas_golden` de **76,32% (29/38)** para **100,00% (38/38)**.
3. **Validação empírica pós-remediação via Copilot SDK (`synth-generate` -> `synth-eval` -> `synth-diagnose`)** sobre as rotas remediadas (`gen_run_id: 519889332ebd4f25a8dd43d25052f649`, `eval_run_id: 52e57357-a4e7-4034-8a6e-7bc56047597d`).

## 2. Checklist de Execução (Opção 2 + Opção 1)
- [x] **T1 (Gate 2 / R-064)**: Materializar plano aprovado em `docs/plans/governance/20261115-160000-routing-graph-drift-and-gaps-remediation.md`.
- [x] **T2 (`SUG-0029`)**: Documentar explicitamente a rota `@plan-critic` na Decision Tree e na seção `Quando Delegar` de `.github/agents/agent-router.agent.md`, zerando `nos_nao_citados`.
- [x] **T3 (`SUG-0020`..`SUG-0028`)**: Adicionar casos canônicos (`canon-051` a `canon-060`) em `.github/agents/evals/casos-roteamento.yaml` e ajustar resolução de fallback sem keywords em `routing_graph.py::resolver_aresta` e contagem canônica em `golden.py`, atingindo **38/38 (100%)** de arestas cobertas no Golden Set.
- [x] **T4 (Opção 1 — Pipeline `synth` via Copilot SDK)**: Executar `synth-generate` (`run_id=519889332ebd4f25a8dd43d25052f649`), `synth-eval` (`run_id=52e57357-a4e7-4034-8a6e-7bc56047597d`) e `synth-diagnose` gerando `diagnostic-52e57357-a4e7-4034-8a6e-7bc56047597d.yaml` e `.md`.
- [x] **T5 (Quality Gate)**: Executar suítes de testes automatizados (`tests/synth_unit`, `tests/routing_unit`, `tests/routing_gate`, `tests/evals`) e `get_errors` com 100% de aprovação.
- [x] Alinhamento do template do banner `Workflow: <...>` em `.github/agents/agent-router.agent.md` para listar os 9 workflows canônicos (incluindo `WORKFLOW-REQUIREMENTS-ELICITATION`) e `N/A`.
