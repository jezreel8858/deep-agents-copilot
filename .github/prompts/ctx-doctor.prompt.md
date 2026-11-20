---
name: ctx-doctor
description: Diagnostica o Context Mode usando `ctx_doctor` para validar instalação, hooks e conectividade.
agent: 'agent'
router_bypass: utility
model: "Gemini 4 Hydrogen"
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
- ✅ O uso de `context-mode` (`ctx_batch`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
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
**Enumerar & Consolidar (`>= 2` alvos):** Liste todos os arquivos/comandos antes de agir (mesmo em prompts curtos). Para `>= 2` alvos, use `ctx_batch` ou script único em `ctx_execute` (`language: "javascript"` com `fs`/`path` nativos para I/O; proibido `python`/`python -c` para I/O por bloqueio AMSI/Defender e varreduras irrestritas). Em timeout (`ETIMEDOUT`/`taskkill`), máx. **1 retry** trocando de estratégia; no 2º, aborte e reporte via Compact Error Reporting (`R-020`).
**Orçamento de Turnos & Warm Start (R-060):** Teto de **5 tool turns** por ciclo (1: Batch Gather / Warm Start silencioso; 2: Execução em lote; 3: Validação). Ao atingir o Turno 4 sem conclusão, acione o Circuit Breaker, salve evidências no `ctx_index` e finalize ou use `ask_questions` (`R-027`: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais, `description` com `[Consequência prática + Trade-off]` e 1ª opção `(Recomendado)`).
**Recibo Estruturado de Etapa (R-068):** Encerre entregas de pipeline com bloco YAML `receipt` + `step_delta` conforme `.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml` (`mode: readonly_analysis` para Score 0; máx. 10 itens inline; excedente em `ctx_index` `wf:<trace>:delta:step-<n>`).

</execution_protocol>
