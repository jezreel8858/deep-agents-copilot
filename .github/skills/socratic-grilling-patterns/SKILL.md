---
name: socratic-grilling-patterns
description: >-
  Fornece algoritmo de árvore de decisão e protocolo de registro concorrente (Grill-with-Docs) para conduzir interrogatório socrático estruturado via ask_questions, mapeando a fronteira ativa de incerteza até decisões arquiteturais documentadas. Use quando um requisito, decisão arquitetural ou trade-off técnico permanecer ambíguo após a primeira rodada de clarificação. Não use para coleta trivial de dados objetivos — usar structured-intake-patterns.
tier: 2
category: process
triggers:
  - "interrogatório socrático"
  - "socratic grilling"
  - "trade-off arquitetural"
  - "decisão ambígua"
  - "fronteira ativa"
  - "grill with docs"
  - "glossário ubíquo"
source_docs:
  - .github/skills/structured-intake-patterns/SKILL.md
  - .github/skills/requirements-engineering-patterns/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Socratic Grilling Patterns

## 0) Problema Resolvido & Princípios Fundamentais

Formaliza um protocolo de questionamento iterativo profundo para transformar ambiguidade residual em decisões documentadas e rastreáveis, evitando tanto a paralisia de perguntas infinitas quanto a suposição silenciosa de intenção (violação de R-027).

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Quando uma decisão arquitetural tem múltiplos trade-offs mutuamente exclusivos sem critério objetivo declarado.
- Quando a primeira rodada de `ask_questions` (structured-intake-patterns) não eliminou a ambiguidade central.
- Como base para consolidar glossário ubíquo de domínio durante elicitação.

### ❌ Quando NÃO Usar
- Para coleta de dados objetivos triviais (nome de arquivo, ambiente-alvo) — usar `structured-intake-patterns`.
- Para bloquear indefinidamente um plano já aprovado — respeitar R-031 (zero-interrupção).

---

## 2) Algoritmo da Árvore de Decisão e Gestão da Fronteira Ativa

1. Mapear a **Fronteira Ativa**: o menor conjunto de perguntas cuja resposta desbloqueia o maior número de decisões subsequentes (maximizar valor de informação por pergunta).
2. Priorizar perguntas de alto poder discriminante (que eliminam ramos inteiros da árvore) antes de perguntas de detalhe de implementação.
3. Cada resposta do usuário poda um ramo da árvore — nunca reabrir ramo já podado sem nova evidência contraditória.
4. Encerrar o interrogatório quando a Fronteira Ativa estiver vazia (nenhuma pergunta restante muda a decisão corrente).
5. Toda pergunta usa `ask_questions` (R-027), sempre com a última opção em campo aberto.

---

## 3) Protocolo "Grill-with-Docs" — Registro Concorrente

Durante o interrogatório, registrar **concorrentemente** (nunca apenas ao final):

- **Trade-offs avaliados**: alternativas descartadas e o motivo objetivo do descarte.
- **Decisões arquiteturais tomadas**: decisão + racional + responsável pela resposta.
- **Glossário ubíquo**: termos de domínio definidos durante a conversa, evitando deriva semântica em artefatos subsequentes.

Este registro concorrente alimenta diretamente `docs/requirements/REQ-<modulo>.md`, ADRs (`@adr-sentinel`) ou o Blueprint Técnico (`@tech-solution-architect`).

---

## 4) Handoff para Stakeholder Externo

Quando o impasse técnico não pode ser resolvido apenas com o usuário do chat (decisão de negócio real), sintetizar o impasse via `docs/agent-context/templates/stakeholder-questionnaire.md` — pergunta objetiva assíncrona com Contexto, Pergunta de Decisão, Opções de Trade-off e Impacto.

---

## 5) Checklist de Auto-Verificação

- [ ] Fronteira Ativa identificada e priorizada antes de iniciar as perguntas.
- [ ] Cada pergunta usa `ask_questions` com campo aberto como última opção (R-027).
- [ ] Trade-offs, decisões e glossário registrados concorrentemente (Grill-with-Docs).
- [ ] Impasses de negócio puro sintetizados via `stakeholder-questionnaire.md`.
- [ ] Interrogatório encerrado quando a Fronteira Ativa esvaziar.

---

## 6) Anti-padrões

| Anti-padrão | Risco / Sintoma | Correção Recomendada |
|---|---|---|
| Perguntar tudo de uma vez sem priorização | Sobrecarga cognitiva, abandono do fluxo | Árvore de decisão com Fronteira Ativa priorizada |
| Reabrir ramo já podado sem nova evidência | Loop infinito de re-perguntas | Podar ramo definitivamente após resposta |
| Registrar decisões só ao final da conversa | Perda de racional e trade-offs intermediários | Registro concorrente (Grill-with-Docs) |
| Assumir resposta em vez de perguntar | Decisão arquitetural incorreta silenciosa | `ask_questions` obrigatório, sem inferência (R-027) |
| Bloquear plano já aprovado com nova rodada de perguntas | Viola R-031 (zero-interrupção) | Grilling ocorre antes da aprovação do plano |

---

## 7) Consumidores Mapeados e Integrações

| Consumidor | Papel na Relação | Momento de Uso |
|---|---|---|
| `@requirements-analyst` | Elicitação de requisito ambíguo | Antes de materializar `REQ-<modulo>.md` |
| `@tech-solution-architect` | Trade-off de blueprint técnico | Antes de fechar contrato de API/modelo de dados |
| `@refactor-planner` | Decisão de escopo de refatoração | Antes de fechar o DAG de etapas quando o escopo é ambíguo |

---

## 8) Referências e Documentação Conexa

- `CLAUDE.md` — R-027 (Clarificação Obrigatória via ask_questions), R-031 (Plano Auto-Implementável).
- `.github/skills/structured-intake-patterns/SKILL.md`
- `.github/skills/requirements-engineering-patterns/SKILL.md`
- `docs/agent-context/templates/stakeholder-questionnaire.md`
