---
name: ctx-status
description: Exibe estatísticas de consumo do Context Mode usando `ctx_stats` para diagnosticar uso de contexto e economia.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools:
  - context-mode/ctx_stats
argument-hint: ''
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/context-mode/SKILL.md
---

# `/ctx-status`

Atalho para obter um snapshot rápido de consumo de contexto da sessão atual.

> **Propósito**: Coletar e exibir indicadores consolidado de consumo de tokens e bytes do Context Mode MCP.
> **Workspace**: `${workspaceFolder}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** coletar e exibir estatísticas consolidadas de consumo do Context Mode.
- ✅ **SEMPRE** apresentar resumo de bytes, chamadas e savings ratio.
- ❌ **NÃO** modificar o banco de dados do FTS5 ou resetar telemetria.
- ❌ **NÃO** poluir o chat com dumps excessivos além do resumo formatado.

---

## Sintaxe

```
/ctx-status
```

## Execução obrigatória

### Passo 0 — Coleta direta
`/ctx-status` já usa `ctx_stats` como primeira ação; não precisa pré-checagem adicional.

### Passo 1 — Obter Snapshot de Consumo
1. Execute `ctx_stats` sem argumentos.
2. Exiba a saída completa do `ctx_stats`.
3. Em seguida, adicione um resumo curto com os principais indicadores (bytes, chamadas, tokens estimados, savings ratio).
4. Se houver anomalia, recomende ação objetiva (ex.: reduzir output bruto, usar `queries` em lote, indexar por `path`).

## Exemplo de execução

```javascript
ctx_stats()
```

## Resposta esperada

- Saída completa do `ctx_stats`.
- Total de bytes no contexto.
- Ferramentas com maior consumo.
- Taxa estimada de economia (`context savings ratio`).
- Recomendação curta quando o consumo estiver alto.

## Regras

- Não usar terminal para esse diagnóstico; use apenas `ctx_stats`.
- Não executar testes/build junto com `/ctx-status`.
- Se `ctx_stats` falhar, reportar erro no formato compacto (Causa / Local / Ação).
- Não resumir sem apresentar o output completo primeiro.

## Combina Com

- `/ctx-doctor` → diagnostique conectividade se `ctx_stats` falhar
- `/ctx-checkpoint` → grave um checkpoint antes de compactar quando consumo estiver alto
- `/ctx-insight` → abra o dashboard para análise mais profunda

