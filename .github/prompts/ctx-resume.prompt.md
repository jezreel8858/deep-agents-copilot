---
name: ctx-resume
description: Retoma contexto específico via `ctx_search(source:"checkpoint::<slug>")`. Cobre cenário de múltiplos chats abertos com checkpoints distintos — lista e seleciona o correto.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools:
  - context-mode/ctx_search
  - ask_questions
argument-hint: '[<task-slug>]'
source_docs:
  - .github/skills/context-mode/SKILL.md
  - .github/skills/agent-memory-policy/SKILL.md
  - .github/skills/terminal-governance/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/ctx-resume`

Reidrata contexto antes de planejar, implementar ou validar. Cobre: mesmo chat, novo chat, e múltiplos chats simultâneos com checkpoints diferentes.

> **Propósito**: Reidratar e restaurar o contexto de uma sessão anterior a partir de checkpoints salvos no FTS5.
> **Workspace**: `${workspaceFolder}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** buscar e reidratar os dados de checkpoints previamente salvos no FTS5.
- ✅ **SEMPRE** listar opções claras via `ask_questions` quando o slug não for fornecido.
- ❌ **NÃO** sobrescrever checkpoints existentes durante a retomada.
- ❌ **NÃO** executar ações do plano antes que o usuário confirme a retomada do contexto.

---

## Sintaxe

```
/ctx-resume                     → lista todos os checkpoints disponíveis
/ctx-resume "<task-slug>"       → resume direto do checkpoint do task especificado
```

## Execução obrigatória

### Passo 0 — Tentar retomada diretamente
Execute a busca de checkpoints primeiro.
Se houver falha por `Not connected`, aplique R-022 (1 auto-recuperação) e repita a busca uma única vez.

### Cenário 1 — Múltiplos chats / não sei qual retomar (sem argumento)

**Passo 1a — Listar todos os checkpoints disponíveis:**

```javascript
ctx_search({
  queries: ["task date lastStep nextStep summary"],
  source: "checkpoint::",
  limit: 10
})
```

**Passo 1b — `ask_questions` compacto com opção de detalhe:**

> ⚠️ JetBrains: só `question` e `label` renderizam — `description` e `\n` no `question` não funcionam.
> **Solução:** options compactas para retomar + options `🔍 Detalhar` para ver detalhes em markdown puro no turno seguinte.

```javascript
ask_questions({
  questions: [{
    header: "checkpoint-selector",
    question: "Checkpoints disponíveis — selecione para retomar ou 🔍 para ver detalhes:",
    allowFreeformInput: false,
    options: [
      // --- opções de retomada direta (uma por checkpoint) ---
      { label: "<task-slug>::<YYYY-MM-DD-HHmm>  ✅ done" },
      // --- opções de detalhe (uma por checkpoint) ---
      { label: "🔍 Detalhar: <task-slug>" }
    ]
  }]
})
```

**Se o usuário selecionou um checkpoint direto (sem 🔍):** ir para o Passo 1c.

**Se o usuário selecionou 🔍 Detalhar `<task-slug>`:** responder com **somente markdown** (sem nenhuma tool call — garante renderização correta).

Inclua todos os campos disponíveis no checkpoint recuperado:

```markdown
**🔖 <task-slug>::<YYYY-MM-DD-HHmm>  ✅ done**

↩ **último:** <lastStep>
→ **próximo:** <nextStep>
📁 `<arquivo1>` · `<arquivo2>`
🏷 <tag1> · <tag2>

📋 **Resumo:** <summary>

✅ **Ações concluídas:**
- <ação 1>
- <ação 2>

🧠 **Decisões:**
- <decisão 1>

🚧 **Blockers:** nenhum (ou lista)

---
Para retomar responda **"retomar"**, ou rode **/ctx-resume** para ver a lista novamente.
```

> Campos obrigatórios: `🔖 header`, `↩ último`, `→ próximo`, `📁 files`, `🏷 tags`, `📋 Resumo`.
> Campos condicionais (exibir se presentes): `✅ Ações concluídas`, `🧠 Decisões`, `🚧 Blockers`.

**Passo 1c — Após a escolha, buscar o checkpoint específico:**

```javascript
ctx_search({
  queries: ["task lastStep nextStep files summary"],
  source: "checkpoint::<task-slug-escolhido>",
  limit: 3
})
```

---

### Cenário 2 — Task específico já conhecido (com argumento)

**Passo 2a — Buscar diretamente pelo task-slug:**

```javascript
ctx_search({
  queries: ["task lastStep nextStep files summary"],
  source: "checkpoint::<task-slug>",
  limit: 3
})
```

> Se múltiplos checkpoints do mesmo task existirem (datas diferentes), o mais recente aparece primeiro. Use `ask_questions` com cada data como option para que o usuário confirme qual é o correto.

---

### Passo final — Resumir e propor

## Saída esperada

```
Contexto recuperado [checkpoint::<task-slug>::<date>]:

- task: ...
- Último passo: ...
- Próximo passo: ...
- Arquivos relevantes: ...
- Decisões/bloqueios: ...

Posso seguir com [ação proposta]?
```

## Regras

- **Sem argumento:** `ask_questions` compacto com opções de retomada direta + `🔍 Detalhar` por checkpoint. Se usuário escolher detalhe → próxima resposta é **somente markdown** (sem tool call). Se retomar direto → Passo 1c.
- **Com argumento:** buscar por `source: "checkpoint::<task-slug>"` direto; se único resultado, prosseguir sem perguntar.
- **Múltiplos checkpoints** do mesmo task: usar `ask_questions` com as datas como options, aguardar confirmação.
- **`ask_questions` é obrigatório** para qualquer seleção interativa neste comando.
- Timeline geral (`sort: "timeline"`) é fallback apenas se `source: "checkpoint::"` retornar vazio.
- Não executar build/teste automaticamente.
- Não usar terminal; somente tools `ctx_*`.

## Retomada Após Crash/Trava SEM Checkpoint Prévio (Fallback Best-Effort)

Quando não há checkpoint salvo via `/ctx-checkpoint` (nem checkpoint automático pré-risco de `agent-memory-policy/SKILL.md` § 3.2) — sessão travou/crashou sem persistência prévia — aplicar reconstrução best-effort.

### Passo F1 — Inspecionar estado do repositório

```bash
git --no-pager status
git --no-pager diff --stat
```

### Passo F2 — Inspecionar arquivos recentemente modificados (via sandbox, nunca via terminal find/ls)

```javascript
const { execSync } = require('child_process');
console.log(execSync('git --no-pager diff --name-only', { encoding: 'utf8' }));
```

### Passo F3 — Reportar reconstrução ao usuário e confirmar antes de prosseguir

```markdown
⚠️ Nenhum checkpoint encontrado — reconstrução best-effort a partir do estado do repositório:

**Arquivos modificados (não commitados):** <lista de git diff --stat>
**Último commit:** <git log -1 --oneline>

Não é possível recuperar decisões/raciocínio de sessões anteriores. Confirme se devo prosseguir a partir deste estado ou se prefere descartar as mudanças pendentes.
```

- Nunca assumir automaticamente o próximo passo — sempre confirmar via `ask_questions` antes de prosseguir.
- Esta é a via de **último recurso**; o checkpoint automático pré-risco (`agent-memory-policy/SKILL.md` § 3.2) existe justamente para evitar cair neste cenário.

---

## Combina Com

- `/ctx-checkpoint` → cria o checkpoint que este retoma
- `/plan` → use após retomar para planejar próximo passo
- `/implement` → use após retomar para continuar implementação

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
