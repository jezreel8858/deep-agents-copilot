---
name: ctx-checkpoint
description: Grava snapshot de sessão no Context Mode via `ctx_index` (persistência cross-session) para retomada com `/ctx-resume`.
model: "Gemini 3.8 Flash"
tools:
  - context-mode/ctx_index
---

# /ctx-checkpoint

Persiste o estado da sessão atual antes de pausar, trocar de tarefa ou fechar sessão.

## Quando usar

- Antes de fechar o chat atual e querer continuar em um novo com `/ctx-resume`.
- Antes de uma pausa longa (risco de compactação automática).
- Após concluir uma fase importante de trabalho.

## Por que `ctx_index` e não `ctx_execute echo`?

`ctx_execute echo` só grava no sandbox da sessão corrente — não persiste de forma confiável no FTS5 entre sessões.
`ctx_index` grava explicitamente no FTS5 ContentStore e é recuperável via `ctx_search` em qualquer sessão futura.

## Execução obrigatória

### Passo 0 — Pré-checagem de sessão (Opcional)
Se quiser confirmar telemetria, execute `ctx_stats` antes do checkpoint.
Se qualquer chamada `ctx_*` retornar `Not connected`, aplique R-022: 1 tentativa de recuperação com `/ctx-start` e retome.

### Passo 1 — Análise comprimida da sessão (obrigatório antes de indexar)

Antes de chamar `ctx_index`, analise a conversa atual e extraia os campos abaixo.
**Para chats longos (> 20 turnos):** priorize as últimas 5 trocas + decisões explícitas; descarte steps de exploração superados por versões posteriores.

| Campo | Limite | Critério de extração |
|---|---|---|
| `lastStep` | 1 linha · ≤ 100 chars | Ação mais recente concluída |
| `nextStep` | 1 linha · ≤ 100 chars | Próxima ação imediata |
| `completedActions` | máx 3 items · ≤ 80 chars cada | Ações significativas da sessão (não triviais) |
| `decisions` | máx 2 items · ≤ 80 chars cada | Decisões técnicas/arquiteturais tomadas |
| `blockers` | máx 2 items · ≤ 80 chars cada | Impedimentos ativos não resolvidos (ou `na`) |
| `summary` | 1 linha · ≤ 120 chars | Essência da sessão — o que foi feito e por quê |

> **Budget total do content:** ≤ 600 chars. Se estourar, comprima `completedActions` primeiro, depois `decisions`. Nunca omita `lastStep`, `nextStep` e `summary`.

### Passo 2 — Gravar checkpoint no FTS5 via `ctx_index`

O `source` deve conter `task-slug` + data + hora para garantir unicidade entre múltiplos chats/checkpoints do mesmo task:

```javascript
ctx_index({
  source: "checkpoint::<task-slug>::<YYYY-MM-DD-HHmm>",
  content: `# CHECKPOINT

**task:** <task-slug>
**date:** <YYYY-MM-DD HH:mm>
**phase:** <fase-ou-na>
**status:** <status>
**tags:** <módulo>, <tecnologia>, <tipo-de-tarefa>, <status-keyword>
**lastStep:** <ação mais recente — 1 linha ≤100 chars>
**nextStep:** <próxima ação — 1 linha ≤100 chars>
**files:** <files-csv-ou-na>
**summary:** <resumo 1 linha ≤120 chars>

## Contexto Comprimido
**completedActions:**
- <ação 1 ≤80 chars>
- <ação 2 ≤80 chars>
- <ação 3 ≤80 chars>

**decisions:**
- <decisão 1 ≤80 chars>
- <decisão 2 ≤80 chars>

**blockers:**
- <bloqueio ≤80 chars>  (ou na)
`
})
```

> **Unicidade:** `checkpoint::<task-slug>::<YYYY-MM-DD-HHmm>` garante que cada checkpoint é identificável individualmente — múltiplos chats trabalhando no mesmo task não se sobrescrevem.
>
> **Tags — critérios:** termos que um agente provavelmente usaria em buscas futuras. Exemplos:
> - Módulo/domínio: `governanca`, `agents`, `skills`, `integracao`
> - Tecnologia: `backend`, `frontend`, `api`, `database`, `queue`
> - Tipo de tarefa: `migration`, `endpoint`, `test`, `refactor`, `docs`
> - Status keyword: `in-progress`, `phase-done`, `blocked`, `waiting-review`

### Passo 3 — Confirmar

Responda ao usuário confirmando o checkpoint com o `source` completo gerado e instrua como retomar:

```
✅ Checkpoint gravado: checkpoint::<task-slug>::<YYYY-MM-DD-HHmm>

Para retomar:
- Mesmo chat:    /ctx-resume "<task-slug>"
- Novo chat:     /ctx-resume "<task-slug>"  (após abrir novo chat)
```

## Regras

- **Passo 1 é obrigatório** — nunca indexar sem antes analisar e comprimir a sessão.
- `source` deve ter formato `checkpoint::<task-slug>::<YYYY-MM-DD-HHmm>` — nunca sem data/hora.
- Budget total do content: ≤ 600 chars — comprimir `completedActions` primeiro se necessário.
- O uso de `ctx_index(content: ...)` é permitido aqui apenas para payload curto e estruturado (checkpoint compacto).
- Não usar `ctx_execute echo` — não persiste cross-session.
- Não usar terminal; somente tools `ctx_*`.
- Não rodar testes/build junto do checkpoint.
- Se faltar parâmetro, preencher com `na` e seguir.

## Combina Com

- `/ctx-resume` → retoma o checkpoint gravado aqui
- `/ctx-status` → verifica consumo de contexto antes de criar checkpoint
- `/implement` → use checkpoint ao finalizar cada fase

