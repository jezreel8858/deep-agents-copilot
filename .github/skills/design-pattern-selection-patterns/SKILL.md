---
name: design-pattern-selection-patterns
description: Fornece Decision Tree objetiva para selecionar (ou descartar) design patterns GoF, funcionais, arquiteturais e de resiliência na fase de planejamento, com guardrails anti-overengineering e registro em mini-ADR dentro do Template de Plano de Implementação Técnica (R-064).
tier: 2
category: governance
triggers: ["seleção de design pattern", "mini-ADR", "decision tree de patterns", "golden hammer", "premature pattern", "nenhum pattern necessário", "trade-offs arquiteturais"]
source_docs:
  - ".github/skills/refactoring-planning-patterns/SKILL.md"
  - ".github/skills/integration-contract-analysis/SKILL.md"
  - ".github/skills/documentation-writing-patterns/SKILL.md"
  - ".github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md"
  - ".github/skills/mermaid-diagrams/SKILL.md"
  - ".github/skills/agent-contracts/SKILL.md"
  - ".github/agents/adr-sentinel.agent.md"
source_docs_lazy:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
tools: []
---

# Design Pattern Selection Patterns

Skill **puramente analítica/decisória**, consumida pelos agents `*-arch-advisor` (read-only). Opera apenas na fase de planejamento (equivalente a *Design Doc Review*): valida a necessidade e a escolha de pattern ANTES de qualquer código. Nunca prescreve edição de arquivo nem implementação.

## 1) Quando Usar

**Use quando:**
- O plano técnico (R-064) envolve criação de abstração, desacoplamento, integração, migração ou resiliência e é preciso decidir se um pattern se justifica.
- Há mais de uma forma plausível de estruturar a solução e o trade-off precisa ser explícito.
- Um pedido já nomeia um pattern ("use Factory/CQRS") e é preciso validar a necessidade antes de aceitar.

**Não use quando:**
- A tarefa é implementar, editar código ou corrigir bug (escopo de `*-developer` / `*-bug-fixer`).
- Auditar código existente por oportunidade de pattern (modo *Code Review* — fora de escopo desta skill).
- A mudança é trivial (renomear, ajustar texto, config) e não envolve decisão estrutural.
- A decisão é puramente de documentação ou governança de artefatos.

## 2) Workflow Canônico

1. **Entender requisitos** — problema real, restrições, forças em conflito.
2. **Identificar a força dominante** — variação de comportamento, criação de objetos, integração, falha/concorrência, consistência de dados ou estrutura macro.
3. **Gate de necessidade** — existe problema concreto e mensurável? Se não → `nenhum pattern` (solução direta).
4. **Percorrer a Decision Tree (§3)** e listar 2–3 candidatos, SEMPRE incluindo a opção simples.
5. **Aplicar fatores objetivos (§4)** e checar anti-padrões (§5).
6. **Registrar o mini-ADR (§6)** dentro do Plano R-064 e revisar com o checklist (§7).

## 3) Decision Tree por Família

```text
Qual força domina?
├─ Sem problema mensurável ─────────────────► NENHUM pattern (solução direta)
├─ CRIAÇÃO de objetos (GoF criacional)
│   ├─ Construção complexa/opcional ────────► Builder
│   ├─ Família de objetos relacionados ─────► Abstract Factory
│   ├─ Subclasse decide o tipo ─────────────► Factory Method
│   └─ Instância única global ──────────────► Singleton (raro; preferir injeção de dependência)
├─ ESTRUTURA/INTEGRAÇÃO (GoF estrutural)
│   ├─ Interfaces incompatíveis ────────────► Adapter
│   ├─ Adicionar comportamento dinamicamente► Decorator
│   ├─ Simplificar subsistema complexo ─────► Facade
│   └─ Controle de acesso/lazy/cache ───────► Proxy
├─ COMPORTAMENTO (GoF comportamental)
│   ├─ Notificar mudança de estado ─────────► Observer
│   ├─ Trocar algoritmo em runtime ─────────► Strategy
│   ├─ Encapsular ação (undo/fila) ─────────► Command
│   └─ Comportamento depende do estado ─────► State
├─ FUNCIONAL/MODERNO
│   ├─ Erro/ausência como valor ────────────► Monad (Result/Option)
│   └─ Etapas encadeadas e transversais ────► Pipeline/Middleware
├─ ARQUITETURAL (decisão estrutural)
│   ├─ Isolar domínio de infraestrutura ────► Clean Architecture / Hexagonal
│   ├─ Leitura e escrita com perfis distintos► CQRS
│   ├─ Desacoplamento temporal entre serviços► Event-driven
│   └─ Migração incremental de legado ──────► Strangler Fig
└─ RESILIÊNCIA (dependência remota instável)
    ├─ Falha transitória ───────────────────► Retry (com backoff/jitter)
    ├─ Falha persistente/cascata ───────────► Circuit Breaker
    └─ Isolar recursos por consumidor ──────► Bulkhead
```

Adaptar ao stack do advisor (ex.: Monad/Pipeline em Spring Reactive e React; Hexagonal/Strangler Fig em EJB/Struts; CQRS/Event-driven em backends distribuídos; padrões de acesso a dados em database).

## 4) Fatores Objetivos de Decisão

A escolha deriva de evidência, nunca de preferência estética do agent:

| Fator | Pergunta objetiva |
|---|---|
| Time | Tamanho, estrutura e familiaridade com o pattern |
| Desacoplamento | Há acoplamento medido/observado que causa custo real? |
| Consistência vs disponibilidade | O domínio tolera consistência eventual? |
| Maturidade operacional | Há observabilidade/operação para sustentar a complexidade? |
| Complexidade do domínio | O domínio é realmente complexo ou CRUD? |
| Custo de reversão | Quão caro é desfazer a decisão? |

Regra: *complexity is a cost you pay, not a feature you gain*. Escalar para pattern mais complexo exige evidência mensurável do trade-off.

## 5) Anti-Padrões (Guardrails Anti-Overengineering)

| Anti-padrão | Sintoma | Remédio |
|---|---|---|
| God Object | Uma classe/módulo faz tudo | Dividir em unidades focadas (SRP) |
| Golden Hammer | Mesmo pattern aplicado a tudo | Escolher por problema; exigir alternativas no mini-ADR |
| Spaghetti Code | Dependências emaranhadas, fluxo sem fronteiras | SRP, módulos, camadas e contratos explícitos |
| Premature Optimization/Pattern | Pattern aplicado antes de medir o problema | Gate de necessidade; opção `nenhum pattern`; evidência antes de escalar (R-058) |

Anti-padrões de ADR a evitar: listar só benefícios, agrupar várias decisões num ADR, ausência de decisão explícita.

## 6) Formato de Saída — Mini-ADR no Plano R-064

Toda decisão (inclusive `nenhum pattern`) é registrada como seção do **Template de Plano de Implementação Técnica (R-064)** já emitido pelo advisor. NÃO criar arquivo/artefato separado.

```markdown
### Mini-ADR — <título da decisão>
- **Contexto:** problema, forças e trade-off identificados.
- **Decisão:** <pattern escolhido | nenhum — solução direta é suficiente>.
- **Alternativas consideradas:** 2–3 opções (incluindo a simples), com prós/contras e motivo da rejeição.
- **Consequências:** o que se ganha e o que se perde (complexidade, custo de reversão, operação).
```

Uma decisão por mini-ADR. Implementação é delegada via handoff ao `*-developer` (`handoff-governance`).

## 7) Checklist

- [ ] Requisitos e forças descritos com evidência (não opinião).
- [ ] Gate de necessidade aplicado; `nenhum pattern` considerado.
- [ ] Decision Tree percorrida e ≥ 2 alternativas listadas (incluindo a simples).
- [ ] Fatores objetivos (§4) citados na decisão.
- [ ] Anti-padrões (§5) verificados.
- [ ] Mini-ADR com Contexto/Decisão/Alternativas/Consequências dentro do Plano R-064.
- [ ] Nenhuma instrução de edição de arquivo nem transferência de edição manual ao usuário (R-057).

## 8) Referências

- Martin Fowler — Architecture Decision Record: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
- ADR GitHub: https://adr.github.io
- bool.dev — 10 ADR Anti-Patterns: https://bool.dev/blog/detail/10-adr-antipatterns
- Skills relacionadas: `refactoring-planning-patterns`, `integration-contract-analysis`, `documentation-writing-patterns`, `specialist-hybrid-advisory-implementation-patterns`, `agent-contracts`.
