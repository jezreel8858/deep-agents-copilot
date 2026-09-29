# Fonte Canônica: Seção "Retorno ao Router (R-042 — Anti Sticky-Session)"

Este arquivo define o fragmento canônico normativo da seção de Retorno ao Router (R-042)
utilizado por `tools/agent_router_return_sync/sync_router_return.py`.

---

<!-- BEGIN:HEADING -->
## Retorno ao Router (R-042 — Anti Sticky-Session)
<!-- END:HEADING -->

<!-- BEGIN:BANNER -->
**Banner obrigatório (visibilidade de fluxo)**: toda resposta deste agent abre com a linha `Agente Ativo: {AGENT_ID}` antes de qualquer outro conteúdo — mesmo sem handoff neste turno. Se esta resposta é resultado de handoff/re-triagem recebido, adicionar `Handoff: <agent-origem> → {AGENT_ID} (motivo: <motivo>)` na linha seguinte. Padrão de mercado: OpenAI Agents SDK (`HandoffOutputItem` — "Handed off from X to Y") e LangGraph (campo `active_agent` streamado ao usuário) — ver `agent-contracts/SKILL.md` seção 0.
<!-- END:BANNER -->

<!-- BEGIN:TELEMETRY -->
**Telemetria de Handoff (Decisão de Baseline R-054 / handoff-governance § 2.4)**: Por princípio de Least Privilege e Zero Discovery (R-054), os routers operam com as 7 tools canônicas e **NÃO** possuem `context-mode/ctx_index` em sua baseline. Consequentemente, o router não emite `ctx_index` diretamente ao despachar; a responsabilidade pelo registro físico do evento `telemetry_entry` (tag `[HANDOFF]`, campos `session_id` e `sequence_index`) recai compulsoriamente sobre o **AGENT RECEPTOR / DELEGADO** (que possui `ctx_index` em sua baseline), o qual registra o evento referenciando `origem_contexto.parent_agent` como este router emissor.
<!-- END:TELEMETRY -->
