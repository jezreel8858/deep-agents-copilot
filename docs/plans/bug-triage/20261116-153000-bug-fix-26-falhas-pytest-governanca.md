---
plan_id: "20261116-153000-bug-fix-26-falhas-pytest-governanca"
status: "APPROVED"
approved: true
author: "@bug-triage"
materialized_by: "@docs-engineer"
plan_type: "bug-triage"
workflow: "WORKFLOW-BUG-FIX"
created_at: "2026-11-16"
updated_at: "2026-11-16"
session_id: "sess-20261116-153000-bugfix-pytest"
workflow_id: "WORKFLOW-BUG-FIX"
workflow_trace_id: "wf-bugfix-20261116-153000"
parent_plan_ref: "N/A — plano raiz"
related-planning-doc: "N/A"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: "PASS"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  high: 0
  medium: 0
  majors: 0
  minors: 0
  nits: 3
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@bug-triage"
allowed_files:
  - "docs/plans/architecture/20261115-100000-synth-routing-eval-sqlite.md"
  - "docs/plans/governance/20261116-141000-governance-maintenance-preflight-c10-sync.md"
  - "docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md"
  - "docs/plans/implementation/20261116-120500-bug-fix-synth-waves-timeout.md"
  - "docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md"
  - "docs/plans/implementation/20261116-130500-governance-maintenance-pre-commit-r044-tb34-fix-python-tests.md"
  - ".github/agents/workflows.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - ".github/agents/workflows/workflow-bug-fix.md"
  - ".github/agents/workflows/workflow-dependency-vulnerability-remediation.md"
  - ".github/agents/workflows/workflow-feature-development.md"
  - ".github/agents/workflows/workflow-framework-migration.md"
  - ".github/agents/workflows/workflow-governance-maintenance.md"
  - ".github/agents/workflows/workflow-prompt-synthesis.md"
  - ".github/agents/workflows/workflow-refactoring.md"
  - ".github/agents/workflows/workflow-release-readiness.md"
  - ".github/agents/workflows/workflow-technical-analysis.md"
  - ".github/agents/workflows/workflow-ui-layout.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/deep-search.agent.md"
  - ".github/skills/handoff-governance/SKILL.md"
  - ".github/agents/evals/casos-roteamento.yaml"
  - "tests/governance_audit/_helpers.py"
  - "tests/context_insight_visualizer/test_agent_invocations.py"
  - "CLAUDE.md"
  - "README.md"
  - "docs/repo-map.md"
  - "docs/plans/architecture/20261115-140000-synth-routing-graph-diagnostics.md"
  - "docs/plans/architecture/20261115-170000-synth-workflow-triggers-diagnostics.md"
  - "docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md"
  - "docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md"
  - "docs/plans/governance/20261115-120000-guardrails-agency-score-regression.md"
  - "docs/plans/governance/20261115-120000-workflow-governance-maintenance-arch-advisor-post-plan-gate.md"
  - "docs/plans/governance/20261115-120000-workflows-parity-remediation.md"
  - "docs/plans/governance/20261115-160000-routing-graph-drift-and-gaps-remediation.md"
  - "docs/plans/governance/20261115-183000-synth-waves-prompt.md"
  - "docs/plans/governance/20261116-120000-eval-workflows-prompt-melhorias.md"
  - "docs/plans/governance/20261116-120000-governance-maintenance-changelog-concisao.md"
  - "docs/plans/governance/20261116-120000-governance-maintenance-quality-gate-pos-execucao.md"
  - "docs/plans/governance/20261116-120000-vscode-mcp-config-sync.md"
  - "docs/plans/governance/20261116-123000-pre-commit-r044-tb34-fix.md"
  - "docs/plans/implementation/20261115-110000-feature-synth-routing-eval-sqlite.md"
  - "docs/plans/implementation/20261115-150000-feature-synth-routing-graph-diagnostics.md"
  - "docs/plans/implementation/20261115-173000-feature-synth-workflow-triggers-diagnostics.md"
  - "docs/plans/implementation/20261116-123000-governance-maintenance-sensor-q3-post-execution.md"
  - "docs/plans/implementation/20261116-130000-governance-maintenance-test-upstream-rca-gate.md"
  - "docs/plans/implementation/20261116-142000-governance-maintenance-preflight-c10-sensor-q3.md"
blast_radius: "Restrito a metadados de planos em docs/plans/governance, docs/plans/implementation e docs/plans/bug-triage, contratos de workflows (.github/agents/workflows.md e .github/agents/workflows/workflow-*.md), agents (.github/agents/tech-solution-architect.agent.md e .github/agents/deep-search.agent.md), skill .github/skills/handoff-governance/SKILL.md, testes de auditoria pytest e artefatos derivados do governance_sync (CLAUDE.md, README.md, docs/repo-map.md)"
rollback_plan: "Reverter alteracoes por grupo via git restore --staged --worktree nos arquivos modificados (G1: docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md; G2: .github/agents/workflows.md, .github/agents/workflows/*.md, CLAUDE.md, README.md, docs/repo-map.md; G3: .github/agents/tech-solution-architect.agent.md e tests/context_insight_visualizer/test_agent_invocations.py; G4: .github/skills/handoff-governance/SKILL.md; G5: tests/governance_audit/_helpers.py; G6: .github/agents/deep-search.agent.md; G7: .github/agents/evals/casos-roteamento.yaml e docs/plans/implementation/20261116-130500-governance-maintenance-pre-commit-r044-tb34-fix-python-tests.md) e reverter os renames de G7 com git mv docs/plans/implementation/20261116-120500-bug-fix-synth-waves-timeout.md docs/plans/implementation/20261116-120500-bugfix-synth-waves-timeout.md e git mv docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md"
lessons_learned: "Garantir citacao de strings com dois-pontos em frontmatter YAML, listar exclusivamente caminhos existentes sem globs em allowed_files, respeitar teto R-066 de 300 linhas em SKILL.md e usar prefixo canonico bug-fix- em planos recentes"
lessons_extracted: false
lessons_applied_to: []
lessons_at: "2026-11-16"
---

# Plano de Triagem e Correcao de Bugs: 26 Falhas na Suite Pytest de Governanca

## 1. Contexto e Sintoma Reportado

A execucao da suite de auditoria de governanca (`pytest tests/governance_audit tests/context_insight_visualizer`) apresentou **26 falhas** distribuidas em **7 grupos de causa raiz (G1 a G7)**, abrangendo erro de sintaxe YAML em frontmatter de plano recente, divergencias de paridade em `.github/agents/workflows.md` e `.github/agents/workflows/workflow-*.md`, caminho legado em `test_agent_invocations.py` e contrato pos-materializacao em `tech-solution-architect.agent.md`, estouro do teto R-066 em `handoff-governance/SKILL.md`, varredura indevida de artefatos sinteticos em `.github/agents/evals/synthetic/*.md`, mencao indevida a `ctx_execute` no corpo de `deep-search.agent.md` e convencao de prefixo/threshold em planos `bugfix-synth-waves-timeout.md` e `casos-roteamento.yaml`.

---

## 2. Agrupamento de Causa Raiz (RCA) — G1 a G7

| Grupo | Qtd. Falhas | IDs das Falhas | Alvo Principal | Evidencia de Falha (Teste + Linha + Assert) |
|---|---|---|---|---|
| **G1** | 7 | 14, 15, 16, 17, 19, 20, 21 | `docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md` | Linha 31: `rollback_plan` com string escalar contendo aspas/dois-pontos quebrando o bloco YAML na linha 30 col 1 (`yaml.parser.ParserError`). |
| **G2** | 7 | 4, 5, 6, 7, 8, 24, 25 | `.github/agents/workflows.md`, `.github/agents/workflows/workflow-governance-maintenance.md`, `.github/agents/workflows/workflow-framework-migration.md` | `test_r064_arch_advisor_gate.py:178`, `test_markdown_ssot_counts_and_mermaid_sync.py:97,108,114`, `test_migration_engine_governance.py:370`, `test_operational_workflows.py:294,456`. |
| **G3** | 2 | 1, 3 | `tests/context_insight_visualizer/test_agent_invocations.py` e `.github/agents/tech-solution-architect.agent.md` | `test_agent_invocations.py:237` (`FileNotFoundError: .github/agents/architecture/tech-solution-architect.agent.md`) e `test_agent_guardrails_regression.py:270` (ausencia de `PASS_WITH_NITS`). |
| **G4** | 3 | 13, 22, 23 | `.github/skills/handoff-governance/SKILL.md` | `test_r066_progressive_disclosure_budget.py:316` e `test_otel_handoff_hydration_governance.py` (`AssertionError: R-066 violado: handoff-governance/SKILL.md tem 304 linhas (> 300)`). |
| **G5** | 4 | 9, 10, 11, 12 | `tests/governance_audit/_helpers.py` | `test_model_allowlist_governance.py` e `test_model_profiles_parity.py` via `tests/governance_audit/_helpers.py:168` (`AssertionError: Varredura de frontmatter falhou para 16 arquivo(s)` em `.github/agents/evals/synthetic/*.md`). |
| **G6** | 1 | 2 | `.github/agents/deep-search.agent.md` | `test_governance_smells.py:878` (`test_agent_tools_cover_body_context_mode_invocations` falha para `.github/agents/deep-search.agent.md`). |
| **G7** | 2 | 18, 26 | `docs/plans/implementation/20261116-120500-bugfix-synth-waves-timeout.md`, `docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md`, `.github/agents/evals/casos-roteamento.yaml` | `test_planning_doc_template_governance.py:303` (`Planos recentes sem prefixo de workflow`) e `test_routing_quality_gate.py:160` (`threshold >= 0.85 (atual: 0.0)` em `casos-roteamento.yaml:1490`). |

---

## 3. Detalhamento Tecnico por Grupo e Estrategia de Correcao Deterministica

### 3.1. Grupo G1 — Correcao de Frontmatter YAML em Plano de Governanca (7 falhas: 14, 15, 16, 17, 19, 20, 21)

- **Arquivo afetado**: `docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md`
- **Evidencia exata de falha**: Linha 31 do arquivo possui `rollback_plan` com string escalar contendo aspas e dois-pontos que quebram o bloco YAML na linha 30 coluna 1 (`yaml.parser.ParserError`).
- **Comando de reproducao**: `pytest tests/governance_audit/test_r064_otel_correlation_fields.py -k test_all_existing_plans_pass_v2_frontmatter_validation -q`
- **Hipotese descartada**: Erro no parser `yaml.safe_load` dos testes (descartada pois os demais planos passam integralmente na validacao v2).
- **Decisao tecnica unica**: Substituir o valor escalar quebrado de `rollback_plan` na linha 31 de `docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md` por uma string entre aspas duplas validas sem aspas internas nao escapadas, garantindo parse limpo via `yaml.safe_load`.

### 3.2. Grupo G2 — Paridade de Workflows e Sincronizacao SSOT (7 falhas: 4, 5, 6, 7, 8, 24, 25)

- **Arquivos afetados**:
  - `.github/agents/workflows.md`
  - `.github/agents/workflows/workflow-governance-maintenance.md`
  - `.github/agents/workflows/workflow-framework-migration.md`
  - Artefatos sincronizados por `python -m tools.governance_sync`: `CLAUDE.md`, `README.md`, `docs/repo-map.md` e `.github/agents/workflows/workflow-*.md`.
- **Evidencias exatas de falha**:
  1. `test_r064_arch_advisor_gate.py:178` — `AssertionError: Etapa 'implementation_plan_authoring' ausente no workflow WORKFLOW-GOVERNANCE-MAINTENANCE`.
  2. `test_markdown_ssot_counts_and_mermaid_sync.py:97,108,114` — `plan-critic ausente nos blocos mermaid de .github/agents/workflows.md` e `governance_sync --check` retornando exit code `1`.
  3. `test_migration_engine_governance.py:370` — `AssertionError: Estado 6 deve estar detalhado na cadeia sequencial`.
  4. `test_operational_workflows.py:294,456` — `assert 3 >= 6` para `Loop de Revisão de Qualidade (§ 1.5)` e `workflows.md deve especificar pesquisa prévia`.
- **Comando de reproducao**: `pytest tests/governance_audit/test_r064_arch_advisor_gate.py tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py tests/governance_audit/test_migration_engine_governance.py tests/governance_audit/test_operational_workflows.py -q`
- **Hipotese descartada**: Testes desatualizados em relacao a governanca (descartada pois `.github/agents/workflows.md` foi truncado e dessincronizado nos commits recentes `e3e8d7a` e `a53afe2`).
- **Decisao tecnica unica**:
  1. Restaurar nos blocos Mermaid de `.github/agents/workflows.md` a presenca explicita do no `plan-critic` em todos os workflows auditados.
  2. Declarar a etapa `implementation_plan_authoring` e os requisitos de pesquisa previa e sincronizacao quadrupla SSOT em `WORKFLOW-GOVERNANCE-MAINTENANCE` (`.github/agents/workflows.md` e `.github/agents/workflows/workflow-governance-maintenance.md`).
  3. Detalhar `Estado 6 — Post-Migration Verification & Redundancy Gate` na cadeia sequencial do WF7 (`.github/agents/workflows.md` e `.github/agents/workflows/workflow-framework-migration.md`).
  4. Garantir a referencia textual `Loop de Revisão de Qualidade (§ 1.5)` em pelo menos 6 workflows em `.github/agents/workflows.md` e seus respectivos arquivos em `.github/agents/workflows/workflow-*.md`.
  5. Executar `python -m tools.governance_sync` para sincronizar `CLAUDE.md`, `README.md` e `docs/repo-map.md` ate que `python -m tools.governance_sync --check` retorne `0`.

### 3.3. Grupo G3 — Caminho Canonico e Contrato Pos-Materializacao no Tech Solution Architect (2 falhas: 1, 3)

- **Arquivos afetados**:
  - `tests/context_insight_visualizer/test_agent_invocations.py`
  - `.github/agents/tech-solution-architect.agent.md`
- **Evidencias exatas de falha**:
  1. `test_agent_invocations.py:237` — `FileNotFoundError: .github/agents/architecture/tech-solution-architect.agent.md`.
  2. `test_agent_guardrails_regression.py:270` — `tech-solution-architect.agent.md` nao menciona `PASS_WITH_NITS` no contrato pos-plano.
- **Comando de reproducao**: `pytest tests/context_insight_visualizer/test_agent_invocations.py tests/governance_audit/test_agent_guardrails_regression.py -k "tech_solution_architect or post_plan" -q`
- **Hipotese descartada**: Mover o agent para a subpasta `.github/agents/architecture/` (descartada pois todos os 63 agents canônicos residem na estrutura plana `.github/agents/*.agent.md`).
- **Decisao tecnica unica**: Atualizar `tests/context_insight_visualizer/test_agent_invocations.py:237` para apontar para `.github/agents/tech-solution-architect.agent.md` e adicionar `PASS_WITH_NITS` explicitamente na clausula de revisao pos-materializacao (`@docs-engineer` -> `@plan-critic`) em `.github/agents/tech-solution-architect.agent.md`.

### 3.4. Grupo G4 — Compactacao de `handoff-governance/SKILL.md` sob Teto R-066 (3 falhas: 13, 22, 23)

- **Arquivo afetado**: `.github/skills/handoff-governance/SKILL.md`
- **Evidencia exata de falha**: `test_r066_progressive_disclosure_budget.py:316` e `test_otel_handoff_hydration_governance.py` — `AssertionError: R-066 violado: handoff-governance/SKILL.md tem 304 linhas (> 300)`.
- **Comando de reproducao**: `pytest tests/governance_audit/test_r066_progressive_disclosure_budget.py tests/governance_audit/test_otel_handoff_hydration_governance.py -q`
- **Hipotese descartada**: Elevar o teto R-066 acima de 300 linhas nos testes (descartada por violar a invariante arquitetural de Progressive Disclosure R-066).
- **Decisao tecnica unica**: Compactar 6 linhas redundantes (linhas em branco duplicadas e separadores verbosos) em `.github/skills/handoff-governance/SKILL.md`, reduzindo o arquivo para `<= 298` linhas e mantendo intactas as secoes `CLAUSE_OTEL_PASSTHROUGH`, `CLAUSE_CONTEXT_HYDRATION` e `N/A — pré-plano`.

### 3.5. Grupo G5 — Exclusao de `.github/agents/evals/**` do Scanner de Frontmatter de Agents (4 falhas: 9, 10, 11, 12)

- **Arquivo afetado**: `tests/governance_audit/_helpers.py`
- **Evidencia exata de falha**: `test_model_allowlist_governance.py` e `test_model_profiles_parity.py` via `tests/governance_audit/_helpers.py:168` — `AssertionError: Varredura de frontmatter falhou para 16 arquivo(s)` em `.github/agents/evals/synthetic/*.md`.
- **Comando de reproducao**: `pytest tests/governance_audit/test_model_allowlist_governance.py tests/governance_audit/test_model_profiles_parity.py -q`
- **Hipotese descartada**: Adicionar frontmatter de agent (`model`, `tools`, `description`) aos 16 arquivos markdown em `.github/agents/evals/synthetic/` (descartada pois `evals/synthetic/` contem relatorios diagnosticos de ondas sinteticas e `README.md` de evals, nao definicoes de agents ou prompts).
- **Decisao tecnica unica**: Excluir `.github/agents/evals/**` da varredura de frontmatter de agents em `tests/governance_audit/_helpers.py` (ao redor da linha 168), garantindo que apenas arquivos de definicao de agents/prompts reais sejam inspecionados.

### 3.6. Grupo G6 — Alinhamento de Tools Context-Mode no Corpo de `deep-search.agent.md` (1 falha: 2)

- **Arquivo afetado**: `.github/agents/deep-search.agent.md`
- **Evidencia exata de falha**: `test_governance_smells.py:878` (`test_agent_tools_cover_body_context_mode_invocations` falha para `.github/agents/deep-search.agent.md` porque o corpo menciona `ctx_execute` sem que a tool conste no frontmatter Gather-only).
- **Comando de reproducao**: `pytest tests/governance_audit/test_governance_smells.py -k test_agent_tools_cover_body_context_mode_invocations -q`
- **Hipotese descartada**: Conceder `context-mode/ctx_execute` no frontmatter de `deep-search.agent.md` (descartada pois `@deep-search` possui perfil estrito Gather-only restrito a `ctx_batch`, `ctx_search`, `ctx_index` e `ctx_fetch_and_index`).
- **Decisao tecnica unica**: Substituir as mencoes a `ctx_execute` no corpo de `.github/agents/deep-search.agent.md` por `ctx_batch` e `ctx_search`, preservando o perfil Gather-only do agent.

### 3.7. Grupo G7 — Rename para Prefixo Canonico `bug-fix-` e Threshold Silver em `casos-roteamento.yaml` (2 falhas: 18, 26)

- **Arquivos afetados (existentes antes da mutacao)**:
  1. `docs/plans/implementation/20261116-120500-bugfix-synth-waves-timeout.md`
  2. `docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md`
  3. `docs/plans/implementation/20261116-130500-governance-maintenance-pre-commit-r044-tb34-fix-python-tests.md`
  4. `.github/agents/evals/casos-roteamento.yaml`
- **Alvos de rename (caminhos de destino apos `git mv`)**:
  - `docs/plans/implementation/20261116-120500-bugfix-synth-waves-timeout.md` -> `docs/plans/implementation/20261116-120500-bug-fix-synth-waves-timeout.md`
  - `docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md` -> `docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md`
- **Evidencias exatas de falha**:
  1. `test_planning_doc_template_governance.py:303` — `Planos recentes sem prefixo de workflow`: `docs/plans/implementation/20261116-120500-bugfix-synth-waves-timeout.md` e `docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md` usam `bugfix-` em vez de `bug-fix-`.
  2. `test_routing_quality_gate.py:160` — `Caso 'promoted-silver-0d00b0e0b8ca' deve ter threshold >= 0.85 (atual: 0.0)` em `.github/agents/evals/casos-roteamento.yaml:1490`.
- **Comando de reproducao**: `pytest tests/governance_audit/test_planning_doc_template_governance.py tests/governance_audit/test_routing_quality_gate.py -q`
- **Hipotese descartada**: Alterar a regex de prefixos de workflow em `test_planning_doc_template_governance.py` para aceitar `bugfix-` sem hifen (descartada pois o identificador canonico do workflow e `WORKFLOW-BUG-FIX` -> prefixo `bug-fix-`).
- **Decisao tecnica unica**:
  1. Renomear via `git mv` os arquivos `docs/plans/implementation/20261116-120500-bugfix-synth-waves-timeout.md` para `docs/plans/implementation/20261116-120500-bug-fix-synth-waves-timeout.md` e `docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md` para `docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md`, atualizando as referencias cruzadas internas entre ambos (`parent_plan_ref`, `related-planning-doc`) e em `docs/plans/implementation/20261116-130500-governance-maintenance-pre-commit-r044-tb34-fix-python-tests.md`.
  2. Definir `threshold: 0.85` no caso `promoted-silver-0d00b0e0b8ca` na linha 1490 de `.github/agents/evals/casos-roteamento.yaml` (padrao canonico de regressao silver em `casos-roteamento.yaml`).

---

## 4. Criterios de Aceite e Verificacao

1. Frontmatter YAML de todos os planos em `docs/plans/**` valido sem erros de parser (`test_all_existing_plans_pass_v2_frontmatter_validation` passando).
2. Suite completa `pytest tests/governance_audit tests/context_insight_visualizer` passando com **0 falhas** nas 26 assercoes mapeadas (G1 a G7).
3. `python -m tools.governance_sync --check` retornando exit code `0`.
4. `.github/skills/handoff-governance/SKILL.md` com `<= 298` linhas e preservando `CLAUSE_OTEL_PASSTHROUGH` e `CLAUSE_CONTEXT_HYDRATION`.

---

## 5. Alternativas Rejeitadas

1. **Desabilitar ou marcar com `@pytest.mark.skip` os 26 testes falhos**: Rejeitado por violar as invariantes de auditoria deterministica (R-051/R-064) e mascarar desvios reais de governanca e sincronizacao SSOT.
2. **Aumentar o teto global de linhas R-066 (> 300 linhas) para acomodar `handoff-governance/SKILL.md`**: Rejeitado porque o limite de 300 linhas e uma invariante arquitetural de Progressive Disclosure (R-066) e o excesso de 4 linhas (304 vs 300) e resolvido compactando 6 linhas redundantes (`<= 298` linhas) sem perda semantica.
3. **Remover os arquivos de `.github/agents/evals/synthetic/*.md`**: Rejeitado pois sao relatorios diagnosticos de avaliacao sintetica; a correcao deterministica e excluir `.github/agents/evals/**` do scanner de frontmatter de agents em `tests/governance_audit/_helpers.py`.

---

## 6. Plano de Teste de Regressao e Rollback Detalhado

### 6.1. Comandos de Verificacao de Regressao

1. Validar frontmatter YAML v2 e templates de planos:
   `pytest tests/governance_audit/test_r064_otel_correlation_fields.py tests/governance_audit/test_planning_doc_template_governance.py -q`
2. Validar sincronizacao SSOT:
   `python -m tools.governance_sync --check`
3. Executar todos os testes dos grupos G1 a G7:
   `pytest tests/governance_audit tests/context_insight_visualizer/test_agent_invocations.py -q`

### 6.2. Procedimento de Rollback por Grupo (Git Restore + Git MV)

Caso qualquer regressao seja detectada apos a aplicacao de um grupo, executar a reversao isolada correspondente:

- **G1**: `git restore --staged --worktree docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md`
- **G2**: `git restore --staged --worktree .github/agents/workflows.md .github/agents/workflows/ CLAUDE.md README.md docs/repo-map.md`
- **G3**: `git restore --staged --worktree .github/agents/tech-solution-architect.agent.md tests/context_insight_visualizer/test_agent_invocations.py`
- **G4**: `git restore --staged --worktree .github/skills/handoff-governance/SKILL.md`
- **G5**: `git restore --staged --worktree tests/governance_audit/_helpers.py`
- **G6**: `git restore --staged --worktree .github/agents/deep-search.agent.md`
- **G7**:
  1. `git mv docs/plans/implementation/20261116-120500-bug-fix-synth-waves-timeout.md docs/plans/implementation/20261116-120500-bugfix-synth-waves-timeout.md`
  2. `git mv docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md`
  3. `git restore --staged --worktree docs/plans/implementation/20261116-120500-bugfix-synth-waves-timeout.md docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md docs/plans/implementation/20261116-130500-governance-maintenance-pre-commit-r044-tb34-fix-python-tests.md .github/agents/evals/casos-roteamento.yaml`

---

## 7. Parecer do Revisor Cetico Pre-HITL (R-064)

- **Rodada 1/2 — Tier 1 (Deterministico)**: `FAIL` (`T1-2`, `T1-5`)
- **Rodada 1/2 — Tier 2 (`@plan-critic`)**: `NEEDS_REVISION` (`review_rounds: 1`, 1 BLOCKER, 3 HIGH, 2 MEDIUM, 1 LOW — enderecados na revisao do plano)
- **Rodada 2/2 — Tier 1 (Deterministico)**: `PASS` (`critic_rubric_gaps: []`)
- **Rodada 2/2 — Tier 2 (`@plan-critic`)**: `PASS_WITH_NITS` (`review_rounds: 2`, `blockers: 0`, `high: 0`, `medium: 0`, `nits: 3` — 3 NITs informativos incorporados; plano apto para Gate de Aprovacao Humana R-064).
