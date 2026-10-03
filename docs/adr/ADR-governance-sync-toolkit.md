---
id: ADR-0012
title: "Governance Sync Toolkit: Arquitetura de Sincronização Determinística de Governança"
status: Aceito
date: 2026-09-29
decision-makers:
  - governance-maintainer
  - tech-solution-architect
consulted:
  - agent-auditor
  - codegraph-engine
informed:
  - adr-sentinel
  - pr-gatekeeper
type: architectural-decision
diataxis: explanation
---

# ADR-0012: Governance Sync Toolkit: Arquitetura de Sincronização Determinística de Governança

> **Status**: Aceito  
> **Data de Referência**: 2026-09-29  
> **Área / Módulo**: `tools/governance_sync`, `tools/agent_protocol_sync`, `tools/agentcard_exporter`, `tools/agent_router_return_sync`  
> **Origem**: Padronização da governança em lote e eliminação de drift estocástico (R-051, R-059, R-060)

---

## 1. Contexto e Declaração do Problema

O ecossistema `deep-agents-copilot` ultrapassou 85 agentes especializados organizados em subdomínios técnicos e governamentais. Modificações transversais que impactam blocos estruturais repetidos — como `<execution_protocol>` (R-059/R-060), metadados de AgentCards A2A (v1.0.0) e a seção `## Retorno ao Router (R-042)` — enfrentavam os seguintes desafios:

1. **Queima Excessiva de Tokens:** Realizar dezenas de tool-calls sequenciais via chat consome créditos premium desnecessariamente.
2. **Deriva Estocástica e Erros de Codificação:** Operações ad-hoc via regex em chat ou comandos de terminal causavam corrupção de caracteres especiais ou quebras acidentais de frontmatter.
3. **Ausência de Gates em CI:** Sem comandos determinísticos executáveis via GitHub Actions, drifts não detectados chegavam às branches principais.

Já existiam dois precedentes consolidados:
- `tools/agent_protocol_sync/sync_execution_protocol.py` (com suporte a `--check`, `--dry-run`, `--apply`).
- `tools/agentcard_exporter/export_agentcards.py` (anteriormente sem padronização de flags CLI).

---

## 2. Decisão Arquitetural: Branch by Abstraction Incremental

Optou-se por **NÃO** consolidar abruptamente os dois scripts existentes em um monólito acoplado nesta rodada. Em vez disso, adota-se o padrão **Branch by Abstraction**:

1. **Núcleo Fino Reutilizável (`tools/governance_sync/core.py`):**
   - Centraliza o parser unificado com as 3 flags canônicas: `--check` (default/fail-safe), `--dry-run` e `--apply`.
   - Modela os contratos de saída, relatório de drift (`SyncReport`) e cálculo de exit codes (`0` para conformidade, `1` para drift ou erro em `--check`).
   - Fornece motor utilitário de diff unificado (`compute_unified_diff`).

2. **Evolução Gradual dos Scripts:**
   - O novo script do Nó 6 (`tools/agent_router_return_sync/sync_router_return.py`) nasce já consumindo nativamente `tools/governance_sync/core.py`.
   - `export_agentcards.py` foi alinhado ao mesmo contrato de interface CLI (`--check`/`--dry-run`/`--apply`).
   - A migração física dos scripts legados para importar o `core.py` (Nó 8) fica postergada para após a 3ª instância comprovar estabilidade em produção.

---

## 3. Consequências

### Positivas:
- **Segurança Fail-Safe:** Scripts de governança executados sem argumentos entram em modo `--check` (read-only), impedindo gravações acidentais.
- **Fail-Hard CI Gates:** Os workflows de GitHub Actions (`routing-quality-gate.yml`) validam a integridade dos artefatos antes dos testes de unidade, bloqueando PRs com drift em tempo de execução ultra-baixo (<2s).
- **Sem Risco de Regressão nos Legados:** `sync_execution_protocol.py` e `export_agentcards.py` mantêm sua estabilidade operacional comprovada.

### Negativas / Débito Técnico Planejado:
- Existe duplicação temporária da lógica de parser entre os scripts legados e o `core.py`, a ser eliminada na fase subsequente (Nó 8).
