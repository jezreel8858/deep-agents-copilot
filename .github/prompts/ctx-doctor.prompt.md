---
name: ctx-doctor
description: Diagnostica o Context Mode usando `ctx_doctor` para validar instalação, hooks e conectividade.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools:
  - context-mode/ctx_doctor
argument-hint: ''
source_docs:
  - .github/skills/context-mode/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/ctx-doctor`

Atalho para executar diagnóstico rápido do Context Mode antes de troubleshooting mais profundo.

> **Propósito**: Validar instalação, hooks e conectividade do servidor Context Mode MCP.
> **Workspace**: `${workspaceFolder}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** executar o diagnóstico de saúde e conectividade do MCP Context Mode.
- ✅ **SEMPRE** exibir a saída completa exatamente como retornada pelo runtime.
- ❌ **NÃO** executar reparos destrutivos sem aprovação.
- ❌ **NÃO** mascarar alertas ou falhas reportadas pelo `ctx_doctor`.

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

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".

</execution_protocol>
