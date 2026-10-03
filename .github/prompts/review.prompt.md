---
name: review
description:
  Aciona o agent @code-review para revisar diff/PR/arquivo por qualidade,
  segurança, convenções, impacto e testes. Gera relatório por severidade.
  NÃO executa alterações.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'grep_search', 'file_search', 'run_in_terminal', 'run_subagent', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_search']
argument-hint: '[caminho-do-arquivo | diff]'
source_docs:
  - .github/instructions/README.md
  - .github/skills/code-review-patterns/SKILL.md
  - .github/skills/context-mode/SKILL.md
  - .github/skills/efficient-batch-code-modification/SKILL.md
  - .github/agents/code-review.agent.md
  - .github/skills/terminal-governance/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
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

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** analisar código e emitir relatório de revisão estruturado por severidade (Bloqueador/Alto/Sugestão).
- ✅ **SEMPRE** classificar os achados nas 6 dimensões canônicas (correção, segurança, convenções, impacto, testes, performance).
- ❌ **NÃO** modificar ou corrigir arquivos de código diretamente (perfil read-only).
- ❌ **NÃO** emitir sugestões fora do diff ou de escopo não afetado.

---

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
- O uso de `context-mode` (`ctx_batch_execute`, `ctx_execute`, `ctx_search`) é 100% OBRIGATÓRIO para inspecionar arquivos e diffs sob Single-Turn MCP Batching (R-008, R-046, R-056, Smell 2.26). É terminantemente proibido o uso de `read_file` ou comandos de varredura no terminal quando o context-mode estiver ativo.
- ✅ **APENAS** analisar e reportar achados (delegado ao agent `@code-review`)
- ✅ Se achado exige ação complexa → sugerir o agent correto via handoff

---

## 🔄 Combina Com

- [`@code-review`](../agents/code-review.agent.md) → agent que concentra a lógica completa deste prompt.
- `@agent-router` → roteamento em linguagem natural ("revisa esse código") sem precisar digitar `/review`.

---

*v2.0 — review prompt — 2026-08-29 (consolidado como alias do agent @code-review, remove duplicação de lógica — R-003)*

<execution_protocol>
**Protocolo Plan-Then-Batch (Smell 2.26 / Smell 2.13 / R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
3. **DESPACHAR & VALIDAR**: Aplique todas as mutações ou leituras em processo único no sandbox (all-or-nothing verificado, R-051) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
4. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
5. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
6. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).
8. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".
</execution_protocol>
