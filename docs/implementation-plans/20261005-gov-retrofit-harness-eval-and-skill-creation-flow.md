# Plano de Implementação: Retrofit de `harness-eval` e Evolução do Fluxo de Criação de Skills

**ID:** `20261005-gov-retrofit-harness-eval-and-skill-creation-flow`  
**Data:** 2026-10-05  
**Workflow:** WORKFLOW-GOVERNANCE-MAINTENANCE  
**Referência de Planejamento:** `docs/plans/20261005-gov-retrofit-harness-eval-and-skill-creation-flow.md`  
**Status:** Proposto para Aprovação (Gate R-064.2)

---

## 1. Resumo da Abordagem Técnica

A implementação executa duas frentes complementares de governança sob **Single-Turn Batching (R-046)** e **Safe Verification Pattern (R-051)**:
1. **Retrofit de `harness-eval` nos Consumidores**:
   - Adicionar `.github/skills/harness-eval/SKILL.md` a `eval-workflows.prompt.md` (em `source_docs`).
   - Adicionar `.github/skills/harness-eval/SKILL.md` a `agent-auditor.agent.md`, `governance-factory.agent.md` e `governance-maintainer.agent.md` (em `source_docs_lazy` de acordo com R-066).
   - Sincronizar atômica e deterministicamente o catálogo `catalog.yaml` para refletir as novas dependências dos agents.
2. **Evolução do Fluxo Canônico de Criação de Skills**:
   - Atualizar `.github/skills/governance-factory-patterns/SKILL.md` no ramo CRIAÇÃO da Decision Tree e adicionar a subseção normativa "Retrofit e Descoberta de Consumidores Pós-Criação de Skill", determinando que, após materializar uma nova skill, a factory deve:
     *(a)* Mapear `catalog.yaml` e `.github/prompts/` por palavras-chave e domínio;
     *(b)* Identificar agents e prompts aptos ao consumo da nova skill;
     *(c)* Aplicar imediatamente o retrofit em lote nos `source_docs`/`source_docs_lazy` dos artefatos identificados no mesmo ciclo de entrega (R-015).
   - Atualizar `.github/agents/governance-factory.agent.md` incorporando esse passo em seu checklist operacional e seção de criação de skills.
3. **Validação**: Executar suíte de testes de governança (`pytest tests/governance_audit/`) via sandbox sem regressões.

---

## 2. Detalhamento dos Componentes e Arquivos

### 2.1 `.github/prompts/eval-workflows.prompt.md`
- **Ação**: Edição cirúrgica.
- **Mudança**: Adicionar `.github/skills/harness-eval/SKILL.md` na lista `source_docs:`.

### 2.2 `.github/agents/agent-auditor.agent.md`
- **Ação**: Edição cirúrgica.
- **Mudança**: Adicionar `.github/skills/harness-eval/SKILL.md` na lista `source_docs_lazy:`.

### 2.3 `.github/agents/governance-factory.agent.md`
- **Ação**: Edição cirúrgica.
- **Mudança**:
  - Adicionar `.github/skills/harness-eval/SKILL.md` na lista `source_docs_lazy:`.
  - Adicionar no checklist operacional o passo: "Ao finalizar CRIAÇÃO de nova skill: varrer `catalog.yaml` e `.github/prompts/` por aderência temática e aplicar o retrofit de `source_docs`/`source_docs_lazy` nos agents e prompts aptos."

### 2.4 `.github/agents/governance-maintainer.agent.md`
- **Ação**: Edição cirúrgica.
- **Mudança**: Adicionar `.github/skills/harness-eval/SKILL.md` na lista `source_docs_lazy:`.

### 2.5 `.github/skills/governance-factory-patterns/SKILL.md`
- **Ação**: Edição cirúrgica.
- **Mudança**:
  - Na Decision Tree (§ 1), ramo "Não -> CRIAÇÃO", adicionar a etapa subsequente obrigatória:
    `--> Pós-criação: Varrer catalog.yaml e .github/prompts/ para identificar artefatos aptos -> Aplicar retrofit em lote de source_docs/source_docs_lazy`.
  - Incluir diretriz explícita sobre a obrigatoriedade da etapa de amarração automática pós-criação.

### 2.6 `.github/agents/catalog.yaml`
- **Ação**: Edição cirúrgica via script verificado.
- **Mudança**: Atualizar `source_docs_lazy` dos nós `agent-auditor`, `governance-factory` e `governance-maintainer`.

---

## 3. Plano de Execução em Lote (Single-Turn Batch)

1. **Batch Mutation**: Aplicar as modificações cirúrgicas em todos os 6 arquivos em um único script via sandbox (`ctx_execute`), garantindo integridade de âncoras e checagem pós-escrita (`count === 1`).
2. **Quality Verification**: Executar a suíte `tests/governance_audit/` para assegurar que nenhum parser YAML, regra de R-066 ou contrato de agent foi violado.
3. **Quality Gate Review**: Conduzir re-auditoria cética com `@agent-auditor`.

---

## 4. Plano de Rollback e Critérios de Aceitação
- Reversão instantânea via git checkout dos 6 arquivos se houver falha de testes.
- Critério de aceitação: todos os 4 artefatos consumidores apontando para `harness-eval/SKILL.md`, fluxo de criação de skills formalmente atualizado em `governance-factory-patterns` e `governance-factory.agent.md`, e 100% dos testes de governança passando.

