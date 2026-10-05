# Plano de Planejamento: Retrofit de `harness-eval` em Agents/Prompts e Evolução do Fluxo de Criação de Skills

**ID:** `20261005-gov-retrofit-harness-eval-and-skill-creation-flow`  
**Data:** 2026-10-05  
**Workflow:** WORKFLOW-GOVERNANCE-MAINTENANCE  
**Status:** Proposto para Aprovação (Gate R-064.1)

---

## 1. Contexto e Motivação

Após a incorporação bem-sucedida da nova skill `harness-eval`, foi identificada a necessidade de:
1. Propagar (`retrofit`) a nova skill para os agents e prompts do repositório que desempenham papéis de auditoria, avaliação de trajetórias de workflow e calibração de prompts.
2. Evoluir o fluxo canônico de criação de novas skills em `governance-factory-patterns/SKILL.md` e `governance-factory.agent.md` para que, sempre ao finalizar a criação de uma nova skill, o fluxo execute obrigatoriamente a varredura de agents e prompts aderentes e aplique imediatamente o vínculo em `source_docs:` / `source_docs_lazy:` (R-015 / R-055).

---

## 2. Escopo da Intervenção

### 2.1 Em Escopo (In-Scope)
1. **Propagação da skill `harness-eval` nos consumidores identificados**:
   - `.github/prompts/eval-workflows.prompt.md`: Adicionar `.github/skills/harness-eval/SKILL.md` em `source_docs:`.
   - `.github/agents/agent-auditor.agent.md`: Adicionar `.github/skills/harness-eval/SKILL.md` em `source_docs_lazy:`.
   - `.github/agents/governance-factory.agent.md`: Adicionar `.github/skills/harness-eval/SKILL.md` em `source_docs_lazy:`.
   - `.github/agents/governance-maintainer.agent.md`: Adicionar `.github/skills/harness-eval/SKILL.md` em `source_docs_lazy:` (conforme mapeado em `harness-eval/SKILL.md` § 5).
   - `.github/agents/catalog.yaml`: Sincronizar os metadados dos agents alterados se necessário.
2. **Evolução do Fluxo Canônico de Criação de Skills (R-055 / Q2)**:
   - `.github/skills/governance-factory-patterns/SKILL.md`: Atualizar a Decision Tree canônica (ramo CRIAÇÃO) e adicionar a etapa obrigatória de "Retrofit e Descoberta de Consumidores Pós-Criação de Skill".
   - `.github/agents/governance-factory.agent.md`: Adicionar no checklist e no fluxo operacional a etapa de busca de agents e prompts aptos para ajuste imediato.
3. **Quality Gate e Blindagem de Testes (R-055 / Q3)**:
   - Validação da integridade dos artefatos alterados via suíte `tests/governance_audit/`.

### 2.2 Fora de Escopo (Out-of-Scope)
- Inclusão da skill em agents especialistas de aplicação (`test-strategy`, `deep-search`, etc.), onde a aderência é fraca ou fora de domínio.
- Alterações na lógica de avaliação do próprio `harness-eval`.

---

## 3. Matriz de Impacto e Artefatos Afetados

| Artefato | Tipo | Alteração Prevista |
|---|---|---|
| `.github/prompts/eval-workflows.prompt.md` | Prompt | Inclusão de `harness-eval/SKILL.md` em `source_docs:` |
| `.github/agents/agent-auditor.agent.md` | Agent | Inclusão de `harness-eval/SKILL.md` em `source_docs_lazy:` |
| `.github/agents/governance-factory.agent.md` | Agent | Inclusão de `harness-eval/SKILL.md` em `source_docs_lazy:` e menção a calibração de prompts |
| `.github/agents/governance-maintainer.agent.md` | Agent | Inclusão de `harness-eval/SKILL.md` em `source_docs_lazy:` |
| `.github/skills/governance-factory-patterns/SKILL.md` | Skill | Inserção do passo de varredura/retrofit de consumidores no ramo CRIAÇÃO da Decision Tree |
| `.github/agents/catalog.yaml` | Catálogo | Sincronização atômica dos campos `source_docs_lazy` dos agents |

---

## 4. Estratégia de Rollback
Reversão atômica via git diff/checkout dos arquivos modificados caso ocorra qualquer regressão na suíte de testes de governança.

---

## 5. Critérios de Sucesso
- [ ] Agents `@agent-auditor`, `@governance-factory`, `@governance-maintainer` e prompt `eval-workflows` referenciam `harness-eval`.
- [ ] Catálogo `catalog.yaml` sincronizado com os agents atualizados.
- [ ] `governance-factory-patterns/SKILL.md` e `governance-factory.agent.md` documentam compulsoriamente a etapa pós-criação de busca e ajuste de agents/prompts aptos.
- [ ] 100% dos testes de governança passam sem regressões.

