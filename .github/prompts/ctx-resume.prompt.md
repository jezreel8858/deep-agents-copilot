---
name: ctx-resume
description: Retoma contexto específico via `ctx_search(source:"checkpoint::<slug>")`. Cobre cenário de múltiplos chats abertos com checkpoints distintos — lista e seleciona o correto.
model: "Gemini 3.8 Flash"
---

# /ctx-resume

Reidrata contexto antes de planejar, implementar ou validar. Cobre: mesmo chat, novo chat, e múltiplos chats simultâneos com checkpoints diferentes.

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

## Combina Com

- `/ctx-checkpoint` → cria o checkpoint que este retoma
- `/plan` → use após retomar para planejar próximo passo
- `/implement` → use após retomar para continuar implementação

