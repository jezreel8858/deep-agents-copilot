---
name: test-implementation-react-vitest
description: >-
  Padrões de teste unitário e de componente para React com Vitest e React Testing
  Library — mocks isolados, queries acessíveis e boundary de responsabilidade entre
  unit e component tests.
tier: 2
category: quality
triggers:
  - "vitest react"
  - "react testing library"
  - "teste unitario react"
  - "teste componente react"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/react/react-unit-test-writer.agent.md
  - .github/agents/frontend/react/react-component-test-writer.agent.md
tools: []
---

# Test Implementation — React (Vitest + RTL)

## Quando Usar

- Ao escrever testes unitários de hooks/stores/utils (sem DOM) com Vitest.
- Ao escrever testes de componente com React Testing Library (renderização + interação).
- Ao decidir a fronteira entre unit test e component test.

## Como Usar

- Unit test: `vi.fn()`/`vi.spyOn()` para mocks; testar função pura ou hook via `renderHook` apenas quando necessário.
- Component test: `render()` + `@testing-library/user-event`; queries por `getByRole`/`getByLabelText`, nunca `querySelector`.
- Mock de HTTP: preferir MSW (Mock Service Worker) para interceptar chamadas de rede de forma realista.
- Nomes de `describe`/`it` em Português (Brasil): "deve [ação] quando [condição]".
- Execução: `vitest run --silent` (Zero-Noise Test Policy) com pipe filter quando via terminal.

## Checklist

- [ ] Unit tests não montam DOM/componentes (fronteira com component tests respeitada).
- [ ] Component tests usam queries acessíveis, não seletores de implementação.
- [ ] Mocks de rede via MSW, não fetch real.
- [ ] Testes cobrem boundary values e casos de borda, não apenas happy path.
- [ ] `get_errors` limpo após execução.

## Referências

- Vitest Docs: https://vitest.dev/
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
- MSW Docs: https://mswjs.io/
