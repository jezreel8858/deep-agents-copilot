---
status: "COMPLETED"
approved: true
review_verdict: "PASS"
review_rounds: 1
reviewer: "@plan-critic"
author: "@python-arch-advisor"
plan_type: "implementation"
tier: "light"
intencao_plano: "hibrido"
created_at: "2026-11-16"
related-planning-doc: "docs/plans/governance/20261116-120000-governance-maintenance-quality-gate-pos-execucao.md"
session_id: "sess-20261116-gov-qg-gap"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "trace-20261116-gov-qg-gap"
parent_plan_ref: "docs/plans/governance/20261116-120000-governance-maintenance-quality-gate-pos-execucao.md"
allowed_files:
  - "tests/governance_audit/test_post_execution_conformance_gate.py"
progress: 100
lessons_extracted: true
lessons_applied_to: ["plan-conformance-patterns"]
lessons_at: "2026-11-16"
---

# Plano de Implementação (Tier Light) — Sensor Q3 de Quality Gate Pós-Execução (`test_post_execution_conformance_gate.py`)

## 1. Contexto e Objetivo

Materializar a especificação técnica de implementação (Tier Light — `<= 3` arquivos, sem mudança de arquitetura de domínio nem dependências novas) do sensor determinístico Q3 em `tests/governance_audit/test_post_execution_conformance_gate.py`, vinculado ao plano pai de governança `docs/plans/governance/20261116-120000-governance-maintenance-quality-gate-pos-execucao.md`.

O objetivo é garantir paridade estrutural automatizada via `pytest` para a Etapa 5.5 (`PostExecutionConformanceGate`) do `WORKFLOW-GOVERNANCE-MAINTENANCE`, prevenindo regressões de contrato entre `.github/copilot-instructions.md`, `agent-router.agent.md`, `governance-maintainer.agent.md`, `agent-auditor.agent.md`, `post-implementation-conformance/SKILL.md` e `governance-audit/SKILL.md`.

## 2. Escopo e Fronteira de Mutações (`allowed_files`)

| Arquivo Alvo | Operação | Agente Executor | Responsabilidade |
| :--- | :--- | :--- | :--- |
| `tests/governance_audit/test_post_execution_conformance_gate.py` | CREATE | `@python-test-engineer` | Suíte parametrizada `pytest` (sensor Q3) validando os 5 invariantes do `PostExecutionConformanceGate` no `WORKFLOW-GOVERNANCE-MAINTENANCE`. |

- **Fronteira R-064 / R-043**: Estritamente restrito a `tests/governance_audit/test_post_execution_conformance_gate.py`. Nenhuma dependência externa adicional (`pathlib` e `pytest` padrão do repositório).

## 3. Especificação Técnica dos Testes (Casos e Asserções)

O arquivo `tests/governance_audit/test_post_execution_conformance_gate.py` deve seguir as convenções de `tests/governance_audit/` (resolução de `REPO_ROOT = Path(__file__).resolve().parents[2]`, leitura UTF-8 determinística e mensagens de falha diagnósticas):

1. **`test_copilot_instructions_declares_governance_post_execution_gate`**:
   - Inspeciona `.github/copilot-instructions.md`.
   - Verifica que a linha de `WORKFLOW-GOVERNANCE-MAINTENANCE` na tabela de workflows contém a Etapa 5.5 (`PostExecutionConformanceGate` / `@agent-auditor` em modo `post_execution_gate`) antes do encerramento, e que `R-062` referencia o gate pós-execução para ambos os fluxos (`WORKFLOW-CODE-IMPLEMENTATION` e `WORKFLOW-GOVERNANCE-MAINTENANCE`).
2. **`test_agent_router_enforces_step_5_5_before_closure`**:
   - Inspeciona `.github/agents/core/agent-router.agent.md`.
   - Verifica a presença da Etapa 5.5 obrigatória despachando `@agent-auditor` (`motivo: "post_execution_conformance_gate"`) após o retorno do `@governance-maintainer` e bloqueando fechamento direto sem veredito `PASS` ou `WAIVED_HITL`.
3. **`test_governance_maintainer_forbids_self_closure_without_auditor_gate`**:
   - Inspeciona `.github/agents/governance/governance-maintainer.agent.md`.
   - Verifica a cláusula de retorno obrigatório ao `@agent-router` para acionamento da Etapa 5.5 (`@agent-auditor`) e vedação de auto-encerramento do workflow pelo próprio executor.
4. **`test_agent_auditor_supports_post_execution_gate_mode`**:
   - Inspeciona `.github/agents/governance/agent-auditor.agent.md`.
   - Verifica suporte explícito ao modo `post_execution_gate` (Etapa 5.5) com verificação determinística (escopo `allowed_files` R-064, execução da suíte `pytest tests/governance_audit/`, paridade de catálogos/contagens e vereditos `PASS | FAIL_CONFORMANCE`) sem exigir novo plano em `docs/plans/governance/`.
5. **`test_skills_post_implementation_conformance_and_governance_audit_aligned`**:
   - Inspeciona `.github/skills/post-implementation-conformance/SKILL.md` e `.github/skills/governance-audit/SKILL.md`.
   - Verifica que ambas documentam a variante/modo de gate pós-execução de governança (`WORKFLOW-GOVERNANCE-MAINTENANCE` Etapa 5.5) e a referência ao sensor `test_post_execution_conformance_gate.py`.

## 4. Critérios de Aceite e Verificação

- [x] Arquivo `tests/governance_audit/test_post_execution_conformance_gate.py` criado com os 5 testes determinísticos cobrindo os 6 artefatos do plano pai.
- [x] Execução limpa de `pytest tests/governance_audit/test_post_execution_conformance_gate.py -q` (5 passed).
- [x] Execução regressiva de `pytest tests/governance_audit/ -q` com 100% de aprovação.
- [x] Zero erros de lint/tipagem validados via `get_errors`.

## 5. Riscos e Mitigação

| Risco | Impacto | Mitigação |
| :--- | :--- | :--- |
| Fragilidade por asserção de string excessivamente literal | Médio | Validar invariantes semânticos e tokens canônicos (`PostExecutionConformanceGate`, `post_execution_gate`, `post_execution_conformance_gate`, `Etapa 5.5`, `R-062`) com normalização básica. |
| Divergência de caminho relativo em execução de subdiretório | Baixo | Utilizar `Path(__file__).resolve().parents[2]` idêntico aos demais sensores de `tests/governance_audit/`. |
