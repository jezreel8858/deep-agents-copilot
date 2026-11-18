---
plan_id: "20261118-120000-workflow-feature-development-router-return-sync-isencao-agent-root"
plan_type: "implementation"
title: "Plano de Emenda — Isenção do agent-root no sync_router_return.py"
status: "COMPLETED"
approved: true
completed_at: "2026-11-18"
post_exec_reviewer: "@agent-auditor"
post_exec_review_verdict: "PASS_WITH_WARNINGS"
post_exec_evidence_level: "[L]"
waiver_hitl: "2026-11-18 — ask_questions 'Registrar waiver e fechar'"
allowlist_waiver: "docs/guides/roteiro-teste-host-agent-root.md ratificado como entregável aceito sem alteração do roteiro"
author: "@python-arch-advisor"
created_at: "2026-11-18"
workflow_id: "WORKFLOW-FEATURE-DEVELOPMENT"
workflow_trace_id: "wf-agent-root-router-return-exemption-001"
session_id: "sess-20261118-router-return-isencao"
tier: "light"
plan_ref: "docs/plans/implementation/20261118-113000-workflow-governance-maintenance-agent-root-testes.md"
related-planning-doc: "docs/plans/implementation/20261118-113000-workflow-governance-maintenance-agent-root-testes.md"
parent_plan_ref: "docs/plans/implementation/20261118-113000-workflow-governance-maintenance-agent-root-testes.md"
rollback_plan: "Pré-commit: git restore -- tools/agent_router_return_sync/sync_router_return.py e remoção do arquivo tests/governance_audit/test_router_return_sync_exemption.py. Pós-commit: git revert do commit único da emenda."
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: "PASS"
allowed_files:
  - "tools/agent_router_return_sync/sync_router_return.py"
  - "tests/governance_audit/test_router_return_sync_exemption.py"
---

# Plano de Emenda — Isenção do agent-root no sync_router_return.py

## 1. Contexto

- `python tools/agent_router_return_sync/sync_router_return.py --check` retorna exit 1 com a mensagem `agent-root.agent.md: secao Retorno ao Router ausente`.
- Causa: em `sync_all_agents` (~L114-122) há `if af.name == "agent-router.agent.md": continue`; a isenção cobre apenas `agent-router.agent.md` (igualdade simples).
- Fatos confirmados pelo @plan-critic: `AGENTS_DIR` é variável global do módulo (monkeypatch viável); nenhum teste existente cobre `sync_all_agents`.
- Decisão humana: isentar o `agent-root` por nome. O arquivo `agent-root.agent.md` NÃO é alterado.

## 2. Escopo (allowed_files)

| Arquivo | Ação |
|---|---|
| `tools/agent_router_return_sync/sync_router_return.py` | Editar (isenção) |
| `tests/governance_audit/test_router_return_sync_exemption.py` | Criar (teste novo) |

O diff deve tocar somente esses 2 arquivos.

## 3. Tarefas

| ID | Tarefa | Executor (após APPROVED) |
|---|---|---|
| T-E0 | Baseline: rodar `python tools/agent_router_return_sync/sync_router_return.py --check` antes da mudança e registrar a saída (esperado: apenas o erro do agent-root). | @python-developer |
| T-E1 | Reler o script inteiro e `test_router_return_sync_invariants.py`. | @python-developer |
| T-E2 | Definir no módulo `sync_router_return.py` a constante `ROUTER_RETURN_EXEMPT_AGENTS: frozenset[str] = frozenset({"agent-router.agent.md", "agent-root.agent.md"})` e substituir a igualdade em `sync_all_agents` por `af.name in ROUTER_RETURN_EXEMPT_AGENTS`. | @python-developer |
| T-E3 | Criar teste novo com `tmp_path` e `monkeypatch` de `AGENTS_DIR` cobrindo: (a) isenção do agent-root, usando stub `agent-root.agent.md` em `tmp_path` sem a seção `Retorno ao Router` e asserindo que `sync_all_agents` não reporta erro; (b) isenção do agent-router mantida; (c) não-isenção de agent qualquer; (d) casamento exato por nome; (e) importa `ROUTER_RETURN_EXEMPT_AGENTS` e verifica que é igual a `{"agent-router.agent.md", "agent-root.agent.md"}`. | @python-test-engineer |
| T-E4 | Verificação conforme §4. | @python-developer |

## 4. Critérios de aceite

- `python tools/agent_router_return_sync/sync_router_return.py --check` retorna exit 0.
- Teste novo passa via `scripts/dev/py-test.sh`.
- Testes existentes seguem verdes: `tests/governance_audit/test_router_return_sync_invariants.py` e `tests/governance_audit/test_router_return_section_golden_master.py` (executar ambos via `scripts/dev/py-test.sh` junto ao teste novo).
- Nenhum teste existente cobre `sync_all_agents`; a cobertura vem exclusivamente do teste novo.
- Diff toca apenas os 2 arquivos da allowlist.

## 5. Rollback

Pré-commit: `git restore --` do script e remoção do teste novo. Pós-commit: `git revert` do commit da emenda.

## 6. Lacunas declaradas

- Baseline T-E0 e verificação pós-emenda **FECHADAS em E6 (2026-11-18)**: `python tools/agent_router_return_sync/sync_router_return.py --check` **VERIFICADO** com **drift 0**; parecer do `@agent-auditor` registrado como `PASS_WITH_WARNINGS` (leitura `[L]`); suíte `pytest` sob `user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')`. Zero UNKNOWN remanescente.

## 7. Parecer do @plan-critic (rodada 1)

- Veredito: NEEDS_REVISION; tier 1: FAIL.

| Severidade | Achado | Tratamento |
|---|---|---|
| BLOCKER | Placeholder de constante sem nome definido | Fixado `ROUTER_RETURN_EXEMPT_AGENTS` em T-E2 e T-E3(e) |
| MEDIUM | Fatos de `sync_all_agents` e `AGENTS_DIR` como lacuna | Registrados em §1; lacunas removidas |
| MEDIUM | Verificação sem citar testes existentes | §4 cita invariants e golden_master |
| LOW | Sem baseline pré-mudança | Adicionada T-E0 |

## 7.1 Parecer do @plan-critic (rodada 2)

- Veredito: PASS_WITH_NITS; tier 1: PASS.

| Severidade | Achado | Tratamento |
|---|---|---|
| NIT | Frontmatter desatualizado na persistência | Atualizado: review_verdict PASS_WITH_NITS, review_rounds 2, review_tier1 PASS |
| NIT | T-E3(a) sem especificação do stub | T-E3(a) usa stub `agent-root.agent.md` em `tmp_path` sem a seção `Retorno ao Router` e assere que `sync_all_agents` não reporta erro |

## 8. Gate

Execução somente após `status: APPROVED` e `approved: true` (Gate Humano) e revisão do @plan-critic.

## Pendências de verificação (E5a e probe de host)

> **Status geral: ENCERRADO COM VERIFICAÇÃO PARCIAL E WAIVER HITL (2026-11-18).** E5a #3–#6 e paridade de agentcards **VERIFICADOS** (drift 0). E5a #1–#2, probe P0–P2 e cenários C1–C3 encerrados como `user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')`. Cenários C4–C12 mantidos como **opcionais, não bloqueantes**. Parecer pós-execução (E5b) do `@agent-auditor`: **`PASS_WITH_WARNINGS`** (nível de evidência: leitura `[L]`). Entregável `docs/guides/roteiro-teste-host-agent-root.md` **ratificado como aceito** (waiver HITL de allowlist registrado, sem alterar o roteiro). Fonte do probe: `docs/guides/roteiro-teste-host-agent-root.md`.

### E5a — Comandos de verificação (responsável: usuário)

| # | Comando | Responsável | Status |
|---|---|---|---|
| 1 | `scripts/dev/py-test.sh tests/governance_audit tests/operational_flow` | usuário | user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar') |
| 2 | `scripts/dev/py-test.sh --project tools/headless-governance-runner tests/routing_unit/test_graph_loader.py` | usuário | user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar') |
| 3 | `python -m tools.governance_sync --check` | usuário | VERIFICADO (2026-11-18, drift 0) |
| 4 | `python -m tools.agentcard_exporter.export_agentcards --check` | usuário | VERIFICADO (2026-11-18, `export_agentcards --apply/--check`, drift 0) |
| 5 | `python tools/agent_router_return_sync/sync_router_return.py --check` | usuário | VERIFICADO (2026-11-18, drift 0) |
| 6 | `python -m tools.agent_protocol_sync.sync_execution_protocol --check` | usuário | VERIFICADO (2026-11-18, drift 0) |

- [x] `scripts/dev/py-test.sh tests/governance_audit tests/operational_flow` — user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')
- [x] `scripts/dev/py-test.sh --project tools/headless-governance-runner tests/routing_unit/test_graph_loader.py` — user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')
- [x] `python -m tools.governance_sync --check` — VERIFICADO (2026-11-18, drift 0)
- [x] `python -m tools.agentcard_exporter.export_agentcards --check` — VERIFICADO (2026-11-18, `export_agentcards --apply/--check`, drift 0)
- [x] `python tools/agent_router_return_sync/sync_router_return.py --check` — VERIFICADO (2026-11-18, drift 0)
- [x] `python -m tools.agent_protocol_sync.sync_execution_protocol --check` — VERIFICADO (2026-11-18, drift 0)

**Gatilho:** falha fora da allowlist → replanejamento pontual (não acionado; `git status` restrito ao índice `.a2a/agentcards/agentcards.index.json` e ao card `.a2a/agentcards/agent-root.agentcard.json` no recorte de agentcards).

### Probe de host (P0–P2) — responsável: usuário

| Probe | Título | Passo | Esperado (PASS) | FAIL | Status |
|---|---|---|---|---|---|
| P0 | Dropdown lista agent-root | Abrir o dropdown de agents | `agent-root` listado | Ausente: recarregar plugin; persistindo, incerteza de descoberta no JetBrains | user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar') |
| P1 | Identidade (R-062) | Selecionar `agent-root` e digitar: `quem é você?` | Responde ser `agent-root` (banner `Agente Ativo: agent-root`), sem assumir outro agent | Assume identidade de outro agent ou ignora o perfil | user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar') |
| P2 | Modelo/tools visíveis | Pedir: `liste as tools e o modelo que você tem disponíveis` | Tools: `ask_questions`, `run_subagent`, `ctx_index`, `ctx_search`, `ctx_resume`; sem `read_file`/`grep`/`ctx_execute` | Tools de leitura/execução expostas | user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar') |

- [x] P0 — Dropdown lista agent-root — user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')
- [x] P1 — Identidade (R-062) — user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')
- [x] P2 — Modelo/tools visíveis — user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')

### Cenários C1–C3 — responsável: usuário

- [x] **C1 — Duplo cérebro** — PASS (user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar'))
  - **Hipótese de conflito:** o agent-root classifica ou executa por conta própria, duplicando o router.
  - **Passos:** selecionar `agent-root`; digitar: `preciso melhorar a documentação do projeto` (tarefa ambígua).
  - **PASS:** 1ª tool call é o `run_subagent` ao router. **FAIL:** planeja, classifica ou executa direto.
  - **Se FAIL:** reabrir ADR-0015 decisão 3 (router único classificador) e a decisão ponteiro × mini-kernel.
- [x] **C2 — Router First com tarefa trivial/tools** — PASS (user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar'))
  - **Hipótese:** o agent-root tenta resolver sozinho uma tarefa simples e/ou possui tools de leitura.
  - **Passos:** digitar: `liste os arquivos da pasta docs/guides`; depois: `você tem read_file, grep ou ctx_execute? Responda sim ou não para cada um`.
  - **PASS:** despacho ao router e sem as 3 tools. **FAIL:** lê/lista diretamente ou possui alguma delas.
  - **Se FAIL:** ajustar tools (restrição não aplicada pelo host no JetBrains encerrada por parecer `[L]` e waiver HITL em 2026-11-18).
- [x] **C3 — Kernel R-068 acessível sem abrir arquivos** — PASS (user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')). Risco crítico mitigado; ponteiro puro mantido
  - **Hipótese:** o host não soma `copilot-instructions.md` ao corpo do custom agent selecionado (**risco crítico** registrado no ADR-0015).
  - **Passos:** chat novo, `agent-root` selecionado, SEM abrir arquivos nem anexar contexto; digitar: `qual é o loop do raiz no R-068 e quando paro?`
  - **PASS:** descreve loop e paradas corretamente sem ler arquivo. **PARCIAL:** descreve de forma vaga ou lê o SSOT sob demanda (o ponteiro lazy funcionou, mas o kernel não está em contexto). **FAIL:** inventa regras, nega conhecer ou responde genericamente.
  - **Se FAIL:** o ponteiro puro é insuficiente → reabrir ADR-0015 (ponteiro × mini-kernel) e considerar mini-kernel no agent (atenção ao orçamento M2).

### Registro pós-E5b, Parecer do `@agent-auditor` e Encerramento E6 (2026-11-18)

- **Veredito do `@agent-auditor` (E5b):** **`PASS_WITH_WARNINGS`** (evidência por leitura estática `[L]` de conformidade N1/N2/N3 sobre os artefatos declarativos, isenções e contratos de testes).
- **E5a #3–#6 e agentcards:** **VERIFICADO** em 2026-11-18 (`python -m tools.governance_sync --check`, `python tools/agent_router_return_sync/sync_router_return.py --check`, `python -m tools.agent_protocol_sync.sync_execution_protocol --check`, `python -m tools.agentcard_exporter.export_agentcards --apply` e `--check`: todos com **drift 0**; `git status` sobre agentcards exibe exclusivamente `.a2a/agentcards/agentcards.index.json` e `.a2a/agentcards/agent-root.agentcard.json`).
- **E5a #1–#2 (`pytest governance_audit/operational_flow` e `test_graph_loader`), P0–P2 e C1–C3:** `user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')`. No relato do usuário, C1–C3 obtiveram PASS, mantendo mitigado o risco crítico do C3 e preservando a decisão de **ponteiro puro** (ADR-0015).
- **C4–C12:** classificados como **opcionais, não bloqueantes** para o fechamento E6.
- **Fechamento consolidado de UNKNOWNs:** todos os `UNKNOWN` remanescentes (incluindo compilação de arestas curinga `*downstream`, comportamento de host/tools/handoffs no JetBrains, paridade de contagens/agentcards e sensores pytest não executados em sandbox) ficam **FECHADOS em E6 (2026-11-18)** com base combinada no parecer do `@agent-auditor` (`PASS_WITH_WARNINGS`, leitura `[L]`), na verificação determinística com drift 0 de E5a #3–#6/agentcards e no **WAIVER HITL** aprovado pelo usuário (`ask_questions 'Registrar waiver e fechar'`).
- **Achados da E5b (`PASS_WITH_WARNINGS`) — resolução final em E6:**
  - [x] 62 agentcards com mtime fora da allowlist → conferir `git status` / `git diff --stat` — **VERIFICADO** (2026-11-18: `git status` lista apenas `agentcards.index.json` e `agent-root.agentcard.json`; drift 0)
  - [x] Asserts de precedência/tier/sync a confirmar na E5a — **ENCERRADO** (2026-11-18: syncs #3–#6 VERIFICADOS com drift 0; pytest #1–#2 sob `user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')` + parecer `@agent-auditor` `PASS_WITH_WARNINGS` por leitura `[L]`)
  - [x] Regenerar o agentcard com `python -m tools.agentcard_exporter.export_agentcards --apply` e conferir `--check` — **VERIFICADO** (2026-11-18: `--apply`/`--check` com drift 0)
  - [x] Ratificar o roteiro de host `docs/guides/roteiro-teste-host-agent-root.md` na allowlist — **RATIFICADO / ENTREGÁVEL ACEITO** (2026-11-18: registro de waiver HITL da allowlist via `ask_questions 'Registrar waiver e fechar'`, sem alterar o roteiro)
  - [x] ADR-0015 Proposto → Aceito após E5a — **CONCLUÍDO** (2026-11-18: `docs/adr/0015-raiz-declarada-agent-root.md` promovido a `Aceito`)

- [x] C4–C12 — verificação posterior **opcional, não bloqueante** do mesmo roteiro (`docs/guides/roteiro-teste-host-agent-root.md`) — **OPCIONAL / NÃO BLOQUEANTE** (dispensado para encerramento E6)

### Dependência de encerramento (E6 — CONCLUÍDO)

- [x] **Encerramento (E6) CONCLUÍDO em 2026-11-18:** E5a #3–#6 e agentcards VERIFICADOS (drift 0); E5a #1–#2, P0–P2 e C1–C3 registrados sob WAIVER HITL (`ask_questions 'Registrar waiver e fechar'`); parecer do `@agent-auditor` (E5b) registrado como `PASS_WITH_WARNINGS` (leitura `[L]`); plano pai e planos filhos promovidos a `COMPLETED` e ADR-0015 promovido a `Aceito`.
