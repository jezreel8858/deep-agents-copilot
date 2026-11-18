---
title: "Plano de Governança — Criação do agent @agent-root (B' endurecida; Router First R-037/R-062/R-063/R-068)"
status: COMPLETED
approved: true
completed_at: "2026-11-18"
post_exec_reviewer: "@agent-auditor"
post_exec_review_verdict: "PASS_WITH_WARNINGS"
post_exec_evidence_level: "[L]"
waiver_hitl: "2026-11-18 — ask_questions 'Registrar waiver e fechar'"
allowlist_waiver: "docs/guides/roteiro-teste-host-agent-root.md ratificado como entregável aceito sem alteração do roteiro"
author: "@agent-auditor"
plan_type: "governance"
tier: "governance"
created_at: "2026-11-18"
related-planning-doc: "N/A"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-20261118-agent-root-criacao"
session_id: "sess-20261118-agent-root-criacao"
review_rounds: 2
reviewer: "@plan-critic"
review_verdict: "ESCALATED_HITL_RESOLVIDO_POR_HUMANO"
review_tier1: "PASS"
review_resolution: "ESCALATED_HITL (teto R-065, rodada 2/2) resolvido por decisao humana via ask_questions (recibo r-9); plano segue ao Gate 4 com decisao humana, sem 3a rodada do critic (R-065); status DRAFT e approved false mantidos"
adr_sentinel_verdict: "CONFORME_COM_RESSALVAS"
plan_ref: "docs/plans/governance/20261118-100000-governance-maintenance-agent-root-viabilidade.md"
parent_plan_ref: "docs/plans/governance/20261118-100000-governance-maintenance-agent-root-viabilidade.md"
rollback_plan: "GUARD: nenhum arquivo de allowed_files e nenhum .py e commitado isoladamente; o commit so ocorre com o plano implementation dos .py aprovado e os .py no MESMO commit (sem isso, 6 testes governance_audit quebram: contagens 63 e Score 1 == 9). Pos-commit: git revert do commit do lote (reverte atomicamente allowed_files e .py). Pre-commit: git restore -- de cada arquivo de allowed_files e remover os novos .github/agents/agent-root.agent.md, .a2a/agentcards/agent-root.agentcard.json e docs/adr/0015-raiz-declarada-agent-root.md; reverter agentcards.index.json por git restore ou regenerar via tools/agentcard_exporter. ADR 0015, se ja Aceito: supersessao para Substituido. Sem aprovacao do Gate nenhum arquivo fora de docs/plans/ e alterado"
allowed_files_note: "allowed_files cobre so .md/.yaml/.json declarativos. Os testes .py (ver secao 6) ficam FORA e exigem plano de implementation proprio via @python-router (R-055 Q3), aprovado e aplicado no MESMO commit (pre-condicao bloqueante, secao 14). agentcards (agent-root.agentcard.json e agentcards.index.json) sao gerados por tools/agentcard_exporter (--apply), nunca editados a mao (limite do ADR 0012). Verificado: casos-roteamento.yaml e test_routing_accuracy_evals.py NAO contam nos (so exigem agent-router nos nos, >=10 arestas e extremidades validas) e por isso ficam fora. Rodada 2 (recibo r-9): lote inclui 4 .md de contagem (docs/README.md, guia de arquitetura, agency-score-matrix.md, agent-safety-guardrails/SKILL.md); o tipo do no agent-root e downstream (valor existente), sem tocar schema, model.py, graph_loader.py nem testes do runner; varredura de tools/headless-governance-runner/tests nao exige .py por causa do no (secao 6.1); sensor: python -m tools.governance_sync --check"
allowed_files:
  - ".github/agents/agent-root.agent.md"
  - ".github/agents/catalog.yaml"
  - ".github/agents/routing-graph.yaml"
  - ".github/agents/README.md"
  - ".a2a/agentcards/agent-root.agentcard.json"
  - ".a2a/agentcards/agentcards.index.json"
  - "README.md"
  - "docs/repo-map.md"
  - "tools/governance_sync/README.md"
  - ".github/copilot-instructions.md"
  - "CLAUDE.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - "docs/adr/0015-raiz-declarada-agent-root.md"
  - "docs/README.md"
  - "docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md"
  - ".github/skills/agent-safety-guardrails/references/agency-score-matrix.md"
  - ".github/skills/agent-safety-guardrails/SKILL.md"
---

# Criação do agent @agent-root

> Materializado por `@docs-engineer` (R-064) a partir do parecer de `@agent-auditor` (Etapa 1) e da pesquisa (Etapa 2). Plano em **DRAFT**: nenhuma alteração fora deste arquivo foi feita. Pytest NÃO foi executado por agentes.

## 1. Contexto e decisão

- Plano pai: [viabilidade do @agent-root](20261118-100000-governance-maintenance-agent-root-viabilidade.md) — **SUPERADO NESTE ESCOPO** pela decisão humana de criar o agent. A opção D (prompt de bootstrap) está **descartada** ("prompt de bootstrap: não faz nada"); a recomendação E+D do plano pai não prevalece.
- Plano irmão já aplicado: [R-068](20261117-160000-blindagem-aderencia-raiz-workflow.md).
- **Decisão humana (ask_questions, texto livre)**: "assumo o risco de que o agent selecionado no chat se torna o agent raiz do chat, crie o agent-root". Teste de host: roteiro elaborado para o usuário (Etapa 10).

## 2. Objetivo

Criar o agent selecionável `@agent-root` como identidade oficial do turno raiz, de modo que o agent selecionado no chat carregue Router First (R-063) e Raiz = Executor (R-068) sem depender da autoridade difusa do `copilot-instructions.md`.

## 3. Desenho do agent (B' endurecida)

Triagem, planejamento e execução de etapa = **zero**. Só invoca o `@agent-router` (R-063) e executa o pipeline emitido (R-068).

| Campo | Valor proposto |
|---|---|
| name | `agent-root` |
| description | "Identidade oficial do turno raiz: invoca @agent-router (R-063) e executa o pipeline emitido (R-068). Não classifica nem executa o trabalho das etapas." |
| model | Claude Sonnet 5.5 (igual ao router; R-054 zero discovery) |
| tools | `['ask_questions','run_subagent','context-mode/ctx_index','context-mode/ctx_search','context-mode/ctx_resume']` (formato espelhando `agent-router.agent.md:1-8`) |
| Fora das tools | `read_file`, `grep_search`, `file_search`, `list_dir`, `ctx_execute`, `ctx_batch` (sem elas não executa o trabalho das etapas) |
| Proibido | `infer` (retirado); omitir `tools` (daria acesso a tudo) |
| Agency Score | 1 (perfil Roteador / Supervisor sem escrita) — **confirmado** em `agency-score-matrix.md:12` (Score 1 = 9 agents hoje → 10 com agent-root; `agent-safety-guardrails/SKILL.md:260` repete a contagem) |

**Corpo (~1,5 KB)**: banner "Agente Ativo: agent-root"; ponteiro lazy para `copilot-instructions.md` § "Raiz = Executor de Workflow (R-068)" e `invariantes-e-protocolos.md` §4.1–4.3 (sem copiar o kernel); 1ª ação = `run_subagent` `@agent-router` com `correlation_context` exceto `router_bypass`; proibido executar o trabalho da etapa; re-triagem R-042 por turno.

**Catálogo**: `ROUTER_EXEMPT` NÃO existe; usar entrada normal com `related_agents: [agent-router]`, `priority` > 1, `domain: "Orquestracao agent-first (raiz)"`.

**Grafo**: nó `agent-root` com **`tipo: downstream`** (decisão humana, recibo r-9, após ESCALATED_HITL da rodada 2), sem arestas de entrada e nunca destino do router (evita ciclo). Justificativa verificada no repositório: (a) o enum de `tipo` de nó em `routing-graph.schema.json` tem 6 valores — entry_point, health_check, mandatory_pre_step, domain_router, downstream, fallback (os demais valores citados na v1 não pertencem a esse enum); (b) `TipoNo` em `model.py` e `graph_loader.py:136` (`TipoNo(item["tipo"])` → `GraphValidationError` em valor desconhecido) rejeitariam `root_declared`; (c) `entry_point` deve ser único (`graph_loader.py:145-150`: exatamente 1, hoje `agent-router`), o que inviabiliza o fallback `entry_point`; (d) `downstream` já existe: **sem tocar schema, `model.py`, `graph_loader.py` ou testes do runner (`tools/headless-governance-runner/**` fora de escopo)**; (e) nó `downstream` sem aresta de entrada é válido: a invariante 5 é de ciclo, não de cobertura (`graph_loader.py:310-321`; `test_graph_loader.py:144-147`). Varredura de testes: ver §6.1.

### 3.1 Decisão de desenho (Gate): ponteiro × mini-kernel

| Opção | Condição de aceite | Sensor correspondente | Risco/Trade-off |
|---|---|---|---|
| (i) Corpo só com ponteiro | Probe de host comprova que `copilot-instructions.md` e somado ao corpo do agent selecionado (agent-root cita R-068 e executa o loop sem o kernel no corpo) | `test_agent_root_contract.py`: corpo aponta para `copilot-instructions.md` § R-068 e `invariantes-e-protocolos.md` §4.1-4.3; sem copiar o kernel; <= 2 KB | Depende do host; SSOT preservado |
| (ii) Corpo com mini-kernel (<= ~1 KB) | Probe mostra que o host NAO soma o kernel, ou resultado inconclusivo apos 2 tentativas | Sensor de **equivalencia** ao kernel de `copilot-instructions.md:81` (secao "Raiz = Executor de Workflow (R-068)"): cada passo normativo do mini-kernel (alvo = 1a etapa, delegacao plana, sem trabalho de etapa no raiz) presente no kernel-fonte; divergencia = falha. Substitui o criterio "sem duplicar" | Duplicacao controlada; custo de teste de sincronia |

**RISCO CRITICO**: nao se sabe se o `copilot-instructions.md` continua somado ao corpo quando um custom agent esta selecionado. A escolha depende do **teste de host barato (probe)**. Proposta: executar o probe (Etapa 10 do roteiro, como pre-validacao) **ANTES do lote completo** (Etapas 6-9): 3 casos, apenas observar a 1a tool call e se o agent cita o kernel. Resultado do probe decide (i) × (ii); a decisao final cabe ao humano no Gate.
## 4. Exceção declarada (sem nova regra)

SSOT: nova seção curta **"Raiz declarada (@agent-root)"** em `invariantes-e-protocolos.md`:

> O agent selecionado no chat como @agent-root é o turno raiz e a identidade oficial dele; a autodenominação `agent-root` não viola R-062 e nenhum outro nome de especialista é permitido; o @agent-router continua o único classificador (R-037/R-063); o agent-root nunca classifica e sua 1ª ação é invocar o router.

- Ancoragens de 1 linha em `copilot-instructions.md` (:46 R-037, :49 R-063, :50 R-062) e `CLAUDE.md` (R-062 ~:81, R-063 ~:82).
- A exceção vale **só** para o nome literal no turno raiz; sem agent selecionado, R-062/R-063 seguem integrais.
- **Orçamento** (`test_root_instruction_file_budget.py:76-78`: `KERNEL_MAX_BYTES=2048`, `COPILOT_BASELINE_BYTES=17509`, `COPILOT_GROWTH_BUDGET_BYTES=2048`): teto M2 = 19.557 B; `copilot-instructions.md` mede **19.002 B** (bytes, `fs.statSync`) → **folga real 555 B** (nao 557). Estimativa das ancoragens: 3 linhas × ~120 B ≈ **360 B** (cabe, sobra ~195 B). M1 (kernel <= 2.048 B) nao e afetado (ancoragens ficam fora da secao do kernel). Reajuste de M2 so se o Gate escolher mini-kernel no copilot-instructions (nao previsto) ou se a medicao real exceder 555 B.

## 5. Mapa de impacto declarativo (allowed_files)

| Arquivo | Mudança |
|---|---|
| `.github/agents/agent-root.agent.md` | Novo |
| `.github/agents/catalog.yaml` | Nova entrada (63→64 totais; raiz 39→40) |
| `.github/agents/routing-graph.yaml` | Nó `agent-root` com `tipo: downstream` (§3) sem arestas de entrada; 39→40 nós |
| `.github/agents/README.md` | **Decisão cravada por grep**: sem contagens (63/64/39/40/31/32); tem tabela "2) Catálogo Atual" (linhas ~20-46, 40 linhas `| Agent |`, subconjunto) e "3) Roteamento Rápido"; a regra :122 exige atualizar README e catalog na mesma entrega → **+1 linha `agent-root`** na tabela do §2 (sem contagem). Permanece em allowed_files |
| `.a2a/agentcards/agent-root.agentcard.json` | Novo, gerado por `tools/agentcard_exporter` (--apply) |
| `.a2a/agentcards/agentcards.index.json` | Existe; **gerado** pelo agentcard_exporter (63→64), sem edição manual (ADR 0012) |
| `README.md` | Linhas confirmadas: 76 (63, 31 raiz, 32, 39), 214 (39/63), 257 (39/63), 383 (39/63), 403 (39/63 e sincronia), 407 (39 nós) → 64 / 32 raiz / 40; 32 stacks inalterado; **+ `agent-root` nos 2 primeiros blocos Mermaid** (hoje 0 ocorrências; exigido por `tests/operational_flow/test_operational_workflows.py:127-141` para todo nó `downstream`) |
| `docs/repo-map.md` | Linhas 29 e 73: 39→40; 63→64 |
| `tools/governance_sync/README.md` | Linhas 8 (63; 31→32 raiz; 32 stacks), 9 (39→40 entradas), 10 (39→40 nós) |
| `.github/copilot-instructions.md` | Âncora 1 linha em :46 (R-037), :49 (R-063), :50 (R-062) |
| `CLAUDE.md` | Âncora em R-062 (:81) e R-063 (:82) |
| `.github/agents/workflows/invariantes-e-protocolos.md` | Seção "Raiz declarada (@agent-root)" |
| `docs/adr/0015-raiz-declarada-agent-root.md` | Novo (ver §13); decisão do router: entra no lote |
| `docs/README.md` | Linha 65: "39 agents no catálogo raiz (63 totais)" → 40 / 64 (decisão r-9) |
| `docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md` | Linha 22 (63 totais / 39 raiz → 64 / 40; verificada), 57 (39 nós → 40), 59 (63 → 64; 39 raiz → 40) |
| `.github/skills/agent-safety-guardrails/references/agency-score-matrix.md` | Linha 12: Score 1 = 9 agents → 10, incluir `agent-root` na lista |
| `.github/skills/agent-safety-guardrails/SKILL.md` | Contagem real em :260 (Score 1 — 9 agents → 10); :35 verificado: sem contagem (só "Quando Usar") |

Fora de allowed_files (verificado, sem contagem de nós): `.github/agents/evals/casos-roteamento.yaml`, `tests/evals/test_routing_accuracy_evals.py`. Opcional (só se o executor comprovar necessidade): templates.

## 6. Trilha de testes (.py — plano próprio via @python-router, MESMO commit)

| Teste | Ajuste (asserção atual lida do disco) |
|---|---|
| `test_markdown_ssot_counts_and_mermaid_sync.py:38-42` | 63/31/32/39/39 → 64/32/32/40/40; revisar fixture :126 ("62 arquivos (30 na raiz…)") |
| `test_agent_headings_standardization.py:147` | `len(agents) == 63` → 64 |
| `test_otel_handoff_hydration_governance.py:34` | `== 63` → 64 |
| `test_r064_otel_correlation_fields.py:207` | `== 63` → 64 |
| `test_telemetry_emission_governance.py:82-83` | `total_scanned == 63` e mensagem → 64 |
| `test_agent_guardrails_regression.py:112` | `>= 63` → `>= 64`; `SCORE_1_AGENTS` (:40) inclui `agent-root` e a asserção `len(s1) == 9` (:120) → 10 (sem isto, órfão/contagem falham); `test_score_1_router_guardrails` (:153) revisar tools do agent-root |
| `test_root_instruction_file_budget.py` | M1/M2 sem reajuste previsto (folga 555 B ≥ ~360 B) |
| Sem mudança | `test_agent_count_per_stack_governance.py`, `test_a2a_agentcards_parity.py` (card gerado), `test_routing_accuracy_evals.py` |
| Sensor novo (possível) | `test_agent_root_contract.py`: tools exatas = 5; nó sem arestas de entrada; ≤ 2 KB; sensor conforme opção (i) ou (ii) de §3.1 |

### 6.1 Varredura dos testes do runner e do repositório (rodada 2, HIGH-2)

Leitura estática (grep/leitura em `tools/**/tests` e `tests/`); pytest NÃO executado por agentes.

| Teste | Resultado |
|---|---|
| `tools/headless-governance-runner/tests/routing_unit/test_graph_loader.py` | Fixture reduzida: `len(nos_por_id) == 7` (:48) e 6 arestas (:49), independentes do grafo real; grafo real: `>= 30` nós/arestas (:162-163) e `entry_points == 1` (:165) → não quebra (`downstream` não é `entry_point`); :144-147 confirma que nó `downstream` órfão não é erro |
| `test_TC07_graph_schema_validation.py`, `test_graph_consistency_cross_ref.py` | Fixtures inline (`entry_point`/`downstream`); sem contagem do grafo real → não quebram |
| `conftest.py:65` (`grafo_real`), `test_smoke_end_to_end.py`, `test_TC05`, `test_workflow_spec_gatilhos.py` | Carregam o grafo real sem contar nós → não afetados |
| `synth_unit/test_routing_graph.py:28-33`, `test_graph_seeding.py` | Snapshot usa só rotas `de == agent-router`; nó sem arestas de entrada não entra; contagens de seeds, não de nós |
| `model.py:43` (docstring "37 nós"), `test_graph_loader.py:151` ("~37 nós") | Comentários já defasados (grafo real tem 39), não asserções → sem quebra; sem edição (fora de escopo) |
| `tests/routing_gate/test_routing_quality_gate.py:64-65,68` | `>= 10` nós/arestas; todo nó exige `.agent.md` real (satisfeito pela criação do agent) |
| `tests/operational_flow/test_operational_workflows.py:127-141` | **Impacto .md (não .py)**: todo nó `downstream`/`fallback` deve constar nos 2 primeiros blocos Mermaid de `README.md` (hoje 0 ocorrências de `agent-root`) → tratado no §5 (README.md em allowed_files) |

**Resultado real**: nenhum teste do runner conta nós do grafo real, exige arestas de entrada ou tipo específico além de `entry_point` único; **nenhum impacto .py novo do runner** e nenhuma entrada nova na pré-condição do §14. A pré-condição dos 6 testes `governance_audit` do §14 permanece.

**UNKNOWN [FECHADO em E6 — 2026-11-18]**: efeito do nó `downstream` nas arestas curinga (`de: "*downstream"` em `routing-graph.yaml:1044,1473` e `para: "*downstream"` :1498) na compilação da tabela de transição/`rotear` do runner — fechado pelo parecer do `@agent-auditor` (`PASS_WITH_WARNINGS`, leitura `[L]`) e registro de E5a #2 (`user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')`).

Comandos para o **usuário** (agentes não executam pytest): `pytest tests/governance_audit -q --tb=short`; `pytest tests/evals -q`; `python -m tools.governance_sync --check`.

## 7. Critérios de sucesso (métrica verificável)

| Critério | Métrica verificável |
|---|---|
| Testes de governança verdes | `pytest tests/governance_audit -q --tb=short` → 0 falhas |
| Evals de roteamento sem regressão | `pytest tests/evals -q` → 0 falhas |
| Paridade de contagens/catálogo/agentcards | `python -m tools.governance_sync --check` → exit 0 |
| 1ª tool call = `run_subagent` `@agent-router` | Roteiro de host (Etapa 10): 3/3 casos |
| 0 violações de R-062 | Roteiro de host: 0 nomes de especialista assumidos nos 3 casos |
| 5/5 tools, nenhuma a mais | `test_agent_root_contract.py` (ou leitura do frontmatter): lista exata = 5 |
| Kernel R-068 acessível | Probe de host: agent cita/executa o loop; define opção (i) ou (ii) |

## 8. Riscos residuais e condição de reabertura

- Fatos da pesquisa: custom agents GA no JetBrains desde 2026-03-11; corpo ≤ 30.000 caracteres; formato `servidor/tool` compatível; `infer` retirado; user-invocable default true.
- **UNKNOWN [FECHADO em E6 — 2026-11-18]**: handoffs/target/model por IDE no JetBrains, subagent a partir de agent selecionado e soma do `copilot-instructions.md` ao corpo do agent — fechado pelo parecer do `@agent-auditor` (`PASS_WITH_WARNINGS`, leitura `[L]`) e pelo registro de P0–P2 e C1–C3 (`user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')`; C4–C12 opcionais, não bloqueantes).
- **Reabertura**: se o teste de host falhar 2x, ou dropdown/tools/kernel falharem → reverter via `git revert` do lote e voltar à opção E+D do plano pai.

## 9. Vínculo com o teste de host

A Etapa 10 (roteiro de teste de host para o usuário) é **entregável separado**, `docs_only`.

## 10. Decisões do Gate (R-027, Etapa 5) — perguntas `ask_questions`

| # | header (≤ 25) | Pergunta | Opções (mutuamente exclusivas; 1ª recomendada) |
|---|---|---|---|
| a | `Aprovar plano` | Aprovar este plano (rodada 2 do @plan-critic = ESCALATED_HITL, resolvida por decisão humana r-9) para a Etapa 6? | **(Recomendado) Aprovar**: libera `@governance-factory`; exige `.py` no mesmo commit (§14). / **Aprovar com ajustes**: volta ao autor, +1 rodada. / **Rejeitar**: mantém E+D do plano pai. |
| b | `Ponteiro x mini-kernel` | Qual desenho do corpo do agent-root? | **(Recomendado) Ponteiro, condicionado ao probe**: SSOT limpo, depende do host somar o kernel; vira mini-kernel se o probe falhar. / **Mini-kernel (<= ~1 KB)**: resiliente, custo de sensor de equivalência. |
| c | `ADR 0015 no lote` | Confirmar o ADR 0015 no lote (já decidido pelo router)? | **(Recomendado) Confirmar**: registra a exceção e a decisão; +1 arquivo. / **Remover do lote**: exceção só em invariantes; menos rastreabilidade. |
| d | `Orçamento M2` | Ajustar `COPILOT_BASELINE_BYTES`/teto M2? | **(Recomendado) Manter**: folga 555 B ≥ ~360 B; sem mexer em teste. / **Ajustar teto**: cobre mini-kernel/ancoragens maiores; afrouxa o guard de crescimento. |

Item "ID/regra": sem nova regra, só exceção declarada (R-066 e regras-fonte como ressalva do sentinel, §13).

## 11. Fluxo restante

4 `@plan-critic` rodada 2 (teto 2) → 5 Gate humano → **probe de host (pré-validação, Etapa 10 antecipada)** → 6 `@governance-factory` → 7 `@governance-maintainer` → 8 `@python-router` (testes .py, mesmo commit) → 9 `@agent-auditor` → 10 roteiro completo de host.

## 12. Parecer da rodada 1 (@plan-critic + @adr-sentinel)

- `@plan-critic` rodada 1: **NEEDS_REVISION**, Tier 1 **FAIL** (BLOCKER T1-8: `session_id` ausente — corrigido: `sess-20261118-agent-root-criacao`, padrão `^[a-z0-9][a-z0-9-]{7,95}$`). Achados HIGH/MEDIUM/LOW tratados nesta revisão: citação do ADR 0014, pré-condição dos `.py`, mini-kernel × ponteiro, bytes, perguntas R-027, `tipo` do nó. Rodada 2: ver §15.
- `@adr-sentinel`: **CONFORME_COM_RESSALVAS**; ADRs 0011–0013 sem conflito; limite do ADR 0012: usar `governance_sync`/`agentcard_exporter`, sem edição manual de artefatos gerados; R-066 e regras-fonte permanecem como **ressalva do sentinel** (não tratadas neste plano).
- Correção de citação: **ADR 0014 = Quality Gate Universal de Revisão Cética Pré-HITL (R-064) via @plan-critic** (status Aceito); topologia plana = R-047/R-054, **sem ADR próprio**; o 0014 só a aplica ao plan-critic (item 7: retorno ao router).

## 13. Especificação do ADR 0015 (`docs/adr/0015-raiz-declarada-agent-root.md`, novo)

Convenção real (lida em 0013/0014): arquivo `NNNN-slug-kebab.md`; front-matter `id: ADR-0015`, `title`, `status` (Proposto → Aceito após o Gate), `date`, `decision-makers`, `consulted`, `informed`, `type: architectural-decision`, `diataxis: explanation`. Seções numeradas:

1. **Contexto**: R-062/R-063/R-068 e a decisão humana de criar o agent-root.
2. **Drivers**: Router First sem autoridade difusa; zero impersonation; orçamento do kernel.
3. **Alternativas**: A (status quo); B' endurecida (**escolhida**); D prompt de bootstrap (descartada); E+D do plano pai (superada); status quo; sub-decisão ponteiro × mini-kernel.
4. **Decisão**: agent selecionado = turno raiz; nome literal `agent-root` só no turno raiz; `@agent-router` único classificador; 5 tools; nó sem arestas de entrada; registrar que a topologia plana (R-047/R-054) **não tem ADR próprio**.
5. **Consequências**: contagens 63→64; testes `.py` em lote via `@python-router`; risco do kernel; dependência do teste de host.
6. **Reversão**: `git revert`; remover agent/agentcard; supersessão para Substituído.

## 14. Pré-condição bloqueante (testes .py)

O commit do lote **só ocorre** com o plano `implementation` dos `.py` (via `@python-router`, R-055 Q3) **aprovado** e os `.py` aplicados **no MESMO commit**. Asserções cravadas que quebram sem isso: `test_markdown_ssot_counts_and_mermaid_sync.py:38-42`; `test_agent_headings_standardization.py:147`; `test_otel_handoff_hydration_governance.py:34`; `test_r064_otel_correlation_fields.py:207`; `test_telemetry_emission_governance.py:82`; `test_agent_guardrails_regression.py:112` (e `len(s1) == 9` em :120). Guard repetido no `rollback_plan`. A varredura da rodada 2 (§6.1) não acrescentou nenhum teste `.py` do runner a esta pré-condição.

## 15. Parecer da rodada 2 e resolução humana (R-065)

- `@plan-critic` rodada 2/2: **ESCALATED_HITL** (teto R-065 atingido; 2 HIGH técnicos). Tier 1: **PASS**.

| # | Severidade | Achado | Resolução (decisão humana, recibo r-9) |
|---|---|---|---|
| 1 | HIGH | `tipo` do nó (`root_declared`/fallback `entry_point`) inviável: enum do schema, `TipoNo`, `graph_loader.py:136` e unicidade de `entry_point` | `tipo: downstream` (§3); sem tocar schema/model.py/runner |
| 2 | HIGH | Testes do runner (`tools/**/tests`) não varridos | Varrido (§6.1): nenhum quebra; 1 UNKNOWN sobre curingas declarado |
| 3 | MEDIUM | Contagens em `docs/README.md` e guia de arquitetura | Incluídos em allowed_files e §5 (:65; :22,:57,:59) |
| 4 | MEDIUM | `agency-score-matrix.md` (Score 1 = 9) | Incluído (:12) + `SKILL.md:260` (a contagem não está em :35) |
| 5 | LOW | `.github/agents/README.md` "a confirmar" | Decisão cravada por grep (§5): +1 linha `agent-root`; contagens ausentes |

- **Resolução**: o humano decidiu via `ask_questions` (recibo r-9): (1) tipo `downstream`; (2) incluir no lote `docs/README.md`, o guia de arquitetura e `agency-score-matrix.md`.
- **Próximo passo**: o plano segue ao **Gate 4** com decisão humana registrada; **sem 3ª rodada do critic** (R-065). Status permanece `DRAFT` / `approved: false` até o Gate.
- **Sensor**: `python -m tools.governance_sync --check` (**VERIFICADO** em 2026-11-18, drift 0); paridade dos 4 docs de contagem **FECHADA** em E6 por leitura `[L]` no parecer do `@agent-auditor` (`PASS_WITH_WARNINGS`).

## Decisão do Gate 4

- Data: 2026-11-18 (recibos ask_questions r-9 e r-11)
- Aprovação: aprovar o plano como está.
- Arquitetura: ponteiro puro (sem mini-kernel).
- ADR 0015: incluído no escopo.
- Orçamento M2: mantido (teto +2.048 B).

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

### Encerramento (E6 — CONCLUÍDO)

- [x] **E6 (encerramento) CONCLUÍDO em 2026-11-18:** (i) E5a #3–#6 e agentcards VERIFICADOS (drift 0); E5a #1–#2 encerrados sob WAIVER HITL; (ii) probe de host P0–P2 e C1–C3 registrados sob WAIVER HITL (`ask_questions 'Registrar waiver e fechar'`), C4–C12 classificados como opcionais e não bloqueantes; (iii) veredito do `@agent-auditor` (E5b) registrado como `PASS_WITH_WARNINGS` (leitura `[L]`); roteiro `docs/guides/roteiro-teste-host-agent-root.md` ratificado como entregável aceito (waiver de allowlist); ADR-0015 promovido de `Proposto` para `Aceito`.
