---
id: ADR-0015
title: "Raiz Declarada: Agent `agent-root` como Turno Raiz Explícito com @agent-router como Único Classificador"
status: Aceito
date: 2026-11-18
decision-makers:
  - governance-maintainer
  - tech-solution-architect
consulted:
  - agent-auditor
  - adr-sentinel
  - plan-critic
informed:
  - pr-gatekeeper
type: architectural-decision
diataxis: explanation
---

# ADR-0015: Raiz Declarada: Agent `agent-root` como Turno Raiz Explícito com @agent-router como Único Classificador

> **Status**: Aceito (2026-11-18 — ratificado no encerramento E6 do workflow `wf-20261118-agent-root-criacao` com parecer `@agent-auditor` `PASS_WITH_WARNINGS` `[L]` e waiver HITL)

## 1. Contexto

A autoridade do turno raiz é difusa: nenhum artefato declara quem responde antes da triagem. O R-068 (zero impersonation) já se aplica, mas sem um agent raiz declarado a regra não tem âncora explícita.

Premissas e incertezas:

- O agent selecionado no dropdown do host vira o turno raiz (confiança média, não verificada em todos os hosts).
- Há incerteza sobre se `copilot-instructions.md` é somado ao corpo do custom agent selecionado.
- Decisão humana explícita registrada no Gate 4: "assumo o risco... crie o agent-root".

Regras envolvidas: R-062 e R-063 (Router First) e R-068 (zero impersonation). O plano aprovado é `docs/plans/governance/20261118-110000-governance-maintenance-agent-root-criacao.md`.

## 2. Drivers

| Driver | Relevância |
|---|---|
| R-037 | Governança de criação e catalogação de agents |
| R-062 / R-063 | Router First sem autoridade difusa |
| R-068 | Zero impersonation: o raiz não assume identidade de outros agents |
| R-047 / R-054 | Topologia plana; roteadores sem hidratação e sem `context-mode` |
| R-066 | Conformidade com o contrato de execução dos agents |
| Orçamento M2 | Teto de +2.048 B no kernel; folga de 555 B após a mudança |

## 3. Alternativas

| Opção | Descrição | Veredito |
|---|---|---|
| Status quo | Manter a autoridade difusa do raiz | Rejeitada: mantém o problema |
| A | Declaração mínima sem agent dedicado | Rejeitada: não fornece âncora selecionável |
| B' endurecida | Agent `agent-root` com 5 tools exatas, nó no grafo sem arestas de entrada e exceção de identidade em redação única | **Escolhida** |
| D | Prompt de bootstrap | Descartada: não define turno raiz e depende de invocação manual |
| E+D do plano pai | Combinação de E com prompt de bootstrap | Superada pela B' endurecida |
| Ponteiro × mini-kernel | Agent-root apenas aponta ao SSOT ou carrega um mini-kernel próprio | **Ponteiro escolhido**: evita duplicar o kernel e preserva o orçamento M2 |

## 4. Decisão

1. O agent selecionado no dropdown é o turno raiz.
2. O nome literal `agent-root` só pode ser usado no turno raiz.
3. `@agent-router` permanece o único classificador de intenção.
4. O `agent-root` declara exatamente 5 tools.
5. Nó no `routing-graph.yaml` com `tipo: downstream` e sem arestas de entrada, sem alterar schema, `model.py` ou runner.
6. A exceção de identidade ao R-068 é escrita uma única vez, no SSOT `invariantes-e-protocolos.md`, e apenas referenciada pelos demais artefatos.
7. O `agent-root` é um ponteiro puro, sem mini-kernel.

Registro: a topologia plana (R-047/R-054) não tem ADR próprio. O ADR 0014 apenas a aplica ao `@plan-critic`. Este ADR também apenas a aplica ao `agent-root`.

## 5. Consequências

- Contagens de agents passam de 63 para 64 em catálogo, agentcards e READMEs.
- Os testes `.py` afetados seguem em lote separado, via `@python-router`, com plano `implementation` próprio, aplicados no mesmo commit do lote.
- Risco do kernel: se o host somar `copilot-instructions.md` ao corpo do agent selecionado, o raiz pode receber contexto duplicado. Mitigado pelo ponteiro puro.
- Dependência do roteiro de teste de host para confirmar o comportamento do dropdown.
- Orçamento M2: folga de 555 B mantida.

## 6. Reversão

1. `git revert` do commit do lote.
2. Remover o agent `agent-root` e o respectivo agentcard.
3. Marcar este ADR como Substituído.
4. Retornar à opção E+D do plano pai.
