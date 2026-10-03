---
applyTo: ["**/*.tsx", "**/*.jsx", "**/*.ts", "**/*.js"]
---
# Regras de estilo do React

> Resumo consolidado das convenções de frontend para projetos React moderno (React 19+). Use este documento como referência principal para padrões React; consulte `CLAUDE.md` e `.github/copilot-instructions.md` apenas para governança geral.
>
> **Instruções genéricas**: este arquivo é reutilizável por qualquer projeto React. Customizações específicas de projeto devem ser adicionadas via adapter próprio em `.github/instructions/<projeto>-react-frontend.instructions.md`.

Objetivo: concentrar boas práticas e regras de estilo para projetos React (incluindo notas específicas para React 19+), cobrindo arquitetura, state management, roteamento, estilização, testes, performance e acessibilidade.

Escopo: código TypeScript/JSX/TSX, configuração (tsconfig/vite.config), build, testes e operação do frontend.

## 1) Versão e compatibilidade

- React 19+ traz Server Components estáveis, o hook `use()`, Actions e o React Compiler (estável desde out/2025) como padrão de mercado.
- Ative `"strict": true` em `tsconfig.json` e use tipos estritos para minimizar bugs em runtime.
- Antes de usar APIs específicas, valide a versão real em `package.json`.

## 2) Arquitetura: Server Components vs Client Components

- Server Component é o **default**; use `'use client'` **somente** quando houver interatividade, estado local ou APIs de browser.
- O boundary de `'use client'` é de **módulo** (propaga para todos os imports) — mantenha o boundary próximo das folhas da árvore ("wrap, don't import").
- Hooks seguem as regras canônicas (topo do componente/custom hook); exceção do `use()` (React 19) pode estar em condicional/loop, mas nunca em `try/catch`.
- Data fetching: prefira `async/await` direto em Server Component com `cache()`; use `use()` para ler Promises/Context com `Suspense`. Evite `useEffect`+`setState` para fetch quando houver alternativa declarativa.

## 3) Gerenciamento de estado (padrão consolidado 2025/2026)

- **Server state**: TanStack Query é o padrão inquestionável de mercado (`useQuery`/`useMutation`, invalidação de cache). Nunca duplicar dados de servidor em store de cliente.
- **Client/UI state**: Zustand é a tendência dominante para apps pequenos/médios (stores leves, sem boilerplate de actions/reducers).
- Redux Toolkit permanece recomendado para apps enterprise grandes que exijam time-travel debugging; Jotai para estado atômico granular em casos de nicho.
- Critério de escolha: server state sempre TanStack Query; client state Zustand por padrão; Redux Toolkit apenas com justificativa de escala/debugging; Jotai para granularidade atômica específica.

## 4) Roteamento (decisão contextual)

- Não há vencedor único consolidado: **React Router v7** tem maior adorção/ecossistema e SSR nativo; **TanStack Router** oferece type-safety ponta a ponta e integração nativa com TanStack Query.
- Documente o critério de escolha no `react-arch-advisor` do projeto em vez de impor um padrão fixo.

## 5) Performance e Core Web Vitals

- Metas: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1.
- O **React Compiler** (estável) torna memoização manual majoritariamente desnecessária; reserve `useMemo`/`useCallback`/`React.memo` para casos medidos via Profiler.
- Code-splitting route-based (`React.lazy`/`import()` dinâmico) reduz 60-80% do bundle inicial.
- Streaming SSR com Suspense reveals substitui o modelo `useEffect`+`setState` para data fetching.

## 6) Estilização

- **Tailwind CSS** é o padrão de mercado para projetos greenfield (utility-first, compatível com RSC).
- **CSS Modules** quando o projeto exigir encapsulamento estrito ou for agnóstico de framework.
- Evite CSS-in-JS runtime (styled-components/Emotion) em árvores com Server Components — incompatibilidade estrutural (sem contexto de browser no servidor, risco de FOUC). Prefira zero-runtime (Panda CSS/StyleX/vanilla-extract) quando theming pesado for necessário.
- Proibido cores hexadecimais arbitrárias inline; use tokens de tema do `tailwind.config`.

## 7) Testes e cobertura (Vitest + RTL + Playwright)

- **Unit/Component**: Vitest + React Testing Library é o padrão consolidado para projetos novos (Vite nativo, ESM, cold start rápido).
- **E2E**: Playwright é o líder de momentum de mercado (multi-browser nativo incl. WebKit, paralelização gratuita); Cypress permanece viável para manutenção de bases existentes.
- Queries de componente por acessibilidade (`getByRole`, `getByLabelText`), nunca `querySelector`.
- Mock de rede via MSW (Mock Service Worker) para interceptar chamadas HTTP de forma realista.
- Nomes de `describe`/`it` em Português (Brasil): "deve [ação] quando [condição]".
- **Higiene de Execução (Zero-Noise)**: proibido rodar testes em modo watch no CI/agentes; usar `vitest run --silent` / `playwright test` com reporter enxuto e filtro via pipe.

## 8) Acessibilidade (WCAG 2.2 AA)

- HTML semântico primeiro, ARIA depois: `role="dialog"` + `aria-modal="true"` em modais com foco gerenciado/restaurado; roving tabindex em tabs/toolbars; `aria-live="polite"` para conteúdo dinâmico, `role="alert"` apenas para erros.
- Camadas de validação: `eslint-plugin-jsx-a11y` (estático) → `jest-axe`/RTL (componente) → `@axe-core/playwright` (E2E) → teste manual de teclado/leitor de tela (insubstituível).

## 9) Reutilização e organização

- **Protocolo "Canonical Sibling First"**: antes de criar qualquer tela ou modal novo, inspecionar compulsoriamente um componente irmão canônico homologado no projeto.
- **Contratos Reais de Componentes Compartilhados**: ao consumir componentes de `shared/`, ler compulsoriamente a definição TypeScript para confirmar nomes reais de props. NUNCA presumir nomes de props sem verificação (Smell 2.21).
- Funções puras e reutilizáveis devem ser movidas para módulos `utils/` dedicados.
- Hooks customizados complexos devem ter nome descritivo (`use<Dominio><Acao>`) e testes unitários associados.

## 10) Boas práticas rápidas

- Evite `useEffect` para sincronização de estado que poderia ser derivação direta no render ("You Might Not Need an Effect").
- Sempre limpe listeners/timers/subscriptions no retorno de `useEffect` (prevenção de memory leaks).
- Mantenha regras ESLint compartilhadas (`eslint-plugin-react-hooks`) e CI que falhe em linting ou testes quebrados.
- Consulte a documentação específica de feature/componente quando existir antes de mudar uma regra de negócio.

## Referências da convenção consolidada

- `CLAUDE.md` e `.github/copilot-instructions.md` para governança global.
- Este documento para as convenções genéricas de frontend React.
- `package.json` para validação de versão, scripts e configuração do projeto.
- Adapter específico do projeto (ex.: `.github/instructions/<projeto>-react-frontend.instructions.md`) para customizações por projeto.
- Documentação específica de feature/componente quando existir.

Fontes selecionadas
- React Docs — Server Components: https://react.dev/reference/rsc/server-components
- React Docs — Rules of Hooks: https://react.dev/warnings/invalid-hook-call-warning
- TanStack Query Docs: https://tanstack.com/query/latest
- Zustand Docs: https://zustand.docs.pmnd.rs/
- Web.dev Core Web Vitals: https://web.dev/vitals/
- Tailwind CSS Docs: https://tailwindcss.com/docs
- Vitest Docs: https://vitest.dev/
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
- Playwright Docs: https://playwright.dev/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
