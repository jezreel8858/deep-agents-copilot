---
status: APPROVED
approved: true
author: "agent-auditor"
plan_type: "implementation"
tier: "light"
created_at: "2026-11-14"
plan_ref: "docs/plans/bug-triage/20261114-184500-correcao-ci-subprojects-emnapi-governance-runner.md"
related-planning-doc: "docs/plans/bug-triage/20261114-184500-correcao-ci-subprojects-emnapi-governance-runner.md"
allowed_files:
  - ".github/workflows/ci-subprojects.yml"
  - "apps/web/package-lock.json"
  - "deploy/local-chat-gateway/pyproject.toml"
  - "tools/headless-governance-runner/pyproject.toml"
  - "deploy/local-chat-gateway/tests/unit/test_sdk_session.py"
  - "deploy/local-chat-gateway/tests/fixtures/valid_graph.yaml"
rollback_plan: "git checkout -- .github/workflows/ci-subprojects.yml apps/web/package-lock.json deploy/local-chat-gateway/pyproject.toml tools/headless-governance-runner/pyproject.toml deploy/local-chat-gateway/tests/unit/test_sdk_session.py deploy/local-chat-gateway/tests/fixtures/valid_graph.yaml"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
reviewer: "plan-critic"
review_tier1: "PASS"
---

# Plano de Implementação Técnica — Correção do Workflow CI de Sub-projetos (@emnapi/* e governance-runner)

## Contexto e Referência ao Plano de Domínio

Plano Gate 2 (R-064) derivado do Gate 1 aprovado (`docs/plans/bug-triage/20261114-184500-correcao-ci-subprojects-emnapi-governance-runner.md`) sob a decisão **Aplicar pacote completo (Node 22 + paths runner + SPDX license)**.

- **Inspeção de `apps/web/package-lock.json`**: `node_modules/@img/sharp-wasm32` (`0.35.5`) declara `dependencies: { "@emnapi/runtime": "^1.11.3" }`; `node_modules/@napi-rs/wasm-runtime` (`1.2.4`) declara `peerDependencies: { "@emnapi/core": "^1.7.1 || ^2.0.0-alpha.4", "@emnapi/runtime": "^1.7.1 || ^2.0.0-alpha.4" }`; `node_modules/@unrs/resolver-binding-wasm32-wasi/node_modules/@emnapi/{core,runtime}` estão fixados em `1.10.0` aninhados; `node_modules/@emnapi/wasi-threads` está em `1.2.3` na raiz, mas `packages["node_modules/@emnapi/runtime"]` e `packages["node_modules/@emnapi/core"]` estão ausentes (`null`).
- **Verificação no registry npm**: `@emnapi/runtime@1.11.3` (`https://registry.npmjs.org/@emnapi/runtime/-/runtime-1.11.3.tgz`, `sha512-Xz4Tpyki7XyrpbUK1jR1AhdAdaXyhhY4lZ3neLodmhpuWfy2PAQN5B46sAiU4liOXGLkHypn/qU+jvfWSCYYLA==`) e `@emnapi/core@1.11.3` (`https://registry.npmjs.org/@emnapi/core/-/core-1.11.3.tgz`, `sha512-zLpS5asjEb7lq8jYLq37N6XKaE41DIexlY1rF/z4/tIl3wo13Sqm28fRyfIsKZD+NZ8mM5RoKkpW/rBcuoSZSg==`) existem e devem ser gravados em `packages["node_modules/@emnapi/runtime"]` e `packages["node_modules/@emnapi/core"]` via CLI do `npm`.

## Escopo de Arquivos Permitidos (Allowlist)

| Arquivo | Operação | Justificativa |
| :--- | :--- | :--- |
| `.github/workflows/ci-subprojects.yml` | Modificar | Usar `node-version: "22"` em `web-lint-build`, incluir `tools/headless-governance-runner/**` em `paths` e instalar runner local em `gateway-tests`. |
| `apps/web/package-lock.json` | Modificar | Sincronizar via `npm install --package-lock-only` sob Node 22 para incluir `@emnapi/runtime@1.11.3` e `@emnapi/core@1.11.3`. |
| `deploy/local-chat-gateway/pyproject.toml` | Modificar | Definir `requires = ["setuptools>=77.0.0", "wheel"]` e `license = "LicenseRef-Proprietary"` (PEP 639). |
| `tools/headless-governance-runner/pyproject.toml` | Modificar | Definir `requires = ["setuptools>=77.0.0", "wheel"]` e `license = "LicenseRef-Proprietary"` (PEP 639). |
| `deploy/local-chat-gateway/tests/unit/test_sdk_session.py` | Modificar | Atualizar asserção da linha 1784 e docstring (1744–1745) para `"mcp_context-mode_ctx_batch"` conforme `sdk_session.py:466-477`. |
| `deploy/local-chat-gateway/tests/fixtures/valid_graph.yaml` | Modificar | Adicionar `gatilhos` em `WORKFLOW-TECHNICAL-ANALYSIS` e aresta `agent-router -> deep-search` para `test_governance_phase5.py:407`. |

## Passos de Implementação Sequenciais

- [x] **Passo 1**: Em `apps/web` sob Node.js >= 22.15.0 (sem `node_modules` residual), executar `npm install --package-lock-only` para registrar `node_modules/@emnapi/runtime@1.11.3` e `node_modules/@emnapi/core@1.11.3` em `apps/web/package-lock.json` sem edição manual de hashes.
- [x] **Passo 2**: Em `.github/workflows/ci-subprojects.yml`, adicionar `"tools/headless-governance-runner/**"` aos filtros `on.push.paths` e `on.pull_request.paths`, atualizar `node-version` para `"22"` no job `web-lint-build` e executar `pip install -e ../../tools/headless-governance-runner -e ".[dev]"` no job `gateway-tests`.
- [x] **Passo 3**: Em `deploy/local-chat-gateway/pyproject.toml` e `tools/headless-governance-runner/pyproject.toml`, atualizar `[build-system] requires = ["setuptools>=77.0.0", "wheel"]` e `[project] license = "LicenseRef-Proprietary"`.
- [x] **Passo 3b (`deploy/local-chat-gateway/tests/unit/test_sdk_session.py`)**: Atualizar a asserção da linha 1784 (e docstring das linhas 1744–1745) de `"mcp_context-mode_ctx_batch_execute"` para `"mcp_context-mode_ctx_batch"`, citando como evidência a normalização em `src/local_chat_gateway/sdk_session.py:466-477` sobre `mcp_tool_name="ctx_batch"` (linha 1763).
- [x] **Passo 3c (`deploy/local-chat-gateway/tests/fixtures/valid_graph.yaml`)**: Adicionar `gatilhos: ["analise tecnica", "arquitetura"]` em `WORKFLOW-TECHNICAL-ANALYSIS` e a aresta `agent-router -> deep-search` (`keywords: ["analise tecnica", "arquitetura"]`, `nivel_routing: "rule-based"`, `threshold_score: 0.70`) para atender `deploy/local-chat-gateway/tests/integration/test_governance_phase5.py:407`, documentando o Blast Radius sobre os consumidores da fixture (`tests/conftest.py:29`, `tests/integration/test_governance_phase5.py:446` e `tests/unit/test_governance_pipeline.py:219`).
- [x] **Passo 4**: Validar localmente com `npm ci && npm run lint && npm test && npm run build` em `apps/web` e `pip install -e ../../tools/headless-governance-runner -e ".[dev]" && pytest -q` em `deploy/local-chat-gateway`.

## Estratégia de Testes e Validação

| Alvo | Comando | Resultado Esperado |
| :--- | :--- | :--- |
| Web CI | `npm --prefix apps/web ci && npm --prefix apps/web run lint && npm --prefix apps/web test && npm --prefix apps/web run build` | Exit 0, sem `EUSAGE` ou `EBADENGINE`. |
| Gateway Testes Alvo | `pytest tests/unit/test_sdk_session.py tests/integration/test_governance_phase5.py tests/unit/test_governance_pipeline.py -q` (em `deploy/local-chat-gateway`) | Exit 0 nas suítes de SDK e governança. |
| Gateway CI Completo | `pip install -e tools/headless-governance-runner -e "deploy/local-chat-gateway[dev]" && pytest -q` (em `deploy/local-chat-gateway`) | Exit 0, sem `SetuptoolsDeprecationWarning`. |
| Conformidade R-064 | Validação `tier1_validate` em Gate 1 e Gate 2 | Veredito `PASS` em ambos os planos. |

## Plano de Rollback

```bash
git checkout -- .github/workflows/ci-subprojects.yml apps/web/package-lock.json deploy/local-chat-gateway/pyproject.toml tools/headless-governance-runner/pyproject.toml
```

## Alternativas Rejeitadas

1. **Edição manual de hashes SHA-512 em `apps/web/package-lock.json`**: rejeitada por risco de corrupção de integridade do lockfile.
2. **Troca de `npm ci` por `npm install` no CI**: rejeitada por eliminar builds determinísticos.
3. **Manter `license = { text = "Proprietary" }`**: rejeitada por depreciação PEP 639 no `setuptools>=77`.

## Parecer do Revisor Cético Pré-HITL (R-064)

- review_verdict: PASS_WITH_NITS
- review_rounds: 2 / teto 2 (Fast-Pass — Rastreabilidade dos 6 arquivos no corpo concluída)
- reviewer: "@plan-critic" | review_tier1: PASS
- Contagem de Achados (Rodada 2/2): `0 BLOCKER`, `0 HIGH`, `0 MEDIUM`, `1 NIT`
- Nota de Resolução (Rodada 2/2): Os 3 apontamentos de rastreabilidade do corpo foram resolvidos: (1) Allowlist com as 6 linhas dos 6 arquivos de `allowed_files`; (2) Passos 3b (`test_sdk_session.py:1784` / `sdk_session.py:466-477`) e 3c (`valid_graph.yaml` / `test_governance_phase5.py:407` + Blast Radius em `tests/conftest.py:29`, `tests/integration/test_governance_phase5.py:446` e `tests/unit/test_governance_pipeline.py:219`); (3) comando alvo `pytest tests/unit/test_sdk_session.py tests/integration/test_governance_phase5.py tests/unit/test_governance_pipeline.py -q` além de `pytest -q`.

| # | Severidade | Evidência | Recomendação | Status |
| :--- | :--- | :--- | :--- | :--- |
| `[I]1` | `HIGH` | Allowlist (6 arquivos) | Sincronizar tabela com `allowed_files` | `RESOLVED (Rodada 2/2)` |
| `[I]2` | `HIGH` | Passos 3b e 3c | Documentar passos e Blast Radius | `RESOLVED (Rodada 2/2)` |
| `[I]3` | `MEDIUM` | Estratégia de Testes | Incluir `pytest` alvo + `pytest -q` | `RESOLVED (Rodada 2/2)` |
| `[G]1` | `NIT` | `.github/workflows/ci-subprojects.yml` | Manter `-e ../../tools/headless-governance-runner` antes de `-e ".[dev]"` | `OPEN (Não-bloqueante — Fast-Pass)` |
