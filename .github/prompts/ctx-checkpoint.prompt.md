---
name: ctx-checkpoint
description: Grava snapshot de sessão no Context Mode via `ctx_index` (persistência cross-session) para retomada com `/ctx-resume`.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools:
  - context-mode/ctx_index
argument-hint: ''
source_docs:
  - .github/skills/context-mode/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/ctx-checkpoint`

Persiste o estado da sessão atual antes de pausar, trocar de tarefa ou fechar sessão.

> **Propósito**: Gravar snapshot de sessão no Context Mode via `ctx_index` para persistência e recuperação cross-session.
> **Workspace**: `${workspaceFolder}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** persistir o snapshot condensado da sessão atual no FTS5 ContentStore via `ctx_index`.
- ✅ **SEMPRE** analisar a conversa e extrair os campos estruturados (`lastStep`, `nextStep`, `completedActions`, `decisions`).
- ❌ **NÃO** gravar conteúdo bruto não filtrado no FTS5.
- ❌ **NÃO** modificar arquivos de código durante o checkpoint.

---

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
