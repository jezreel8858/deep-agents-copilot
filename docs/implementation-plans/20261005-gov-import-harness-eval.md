# Plano de Implementação: Importação e Adaptação da Skill `harness-eval`

**ID:** `20261005-gov-import-harness-eval`  
**Data:** 2026-10-05  
**Workflow:** WORKFLOW-GOVERNANCE-MAINTENANCE  
**Referência de Planejamento:** `docs/plans/20261005-gov-import-harness-eval.md`  
**Status:** Proposto para Aprovação (Gate R-064.2)

---

## 1. Resumo da Abordagem Técnica

A implementação realiza a ingestão e adaptação canônica da skill externa `harness-eval` (proveniente de `tech-leads-club/agent-skills`), garantindo paridade estrutural com os padrões do ecossistema `deep-agents-copilot`.

A execução segue o protocolo **Single-Turn Batching (R-046)** e **Reúso Sistêmico (R-055)**:
- **Passo 1 (Q2 - Template)**: Atualizar `.github/skills/templates/skill-template.md` com campos opcionais para procedência externa (`license:`, `source_attribution:`, `imported_from:`) e seção de conformidade de direitos autorais.
- **Passo 2 (Skill N1/N2)**: Criar `.github/skills/harness-eval/SKILL.md` no padrão canônico N1 (frontmatter estrito com `tier: 2`, `category: quality`, triggers em PT-BR) e N2 (seções `0` a `5`, blocos `✅/❌`, resumo operacional ≤ 2.000 palavras).
- **Passo 3 (Skill N3)**: Materializar subpastas `references/` e `scripts/` sob `.github/skills/harness-eval/`, importando o protocolo procedural e os utilitários de avaliação determinística Track A/B/C.
- **Passo 4 (Fronteira Semântica)**: Atualizar `harness-engineering-patterns/SKILL.md` para delimitar a fronteira entre diagnóstico heurístico contínuo e avaliação dual-judge sob demanda.
- **Passo 5 (Catálogo R-015)**: Registrar atomicamente a nova skill em `.github/skills/.index.json`.
- **Passo 6 (Q3 - Quality Gate)**: Executar suíte de testes de governança (`pytest tests/governance_audit/`) via sandbox `ctx_execute` (Think-in-Code, Zero-Noise).

---

## 2. Detalhamento dos Componentes e Arquivos

### 2.1 `.github/skills/templates/skill-template.md`
- **Ação**: Edição cirúrgica.
- **Mudança**: Adicionar campos comentados no frontmatter:
  ```yaml
  # Metadados opcionais para skills importadas/adaptadas de fontes externas:
  # license: "CC-BY-4.0"
  # source_attribution: "Tech Leads Club (agent-skills)"
  # imported_from: "https://github.com/tech-leads-club/agent-skills/..."
  ```
  E incluir subseção em `## 0) Problema Resolvido` indicando a proveniência e termos de licenciamento quando aplicável.

### 2.2 `.github/skills/harness-eval/SKILL.md`
- **Ação**: Criação de novo arquivo.
- **Frontmatter N1**:
  ```yaml
  ---
  name: harness-eval
  description: Executa o protocolo de avaliação determinística de harness de agentes (Track A: regressão de instruções; Track B: calibração de prompts; Track C: auditoria dual-judge) comparando comportamento esperado contra evidências observáveis.
  tier: 2
  category: quality
  license: "CC-BY-4.0"
  source_attribution: "Tech Leads Club (agent-skills)"
  imported_from: "https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/(development)/harness-eval"
  triggers:
    - "quando precisar avaliar deterministamente a eficácia do harness de um agente"
    - "quando for necessário rodar auditoria dual-judge em prompts de agentes"
    - "quando executar testes de regressão de instruções ou calibração de harness"
    - "quando auditar fidelidade de execução contra claims e critérios de aceitação"
  source_docs:
    - ".github/skills/harness-eval/references/GLOSSARY.md"
  source_docs_lazy:
    - ".github/skills/harness-eval/references/PROTOCOL.md"
    - ".github/skills/harness-eval/references/judge-prompts.md"
  tools: []
  ---
  ```
- **Corpo N2**:
  - `## 0) Problema Resolvido & Atribuição de Origem`
  - `## 1) Quando Usar vs Quando NÃO Usar` (distinguindo de `harness-engineering-patterns` e `agent-evals-lab`)
  - `## 2) Diretrizes Operacionais (Tracks A, B e C)`
  - `## 3) Padrões Canônicos com Exemplos Contrastantes (Anti-Padrão vs Padrão Canônico)`
  - `## 4) Checklist Operacional`
  - `## 5) Consumidores Mapeados (@agent-auditor, @governance-maintainer)`

### 2.3 Suporte de Nível 3 (`.github/skills/harness-eval/references/` e `scripts/`)
- `references/PROTOCOL.md`: Protocolo detalhado com os 11 passos de execução da avaliação.
- `references/judge-prompts.md`: Prompts canônicos para juízes LLM dual-judge.
- `references/GLOSSARY.md`: Glossário técnico de termos de harness evaluation.
- `references/claims.schema.json`: Schema JSON de validação de claims.
- `scripts/`: Scripts utilitários de suporte à avaliação.

### 2.4 `.github/skills/harness-engineering-patterns/SKILL.md`
- **Ação**: Edição cirúrgica.
- **Mudança**: Adicionar menção em "Quando NÃO Usar": "Não use para executar auditoria dual-judge de claims ou calibração formal de prompts via protocolo de 3 trilhas — use `harness-eval`."

### 2.5 `.github/skills/.index.json`
- **Ação**: Atualização atômica adicionando metadados de `harness-eval`.

---

## 3. Plano de Execução em Lote (Single-Turn Batch)

1. **Batch Phase**: Criar diretórios e arquivos de `harness-eval`, atualizar `skill-template.md`, atualizar `harness-engineering-patterns/SKILL.md` e sincronizar `.index.json`.
2. **Verification Phase**: Executar testes automatizados de governança para validar integridade sintática e conformidade dos arquivos alterados.
3. **Audit Closure**: Relatório final do gate de qualidade.

---

## 4. Plano de Rollback e Critérios de Aceitação
- Reversão atômica via git se qualquer teste de governança falhar.
- Critério de aprovação: 100% dos testes em `tests/governance_audit/` verdes, zero smells bloqueadores no `@agent-auditor`.

