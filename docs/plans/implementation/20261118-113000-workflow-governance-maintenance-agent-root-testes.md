---
plan_id: "20261118-113000-workflow-governance-maintenance-agent-root-testes"
plan_type: "implementation"
title: "Plano de Implementação — Sensores e Contagens de Teste do agent-root (ADR-0015)"
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
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
tier: "full"
review_rounds: 3
reviewer: "@plan-critic"
review_verdict: "ESCALATED_HITL_RESOLVIDO_POR_HUMANO"
review_tier1: "PASS"
review_resolution: "ESCALATED_HITL da rodada 3/3 (H-1 HIGH, M-1 MEDIUM, L-1 LOW, N-1 NIT) resolvido por decisão humana via ask_questions, recibo r-26: H-1 = 'Editar o teste' (T-10; allowlist +1 .py); M-1 = 'Verificar depois' (§4, verificação do usuário); L-1 corrigido em T-00/§1.3/§3; plano permanece DRAFT e approved: false até o Gate E5.4 (§9)"
plan_ref: "docs/plans/governance/20261118-110000-governance-maintenance-agent-root-criacao.md"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-20261118-agent-root-criacao"
session_id: "sess-20261118-agent-root-criacao"
related-planning-doc: "docs/plans/governance/20261118-110000-governance-maintenance-agent-root-criacao.md"
parent_plan_ref: "docs/plans/governance/20261118-110000-governance-maintenance-agent-root-criacao.md"
parent_plan_addendum: "T-00 — ajuste do corpo do agent-root (md) sob o plano pai governance APPROVED"
rollback_plan: "Pós-commit: git revert do commit único do lote (reverte atomicamente T-00, artefatos de governança e .py). Pré-commit: git restore -- do .github/agents/agent-root.agent.md para o corpo anterior (T-00), dos 9 .py editados em tests/governance_audit (6 de contagem + test_context_mode_precedence_governance.py + test_template_sections.py + test_router_return_section_golden_master.py), do test_graph_loader.py do runner (se D-2 aprovada) e remoção do novo sensor tests/governance_audit/test_agent_root_contract.py."
allowed_files:
  - "tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py"
  - "tests/governance_audit/test_agent_headings_standardization.py"
  - "tests/governance_audit/test_otel_handoff_hydration_governance.py"
  - "tests/governance_audit/test_r064_otel_correlation_fields.py"
  - "tests/governance_audit/test_telemetry_emission_governance.py"
  - "tests/governance_audit/test_agent_guardrails_regression.py"
  - "tests/governance_audit/test_context_mode_precedence_governance.py"
  - "tests/governance_audit/test_template_sections.py"
  - "tests/governance_audit/test_router_return_section_golden_master.py"
  - "tests/governance_audit/test_agent_root_contract.py"
  - "tools/headless-governance-runner/tests/routing_unit/test_graph_loader.py"
---

# Plano de Implementação — Sensores e Contagens de Teste do agent-root (ADR-0015)

## 1. Contexto

Etapa E5.3b do `WORKFLOW-GOVERNANCE-MAINTENANCE` (trace `wf-20261118-agent-root-criacao`). Cobre os `.py` (pré-condição bloqueante §14 do plano pai: commit único com estes `.py` e os artefatos de governança) e o ajuste T-00 do corpo de `agent-root.agent.md` (adendo ao plano pai, §1.4). Revisão 2: parecer @plan-critic rodada 2 (N-1 HIGH, N-2 MEDIUM, N-3 LOW) e revisão do @python-arch-advisor. Revisão 3: parecer da rodada 3/3 (ESCALATED_HITL) e resolução humana r-26 (§8); T-10 adicionada (§2.1.3).

### 1.1 Estado verificado em disco

| Item | Valor | Evidência |
| :--- | :--- | :--- |
| `.github/agents/agent-root.agent.md` | 1.557 B; `tools` com 5 entradas (`ask_questions`, `run_subagent`, `context-mode/ctx_index`, `context-mode/ctx_search`, `context-mode/ctx_resume`) | leitura |
| Nó no `routing-graph.yaml` | `id: agent-root`, `tipo: downstream` (linha 16–17) | leitura |
| Nós em `nos:` | 40 (confere com 40) | contagem de `  - id:` entre `nos:` e `convencao_papeis_genericos:` |
| `.github/copilot-instructions.md` | 19.284 B; teto M2 19.557 B; folga 273 B | tamanho em disco + valores do plano pai |
| ADR | `docs/adr/0015-raiz-declarada-agent-root.md` existe | listagem |
| Exceção em invariantes | `### Raiz declarada (@agent-root — R-037 / R-062 / R-063 / ADR-0015)` (linha 529) em `.github/agents/workflows/invariantes-e-protocolos.md` | leitura |
| README | `agent-root` aparece nos 2 diagramas Mermaid (linhas 207 e 300) | leitura |
| Corpo do agent-root (após frontmatter) | 1015 B; abre com `# Perfil Operacional` (único H1); H2 existentes: `CRÍTICO: ESCOPO E LIMITES` e `Quando Delegar`; sem `CLAUSE_CONTEXT_HYDRATION`, sem `R-060` | leitura + medição em memória |

### 1.2 Arestas curinga (verificadas)

| Linha | Aresta | Implicação |
| :--- | :--- | :--- |
| 1048 | `de: "*downstream"` → `codegraph-engine` | agent-root é origem, não destino |
| 1477 | `de: "*downstream"` → `agent-router` | agent-root é origem, não destino |
| 1502 | `de: agent-router` → `para: "*downstream"` | curinga de destino: semanticamente pode cobrir agent-root; congelar em `KNOWN_WILDCARD_EDGES` (decisão D-1) |

Arquivo: `.github/agents/routing-graph.yaml`. Chave de arestas: `arestas:` (linha 776), campos `de`/`para`. As linhas acima são referência de leitura; o sensor congela as arestas curinga em `KNOWN_WILDCARD_EDGES` por pares `(de, para)`, nunca por número de linha.

O loader do runner (`tools/headless-governance-runner/src/governance_runner/routing/graph_loader.py`, ~l.319, RG-04) ignora `*downstream` na adjacência concreta. Logo a aresta curinga `agent-router → *downstream` (~l.1502) NÃO é verificável semanticamente por esse loader: só pode ser congelada, não validada quanto a cobrir ou não `agent-root`.

### 1.3 Enquadramento do agent-root perante os testes de context-mode

- `ROUTER_EXEMPT` NÃO existe em código `.py`; é apenas prosa de `copilot-instructions.md`.
- O código reconhece exceção somente por NOME em `tests/governance_audit/test_context_mode_precedence_governance.py`. Os 5 filtros de não-roteadores (linhas 397, 441, 486, 710, 746) têm a forma real `if not p.name.endswith("-router.agent.md") and p.name != "agent-router.agent.md" and p.name != "prompt-structuring.agent.md"` (verificado por leitura). Sem ajuste, `agent-root` (tools sem `ctx_batch`/`ctx_execute`) falharia nesses 5 testes.
- **Decisão (a) ampliada**: `agent-root` = "raiz declarada" (ADR-0015). (i) Exceção por NOME apenas onde o agent não pode cumprir a regra sem ferramentas de fan-out (T-08, context-mode); (ii) o CORPO do agent passa a cumprir as invariantes universais (CLAUSE_CONTEXT_HYDRATION, R-060, H1/H2 canônicos) via T-00; (iii) a única isenção adicional em teste é `retorno_router` (T9), análoga à do `agent-router`.
- **Alternativa (b) REJEITADA** (exceções por nome nos testes de OTel ×2, headings e seções em vez de T-00): enfraquece invariantes universais (CLAUSE_CONTEXT_HYDRATION em 100% dos agents, :38/:211) com lista de exceção a manter em 4+ testes; a leitura mostra que o H1 já passa e que `test_turn_budget…` (R-060) exigiria mais uma exceção, logo a lista só cresceria. T-00 custa ≈ 847 B de corpo, dentro do teto de 2.048 B. Mantém-se REJEITADA também a variante "dar `ctx_batch`/`ctx_execute` ao agent" (reabre as 5 tools exatas do plano pai).
- `GATHER_ONLY_AGENTS` NÃO muda: `tests/governance_audit/test_ctx_execute_capability_profile.py:126` tem `assert len(GATHER_ONLY_AGENTS) == 24`; incluir `agent-root` quebraria o assert e exigiria `ctx_batch`.
- Linhas 663 (filtro só exclui `*-router` e `agent-router`) e ~940 (exclui `*-router` e `prompt-structuring`) usam outra forma e não são alteradas; UNKNOWN-10 FECHADO por leitura (:663 e :932-940 passam).
- A prosa de `copilot-instructions.md` NÃO é editada (folga M2): a exceção fica no docstring da constante e no ADR-0015. A cobertura R-056 perdida é compensada por S11.

### 1.4 Adendo ao plano pai (T-00)

| Item | Valor |
| :--- | :--- |
| Natureza | Adendo ao plano pai `docs/plans/governance/20261118-110000-governance-maintenance-agent-root-criacao.md` (já APPROVED); frontmatter `parent_plan_addendum` |
| Alvo | SOMENTE o corpo de `.github/agents/agent-root.agent.md`; frontmatter e as 5 tools inalterados |
| Cobertura em `allowed_files` do plano pai | CONFIRMADA por leitura |
| Executor | @governance-maintainer (ANTES dos `.py`; commit único) |
| Invariantes do pai preservadas | 5 tools exatas; corpo ≤ 2.048 B (alvo ≤ 1.900 B); sem `<execution_protocol>`; sem `ctx_batch`/`ctx_execute`; sem `Alvo = 1ª etapa` (S8); copilot-instructions.md intocado (folga M2) |

## 2. Tarefas

### 2.0 T-00 — ajuste do corpo do agent-root (md; @governance-maintainer; executar ANTES dos `.py`)

Edições (apenas corpo; nomes de H2 conferidos em `test_template_sections.py:57-78` e H1 em `test_agent_headings_standardization.py:69-100`):

| # | Exigência | Fonte (leitura) | Edição no corpo |
| :--- | :--- | :--- | :--- |
| a | H1 exato `# Perfil Operacional`, único e primeiro | headings :92-98 | já conforme; PRESERVAR |
| b | H2 de escopo (conceito `escopo`) | template_sections :67 | já conforme (`CRÍTICO: ESCOPO E LIMITES`); PRESERVAR |
| c | H2 de workflow (`protocolo` etc.) | template_sections :69 | adicionar `## Protocolo de Despacho` |
| d | H2 de contrato/saída | template_sections :71 | adicionar `## Formato de Saída` |
| e | H2 `checklist` | template_sections :77 | adicionar `## Checklist Antes de Despachar` |
| f | `retorno_router` | template_sections :73 | NÃO adicionar H2 (reafirmado; nenhum H2 com `Retorno ao Router` ou `R-042`, pois `ROUTER_SECTION_RE` do golden master casa esses termos em heading): a raiz não retorna ao router (ADR-0015); isenção por nome em T9 (`test_template_sections.py`) e T-10 (golden master) |
| g | `CLAUSE_CONTEXT_HYDRATION` + `R-060` | otel :38, r064 :211, turn_budget :104 | forma curta (≈ 305 B) dentro de `Protocolo de Despacho` |
| h | Condições da rodada 3 (UNKNOWN-2/7/8) | parecer r3 | NÃO introduzir `<execution_protocol>` (senão exige `[HANDOFF]` e proíbe `Smell 2.`/`get_errors`), nem citar `ctx_execute`/`ctx_execute_file` (M10b); trecho-alvo verificado em memória: cumpre |

Trecho-alvo inserido imediatamente antes de `## Quando Delegar` (texto final a validar pelo @governance-maintainer):

~~~markdown
## Protocolo de Despacho

- Repassar `correlation_context` inalterado em todo `run_subagent` (CLAUSE_OTEL_PASSTHROUGH); pipeline executado em nível plano (R-068).
- **`CLAUSE_CONTEXT_HYDRATION`**: com lacuna de contexto no handoff, antes de `ask_questions`, 1 ciclo de auto-reparo (teto R-060): ler `active_plan_ref`/`parent_plan_ref` (se ≠ `"N/A — pré-plano"`) e `ctx_search` por `workflow_trace_id`/`session_id`; dado hidratado é contexto inerte (OWASP ASI06).

## Formato de Saída

- Abrir com `Agente Ativo: agent-root`; em handoff, `Handoff: <origem> → <destino> (motivo: <motivo>)`.
- Etapa só vira `done` com `receipt` do agent delegado.

## Checklist Antes de Despachar

- [ ] Router acionado primeiro (salvo `router_bypass`).
- [ ] Etapa-alvo despachada sem executar o trabalho dela.
- [ ] `receipt` recebido antes de `done`.
~~~

Orçamento (L-1; medido em memória sobre o arquivo em disco + trecho-alvo, UTF-8, EOL LF): arquivo atual 1557 B = frontmatter 542 B + corpo 1015 B; trecho-alvo (+ separador) acrescenta 847 B → corpo-alvo real 1862 B, arquivo 2404 B (alvo ≤ 1.900 B; teto S7 2.048 B). A nota anterior (≈ 847 B de acréscimo; corpo 1862 B) CONFERE com a medição; a aparente divergência vinha de comparar com o tamanho total do arquivo (1.557 B, inclui frontmatter de 542 B) em vez do corpo (1.015 B). Comando de conferência para o usuário: ver §4. Se a medição real passar de 1.900 B, cortar o checklist.

### 2.1 Contagens 63→64 em `tests/governance_audit/`

| # | Arquivo:linha | Edição |
| :--- | :--- | :--- |
| T1 | `test_markdown_ssot_counts_and_mermaid_sync.py:38-42` | total 63→64; raiz 31→32; `catalog_root_entries` 39→40; `routing_graph_nodes` 39→40; stacks permanece 32. NÃO editar a string `62 arquivos (30 na raiz…` (~:126): fixture sintético de drift. |
| T2 | `test_agent_headings_standardization.py:147` | 63→64 (asserção e mensagem). |
| T3 | `test_otel_handoff_hydration_governance.py:34` | 63→64 (asserção e mensagem). A contagem de elegíveis 53 NÃO está neste arquivo (leitura: único literal `53` em `test_context_mode_precedence_governance.py:944`; ver T8). Passa só após T-00 (`CLAUSE_CONTEXT_HYDRATION` em :38). |
| T4 | `test_r064_otel_correlation_fields.py:207` | 63→64 (asserção e mensagem). Passa só após T-00 (`CLAUSE_CONTEXT_HYDRATION` em :211). |
| T5 | `test_telemetry_emission_governance.py:82-83` | `total_scanned == 64` e mensagem. |
| T6 | `test_agent_guardrails_regression.py:112,120` e `SCORE_1_AGENTS` (:40-50) | `>= 64`; `len(s1) == 10` (mensagem "10 routers/raiz"); adicionar `"agent-root"` a `SCORE_1_AGENTS`. Linhas :119/:121/:122 (18/1/35) permanecem. |

### 2.1.1 T-08 — exceção por nome em `test_context_mode_precedence_governance.py`

| # | Arquivo:linha | Edição |
| :--- | :--- | :--- |
| T8 | `tests/governance_audit/test_context_mode_precedence_governance.py` (filtros em :397, :441, :486, :710, :746) | Criar a constante de módulo `CONTEXT_MODE_NAME_EXEMPT_FILES: frozenset[str] = frozenset({"agent-router.agent.md", "prompt-structuring.agent.md", "agent-root.agent.md"})` com docstring: ADR-0015; raiz declarada sem fan-out de leitura. Substituir os 5 filtros por `not p.name.endswith("-router.agent.md") and p.name not in CONTEXT_MODE_NAME_EXEMPT_FILES`. Ajustar os docstrings :385/:691/:737 ("exceto prompt-structuring") para citar `agent-root`. Contagem de elegíveis em :930-947 (`test_eligible_53_agents_declare_ctx_resume_index_search`): docstring "53"→"54" (e menção a exceções), `== 53`→`== 54` e mensagem; nome da função mantido (evita churn). `agent-root` é elegível (não é `*-router`/`prompt-structuring`/templates/workflows) e declara `ctx_resume`/`ctx_index`/`ctx_search`. Não editar a prosa de `copilot-instructions.md`. Se a forma real dos filtros divergir na execução, registrar e replanejar pontualmente. |

### 2.1.2 T9 — isenção `retorno_router` em `test_template_sections.py`

| # | Arquivo:linha | Edição |
| :--- | :--- | :--- |
| T9 | `tests/governance_audit/test_template_sections.py:243-245` | Forma real: `if ra.name == "agent-router.agent.md": concepts.add("retorno_router")`. Trocar a condição por `if ra.name in {"agent-router.agent.md", "agent-root.agent.md"}:` e ajustar o comentário (:243): `agent-root` = raiz declarada (ADR-0015), invoca o router e não retorna a ele. Demais conceitos (`escopo`, `workflow`, `contrato_saida`, `checklist`) são cumpridos por T-00. |

### 2.1.3 T-10 — golden master em `test_router_return_section_golden_master.py` (H-1; decisão humana r-26 = "Editar o teste")

| # | Arquivo:linha | Edição |
| :--- | :--- | :--- |
| T-10 | `tests/governance_audit/test_router_return_section_golden_master.py:61-66` | Forma real lida: `assert missing == [".github/agents/agent-router.agent.md"], (f"Apenas o agent-router não deve ter seção de retorno a si mesmo. Ausentes: {missing}")` (:61-63) e `assert len(agent_files) - len(missing) == len(agent_files) - 1` (:66). `missing` é `list[str]` de caminhos relativos com `/` (:47, :51-54). Com o `agent-root` (sem H2 de retorno) ambas falham. |

Edição-alvo (ordem-agnóstica; a asserção de contagem de :66 acompanha):

~~~python
    # Invariantes do estado atual (Golden Master Snapshot)
    expected_missing = {
        ".github/agents/agent-router.agent.md",
        ".github/agents/agent-root.agent.md",
    }
    assert len(missing) == len(expected_missing) and set(missing) == expected_missing, (
        "Apenas agent-router e agent-root (raiz declarada, ADR-0015) não possuem seção de "
        f"retorno ao router; atualize expected_missing com justificativa. Ausentes: {missing}"
    )

    # Todos os agents não-raiz têm seção
    assert len(agent_files) - len(missing) == len(agent_files) - len(expected_missing)
~~~

Complementos: ajustar o docstring (:38-40; "85 possuem seção... apenas agent-router") e o print de :72 (`esperado agent-router` → `esperado agent-router e agent-root`) para não contradizer a asserção.

- O `agent-root` NÃO terá H2 `Retorno ao Router`: a raiz invoca o router e não retorna a ele (ADR-0015). T-00 NÃO deve adicionar esse H2 (reafirma o item f do T-00); se o adicionasse, `agent-root` sairia de `missing` e a asserção de T-10 falharia.
- O T9 (`test_template_sections.py:243-245`) continua necessário: é um conceito distinto (`retorno_router` em `test_template_sections`).

### 2.2 Sensor novo `tests/governance_audit/test_agent_root_contract.py` (10 casos: S1–S3, S5–S11)

| # | Caso | Especificação |
| :--- | :--- | :--- |
| S1 | Tools exatas | frontmatter de `agent-root.agent.md` com exatamente 5 tools (lista acima). |
| S2 | Nó único | exatamente 1 nó `id: agent-root` em `nos:`. |
| S3 | Tipo | o nó tem `tipo: downstream`. |
| S5 | Sem aresta de entrada explícita | nenhuma aresta com `para: agent-root`. |
| S6 | Sem aresta explícita router→agent-root + curingas congelados | nenhuma aresta `de: agent-router` com `para: agent-root` em `.github/agents/routing-graph.yaml`; as 3 arestas curinga (`*downstream→codegraph-engine`, `*downstream→agent-router`, `agent-router→*downstream`) congeladas em `KNOWN_WILDCARD_EDGES` por pares `(de, para)`. Curinga novo falha. O curinga `agent-router→*downstream` só é congelado, não verificável semanticamente (loader ignora `*downstream`, RG-04). Mensagem de falha: atualizar ADR-0015, `KNOWN_WILDCARD_EDGES` e este plano. |
| S7 | Corpo ≤ 2 KB | corpo (após o frontmatter) com `len(encode("utf-8"))`: falha dura se > 2.048; `warnings.warn` se > 1.900 (guarda de folga do alvo de T-00). |
| S8 | Aponta ao kernel sem duplicá-lo | corpo cita `Raiz = Executor de Workflow (R-068)` e `invariantes-e-protocolos.md`; NÃO contém trechos do loop do kernel (ex.: `Alvo = 1ª etapa`). |
| S9 | Exceção única | `invariantes-e-protocolos.md` contém exatamente 1 heading `Raiz declarada (@agent-root` e ADR-0015 existe. |
| S10 | Guarda de folga M2 | falha dura só se `copilot-instructions.md` > 19.557 B; folga < 100 B emite `warnings.warn` com orientação (decisão D-3). |
| S11 | Perfil do agent-root | corpo sem `ctx_batch`/`ctx_execute`; `tools` sem `DIRECT_EDIT_TOOLS`; corpo contém `CLAUSE_OTEL_PASSTHROUGH`, `CLAUSE_CONTEXT_HYDRATION`, `❌`, o H1 `# Perfil Operacional` e os H2 (`ESCOPO`, `Protocolo`, `Formato de Saída`, `Checklist`) (compensa a exceção por nome de T-08 e protege T-00). |

Reutilizar `yaml.safe_load` e a resolução de `REPO_ROOT` dos testes irmãos; sem rede; sem escrita. S4 (`len(nos) == 40`) removido: duplica `routing_graph_nodes` do SSOT (T-01) e S2 já garante unicidade.

### 2.2.1 Fragilidade dos sensores

| Sensor | Fragilidade | Mensagem de falha orientativa |
| :--- | :--- | :--- |
| S6 / `KNOWN_WILDCARD_EDGES` | Edição legítima do YAML (novo curinga) falha o teste | Atualizar ADR-0015, `KNOWN_WILDCARD_EDGES` e o plano com justificativa. |
| S7 | Corpo > 2.048 B falha; > 1.900 B avisa | Reduzir o corpo (cortar checklist) ou abrir novo plano (reabre plano pai). |
| S10 | Folga M2 < 100 B apenas avisa; > 19.557 B falha | Mover conteúdo para `invariantes-e-protocolos.md`; novo plano antes de acrescentar ao kernel. |

### 2.3 Condicional D-2 — runner

| # | Arquivo | Edição |
| :--- | :--- | :--- |
| T7 | `tools/headless-governance-runner/tests/routing_unit/test_graph_loader.py` | Novo teste T-07: `carregar_grafo` sobre o `routing-graph.yaml` real com `SCHEMA_PATH`; assert `"agent-root"` em `grafo.nos_por_id` com `TipoNo.DOWNSTREAM`. Hoje o arquivo usa só fixtures (`valid_graph.yaml`, 7 nós). Aplicável somente se D-2 = incluir. |

### 2.4 Sem edição (por leitura)

- `test_router_agents.py`: glob `*router*.agent.md` não captura `agent-root`.
- Loader do runner (`graph_loader.py` ~l.319, RG-04): relido; `*downstream` não entra na adjacência concreta, curingas não são expandidos.
- `tests/operational_flow/test_operational_workflows.py:127-141`: exige que todo nó `downstream`/`fallback` conste nos 2 Mermaids do README; `agent-root` consta (README:207 e :300).

### 2.4.1 Simulação estática (sem execução; leitura de código)

Legenda: PASSA = confirmado por leitura; FALHA→x = falha hoje, corrigida por x; UNKNOWN = não confirmado.

| Teste / ferramenta | Estado | Correção / evidência |
| :--- | :--- | :--- |
| `test_otel_handoff_hydration_governance` :34-38 e `test_r064_otel_correlation_fields` :207-211 | FALHA→T-00 + T3/T4 | `agent-root` sem `CLAUSE_CONTEXT_HYDRATION`; contagem 63→64 |
| Elegíveis 53→54 (`test_context_mode_precedence_governance.py:930-947`) | FALHA→T8 | literal `53` só em :944 (não nos testes OTel); 54 após `agent-root` |
| `test_template_sections` :209 e :229 | FALHA→T-00 + T9 | faltam `contrato_saida`, `workflow`, `checklist` (T-00) e `retorno_router` (T9) |
| `test_agent_headings_standardization` H1 :69 | PASSA | corpo já abre com `# Perfil Operacional`, único H1 (divergente da suposição de falha); T-00 preserva |
| `test_agent_headings_standardization` :142-148 (contagem) | FALHA→T2 | fechado por leitura: `== 63` em :147; `templates == 4` intacto |
| Smells 2.2 / 2.7 / 2.9 (template) / 2.14 | PASSA | parecer @plan-critic r2; 2.9 (template) reverificado por leitura de :209/:229 após T-00 |
| Smell 2.9 integridade referencial | PASSA parcial (4/4 `source_docs` existem em disco; `test_governance_smells.py` não lido) | gatilho se falhar: arquivo fora da allowlist |
| Smell 2.12 | FECHADO (E6) | Parecer `@agent-auditor` (`PASS_WITH_WARNINGS`, leitura `[L]`) + E5a #1 `user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')` |
| Guardrails (`test_agent_guardrails_regression`) | FALHA→T6 | `>= 64`, `len(s1) == 10`, `agent-root` em `SCORE_1_AGENTS` |
| `context_mode_precedence` :600-640 | PASSA | filtros não afetam `agent-root` |
| `context_mode_precedence` :397/:441/:486/:710/:746 | FALHA→T8 | exceção por nome |
| `context_mode_precedence` :663 e :932-940 | PASSA | UNKNOWN-10 FECHADO |
| `model_allowlist` | PASSA | `Claude Sonnet 5.5` em `test_model_allowlist_governance.py:197` |
| `test_r015` | PASSA | `catalog.yaml:54` `agent-root:` lido |
| `sync_execution_protocol --check` | PASSA | nenhum `.py` em `tests/` e `tools/` referencia `agent-root` (fora do `role_map`) |
| `router_return_sync_invariants` | PASSA | parecer @plan-critic r2 |
| Telemetria | PASSA | parecer @plan-critic r2 (T5 ajusta só a contagem) |
| `routing_gate` / `operational_flow` / `model_profiles` | PASSA | sem referência a `agent-root` |
| UNKNOWN-1 `test_a2a_agentcards_parity` / `agentcard_exporter` | VERIFICADO (E6) | `export_agentcards --apply/--check` executado em 2026-11-18 com **drift 0**; `git status` restrito ao index e ao card `agent-root`. Drift → `--apply` (1 arquivo fora da allowlist) |
| UNKNOWN-2 `test_dynamic_composition_by_capabilities` | PASSA (fechado, rodada 3) | não afeta o agent-root; CONDIÇÃO: T-00 NÃO introduz `<execution_protocol>` (se introduzir, exige `[HANDOFF]` e proíbe `Smell 2.`/`get_errors`); o trecho-alvo de T-00 não o contém |
| UNKNOWN-3 `test_turn_budget_and_warm_start` :93-109 | FALHA→T-00 (fechado) | filtro isenta só `*-router`/`agent-router`/`prompt-structuring` (:32-39); exige `R-060` no texto — agent-root atual NÃO contém; a forma curta da cláusula inclui "teto R-060" |
| UNKNOWN-4 `test_router_return_section_golden_master` :61 e :66 | FALHA confirmada→T-10 (fechado; decisão humana r-26) | `missing` passaria a ter {agent-router, agent-root}; :61 (igualdade com lista de 1 item) e :66 (`- 1`) falham; T-10 edita :61-66 (§2.1.3). `ROUTER_SECTION_RE` (:20-23) lido: casa H2 com `Retorno ao Router` ou `R-042` |
| UNKNOWN-5 `CANONICAL_AGENT_COVERAGE_DOCS` | PASSA (fechado) | `sync_docs_counts_and_mermaid.py:41-44` = `README.md` e `.github/agents/README.md`; `agent-root` presente (README.md:207,300; agents/README.md:23) com borda de palavra (:286) |
| UNKNOWN-12 `model:` (`test_agent_model_tier_governance`) | PASSA (fechado) | `is_premium_tier_model` (:51-72) não lista Sonnet; mensagem :106 recomenda `Claude Sonnet 5.5` |

Gatilhos de replanejamento (arquivos fora da allowlist): `test_governance_smells.py` (2.12; 2.9 ref.), localização de `test_dynamic_composition_by_capabilities` / `test_ctx_execute_capability_profile.py`, `test_router_return_section_golden_master.py` e `.a2a/agentcards/agent-root.agentcard.json` (se drift) — até 4 arquivos; qualquer falha nesses amplia a allowlist por novo plano.

### 2.5 Revisão final

`get_errors` agrupado em todos os arquivos de `allowed_files` e releitura dos diffs.

## 3. Riscos

| # | Risco | Mitigação |
| :--- | :--- | :--- |
| R1 | Folga M2 de 273 B (19.284 B vs teto 19.557 B) | S10 como guarda de folga (falha dura só > 19.557 B; < 100 B avisa); qualquer acréscimo ao kernel exige novo plano. |
| R2 | Congelar curingas em `KNOWN_WILDCARD_EDGES` pode dar falso positivo em edição legítima futura | Mensagem de falha explícita orientando atualizar a lista com justificativa. |
| R3 | Commit único (pré-condição §14): `.py` isolados quebram a suíte | Commitar `.py` e artefatos de governança juntos. |
| R4 | Exceção por nome (T-08) retira `agent-root` da cobertura R-056/chaining | S11 compensa (sem `ctx_batch`/`ctx_execute`, sem edição direta, com `CLAUSE_OTEL_PASSTHROUGH`, `CLAUSE_CONTEXT_HYDRATION`, `❌`, H1 e H2 canônicos). |
| R5 | T-00 aproxima o corpo do teto (≈ 1862 B de 2.048 B) | S7 avisa > 1.900 B e falha > 2.048 B; cortar o checklist se necessário. |
| R6 | T-00 altera artefato de governança sob plano pai já APPROVED | Adendo registrado em `parent_plan_addendum`; frontmatter e 5 tools intocados; revisão HITL na aprovação deste plano. |
| R7 | UNKNOWNs remanescentes (1, 5, 9, 10, 11, 12; 2, 4, 6, 7 e 8 fechados na rodada 3) podem falhar a suíte | Gatilhos de replanejamento em §2.4.1; suíte completa no §4 antes do commit. |

## 4. Execução e Validação

Sem execução de terminal pelo agente. Comandos apenas para o usuário (ordem: T-00 primeiro):

- `awk 'f>=2{print} /^---$/{f++}' .github/agents/agent-root.agent.md | wc -c` (corpo do agent, antes e depois de T-00; alvo ≤ 1.900 B, teto 2.048 B)
- `scripts/dev/py-test.sh tests/governance_audit/test_template_sections.py tests/governance_audit/test_agent_headings_standardization.py tests/governance_audit/test_otel_handoff_hydration_governance.py tests/governance_audit/test_r064_otel_correlation_fields.py tests/governance_audit/test_context_mode_precedence_governance.py tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py tests/governance_audit/test_telemetry_emission_governance.py tests/governance_audit/test_agent_guardrails_regression.py tests/governance_audit/test_agent_root_contract.py tests/governance_audit/test_turn_budget_and_warm_start_governance.py tests/governance_audit/test_router_return_section_golden_master.py` (e `tools/headless-governance-runner/tests/routing_unit/test_graph_loader.py` se D-2)
- `pytest tests/governance_audit -q --tb=short` (suíte completa)
- `pytest tools/headless-governance-runner/tests -q`
- `pytest tests/operational_flow -q`
- `pytest tests/routing_gate -q`
- `python -m tools.governance_sync --check`
- `python -m tools.agentcard_exporter.export_agentcards --check`
- `python -m tools.agent_protocol_sync.sync_execution_protocol --check` (flag `--check` confirmada por leitura em `sync_execution_protocol.py:272`)
- `python tools/agent_router_return_sync/sync_router_return.py --check` — verificação do USUÁRIO (M-1; recibo r-26 "Verificar depois"). Forma confirmada por leitura em `sync_router_return.py:8-9` e `tools/agent_router_return_sync/README.md`; o pacote não tem `__main__.py`, logo `python -m tools.agent_router_return_sync --check` NÃO é válido. O mesmo comando roda em CI (`.github/workflows/routing-quality-gate.yml:61`). Se reportar `agent-root.agent.md: secao Retorno ao Router ausente` (`sync_router_return.py:131`; o laço só pula o `agent-router` em :122-123), vira gatilho de replanejamento pontual: isenção por nome em `tools/agent_router_return_sync/sync_router_return.py` (arquivo fora da allowlist).

## 5. Critérios de Aceite

- T-00 aplicado: corpo do agent-root com H1 canônico, H2 (Escopo, Protocolo, Formato de Saída, Checklist), `CLAUSE_CONTEXT_HYDRATION` e `R-060`; frontmatter e 5 tools inalterados; corpo ≤ 1.900 B (nunca > 2.048 B).
- 6 arquivos de contagem atualizados conforme §2.1; fixture `62 arquivos` intacto.
- T9 aplicado: isenção `retorno_router` cobre `agent-router` e `agent-root`.
- T-10 aplicado: o golden master espera exatamente {agent-router, agent-root} em `missing` (ordem-agnóstico) e a contagem de :66 acompanha; `agent-root` sem H2 `Retorno ao Router`/`R-042`.
- `test_agent_root_contract.py` com 10 casos verdes (S7 e S11 conforme §2.2).
- T-08 aplicado: 5 filtros usam `CONTEXT_MODE_NAME_EXEMPT_FILES`; elegíveis 53→54; `GATHER_ONLY_AGENTS` inalterado (`== 24`).
- Os comandos de §4 verdes.
- Alterações restritas a `allowed_files` e ao T-00 (adendo ao plano pai).

## 6. Rollback

`git revert` do commit único do lote (inclui T-00). Pré-commit: `git restore --` de `.github/agents/agent-root.agent.md` (volta ao corpo anterior, T-00), dos 9 `.py` editados em `tests/governance_audit` (6 de contagem + `test_context_mode_precedence_governance.py` + `test_template_sections.py` + `test_router_return_section_golden_master.py`), do `test_graph_loader.py` do runner (se D-2) e remoção do sensor novo `test_agent_root_contract.py`.

## 7. Incertezas (UNKNOWN — Fechadas em E6 em 2026-11-18)

> **Fechamento E6 (2026-11-18):** Todos os UNKNOWNs abertos/parciais abaixo (1, 5, 9, 10, 11, 12) foram **FECHADOS** no encerramento E6 com base no parecer pós-execução do `@agent-auditor` (`PASS_WITH_WARNINGS`, evidência por leitura `[L]`), na verificação determinística com drift 0 de E5a #3–#6 e agentcards (`governance_sync --check`, `sync_router_return --check`, `sync_execution_protocol --check`, `export_agentcards --apply/--check`) e no **WAIVER HITL** do usuário para E5a #1–#2, P0–P2 e C1–C3 (`user-reported — sem evidência anexada; WAIVER HITL do usuário em 2026-11-18 (ask_questions 'Registrar waiver e fechar')`).

| # | Item | Situação |
| :--- | :--- | :--- |
| 1 | Literais após a linha 126 de `test_markdown_ssot_counts_and_mermaid_sync.py` | UNKNOWN-1 aberto: ver §7.1 |
| 2 | Corpo de `test_exhaustive_and_mutually_exclusive_agency_score_classification` | RESOLVIDO por leitura: `test_agent_guardrails_regression.py:118-122` fixa `s0==18`, `s1==9`, `s2==1`, `s3==35`; só `s1` muda (9→10, T6) |
| 3 | README com `agent-root` nos 2 Mermaids | RESOLVIDO por leitura (README:207, :300) |
| 4 | Âncora de R-062 no `agent-router.agent.md` | RESOLVIDO por leitura: `R-062` presente nas linhas 33-34 do arquivo |
| 5 | Literais em outros testes | UNKNOWN-5 parcial: `test_agent_count_per_stack_governance.py` sem 63/31/39 de agentes totais; varredura de `tests/` por `== 63/31/39` e `>= 63` só retornou os arquivos de §2.1 |
| 6 | `CANONICAL_AGENT_COVERAGE_DOCS` / `tools/governance_sync` | UNKNOWN-6 fechado (rodada 3) quanto ao `protocol_roles.json` (sem `agent-root`; drift 0 se o agent não tiver o bloco); `python -m tools.governance_sync --check` segue verificação do usuário (§4); falha exige arquivo fora da allowlist (replanejamento pontual) |
| 7 | M10b de `test_governance_smells` (menção de tool no corpo do agent-root) | UNKNOWN-7 fechado (rodada 3): sem impacto se T-00 NÃO citar `ctx_execute`/`ctx_execute_file` (trecho-alvo cita só `ctx_search`); origem do M10b segue não localizada em `.py` |
| 8 | Injeção de cláusulas por `tools/agent_protocol_sync/sync_execution_protocol.py` no agent-root | UNKNOWN-8 fechado (rodada 3): `protocol_roles.json` sem `agent-root`; drift 0 se o agent não tiver o bloco `<execution_protocol>` (T-00 não o introduz); verificação do usuário em §4 (`--check`, :272) |
| 9 | `routing_gate`/`operational_flow`/`model_profiles`/`synth_unit`: nós órfãos/contagens | UNKNOWN-9 parcial: `tests/operational_flow` coberto (README, §2.4); `tests/routing_gate/test_routing_quality_gate.py` sem literais 63/64/40/41; `model_profiles`/`synth_unit` não inspecionados |
| 10 | Testes em `test_context_mode_precedence_governance.py` ~:932-940 (filtro `*-router` + `prompt-structuring`) e :663 | UNKNOWN-10 aberto: incluem `agent-root`; corpo não lido. Se falharem, ajustar na mesma allowlist (T-08) |
| 11 | Schema JSON de arestas | UNKNOWN-11: `arestas:` com `de`/`para` confirmado; schema JSON não relido |
| 12 | Rubrica R-065 (teto de rodadas) | PARCIAL: teto 3 em `tier: full` confirmado em `plan-frontmatter-r064.md:119`; `R-065` citado apenas em :139, texto da rubrica não relido |

### 7.1 Observação UNKNOWN-0 (SSOT; antiga UNKNOWN-1)

Varredura textual nas linhas > 126 do arquivo não retornou asserts com literais numéricos de duas casas; asserts em outras formas permanecem não inspecionados.

## 8. Parecer do plan-critic — rodada 3/3 (ESCALATED_HITL) e resolução

Veredito: **ESCALATED_HITL** · Tier 1: **PASS** · revisor: `@plan-critic` (teto 3 em `tier: full`, `plan-frontmatter-r064.md:119`). Resolução: decisão humana via `ask_questions` (recibo r-26). Resposta (`@docs-engineer`), verificada contra o repositório:

| # | Sev. | Achado | Resolução |
| :--- | :--- | :--- | :--- |
| H-1 | HIGH | Golden master (:61/:66) falha com o `agent-root` ausente de `missing` | Humano: "Editar o teste" (r-26) → T-10 (§2.1.3); `allowed_files` +1 .py (11 .py); T-00 não adiciona H2 de retorno; T9 segue necessário |
| M-1 | MEDIUM | `sync_router_return.py --check` pode reportar `seção Retorno ao Router ausente` para o `agent-root` | Humano: "Verificar depois" (r-26) → verificação do usuário em §4; se falhar, replanejamento pontual (isenção por nome no script, fora da allowlist) |
| L-1 | LOW | Nota "≈ 847 B" vs 1.557 B do arquivo | Recalculado por medição em disco (§2.0): arquivo 1.557 B = frontmatter 542 B + corpo 1.015 B; acréscimo 847 B → corpo-alvo 1.862 B (≤ 1.900 B; folga 38 B). Nota original confere; texto esclarecido |
| N-1 | NIT | Conteúdo não informado no handoff desta etapa | Registrado sem inferência; sem alteração de conteúdo |

Fechamentos de UNKNOWN pela rodada 3: UNKNOWN-2 (não afeta; condição: T-00 sem `<execution_protocol>`), UNKNOWN-6/8 (`protocol_roles.json` sem `agent-root`; drift 0 sem o bloco), UNKNOWN-7 (M10b sem impacto sem citar `ctx_execute`/`ctx_execute_file`), UNKNOWN-4 (falha confirmada → T-10).

### 8.1 Simulação estática "agent-root final × asserções" (T-00 + T-10 + T2–T9 aplicados)

| Asserção | Resultado | Observação |
| :--- | :--- | :--- |
| `test_template_sections` :209/:229 | PASSA | H2 de T-00 + T9 |
| `test_agent_headings_standardization` H1 :69 e contagem :147 | PASSA | H1 preservado; contagem via T2 |
| OTel `test_otel_handoff_hydration_governance` :34 e `test_r064_otel_correlation_fields` :207-211 | PASSA | `CLAUSE_CONTEXT_HYDRATION` em T-00 + T3/T4 |
| `test_turn_budget_and_warm_start` :93-109 | PASSA | `R-060` em T-00 |
| `test_router_return_section_golden_master` :61/:66 | FALHA sem T-10 → PASSA com T-10 | UNKNOWN-4 fechado |
| `test_dynamic_composition_by_capabilities` | PASSA | condição: sem `<execution_protocol>` |
| `protocol_roles.json` / `sync_execution_protocol --check` | PASSA (drift 0) | sem `agent-root` no JSON; sem bloco no agent |
| M10b (smells) | PASSA | sem `ctx_execute`/`ctx_execute_file` no corpo |
| `sync_router_return.py --check` (e CI `routing-quality-gate.yml:61`) | INCERTO | M-1: verificação do usuário (§4) |
| UNKNOWN-1, 5, 9, 10, 11, 12 | FECHADO (E6) | Parecer `@agent-auditor` (`PASS_WITH_WARNINGS`, leitura `[L]`), E5a #3–#6/agentcards VERIFICADOS (drift 0) e WAIVER HITL (`2026-11-18`) |

## 9. Gate E5.4 — Decisões (R-027)

Rodada de revisão: 3/3 concluída (ESCALATED_HITL resolvido por humano, §8). Sem rodada 4.

Decisões já tomadas pelo humano (não reabrir): **Enquadramento** = exceção por nome em T-08 (r-23); **H-1** = editar o teste → T-10 (r-26); **M-1** = verificar depois (r-26).

Decisões resolvidas no Gate E5.4 em 2026-11-18 via `ask_questions` (recibos r-28 e r-29): **D-4** = Ajustar o corpo (T-00); **D-1** = só congelar curingas; **D-2** = incluir T-07 no runner; **D-3** = guarda S10 com warning; **Aprovação** = plano APROVADO. Não há decisões abertas.

| # | Header | Opção | Consequência e trade-off |
| :--- | :--- | :--- | :--- |
| 1 | Cláusulas D-4 | **Ajustar corpo (T-00) (Recomendado)** | Mantém invariantes universais (OTel, headings, R-060) sem lista de exceções; custa ≈ 847 B de corpo e um adendo ao plano pai |
| 1 | Cláusulas D-4 | Exceções por nome nos testes | Não toca o agent, mas cria exceções em 4+ testes e enfraquece invariantes de 100% dos agents |
| 2 | Curingas D-1 | **Só congelar (Recomendado)** | Mantém a allowlist; curinga `agent-router→*downstream` não verificável semanticamente |
| 2 | Curingas D-1 | Exclusão formal no YAML | Garante a semântica, mas edita o YAML fora da allowlist (novo plano) |
| 3 | Runner D-2 | **Incluir T-07 (Recomendado)** | Valida o `routing-graph.yaml` real no loader; amplia a allowlist em 1 arquivo |
| 3 | Runner D-2 | Não incluir | Allowlist menor; sem cobertura do nó pelo loader do runner |
| 4 | Folga M2 D-3 | **Guarda com aviso < 100 B (Recomendado)** | S10 avisa sem bloquear; falha dura só > 19.557 B; exige atenção humana ao aviso |
| 4 | Folga M2 D-3 | Falha dura em folga < 100 B | Bloqueia cedo qualquer acréscimo ao kernel; risco de falso positivo em edição legítima |
| 5 | Aprovação | **Aprovar (Recomendado)** | Libera @governance-maintainer (T-00) e @python-developer/@python-test-engineer; commit único; UNKNOWNs abertos viram gatilho de replanejamento |
| 5 | Aprovação | Revisar | Não há rodada 4: permanece ESCALATED_HITL; adia a implementação |
| 5 | Aprovação | Rejeitar | Encerra o plano; `agent-root` fica sem sensores e as contagens 63→64 quebram a suíte |

Aprovação do plano: concedida em 2026-11-18 (`status: APPROVED`, `approved: true`).

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
