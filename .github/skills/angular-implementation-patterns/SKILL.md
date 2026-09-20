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
  - .github/skills/frontend-visual-feedback-loop/SKILL.md
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

0. **Reuse-First & Protocolo "Canonical Sibling First" (obrigatório antes de qualquer HTML/CSS novo)**:
   - **Inventário e Reuso**: inventariar `shared/components/` e a documentação interna de design system do projeto (ex.: `docs/*componentes*`/`docs/*padrao*`) — reaproveitar componentes/tokens existentes (cards, filtros, badges, diálogos, form fields) é preferencial a criar padrão customizado (Smell 2.19).
   - **Leitura Estrita da Definição TypeScript (`.ts`)**: ao consumir qualquer componente de `shared/`, ler compulsoriamente seu arquivo `.component.ts` para mapear nomes reais e tipos dos `@Input()`/`input()`. NUNCA presumir propriedades em inglês (`[icon]`, `[title]`) quando o design system padroniza em português (`[icone]`, `[titulo]`), evitando que o Angular trate atributos não mapeados como atributos HTML nativos sem acusar erro de compilação (Smell 2.21).
   - **Inspeção por Paridade (Canonical Sibling First)**: antes de escrever qualquer `*DialogComponent` ou `*PageComponent` novo, ler um componente equivalente 100% funcional no repositório para clonar hierarquia de tags, grid responsivo de 2 colunas, envelopamento de empty-state e classes utilitárias de scroll (`.app-dialog-content`, `.form-grid`).
   - **Zero Cores Hexadecimais**: proibido utilizar cores hexadecimais arbitrárias inline em SCSS de feature; utilizar estritamente variáveis CSS de tema ou tokens semânticos do projeto.
   - **Auditoria de Padrão de UI**: Se o projeto tiver script de auditoria de padrão de UI (ex.: `npm run <lint-de-padrao-ui>`), executá-lo antes de reportar conclusão.
1. Confirmar escopo com `@requirements-analyst`/handoff recebido (critério de aceite testável).
2. **Implementar a funcionalidade primeiro (Implementation-First)**: construir com **standalone components**, `ChangeDetectionStrategy.OnPush`, `inject()` e Signals.
3. Aplicar convenções do adapter do projeto (`.github/instructions/<projeto>-frontend.instructions.md` ou `frontend.instructions.md` genérico) para naming, SCSS e organização.
4. Validar compilação limpa via `get_errors` no(s) arquivo(s) editado(s).
5. **Test-Last com Verification Gate Obrigatório**: após a estabilização da lógica/componente, escrever os testes unitários/componentes necessários (ou delegar aos especialistas de teste `@angular-unit-test-writer` / `@angular-component-test-writer`), eliminando o atrito de runners prematuros e mocks efêmeros durante a fase de prototipagem/desenvolvimento. Tarefas puramente de UI/estilização (`@angular-ui-stylist`) são **isentas** de criação/execução de testes unitários.
6. Rodar suíte local com flags silenciosas e filtro de ruído quando da validação final do módulo.
7. **Navegabilidade (Definition of Done)**: se a feature introduziu nova(s) rota(s), localizar o(s) componente(s) de shell de navegação do projeto (menu lateral, sidenav, tab-bar, breadcrumb) e registrar a nova entrada de acesso — uma rota sem ponto de entrada de navegação correspondente é considerada **incompleta**, mesmo com testes verdes e build íntegro.

## Workflow — Correção de Bug

1. Exigir causa raiz com evidência (`arquivo:linha`) — se ausente, delegar para `@bug-triage` primeiro.
2. **Rastrear de fora para dentro**: auditar o momento de montagem no DOM (`@if` no componente pai) e o ciclo de vida das entradas (`input()`) antes de alterar a máquina de estados interna do filho.
3. **Não mascarar o sintoma visual**: proibido forçar flags de prontidão/loading (`isLoading = false`) para sumir com spinners; resolver a Promise ou stream subjacente que não resolveu.
4. **Respeitar invariantes e contratos**: garantir que o fluxo produtor emita estado terminal em todos os ramos (sucesso, erro ou vazio), sem nunca afrouxar travas ou validações de componentes consumidores vizinhos.
5. **Zero band-aids imperativos**: proibido usar `setTimeout` para destravar streams; usar operadores declarativos nativos ou corrigir o gatilho na raiz.
6. **Correção Cirúrgica Primeiro (Implementation-First)**: aplicar diff mínimo localizado na causa raiz sem travar o fluxo em reexecuções de runner.
7. Validar compilação limpa com `get_errors`.
8. **Test-Last de Regressão**: criar/executar o teste de regressão comprovando o fix e garantindo a não-regressão do módulo antes de reportar conclusão.

## Padrões de Código (mercado 2026)

| Prática | Diretriz | Evidência de conformidade |
|---|---|---|
| Componentes | Standalone, pequenos, `OnPush`, `trackBy`/`track` obrigatório em `@for` | Sem `NgModule` novo; template sem lógica complexa |
| Formulários | Signal Forms quando disponível na versão do projeto; Reactive Forms como fallback estável | Migração incremental, nunca big-bang |
| Dados assíncronos | `resource()`/`httpResource()` para loading declarativo | Sem `subscribe()` manual não gerenciado |
| Imagens | `NgOptimizedImage` (`[ngSrc]`) em imagens críticas para LCP | Presença de `ngSrc` em novas imagens |
| Lazy loading | `loadComponent`/`@defer` para código não crítico na viewport inicial | Bundle splitting visível no build |
| Lint | ESLint (não TSLint, deprecado) | `.eslintrc`/`eslint.config.js` presente |

## Estratégia de Testes Frontend: Test-Last com Verification Gate Obrigatório

- **Desacoplamento de UI vs Lógica**: Tarefas e agentes de UI/estilização pura (`@angular-ui-stylist`) são **ISENTOS** de criar ou rodar testes unitários (validação é visual via Visual Feedback Loop / DOM inspection, design tokens e acessibilidade).
- **Test-Last Pragmático**: Componentes e services são implementados e estabilizados primeiro (`Implementation-First`); testes unitários e de integração são criados ao final pelos especialistas de teste (`@angular-unit-test-writer`), evitando context thrashing e reescrita de testes contra DOM instável.
- **Verification Gate**: Nenhuma entrega é submetida a PR sem suíte de regressão verde no quality gate final.
- Runner: o já configurado no projeto (`ng test`, Vitest nativo em Angular 20+, ou Jasmine/Karma legado) — consultar `test-implementation-angular-vitest`/`test-implementation-angular-jasmine`.
- Cobertura mínima do trecho alterado, não da suíte inteira (diff coverage).

## Checklist de PR (implementação)

- [ ] Teste novo/atualizado cobre o comportamento implementado ou corrigido.
- [ ] Protocolo "Canonical Sibling First" executado: componente irmão canônico inspecionado antes de escrever o template/estilo (Smell 2.21).
- [ ] Contratos de componentes `shared/` consumidos validados diretamente em seus arquivos `.ts` (sem suposição de props em inglês).
- [ ] Zero cores hexadecimais arbitrárias inline nos arquivos SCSS (apenas variáveis de tema/design tokens — Smell 2.21).
- [ ] Diálogos utilizam classes utilitárias de scroll e layout padrão do projeto (sem larguras máximas inline arbitrárias).
- [ ] Estados vazios envelopados com largura total na seção correspondente.
- [ ] `OnPush` + `track`/`trackBy` aplicados onde há listas/loops.
- [ ] Sem lógica de negócio relevante no template.
- [ ] Convenções do adapter do projeto respeitadas (SCSS, naming, estrutura).
- [ ] `get_errors` limpo no(s) arquivo(s) tocado(s).
- [ ] Diff mínimo — sem refactor oportunista fora do escopo pedido.
- [ ] Toda nova rota está alcançável via componente de navegação do projeto (menu/sidenav/tabs) — não apenas via URL direta (Smell 2.18).
- [ ] Nenhum padrão visual novo (card, filtro, diálogo, badge, select) foi criado sem antes verificar componentes/design system compartilhados já existentes no projeto (Smell 2.19).

## Anti-padrões

- ❌ Implementar sem teste (viola testing-first).
- ❌ Recriar manualmente com Signals o que RxJS já resolve em orquestração assíncrona.
- ❌ Reescrever componente inteiro para corrigir 1 bug pontual.
- ❌ Ignorar convenções do adapter do projeto em favor de preferência pessoal.
- ❌ Reportar "concluído" sem rodar a suíte de teste local.
- ❌ Entregar rota/feature nova sem vínculo em menu/sidenav/navegação — usuário final não consegue alcançar a funcionalidade (Smell 2.18).
- ❌ Recriar em HTML/CSS customizado um padrão (card, filtro, diálogo, badge) que já existe como componente compartilhado documentado no projeto (Smell 2.19).
- ❌ Presumir contratos/inputs de componentes compartilhados em inglês sem abrir e ler o arquivo `.ts` correspondente (Smell 2.21).
- ❌ Adicionar cores hexadecimais inline em arquivos SCSS de features em vez de tokens de tema (Smell 2.21).
- ❌ Implementar telas ou diálogos "do zero" sem inspecionar um componente irmão funcional homologado (violação do "Canonical Sibling First").
- ❌ Declarar entrega concluída baseando-se unicamente em compilação e testes unitários headless sem auditar paridade de layout e contratos de UI (cegueira visual).
- ❌ Forçar flags de `isLoading = false` ou `isDone = true` para desligar spinners visuais sem resolver a Promise ou Observable de fundo (mascarar sintoma).
- ❌ Adicionar temporizadores artificiais (`setTimeout`) como band-aid para contornar streams reativos inertes.
- ❌ Afrouxar regras de validação ou travas de segurança de componentes consumidores para mascarar a ausência de resposta do componente produtor.
- ❌ Ignorar a renderização condicional do componente pai (`@if` tardio) que faz o componente filho perder eventos de carga já transitados no barramento.

## Referências

- Angular Roadmap 2026 (Signal Forms, `resource()`/`httpResource()`, Vitest como runner primário): https://angular.dev/roadmap
- Angular Style Guide: https://angular.dev/style-guide
- Angular Best Practices 2026 (Ideas2IT): https://www.ideas2it.com/blogs/angular-development-best-practices
- Angular Signals Enterprise State Management 2026: https://modernfrontendarchitecture.com/articles/angular-signals-enterprise-state

