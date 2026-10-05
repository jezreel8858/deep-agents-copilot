---
name: plan-conformance-patterns
version: "1.0.0"
description: >-
  Fornece protocolo determinístico em 3 níveis (Allowlist, Blast Radius
  estrutural e Checagem Semântica de Escopo) para verificar se o diff de
  código permanece em conformidade com o Plano de Implementação Técnica
  aprovado (R-064) antes do merge. Use quando precisar validar se um PR
  extrapola o blast radius planejado, introduz arquivos ou tarefas não
  aprovadas, ou carece de testes para código planejado. Não use para
  auditoria de Architectural Decision Records (escopo exclusivo de
  `@adr-sentinel` sobre `docs/adr/*.md`) nem para planejamento macro de
  decomposição de refatoração (delegar para `refactoring-planning-patterns`).
tier: 2
category: process
triggers:
  - "verificar conformidade de escopo do diff com o plano aprovado"
  - "o pr extrapola o plano de implementação"
  - "plan conformance"
  - "escopo do pr versus plano aprovado"
  - "blast radius do diff fora do planejado"
  - "arquivo alterado fora do plano de implementação"
  - "desvio de escopo em relação ao related-planning-doc"
source_docs:
  - .github/agents/code-review.agent.md
  - .github/agents/pr-gatekeeper.agent.md
  - .github/agents/codegraph-engine.agent.md
  - docs/implementation-plans/README.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Plan Conformance Patterns

## 0) Problema Resolvido & Princípios Fundamentais

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: Frontmatter com `name`, `description`, `tier`, `category` e `triggers` para descoberta e roteamento rápido.
> - **Nível 2 (Corpo Operacional)**: Este arquivo `SKILL.md` contendo o Protocolo de Verificação em 3 Níveis, a Classificação de Desvios de Escopo e o Checklist de consumo por `@code-review`/`@pr-gatekeeper`.
> - **Nível 3 (Recursos Suplementares)**: Não aplicável nesta versão (sem `references/`, `scripts/` ou `snippets/` adicionais).

Esta skill formaliza o **Shift-Left Conformance**: verificar a aderência do diff ao escopo aprovado *antes* do merge (no quality gate de `@code-review`/`@pr-gatekeeper`), em vez de descobrir desvios de escopo somente em auditoria pós-hoc ou em incidente de produção. O princípio operacional segue **Plan-Then-Batch** (`governance-factory-patterns` / R-059): toda a verificação em 3 níveis é executada em UMA única chamada consolidada de batch-gather (diff + allowlist do plano + consulta a `@codegraph-engine`), nunca em chamadas sequenciais por arquivo.

Esta skill materializa, no momento do merge, a garantia de que o Duplo Gate Documental de Planejamento e Implementação (**R-064**) foi respeitado na prática: o Plano de Implementação Técnica aprovado e persistido em `docs/implementation-plans/*.md` (referenciado por `related-planning-doc` no front-matter do documento de implementação) é o **contrato de escopo vinculante** contra o qual o diff final é auditado.

> **Cross-Reference sem Colisão Conceitual com `refactoring-planning-patterns`**: a métrica de **blast radius** (dependências, fan-in/fan-out via `@codegraph-engine`) é a mesma computação estrutural usada por `refactoring-planning-patterns` — mas com propósito distinto e não concorrente. Em `refactoring-planning-patterns`, o blast radius é calculado **antes** da execução, para decompor a refatoração em um DAG de etapas seguras. Nesta skill, o blast radius é recalculado **depois** da implementação, como **gate de verificação retrospectiva** comparando o blast radius real do diff contra o blast radius declarado/esperado no plano aprovado. Mesma ferramenta (`@codegraph-engine`), mesmo vocabulário técnico, momentos e finalidades diferentes — nunca redefinir o conceito localmente.

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Ao revisar um diff/PR que possui um Plano de Implementação Técnica aprovado associado (`related-planning-doc` em `docs/implementation-plans/*.md`).
- Antes de gerar a submissão final do PR, para confirmar que nenhum desvio Bloqueador de escopo permanece sem justificativa.
- Quando o blast radius real do diff (via `@codegraph-engine`) precisa ser comparado contra o blast radius planejado.

### ❌ Quando NÃO Usar
- Para auditar conformidade com Architectural Decision Records — delegar para `@adr-sentinel` (`docs/adr/*.md`).
- Para planejar ou decompor uma refatoração estrutural antes da execução — usar `refactoring-planning-patterns`.
- Quando o diff não possui nenhum Plano de Implementação Técnica associado (ex.: hotfix emergencial sem R-064 aplicável) — reportar a ausência do plano como lacuna, sem inventar escopo retroativo.

## 2) Diretrizes Operacionais e Processo Canônico — Protocolo de Verificação em 3 Níveis

### Nível 1 — Validação de Allowlist
1. Extrair a lista exata de arquivos planejados do checklist GFM do(s) documento(s) correspondente(s) em `docs/implementation-plans/*.md` (campo `related-planning-doc`).
2. Comparar byte a byte essa allowlist contra a lista de arquivos efetivamente alterados no diff/PR.
3. Qualquer arquivo alterado fora da allowlist, sem justificativa textual explícita no PR, é candidato a desvio **Bloqueador** (§3).

### Nível 2 — Verificação Estrutural de Blast Radius
1. Reaproveitar `@codegraph-engine` (via `run_subagent`, operações `diff-impact`/`fn-impact`) — nunca recalcular dependências manualmente via `list_dir`/`grep_search`.
2. Comparar o blast radius estrutural retornado (dependências diretas/indiretas, fan-in/fan-out) contra o blast radius declarado no plano aprovado.
3. Arquivos órfãos de dependência (alterados sem nenhuma relação estrutural com o escopo planejado) são candidatos a desvio **Bloqueador** (§3).

### Nível 3 — Checagem Semântica Assistida de Escopo
1. Produzir um resumo funcional objetivo do diff (o que o código efetivamente faz).
2. Confrontar esse resumo contra o checklist GFM (`- [ ] <descrição>`) do documento de implementação aprovado.
3. Tarefas implementadas sem item correspondente no checklist, ou itens do checklist sem implementação correspondente, são reportados conforme a severidade aplicável (§2).

## 3) Padrões Canônicos com Exemplos Contrastantes — Classificação de Desvios de Escopo

| Severidade | Critério | Exemplo |
|---|---|---|
| 🔴 **Bloqueador** | Arquivo alterado fora do blast radius planejado sem justificativa, ou tarefa implementada que não consta do checklist GFM aprovado | ❌ Diff modifica `PaymentGateway.java` sem relação estrutural nem menção no plano aprovado |
| 🟠 **Alto** | Arquivo de teste ausente para código novo/alterado que estava previsto no plano | ❌ Plano previa `UserServiceTest.java` no checklist, mas o diff não contém o arquivo de teste correspondente |
| 🟡 **Sugestão** | Refatoração cosmética pontual dentro de um arquivo já planejado (sem extrapolar escopo) | ✅ Renomear variável local em `UserService.java`, arquivo já presente na allowlist do plano |

## 4) Checklist de Verificação de Conformidade de Escopo

- [ ] O diff/PR possui `related-planning-doc` identificável em `docs/implementation-plans/*.md`? Se não, reportar a ausência como lacuna (não aplicar o protocolo retroativamente).
- [ ] Nível 1 (Allowlist): todo arquivo alterado no diff está na allowlist do plano aprovado, ou possui justificativa textual explícita no PR.
- [ ] Nível 2 (Blast Radius): blast radius estrutural real (via `@codegraph-engine`) confere com o blast radius declarado no plano — sem arquivos órfãos de dependência.
- [ ] Nível 3 (Checagem Semântica): resumo funcional do diff mapeado 1:1 contra o checklist GFM do plano — sem tarefa implementada fora do checklist nem item do checklist sem implementação correspondente.
- [ ] Todo desvio identificado foi classificado por severidade (Bloqueador | Alto | Sugestão) conforme §2, com evidência `arquivo:linha`.
- [ ] Verificação executada em chamada única consolidada de batch-gather (diff + allowlist + `@codegraph-engine`), nunca em chamadas sequenciais por arquivo (R-046/R-060).
- [ ] Nenhum desvio Bloqueador pendente antes de `@pr-gatekeeper` gerar a submissão final do PR.
