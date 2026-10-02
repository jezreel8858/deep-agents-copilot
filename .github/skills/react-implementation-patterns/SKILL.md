---
name: react-implementation-patterns
description: >-
  Padrões de mercado 2025/2026 para implementar features/bugs em React (hooks, TanStack
  Query + Zustand, TDD red-green-refactor, checklist de PR) — contraparte de execução
  de react-frontend-patterns.
tier: 2
category: quality
triggers:
  - "implementar feature react"
  - "criar componente react"
  - "tanstack query zustand"
  - "tdd react"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/react/react-feature-developer.agent.md
tools: []
---

# React Implementation Patterns

> Esta skill cobre o modo **Implementação**. Para o modo **Advisory**, ver [`react-frontend-patterns`](../react-frontend-patterns/SKILL.md).

## Quando Usar

- Ao implementar nova feature, componente, hook customizado ou correção de bug em React.
- Ao decidir entre TanStack Query (server state) e Zustand (client/UI state).
- Ao aplicar o workflow TDD estrito (red-green-refactor) em frontend React.

## Como Usar

- Server state: `useQuery`/`useMutation` do TanStack Query; invalide cache com `queryClient.invalidateQueries`.
- Client/UI state: store Zustand leve (`create((set) => ({...}))`), sem boilerplate de actions/reducers.
- Teste vermelho (red) sempre antes da implementação (handoff a test-writer quando aplicável).
- Implemente o mínimo necessário para o teste passar (green); refatore em seguida.
- Rotas novas: registrar no shell de navegação (sidebar/menu) antes de reportar conclusão.

## Checklist

- [ ] Teste vermelho (red) existe e falha antes da implementação.
- [ ] Implementação mínima faz o teste passar (green), sem gold-plating.
- [ ] Server state exclusivamente via TanStack Query; client state exclusivamente via Zustand.
- [ ] Componentes reaproveitam contratos reais de `shared/`/design system (Canonical Sibling First).
- [ ] `get_errors` limpo antes de reportar conclusão.
- [ ] Handoff para `@react-unit-test-writer`/`@react-component-test-writer` ao final da fase green.

## Referências

- TanStack Query Docs: https://tanstack.com/query/latest
- Zustand Docs: https://zustand.docs.pmnd.rs/
- React Docs — Hooks: https://react.dev/reference/react/hooks
