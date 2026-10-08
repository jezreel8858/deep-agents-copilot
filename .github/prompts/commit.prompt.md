---
name: commit
description: >-
  Gera mensagem de commit convencional (PT-BR), título/descrição de PR com matriz
  de risco e plano de rollback, e entrada de CHANGELOG, consumindo a skill
  git-governance. Aplica guardrail de segredos e atomicidade. NÃO executa
  git add/commit/push.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['context-mode/ctx_batch_execute', 'context-mode/ctx_execute', 'context-mode/ctx_execute_file', 'context-mode/ctx_search']
argument-hint: '[contexto-opcional-da-mudança]'
source_docs:
  - .github/skills/git-governance/SKILL.md
  - .github/skills/context-mode/SKILL.md
  - .github/skills/efficient-batch-code-modification/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/commit`

Analisa o diff/stage e gera mensagem de commit, título/descrição de PR e entrada de CHANGELOG. Regras normativas vivem na skill [`git-governance`](../skills/git-governance/SKILL.md) (SSOT); consultar `references/` sob demanda.

```bash
/commit
/commit "contexto opcional da mudança"
```

> **Arquivo Ativo**: `${file}` · **Workspace**: `${workspaceFolder}`

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ APENAS analisar diff/log e gerar texto (commit, PR, CHANGELOG).
- ✅ SEMPRE executar o guardrail de segredos antes de emitir qualquer mensagem.
- ❌ NUNCA executar `git add`, `git commit` ou `git push` (R-031) nem alterar o índice do git.
- ❌ NUNCA gerar mensagem para diff com credencial/caminho local absoluto exposto (R-010 / R-044).
- ✅ O uso de context-mode é 100% OBRIGATÓRIO para leituras e inspeções quando disponível (R-008 / R-046 / R-056 / Smell 2.24 / Smell 2.26): toda coleta via `ctx_batch_execute` ou script consolidado em lote único. Proibido terminal de leitura e ferramentas nativas de editor; sem chamadas unitárias encadeadas.

## 📋 Fluxo em 5 Passos

### Passo 1 — Guardrail de Segredos (bloqueante)

Coletar em **uma** chamada batch: `git --no-pager diff HEAD -- . ':!*.lock' ':!*.min.js'`, `git --no-pager status --short`, `git --no-pager diff --stat HEAD`. Varrer o diff com o catálogo de `references/secrets-guardrail.md` (camada 3).

- Achado → **PARAR**, reportar `arquivo:linha` (sem ecoar o valor), exigir remoção + rotação.
- Limpo → prosseguir.

### Passo 2 — Inspeção do Stage

Priorizar `Changes to be committed`. Sem stage: listar modificados relevantes e sugerir `git add <arquivos>`. Stage misto: sugerir `git add` complementar para a mesma intenção.

### Passo 3 — Atomicidade

Aplicar o teste do "e" (`references/commit-formats.md` § 3). Não-atômico → sugerir split (`git add -p`) e gerar uma mensagem por commit.

### Passo 4 — Classificação e Estrutura

Definir tipo, escopo e breaking change (`references/commit-formats.md` § 1-2). Escolher o formato por volume: **A** (1-5 arquivos) ou **B** (6+ ou múltiplas frentes) — § 4-5. Incluir "Como validar" (§ 6), motivo/substituto para removidos (§ 7) e trailers reais (§ 8).

### Passo 5 — Apresentação

> **Anti-Corrupção de Markdown**: NUNCA encapsular a resposta inteira em bloco global; cada artefato copiável deve ser um bloco isolado e autocontido (Blocos 1 a 5).

Apresentar a saída estruturada nas seguintes seções claras:

1. **Bloco 1 (Mensagem de Commit)**: bloco ```text isolado pronto para revisão (Formato A ou Formato B conforme `references/commit-formats.md`).
2. **Bloco 2 (Comando para Execução Manual)**: bloco ```bash isolado utilizando `git commit -F - << 'EOF' ... EOF` (precedido de `git add` se sugerido) para preservar formatação e evitar cercas aninhadas.
3. **Bloco 3 (Título do PR)**: bloco ```text isolado no formato Conventional Commits (≤72 cols, imperativo, PT-BR).
4. **Bloco 4 (Descrição do PR)**: bloco ````markdown isolado (delimitado por 4 backticks) com seções "O que mudou", "Matriz de Risco", "Plano de Rollback", "Como validar" e "Checklist" (alinhado a `references/pr-template.md`). Em "Como validar", usar inline code para evitar conflito de cercas.
5. **Bloco 5 (CHANGELOG.md - Entrada Sugerida)**: bloco ```diff isolado sugerido no formato Keep a Changelog / SemVer (alinhado a `references/changelog.md`).

A matriz de risco segue `references/risk-matrix.md`. Em "Como validar", usar inline code.

## ✅ Checklist Antes de Exibir

- [ ] Guardrail de segredos executado e diff limpo
- [ ] Mensagem reflete o stage; atomicidade respeitada
- [ ] Título imperativo, PT-BR, sem ponto final, ≤ 72 cols; corpo ≤ 72 cols
- [ ] Removidos com motivo e substituto; "Como validar" presente
- [ ] PR com Matriz de Risco e Plano de Rollback; CHANGELOG compatível com SemVer
- [ ] Blocos isolados (sem cerca global ou aninhada)
- [ ] Nenhum comando git de escrita executado

## 🔄 Referências

- Skill SSOT: [`.github/skills/git-governance/SKILL.md`](../skills/git-governance/SKILL.md)
- Consumidor correlato: [`@pr-gatekeeper`](../agents/pr-gatekeeper.agent.md)

---

*v2.0 — commit prompt — modularizado sobre git-governance (SSOT única)*

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
7. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".

</execution_protocol>
