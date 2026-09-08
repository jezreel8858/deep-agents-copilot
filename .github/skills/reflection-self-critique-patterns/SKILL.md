---
name: reflection-self-critique-patterns
description: >
  Padrão generate → critique → revise (Reflection) para agents Executores
  reexaminarem o próprio artefato de saída antes de reportar sucesso —
  self-reflection de baixo custo (mesmo modelo) vs. critic separado
  (alto risco), com critério objetivo de quando aplicar cada um.
tier: 2
category: process
triggers:
  - "reflection"
  - "self-critique"
  - "auto-crítica"
  - "revisar antes de reportar"
  - "generate critique revise"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/agent-contracts/SKILL.md
tools: []
---

# Reflection / Self-Critique Patterns

## 0) Problema Resolvido

Gap de mercado identificado em `docs/plan/categorizacao-agents-mercado.md` §5.1: nenhum agent Executor deste catálogo reexamina o **próprio artefato de saída** (documento gerado, cobertura de teste, código) antes de reportar sucesso — apenas o prompt de entrada é refinado (`prompt-structuring`). Pesquisa de mercado (2026) confirma que Reflection é um padrão de **baixo custo e alto retorno** quando aplicado como passo interno (não como agent separado) para tarefas de risco baixo/médio.

## 1) Fundamentação de Mercado

| Fonte | Achado |
|---|---|
| Taskade, "Self-Improving AI Agents: The Reflection Loop" (2026) | "Self-reflection is one model doing both jobs, cheap and fast... Use self-reflection for quick passes, a critic agent for high-stakes outputs." Grounded/tool-based critique (testes, lint) é mais confiável que crítica puramente intrínseca. |
| Techademy, "ReAct, Plan-and-Execute & Reflection" (2026) | "The critique can be done by the same model with a different prompt, by a separate critic model, or by an external verifier such as a unit test runner." |
| Future AGI, "Evaluating LLM Self-Reflection Loops" (2026) | "Single-shot critique: one pass, draft → critique → rewrite → commit. Cheap and bounded." Recomenda **limite explícito de rounds** para não thrashing (4+ rounds sem convergência). |
| Zylos AI (2026) | Multi-agent debate custa 2-5× o compute — desproporcional para tarefas de baixo/médio risco. |

**Decisão de arquitetura para este projeto:** dado R-011 (sem overengineering) e a arquitetura hub-and-spoke já estabelecida (R-042), a Reflection é implementada como **passo interno do próprio agent Executor** (self-reflection, 1 round, grounded quando possível) — **não** como um agent `reflection-critic` separado. Um critic separado já existe para artefatos de alto risco: `code-review` (diff/PR) e `tech-solution-architect`/`bug-triage` cobrem o papel de "critic externo" quando o artefato é código de produção.

## 2) Padrão Canônico — Single-Shot Reflection (1 Round)

```
1. GERAR: produzir o artefato de saída (documento, suíte de teste, plano).
2. CRITICAR (grounded, quando possível): revisar contra critério objetivo e verificável:
   - Documento: contra a skill de estrutura do domínio (ex.: documentation-writing-patterns) + fonte real (evita alucinação).
   - Teste: contra o comando de cobertura executado (não contra "parece certo").
   - Código: contra `get_errors` + testes executados (grounded, não intrínseco).
3. REVISAR: se o critério objetivo falhar, corrigir e repetir 1 vez.
4. LIMITE: máximo 1 round de revisão automática — se ainda falhar, reportar como bloqueante (R-020, formato 3 linhas), nunca insistir em loop (alinhado à regra já existente "Sem Loops" de `test-engineer`).
```

**Regra de ouro:** a crítica deve ser **grounded** (verificável externamente: comando executado, lint, fonte real) sempre que possível — crítica puramente intrínseca ("parece bom") tem cobertura fraca de blind-spot (mesma limitação do modelo que gerou o erro).

## 3) Critério Objetivo de Quando Aplicar

| Cenário | Aplicar Reflection? | Formato |
|---|---|---|
| Artefato de baixo risco, reversível (doc `.md`, teste unitário isolado) | Sim — self-reflection, 1 round | Checklist objetivo do próprio agent |
| Artefato de alto risco, difícil de reverter (mudança de contrato, decisão de arquitetura) | Não neste padrão — usar critic separado já existente (`code-review`, `tech-solution-architect`) | Handoff explícito, não self-reflection |
| Falha grounded já disponível (teste rodou e falhou, lint apontou erro) | Sim — sempre corrigir antes de reportar (isso já é regra implícita em vários agents; esta skill formaliza o nome do padrão) | Corrigir e re-executar validação 1×, então reportar |
| Artefato de governança gerado referencia outro artefato como "dependente/consumidor" (ex.: agent X consome skill Y) | Sim — confirmar que a referência é dependência funcional real, não só rótulo semântico (ver `governance-factory-patterns` § 3.1) | Gate de autocrítica semântica, 1 round, antes do checklist estrutural |

## 4) Checklist de Conformidade

- [ ] Artefato gerado revisado contra critério objetivo/grounded antes de reportar sucesso.
- [ ] Revisão limitada a 1 round automático — sem loop (alinhado a R-011/regra "Sem Loops").
- [ ] Se a revisão falhar após 1 round, reportar bloqueante no formato de 3 linhas (R-020), não insistir.
- [ ] Preferir crítica grounded (comando/teste/lint executado) a crítica puramente intrínseca.

## 5) Anti-padrões

- ❌ Criar um agent `reflection-critic` dedicado para tarefas de baixo risco (overengineering — viola R-011; o custo de orquestração extra não se paga para docs/testes rotineiros).
- ❌ Loop de revisão sem limite (thrashing — 4+ rounds sem convergência, achado de mercado).
- ❌ Crítica puramente intrínseca quando existe fonte grounded disponível (teste, lint, fonte real).
- ❌ Confundir esta skill com `code-review-patterns` (aquela é crítica externa formal de PR/diff por outro agent; esta é auto-revisão interna de 1 round pelo próprio agent gerador).
- ❌ Registrar um agent/skill como "consumidor" desta skill quando o mecanismo real não é generate→critique→revise de um artefato (scope-creep — ex.: um Retriever decidindo parar/continuar chamadas externas usa *stop-condition*, não Reflection; caso corrigido: `deep-search` registrado indevidamente, depois removido).

## 6) Consumidores Mapeados

- `docs-engineer` — reexamina o `.md` gerado contra `documentation-writing-patterns` + fonte real antes de reportar (1 round).
- `test-engineer` — reexamina cobertura/resultado do comando de teste executado antes de reportar `SUCESSO` (grounded — já é comportamento parcialmente presente na "Regra de Ouro: Bloqueia Teste Falhando"; esta skill formaliza como passo de Reflection nomeado).
- `governance-factory` — aplica o gate de autocrítica semântica de [`governance-factory-patterns/SKILL.md`](../governance-factory-patterns/SKILL.md) § 3.1 antes do checklist estrutural: confirma que toda referência cruzada a outro artefato (ex.: "agent X consome skill Y") é dependência funcional real, não rótulo. Caso concreto que motivou o gate: `deep-search` registrado incorretamente como consumidor desta própria skill (corrigido — ver § 5 anti-padrões, item de scope-creep).
- **Futuro:** qualquer novo agent Executor que produza artefato revisável antes de reportar sucesso.

## 7) Referências

- Taskade, "Self-Improving AI Agents: The Reflection Loop" (2026) — https://www.taskade.com/blog/self-improving-ai-agents-reflection
- Techademy, "ReAct, Plan-and-Execute & Reflection: AI Agent Patterns" (2026) — https://www.techademy.com/react-plan-execute-reflection-agent-patterns
- Future AGI, "Evaluating LLM Self-Reflection Loops" (2026) — https://futureagi.com/blog/evaluating-llm-self-reflection-loops-2026
- `docs/plan/categorizacao-agents-mercado.md` §5.1 — origem desta skill.

