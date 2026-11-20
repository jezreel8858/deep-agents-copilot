# Instruções de IA — Base de Governança Reutilizável

## 1) Diretriz & Separação de Camadas (R-003 / R-038 / R-043)
- **SSOT Normativo:** Regras universais residem em [`CLAUDE.md`](../CLAUDE.md) e [`.github/agents/workflows/invariantes-e-protocolos.md`](agents/workflows/invariantes-e-protocolos.md).
- **Governança Global (`.github/agents/`, `.github/skills/`, `.github/prompts/`):** Genérica e agnóstica a stack (`R-038`).
- **Adapters (`.github/instructions/`):** Convenções de ecossistema (`*.instructions.md`) na raiz; bindings específicos de projeto exclusivamente em `local/` e `projects.local.yaml` (gitignored, `R-043`).

## 2) Ponto de Entrada & Orquestração Plana (R-037 / R-063 / R-068)
## Raiz = Executor de Workflow (R-068)
- **Agent Router First (`R-037` / `R-063`):** Sem agent ativo → **triagem normal** obrigatória via `@agent-router` (`run_subagent`) antes de qualquer tool (exceto Slash Prompts com `router_bypass: utility | slash_workflow`).
- **Orquestração Plana (`R-068`):** O `agent-root` despacha 1 etapa por vez de `ordem_execucao` — proibição de impersonação pelo Orquestrador Raiz (`R-062`), sem editar código nem pular/reordenar etapas; valida `receipt` + `step_delta` (`.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml`), bloqueia `plan_drift_detected` (`R-064`) e espelha estado em `ctx_index` (`wf:<trace>:state`).
- **Anti Sticky-Session (`R-042` / `R-052`):** Reavalie intenção a cada turno; avance `etapa_atual` se o pipeline estiver ativo ou retorne ao `@agent-router` em deriva/conclusão.
- **Pré-condição & Fluxo Canônico (`R-006` / `R-041` / `R-050` / `R-064` / `R-065`):** Pedidos ambíguos → `@prompt-structuring` (máx. 5x) → `@agent-router`. Planos → `@docs-engineer` (`DRAFT` em `docs/plans/<tipo>/`, sem prefixos `PLAN-`/`REQ-`) → `@plan-critic` (Two-Tier Hybrid, máx. 2x/3x, Noise Budget ≤ 5) → Gate HITL (`ask_questions`).

## 3) Regras Operacionais Não Negociáveis
- **Context Mode 100% Obrigatório (`R-008` / `R-056`):** Use `context-mode` MCP (`ctx_execute` JS `fs`/`path`, `ctx_batch`, `ctx_search`, `ctx_index`); ferramentas nativas de editor são proibidas quando `context-mode` estiver ativo. Perfis: `COMPUTE_MUTATE`, `COMPUTE_READONLY` (sem escrita), `GATHER_ONLY` (sem `ctx_execute`) e `ROUTER_EXEMPT` (**Blindagem contra Discovery de Modelos (`R-054`)** — Zero Discovery absoluto).
- **Single-Turn Batching & Limiar >= 2 (`R-046` / `R-059`):** Aplique a **Regra do Limiar >= 2** (`Plan-Then-Batch`) e **Teto Rígido de Tool Turns (≤ 5) (`R-060`)**; no `ctx_execute`, use `language: "javascript"` (proibido `python -c` para I/O por bloqueio AMSI/Defender; máx. 1 retry com troca de estratégia em timeout).
- **Quality Gates & Reúso (`R-027` / `R-055` / `R-057` / `R-058` / `R-066` / `R-067`):** `ask_questions` com 1ª opção `(Recomendado)` (`R-027`); **Blueprint Técnico obrigatório (`R-058`)** pré-código; proibido delegar edição manual ao usuário (`R-057`); *Progressive Disclosure* (`R-066`); **Portão de Reúso Sistêmico (`R-055`)** (Q0..Q3) e **Protocolo de Avaliação de Pertinência de Importação de Skills (`R-067`)**.
- **Pergunte Primeiro:** Alterações destrutivas/irreversíveis ou decisões arquiteturais transversais não acordadas.

## 4) Model Routing Signal (R-021)
Emita quando a tarefa exigir modelo **1× ou superior** (ou fan-out ≥ 10 alvos `R-021.1` / 2 falhas consecutivas de teste `R-021.2`):
> 🧠 **Modelo recomendado: `<Claude Sonnet / GPT-5>`** — **Motivo:** `<1 linha>` | Troque o modelo e continue neste chat.
- **Fan-Out (`R-021.1`) & Retry-Rate Escalation (`R-021.2`):** Escalone para Claude Sonnet / GPT-5 em tarefas com **>= 10 alvos/arquivos/operações** homogêneas ou após 2 falhas consecutivas do mesmo teste.

| Perfil de Tarefa | Modelo | Custo |
|---|---|---|
| Exploração · contexto · Q&A · confirmação · MCP fetch | **Claude Haiku** | **0×** |
| Edições pequenas · respostas rápidas | Claude Haiku | 0.33× |
| Implementação padrão · refactor · fan-out ≥ 10 alvos (`R-021.1`) | Claude Sonnet / GPT-5 | 1× |
| Arquitetura complexa · debug crítico · decisão crítica | Claude Opus 5.5 | 3× |

## 5) Health Check, Mapa SSOT & Formato de Saída
- **Health Check (`R-034`):** Validar `.github/instructions/README.md`, confinamento em `local/` (`R-043`) e consulta sob demanda via `catalog.yaml` / `skills/.index.json` (`R-066`).
- **Compact Error Reporting (`R-020`):** `Causa: <raiz>` | `Local: <arquivo:linha>` | `Ação: <correção>`.
- **Saída Técnica (`R-028`):** Iniciar com `Agente Ativo: <nome>` seguido de: `1. Abordagem`, `2. Artefatos Modificados`, `3. Economia de Turnos`, `4. Riscos / Alinhamento`, `5. Próximo Passo`.

| Domínio Normativo | Fonte Única de Verdade (SSOT — R-003 / R-066) |
|---|---|
| Invariantes, pipeline, `workflow_tracking` e gates | `.github/agents/workflows/invariantes-e-protocolos.md` |
| Schema canônico `receipt` + `step_delta` | `.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml` |
| Contratos de agentes & handoff/hidratação | `.github/skills/agent-contracts/SKILL.md` · `.github/skills/handoff-governance/SKILL.md` |
| Catálogo ativo e índice de skills | `.github/agents/catalog.yaml` · `.github/skills/.index.json` |
