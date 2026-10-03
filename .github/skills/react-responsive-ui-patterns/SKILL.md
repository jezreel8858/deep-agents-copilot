---
name: react-responsive-ui-patterns
description: >-
  Padrões de estilização Tailwind CSS/CSS Modules, layout responsivo mobile-first e
  acessibilidade WCAG 2.2 AA para componentes React.
tier: 2
category: quality
triggers:
  - "tailwind react"
  - "layout responsivo react"
  - "acessibilidade react"
  - "wcag react"
source_docs:
  - .github/agents/frontend/react/react-ui-stylist.agent.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# React Responsive UI Patterns

## Quando Usar

- Ao estilizar componentes JSX com Tailwind CSS ou CSS Modules.
- Ao validar layout responsivo mobile-first (375px, 768px, 1440px).
- Ao auditar conformidade WCAG 2.2 AA em componentes React.

## Diretrizes

- Tailwind CSS é o padrão de mercado para projetos greenfield; CSS Modules para encapsulamento estrito em codebases agnósticas de framework.
- Evitar CSS-in-JS runtime (styled-components/Emotion) em árvores com Server Components (incompatibilidade estrutural — sem contexto de browser no servidor).
- HTML semântico primeiro, ARIA depois: `role`, `aria-modal`, foco gerenciado/restaurado em modais, roving tabindex em tabs/toolbars, `aria-live="polite"` para conteúdo dinâmico.
- Camadas de validação de acessibilidade: `eslint-plugin-jsx-a11y` (estático) → `jest-axe`/RTL (componente) → `@axe-core/playwright` (E2E) → teste manual de teclado/leitor de tela.

## Checklist

- [ ] Tokens de tema Tailwind usados em vez de cores hexadecimais arbitrárias.
- [ ] Layout validado em 375px, 768px e 1440px.
- [ ] Modais possuem `role="dialog"`, `aria-modal="true"` e gestão de foco.
- [ ] Contraste de cores atende WCAG 2.2 AA.
- [ ] Nenhum teste unitário criado/executado por este especialista (fora de escopo).

## Referências

- Tailwind CSS Docs: https://tailwindcss.com/docs
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- eslint-plugin-jsx-a11y: https://github.com/jsx-eslint/eslint-plugin-jsx-a11y
