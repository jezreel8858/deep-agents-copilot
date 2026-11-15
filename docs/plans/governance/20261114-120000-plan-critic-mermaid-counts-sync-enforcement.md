---
status: APPROVED
approved: true
approved_by: "human"
approved_at: "2026-11-14T12:15:00Z"
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-14"
related-planning-doc: "docs/plans/governance/20261114-120000-revisor-cetico-universal-pre-hitl-r064.md"
allowed_files:
  - "README.md"
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/agents/README.md"
  - ".github/skills/README.md"
  - ".github/instructions/README.md"
  - ".github/agents/workflows.md"
  - ".github/agents/workflows/*.md"
  - ".github/agents/governance-factory.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/skills/governance-factory-patterns/SKILL.md"
  - "docs/README.md"
  - "docs/repo-map.md"
  - "docs/architecture/*.md"
  - "docs/guides/*.md"
  - "tests/README.md"
  - "tools/governance_sync/__init__.py"
  - "tools/governance_sync/__main__.py"
  - "tools/governance_sync/sync_docs_counts_and_mermaid.py"
  - "tools/governance_sync/README.md"
  - "tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py"
lessons_extracted: true
lessons_applied_to: ["@agent-auditor", "plan-conformance-patterns"]
lessons_at: "2026-11-15"
---

# Plano de Governança: Sincronização Canônica de Contagens SSoT, Diagramas Mermaid (@plan-critic) e Enforcement Automatizado

## 1. Contexto, Diagnóstico de Gaps (Causa-Raiz) e Aritmética Canônica SSoT

Após a introdução do agente `@plan-critic` (Gate Pré-HITL R-064) no plano `docs/plans/governance/20261114-120000-revisor-cetico-universal-pre-hitl-r064.md`, identificou-se que os diagramas `mermaid` de workflows e as contagens agregadas de artefatos em documentos Markdown vivos sofrem de deriva recorrente por falta de uma ferramenta determinística de sincronização e de um teste de auditoria dedicado ao conteúdo Markdown/Mermaid.

### 1.1. Aritmética Canônica SSoT (Equação Inequívoca de Agents e Nós)

| Métrica SSoT | Valor Canônico Atual | Equação / Composição Exata | Fonte SSoT Primária (Derivação Dinâmica em Runtime) |
|---|---|---|---|
| **Total de arquivos `*.agent.md` físicos** | **63** | **31** na raiz (`.github/agents/*.agent.md`) + **32** nas 8 stacks (`.github/agents/{frontend,backend}/*/*.agent.md`, sendo **8** domain routers + **24** especialistas de stack) | Glob físico `.github/agents/**/*.agent.md` |
| **Entradas em `.github/agents/catalog.yaml` (catálogo raiz)** | **39** | **31** agents da raiz + **8** domain routers (que residem fisicamente nas pastas de stack, mas também são indexados no `catalog.yaml` raiz para roteamento de 1º nível pelo `@agent-router`) | `len(yaml.safe_load(catalog_root)[agents])` |
| **Entradas nos 8 `catalog.yaml` de stack** | **32** (8 x 4) | **8** stacks x (**1** domain router + **3** especialistas). Interseção deliberada dos 8 domain routers com o catálogo raiz: `39 + 32 - 8 = 63` agents únicos | `.github/agents/{frontend,backend}/*/catalog.yaml` |
| **Nós em `.github/agents/routing-graph.yaml`** | **39** | **39** entradas `- id:` na chave `nos:` (**31** agents da raiz + **8** domain routers, excluindo `workflows:` e `arestas:`). Substitui a menção obsoleta `(42 nós)` por `(39 nós)` | `len(yaml.safe_load(routing_graph)["nos"])` |
| **Skills canônicas** | **81** | **81** skills (**15** Tier 1, **65** Tier 2, **1** Tier 3) em `.github/skills/.index.json` e **81** arquivos `.github/skills/*/SKILL.md` | Derivação dinâmica em runtime via `.github/skills/.index.json` e glob `.github/skills/*/SKILL.md` (sem hardcode) |
| **Instructions canônicas** | **6** | **6** adapters genéricos `*.instructions.md` na raiz de `.github/instructions/` (excluindo `local/`, que é gitignored por R-043) | Derivação dinâmica em runtime via glob não-recursivo `.github/instructions/*.instructions.md` (sem hardcode) |
| **Workflows canônicos** | **10** | Arquivos `workflow-*.md` em `.github/agents/workflows/` (+ `invariantes-e-protocolos.md` e índice `.github/agents/workflows.md`) | Glob `.github/agents/workflows/workflow-*.md` |

> **Nota de Derivação Dinâmica em Runtime (Zero Hardcode)**: O script `sync_docs_counts_and_mermaid.py` e o teste derivam todos os números dinamicamente em runtime a partir dos arquivos SSoT (`catalog.yaml`, chave `nos:` de `routing-graph.yaml`, `.github/skills/.index.json` + `.github/skills/*/SKILL.md` e `.github/instructions/*.instructions.md` excluindo `local/`), sem hardcode.

## 2. Decisão Arquitetural e Tabela Determinística de Workflows (Mermaid & Gate Pré-HITL R-064)

### 2.1. Tabela Decisória Explícita (10 `workflow-*.md` + `workflows.md` + `invariantes-e-protocolos.md`)

| # | Arquivo | Gera Plano R-064 em `docs/plans/<tipo>/`? | Possui Bloco `mermaid`? | Decisão Canônica | Nó Exato de Transição no Mermaid (De -> `@plan-critic` -> Para) / Justificativa |
|---|---|---|---|---|---|
| 1 | `.github/agents/workflows.md` | Sim (Índice Macro R-064) | Sim | **INSERIR `@plan-critic`** | `Planner / @docs-engineer (docs/plans/<tipo>/) --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{Gate HITL: ask_questions}` |
| 2 | `.github/agents/workflows/workflow-feature-development.md` | Sim (`feature`, `requirements`, `architecture`, `implementation`, `test-strategy`) | Sim | **INSERIR `@plan-critic`** | `FeaturePlan[@feature-planner / *-arch-advisor -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{ask_questions}` (com loop `NEEDS_REVISION max 2x`) |
| 3 | `.github/agents/workflows/workflow-refactoring.md` | Sim (`refactor`, `test-strategy`) | Sim | **INSERIR `@plan-critic`** | `MikadoPlan[@refactor-planner + @test-strategy -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{ask_questions}` antes da Etapa 4 (Execução em Lote) |
| 4 | `.github/agents/workflows/workflow-bug-fix.md` | Sim (`bug-triage`, `implementation`) | Sim | **INSERIR `@plan-critic`** | `BugTriage[@bug-triage -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{ask_questions}` antes da Etapa 3 (Correção Cirúrgica) |
| 5 | `.github/agents/workflows/workflow-governance-maintenance.md` | Sim (`governance`) | Sim | **INSERIR `@plan-critic`** | `AuditPlan[@agent-auditor -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> Etapa2{Etapa 2: Checkpoint HITL ask_questions}` |
| 6 | `.github/agents/workflows/workflow-framework-migration.md` | Sim (`architecture`, `refactor`, `implementation`) | Sim | **INSERIR `@plan-critic`** | `MigrationPlan[@tech-solution-architect / @refactor-planner -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{ask_questions}` |
| 7 | `.github/agents/workflows/workflow-dependency-vulnerability-remediation.md` | Sim (`bug-triage`, `refactor`, `implementation`) | Sim | **INSERIR `@plan-critic`** | `RemediationPlan[@security-auditor / @refactor-planner -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{ask_questions}` |
| 8 | `.github/agents/workflows/workflow-ui-layout.md` | Sim (`feature`, `implementation`) | Sim | **INSERIR `@plan-critic`** | `UIPlan[@requirements-analyst / @feature-planner -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{ask_questions}` |
| 9 | `.github/agents/workflows/workflow-release-readiness.md` | Sim (`test-strategy`, `implementation`) | Sim | **INSERIR `@plan-critic`** | `ReleasePlan[@test-strategy / @devops-ci-cd -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{ask_questions}` |
| 10 | `.github/agents/workflows/workflow-technical-analysis.md` | Sim (`architecture`) | Sim | **INSERIR `@plan-critic`** | `ArchAnalysis[@tech-solution-architect / *-arch-advisor -> @docs-engineer] --> PlanCritic[@plan-critic: Gate Pré-HITL R-064] --> GateHITL{ask_questions}` |
| 11 | `.github/agents/workflows/workflow-prompt-synthesis.md` | **Não** (Loop R-041 no Problem Space) | Sim | **N/A — Isento de `@plan-critic`** | Opera em loop R-041 no Problem Space sem gerar plano R-064 em `docs/plans/<tipo>/` |
| 12 | `.github/agents/workflows/invariantes-e-protocolos.md` | Normativo transversal | Não (0 blocos Mermaid) | **N/A (Mermaid) / ATUALIZAR TEXTO** | Documento normativo sem bloco Mermaid; sincronizar menção textual ao Gate Pré-HITL (`@plan-critic`) na Matriz de Evidências |

### 2.2. Regra Determinística Exata no Teste e na Ferramenta de Sync

Tanto `tools/governance_sync/sync_docs_counts_and_mermaid.py` quanto `tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py` usarão duas constantes canônicas explícitas:

- `R064_PRE_HITL_WORKFLOW_MERMAID_FILES: tuple[str, ...]`: contém exatamente os **10 arquivos** com decisão **INSERIR `@plan-critic`** (itens #1 a #10 da Tabela 2.1: `.github/agents/workflows.md` e os 9 `workflow-*.md` que geram planos R-064 em `docs/plans/<tipo>/`). Para cada arquivo desta tupla, exige-se pelo menos 1 bloco `mermaid` sintaticamente válido contendo a substring `plan-critic`.
- `WORKFLOW_MERMAID_EXEMPTIONS: dict[str, str]`: mapeia explicitamente `.github/agents/workflows/workflow-prompt-synthesis.md` e `.github/agents/workflows/invariantes-e-protocolos.md` para suas justificativas técnicas não-vazias.
- **Invariante de Cobertura Exaustiva**: `set(R064_PRE_HITL_WORKFLOW_MERMAID_FILES) | set(WORKFLOW_MERMAID_EXEMPTIONS.keys())` deve ser idêntico ao conjunto `{.github/agents/workflows.md} | set(glob(.github/agents/workflows/*.md))`.

## 3. Especificação Técnica de `tools/governance_sync` (Entry-Points, CLI e Reuso de `core.py`)

1. `tools/governance_sync/sync_docs_counts_and_mermaid.py`: módulo concreto de sincronização e auditoria de contagens SSoT e presença/sintaxe Mermaid, reutilizando `create_sync_parser`, `SyncOptions` e `SyncReport` de `tools/governance_sync/core.py`.
2. `tools/governance_sync/__main__.py`: entry-point do pacote delegando para `sync_docs_counts_and_mermaid.main()`, permitindo `python -m tools.governance_sync --check` / `--dry-run` / `--apply` e `python -m tools.governance_sync.sync_docs_counts_and_mermaid --check` / `--dry-run` / `--apply`.
3. `tools/governance_sync/README.md`: documentação técnica dos modos CLI (`--check` audita contagens SSoT e presença/sintaxe Mermaid nos arquivos monitorados com exit code 0/1; `--dry-run` exibe o `SyncReport` sem mutar disco; `--apply` atualiza deterministicamente contagens e blocos sincronizáveis em `MONITORED_LIVE_MARKDOWN_FILES`).

## 4. Portão R-055 (Q1, Q2, Q3) — Justificativa de Novo Teste e Não-Sobreposição

- **Q1 — Relação com testes existentes em `tests/governance_audit/`**:
  - `test_catalog_agents_referenced_in_canonical_workflows.py` checa apenas se o nome textual do agent de `catalog.yaml` aparece em algum lugar de `.github/agents/workflows.md`, sem inspecionar blocos `mermaid` dos 10 `workflow-*.md`, sem validar sintaxe Mermaid e sem auditar contagens em `README.md`/`CLAUDE.md`/`docs/**`.
  - `test_agent_count_per_stack_governance.py` checa apenas a estrutura interna das 8 stacks (4 agents por stack), sem auditar os totais globais (**63** `*.agent.md`, **39** no `catalog.yaml` raiz, **39** nós no `routing-graph.yaml`, **79** skills, **17** instructions, **10** workflows) nos arquivos Markdown vivos.
  - Logo, `test_markdown_ssot_counts_and_mermaid_sync.py` complementa ambos sem duplicação.
- **Q2 — Falha real capturada**: ausência de `@plan-critic` nos diagramas Mermaid dos workflows R-064, menção obsoleta `(42 nós)` em vez de `(39 nós)` para `routing-graph.yaml` e contagens desatualizadas em `README.md`/`docs/**`.
- **Q3 — Determinístico, offline e < 1s**: Sim (< 200ms, 100% local).

## 5. Ondas de Implementação (Sequenciamento Estrito: Onda 1 -> Onda 2 -> Onda 3 -> Onda 4)

- **Onda 1 (Documentação Viva & Mermaid)**: Atualizar os blocos `mermaid` dos 10 arquivos de `R064_PRE_HITL_WORKFLOW_MERMAID_FILES` com `@plan-critic`, atualizar texto de `invariantes-e-protocolos.md` e sincronizar contagens (**63** `*.agent.md` = 31 raiz + 32 stacks; **39** em `catalog.yaml` raiz; **39** nós em `routing-graph.yaml`; **79** skills; **17** instructions; **10** workflows) em `MONITORED_LIVE_MARKDOWN_FILES`.
- **Onda 2 (Contratos da Fábrica)**: Atualizar `.github/agents/governance-factory.agent.md`, `.github/agents/governance-maintainer.agent.md` e `.github/skills/governance-factory-patterns/SKILL.md`.
- **Onda 3 (Ferramenta `tools/governance_sync`)**: Criar `tools/governance_sync/sync_docs_counts_and_mermaid.py`, `tools/governance_sync/__main__.py` e `tools/governance_sync/README.md` e validar `python -m tools.governance_sync --check`.
- **Onda 4 (Teste de Auditoria Tier 1 — ativado somente após Ondas 1, 2 e 3 verdes)**: Criar `tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py` e executar `pytest`.

## 6. Riscos, Mitigações, Escopo de Exclusão de Históricos e Validação Sintática Mermaid

- **Allowlist Monitorada (`MONITORED_LIVE_MARKDOWN_FILES`)**: `README.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/README.md`, `.github/skills/README.md`, `.github/instructions/README.md`, `.github/agents/workflows.md`, `.github/agents/workflows/*.md`, `docs/README.md`, `docs/repo-map.md`, `docs/architecture/*.md`, `docs/guides/*.md` e `tests/README.md`.
- **Exclusão Explícita de Históricos (`EXCLUDED_HISTORICAL_PATHS`)**: `docs/plans/**`, `CHANGELOG.md` e `docs/adr/**` são estritamente excluídos para preservar o registro histórico imutável e evitar falsos positivos.
- **Validação Sintática de Blocos `mermaid`**: Verifica fechamento paritário de fences (````mermaid` ... `````), cabeçalho válido (`flowchart`/`graph`/`sequenceDiagram`/`stateDiagram-v2`) e paridade de colchetes `[]`, chaves `{}`, parênteses `()` e aspas `"` nos nós inseridos.

## 7. Estratégia de Rollback Completa (Ordem Inversa: Onda 4 -> Onda 3 -> Onda 2 -> Onda 1)

1. **Reverter Onda 4 (remover arquivo novo untracked/tracked)**: `git rm -f --ignore-unmatch tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py` seguido de `rm -f tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py`.
2. **Reverter Onda 3 (remover arquivos novos untracked/tracked de `tools/governance_sync`)**: `git rm -f --ignore-unmatch tools/governance_sync/sync_docs_counts_and_mermaid.py tools/governance_sync/__main__.py tools/governance_sync/README.md` seguido de `rm -f tools/governance_sync/sync_docs_counts_and_mermaid.py tools/governance_sync/__main__.py tools/governance_sync/README.md`.
3. **Reverter Onda 2 (restaurar agents e skill existentes)**: `git checkout -- .github/agents/governance-factory.agent.md .github/agents/governance-maintainer.agent.md .github/skills/governance-factory-patterns/SKILL.md`.
4. **Reverter Onda 1 (restaurar documentação viva e Mermaid)**: `git checkout -- README.md CLAUDE.md .github/copilot-instructions.md .github/agents/README.md .github/skills/README.md .github/instructions/README.md .github/agents/workflows.md .github/agents/workflows/ docs/README.md docs/repo-map.md docs/architecture/ docs/guides/ tests/README.md`.

## 8. Critérios de Aceite

- [x] **CA-01**: `python -m tools.governance_sync.sync_docs_counts_and_mermaid --check` e `python -m tools.governance_sync --check` retornam exit code 0 reutilizando `create_sync_parser`, `SyncOptions` e `SyncReport` de `tools/governance_sync/core.py`.
- [x] **CA-02**: Os 10 arquivos de `R064_PRE_HITL_WORKFLOW_MERMAID_FILES` contêm `@plan-critic` antes do Gate HITL (`ask_questions`) em blocos `mermaid` com fences, colchetes, parênteses, chaves e aspas 100% balanceados.
- [x] **CA-03**: Documentos vivos monitorados refletem **63** `*.agent.md` (31 raiz + 32 stacks), **39** entradas em `catalog.yaml` raiz, **39** nós na chave `nos:` de `routing-graph.yaml` (excluindo `workflows:` e `arestas:`, substituindo `42 nós`), **81** skills (**15** Tier 1, **65** Tier 2, **1** Tier 3), **6** instructions na raiz de `.github/instructions/` (excluindo `local/` por R-043) e **10** workflows (derivados dinamicamente em runtime sem hardcode).
- [x] **CA-04**: Exclusão estrita de `docs/plans/**`, `CHANGELOG.md` e `docs/adr/**` preservada.
- [x] **CA-05**: `pytest tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py -q` 100% verde após Ondas 1–3.

## Checklist

- [x] Artefato(s) alvo lido(s) integralmente antes da edição
- [x] Invariantes de escopo e não-escopo preservadas
- [x] Sincronização com `catalog.yaml` / `README.md` / `routing-graph.yaml` mapeada
- [x] Testes de governança existentes continuam passando
- [x] Se novo teste foi proposto, portão R-055 (Q1, Q2, Q3) respondido
- [x] Estratégia de rollback reversa (Onda 4 -> Onda 1) com remoção de arquivos untracked validada

## 9. Rastreabilidade de Resolução dos Achados do `@plan-critic` (Rodadas 1/2 e 2/2)

### 9.1. Achados da Rodada 1/2 (F1..F6)

| ID | Severidade | Achado da Rodada 1/2 | Resolução Aplicada no Plano |
|---|---|---|---|
| **F1** | `HIGH` | Ambiguidade aritmética entre **63** `*.agent.md`, **39** entradas no `catalog.yaml` raiz e `42 nós` em `routing-graph.yaml`. | Seção 1.1 documenta a equação canônica exata (**63** físicos = 31 raiz + 32 stacks; **39** no catálogo raiz; **39** nós na chave `nos:` de `routing-graph.yaml`). |
| **F2** | `HIGH` | Indefinição de quais workflows recebem o nó `@plan-critic` no Mermaid. | Seção 2.1 traz tabela determinística dos **12 arquivos** (**10** com inserção obrigatória de `@plan-critic` e **2** isenções justificadas). |
| **F3** | `MEDIUM` | Risco de falsos positivos em históricos (`docs/plans/**`, `CHANGELOG.md`, `docs/adr/**`). | Seção 6 define `MONITORED_LIVE_MARKDOWN_FILES` e `EXCLUDED_HISTORICAL_PATHS` explícitos. |
| **F4** | `MEDIUM` | Ausência de validação sintática dos blocos `mermaid`. | Seções 2.2 e 6 exigem validação de fences, cabeçalhos e balanceamento de delimitadores. |
| **F5** | `MEDIUM` | Portão R-055 (Q1, Q2, Q3) ausente para o novo arquivo de teste. | Seção 4 documenta as respostas formais a Q1, Q2 e Q3 da R-055. |
| **F6** | `LOW` | Rollback sem ordem reversa entre ondas nem limpeza de untracked. | Seção 7 e Checklist especificam rollback reverso (Onda 4 -> Onda 1) com remoção de arquivos untracked. |

### 9.2. Achados da Rodada 2/2 (R2-1..R2-4)

| ID | Severidade | Achado Factual da Rodada 2/2 | Resolução Aplicada no Plano |
|---|---|---|---|
| **R2-1** | `MEDIUM` | Chave de nós em `.github/agents/routing-graph.yaml` referenciada como `nodes:` em vez de `nos:` (**39** itens `- id:`, excluindo `workflows:` e `arestas:`). | Corrigido na Seção 1.1 e CA-03 para usar a chave real `nos:` (`len(yaml.safe_load(routing_graph)["nos"]) == 39`). |
| **R2-2** | `MEDIUM` | Contagem de skills referenciava `79` em vez de **81** skills (**15** Tier 1, **65** Tier 2, **1** Tier 3) em `.github/skills/.index.json` e **81** `.github/skills/*/SKILL.md`. | Substituído por **81** (**15** Tier 1, **65** Tier 2, **1** Tier 3) na Seção 1.1 e CA-03, explicitando derivação dinâmica em runtime sem hardcode. |
| **R2-3** | `MEDIUM` | Contagem de instructions referenciava `17` em vez dos **6** adapters genéricos na raiz de `.github/instructions/` (excluindo `local/`, gitignored por R-043). | Substituído por **6** na Seção 1.1 e CA-03, com glob não-recursivo `.github/instructions/*.instructions.md` (excluindo `local/`). |
| **R2-4** | `LOW` | Redundância em `allowed_files` pelo glob `tools/governance_sync/**` junto aos caminhos explícitos. | Removido `tools/governance_sync/**` e mantidos apenas os 4 caminhos explícitos (`__init__.py`, `__main__.py`, `sync_docs_counts_and_mermaid.py`, `README.md`). |

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Agente Revisor**: `@plan-critic`
- **Rodadas Executadas**: `2/2` (Rodada 1/2: 6 achados estruturais `F1..F6` saneados; Rodada 2/2: 4 ajustes factuais `R2-1..R2-4` saneados)
- **Veredito Final**: `APROVADO_COM_RESSALVAS` (ressalvas factuais R2-1..R2-4 integralmente incorporadas antes do Gate HITL humano)
- **Checklist de Conformidade Pré-HITL (R-064)**:
  - Frontmatter R-064 preservado com `status: DRAFT`, `approved: false` e `author: "@agent-auditor"` aguardando HITL humano.
  - `allowed_files` sem glob redundante em `tools/governance_sync/`.
  - Fatos SSoT verificados: chave `nos:` com **39** nós em `routing-graph.yaml`; **81** skills (**15** Tier 1, **65** Tier 2, **1** Tier 3) em `.github/skills/.index.json` e `.github/skills/*/SKILL.md`; **6** instructions genéricas na raiz de `.github/instructions/*.instructions.md` (excluindo `local/` por R-043); derivação 100% dinâmica em runtime sem hardcode.
