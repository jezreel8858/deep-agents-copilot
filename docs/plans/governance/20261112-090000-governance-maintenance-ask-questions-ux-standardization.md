---
status: COMPLETED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-12"
date: "2026-11-12"
related-planning-doc: "N/A — plano raiz (WORKFLOW-GOVERNANCE-MAINTENANCE)"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
allowed_files:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - ".github/skills/**"
  - ".github/agents/**"
  - ".github/prompts/**"
  - "tools/agent_protocol_sync/**"
  - "tests/governance_audit/**"
---

# Plano de Manutenção de Governança — Padronização Universal de UX na Tool `ask_questions` (R-027)

## 1. Contexto e Diagnóstico de Causa Raiz (RCA)

A inspeção da malha de agentes revelou que o contrato da ferramenta nativa de clarificação e gate humano (`ask_questions`, regida pela invariante **R-027**) apresentava especificações heterogêneas entre documentos normativos (`CLAUDE.md`, `invariantes-e-protocolos.md`), skills de protocolo, perfis operacionais de agentes (`.agent.md`) e o sincronizador automatizado (`tools/agent_protocol_sync/`).

### Problemas Diagnosticados
1. **Ausência de Formato Canônico para `description` das Opções**: Vários agentes listavam opções em `ask_questions` sem o campo `description` ou sem explicitar a consequência prática e o trade-off técnico de cada escolha.
2. **Falta de Indicação da Opção Recomendada**: Quando havia uma melhor prática técnica evidente, ela não era consistentemente posicionada na 1ª opção com o sufixo `(Recomendado)`.
3. **Limites Estruturais Inconsistentes**: Divergência na exigência explícita de `1 a 4 perguntas por chamada`, `header <= 25 caracteres`, `allowFreeformInput: true` e `2 a 4 opções reais sem espantalhos`.
4. **Propagação Incompleta (Tríade Q1+Q2+Q3 — R-055)**: O gerador `tools/agent_protocol_sync/protocol_sync.py` e a suíte `tests/governance_audit/` não validavam o contrato completo de UX de `ask_questions` em todos os agentes da malha.

---

## 2. Escopo, Critérios de Aceitação (CA-01 a CA-06) e Regras Impactadas

### 2.1 Regras Impactadas
- **R-027 (Clarificação Estruturada via `ask_questions`)**: Padronização universal dos parâmetros estruturais e de UX das perguntas e opções.
- **R-034 (Gates de Aprovação Humana — HITL)**: Alinhamento dos checkpoints humanos de aprovação de planos com o novo padrão de opções e descrições de R-027.
- **R-055 (Integridade Sistêmica Universal — Tríade Q1+Q2+Q3)**: Sincronização completa entre regras/skills (Q1), agentes/prompts/ferramenta de sync (Q2) e testes automatizados pytest (Q3).
- **R-064 (Persistência Física Universal de Planos)**: Registro físico deste plano em `docs/plans/governance/` para rastreabilidade histórica da evolução da malha.

### 2.2 Critérios de Aceitação (CA-01 a CA-06)
- **CA-01 (Contrato Normativo R-027 Unificado)**: `CLAUDE.md`, `.github/copilot-instructions.md` e `.github/agents/workflows/invariantes-e-protocolos.md` especificam integralmente a assinatura UX de `ask_questions`: 1–4 perguntas, `header` <= 25 chars, `allowFreeformInput: true`, 2–4 opções mutuamente exclusivas sem espantalhos, `description` obrigatório no formato `[Consequência prática + Trade-off/quando escolher]` e 1ª opção marcada com `(Recomendado)`.
- **CA-02 (Skills de Governança Atualizadas)**: As skills de contratos e handoffs refletem o padrão obrigatório de `description` e `(Recomendado)` nos exemplos e regras de clarificação.
- **CA-03 (Sincronização Automatizada do Protocolo de Execução)**: `tools/agent_protocol_sync/protocol_sync.py` injeta a cláusula atualizada de R-027 no bloco `<execution_protocol>` (item 4 — Circuit Breaker / Clarificação) de todos os agentes aplicáveis.
- **CA-04 (Alinhamento dos Agentes e Prompts de Entrada)**: Perfis de agentes planejadores, roteador, auditor e prompts estruturadores incorporam o padrão UX de `ask_questions`.
- **CA-05 (Cobertura Determinística em Testes Pytest — Q3)**: Suíte `tests/governance_audit/` valida a presença dos invariantes de R-027 nos arquivos normativos e agentes sincronizados.
- **CA-06 (Zero Regressão na Malha)**: 100% dos testes da suíte de auditoria de governança executados com sucesso e zero erros de lint/schema.

---

## 3. Artefatos Atualizados na Entrega (21 Arquivos)

A execução consolidada abrangeu os 21 artefatos abaixo na malha de governança:

| # | Caminho do Artefato | Quadrante (R-055) | Natureza da Atualização |
| :--- | :--- | :--- | :--- |
| 1 | `CLAUDE.md` | Q1 (Normativo) | Atualização da definição canônica da regra R-027 com requisitos de `description` e `(Recomendado)`. |
| 2 | `.github/copilot-instructions.md` | Q1 (Normativo) | Espelhamento da invariante R-027 nas instruções globais do Copilot. |
| 3 | `.github/agents/workflows/invariantes-e-protocolos.md` | Q1 (Normativo) | Detalhamento técnico do contrato de UX da tool `ask_questions` (R-027 / R-034). |
| 4 | `.github/skills/agent-contracts/SKILL.md` | Q1 (Skill) | Padronização do contrato de interação humana via `ask_questions`. |
| 5 | `.github/skills/handoff-governance/SKILL.md` | Q1 (Skill) | Alinhamento dos gates de handoff e clarificação com R-027. |
| 6 | `.github/skills/plan-conformance-patterns/SKILL.md` | Q1 (Skill) | Padronização do checkpoint de aprovação de planos via `ask_questions`. |
| 7 | `tools/agent_protocol_sync/protocol_sync.py` | Q2 (Tooling) | Atualização do template de `<execution_protocol>` (item 4) com a assinatura completa de R-027. |
| 8 | `.github/agents/agent-router.agent.md` | Q2 (Agente) | Sincronização de R-027 para desambiguação de intenção e gates de roteamento. |
| 9 | `.github/agents/agent-auditor.agent.md` | Q2 (Agente) | Sincronização de R-027 para checkpoints de diagnóstico de governança. |
| 10 | `.github/agents/governance-maintainer.agent.md` | Q2 (Agente) | Sincronização do protocolo de execução com R-027. |
| 11 | `.github/agents/requirements-analyst.agent.md` | Q2 (Agente) | Padronização do levantamento de requisitos via `ask_questions` (R-027). |
| 12 | `.github/agents/feature-planner.agent.md` | Q2 (Agente) | Padronização de perguntas de escopo e gate de plano com R-027. |
| 13 | `.github/agents/refactor-planner.agent.md` | Q2 (Agente) | Padronização de clarificação de refatoração com R-027. |
| 14 | `.github/agents/tech-solution-architect.agent.md` | Q2 (Agente) | Padronização de trade-offs arquiteturais nas opções de `ask_questions`. |
| 15 | `.github/agents/bug-triage.agent.md` | Q2 (Agente) | Sincronização do protocolo de triagem e clarificação com R-027. |
| 16 | `.github/agents/test-strategy.agent.md` | Q2 (Agente) | Sincronização do protocolo de estratégia de testes com R-027. |
| 17 | `.github/agents/docs-engineer.agent.md` | Q2 (Agente) | Sincronização do `<execution_protocol>` com R-027. |
| 18 | `.github/agents/prompt-structuring.agent.md` | Q2 (Agente) | Inclusão das regras de UX de `ask_questions` na estruturação de prompts e clarificação. |
| 19 | `.github/agents/templates/specialist-agent-template.md` | Q2 (Template) | Atualização do template base de agentes especialistas com a cláusula R-027. |
| 20 | `.github/prompts/craft-prompt.prompt.md` | Q2 (Prompt) | Alinhamento do prompt `/craft-prompt` com o contrato UX de `ask_questions`. |
| 21 | `tests/governance_audit/test_ask_questions_r027_governance.py` (e suíte correlata em `tests/governance_audit/`) | Q3 (Testes) | Validação automatizada dos invariantes de R-027 na malha de governança. |

---

## 4. Status de Execução e Rastreabilidade

- **Estado do Plano**: `COMPLETED` (`approved: true`).
- **Conformidade R-064**: Materializado fisicamente em `docs/plans/governance/20261112-090000-governance-maintenance-ask-questions-ux-standardization.md` para assegurar 100% de paridade e rastreabilidade histórica em disco das manutenções de governança realizadas na sessão.
