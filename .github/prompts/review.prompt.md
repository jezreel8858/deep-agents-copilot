---
name: review
description:
  Aciona o agent @code-review para revisar diff/PR/arquivo por qualidade,
  segurança, convenções, impacto e testes. Gera relatório por severidade.
  NÃO executa alterações.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'grep_search', 'file_search', 'run_in_terminal', 'run_subagent']
argument-hint: '[caminho-do-arquivo | diff]'
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/instructions/README.md
  - .github/skills/terminal-governance/SKILL.md
  - .github/skills/code-review-patterns/SKILL.md
  - .github/agents/code-review.agent.md
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
- ✅ **APENAS** analisar e reportar achados (delegado ao agent `@code-review`)
- ✅ Se achado exige ação complexa → sugerir o agent correto via handoff

---

## 🔄 Combina Com

- [`@code-review`](../agents/code-review.agent.md) → agent que concentra a lógica completa deste prompt.
- `@agent-router` → roteamento em linguagem natural ("revisa esse código") sem precisar digitar `/review`.

---

*v2.0 — review prompt — 2026-08-29 (consolidado como alias do agent @code-review, remove duplicação de lógica — R-003)*

