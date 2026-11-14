---
status: "APPROVED"
approved: true
author: "agent-auditor"
plan_type: "implementation"
created_at: "2026-11-14"
tier: "light"
plan_ref: "docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md"
related-planning-doc: "docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md"
review_verdict: "PASS_WITH_NITS"
review_rounds: 3
reviewer: "plan-critic"
review_tier1: "PASS"
rollback_plan: "git checkout -- apps/web/package.json apps/web/package-lock.json .github/agents/backend/*/*.agent.md .github/agents/frontend/*/*.agent.md .a2a/agentcards/"
allowed_files:
  - "apps/web/package.json"
  - "apps/web/package-lock.json"
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
  - ".a2a/agentcards/database-arch-advisor.agentcard.json"
  - ".a2a/agentcards/informix-database-specialist.agentcard.json"
  - ".a2a/agentcards/oracle-database-specialist.agentcard.json"
  - ".a2a/agentcards/ejb-developer.agentcard.json"
  - ".a2a/agentcards/ejb-test-engineer.agentcard.json"
  - ".a2a/agentcards/python-arch-advisor.agentcard.json"
  - ".a2a/agentcards/python-developer.agentcard.json"
  - ".a2a/agentcards/python-router.agentcard.json"
  - ".a2a/agentcards/python-test-engineer.agentcard.json"
  - ".a2a/agentcards/spring-boot-arch-advisor.agentcard.json"
  - ".a2a/agentcards/spring-boot-developer.agentcard.json"
  - ".a2a/agentcards/spring-boot-test-engineer.agentcard.json"
  - ".a2a/agentcards/spring-reactive-developer.agentcard.json"
  - ".a2a/agentcards/spring-reactive-test-engineer.agentcard.json"
  - ".a2a/agentcards/struts-developer.agentcard.json"
  - ".a2a/agentcards/struts-test-engineer.agentcard.json"
  - ".a2a/agentcards/angular-developer.agentcard.json"
  - ".a2a/agentcards/angular-test-engineer.agentcard.json"
  - ".a2a/agentcards/react-arch-advisor.agentcard.json"
  - ".a2a/agentcards/react-developer.agentcard.json"
  - ".a2a/agentcards/react-test-engineer.agentcard.json"
  - ".a2a/agentcards/agentcards.index.json"
---

# Plano de Implementação (Gate 2) — Correção das Falhas dos Workflows GitHub Actions CI

## 1. Resumo, Escopo e Não-Escopo

Plano alinhado a `docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md`:
1. **`ci-subprojects.yml` (`apps/web`)**: `apps/web` é **Next.js 16** (`"dev": "next dev"`, `"build": "next build"`, `"lint": "eslint ."`, `"test": "vitest run"`). O `npm ci` falha porque `apps/web/package.json` declara `"vitest": "5.0.3"` e `"lucide-react": "0.525.0"` enquanto `apps/web/package-lock.json` possui entradas `@vitest/*` híbridas (`5.0.3` + `4.1.11`) não sincronizadas.
2. **Workflows Python/Governança**: 21 agents em `.github/agents/{backend,frontend}/*/*.agent.md` divergem do fragmento SSOT `tools/agent_router_return_sync/_router-return-fragment.md`.

**Não-Escopo**: Não alterar `.github/workflows/*.yml`, não adicionar `typecheck` nem Vite em `apps/web`, não alterar `tools/` nem `tests/`.

## 2. Checklist GFM de Passos Executáveis

- [x] **Passo 1 (`apps/web`)**: Alinhar `vitest` para `"4.1.12"` em `apps/web/package.json`, regenerar `apps/web/package-lock.json` via `npm install --package-lock-only` em `apps/web` e validar `npm ci --dry-run` (exit 0).
- [x] **Passo 2 (Sync SSOT Retorno ao Router)**: Executar `python tools/agent_router_return_sync/sync_router_return.py --apply` e validar com `python tools/agent_router_return_sync/sync_router_return.py --check` (exit 0) contra `tools/agent_router_return_sync/_router-return-fragment.md`.
- [x] **Passo 3 (AgentCards A2A)**: Executar `python tools/agentcard_exporter/export_agentcards.py --check`; se houver drift de hashes/cards após o sync dos 21 agents, executar `python tools/agentcard_exporter/export_agentcards.py --write` e revalidar `--check`.
- [x] **Passo 4 (Testes e Build)**: Executar `pytest tests/routing_gate/ tests/governance_audit/ tests/operational_flow/ -q` e, em `apps/web`, `npm run lint && npm test && npm run build`.

## 3. Escopo de Arquivos Autorizados (`allowed_files`) e Blast Radius

| Alvo | Qtd | Condicionalidade | Ação e Blast Radius |
|---|---|---|---|
| `apps/web/package.json` | 1 | Obrigatório | Alinhar `"vitest": "4.1.12"` (Next.js 16; baixo blast radius) |
| `apps/web/package-lock.json` | 1 | Obrigatório | Regenerar via `npm install --package-lock-only` em `apps/web` |
| `.github/agents/{backend,frontend}/*/*.agent.md` | 21 | Obrigatório | Sincronizar com `tools/agent_router_return_sync/_router-return-fragment.md` via `sync_router_return.py --apply` |
| `.a2a/agentcards/*.json` | 22 | **Condicional** | Os 22 arquivos de `.a2a/agentcards/` são condicionais (caso `export_agentcards.py --check` aponte necessidade de atualizar os hashes/cards após o sync dos 21 agents) |

## 4. Estratégia de Testes (Testing-First)

- **Pré-Fix (Red)**: `npm ci --dry-run` falha em `apps/web` (EUSAGE); `python tools/agent_router_return_sync/sync_router_return.py --check` falha (21 agents).
- **Pós-Fix (Green)**: `npm ci --dry-run` (exit 0), `python tools/agent_router_return_sync/sync_router_return.py --check` (exit 0), `python tools/agentcard_exporter/export_agentcards.py --check` (exit 0) e `pytest tests/routing_gate/ tests/governance_audit/ tests/operational_flow/ -q` (0 failed).

## Plano de Rollback

- **Tier**: `light` (enum `full | light | governance` compatível com `tier1_validate`).
- **Comando específico da allowlist (sem descartar `.github/agents/` inteiro)**:
  ```bash
  git checkout -- apps/web/package.json apps/web/package-lock.json .github/agents/backend/*/*.agent.md .github/agents/frontend/*/*.agent.md .a2a/agentcards/
  ```

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Reviewer**: `plan-critic`
- **Rodada**: `2/2`
- **Tier 1 (`tier1_validate`)**: `PASS` (0 violações determinísticas T1-1..T1-10)
- **Veredito Final**: `ESCALATED_HITL` (Rodada 2/2 concluída; os 2 apontamentos textuais remanescentes de path foram saneados na persistência pré-HITL pelo `@docs-engineer`)

### Resolução dos Achados da Rodada 1/2 e Saneamento Pré-HITL (Rodada 2/2)

| ID | Severidade Original | Status na Rodada 2/2 | Evidência de Resolução / Saneamento Pré-HITL |
|---|---|---|---|
| **BLOCKER #1** | BLOCKER | ✅ Resolvido | Removida referência inexistente a `npm run typecheck`; scripts reais validados em `apps/web/package.json` (`dev`, `build`, `lint`, `test`). |
| **BLOCKER #2** | BLOCKER | ✅ Resolvido | Corrigida premissa arquitetural: `apps/web` é **Next.js 16** (sem Vite); fix foca em alinhar `"vitest": "4.1.12"` e regenerar `apps/web/package-lock.json` via `npm install --package-lock-only` para destravar `npm ci`. |
| **HIGH #3** | HIGH | ✅ Resolvido | Comandos de validação e build ajustados para o pipeline real de `ci-subprojects.yml` (`npm ci --dry-run`, `npm run lint`, `npm test`, `npm run build`). |
| **HIGH #4** | HIGH | ✅ Saneado Pré-HITL | Definido `tier: "light"`, comandos reais de validação (`sync_router_return.py`, `export_agentcards.py`, `pytest`) e corrigidas as 3 menções do fragmento SSOT para o caminho real `tools/agent_router_return_sync/_router-return-fragment.md`. |
| **MEDIUM #5** | MEDIUM | ✅ Saneado Pré-HITL | Explicitada a condicionalidade dos 22 arquivos de `.a2a/agentcards/` e corrigidos os globs de `rollback_plan` (frontmatter e seção `## Plano de Rollback`) para os diretórios reais `.github/agents/backend/*/*.agent.md .github/agents/frontend/*/*.agent.md`. |
| **LOW #6** | LOW | ✅ Resolvido | Mantido `author: "agent-auditor"` sem `@` no frontmatter em conformidade com o contrato regex `T1-3` (`^[a-z0-9-]+$`) de `tier1_validate`. |

### Rodada 3 (Convergência Final — )

- **review_verdict**: 
- **review_rounds**: 
- **reviewer**:  | **review_tier1**: 
- **Contagem de Achados (Rodada 3)**: , , , ,  (NIT #1 resolvido com ).
- **Validação **:  (frontmatter R-064 completo, , ,  explícitos sem globs e  íntegro).
