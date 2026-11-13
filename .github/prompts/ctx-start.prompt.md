---
name: ctx-start
description: Inicializa e valida a sessão do Context Mode para garantir rastreabilidade e ingestão no dashboard.
agent: 'agent'
router_bypass: utility
model: "Gemini 3.8 Flash"
tools: ['context-mode/ctx_stats', 'context-mode/ctx_doctor', 'context-mode/ctx_execute']
argument-hint: ''
source_docs:
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/ctx-start`

Garante que o Context Mode está ativo e pronto para uso com baixo custo de contexto.

> **Propósito**: Inicializar e certificar a conectividade do Context Mode e o rastreamento no Dashboard.
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/ctx-start` (sem argumentos obrigatórios), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` nem delegar via `run_subagent` — este prompt utilitário possui `router_bypass: utility` (exceção canônica a R-037/R-063) e DEVE ser executado diretamente pelo Orquestrador Raiz.
- ✅ O uso de `context-mode` (`ctx_batch_execute`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** inicializar a sessão do MCP Context Mode e validar sua conectividade básica.
- ✅ **SEMPRE** emitir comando leve de sincronização para registrar telemetria.
- ❌ **NÃO** executar scripts arbitrários fora da validação de saúde do MCP.
- ❌ **NÃO** ignorar falhas de conexão não resolvidas após 1 tentativa (R-022).

---

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/ctx-start`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## Objetivo
Validar conectividade MCP, bootstrap mínimo da sessão e disponibilidade de métricas para execução `ctx-first`.

## Execução

### Passo 1 — Health Check de Conectividade
Execute `ctx_doctor()` e exiba o retorno completo.

### Passo 2 — Validação de Sessão Manual (Sync)
Execute um comando leve para registrar pelo menos uma chamada na sessão:
```javascript
ctx_execute({
  language: "shell",
  code: "echo 'context-mode: sync-validation'"
})
```

### Passo 3 — Verificação de Ingestão e Regras
Execute `ctx_stats()`. 
- **Se `Total calls > 0`**: Sucesso.
- **Se `Total calls = 0`**: rode `ctx_doctor` novamente e siga o comando de correção retornado (se houver). Persistindo zero, reportar falha compacta e aguardar ação do usuário.

## Resposta Esperada
```
✅ Sessão Context Mode Validada
├─ Conectividade: [OK] via ctx_doctor
├─ Ingestão: chamada detectada em ctx_stats
└─ Próximo: /pesquisar ou @agent-router
```

## Troubleshooting (Dashboard Vazio)
Se o dashboard continuar sem sessões:
1. Execute `/ctx-doctor` e aplique o comando sugerido no retorno.
2. Reexecute `/ctx-start` para validar se `ctx_stats` passa a registrar chamadas.

## Regras
- **R-022 (Auto-recuperação)**: Aplique se o Context Mode estiver desconectado.
- Não usar terminal para a verificação de stats; use `ctx_stats`.
- Priorize sempre ferramentas `ctx_*`; não usar fallback fora do fluxo sem aprovação do usuário.
- Em caso de falha persistente de ingestão (stats continuam em zero após trigger), reportar no formato compacto (Causa / Local / Ação).

## Combina Com
- `/ctx-status` → para ver o consumo detalhado após o início
- `/ctx-doctor` → diagnóstico profundo se o início falhar
- `/init-context` → executado após a governança global ser carregada

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/ctx-start` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/ctx-start`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`. No `ctx_execute`, use obrigatoriamente `language: "javascript"` (`fs`/`path` nativos do Node.js) para I/O, inspeção e mutação de arquivos (proibido `language: "python"` ou `python -c` para I/O, evitando bloqueio do `python.exe` pelo Windows Defender/AMSI); em `ctx_batch_execute`, use apenas comandos shell leves com escopo restrito (proibido `python -c` inline ou varreduras recursivas irrestritas). Em caso de timeout (`ETIMEDOUT`/`timed out`/`taskkill`), aplica-se **Circuit Breaker Fail-Fast**: tolerância zero para repetir a mesma chamada/runtime — máximo de **1 retry** exigindo troca obrigatória de estratégia (migrar para `language: "javascript"` puro com `fs` ou reduzir o lote); no 2º timeout, aborte novos spawns e reporte em formato Compact Error Reporting (R-020).
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions (R-027: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais sem espantalhos, `description` obrigatório com `[Consequência prática + Trade-off/quando escolher]` e 1ª opção `(Recomendado)` para melhor prática técnica), vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).

</execution_protocol>
