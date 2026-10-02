---
name: react-frontend-patterns
description: >-
  Boas práticas e patterns de codificação React moderno (React 19+) para componentes,
  Server/Client Components, hooks, reatividade, segurança e consistência arquitetural.
tier: 2
category: quality
triggers:
  - "boas práticas react"
  - "padrões de componente react"
  - "server components"
  - "regras de hooks"
  - "arquitetura react"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/react/react-router.agent.md
tools: []
---

# React Frontend Patterns

> Esta skill cobre o modo **Advisory** (análise/recomendação, sem código). Para o modo **Implementação** (codificar feature/bugfix), ver [`react-implementation-patterns`](../react-implementation-patterns/SKILL.md).

## Quando Usar

- Quando for necessário revisar qualidade e consistência de código React.
- Quando houver decisão de padrão entre Server Components, Client Components e boundary de estado.
- Quando precisar de baseline para recomendações sem implementar código.

## Padrões Recomendados

| Pilar | Diretriz | Evidência mínima |
|---|---|---|
| Server vs Client | Server Component é o default; `'use client'` apenas com interação/estado/APIs de browser, boundary próximo das folhas | Diretiva `'use client'` presente apenas onde há estado/evento real |
| Regras de hooks | Hooks no topo do componente/custom hook; exceção do `use()` (React 19) pode estar em condicional | Ausência de hooks condicionais fora da exceção documentada |
| Data fetching | `async/await` direto em Server Component + `cache()`; evitar `useEffect`+`setState` para fetch | Zero padrão de fetch-on-mount manual sem justificativa |
| Estado | Server state via TanStack Query; client/UI state via Zustand; sem duplicação entre as duas camadas | Ausência de dados de servidor replicados em store de cliente |
| Performance | React Compiler cobre memoização padrão; `useMemo`/`useCallback`/`React.memo` reservados a casos medidos | Justificativa via Profiler antes de memoização manual |
| Segurança | Evitar `dangerouslySetInnerHTML` sem sanitização explícita | Mapeamento de pontos de risco XSS e sanitização aplicada |

## Checklist de Revisão React

- [ ] Fronteira Server/Client Components está próxima das folhas, não propagada ao topo da árvore.
- [ ] Hooks seguem as regras canônicas (sem condicionais fora da exceção do `use()`).
- [ ] Server state e client state não estão duplicados entre TanStack Query e Zustand.
- [ ] Não há `useEffect` cobrindo data fetching que poderia ser `async`/TanStack Query.
- [ ] Memória/memoização manual é justificada por medição real (Profiler), não especulativa.
- [ ] Recomendações incluem impacto esperado em performance (Core Web Vitals) e manutenibilidade.

## Anti-padrões

- ❌ Marcar `'use client'` no topo da árvore de componentes "por segurança".
- ❌ Usar `useEffect` para fetch sem necessidade (race conditions, boilerplate).
- ❌ Duplicar dados de servidor em store Zustand.
- ❌ Context mal segmentado causando re-render storms.
- ❌ Memory leaks por listeners/timers/subscriptions sem cleanup em `useEffect`.

## Referências

- React Docs — Server Components: https://react.dev/reference/rsc/server-components
- Rules of Hooks: https://react.dev/warnings/invalid-hook-call-warning
- You Might Not Need an Effect: https://react.dev/learn/you-might-not-need-an-effect
- Web.dev Core Web Vitals: https://web.dev/vitals/
