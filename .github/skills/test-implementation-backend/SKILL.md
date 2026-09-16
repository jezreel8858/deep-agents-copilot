---
name: test-implementation-backend
description: 
  Padrões genéricos e agnósticos para implementação de testes em qualquer projeto
  backend, independente de linguagem ou framework. Define contratos, tipos de teste
  e estratégias de cobertura aplicáveis a qualquer stack server-side.
tier: 2
category: testing
triggers:
  - "testar backend"
  - "testes de serviço"
  - "unit test backend"
  - "integration test"
  - "test backend"
  - "testes unitários"
  - "testes de integração"
  - "mocks backend"
  - "cobertura backend"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/test-coverage-governance/SKILL.md
tools: []
---

# Test Implementation — Backend (Genérico)

> **Escopo**: padrões **agnósticos de framework** para qualquer projeto backend.
> Para implementação específica por stack, consulte:
> - `test-implementation-spring-boot` → Java + Spring Boot + JUnit 5 + Mockito
> - `test-implementation-python` → Python + pytest + coverage.py
>
> **Quando usar esta skill**: ao definir estratégia de testes, revisar cobertura
> ou trabalhar em projeto com stack ainda não catalogada.

## 1) Tipos de Teste — Pirâmide

```
        ┌─────────┐
        │   E2E   │  ← Poucos, lentos, custo alto
        ├─────────┤
        │ Integr. │  ← Moderados, testam contratos
        ├─────────┤
        │  Unit   │  ← Muitos, rápidos, isolados
        └─────────┘
```

| Tipo | Isola de | Testa | Velocidade |
|---|---|---|---|
| **Unit** | Todas as dependências externas | Lógica de negócio pura | Muito rápido |
| **Integration** | Infra externa (APIs, clouds) | Contratos entre camadas | Moderado |
| **E2E** | Nada | Fluxo completo do sistema | Lento |

## 2) Padrão AAA (Universal)

```
Arrange  → Configurar dados, mocks e estado inicial
Act      → Executar a unidade sob teste
Assert   → Verificar resultado, efeitos e chamadas
```

**Regras do AAA:**
- Cada teste valida **uma única responsabilidade**.
- Estado não deve vazar entre testes.
- Nome do teste descreve `[ação] quando [condição]`.

## 3) Unit Tests — Conceitos

### Estrutura de Arquivo de Teste

```
src/
  [módulo]/
    [Classe].ext          ← Código fonte
    [Classe].test.ext     ← Testes correspondentes (próximo ao fonte)
    OR
tests/
  unit/
    [módulo]/
      test_[classe].ext   ← Estrutura espelho do source
```

### Isolamento de Dependências

```
Dependência Externa      Substituto no Teste
────────────────────     ─────────────────────
Banco de Dados     →     Mock / In-memory DB
API HTTP Externa   →     Mock / Stub
Sistema de Arquivos →    Mock / Temp directory
Clock/Tempo        →     Mock de tempo fixo
Filas/Mensageria   →     Mock / In-process queue
```

### Cobertura Mínima por Tipo de Lógica

| Tipo de Lógica | Cobertura Mínima | Prioridade |
|---|---|---|
| Regra de negócio crítica | 90%+ | ⭐ Alta |
| Validação de entrada | 85%+ | ⭐ Alta |
| Integração com BD/API | 80%+ | ⭐ Alta |
| Controllers/Handlers | 70%+ | ✓ Média |
| Utilitários | 75%+ | ✓ Média |
| Configuração/Bootstrap | Opcional | ◯ Baixa |

## 4) Integration Tests — Conceitos

### Quando Usar

- Validar contrato entre camada de serviço e repositório.
- Testar queries/stored procedures com banco real.
- Verificar serialização/deserialização de APIs.
- Confirmar comportamento transacional.

### Estratégias de Isolamento

```
Banco de Dados:
  - In-memory (H2, SQLite) — rápido, sem estado persistido
  - Container (TestContainers) — fiel ao ambiente de produção
  - Schema dedicado de teste — mais rápido que container

APIs Externas:
  - WireMock / MockServer — servidor HTTP local
  - Respostas gravadas (cassette) — replay determinístico
```

## 5) Nomenclatura de Testes

```
[deve/should] [resultado esperado] [quando/when] [condição]

Exemplos PT-BR:
  deve retornar lista vazia quando nenhum registro encontrado
  deve lançar exceção quando campo obrigatório ausente
  deve persistir entidade quando dados válidos
  deve retornar 404 quando id não existe

Exemplos EN:
  should return empty list when no records found
  should throw exception when required field is missing
```

## 6) Checklist Universal de Qualidade

- [ ] Happy path testado (fluxo principal com dados válidos)
- [ ] Edge cases testados (limites: null, vazio, máximo, mínimo)
- [ ] Error paths testados (exceções esperadas com tipo e mensagem corretos)
- [ ] Dependências externas mockadas (sem chamadas reais a BD/API em unit test)
- [ ] Testes independentes (sem ordem de execução obrigatória)
- [ ] Nomes descritivos e autoexplicativos
- [ ] Sem código duplicado (helpers/builders para dados de teste comuns)

## 6.1) Execução de Testes com Zero Ruído (R-008 / R-049)

Ao validar suites de teste, os agentes de IA devem proteger ativamente a janela de contexto contra poluição de logs (INFO, WARNING, download de dependências e banners de framework):

1. **Prioridade 1 — Sandbox `ctx_execute` (Think-in-Code)**: Execute o runner de teste (`mvn test`, `pytest`, `vitest`) dentro do sandbox isolado. Capture o stdout/stderr em código, filtre linhas de compilação/INFO e imprima apenas o resumo de testes ou stack traces estritos de falha.
2. **Prioridade 2 — Terminal Silencioso com Filtro**: Se executar diretamente no terminal via `run_in_terminal`, é **OBRIGATÓRIO** usar a flag silenciosa da stack (`-q`, `--quiet`, `-B`) e canalizar a saída através de filtro (`grep -E "ERROR|FAILURE|BUILD|Tests run"` ou PowerShell `Select-String`) limitado a 40 linhas (`head -40`).
3. **Proibição Absoluta**: É terminantemente proibido executar comandos de teste "bare" (`mvn test`, `pytest`) sem flags de supressão ou sem filtros.

## 7) Anti-padrões Universais
- ❌ Executar comandos de teste sem filtro de ruído ou flags silenciosas no terminal

- ❌ Testes que dependem de ordem de execução
- ❌ Shared mutable state entre testes (pode causar flakiness)
- ❌ Chamar serviços externos reais em unit tests
- ❌ Testes sem assertions (test que nunca falha)
- ❌ Cobertura de linha sem cobertura de branch (falsa sensação de segurança)
- ❌ Testar implementação em vez de comportamento (testes frágeis)
- ❌ Ignorar testes falhando ou marcá-los como skip indefinidamente

## 8) Skills Específicas por Stack

| Stack | Skill Específica |
|---|---|
| Java + Spring Boot + JUnit 5 | `test-implementation-spring-boot` |
| Python + pytest | `test-implementation-python` |
| TypeScript/Node + Jest | *(criar adapter quando necessário)* |
| Go + testing | *(criar adapter quando necessário)* |

## Referências

- Test Pyramid: https://martinfowler.com/articles/practical-test-pyramid.html
- Unit Testing Principles: https://enterprisecraftsmanship.com/posts/unit-testing-best-practices/
- Test Coverage: https://martinfowler.com/bliki/CodeCoverage.html
