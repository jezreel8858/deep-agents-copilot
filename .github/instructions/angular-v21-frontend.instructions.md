---
applyTo: ["**/*.ts", "**/*.js"]
---
# Regras de estilo do Angular

> Resumo consolidado das convenções de frontend para projetos Angular. Use este documento como referência principal para padrões Angular; consulte `CLAUDE.md` e `.github/copilot-instructions.md` apenas para governança geral.
>
> **Instruções genéricas**: este arquivo é reutilizável por qualquer projeto Angular. Customizações específicas de projeto devem ser adicionadas via adapter próprio em `.github/instructions/<projeto>-angular-v21-frontend.instructions.md`.

Objetivo: concentrar boas práticas e regras de estilo para projetos Angular (incluindo notas específicas para Angular 21), cobrindo arquitetura, tooling, performance, segurança e testes.

Escopo: código TypeScript/JS, configuração (tsconfig/angular.json), build, testes e operação do frontend.

## 1) Versão e compatibilidade

- Angular 21 (v21) traz zoneless como default para novas aplicações e avanços em Signals; revise o guia de migração (`ng update`) antes de subir de versão.
- Ative `"strict": true` em `tsconfig.json` e use tipos estritos para minimizar bugs em runtime.
- Antes de usar APIs específicas, valide a versão real em `package.json` e `angular.json`.

## 2) Arquitetura e Change Detection

- Prefira componentes standalone e `ChangeDetectionStrategy.OnPush` quando o projeto permitir.
- Adote `inject()` e Signals como padrão em código novo; use `input()`, `output()`, `model()` e `viewChild()` quando fizer sentido.
- Em templates novos, prefira `@if`, `@for` e `@switch`; em `@for`, `track` é obrigatório.
- Use `@defer` para carregamento sob demanda de componentes pesados ou não críticos na viewport inicial.
- Use `NgOptimizedImage` (`[ngSrc]`) para imagens novas ou críticas para LCP eficiente.
- Centralize autenticação e tratamento de erros em `HttpInterceptor`.

## 3) Ciclo de vida, estado e subscriptions

- `constructor` deve ser usado exclusivamente para injeção de dependência.
- Toda lógica de inicialização (subscriptions, chamadas iniciais que dependem de `@Input`) deve ficar em `ngOnInit`.
- Prefira fluxo declarativo e `| async` sempre que possível.
- Para subscriptions imperativas, use `@ngneat/until-destroy` (`@UntilDestroy()` + `pipe(untilDestroyed(this))`) ou `Subject` + `takeUntil(this.destroy$)` quando UntilDestroy não estiver adotado.
- Evite `any`; defina interfaces estritas para retornos de APIs e estados locais.

## 4) Reutilização e organização

- **Protocolo "Canonical Sibling First"**: antes de criar qualquer tela ou diálogo novo, inspecionar compulsoriamente um componente irmão canônico homologado no projeto para replicar tags, grids de formulário e classes utilitárias de scroll.
- **Contratos Reais de Componentes Compartilhados**: ao consumir componentes de `shared/`, ler compulsoriamente a definição TypeScript (`.component.ts`) para confirmar os nomes reais e tipos dos `@Input()`/`input()`. NUNCA presumir propriedades em inglês (`[icon]`, `[title]`) quando o projeto adotar português (`[icone]`, `[titulo]`), evitando atributos HTML órfãos ignorados silenciosamente (Smell 2.21).
- Funções puras e reutilizáveis devem ser movidas para classes `*Util` com métodos `static`.
- Métodos longos devem ser extraídos para privados bem nomeados.
- Componentes com lógica relevante (>200 linhas, múltiplas chamadas de API ou regras de cruzamento de dados) devem ter um `*.service.ts` local no próprio escopo.
- O service local orquestra chamadas de API, regras de cruzamento/filtragem de dados e montagem de filtros/payloads; o componente fica com o estado da UI.
- Para telas que persistem dados, mantenha snapshot inicial do estado carregado e só habilite o submit quando houver alteração.

## 5) SCSS e estilização

- **Proibição de Hex Inline**: proibido usar cores hexadecimais arbitrárias inline em SCSS de features (`#...`); utilizar estritamente variáveis CSS de tema ou tokens semânticos do projeto (Smell 2.21).
- **Layout de Diálogos e Grids**: diálogos devem utilizar classes utilitárias de scroll e grid responsivo de 2 colunas do projeto (`.app-dialog-content`, `.form-grid`) em vez de larguras fixas arbitrárias inline.
- **Empty States**: componentes de estado vazio devem ser posicionados no container de seção para herdar largura total, evitando caixas colapsadas no centro da tela.
- Inclua sempre um fallback genérico em `font-family`.
- Use `:host` e `::ng-deep` com parcimônia; prefira estilos encapsulados quando possível.

## 6) Testes e cobertura

- Prefira os runners já configurados no projeto (`ng test`, `test-ci`, `test-coverage` e Playwright para E2E); só migre para Vitest após validação explícita.
- Nomes de `describe` e `it` em Português (Brasil), no formato: "deve [ação] quando [condição]".
- Mockar todas as dependências injetadas com `jasmine.createSpyObj`.
- Quando necessário, use `as unknown as Tipo` para tipar mocks complexos.
- Evite testar membros privados; se estritamente necessário, acesse via `(component as any).privateMember` com comentário justificando.
- Todo novo código de teste deve buscar 100% de cobertura do arquivo alvo (linhas, ramos e funções).

## 7) Documentação de componentes

- Todo componente de média/alta complexidade deve ter um arquivo `<nome-do-componente>.component.md` na mesma pasta do componente.
- O arquivo de documentação deve ser atualizado na mesma entrega quando fluxo público ou regra de negócio mudar.
- Quando necessário, documente visão geral, fluxo de inicialização, regras de negócio, modelos de dados e fluxos de persistência com Mermaid.
- Mantenha a divisão de responsabilidades entre componente, service local e documentação de apoio.

## 8) Boas práticas rápidas

- Use `async` pipe e evite `subscribe()` manual quando possível; se necessário, gerencie unsubscription com `takeUntil` ou `Signals`.
- Prefira testes unitários rápidos (Jasmine/Karma) e testes E2E separados (Playwright).
- Mantenha regras ESLint compartilhadas e CI que falhe em linting ou testes quebrados.
- Consulte a documentação específica de feature/componente quando existir antes de mudar uma regra de negócio.

## Exemplos curtos

- Criar app com strict:
```
ng new meu-app --routing --style=scss --strict
```

- tsconfig.json (trecho):
```
{
  "compilerOptions": { "strict": true, "forceConsistentCasingInFileNames": true }
}
```

## Referências da convenção consolidada

- `CLAUDE.md` e `.github/copilot-instructions.md` para governança global.
- Este documento para as convenções genéricas de frontend Angular.
- `package.json` e `angular.json` para validação de versão, scripts e configuração do projeto.
- Adapter específico do projeto (ex.: `.github/instructions/<projeto>-angular-v21-frontend.instructions.md`) para customizações por projeto.
- Documentação específica de feature/componente quando existir.

Fontes selecionadas
- Angular v21 Release — https://angular.dev/events/v21
- Angular Style Guide — https://angular.dev/guide/styleguide
- Update Guide — https://angular.dev/update-guide
- Documentação oficial Angular — https://angular.dev
