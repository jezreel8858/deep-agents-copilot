# Router Return Section Sync (R-042 — Anti Sticky-Session)

> Sincronização e padronização determinística da seção `## Retorno ao Router (R-042 — Anti Sticky-Session)` em todos os agentes não-roteadores do ecossistema.

---

## 1) 🎯 Objetivo e Escopo

Garante que todos os 85 agentes especializados apresentem visibilidade de fluxo padronizada e banner canônico em conformidade com o padrão de mercado (OpenAI Agents SDK `HandoffOutputItem` e LangGraph `active_agent`), preservando integralmente suas regras específicas de roteamento, handoffs e gatilhos de circuit breaker.

### Artefatos:
- **Fonte Canônica:** `tools/agent_router_return_sync/_router-return-fragment.md`
- **Script Executor:** `tools/agent_router_return_sync/sync_router_return.py`
- **Núcleo Compartilhado:** `tools/governance_sync/core.py`

---

## 2) 🛠️ Modos de Operação (CLI)

```bash
# 1. Modo Check (default fail-safe / CI)
python tools/agent_router_return_sync/sync_router_return.py --check

# 2. Modo Dry-Run (visualização de diffs unificados)
python tools/agent_router_return_sync/sync_router_return.py --dry-run

# 3. Modo Apply (aplicação física das alterações)
python tools/agent_router_return_sync/sync_router_return.py --apply
```
