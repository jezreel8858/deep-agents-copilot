---
status: APPROVED
approved: true
author: "@governance-maintainer"
plan_type: "implementation"
created_at: "2026-11-13"
date: "2026-11-13"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
related-planning-doc: "docs/plans/governance/20261113-120000-tools-inline-e-timestamp-hhmmss-plans.md"
plan_ref: "docs/plans/implementation/20261113-120000-governance-tools-inline-e-timestamp-hhmmss-plans.md"
reversibility: "T2"
progress: 0
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

# Plano de Implementação — Padronização de `tools:` Inline Array e Timestamp `AAAAMMDD-HHMMSS` em `docs/plans/`

## Objetivo e Contexto

Executar a manutenção transversal de governança diagnosticada em `docs/plans/governance/20261113-120000-tools-inline-e-timestamp-hhmmss-plans.md`, dividida em duas frentes complementares:
1. **Frente 1 (`tools:` Inline Array)**: Converter todas as declarações `tools:` multiline nos 5 arquivos `.github/prompts/ctx-*.prompt.md` e nos 10 arquivos `.github/skills/*/SKILL.md` para o formato canônico inline array (`tools: ['tool1', 'tool2']`), corrigindo também o posicionamento fora do frontmatter em `.github/skills/project-context-builder/SKILL.md` (linhas 50–55).
2. **Frente 2 (Timestamp `AAAAMMDD-HHMMSS` em `docs/plans/<tipo>/`)**: Padronizar a nomenclatura de todos os 44 planos existentes nas 8 subpastas de `docs/plans/` para `AAAAMMDD-HHMMSS-<slug>.md` (e `AAAAMMDD-HHMMSS-<workflow>-<slug>.md` em `docs/plans/implementation/`), atualizando todas as referências cruzadas (`related-planning-doc`, `plan_ref`, documentação, templates e testes).

---

## Arquivos Afetados (Blast Radius)

- **Prompts (5 arquivos)**:
  - `.github/prompts/ctx-checkpoint.prompt.md`
  - `.github/prompts/ctx-doctor.prompt.md`
  - `.github/prompts/ctx-insight.prompt.md`
  - `.github/prompts/ctx-resume.prompt.md`
  - `.github/prompts/ctx-status.prompt.md`
- **Skills — Frontmatter `tools:` (10 arquivos)**:
  - `.github/skills/business-rules-governance/SKILL.md`
  - `.github/skills/code-tracing/SKILL.md`
  - `.github/skills/context-mode/SKILL.md`
  - `.github/skills/efficient-batch-code-modification/SKILL.md`
  - `.github/skills/git-worktree-governance/SKILL.md`
  - `.github/skills/integration-contract-analysis/SKILL.md`
  - `.github/skills/project-context-builder/SKILL.md`
  - `.github/skills/project-scanner/SKILL.md`
  - `.github/skills/tavily/SKILL.md`
  - `.github/skills/terminal-governance/SKILL.md`
- **Planos em `docs/plans/<tipo>/` (44 arquivos renomeados + 2 planos desta execução)**:
  - `docs/plans/architecture/` (6 arquivos)
  - `docs/plans/bug-triage/` (3 arquivos)
  - `docs/plans/feature/` (1 arquivo)
  - `docs/plans/governance/` (14 arquivos legados + 1 plano atual)
  - `docs/plans/implementation/` (19 arquivos legados + 1 plano atual)
  - `docs/plans/requirements/` (1 arquivo)
- **Templates, Documentação e Sensores de Teste**:
  - `docs/plans/README.md` e `docs/plans/implementation/README.md`
  - `.github/skills/*/references/plan-template-*.md` e `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`
  - `.github/agents/workflows/*.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `CHANGELOG.md`
  - `tests/governance_audit/test_planning_doc_template_governance.py`, `tests/governance_audit/test_ctx_execute_capability_profile.py`, `tests/governance_audit/test_playwright_mcp_frontend_governance.py`, `tests/governance_audit/test_universal_plan_materialization_governance.py`

---

## Seleção de Design Patterns e Justificativa Arquitetural

- **Atomic Batch Mutation Pattern (`efficient-batch-code-modification` / R-059)**: Execução consolidada via script Node.js no sandbox `ctx_execute` para aplicar as transformações de frontmatter, renomeações no filesystem (`fs.renameSync`) e substituição global de referências cruzadas em uma única transação lógica sem estados intermediários quebrados.
- **Lexicographical Timestamp Ordering (`AAAAMMDD-HHMMSS`)**: Garante ordenação cronológica determinística por nome de arquivo mesmo quando múltiplos planos são materializados no mesmo dia.
- **Shift-Left Governance Sensor (R-055 Q3)**: Evolução de `test_planning_doc_template_governance.py` para validar o novo regex `^\d{8}-\d{6}-[a-z0-9]+(-[a-z0-9]+)*\.md$` e o formato inline `tools: [...]` em prompts, skills e agents.

---

## Ondas de Execução (Waves)

- [ ] 1.1 Converter `tools:` multiline para inline array nos 5 prompts e 10 skills (incluindo realocação para o frontmatter principal em `project-context-builder/SKILL.md`) {paralelizavel: false, responsavel: "governance-maintainer"}
- [ ] 2.1 Renomear os 44 planos existentes nas 8 subpastas de `docs/plans/` para o padrão `AAAAMMDD-HHMMSS-*` e atualizar todas as referências cruzadas (`related-planning-doc`, `plan_ref`, links em docs/agents/skills/tests) {paralelizavel: false, responsavel: "governance-maintainer"}
- [ ] 3.1 Atualizar templates canônicos de planos, documentação de governança (`docs/plans/README.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `CHANGELOG.md`) e sensores `tests/governance_audit/test_planning_doc_template_governance.py` {paralelizavel: false, responsavel: "governance-maintainer"}

---

## Checklist Defensivo Pré-Code-Review

- [ ] Nenhum arquivo de código de aplicação fora do domínio de governança é tocado.
- [ ] Todos os campos `related-planning-doc` e `plan_ref` continuam resolvendo para caminhos existentes em disco (`test_universal_plan_materialization_governance.py`).
- [ ] Nenhum identificador proibido de projeto local vaza nos novos nomes de arquivo (`test_nao_deve_conter_identificador_proibido_quando_nome_de_plano`).
- [ ] Nenhum `SKILL.md` excede os limites de linhas da regra R-066.

---

## Estratégia de Testes e Validação

1. Executar `pytest tests/governance_audit/test_planning_doc_template_governance.py tests/governance_audit/test_universal_plan_materialization_governance.py tests/governance_audit/test_ctx_execute_capability_profile.py tests/governance_audit/test_playwright_mcp_frontend_governance.py` via `ctx_execute`.
2. Executar a suíte completa de auditoria `pytest tests/governance_audit/` para comprovar regressão zero.
3. Executar `get_errors` consolidado uma única vez sobre os artefatos alterados.

---

## Plano de Rollback

Em caso de falha na validação ou quebra de referência cruzada:
1. Reverter as renomeações usando o mapa inverso (`novo -> antigo`) via script Node.js em `ctx_execute` ou `git checkout`.
2. Restaurar os arquivos modificados e reexecutar `pytest tests/governance_audit/`.

---

## Checklist de Prontidão (DoD)

- [ ] Planos de Governança e de Implementação aprovados pelo usuário no Gate R-064 (`status: APPROVED`, `approved: true`).
- [ ] 15 artefatos da Frente 1 com `tools: [...]` em formato inline array válido.
- [ ] 44 planos da Frente 2 renomeados para `AAAAMMDD-HHMMSS-*` e referências sincronizadas.
- [ ] Testes em `tests/governance_audit/` atualizados e 100% passando.
