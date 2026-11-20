---
name: ctx-status
description: Exibe estatísticas de consumo do Context Mode usando `ctx_stats` para diagnosticar uso de contexto e economia.
agent: 'agent'
router_bypass: utility
model: "Gemini 4 Hydrogen"
tools: ['context-mode/ctx_stats']
argument-hint: ''
source_docs:
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/ctx-status`

Atalho para obter um snapshot rápido de consumo de contexto da sessão atual.

> **Propósito**: Coletar e exibir indicadores consolidado de consumo de tokens e bytes do Context Mode MCP.
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/ctx-status` (sem argumentos obrigatórios), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` nem delegar via `run_subagent` — este prompt utilitário possui `router_bypass: utility` (exceção canônica a R-037/R-063) e DEVE ser executado diretamente pelo Orquestrador Raiz.
- ❌ **NÃO** modificar o banco de dados do FTS5 ou resetar telemetria.
- ❌ **NÃO** poluir o chat com dumps excessivos além do resumo formatado.
- ✅ O uso de `context-mode` (`ctx_batch`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** coletar e exibir estatísticas consolidadas de consumo do Context Mode.
- ✅ **SEMPRE** apresentar resumo de bytes, chamadas e savings ratio.

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/ctx-status`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

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

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/ctx-status` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/ctx-status`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
**Enumerar & Consolidar (`>= 2` alvos):** Liste todos os arquivos/comandos antes de agir (mesmo em prompts curtos). Para `>= 2` alvos, use `ctx_batch` ou script único em `ctx_execute` (`language: "javascript"` com `fs`/`path` nativos para I/O; proibido `python`/`python -c` para I/O por bloqueio AMSI/Defender e varreduras irrestritas). Em timeout (`ETIMEDOUT`/`taskkill`), máx. **1 retry** trocando de estratégia; no 2º, aborte e reporte via Compact Error Reporting (`R-020`).
**Orçamento de Turnos & Warm Start (R-060):** Teto de **5 tool turns** por ciclo (1: Batch Gather / Warm Start silencioso; 2: Execução em lote; 3: Validação). Ao atingir o Turno 4 sem conclusão, acione o Circuit Breaker, salve evidências no `ctx_index` e finalize ou use `ask_questions` (`R-027`: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais, `description` com `[Consequência prática + Trade-off]` e 1ª opção `(Recomendado)`).
**Recibo Estruturado de Etapa (R-068):** Encerre entregas de pipeline com bloco YAML `receipt` + `step_delta` conforme `.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml` (`mode: readonly_analysis` para Score 0; máx. 10 itens inline; excedente em `ctx_index` `wf:<trace>:delta:step-<n>`).

</execution_protocol>
