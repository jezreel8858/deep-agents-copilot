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
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/test-coverage-governance/SKILL.md
tools: []
---

# Test Implementation — Frontend (Genérico)

> **Escopo**: padrões **agnósticos de framework** para qualquer projeto frontend.
> Para implementação específica por stack, consulte:
> - `test-implementation-angular-jasmine` → Angular 21 + Jasmine + Karma + Playwright
> - *(criar adapter para React/Jest, Vue/Vitest quando necessário)*
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
| Componentes puramente visuais | 60%+ | ◯ Baixa |

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

## 7) Checklist Universal de Qualidade

- [ ] Componente renderiza sem erros (inicialização básica)
- [ ] Happy path testado (dados válidos → resultado esperado)
- [ ] Error path testado (serviço falha → mensagem de erro exibida)
- [ ] Todas as dependências mockadas (sem chamadas reais a HTTP/storage)
- [ ] Eventos do usuário testados (click, input, submit)
- [ ] Condicionais de UI testadas (show/hide baseado em estado)
- [ ] Testes independentes (sem dependência de ordem)

## 8) Anti-padrões Universais

- ❌ Testar estado interno privado em vez de comportamento visível
- ❌ Mocks parciais frágeis (mockar apenas parte do serviço)
- ❌ Usar `setTimeout` real em testes (use timer fakes)
- ❌ Seletores CSS instáveis em E2E (mudam com refatoração)
- ❌ Testes E2E para cenários cobertos por unit tests (custo alto)
- ❌ Cobertura de linha sem cobertura de branch crítica
- ❌ Testes lentos em pipeline (E2E sem agrupamento/parallelism)

## 9) Skills Específicas por Stack

| Stack | Skill Específica |
|---|---|
| Angular 21 + Jasmine/Karma + Playwright | `test-implementation-angular-jasmine` |
| React + Jest + Testing Library | *(criar adapter quando necessário)* |
| Vue + Vitest + Playwright | *(criar adapter quando necessário)* |
| Svelte + Vitest | *(criar adapter quando necessário)* |

## Referências

- Test Pyramid Frontend: https://martinfowler.com/articles/practical-test-pyramid.html#TheImportanceOfTestAutomation
- Testing Trophy: https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications
- E2E Best Practices: https://playwright.dev/docs/best-practices
