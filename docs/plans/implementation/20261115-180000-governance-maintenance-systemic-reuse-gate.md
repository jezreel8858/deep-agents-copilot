---
status: APPROVED
approved: true
author: "@python-arch-advisor"
workflow_tracking:
  gate2_status: "approved"
  isencao_r064: null
plan_type: "implementation"
tier: "light"
created_at: "2026-11-15"
related-planning-doc: "docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md"
review_verdict: "PASS"
review_rounds: 1
critic_review_iterations: 1
reviewer: "@plan-critic"
review_tier1: PASS
session_id: "root-session"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "trace-gov-python-boundary-001"
parent_plan_ref: "docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  resolved_in_round_2: true
  last_verdict: "PASS"
  author_ref: "@python-arch-advisor"
rollback_plan:
  - "git checkout -- tests/governance_audit/test_systemic_reuse_gate.py"
allowed_files:
  - "tests/governance_audit/test_systemic_reuse_gate.py"
progress: "8/8 (100%)"
lessons_extracted: true
lessons_applied_to: []
lessons_at: "2026-11-16"
---

# Plano de Implementação e Testes — Systemic Reuse Gate (R-055 Q3 & Veto Fail-Closed Python)

## 1. Resumo e Escopo / Não-Escopo

### Resumo
Plano de implementação técnica e testes determinísticos elaborado pelo `@python-arch-advisor` (1º passo da Tríade Python sob `@python-router`) em cumprimento ao requisito **R-055 Q3** e ao Lote 2 do plano de governança pai (`docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md`).

### Escopo (In-Scope)
- Atualização de `tests/governance_audit/test_systemic_reuse_gate.py` pelo `@python-test-engineer` para validar deterministicamente a separação de fronteira entre `@governance-maintainer` e `@python-router` (Tríade Python).
- Execução da suíte `pytest` via `scripts/dev/py-test.sh` sobre `tests/governance_audit/test_systemic_reuse_gate.py` e sobre toda a pasta `tests/governance_audit/`.

### Não-Escopo (Out-of-Scope)
- Nenhuma alteração em artefatos declarativos (`.md`, `.yaml`, `.json`), já concluídos e sincronizados no Lote 1 pelo `@governance-maintainer`.
- Nenhuma alteração em scripts de produção (`tools/**`, `scripts/**`) ou `pyproject.toml`.

---

## 2. Checklist GFM de Passos Executáveis (`@python-test-engineer`)

- [x] **Passo 1 — Suporte a subpastas em `.github/agents/` (`rglob`)**: Atualizar/adicionar helper ou leitura em `tests/governance_audit/test_systemic_reuse_gate.py` para suportar busca recursiva de agentes em subpastas de `.github/agents/` (`rglob`), permitindo localizar `.github/agents/backend/python/python-router.agent.md` e `.github/agents/backend/python/python-arch-advisor.agent.md`.
- [x] **Passo 2 — Teste 1 (Veto Fail-Closed Python no `@governance-maintainer`)**: Validar em `.github/agents/governance-maintainer.agent.md` a proibição explícita (Veto Fail-Closed) de criar, editar, formatar ou refatorar `*.py`, `conftest.py` e `pyproject.toml`.
- [x] **Passo 3 — Teste 2 (Delegação R-055 Q3 para a Tríade Python)**: Validar em `.github/agents/governance-maintainer.agent.md` a delegação obrigatória de R-055 Q3 na cadeia `@python-router` → `@python-arch-advisor` → `@python-test-engineer`.
- [x] **Passo 4 — Teste 3 (Fluxo de 2 Passos e Cobertura Python no Router e Advisor)**: Validar o fluxo de 2 passos (1º `@python-arch-advisor` → 2º `@python-developer` / `@python-test-engineer`) e a cobertura explícita de `tools/**/*.py`, `scripts/**/*.py` e `tests/**/*.py` em `.github/agents/backend/python/python-router.agent.md` e `.github/agents/backend/python/python-arch-advisor.agent.md`.
- [x] **Passo 5 — Validação e Execução da Suíte `pytest`**: Executar `scripts/dev/py-test.sh` sobre `tests/governance_audit/test_systemic_reuse_gate.py` e sobre toda a pasta `tests/governance_audit/` garantindo 100% de aprovação (exit code 0).

---

## 3. `allowed_files` e Blast Radius

- **Arquivos permitidos para mutação (`allowed_files`)**:
  - `tests/governance_audit/test_systemic_reuse_gate.py`
- **Blast Radius**: Baixo e estritamente confinado à suíte de auditoria de governança (`tests/governance_audit/`), sem impacto em runtime de aplicação ou CLIs em `tools/`.

---

## 4. Estratégia de Testes (Testing-First)

### Cenários Gherkin (R-064)

```gherkin
Funcionalidade: Enforcement determinístico da fronteira entre @governance-maintainer e @python-router

  Cenário: C1 - Veto Fail-Closed a arquivos Python no @governance-maintainer
    Dado o contrato declarativo ".github/agents/governance-maintainer.agent.md"
    Quando a suíte "test_systemic_reuse_gate.py" inspecionar as regras de escopo e não-escopo
    Então deve confirmar o veto explícito a "*.py", "conftest.py" e "pyproject.toml"
    E deve confirmar a delegação de R-055 Q3 para "@python-router" -> "@python-arch-advisor" -> "@python-test-engineer"

  Cenário: C2 - Cobertura de tools, scripts e tests na Tríade Python
    Dados os contratos ".github/agents/backend/python/python-router.agent.md" e ".github/agents/backend/python/python-arch-advisor.agent.md"
    Quando a suíte "test_systemic_reuse_gate.py" resolver os caminhos via rglob em ".github/agents/"
    Então deve confirmar o fluxo em 2 passos (1º "@python-arch-advisor" -> 2º "@python-developer" / "@python-test-engineer")
    E deve confirmar a cobertura explícita de "tools/**/*.py", "scripts/**/*.py" e "tests/**/*.py"
```

### Comandos de Verificação
1. `bash scripts/dev/py-test.sh tests/governance_audit/test_systemic_reuse_gate.py`
2. `bash scripts/dev/py-test.sh tests/governance_audit/`

---

## 5. Rollback (`tier: "light"`)

- **Tier**: `light`
- **Procedimento de Reversão**:
  - `git checkout -- tests/governance_audit/test_systemic_reuse_gate.py`
  - Preservar `docs/plans/implementation/20261115-180000-governance-maintenance-systemic-reuse-gate.md` como trilha de auditoria R-064.

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: `PASS`
- **Tier 2 (`@plan-critic`)**: `PASS` (`review_rounds: 1`, Noise Budget 0 findings `BLOCKER`/`HIGH`)
- **Findings e Resoluções**: Nenhum finding `BLOCKER`/`HIGH`. Escopo derivado do plano pai `docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md` já aprovado no Gate 2 HITL.

## Checklist

- [x] Frontmatter R-064 completo (`plan_type: "implementation"`, `tier: "light"`, `status: APPROVED`, `approved: true`).
- [x] Passos mapeados em `allowed_files` (`tests/governance_audit/test_systemic_reuse_gate.py`).
- [x] Handoff de materialização física executado por `@governance-maintainer` preservando `@python-arch-advisor` 100% Read-Only (R-025 / R-057).
