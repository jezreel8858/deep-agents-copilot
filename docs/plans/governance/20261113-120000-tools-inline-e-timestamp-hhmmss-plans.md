---
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-13"
date: "2026-11-13"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
related-planning-doc: "N/A — plano raiz (WORKFLOW-GOVERNANCE-MAINTENANCE)"
allowed_files:
  - ".github/prompts/ctx-*.prompt.md"
  - ".github/skills/**/SKILL.md"
  - ".github/skills/**/references/*.md"
  - ".github/agents/**/*.md"
  - ".github/copilot-instructions.md"
  - "CLAUDE.md"
  - "AGENTS.md"
  - "README.md"
  - "CHANGELOG.md"
  - "docs/plans/**"
  - "tests/governance_audit/*.py"
---

# Plano de Manutenção de Governança — Padronização de `tools:` Inline Array e Timestamp `AAAAMMDD-HHMMSS` em `docs/plans/`

## 1. Escopo da Manutenção e Achados (Smells 2.x com Severidade)

| ID | Smell / Achado | Severidade | Descrição e Evidência |
|---|---|---|---|
| **Frente 1** | **Smell 2.14 / R-053 — Frontmatter `tools:` em lista YAML multiline** | **MÉDIA** | 15 artefatos de governança (5 `.prompt.md` em `.github/prompts/ctx-*.prompt.md` e 10 `SKILL.md` em `.github/skills/`) declaram `tools:` em formato de lista YAML multiline (`\n  - tool`) em vez do padrão canônico inline array (`tools: ['tool1', 'tool2']`). Em `project-context-builder/SKILL.md`, o bloco `tools:` encontra-se ainda fora do frontmatter principal (linhas 50–55), logo após um bloco de exemplo markdown. |
| **Frente 2** | **Smell 2.34 / R-064 — Colisão intra-dia e heterogeneidade de nomes em `docs/plans/<tipo>/`** | **ALTA** | Os 44 planos existentes nas 8 subpastas de `docs/plans/` utilizam apenas data de 8 dígitos (`AAAAMMDD-<slug>.md`) ou nomes legados sem prefixo temporal (`PLAN-*.md`, `REQ-*.md`, `plano-*.md`, `agent-profiles-taxonomy.md`), impedindo ordenação cronológica determinística intra-dia quando múltiplos planos são gerados na mesma data. |

---

## 2. Artefatos Afetados e `allowed_files`

### 2.1 Frente 1 — 15 Artefatos com `tools:` Multiline → Inline Array

#### Prompts (`.github/prompts/` — 5 arquivos)
1. `.github/prompts/ctx-checkpoint.prompt.md` → `tools: ['context-mode/ctx_index']`
2. `.github/prompts/ctx-doctor.prompt.md` → `tools: ['context-mode/ctx_doctor']`
3. `.github/prompts/ctx-insight.prompt.md` → `tools: ['context-mode/ctx_insight']`
4. `.github/prompts/ctx-resume.prompt.md` → `tools: ['context-mode/ctx_search', 'ask_questions']`
5. `.github/prompts/ctx-status.prompt.md` → `tools: ['context-mode/ctx_stats']`

#### Skills (`.github/skills/` — 10 arquivos)
6. `.github/skills/business-rules-governance/SKILL.md` → `tools: ['read_file', 'grep_search', 'file_search', 'create_file', 'insert_edit_into_file']`
7. `.github/skills/code-tracing/SKILL.md` → `tools: ['grep_search', 'file_search', 'read_file', 'run_in_terminal']`
8. `.github/skills/context-mode/SKILL.md` → `tools: ['context-mode/ctx_search', 'context-mode/ctx_batch_execute', 'context-mode/ctx_execute', 'context-mode/ctx_execute_file', 'context-mode/ctx_index', 'context-mode/ctx_fetch_and_index', 'context-mode/ctx_stats', 'context-mode/ctx_doctor', 'context-mode/ctx_upgrade', 'context-mode/ctx_purge', 'context-mode/ctx_insight']`
9. `.github/skills/efficient-batch-code-modification/SKILL.md` → `tools: ['replace_string_in_file', 'insert_edit_into_file', 'create_file', 'read_file', 'grep_search', 'get_errors', 'context-mode/ctx_execute', 'context-mode/ctx_execute_file', 'context-mode/ctx_batch_execute']`
10. `.github/skills/git-worktree-governance/SKILL.md` → `tools: ['run_in_terminal']`
11. `.github/skills/integration-contract-analysis/SKILL.md` → `tools: ['grep_search', 'file_search', 'read_file', 'context-mode/ctx_batch_execute', 'context-mode/ctx_execute']`
12. `.github/skills/project-context-builder/SKILL.md` → mover `tools: ['read_file', 'create_file', 'list_dir', 'grep_search', 'file_search']` das linhas 50–55 para dentro do frontmatter YAML principal (topo do arquivo)
13. `.github/skills/project-scanner/SKILL.md` → `tools: ['read_file', 'list_dir', 'grep_search', 'file_search']`
14. `.github/skills/tavily/SKILL.md` → `tools: ['tavily/tavily_search', 'tavily/tavily_extract', 'tavily/tavily_crawl', 'tavily/tavily_map', 'tavily/tavily_research', 'context-mode/ctx_search']`
15. `.github/skills/terminal-governance/SKILL.md` → `tools: ['run_in_terminal']`

### 2.2 Frente 2 — Tabela De-Para Completa dos 44 Planos em `docs/plans/<tipo>/`

Padrão canônico alvo:
- Subpastas gerais (`architecture`, `bug-triage`, `feature`, `governance`, `refactor`, `requirements`, `test-strategy`): `AAAAMMDD-HHMMSS-<slug>.md`
- Subpasta `implementation/` (para planos recentes sob D5): `AAAAMMDD-HHMMSS-<workflow>-<slug>.md`

| # | Subpasta | Arquivo Atual (`docs/plans/<subpasta>/...`) | `created_at` | Novo Arquivo Canônico (`AAAAMMDD-HHMMSS-...`) |
|---|---|---|---|---|
| 1 | `architecture` | `agent-profiles-taxonomy.md` | 2026-08-30 | `20260830-090000-agent-profiles-taxonomy.md` |
| 2 | `architecture` | `categorizacao-agents-mercado.md` | 2026-08-30 | `20260830-090100-categorizacao-agents-mercado.md` |
| 3 | `architecture` | `plano-grafico-invocacao-agents.md` | 2026-08-30 | `20260830-090200-plano-grafico-invocacao-agents.md` |
| 4 | `architecture` | `plano-motor-migracao-agnostica.md` | 2026-08-30 | `20260830-090300-plano-motor-migracao-agnostica.md` |
| 5 | `architecture` | `proposta-orquestracao-langchain.md` | 2026-08-30 | `20260830-090400-proposta-orquestracao-langchain.md` |
| 6 | `architecture` | `analise-arquitetura-multi-agent-alinhamento.md` | 2026-09-02 | `20260902-090000-analise-arquitetura-multi-agent-alinhamento.md` |
| 7 | `bug-triage` | `20261002-bugfix-mcp-tools-headless-sdk.md` | 2026-10-02 | `20261002-090000-bugfix-mcp-tools-headless-sdk.md` |
| 8 | `bug-triage` | `20261003-bugfix-anti-truncamento-changelog-hook-falso-positivo.md` | 2026-10-03 | `20261003-090000-bugfix-anti-truncamento-changelog-hook-falso-positivo.md` |
| 9 | `bug-triage` | `20261004-bugfix-shell-permission-persistente-logging-arquivo.md` | 2026-10-04 | `20261004-090000-bugfix-shell-permission-persistente-logging-arquivo.md` |
| 10 | `feature` | `20261001-feature-development-governance-runner-sdk-integration.md` | 2026-10-01 | `20261001-090000-feature-development-governance-runner-sdk-integration.md` |
| 11 | `governance` | `PLAN-slash-prompts-router-bypass.md` | 2026-04-20 | `20260420-090000-slash-prompts-router-bypass.md` |
| 12 | `governance` | `plano-otimizacao-catalogo-agents.md` | 2026-08-30 | `20260830-090000-plano-otimizacao-catalogo-agents.md` |
| 13 | `governance` | `20260927-governance-maintenance-session-checkpoint-recovery.md` | 2026-09-27 | `20260927-090000-governance-maintenance-session-checkpoint-recovery.md` |
| 14 | `governance` | `20260927-workflow-governance-maintenance-prompt-synthesis-redesign.md` | 2026-09-27 | `20260927-090100-workflow-governance-maintenance-prompt-synthesis-redesign.md` |
| 15 | `governance` | `20260929-governance-maintenance-harness-bloat-audit.md` | 2026-09-29 | `20260929-090000-governance-maintenance-harness-bloat-audit.md` |
| 16 | `governance` | `20261003-governance-maintenance-ctx-execute-profile-classification.md` | 2026-10-03 | `20261003-090000-governance-maintenance-ctx-execute-profile-classification.md` |
| 17 | `governance` | `20261003-governance-maintenance-progressive-disclosure-source-docs.md` | 2026-10-03 | `20261003-090100-governance-maintenance-progressive-disclosure-source-docs.md` |
| 18 | `governance` | `20261005-gov-import-harness-eval.md` | 2026-10-05 | `20261005-090000-gov-import-harness-eval.md` |
| 19 | `governance` | `20261005-gov-retrofit-harness-eval-and-skill-creation-flow.md` | 2026-10-05 | `20261005-090100-gov-retrofit-harness-eval-and-skill-creation-flow.md` |
| 20 | `governance` | `20261006-governance-maintenance-consolidacao-agents-stacks.md` | 2026-10-06 | `20261006-090000-governance-maintenance-consolidacao-agents-stacks.md` |
| 21 | `governance` | `PLAN-padronizacao-templates-agents-prompts-skills-5-ondas.md` | 2026-10-06 | `20261006-090100-padronizacao-templates-agents-prompts-skills-5-ondas.md` |
| 22 | `governance` | `20261112-governance-maintenance-ask-questions-ux-standardization.md` | 2026-11-12 | `20261112-090000-governance-maintenance-ask-questions-ux-standardization.md` |
| 23 | `governance` | `20261112-governance-maintenance-r064-failclosed-hardstop.md` | 2026-11-12 | `20261112-090100-governance-maintenance-r064-failclosed-hardstop.md` |
| 24 | `governance` | `20261112-governance-maintenance-universal-plan-materialization.md` | 2026-11-12 | `20261112-090200-governance-maintenance-universal-plan-materialization.md` |
| 25 | `implementation` | `plano-implementacao-orquestracao.md` | 2026-08-30 | `20260830-090000-architecture-plano-implementacao-orquestracao.md` |
| 26 | `implementation` | `20260927-governance-maintenance-session-checkpoint-recovery.md` | 2026-09-27 | `20260927-090000-governance-maintenance-session-checkpoint-recovery.md` |
| 27 | `implementation` | `20260927-workflow-governance-maintenance-prompt-synthesis-redesign.md` | 2026-09-27 | `20260927-090100-workflow-governance-maintenance-prompt-synthesis-redesign.md` |
| 28 | `implementation` | `20260929-feature-development-local-chat-gateway-mvp.md` | 2026-09-29 | `20260929-090000-feature-development-local-chat-gateway-mvp.md` |
| 29 | `implementation` | `20261001-feature-development-governance-runner-sdk-integration.md` | 2026-10-01 | `20261001-090000-feature-development-governance-runner-sdk-integration.md` |
| 30 | `implementation` | `20261002-bugfix-mcp-tools-headless-sdk.md` | 2026-10-02 | `20261002-090000-bugfix-mcp-tools-headless-sdk.md` |
| 31 | `implementation` | `20261003-governance-maintenance-ctx-execute-profile-classification.md` | 2026-10-03 | `20261003-090000-governance-maintenance-ctx-execute-profile-classification.md` |
| 32 | `implementation` | `20261003-governance-maintenance-progressive-disclosure-source-docs.md` | 2026-10-03 | `20261003-090100-governance-maintenance-progressive-disclosure-source-docs.md` |
| 33 | `implementation` | `20261004-bugfix-shell-permission-persistente-logging-arquivo.md` | 2026-10-04 | `20261004-090000-bugfix-shell-permission-persistente-logging-arquivo.md` |
| 34 | `implementation` | `20261005-gov-import-harness-eval.md` | 2026-10-05 | `20261005-090000-gov-import-harness-eval.md` |
| 35 | `implementation` | `20261005-gov-retrofit-harness-eval-and-skill-creation-flow.md` | 2026-10-05 | `20261005-090100-gov-retrofit-harness-eval-and-skill-creation-flow.md` |
| 36 | `implementation` | `20261006-react-consolidation.md` | 2026-10-06 | `20261006-090000-react-consolidation.md` |
| 37 | `implementation` | `20261006-spring-boot-consolidation.md` | 2026-10-06 | `20261006-090100-spring-boot-consolidation.md` |
| 38 | `implementation` | `PLAN-padronizacao-templates-agents-prompts-skills-5-ondas.md` | 2026-10-06 | `20261006-090200-governance-padronizacao-templates-agents-prompts-skills-5-ondas.md` |
| 39 | `implementation` | `20261008-feature-development-embedded-maven-runtime.md` | 2026-10-08 | `20261008-090000-feature-development-embedded-maven-runtime.md` |
| 40 | `implementation` | `20261008-feature-development-embedded-python-runtime.md` | 2026-10-08 | `20261008-090100-feature-development-embedded-python-runtime.md` |
| 41 | `implementation` | `20261008-feature-development-poc-frontend-login-playwright.md` | 2026-10-08 | `20261008-090200-feature-development-poc-frontend-login-playwright.md` |
| 42 | `implementation` | `20261008-governance-maintenance-playwright-mcp-frontend-consolidation.md` | 2026-10-08 | `20261008-090300-governance-maintenance-playwright-mcp-frontend-consolidation.md` |
| 43 | `implementation` | `20261010-feature-development-model-profiles-allowlist.md` | 2026-10-10 | `20261010-090000-feature-development-model-profiles-allowlist.md` |
| 44 | `requirements` | `REQ-migration-engine.md` | 2026-08-30 | `20260830-090000-migration-engine.md` |

> **Nota sobre os próprios planos desta manutenção**:
> - `docs/plans/governance/20261113-120000-tools-inline-e-timestamp-hhmmss-plans.md` (já nasce no formato `AAAAMMDD-HHMMSS-<slug>.md`)
> - `docs/plans/implementation/20261113-120000-governance-tools-inline-e-timestamp-hhmmss-plans.md` (será normalizado na onda de execução para `20261113-120000-governance-maintenance-tools-inline-e-timestamp-hhmmss-plans.md` se a regra D5 de slug completo de workflow for mantida, ou `governance` será aceito como alias canônico).

---

## 3. Plano de Correção em Lote (Plan-Then-Batch)

- **Onda 1 (Frente 1 — Inline Tools Array)**: Script único em `ctx_execute (language: "javascript")` convertendo os 5 `.prompt.md` e 10 `SKILL.md` para `tools: ['...']` inline (incluindo realocação do bloco `tools:` de `project-context-builder/SKILL.md` das linhas 50–55 para o frontmatter principal).
- **Onda 2 (Frente 2 — Renomeação dos 44 Planos + Sincronização de Referências)**: Renomeação atômica dos 44 arquivos em `docs/plans/<tipo>/` e atualização em lote de todos os campos `related-planning-doc`, `plan_ref` e links cruzados em `docs/`, `.github/` e `tests/`.
- **Onda 3 (Templates, Documentação e Sensores Pytest)**: Atualização das convenções de nomenclatura `AAAAMMDD-HHMMSS-*` nas skills/templates de plano (`plan-frontmatter-r064.md`, `plan-template-*.md`, `docs/plans/README.md`, `docs/plans/implementation/README.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, workflows/agents) e nos testes `tests/governance_audit/test_planning_doc_template_governance.py` + novo teste de formato inline `tools:` para prompts e skills.

---

## 4. Alternativas Rejeitadas

1. **Manter `AAAAMMDD-<slug>.md` sem `HHMMSS` e usar sufixo numérico opcional (`-v2`)**: Rejeitada — não impõe ordenação cronológica lexicográfica determinística quando vários planos de escopos distintos são criados no mesmo dia (ex.: 3 planos em `20261112`).
2. **Permitir `tools:` multiline em `SKILL.md` e exigir inline apenas em `.agent.md`**: Rejeitada — parsers regex leves da suíte de auditoria (como `_extract_tools` em `test_ctx_execute_capability_profile.py`) e o contrato de criação de artefatos operam de forma uniforme sobre `tools: ['...']` em linha única.
3. **Renomear apenas planos novos daqui para frente (deixando os 44 legados intocados)**: Rejeitada — perpetua dívida técnica, exceções `LEGACY_MIGRATED_PLANS` nos testes e quebra a invariante uniforme em `docs/plans/<tipo>/`.

---

## 5. Reúso Sistêmico (R-055: Q1/Q2/Q3) e Sensores `tests/governance_audit/`

- **Q1 (Artefatos Irmãos/Peers)**: Verificados todos os `.agent.md`, `.prompt.md` e `SKILL.md` do repositório, bem como todos os 44 planos nas 8 subpastas de `docs/plans/`.
- **Q2 (Templates Canônicos)**: Atualização prevista nos templates de plano em `.github/skills/*/references/plan-template-*.md`, `docs/plans/README.md`, `docs/plans/implementation/README.md` e instruções globais.
- **Q3 (Sensores Determinísticos Pytest)**:
  - Atualização de `PLAN_NAME_PATTERN` em `tests/governance_audit/test_planning_doc_template_governance.py` para exigir `^\d{8}-\d{6}-[a-z0-9]+(-[a-z0-9]+)*\.md$` em todas as 8 subpastas de `docs/plans/` e remover `LEGACY_MIGRATED_PLANS`.
  - Adição de asserção determinística garantindo que todo campo `tools:` presente em frontmatter de `.agent.md`, `.prompt.md` e `SKILL.md` utilize formato inline array `tools: [...]`.

---

## 6. Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)

- **Integridade Referencial (Dangling Links)**: A renomeação em lote de 44 arquivos de planos pode quebrar referências em `related-planning-doc`, `plan_ref` e docstrings de testes (`test_ctx_execute_capability_profile.py`, `test_playwright_mcp_frontend_governance.py`, `test_universal_plan_materialization_governance.py`). Mitigação: substituir atomicamente todas as ocorrências do caminho antigo pelo novo em todo o workspace e validar com `test_universal_plan_materialization_governance.py`.
- **Isolamento de Projeto Local (R-038 / R-044)**: Nenhum identificador de projeto local é introduzido nos novos nomes.

---

## 7. Rollback e Critério de Pronto

- **Rollback**: Reversão integral via `git checkout -- .` / restauração do mapa De-Para em script único caso qualquer teste da suíte `pytest tests/governance_audit/` falhe.
- **Critério de Pronto (DoD)**:
  - [ ] Frontmatter R-064 completo (`plan_type: governance`) e aprovado pelo usuário.
  - [ ] 15 arquivos (5 prompts + 10 skills) convertidos para `tools: [...]` inline no frontmatter principal.
  - [ ] 44 planos renomeados para `AAAAMMDD-HHMMSS-*` com 100% das referências cruzadas atualizadas.
  - [ ] Suíte `pytest tests/governance_audit/` 100% verde e `get_errors` sem erros.
