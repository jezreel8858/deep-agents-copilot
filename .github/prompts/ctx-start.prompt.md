---
name: ctx-start
description: Inicializa e valida a sessão do Context Mode para garantir rastreabilidade e ingestão no dashboard.
agent: 'agent'
router_bypass: utility
model: "Gemini 4 Hydrogen"
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
- ✅ O uso de `context-mode` (`ctx_batch`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
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
**Enumerar & Consolidar (`>= 2` alvos):** Liste todos os arquivos/comandos antes de agir (mesmo em prompts curtos). Para `>= 2` alvos, use `ctx_batch` ou script único em `ctx_execute` (`language: "javascript"` com `fs`/`path` nativos para I/O; proibido `python`/`python -c` para I/O por bloqueio AMSI/Defender e varreduras irrestritas). Em timeout (`ETIMEDOUT`/`taskkill`), máx. **1 retry** trocando de estratégia; no 2º, aborte e reporte via Compact Error Reporting (`R-020`).
**Orçamento de Turnos & Warm Start (R-060):** Teto de **5 tool turns** por ciclo (1: Batch Gather / Warm Start silencioso; 2: Execução em lote; 3: Validação). Ao atingir o Turno 4 sem conclusão, acione o Circuit Breaker, salve evidências no `ctx_index` e finalize ou use `ask_questions` (`R-027`: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais, `description` com `[Consequência prática + Trade-off]` e 1ª opção `(Recomendado)`).
**Recibo Estruturado de Etapa (R-068):** Encerre entregas de pipeline com bloco YAML `receipt` + `step_delta` conforme `.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml` (`mode: readonly_analysis` para Score 0; máx. 10 itens inline; excedente em `ctx_index` `wf:<trace>:delta:step-<n>`).
**Pós-Mutação & Conformidade de Plano (R-051 / R-064):** Execute mutações em lote atômico, rode `get_errors` agrupado uma única vez ao final e preencha `step_delta.plan_conformance` (`within_allowed_files`, `out_of_scope_files`) contra `allowed_files` do `plan_ref` ativo.

</execution_protocol>
