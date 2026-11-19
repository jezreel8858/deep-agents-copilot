---
title: "Protocolo Estruturado de Recibo e Delta de Etapa (receipt + step_delta)"
status: "APPROVED"
approved: true
author: "governance-maintainer"
plan_type: "governance"
created_at: "2026-11-18T20:35:00-03:00"
related_rules:
  - "R-003"
  - "R-042"
  - "R-051"
  - "R-059"
  - "R-064"
  - "R-068"
ssot_schema: ".github/skills/agent-contracts/references/receipt-step-delta-schema.yaml"
---

# Protocolo Estruturado de Recibo e Delta de Etapa (`receipt` + `step_delta`)

## 1. Visão Geral

Com a adoção do contrato `receipt` + `step_delta`, a centralização do schema em **Fonte Única de Verdade (SSOT YAML)** e a sincronização automatizada para todos os **63 agentes** e **24 prompts** mapeados, o ecossistema multi-agente substitui a passagem de contexto em prosa livre por um **pipeline determinístico, auditável e econômico em tokens**.

## 2. Ganhos Arquiteturais e Operacionais

| Dimensão | Antes (Prosa Livre) | Agora (`receipt` + `step_delta`) | Impacto Prático |
| :--- | :--- | :--- | :--- |
| **Continuidade entre Etapas (`R-068` / `R-059`)** | O agente receptor (`N+1`) recebia um resumo textual genérico e precisava redescobrir arquivos e assinaturas via `ctx_batch` / `grep_search`. | O `agent-root` extrai `files_modified`, `files_created`, `exports_and_signatures` e `notes_for_next_step` e injeta no despacho seguinte. | Elimina turnos redundantes de descoberta e reduz consumo de tokens por pipeline. |
| **Janela de Contexto (`overflow_ref`)** | Refatorações em lote com dezenas de arquivos inflavam o chat ou sofriam truncamento silencioso no handoff. | Teto rígido de **10 itens inline** por lista; excedentes são indexados no `context-mode` MCP sob `wf:<trace>:delta:step-<n>`. | Mantém o histórico do chat enxuto sem perda de inventário técnico (*Claim-Check Pattern*). |
| **Detecção de *Plan Drift* (`R-064`)** | Aderência a `allowed_files` dependia apenas de auditoria pós-execução ou revisão humana. | Todo executor preenche `step_delta.plan_conformance` (`within_allowed_files` e `out_of_scope_files`). | Bloqueio imediato antes da próxima etapa com retorno ao `@agent-router` (`motivo: "plan_drift_detected"`). |
| **Paridade Executores vs. Analíticos (`Score 0`)** | Agentes *read-only* / *advisory* não possuíam formato estruturado padrão para repassar contratos e regras descobertas. | Suporte nativo a `mode: mutation` e `mode: readonly_analysis` no mesmo schema YAML. | Fluxo uniforme entre descoberta (`@business-rules-extractor`, `@tech-solution-architect`) e execução. |
| **SSOT e Sincronização (`R-003` / `R-055`)** | Blocos YAML duplicados em múltiplos `.md` e cabeçalhos duplicados nos templates. | Schema único em `receipt-step-delta-schema.yaml` e propagação via `sync_execution_protocol.py --apply`. | Zero deriva documental (`0 drift` validado em 63 agentes e 24 prompts). |
| **Auditoria Automatizada (`pytest`)** | Validação contratual dependia de *parsing* frágil de texto livre em Markdown. | Contrato formalizado em YAML versionado e estruturado. | Base pronta para validação determinística em CI (`tests/governance_audit/`). |

## 3. Artefatos Alterados e Sincronizados

- **Contrato Canônico (SSOT):** `.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml`
- **Orquestrador e Regras Globais:**
  - `.github/agents/agent-root.agent.md`
  - `.github/copilot-instructions.md`
  - `.github/agents/workflows/invariantes-e-protocolos.md` (§ 4.2–4.3)
- **Skills de Governança:**
  - `.github/skills/agent-contracts/SKILL.md` (§ 4.1)
  - `.github/skills/handoff-governance/SKILL.md` (§ 4.1)
- **Templates Higienizados:**
  - `.github/agents/templates/agent-template.md`
  - `.github/agents/templates/operational-agent.md`
  - `.github/agents/templates/research-agent.md`
- **Sincronização Transversal:**
  - `tools/agent_protocol_sync/_execution-protocol-fragment.md` (propagado via `python tools/agent_protocol_sync/sync_execution_protocol.py --apply` e validado com `--check`).

## 4. Próximo Passo Recomendado

- Adicionar suíte de regressão determinística em `tests/governance_audit/` para validar a integridade estrutural do `receipt-step-delta-schema.yaml`, o limite `max_inline_items: 10` e a paridade de referências entre `agent-root.agent.md`, `invariantes-e-protocolos.md` e as skills de contrato.
