---
name: angular-performance-patterns
description: >-
  Diretrizes enterprise de engenharia de performance para Angular (v17–v21+):
  Zoneless change detection, fine-grained reactivity com Signals, @defer views,
  SSR com incremental hydration e event replay, Core Web Vitals (INP/LCP/CLS),
  NgOptimizedImage, bundle budgets e prevenção de memory leaks.
tier: 2
category: quality
triggers:
  - "performance angular"
  - "otimização angular"
  - "zoneless angular"
  - "core web vitals angular"
  - "inp angular"
  - "lcp angular"
  - "incremental hydration"
  - "defer views"
  - "signals performance"
  - "memory leak angular"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/angular/angular-router.agent.md
tools: []
---

# Angular Performance Patterns

> Base de conhecimento especializada em **engenharia de performance frontend** para aplicações Angular modernas (v17 a v21+). Utilizada pelo `@angular-engineer` em modo Advisory (auditoria, diagnóstico de gargalos) e Implementação (aplicação direta de código otimizado).

## Quando Usar

- Ao projetar ou refatorar componentes para Zoneless Change Detection.
- Ao otimizar Core Web Vitals (especialmente INP < 200ms, LCP < 2.5s e CLS < 0.1).
- Ao estruturar carregamento sob demanda com `@defer` e SSR com hidratação incremental.
- Ao auditar bundle size, tree-shaking e tempos de compilação.
- Ao investigar vazamento de memória (subscrições RxJS zumbis, retaining trees no DOM).

---

## Pilares Técnicos de Performance

### 1) Zoneless Change Detection e Reatividade Fina (Signals)

- **Eliminação de Zone.js**:
  Configurar `provideZonelessChangeDetection()` (ou experimental nas v18/v19) em `app.config.ts`. Remove ~35 KB do bundle inicial e elimina varreduras top-down cegas de CD na árvore.
- **Grafo de Dependências de Signals**:
  Preferir `signal()`, `computed()`, `linkedSignal()` e `resource()` / `rxResource()`.
  O `computed()` opera com memoização e avaliação lazy: só recalcula quando o sinal dependente é lido e sofre mutação real.
- **Isolamento de Efeitos**:
  Nunca usar `effect()` para sincronização de estado derivado (gera ciclos de renderização extras); reservar para interações imperativas externas (DOM, Web APIs, logging).

```typescript
// app.config.ts — Zoneless bootstrap
export const appConfig: ApplicationConfig = {
  providers: [provideZonelessChangeDetection()]
};
```

### 2) Deferrable Views (`@defer`) e Incremental Hydration

- **Code-Splitting Declarativo**:
  Embalar blocos pesados ou fora da viewport inicial com `@defer (on viewport; prefetch on idle)`.
- **Incremental Hydration (SSR)**:
  Ativar `withIncrementalHydration()` junto a `provideClientHydration()`. Permite `@defer (hydrate on interaction)`: o HTML SSR permanece estático até a interação do usuário.
- **Event Replay**:
  O event replay captura cliques e inputs no HTML inerte antes do download do chunk JS e dispara replay automático sem perda de ação do usuário.

```html
<!-- Defer com hidratação sob interação e prefetch quando ocioso -->
@defer (hydrate on interaction; prefetch on idle) {
  <app-grafico-pesado [dados]="dados()" />
} @placeholder {
  <div class="skeleton-loader" aria-hidden="true"></div>
}
```

### 3) Core Web Vitals: INP, LCP e CLS

- **INP (Interaction to Next Paint ≤ 200ms)**:
  - Particionar processamento síncrono em chunks pequenos (`scheduler.yield()` ou `requestAnimationFrame`).
  - Utilizar `@defer` para evitar blocos monolíticos de hidratação na main thread.
- **LCP (Largest Contentful Paint ≤ 2.5s)**:
  - Imagem hero obrigatória com `NgOptimizedImage` e atributo `priority` (gera prefetch e `fetchpriority="high"`).
  - Nunca aplicar lazy-loading (`loading="lazy"`) na imagem principal LCP.
- **CLS (Cumulative Layout Shift ≤ 0.1)**:
  - Sempre declarar `width` e `height` explícitos ou `fill` com `aspect-ratio` no container CSS.
  - Reservar espaço visual via `@placeholder` com dimensões idênticas ao componente real.

```html
<!-- Exemplo conceitual de imagem LCP com NgOptimizedImage -->
<img ngSrc="banner.webp" width="1200" height="600" priority alt="Destaque">
```

### 4) Bundle Budgets, Tree-Shaking e Application Builder

- **Application Builder (esbuild/Vite)**:
  Garante tree-shaking agressivo, bundling ESM e compilação incremental de alta velocidade.
- **Orçamentos Rígidos (`angular.json`)**:
  - `initial`: `maximumWarning: 500kb`, `maximumError: 1mb`.
  - `anyComponentStyle`: `maximumWarning: 4kb`, `maximumError: 8kb`.
  - Lazy chunks: manter < 50 KB gzip por rota/bloco `@defer`.
- **Imports Cirúrgicos**:
  Importar apenas submódulos e símbolos necessários (evitar imports globais de bibliotecas de terceiros).

### 5) Prevenção de Memory Leaks e Ciclo de Vida

- **`takeUntilDestroyed` no Constructor/Injection Context**:
  Descarta subscrições RxJS automaticamente ao destruir o componente ou serviço.
- **`DestroyRef` para Limpezas Explícitas**:
  Usar `DestroyRef.onDestroy(() => ...)` para encerramento de timers, listeners de ResizeObserver, MutationObserver ou WebSockets.

```typescript
// Descarte seguro de subscrição e listeners
class ExemploComponent {
  private readonly destroyRef = inject(DestroyRef);
  dados$ = this.servico.stream$.pipe(takeUntilDestroyed());
}
```

---

## Checklist Verificável

- [ ] Componente novo/refatorado adota Signals para estado reativo local e derivado (`computed`).
- [ ] Componentes pesados ou fora da dobra usam `@defer` com `@placeholder` dimensionado.
- [ ] Nenhuma subscrição manual em RxJS sobrevive sem `takeUntilDestroyed` ou `async` pipe.
- [ ] Imagens críticas possuem `NgOptimizedImage` com `priority` e dimensões explícitas.
- [ ] `angular.json` possui limites de bundle declarados e respeitados pelo build de produção.
- [ ] Zoneless habilitado sem regressão em eventos assíncronos ou third-party.

---

## Anti-padrões

| Anti-padrão | Impacto | Correção Recomendada |
|---|---|---|
| Chamar métodos em templates (`{{ calcular() }}`) | Reavaliação a cada tick de CD, CPU spiking | Substituir por `computed()` memoizado |
| `loading="lazy"` na imagem LCP | Atraso grave no LCP (+1.5s a +3s) | Usar `NgOptimizedImage` com `priority` |
| `effect()` mutando outros signals | Loops infinitos e cascata de renderização | Usar `computed()` ou `linkedSignal()` |
| Subscrição sem teardown no destroy | Memory leak cumulativo na SPA | `takeUntilDestroyed()` ou `DestroyRef` |
| Importar lib inteira (ex.: `lodash`) | Bundle bloat (+100 KB desnecessários) | Importar funções específicas ou tree-shakable |

---

## Referências Oficiais

- Angular Docs: *Incremental Hydration Guide* (https://angular.dev/guide/incremental-hydration)
- Angular Docs: *Optimizing Images with NgOptimizedImage* (https://angular.dev/guide/image-optimization)
- Angular Experts: *Zoneless Angular Guide* (https://angularexperts.io/blog/zoneless-angular)
- Google Web Vitals: *Optimize INP, LCP, CLS* (https://web.dev/explore/metrics)

