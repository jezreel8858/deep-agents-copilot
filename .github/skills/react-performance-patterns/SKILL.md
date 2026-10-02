---
name: react-performance-patterns
description: >-
  Diretrizes de performance e Core Web Vitals para aplicações React (React Compiler,
  code-splitting, streaming SSR, memoização orientada a medição).
tier: 2
category: quality
triggers:
  - "performance react"
  - "core web vitals react"
  - "react compiler"
  - "code splitting"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/react/react-arch-advisor.agent.md
tools: []
---

# React Performance Patterns

## Quando Usar

- Ao auditar performance de uma aplicação React (LCP, INP, CLS).
- Ao avaliar necessidade real de memoização manual (`useMemo`/`useCallback`/`React.memo`).
- Ao planejar code-splitting route-based ou adocção de streaming SSR.

## Diretrizes

- Metas de Core Web Vitals: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1.
- React Compiler (estável desde 2025) torna memoização manual majoritariamente desnecessária; reserve `useMemo`/`useCallback`/`React.memo` para casos medidos via Profiler.
- Code-splitting route-based reduz 60-80% do bundle inicial em aplicações grandes.
- Streaming SSR com Suspense reveals substitui o modelo `useEffect`+`setState` para data fetching.

## Checklist

- [ ] Métricas de CWV medidas antes e depois de otimizações estruturais.
- [ ] Memoização manual justificada por Profiler, não especulativa.
- [ ] Rotas pesadas usam code-splitting (`React.lazy`/`import()`dinâmico).
- [ ] Imagens críticas para LCP usam carregamento otimizado (`loading="eager"`/`priority`).

## Referências

- Web.dev Core Web Vitals: https://web.dev/vitals/
- React Compiler: https://react.dev/learn/react-compiler
