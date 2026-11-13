---
name: ctx-doctor
description: Diagnostica o Context Mode usando `ctx_doctor` para validar instalação, hooks e conectividade.
agent: 'agent'
router_bypass: utility
model: "Gemini 3.8 Flash"
tools: ['context-mode/ctx_doctor']
argument-hint: ''
source_docs:
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/ctx-doctor`

Atalho para executar diagnóstico rápido do Context Mode antes de troubleshooting mais profundo.

> **Propósito**: Validar instalação, hooks e conectividade do servidor Context Mode MCP.
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/ctx-doctor` (sem argumentos obrigatórios), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` nem delegar via `run_subagent` — este prompt utilitário possui `router_bypass: utility` (exceção canônica a R-037/R-063) e DEVE ser executado diretamente pelo Orquestrador Raiz.
- ✅ O uso de `context-mode` (`ctx_batch_execute`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** executar o diagnóstico de saúde e conectividade do MCP Context Mode.
- ✅ **SEMPRE** exibir a saída completa exatamente como retornada pelo runtime.
- ❌ **NÃO** executar reparos destrutivos sem aprovação.
- ❌ **NÃO** mascarar alertas ou falhas reportadas pelo `ctx_doctor`.

---

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/ctx-doctor`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## Sintaxe

```
/ctx-doctor
```

## Execução obrigatória

### Passo 0 — Rodar diagnóstico diretamente
`/ctx-doctor` é o ponto de entrada de diagnóstico. Execute mesmo sem pré-checagem.
Se retornar `Not connected`, aplique R-022 (1 auto-recuperação) e tente novamente uma única vez.

### Passo 1 — Diagnóstico de Conectividade
1. Execute `ctx_doctor` sem argumentos.
2. Exiba o relatório completo exatamente como retornado (`[OK]`, `[WARN]`, `[FAIL]`).
3. Se o retorno incluir comando de correção/repair, execute esse comando e reporte em checklist curto.
4. Se houver falha após correção, recomende próximo passo objetivo e aguarde aprovação.

## Exemplo de execução

```javascript
ctx_doctor()
```

## Resposta esperada

- Saída completa do `ctx_doctor` (sem truncar).
- Checklist do comando executado (quando houver repair).
- Próximo passo mínimo (apenas se ainda houver `WARN`/`FAIL`).

## Regras

- Não usar terminal para diagnóstico; use apenas `ctx_doctor`.
- Não executar testes/build junto com `/ctx-doctor`.
- Em erro, reportar no formato compacto (Causa / Local / Ação).
- Se `ctx_doctor` retornar `Not connected`, disparar auto-recuperação conforme R-022.
- Não ocultar linhas do relatório original sem pedido explícito do usuário.

## Combina Com

- `/ctx-status` → verifica consumo após confirmar que o Context Mode está saudável
- `/ctx-resume` → retoma contexto após confirmar conectividade

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/ctx-doctor` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/ctx-doctor`
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

</execution_protocol>
