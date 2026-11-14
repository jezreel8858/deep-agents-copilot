# Cálculo, Interpretação e Relatório de Cobertura — Detalhes

> Referência detalhada (lazy) extraída de `test-coverage-governance/SKILL.md` (R-066). Seções 5–10 originais.

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

