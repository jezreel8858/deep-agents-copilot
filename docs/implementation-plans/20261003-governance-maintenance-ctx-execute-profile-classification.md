---
status: concluído
date: 2026-10-03
autor: governance-maintainer
workflow: WORKFLOW-GOVERNANCE-MAINTENANCE
related-planning-doc: docs/plans/20261003-governance-maintenance-ctx-execute-profile-classification.md
progress: 100
---

# Plano de Implementação — Poda de Ferramentas de Context-Mode em Agentes Gather-Only

- **Workflow**: WORKFLOW-GOVERNANCE-MAINTENANCE — Etapa 4 (Execução de Manutenção, R-058 / R-064)
- **Gate**: 2º gate do Duplo Gate Documental (R-064) — **Status: ✅ APROVADO E EXECUTADO**
- **Autor**: governance-maintainer
- **Data**: 2026-10-03
- **Documento-base**: `docs/plans/20261003-governance-maintenance-ctx-execute-profile-classification.md`

---

## 1) Escopo e Arquivos Alvo (26 Agentes)

A alteração consiste na remoção cirúrgica de `'context-mode/ctx_execute'` e `'context-mode/ctx_execute_file'` do array `tools:` dos 26 arquivos:

1. `.github/agents/agent-auditor.agent.md`
2. `.github/agents/adr-sentinel.agent.md`
3. `.github/agents/bug-triage.agent.md`
4. `.github/agents/code-review.agent.md`
5. `.github/agents/code-style-enforcer.agent.md`
6. `.github/agents/compliance-guardrails.agent.md`
7. `.github/agents/database-specialist.agent.md`
8. `.github/agents/debugger.agent.md`
9. `.github/agents/deep-search.agent.md`
10. `.github/agents/devops-engineer.agent.md`
11. `.github/agents/docs-engineer.agent.md`
12. `.github/agents/feature-planner.agent.md`
13. `.github/agents/pr-gatekeeper.agent.md`
14. `.github/agents/repo-hygiene-auditor.agent.md`
15. `.github/agents/requirements-analyst.agent.md`
16. `.github/agents/runtime-verifier.agent.md`
17. `.github/agents/security-reviewer.agent.md`
18. `.github/agents/tech-solution-architect.agent.md`
19. `.github/agents/test-strategy.agent.md`
20. `.github/agents/backend/ejb/ejb-arch-advisor.agent.md`
21. `.github/agents/backend/python/python-arch-advisor.agent.md`
22. `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md`
23. `.github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md`
24. `.github/agents/backend/struts/struts-arch-advisor.agent.md`
25. `.github/agents/frontend/angular/angular-arch-advisor.agent.md`
26. `.github/agents/frontend/react/react-arch-advisor.agent.md`

---

## 2) Diff Pretendido e Regras de Transformação

Para cada arquivo alvo:
- Localizar a chave de frontmatter `tools: [...]`.
- Garantir a presença prévia de `'context-mode/ctx_batch_execute'` (adicionando-o se faltasse).
- Filtrar e remover exclusivamente os literais `'context-mode/ctx_execute'` e `'context-mode/ctx_execute_file'`.
- Manter formatação inline canônica com aspas simples padronizadas: `tools: ['tool1', 'tool2', ...]`.
- Preservar rigorosamente todas as outras ferramentas, quebras de linha e seções markdown do artefato.

---

## 3) Ordem e Método de Execução (Single-Turn Batching R-046 / R-059)

Em estrita observância a **R-046**, **R-051** e **R-059**:
- Toda a leitura, validação e mutação dos 26 arquivos é realizada em processo consolidado único dentro do sandbox do `context-mode`.
- Zero roundtrips sequenciais no chat (eliminação de Tool Chaining / Smell 2.26).
- Aplicação do Padrão de Edição Segura Verificada (R-051):
  1. Pré-leitura e validação de unicidade da âncora;
  2. Escrita atômica no disco;
  3. Releitura confirmatória e checagem de integridade pós-gravação.

---

## 4) Critérios de Validação Pós-Edição

1. **Validação de Sintaxe e Linter**: Execução única e consolidada de `get_errors` englobando todos os 26 `filePaths` alterados.
2. **Amostragem de Integridade**: Reler no mínimo 3 arquivos (raiz, backend e frontend) para inspecionar integridade YAML.
3. **Teste Automatizado de Não-Regressão**: Criação e execução de `tests/governance_audit/test_ctx_execute_capability_profile.py` validando conformidade 100%.
4. **Alinhamento Transversal**: Atualização de `governance-factory-patterns/SKILL.md`, `governance-audit-patterns/SKILL.md` e `CHANGELOG.md`.
