---
name: review
description:
  Aciona o agent @code-review para revisar diff/PR/arquivo por qualidade,
  segurança, convenções, impacto e testes. Gera relatório por severidade.
  NÃO executa alterações.
agent: 'agent'
router_bypass: slash_workflow
model: "Gemini 4 Argon"
tools: ['read_file', 'grep_search', 'file_search', 'run_in_terminal', 'run_subagent', 'context-mode/ctx_execute', 'context-mode/ctx_batch', 'context-mode/ctx_search']
argument-hint: '[caminho-do-arquivo | diff]'
source_docs:
  - '.github/instructions/README.md'
  - '.github/skills/code-review-patterns/SKILL.md'
  - '.github/skills/efficient-batch-code-modification/SKILL.md'
  - '.github/agents/code-review.agent.md'
  - '.github/skills/terminal-governance/SKILL.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/review`

Atalho manual on-demand para o agent [`@code-review`](../agents/code-review.agent.md) — revisão de código orientada por qualidade, convenções e impacto técnico.

> **Propósito**: Analisar código (diff, PR ou arquivo) contra as convenções do projeto e identificar bugs, riscos, melhorias e gaps de teste, classificados por severidade.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`
>
> **NÃO executa alterações** — apenas analisa e reporta (agent `@code-review` é read-only).
>
> A lógica completa (taxonomia de severidade, dimensões de análise, critérios de bloqueio, anti-padrões) vive em `code-review.agent.md` + `code-review-patterns/SKILL.md` — este prompt apenas dispara o fluxo manualmente, sem duplicar a regra (R-003).

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/review` (argumento: `[caminho-do-arquivo | diff]`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` na triagem inicial — este Slash Prompt possui `router_bypass: slash_workflow` (exceção canônica a R-037/R-063) e seu fluxo já está definido abaixo; o Orquestrador Raiz DEVE executar diretamente as instruções deste `.prompt.md` (ou despachar diretamente para o subagente previsto neste próprio prompt).
- ✅ **APENAS** analisar código e emitir relatório de revisão estruturado por severidade (Bloqueador/Alto/Sugestão).
- ✅ **SEMPRE** classificar os achados nas 6 dimensões canônicas (correção, segurança, convenções, impacto, testes, performance).
- ❌ **NÃO** modificar ou corrigir arquivos de código diretamente (perfil read-only).
- ❌ **NÃO** emitir sugestões fora do diff ou de escopo não afetado.

---

---

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/review`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## 🎯 Uso

```bash
/review                          → revisa mudanças não commitadas (git --no-pager diff HEAD)
/review <arquivo>                → revisa arquivo específico
/review <arquivo> <outro>        → revisa múltiplos arquivos
```

---

## 📋 Fluxo

### PASSO 1 — Coletar mudanças

```bash
# Diff não commitado (padrão)
git --no-pager diff HEAD

# Ou ler arquivo(s) alvo diretamente
```

### PASSO 2 — Delegar ao agent `@code-review`

Aplicar a Decision Tree e o formato de saída definidos em [`code-review.agent.md`](../agents/code-review.agent.md), usando [`code-review-patterns/SKILL.md`](../skills/code-review-patterns/SKILL.md) como base de severidade/dimensões e `.github/instructions/README.md` para identificar o adapter de stack aplicável.

### PASSO 3 — Apresentar o relatório

O relatório e o veredito final (`APROVADO | APROVADO COM RESSALVAS | BLOQUEADO`) seguem exatamente o "Formato de Saída" do agent `@code-review` — ver arquivo referenciado.

---

## 🔀 Roteamento Automático (herdado do agent)

| Achado | Ação |
|--------|------|
| Bug crítico encontrado | Reportar no relatório + handoff `@bug-triage` |
| Impacto em dependências | Reportar + handoff `@tech-solution-architect` |
| Falta de testes | Reportar + handoff `@test-strategy` |
| Dívida técnica estrutural | Reportar + handoff `@refactor-planner` |
| Apenas convenção/estilo | Incluir no relatório, sem escalação |

---

## 🚨 Regras de Autonomia

- ❌ **NUNCA** alterar o código sendo revisado
- ❌ **NUNCA** criar commits ou arquivos derivados da revisão
- O uso de `context-mode` (`ctx_batch`, `ctx_execute`, `ctx_search`) é 100% OBRIGATÓRIO para inspecionar arquivos e diffs sob Single-Turn MCP Batching (R-008, R-046, R-056, Smell 2.26). É terminantemente proibido o uso de `read_file` ou comandos de varredura no terminal quando o context-mode estiver ativo.
- ✅ **APENAS** analisar e reportar achados (delegado ao agent `@code-review`)
- ✅ Se achado exige ação complexa → sugerir o agent correto via handoff

---

## 🔄 Combina Com

- [`@code-review`](../agents/code-review.agent.md) → agent que concentra a lógica completa deste prompt.
- `@agent-router` → roteamento em linguagem natural ("revisa esse código") sem precisar digitar `/review`.

---

*v2.0 — review prompt — 2026-08-29 (consolidado como alias do agent @code-review, remove duplicação de lógica — R-003)*

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/review` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/review`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch(commands, queries)` OU script iterativo consolidado em `ctx_execute`. No `ctx_execute`, use obrigatoriamente `language: "javascript"` (`fs`/`path` nativos do Node.js) para I/O, inspeção e mutação de arquivos (proibido `language: "python"` ou `python -c` para I/O, evitando bloqueio do `python.exe` pelo Windows Defender/AMSI); em `ctx_batch`, use apenas comandos shell leves com escopo restrito (proibido `python -c` inline ou varreduras recursivas irrestritas). Em caso de timeout (`ETIMEDOUT`/`timed out`/`taskkill`), aplica-se **Circuit Breaker Fail-Fast**: tolerância zero para repetir a mesma chamada/runtime — máximo de **1 retry** exigindo troca obrigatória de estratégia (migrar para `language: "javascript"` puro com `fs` ou reduzir o lote); no 2º timeout, aborte novos spawns e reporte em formato Compact Error Reporting (R-020).
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions (R-027: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais sem espantalhos, `description` obrigatório com `[Consequência prática + Trade-off/quando escolher]` e 1ª opção `(Recomendado)` para melhor prática técnica), vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).

</execution_protocol>
