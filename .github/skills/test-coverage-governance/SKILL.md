---
name: test-coverage-governance
description: 
  Governança de cobertura de testes, estratégias de priorização por risco e
  métricas de qualidade consolidadas (agnóstica de stack).
tier: 2
category: testing
triggers:
  - "test coverage"
  - "cobertura de testes"
  - "cálculo de cobertura"
  - "métricas de qualidade"
  - "code coverage report"
  - "jacoco"
  - "istanbul"
source_docs:
  - .github/skills/test-implementation-backend/SKILL.md
  - .github/skills/test-implementation-python/SKILL.md
  - .github/skills/test-implementation-spring-boot/SKILL.md
  - .github/skills/test-implementation-angular-jasmine/SKILL.md
  - .github/skills/test-implementation-angular-vitest/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Test Coverage Governance

## Contexto

Cobertura de testes não é um fim em si mesmo — é uma métrica de risco. Esta skill consolida estratégias de priorização e padrões de cálculo agnósticos de stack.

> **Ferramentas de cobertura por stack** (configuração específica em adapters):
> - Backend Java/Spring Boot → **JaCoCo** (ver `test-implementation-spring-boot`)
> - Frontend Angular → **Istanbul/Karma** (ver `test-implementation-angular-jasmine`)
> - Python → **coverage.py** (ver `test-implementation-python`)

## 1) Quando Usar

- Avaliar e estabelecer metas mínimas de cobertura de testes por criticidade de negócio e superfície de ataque.
- Priorizar cenários de teste antes de refatorações de código legado, upgrades de dependências ou releases críticas.
- Auditar e interpretar relatórios consolidados em pipelines de CI/CD (JaCoCo, Istanbul/Karma/Vitest, coverage.py).
- Orientar o fluxo de testes unitários prevenindo acoplamento indevido ou refatorações estruturais prematuras.

## 1.1) Regra de Seams Pré-Acordados: Testing-First + Refactor Fora do Loop

- **Princípio**: O ciclo de TDD red-green (ciclo curto de feedback) **NUNCA** inclui refatorações estruturais de outros módulos. Testes e refatorações estruturais pertencem a etapas distintas e separadas.
- **Seams Pré-Acordados**: Antes de escrever o primeiro teste unitário, **acordar explicitamente com o usuário onde os mocks/fakes serão colocados** (ponto de injeção de dependência, fronteira de adapter, contrato de repositório, etc.).
- **Regra de Sequenciamento**: O refactoring pertence à etapa POSTERIOR de `code-review` ou refatoração planejada, apenas após a suíte de testes estar completamente verde (`green`).
- **Exemplo Prático**: Testes de `OrderProcessor` devem mockar `TaxCalculator` no seam previamente acordado; qualquer refatoração interna em `TaxCalculator` só ocorre após a suíte de `OrderProcessor` estar verde e validada.
- **Checklist de Validação**:
  - [ ] Antes de escrever qualquer teste, você respondeu: *"Onde colocar os mocks/fakes?"*
  - [ ] *O usuário está explicitamente de acordo com as fronteiras de isolamento (seams) escolhidas?*
  - [ ] O refatoramento estrutural foi postergado para fora do loop red-green?

*(Referência: mattpocock/skills/tdd)*

## 1.2) Matriz de Cobertura por Risco

| Tipo de Código | Relevância | Cobertura Mínima | Prioritário? |
|---|---|---|---|
| **Lógica crítica de negócio** | CRÍTICA | 90%+ | ⭐ SIM |
| **Integração com API/BD** | ALTA | 80%+ | ⭐ SIM |
| **Validação de entrada** | ALTA | 85%+ | ⭐ SIM |
| **Controllers/Handlers** | MÉDIA | 70%+ | ✓ TODO |
| **Utils/Helpers** | MÉDIA | 75%+ | ✓ TODO |
| **Templates/UI genérica** | BAIXA | 60%+ | ◯ OPCIONAL |
| **Config/Bootstrapping** | BAIXA | 0%+ | ◯ OPCIONAL |

## 2) Tipos de Cobertura

```
Statement Coverage (% linhas executadas)
├── Linha 1: y = 5
├── Linha 2: if (y > 3) → EXECUTADA?
└── Linha 3: return y

Branch Coverage (% desvios cobertos)
├── if (y > 3) → TRUE → TESTADO?
└── if (y > 3) → FALSE → TESTADO?

Function Coverage (% funções chamadas)
├── funcao1() → CHAMADA?
└── funcao2() → CHAMADA?
```

### Fórmula Simplificada

```
Statement Coverage = Lin. Executadas / Total de Linhas
Branch Coverage = Desvios Testados / Total de Desvios
Function Coverage = Funções Testadas / Total de Funções
```

## 3) Metas Consolidadas

### Por Tipo de Projeto

| Projeto | Statements | Branches | Functions | Justificativa |
|---|---|---|---|---|
| **Backend crítico** | 80%+ | 75%+ | 85%+ | Dados/regras de negócio |
| **Frontend (SPA)** | 75%+ | 70%+ | 80%+ | UI mais dinâmica |
| **Utils/Libs** | 85%+ | 80%+ | 90%+ | Reutilizado em múltiplos contextos |
| **Novo projeto** | 70%+ | 60%+ | 75%+ | Permitir iteração rápida |

### Metas Recomendadas por Ecossistema

```yaml
# Configure conforme seu projeto — substitua <projeto-backend> e <projeto-frontend>
<projeto-backend>:
  statements: 80%
  branches: 75%
  functions: 85%

<projeto-frontend>:
  statements: 75%
  branches: 70%
  functions: 80%

libs/commons:
  statements: 85%
  branches: 80%
  functions: 90%
```

## 4) Estratégia de Priorização (Risk-Based)

### Passo 1: Mapear Risco

```
Risco Alto = (crítico para negócio) + (muitas dependências) + (histórico de bugs)

Exemplo agnóstico:
- Persistir/salvar dados críticos → CRÍTICO
- Calcular valores financeiros → CRÍTICO
- Gerar relatório/exportação → MÉDIO
- Formatar/exibir dados → BAIXO
```

### Passo 2: Priorizar por Risco

```
Priority 1: Risco CRÍTICO
  └─ Cobertura: 90%+ (todos cenários)
  └─ Tipos: happy path + edge cases + error handling

Priority 2: Risco ALTO
  └─ Cobertura: 80%+ (principais cenários)
  └─ Tipos: happy path + erro comum

Priority 3: Risco MÉDIO
  └─ Cobertura: 70%+ (path mais frequente)
  └─ Tipos: happy path + 1 erro

Priority 4: Risco BAIXO
  └─ Cobertura: 0%+ (opcional)
  └─ Tipos: apenas se tempo permitir
```

## 5) Como Calcular Cobertura

### Backend — JaCoCo (Java/Spring Boot)

```bash
# Gerar report (Maven)
mvn clean test jacoco:report

# Abrir HTML
open target/site/jacoco/index.html

# Esperar por: Instructions, Branches, Lines, Methods, Classes
```

**Mapa de JaCoCo:**
- **Instructions**: micro-operações bytecode (mais preciso)
- **Branches**: if/else/switch branches
- **Lines**: linhas fonte
- **Cxty**: complexidade ciclomática

### Frontend — Istanbul/Karma (Angular/React/Vue)

```bash
# Gerar report (Angular)
ng test --code-coverage --watch=false

# Abrir HTML
open coverage/<nome-projeto>/index.html

# Esperar por: Statements, Branches, Functions, Lines
```

### Python — coverage.py

```bash
# Gerar report
pytest --cov=. --cov-report=html

# Abrir HTML
open htmlcov/index.html
```

## 6) Interpretando Reports

### Red / Yellow / Green

| Cor | Faixa | Ação |
|---|---|---|
| 🔴 **Red** | <60% | ⚠️ Crítico — aumentar testes urgente |
| 🟡 **Yellow** | 60-75% | ⚠️ Avisar — adicionar testes incrementalmente |
| 🟢 **Green** | 75%+ | ✓ Aceitável — manter ou melhorar |

### Exemplo Real

```
[ServiceImpl]
├─ Line Coverage: 82% (VERDE)
├─ Method Coverage: 90% (VERDE)
├─ Branch Coverage: 71% (AMARELO) ← Adicionar testes de edge cases
└─ Class Coverage: 100% (VERDE)
```

**Ação:** Adicionar testes para as branches não cobertas (else/catch blocks).

## 7) Cenários Críticos Sempre Testados

### Backend (Genérico)

```
[Entidade]Service:
  ✓ salvar(dados válidos) → OK
  ✓ salvar(dados nulos/inválidos) → exceção de validação
  ✓ salvar(violação de integridade) → exceção de integração
  ✓ buscar(existe) → entidade
  ✓ buscar(não existe) → vazio/null/404
  ✓ atualizar(sem permissão) → exceção de autorização
```

### Frontend (Genérico)

```
[Nome]Component:
  ✓ renderizar (inicialização)
  ✓ clicar botão → chamada ao serviço
  ✓ resposta HTTP sucesso → atualizar UI
  ✓ resposta HTTP erro → exibir mensagem
  ✓ input vazio → desabilitar botão
  ✓ form inválido → validação visual
```

### E2E (Genérico)

```
Fluxo de Autenticação:
  ✓ credenciais válidas → área autenticada
  ✓ credenciais inválidas → mensagem de erro
  ✓ sessão expirada → redireciona para login
  ✓ sem conectividade → mensagem de retry
```

## 8) Excluindo Código de Cobertura

### Backend — Anotações / Comentários

```java
// Java/JaCoCo
@Generated              // Lombok, builders automaticamente
@ExcludeFromCodeCoverage // Custom annotation
```

### Frontend — Istanbul

```typescript
// istanbul ignore next
if (ambiente === 'development') {
  console.log('Debug info');
}

// istanbul ignore file
// Arquivo inteiro ignorado para coverage
```

## 9) CI/CD Integration

### GitHub Actions / GitLab CI (Genérico)

```yaml
test-and-coverage:
  script:
    # Backend (adapte conforme stack)
    - <comando-test> <opção-coverage>
  coverage: '/Coverage: \d+\.\d+%/'
  after_script:
    - echo "✅ Coverage gerado"
```

## 10) Relatório de Cobertura Final

```markdown
## Coverage Report — [Nome do Projeto]

### Resumo
- **Statements**: XX% (↑ N% desde sprint anterior)
- **Branches**: XX% (↔ estável)
- **Functions**: XX% (↑ N%)
- **Status**: ✅ ACIMA DA META (70%) | ⚠️ ABAIXO DA META

### Top 3 Arquivos com Baixa Cobertura
1. `[Módulo]Service` — XX% (AVISAR — branches não cobertas)
2. `[Módulo]Util` — XX% (CRÍTICO — edge cases faltando)
3. `Config` — 0% (OK — bootstrapping, opcional)

### Ações
- [ ] Adicionar N testes em `[Módulo]Service` para atingir 80%
- [ ] Refatorar ou aumentar cobertura de `[Módulo]Util` para 70%
- [ ] Documentar exclusão de `Config` (bootstrapping)
```

## 11) Anti-padrões

- ❌ Obsessão por 100% cobertura (overhead, testes frágeis)
- ❌ Cobertura sem qualidade (testes triviais: assert True always)
- ❌ Ignorar branches inteiras (catch blocks, error paths críticos)
- ❌ Sem métricas de trend (não saber se está piorando)
- ❌ Bloquear PR por 1% abaixo da meta sem negociação

## Referências

- **JaCoCo**: https://www.eclemma.org/jacoco/
- **Istanbul/nyc**: https://istanbul.js.org/
- **Code Coverage Best Practices**: https://martinfowler.com/bliki/CodeCoverage.html
- **Test Strategy**: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html

