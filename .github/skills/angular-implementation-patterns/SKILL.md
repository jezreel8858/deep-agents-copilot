---
name: angular-implementation-patterns
description: >-
  Padrões de mercado consolidados (2026) para IMPLEMENTAR features novas e
  correções de bug em Angular — fronteira Signals/RxJS, workflow testing-first,
  diffs mínimos e checklist de PR. Contraparte de execução da
  `angular-frontend-patterns` (que é só análise/recomendação).
tier: 2
category: quality
triggers:
  - "implementar componente angular"
  - "corrigir bug angular"
  - "feature angular nova"
  - "codar angular"
  - "signals implementation"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/angular/angular-router.agent.md
  - .github/skills/angular-frontend-patterns/SKILL.md
tools: []
---

# Angular Implementation Patterns

## Quando Usar

- Ao implementar feature nova (componente, service local, rota) em Angular.
- Ao corrigir bug com evidência de causa raiz já localizada no código.
- Ao decidir fronteira Signals vs RxJS **durante a escrita do código** (não só na análise).

## Fronteira de Estado (regra de mercado 2026)

| Camada | Ferramenta | Regra |
|---|---|---|
| Estado síncrono, escopo de feature | `signal()`/`computed()` | Padrão default — nunca recriar RxJS manualmente para isso |
| Orquestração assíncrona (HTTP, streams) | RxJS + `resource()`/`rxResource()`/`httpResource()` | Mantém async loading fora de signals cruas |
| Estado cross-feature genuíno | Store dedicado com provider route-scoped | Exceção documentada — nunca default |

## Workflow — Feature Nova

1. Confirmar escopo com `@requirements-analyst`/handoff recebido (critério de aceite testável).
2. Escrever teste(s) que descrevem o comportamento esperado antes do componente/service (testing-first).
3. Implementar com **standalone components**, `ChangeDetectionStrategy.OnPush`, `inject()`.
4. Aplicar convenções do adapter do projeto (`.github/instructions/<projeto>-frontend.instructions.md` ou `frontend.instructions.md` genérico) para naming, SCSS e organização.
5. Rodar suíte local (`ng test`/Vitest conforme projeto) — nunca reportar sucesso sem rodar.
6. `get_errors` no(s) arquivo(s) editado(s).

## Workflow — Correção de Bug

1. Exigir causa raiz com evidência (`arquivo:linha`) — se ausente, delegar para `@bug-triage` primeiro.
2. Reproduzir a falha em teste antes de corrigir (evita regressão).
3. Aplicar diff mínimo — nunca reescrever componente inteiro para 1 bug.
4. Validar que o teste que reproduzia a falha agora passa + suíte do módulo intacta.

## Padrões de Código (mercado 2026)

| Prática | Diretriz | Evidência de conformidade |
|---|---|---|
| Componentes | Standalone, pequenos, `OnPush`, `trackBy`/`track` obrigatório em `@for` | Sem `NgModule` novo; template sem lógica complexa |
| Formulários | Signal Forms quando disponível na versão do projeto; Reactive Forms como fallback estável | Migração incremental, nunca big-bang |
| Dados assíncronos | `resource()`/`httpResource()` para loading declarativo | Sem `subscribe()` manual não gerenciado |
| Imagens | `NgOptimizedImage` (`[ngSrc]`) em imagens críticas para LCP | Presença de `ngSrc` em novas imagens |
| Lazy loading | `loadComponent`/`@defer` para código não crítico na viewport inicial | Bundle splitting visível no build |
| Lint | ESLint (não TSLint, deprecado) | `.eslintrc`/`eslint.config.js` presente |

## Testing-First (obrigatório)

- Runner: o já configurado no projeto (`ng test`, Vitest nativo em Angular 20+, ou Jasmine/Karma legado) — consultar `test-implementation-angular-vitest`/`test-implementation-angular-jasmine`.
- Nenhuma implementação é considerada concluída sem teste executado e resultado reportado.
- Cobertura mínima do trecho alterado, não da suíte inteira (diff coverage).

## Checklist de PR (implementação)

- [ ] Teste novo/atualizado cobre o comportamento implementado ou corrigido.
- [ ] `OnPush` + `track`/`trackBy` aplicados onde há listas/loops.
- [ ] Sem lógica de negócio relevante no template.
- [ ] Convenções do adapter do projeto respeitadas (SCSS, naming, estrutura).
- [ ] `get_errors` limpo no(s) arquivo(s) tocado(s).
- [ ] Diff mínimo — sem refactor oportunista fora do escopo pedido.

## Anti-padrões

- ❌ Implementar sem teste (viola testing-first).
- ❌ Recriar manualmente com Signals o que RxJS já resolve em orquestração assíncrona.
- ❌ Reescrever componente inteiro para corrigir 1 bug pontual.
- ❌ Ignorar convenções do adapter do projeto em favor de preferência pessoal.
- ❌ Reportar "concluído" sem rodar a suíte de teste local.

## Referências

- Angular Roadmap 2026 (Signal Forms, `resource()`/`httpResource()`, Vitest como runner primário): https://angular.dev/roadmap
- Angular Style Guide: https://angular.dev/style-guide
- Angular Best Practices 2026 (Ideas2IT): https://www.ideas2it.com/blogs/angular-development-best-practices
- Angular Signals Enterprise State Management 2026: https://modernfrontendarchitecture.com/articles/angular-signals-enterprise-state

