---
status: APPROVED
approved: true
author: "bug-triage"
plan_type: "bug-triage"
created_at: "2026-11-14"
related-planning-doc: "N/A — plano raiz"
allowed_files:
  - "apps/web/package.json"
  - "apps/web/package-lock.json"
  - ".github/workflows/ci-subprojects.yml"
  - ".github/workflows/routing-quality-gate.yml"
  - "tools/agent_router_return_sync/sync_router_return.py"
  - ".github/agents/backend/database/database-arch-advisor.agent.md"
  - ".github/agents/backend/database/informix-database-specialist.agent.md"
  - ".github/agents/backend/database/oracle-database-specialist.agent.md"
  - ".github/agents/backend/ejb/ejb-developer.agent.md"
  - ".github/agents/backend/ejb/ejb-test-engineer.agent.md"
  - ".github/agents/backend/python/python-arch-advisor.agent.md"
  - ".github/agents/backend/python/python-developer.agent.md"
  - ".github/agents/backend/python/python-router.agent.md"
  - ".github/agents/backend/python/python-test-engineer.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-developer.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-developer.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-test-engineer.agent.md"
  - ".github/agents/backend/struts/struts-developer.agent.md"
  - ".github/agents/backend/struts/struts-test-engineer.agent.md"
  - ".github/agents/frontend/angular/angular-developer.agent.md"
  - ".github/agents/frontend/angular/angular-test-engineer.agent.md"
  - ".github/agents/frontend/react/react-arch-advisor.agent.md"
  - ".github/agents/frontend/react/react-developer.agent.md"
  - ".github/agents/frontend/react/react-test-engineer.agent.md"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
reviewer: "plan-critic"
review_tier1: "PASS"
---

# Plano de Bug-Triage — Correcao de Falhas nos Workflows de GitHub Actions CI

## Contexto e Conformidade Local

- **Autor Intelectual**: `@bug-triage` (`author: "bug-triage"`, conforme R-064 e regex de `tier1_validate`).
- **Documento Relacionado**: `N/A — plano raiz` (plano raiz do `WORKFLOW-BUG-FIX`, Gate 1 Pre-HITL).
- **Conformidade com Instrucoes Locais**: Elaborado e revisado em conformidade com `.github/instructions/local/deep-agents-chat.instructions.md` (stack Next.js + CopilotKit em `apps/web/`, governanca declarativa em `.github/agents/` e sincronizacao obrigatoria via `tools/agent_router_return_sync/sync_router_return.py`).

## Sintoma Observado e Reproducao

1. **Workflow `.github/workflows/ci-subprojects.yml` (job `web-lint-build`)**: falha em `npm ci` (`working-directory: apps/web`):
```text
npm error Invalid: lock file @vitest/mocker@4.1.11 does not satisfy @vitest/mocker@4.1.12
npm error Invalid: lock file @vitest/spy@4.1.11 does not satisfy @vitest/spy@4.1.12
```
2. **Workflow `.github/workflows/routing-quality-gate.yml` (step `Gates mecanicos`)**:
   - `sync_execution_protocol.py --check`, `sync_required_source_docs.py --check` e `export_agentcards.py --check` -> **PASS (exit 0)**
   - `python tools/agent_router_return_sync/sync_router_return.py --check` -> **FAIL (exit 1)** (21 agents em drift).

### Evidencia de Historico Git (`git log -p -n 3 -- apps/web/package.json apps/web/package-lock.json`)

1. **Commit `898ef803d0db6e4bb9b2ea1e21d728edae5df3c7` (`2026-10-03 02:34:27 -0300`)**: editou manualmente `apps/web/package.json` e `apps/web/package-lock.json` para declarar `vitest: "5.0.3"` em `packages[""]` e `node_modules/vitest` (`version: "5.0.3"`, mantendo na sua lista de `dependencies` os requisitos `@vitest/expect: "4.1.12"`, `@vitest/mocker: "4.1.12"`, `@vitest/runner: "4.1.12"`, `@vitest/snapshot: "4.1.12"`, `@vitest/spy: "4.1.12"` e `@vitest/utils: "4.1.12"` — ou `@vitest/mocker: "5.0.3"` e `node_modules/@vitest/{mocker,spy}` em `"5.0.3"`), enquanto manteve os pacotes resolvidos `node_modules/@vitest/{expect,pretty-format,runner,snapshot,utils}` e `node_modules/@copilotkit/*/node_modules/@vitest/{mocker,spy}` congelados em `version: "4.1.11"`.
2. **Commit `1ef58bf07c931e342af85f59c7865ecf8a6195a5` (`2026-10-03 16:32:40 -0300`, `feat(web): dark mode toggle + streamdown table fix`)**: adicionou `lucide-react: "0.525.0"` em `apps/web/package.json` sem atualizar `apps/web/package-lock.json`.
3. **Comparacao Local vs Remoto (`origin/develop` @ `358b0744`)**: 3 checks passam (`exit 0`) e `sync_router_return.py --check` falha (`exit 1`); `governance-agent-audit.yml` e `model-allowlist-refresh.yml` foram removidos de `allowed_files` (R-001/R-011).

## Hipótese de Causa Raiz (RCA)

1. **Corrupcao de estado hibrido em `apps/web/package-lock.json` e dessincronizacao com `apps/web/package.json` (Nit #1 resolvido)**: a inspecao exata de `apps/web/package-lock.json` comprova que `node_modules/vitest` foi editado manualmente no commit `898ef803` para `version: "5.0.3"` (versao inexistente no npm registry; no estado atual do lockfile, `node_modules/vitest`, `node_modules/@vitest/mocker` e `node_modules/@vitest/spy` estao com `version: "5.0.3"` enquanto `node_modules/@vitest/{expect,pretty-format,runner,snapshot,utils}` e `node_modules/@copilotkit/{channels-intelligence,channels-slack,channels-teams,runtime}/node_modules/@vitest/{mocker,spy}` permanecem em `version: "4.1.11"`, e quando o npm resolve o manifesto real de `vitest@4.1.12` do registry ele exige `@vitest/{expect,mocker,runner,snapshot,spy,utils}@4.1.12` contra os pacotes `4.1.11` fixados no lockfile), causando `EUSAGE` (`Invalid: lock file @vitest/mocker@4.1.11 does not satisfy @vitest/mocker@4.1.12`) no `npm ci`, somado a adicao de `lucide-react: "0.525.0"` (commit `1ef58bf0`) sem atualizacao do `package-lock.json`.
2. **Drift R-042 em 21 agents**: 21 arquivos `.agent.md` sem sincronizacao da secao `Retorno ao Router (R-042)`.

## Alternativas Rejeitadas (Hipóteses Descartadas)

| Alternativa / Hipotese Avaliada | Motivo da Rejeicao (Trade-off e Risco Evitado) |
|---|---|
| **H1 — Trocar `npm ci` por `npm install` no CI** | **Descartada.** Quebra a reprodutibilidade deterministica no GitHub Actions e mascara corrupcoes do `package-lock.json`. |
| **H2 — Manter `vitest: "5.0.3"` no `apps/web/package.json`** | **Descartada.** `vitest@5.0.3` nao existe no npm registry — `apps/web/package-lock.json` usa `4.1.12` / `4.1.11`, alterado por engano em bump automatico que confundiu `@vitejs/plugin-react` 5.x com `vitest`. |
| **H3 — Desabilitar `sync_router_return.py --check` no CI** | **Descartada.** Viola a governanca R-042 (Anti Sticky-Session). |
| **H4 — Manter `governance-agent-audit.yml` e `model-allowlist-refresh.yml` em `allowed_files`** | **Descartada.** Viola R-001/R-011 pois nao serao modificados. |

## Analise de Impacto e Risco de Regressao

| Modulo / Arquivo | Impacto Direto | Risco Colateral |
|---|---|---|
| `apps/web/package.json` e `apps/web/package-lock.json` | Alto — alinhar `vitest` para `4.1.12` (preservando `lucide-react@0.525.0`) e regerar lockfile via `npm install --package-lock-only` | Baixo (restrito a `devDependencies` de teste) |
| `.github/workflows/ci-subprojects.yml` e `routing-quality-gate.yml` | Alto (CI) — desbloqueia `npm ci` e `Gates mecanicos` (`sync_router_return.py --apply` nos 21 agents) | Baixo |

## Escopo da Correcao Proposta (Alto Nivel)

1. **Sincronizacao deterministica de `apps/web`**: fixar `"vitest": "4.1.12"` em `apps/web/package.json`, executar `npm install --package-lock-only` em `apps/web/` e validar com `npm ci --dry-run`.
2. **Sincronizacao R-042**: executar `python tools/agent_router_return_sync/sync_router_return.py --apply` nos 21 agents listados em `allowed_files`.

## Plano de Teste de Regressão e Critérios de Saída

| Ordem | Alvo | Comando Executavel | Criterio de Saida |
|---|---|---|---|
| 1 | Lockfile `apps/web` | `npm --prefix apps/web ci --dry-run` | `exit 0` sem `EUSAGE` |
| 2 | Pipeline `apps/web` | `npm --prefix apps/web ci && npm --prefix apps/web run lint && npm --prefix apps/web run type-check && npm --prefix apps/web test` | `exit 0` em todos os steps |
| 3 | Gates mecanicos (4 checks) | `python tools/protocol_injection/sync_execution_protocol.py --check && python tools/required_source_docs_sync/sync_required_source_docs.py --check && python tools/agent_router_return_sync/sync_router_return.py --check && python tools/a2a_Discovery/export_agentcards.py --check` | Todos `exit 0` |
| 4 | Auditoria de governanca | `pytest tests/governance_audit/ -q` | `exit 0` (100% passando) |

## Plano de Rollback Executável

1. **Pre-commit**: `git checkout -- apps/web/package.json apps/web/package-lock.json .github/agents/`
2. **Pos-commit**: `git revert --no-edit HEAD`
3. **Validacao pos-rollback**: executar `python tools/agent_router_return_sync/sync_router_return.py --check` e `pytest tests/governance_audit/test_pre_hitl_skeptical_plan_gate.py -q`.

## Parecer do Revisor Cético Pré-HITL (R-064)

### Rodada 1/2 — Veredito: `NEEDS_REVISION` (`@plan-critic`)

- **Tier 1**: `PASS`. **Tier 2**: `NEEDS_REVISION` (6 achados resolvidos):
  1. **BLOCKER (Resolvido)**: Adicionada secao `## Alternativas Rejeitadas (Hipóteses Descartadas)`.
  2. **BLOCKER (Resolvido)**: Adicionadas secoes `## Plano de Teste de Regressão e Critérios de Saída` e `## Plano de Rollback Executável`.
  3. **HIGH (Resolvido)**: Removidos `.github/workflows/governance-agent-audit.yml` e `.github/workflows/model-allowlist-refresh.yml` de `allowed_files` (R-001/R-011).
  4. **HIGH (Resolvido)**: Inspecionado `git log -p -n 3 -- apps/web/package.json apps/web/package-lock.json` (commits `898ef803` e `1ef58bf0`) e definido `vitest: "4.1.12"` + `npm install --package-lock-only` validado com `npm ci --dry-run`.
  5. **MEDIUM (Resolvido)**: Mantido `author: "bug-triage"` (compativel com `tier1_validate`) e registrado parecer da Rodada 1/2 e espaco para Rodada 2/2.
  6. **LOW (Resolvido)**: Ajustado `related-planning-doc: "N/A — plano raiz"` e citada conformidade com `.github/instructions/local/deep-agents-chat.instructions.md`.

### Rodada 2/2 — Veredito: `PASS_WITH_NITS` (`@plan-critic`)

- **Tier 1**: `PASS` (`tier1_validate` validado com `status: DRAFT`, `approved: false`, `author: "bug-triage"`, `plan_type: "bug-triage"`, `review_verdict: "PASS_WITH_NITS"`, `review_rounds: 2`, `reviewer: "plan-critic"`, `review_tier1: "PASS"`).
- **Tier 2**: `PASS_WITH_NITS` (0 BLOCKER, 0 HIGH, 1 MEDIUM/Nit resolvido in-place):
  1. **MEDIUM / Nit #1 (Resolvido)**: Esclarecida no RCA e na secao de Evidencia de Historico Git a anatomia exata de `node_modules/vitest` e `node_modules/@vitest/*` em `apps/web/package-lock.json` (`node_modules/vitest`, `node_modules/@vitest/mocker` e `node_modules/@vitest/spy` editados manualmente para `version: "5.0.3"`, coexistindo com `node_modules/@vitest/{expect,pretty-format,runner,snapshot,utils}@4.1.11` e `node_modules/@copilotkit/*/node_modules/@vitest/{mocker,spy}@4.1.11`, o que dispara o conflito `4.1.11 does not satisfy 4.1.12` frente ao manifesto real de `vitest@4.1.12`).
- **Status Gate 1 Pré-HITL**: Aprovado tecnicamente pelo `@plan-critic` (`PASS_WITH_NITS`) — pronto para apresentacao ao Gate de Aprovacao Humana (HITL).
