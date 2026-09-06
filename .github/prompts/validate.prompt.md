---
name: validate
description: Valida implementação contra plano aprovado, verifica critérios de sucesso e identifica desvios.
model: "Gemini 3.8 Flash"
tools: ['read_file', 'grep_search', 'file_search', 'run_in_terminal', 'get_errors', 'run_subagent', 'context-mode/ctx_search', 'context-mode/ctx_batch_execute']
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# /validate

Você foi encarregado de validar que um plano foi implementado corretamente, verificando critérios e identificando desvios.

## Setup

Ao invocar:

1. **Determine contexto** — sessão existente ou nova?
   - Existente: revise o que foi implementado nesta sessão
   - Nova: descubra via análise do codebase

2. **Localize o plano**:
   - Se path fornecido, use-o
   - Senão, pergunte ao usuário

3. **Colete evidência** via `ctx_search(sort: "timeline")` e `ctx_batch_execute(commands, queries)`

## Processo

### Passo 1: Descoberta de Contexto

Se sessão nova:

1. Leia o plano **integralmente**
2. Identifique o que deveria ter mudado:
   - Todos os arquivos que deveriam ser modificados
   - Critérios (automatizados + manuais)
   - Funcionalidade-chave a verificar

3. **Levante evidências em paralelo** via `ctx_batch_execute`:
   - Verificar mudanças de código vs. plano
   - Verificar cobertura de verificações
   - Verificar artefatos criados/alterados

### Passo 2: Validação Sistemática

Para cada fase:

1. **Status de conclusão**:
   - Cheque checkmarks no plano (`- [x]`)
   - Verifique que código real bate com conclusão alegada
   - Verifique que houve checkpoint da fase via `/ctx-checkpoint`

2. **Verificação automatizada**:
   - Execute cada verificação prevista no plano
   - Documente pass/fail com evidências
   - Investigue falhas

3. **Critérios manuais**:
   - Liste o que precisa de verificação humana
   - Forneça passos claros

4. **Edge cases**:
   - Erros tratados?
   - Validações faltando?
   - Implementação pode quebrar funcionalidade existente?

### Passo 3: Relatório de Validação

```markdown
## Relatório de Validação: <Plano>

### Status de Implementação
✓ Fase 1: <Nome> — Totalmente implementado
✓ Fase 2: <Nome> — Totalmente implementado
⚠️ Fase 3: <Nome> — Parcialmente implementado (ver issues)

### Resultados das Verificações Automatizadas
✓ <verificação 1>: passou
✗ <verificação 2>: falhou — <motivo>

### Achados de Code Review

#### Bate com Plano:
- <item>

#### Desvios do Plano:
- <arquivo:linha> — <descrição do desvio>

#### Issues Potenciais:
- <issue> (apenas reportar, sem julgar)

### Verificação Manual Necessária
1. **Funcionalidade**:
   - [ ] <passo manual 1>
   - [ ] <passo manual 2>

### Recomendações
- N/A — apenas reporte achados objetivos
```

## Diretrizes

1. **Exaustivo mas prático** — foque no que importa
2. **Execute todas as verificações** — não pule
3. **Documente tudo** — sucessos e issues
4. **Pense criticamente** — a implementação resolve o problema?
5. **Token budget** — perguntas em lote no `queries`, `source` quando aplicável, sem saída bruta desnecessária
6. **Leitura integral de código é exceção** — priorize evidência indexada e leitura pontual

## Checklist de Validação

- [ ] Todas as fases marcadas completas estão realmente feitas
- [ ] Cada fase concluída possui registro de checkpoint (`/ctx-checkpoint`)
- [ ] Há checkpoint final de fechamento do plano
- [ ] Critérios verificáveis foram testados
- [ ] Código segue padrões existentes do projeto
- [ ] Sem regressões óbvias
- [ ] Tratamento de erro coberto
- [ ] Passos manuais estão claros e executáveis

## Combina Com

- `/implement` → precede este command
- `/plan` → se validação revela necessidade de ajustar plano
