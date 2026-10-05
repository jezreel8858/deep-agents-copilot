---
name: test-implementation-frontend
description: 
  Padrões genéricos e agnósticos para implementação de testes em qualquer projeto
  frontend, independente de framework. Define contratos, tipos de teste e estratégias
  de cobertura aplicáveis a qualquer stack client-side.
tier: 2
category: testing
triggers:
  - "testar frontend"
  - "testes de componente"
  - "component test"
  - "frontend testing"
  - "test frontend"
  - "ui testing"
  - "e2e test"
  - "testes de interface"
  - "cobertura frontend"
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
source_docs:
  - .github/skills/test-coverage-governance/SKILL.md
---

# Test Implementation — Frontend (Genérico)

> **Escopo**: padrões **agnósticos de framework** para qualquer projeto frontend.
> Para implementação específica por stack, consulte:
> - `test-implementation-angular-vitest` → Angular 20/21+ + Vitest + TestBed
> - `test-implementation-angular-jasmine` → Angular 21 + Jasmine + Karma (legado)
> - `test-implementation-react-vitest` → React + Vitest + Testing Library
> - *(criar adapter para Vue/Vitest, Svelte quando necessário)*
>
> **Quando usar esta skill**: ao definir estratégia de testes, revisar cobertura
> ou trabalhar em projeto com stack de frontend ainda não catalogada.

## 1) Tipos de Teste — Frontend

```
        ┌──────────────┐
        │  E2E / UI    │  ← Navegação real no browser, lentos
        ├──────────────┤
        │  Integration │  ← Componente + dependências reais ou parciais
        ├──────────────┤
        │  Unit        │  ← Componente isolado, dependências mockadas
        └──────────────┘
```

| Tipo | O Que Testa | Custo | Volume |
|---|---|---|---|
| **Unit** | Lógica de componente isolada | Baixo | Alto |
| **Integration** | Fluxo entre componentes e serviços | Médio | Médio |
| **E2E** | Jornada completa do usuário no browser | Alto | Baixo |

## 2) Padrão AAA (Universal)

```
Arrange  → Montar componente, configurar dependências mockadas, setar props/inputs
Act      → Disparar evento, chamar método, mudar estado
Assert   → Verificar DOM, estado interno, chamadas a serviços
```

## 3) Unit Tests — Conceitos

### O Que Testar em um Componente

```
✅ Testar:
  - Renderização correta dado um estado (inputs/props)
  - Reação a eventos do usuário (click, change, submit)
  - Chamadas corretas aos serviços com parâmetros esperados
  - Estado atualizado após resposta de serviço (sucesso + erro)
  - Exibição/ocultação condicional baseada em lógica de negócio
  - Validação de formulários (campo obrigatório, formato, range)

❌ Não testar:
  - Detalhes internos de implementação (nomes de variáveis privadas)
  - Framework internals (como Angular/React re-renderiza)
  - Estilos CSS (responsabilidade de visual regression)
```

### Isolamento de Dependências

```
Dependência          Substituto no Teste
──────────────       ─────────────────────────────
HTTP Service   →     Spy/Mock que retorna dados fixos
Router         →     Mock de navegação
Auth Service   →     Mock com usuário fixo
Storage        →     Mock de localStorage/sessionStorage
Date/Time      →     Mock de data fixa para determinismo
```

### Cobertura Mínima por Tipo de Lógica

| Tipo de Lógica | Cobertura Mínima | Prioridade |
|---|---|---|
| Regra de negócio em componente | 85%+ | ⭐ Alta |
| Formulários e validação | 90%+ | ⭐ Alta |
| Chamadas HTTP (happy + error) | 80%+ | ⭐ Alta |
| Renderização condicional | 75%+ | ✓ Média |
| Utilitários/Pipes/Filters | 80%+ | ✓ Média |
| Componentes puramente visuais | Isento de testes unitários (validação visual/VFL) | ◯ Baixa |

### Metodologia de Execução: Test-Last com Verification Gate
Em ambientes frontend com agentes de IA, o workflow canônico adota **Test-Last (Implementation-First)**: componentes, stores e lógica são estabilizados e validados estaticamente primeiro (`get_errors`), sendo a escrita de testes unitários executada ao final pelos especialistas de teste. Agentes e tarefas focados puramente em UI/estilização (`ui-stylist`) são **isentos** de criar ou rodar testes unitários, validando apenas contratos visuais, design tokens e acessibilidade.

## 4) Integration Tests — Conceitos

### Quando Usar

- Testar comunicação entre componente pai e filho.
- Validar roteamento entre páginas.
- Verificar fluxo completo de um formulário (preencher → submeter → feedback).
- Confirmar que estado global (store) é atualizado corretamente.

## 5) E2E Tests — Conceitos

### Quando Usar

- Validar jornadas críticas do usuário (login, checkout, cadastro).
- Smoke tests em ambiente de staging antes de deploy.
- Regressão de fluxos que envolvem múltiplas páginas.

### Boas Práticas de Seletores

```
Preferência (mais estável → menos estável):
  1. [data-testid="nome-elemento"]   ← MELHOR: semântico e estável
  2. [aria-label="ação"]             ← Bom: acessibilidade
  3. role="button" + texto           ← Aceitável
  4. .class-name                     ← Frágil: muda com refatoração CSS
  5. nth-child / deep nesting        ← EVITAR: muito frágil
```

### 5.1) E2E Tests com Playwright (Padrão Moderno Frontend)

Para validação de jornadas completas de usuário com browsers reais em qualquer stack frontend:

- **Web-First Assertions**: sempre utilizar asserções com auto-waiting assíncrono (`await expect(locator).toBeVisible()`).
- **Isolamento de Estado**: cada teste deve operar com contexto de browser limpo (`browser.newContext()`) ou usuário independente.
- **Seletores Semânticos**: priorizar `page.getByTestId('...')` e `page.getByRole('...')`.

```typescript
// Exemplo canônico Playwright agnóstico
import { test, expect } from '@playwright/test';

test('deve autenticar e redirecionar para tela principal', async ({ page }) => {
  await page.goto('/login');

  await page.getByTestId('input-email').fill('usuario@exemplo.com');
  await page.getByTestId('input-senha').fill('senha123');
  await page.getByRole('button', { name: 'Entrar' }).click();

  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByTestId('painel-resumo')).toBeVisible();
});
```

## 6) Nomenclatura de Testes

```
Formato: [deve] [resultado] [quando] [condição]

Exemplos PT-BR:
  deve renderizar título quando componente inicializa
  deve chamar serviço quando botão clicado
  deve exibir erro quando requisição falha
  deve desabilitar submit quando formulário inválido
  deve redirecionar para dashboard quando login bem-sucedido
```

### 6.1) Execução de Testes com Zero Ruído (R-008 / R-049)

Ao validar suites de teste frontend, os agentes de IA devem proteger ativamente a janela de contexto contra poluição de logs (INFO, download de dependências e banners de build):

1. **Prioridade 1 — Sandbox `ctx_execute` (Think-in-Code)**: Execute o runner de teste (`vitest`, `jest`, `playwright`) dentro do sandbox isolado. Capture stdout/stderr em código, filtre linhas de compilação/pass e imprima apenas o resumo de testes ou stack traces estritos de falha.
2. **Prioridade 2 — Terminal Silencioso com Filtro**: Se executar diretamente no terminal via `run_in_terminal`, é **OBRIGATÓRIO** usar a flag silenciosa da stack (`--silent`, `--reporter=basic`, `-q`) e canalizar a saída através de filtro (`grep -E "FAIL|PASS|Tests"`) limitado a 40 linhas (`head -40`).
3. **Proibição Absoluta**: É terminantemente proibido executar comandos de teste "bare" (`npm test`, `ng test`, `npx vitest`) em modo watch ou sem flags de supressão de ruído.

### 6.2) Snapshot Testing (Regressão Visual Estruturada)

- **Quando Usar**: validação de integridade estrutural de árvores de marcação complexas (SVG, templates HTML renderizados sem estado mutável frequente).
- **Quando NÃO Usar**: testes de comportamento, lógica condicional de negócio ou asserts de texto simples.
- **Ciclo de Vida**: arquivos `.snap` residem em `__snapshots__/`, devem ser versionados em Git e atualizados conscientemente via flag de update (`--update-snapshots`).

### 6.3) Diagnóstico Cirúrgico e Correção de Falhas (Test Fixer)

- **Regra de Ouro**: NUNCA alterar regras de negócio da aplicação para fazer o teste passar. Apenas o arquivo de teste ou fixtures devem ser ajustados quando a falha for de especificação.
- **Assincronia e Ciclo de Vida**: verificar se o framework necessita de flush de microtasks (`await fixture.whenStable()`, `waitFor()`, `act()`) antes das asserções.
- **Contratos de Mock**: certificar-se de que mocks retornem Promises ou Observables de acordo com a assinatura esperada pelo componente.

## 7) Checklist Universal de Qualidade

- [ ] Componente renderiza sem erros (inicialização básica)
- [ ] Happy path testado (dados válidos → resultado esperado)
- [ ] Error path testado (serviço falha → mensagem de erro exibida)
- [ ] Todas as dependências mockadas (sem chamadas reais a HTTP/storage)
- [ ] Eventos do usuário testados (click, input, submit)
- [ ] Condicionais de UI testadas (show/hide baseado em estado)
- [ ] Testes independentes (sem dependência de ordem)

## 8) Anti-padrões Universais

- ❌ Executar comandos de teste em modo watch interativo ou sem filtro de ruído
- ❌ Testar estado interno privado em vez de comportamento visível
- ❌ Mocks parciais frágeis (mockar apenas parte do serviço)
- ❌ Usar `setTimeout` real em testes (use timer fakes)
- ❌ Seletores CSS instáveis em E2E (mudam com refatoração)
- ❌ Testes E2E para cenários cobertos por unit tests (custo alto)
- ❌ Usar snapshot para verificar lógica de negócio
- ❌ Cobertura de linha sem cobertura de branch crítica
- ❌ Testes lentos em pipeline (E2E sem agrupamento/parallelism)

## 9) Skills Específicas por Stack

| Stack | Skill Específica | Foco Principal |
|---|---|---|
| Angular 20/21+ + Vitest | `test-implementation-angular-vitest` | TestBed zoneless, Signals, `@angular/build:unit-test`, `@vitest/coverage-v8` |
| Angular 21 + Jasmine/Karma (legado) | `test-implementation-angular-jasmine` | TestBed tradicional com Zone.js, Karma, migração para Vitest |
| React + Vitest + Testing Library | `test-implementation-react-vitest` | RTL `user-event`, hooks isolados, React Compiler boundary |
| Vue + Vitest + Playwright | *(criar adapter quando necessário)* | Vue Test Utils, composables reativos |
| Svelte + Vitest | *(criar adapter quando necessário)* | Svelte Testing Library, runes |

## Referências

- Test Pyramid Frontend: https://martinfowler.com/articles/practical-test-pyramid.html#TheImportanceOfTestAutomation
- Testing Trophy: https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications
- E2E Best Practices: https://playwright.dev/docs/best-practices
