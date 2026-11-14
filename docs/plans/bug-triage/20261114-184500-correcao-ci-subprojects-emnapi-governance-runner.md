---
status: APPROVED
approved: true
author: "bug-triage"
plan_type: "bug-triage"
created_at: "2026-11-14"
related-planning-doc: "N/A — plano raiz"
allowed_files:
  - 
- 
- ".github/workflows/ci-subprojects.yml"
  - "apps/web/package-lock.json"
  - "deploy/local-chat-gateway/pyproject.toml"
  - "tools/headless-governance-runner/pyproject.toml"
  - "deploy/local-chat-gateway/tests/unit/test_sdk_session.py"
  - "deploy/local-chat-gateway/tests/fixtures/valid_graph.yaml"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
reviewer: "plan-critic"
review_tier1: "PASS"
---

# Plano de Bug-Triage — Correção do Workflow CI de Sub-projetos (@emnapi/* e governance-runner)

## Evidência do Bug e Reprodução

Durante a execução do workflow `.github/workflows/ci-subprojects.yml` (`CI — Sub-projetos (apps/web & local-chat-gateway)`), ambos os jobs (`web-lint-build` / `apps/web — lint & build` e `gateway-tests` / `local-chat-gateway — pytest`) falharam na etapa `Install dependencies` com `exit code 1`.

### Log 1 — Job `web-lint-build` (`apps/web — lint & build`)

```text
Run npm ci
npm warn EBADENGINE Unsupported engine { package: '@whatwg-node/promise-helpers@2.0.0', required: { node: '>=22.15.0' }, current: { node: 'v20.20.2', npm: '10.8.2' } }
npm warn EBADENGINE Unsupported engine { package: '@whatwg-node/disposablestack@0.1.0', required: { node: '>=22.15.0' }, current: { node: 'v20.20.2', npm: '10.8.2' } }
npm warn EBADENGINE Unsupported engine { package: 'openai@7.26.0', required: { node: '>=22.0.0' }, current: { node: 'v20.20.2', npm: '10.8.2' } }
npm error code EUSAGE
npm error Missing: @emnapi/runtime@1.11.3 from lock file
npm error Missing: @emnapi/core@1.11.3 from lock file
Error: Process completed with exit code 1.
```

### Log 2 — Job `gateway-tests` (`local-chat-gateway — pytest`)

```text
Run pip install -e ".[dev]"
SetuptoolsDeprecationWarning: project.license as a TOML table is deprecated (available on setuptools>=77.0.0).
ERROR: Could not find a version that satisfies the requirement governance-runner>=0.1.0 (from local-chat-gateway[dev])
Error: Process completed with exit code 1.
```

### Passos de Reprodução Determinística

1. Job `web-lint-build` (`apps/web — lint & build`): executar `npm ci --dry-run` em `apps/web` sob Node.js 20 com o `apps/web/package-lock.json` atual.
2. Job `gateway-tests` (`local-chat-gateway — pytest`): em ambiente limpo Python 3.11 sem `governance-runner` instalado, executar `pip install -e "deploy/local-chat-gateway[dev]"`.

## Hipótese de Causa Raiz (RCA)

A análise estática de `.github/workflows/ci-subprojects.yml`, `apps/web/package-lock.json`, `deploy/local-chat-gateway/pyproject.toml` e `tools/headless-governance-runner/pyproject.toml` identificou quatro defeitos determinísticos:

1. **Defeito 1a — Entradas `@emnapi/runtime@1.11.3` e `@emnapi/core@1.11.3` ausentes na raiz de `packages` do `apps/web/package-lock.json` (Commit `898ef803`)**:
   - A inspeção de `git show 898ef803 -- apps/web/package-lock.json` (`898ef803d0db6e4bb9b2ea1e21d728edae5df3c7 — feat(workspace): adiciona frontend CopilotKit, gateway local-chat e consolida governança multi-stack`) comprova que o lockfile foi criado em ambiente Windows contendo `node_modules/@img/sharp-wasm32` (`0.35.5`, `optional: true`) com `"@emnapi/runtime": "^1.11.3"` e `node_modules/@napi-rs/wasm-runtime` (`1.2.4`, `optional: true`) com `peerDependencies` `@emnapi/core` e `@emnapi/runtime` (`^1.7.1 || ^2.0.0-alpha.4`).
   - O commit `898ef803` gravou apenas versões `1.10.0` aninhadas em `node_modules/@unrs/resolver-binding-wasm32-wasi/node_modules/@emnapi/{core,runtime}` e `node_modules/@emnapi/wasi-threads@1.2.3` na raiz, omitindo os nós raiz `node_modules/@emnapi/runtime` (`1.11.3`) e `node_modules/@emnapi/core` (`1.11.3`), causando `EUSAGE` no `npm ci` em Linux.
2. **Defeito 1b — Engine Node.js 20 incompatível no job `web-lint-build` (`apps/web — lint & build`)**:
   - O workflow define `node-version: "20"` (`v20.20.2`), enquanto `apps/web/package.json` declara `vitest: "4.1.12"` e os pacotes do lockfile disparam `EBADENGINE`: `@whatwg-node/promise-helpers@2.0.0` (`node >= 22.15.0`), `@whatwg-node/disposablestack@0.1.0` (`node >= 22.15.0`) e `openai@7.26.0` (`node >= 22.0.0`).
3. **Defeito 2a — Dependência local `governance-runner>=0.1.0` não instalada no job `gateway-tests`**:
   - `deploy/local-chat-gateway/pyproject.toml` exige `governance-runner>=0.1.0` (pacote local em `tools/headless-governance-runner`), mas o job `gateway-tests` executa apenas `pip install -e ".[dev]"`.
4. **Defeito 2b — `project.license` como tabela TOML e requisito `setuptools>=77.0.0` (PEP 639)**:
   - Tanto `deploy/local-chat-gateway/pyproject.toml` quanto `tools/headless-governance-runner/pyproject.toml` declaram `requires = ["setuptools>=68.0", "wheel"]` em `[build-system]` e `license = { text = "Proprietary" }` em `[project]`. A migração para `license = "LicenseRef-Proprietary"` exige atualizar `[build-system] requires = ["setuptools>=77.0.0", "wheel"]` em **ambos** os arquivos `pyproject.toml`.

## Escopo de Alteração e Blast Radius

| Arquivo (`allowed_files`) | Mudança Planejada | Risco de Blast Radius |
| :--- | :--- | :--- |
| `.github/workflows/ci-subprojects.yml` | No job `web-lint-build` (`apps/web — lint & build`), usar `node-version: "22"`; no job `gateway-tests`, executar `pip install -e ../../tools/headless-governance-runner -e ".[dev]"` | Baixo |
| `apps/web/package-lock.json` | Regenerar/sincronizar entradas via CLI (`npm install --package-lock-only`) sob Node.js 22 sem edição manual de hashes | Médio |
| `deploy/local-chat-gateway/pyproject.toml` | Atualizar `[build-system] requires = ["setuptools>=77.0.0", "wheel"]` e `license = "LicenseRef-Proprietary"` (PEP 639) | Baixo |
| `tools/headless-governance-runner/pyproject.toml` | Atualizar `[build-system] requires = ["setuptools>=77.0.0", "wheel"]` e `license = "LicenseRef-Proprietary"` (PEP 639) | Baixo |

## Estratégia de Correção Mínima e Prevenção de Regressão

1. **Sincronizar `apps/web/package-lock.json` via CLI (`npm`) sem edição manual de hashes (Defeito 1a)**: no diretório `apps/web` sob Node.js >= 22.15.0 (sem `node_modules` residual), executar `npm install --package-lock-only` para que o CLI do `npm` resolva e grave deterministicamente `node_modules/@emnapi/runtime@1.11.3` e `node_modules/@emnapi/core@1.11.3` com `resolved` e `integrity` oficiais do registry, validando em seguida com `npm ci`.
2. **Atualizar `.github/workflows/ci-subprojects.yml` (Defeitos 1b e 2a)**: no job `web-lint-build` (`apps/web — lint & build`), atualizar `node-version` para `"22"`; no job `gateway-tests`, executar `pip install -e ../../tools/headless-governance-runner -e ".[dev]"`.
3. **Atualizar `pyproject.toml` do gateway e do runner (Defeito 2b)**: em `deploy/local-chat-gateway/pyproject.toml` e em `tools/headless-governance-runner/pyproject.toml`, atualizar `[build-system] requires = ["setuptools>=77.0.0", "wheel"]` junto com `license = "LicenseRef-Proprietary"`.

## Plano de Teste de Regressão e Critérios de Saída

1. **Validação completa em `apps/web`**: executar `npm ci`, `npm run lint` e `npm run build` em `apps/web` sob Node.js 22 (todos com `exit code 0`, sem erro `EUSAGE` para `@emnapi/*` e sem avisos `EBADENGINE` para `@whatwg-node/promise-helpers@2.0.0`, `@whatwg-node/disposablestack@0.1.0` e `openai@7.26.0`).
2. **Validação sintática YAML de `.github/workflows/ci-subprojects.yml`**: validar o manifesto do workflow (`python -c "import yaml; yaml.safe_load(open('.github/workflows/ci-subprojects.yml', encoding='utf-8'))"`).
3. **Validação de instalação e testes em `deploy/local-chat-gateway`**: executar `pip install -e ../../tools/headless-governance-runner -e ".[dev]"` (sem `SetuptoolsDeprecationWarning` sobre `project.license`) seguido de `pytest -q` (`exit code 0`).

## Parecer do Revisor Cético Pré-HITL (R-064)

- review_verdict: PASS_WITH_NITS
- review_rounds: 2 / teto 2
- reviewer: "@plan-critic" | review_tier1: PASS
- Contagem de Achados (Rodada 2/2): `0 BLOCKER`, `0 HIGH`, `0 MEDIUM`, `1 NIT`

| # | Severidade | Evidência | Recomendação | Status |
| :--- | :--- | :--- | :--- | :--- |
|  |  |  () | Documentar evidência concreta do commit  para  |  |
|  /  |  |  e  | Atualizar  e incluir  em  |  |
|  |  | Seção de Critérios de Saída | Especificar comandos determinísticos e verificáveis de aceite |  |
|  |  |  () | Manter  antes de  no  para resolução local determinística |  |
