# Plano de Planejamento: Importação e Adaptação da Skill `harness-eval`

**ID:** `20261005-gov-import-harness-eval`  
**Data:** 2026-10-05  
**Workflow:** WORKFLOW-GOVERNANCE-MAINTENANCE  
**Status:** Proposto para Aprovação (Gate R-064.1)

---

## 1. Contexto e Motivação

O projeto `deep-agents-copilot` necessita importar a skill externa `harness-eval` do catálogo aberto `tech-leads-club/agent-skills` (`packages/skills-catalog/skills/(development)/harness-eval`).
A auditoria preliminar conduzida pelo `@agent-auditor` identificou disparidades estruturais e normativas entre o padrão do repositório externo e as diretrizes de governança do `deep-agents-copilot` (especificação N1/N2/N3, frontmatter obrigatório, idioma PT-BR, progressive disclosure e convenções R-015/R-026/R-046/R-055).

Além disso, para preservar a conformidade com a licença de origem (`CC-BY-4.0`), o template canônico de skills precisa evoluir para suportar atribuição explícita de procedência (Systemic Reuse Gate Q2).

---

## 2. Escopo da Intervenção

### 2.1 Em Escopo (In-Scope)
1. **Evolução do Template de Skill (`.github/skills/templates/skill-template.md`)**:
   - Inclusão de campos opcionais no frontmatter YAML para procedência externa: `license:`, `source_attribution:`, `imported_from:`.
   - Inclusão de seção canônica de notas de licença/atribuição no Nível 2 quando a skill for originária de terceiros.
2. **Criação e Adaptação Canônica da Skill `harness-eval` (`.github/skills/harness-eval/`)**:
   - Criação do `SKILL.md` adaptado ao esqueleto canônico (Seções 0 a 5, blocos ✅/❌, triggers em PT-BR, progressive disclosure).
   - Migração dos arquivos de suporte de Nível 3 (`references/PROTOCOL.md`, `references/judge-prompts.md`, `references/GLOSSARY.md`, `references/claims.schema.json`, `scripts/*.py`).
   - Aplicação de compressão textual no N2 (orçamento ≤ 2.000 palavras), delegando detalhamento sequencial ao `references/PROTOCOL.md`.
3. **Delimitação de Fronteira Semântica**:
   - Atualização cruzada de "Quando NÃO Usar" em `harness-eval/SKILL.md` e `harness-engineering-patterns/SKILL.md`.
4. **Sincronização de Catálogos (R-015)**:
   - Registro atômico de `harness-eval` em `.github/skills/.index.json`.
5. **Quality Gate e Blindagem Automatizada (Q3)**:
   - Atualização/criação de asserções em `tests/governance_audit/` para validar a conformidade da nova skill importada.

### 2.2 Fora de Escopo (Out-of-Scope)
- Alteração da lógica interna dos scripts Python (`scripts/*.py`) da skill original, mantendo-os como utilitários N3 executáveis.
- Criação de novos agents executores nesta fase (a invocação de `harness-eval` será associada a `@agent-auditor` e `@governance-maintainer`).

---

## 3. Matriz de Gaps Identificados e Remediação

| Smell / Gap | Gravidade | Solução no Plano |
|---|---|---|
| Frontmatter N1 incompleto (faltam `tier`, `category`, `triggers`, `tools`, `source_docs`) | Bloqueador | Preencher campos obrigatórios seguindo o schema canônico local. |
| Idioma integral em inglês | Alto | Traduzir instruções operacionais e triggers para PT-BR, preservando identificadores técnicos. |
| Hipertrofia do corpo N2 (11 passos, excede ~2.000 palavras) | Alto | Resumir passos em diretrizes operacionais no `SKILL.md` e delegar protocolo exaustivo ao `references/PROTOCOL.md`. |
| Estrutura de seções divergente (falta esqueleto canônico 0-5) | Alto | Mapear conteúdo para as seções canônicas: `0) Problema Resolvido`, `1) Quando Usar vs NÃO Usar`, `2) Diretrizes Operacionais`, `3) Padrões Canônicos`, `4) Checklist`, `5) Consumidores`. |
| Ambiguidade de fronteira com `harness-engineering-patterns` | Alto | Delimitar: `harness-engineering-patterns` = diagnóstico contínuo de minimalismo; `harness-eval` = protocolo determinístico dual-judge sob demanda (Track A/B/C). |
| Atribuição CC-BY-4.0 ausente no template | Alto | Adicionar suporte a atribuição de licença externa no template canônico de skill. |
| Falta de indexação atômica | Alto | Atualizar `.github/skills/.index.json` no mesmo lote de alterações. |

---

## 4. Estratégia de Rollback

Caso a importação ou a adaptação apresente inconsistências não recuperáveis durante a execução do Quality Gate:
1. Reverter alterações em `.github/skills/templates/skill-template.md` e `.github/skills/.index.json`.
2. Remover a pasta `.github/skills/harness-eval/`.
3. Reverter referências cruzadas adicionadas em `harness-engineering-patterns/SKILL.md`.
4. Rastreabilidade via git branch/diff atômico.

---

## 5. Critérios de Sucesso
- [ ] `.github/skills/templates/skill-template.md` atualizado com metadados de atribuição.
- [ ] `.github/skills/harness-eval/SKILL.md` criado em conformidade total com N1/N2/N3 e triggers em PT-BR.
- [ ] Arquivos de suporte em `references/` e `scripts/` importados e vinculados.
- [ ] `.github/skills/.index.json` sincronizado com metadados de `harness-eval`.
- [ ] Testes de governança em `tests/` executados com sucesso (100% pass).

