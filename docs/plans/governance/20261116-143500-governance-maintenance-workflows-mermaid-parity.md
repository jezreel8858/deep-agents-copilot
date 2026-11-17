---
plan_id: "20261116-143500-governance-maintenance-workflows-mermaid-parity"
plan_type: "governance"
title: "Paridade Estrutural dos Diagramas Mermaid dos 10 Workflows Canônicos e Invariantes (R-064/R-065/5a/5b)"
status: "APPROVED"
approved: true
author: "@agent-auditor"
created_at: "2026-11-16"
updated_at: "2026-11-16"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
tier: "governance"
reversibility_tier: "T1"
blast_radius: "medium"
related-planning-doc: "N/A — plano raiz de governança"
allowed_files:
  - ".github/prompts/plan-lessons-harvester.prompt.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md"
  - ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
  - ".github/agents/workflows/workflow-bug-fix.md"
  - ".github/agents/workflows/workflow-dependency-vulnerability-remediation.md"
  - ".github/agents/workflows/workflow-feature-development.md"
  - ".github/agents/workflows/workflow-framework-migration.md"
  - ".github/agents/workflows/workflow-governance-maintenance.md"
  - ".github/agents/workflows/workflow-prompt-synthesis.md"
  - ".github/agents/workflows/workflow-refactoring.md"
  - ".github/agents/workflows/workflow-release-readiness.md"
  - ".github/agents/workflows/workflow-technical-analysis.md"
  - ".github/agents/workflows/workflow-ui-layout.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
rollback_plan: "git restore .github/agents/workflows/workflow-bug-fix.md .github/agents/workflows/workflow-dependency-vulnerability-remediation.md .github/agents/workflows/workflow-feature-development.md .github/agents/workflows/workflow-framework-migration.md .github/agents/workflows/workflow-governance-maintenance.md .github/agents/workflows/workflow-prompt-synthesis.md .github/agents/workflows/workflow-refactoring.md .github/agents/workflows/workflow-release-readiness.md .github/agents/workflows/workflow-technical-analysis.md .github/agents/workflows/workflow-ui-layout.md .github/agents/workflows/invariantes-e-protocolos.md .github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md .github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md .github/agents/governance-maintainer.agent.md .github/prompts/plan-lessons-harvester.prompt.md"
review_verdict: "PASS_WITH_NITS"
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: "PASS"
session_id: "sess-20261116-plan-lessons-harvester"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-workflows-mermaid-audit-01"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 0
  minors: 1
  nits: 2
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
lessons_extracted: true
lessons_applied_to: []
lessons_at: "2026-11-16"
---

# Plano de Manutenção de Governança — Paridade Estrutural dos Diagramas Mermaid nos 10 Workflows Canônicos e Invariantes (R-064 / R-065 / 5a / 5b)

## 1. Contexto, Diagnóstico e Grounding Físico (C1)

A auditoria sistêmica conduzida pelo `@agent-auditor` em `WORKFLOW-GOVERNANCE-MAINTENANCE` identificou deriva estrutural entre o texto normativo atualizado pelas regras **R-064** (Materialização Universal de Planos por `@docs-engineer`, Duplo Gate 1 + Gate 2 e Revisão Cética por `@plan-critic` com teto de rodadas e `ESCALATED_HITL`) e **R-065** (Revisão de Conformidade Pós-Execução `5b` em `REVIEW_PENDING` com `motivo: "revisao_conformidade_pos_execucao"`) e os diagramas ```mermaid``` presentes nos 10 workflows canônicos em `.github/agents/workflows/workflow-*.md` e em `.github/agents/workflows/invariantes-e-protocolos.md`.

Enquanto o texto das etapas de cada workflow já descreve detalhadamente o ciclo `planejador Read-Only -> @docs-engineer (DRAFT) -> @plan-critic (APPROVED | NEEDS_REVISION <= 2x/3x | ESCALATED_HITL) -> Gate HITL (ask_questions) -> Execução -> Subetapa 5a (Testes/Quality Gate) -> Subetapa 5b (Conformance Review via @agent-router)`, os blocos Mermaid permaneceram em versões simplificadas anteriores, gerando ambiguidade visual e até mesmo um bypass Fail-Closed visual na rota `Factory` de `workflow-governance-maintenance.md`.

### 1.1. Inventário de Grounding Físico (Bytes, Linhas e Intervalos Mermaid Reais em Disco)

A tabela a seguir consolida a medição física exata (`fs.statSync` / contagem de linhas e intervalos `L<início>–L<fim>` dos blocos ```mermaid```) dos 11 arquivos Markdown de governança no escopo deste plano e do arquivo de teste Python vinculado ao plano-filho Q3 (`docs/plans/implementation/20261116-143600-governance-maintenance-workflows-mermaid-sensor-q3.md`):

| # | Caminho do Arquivo | Tamanho Real (Bytes) | Linhas Reais | Intervalo(s) Mermaid | Tarefa / Agrupamento | Diagnóstico de Lacunas no Diagrama Mermaid |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| 1 | `.github/agents/workflows/workflow-bug-fix.md` | 24797 B | 173 | L16–L63 | T2 (Execução Mutativa: Gate 1 + Gate 2 + 5b) | Ausência de nó @docs-engineer explícito no Gate 1/Gate 2, ramificação ESCALATED_HITL de @plan-critic e nós 5a/5b (REVIEW_PENDING / revisao_conformidade_pos_execucao) |
| 2 | `.github/agents/workflows/workflow-dependency-vulnerability-remediation.md` | 8846 B | 83 | L12–L31 | T2 (Execução Mutativa: Gate 1 + Gate 2 + 5b) | Ausência de @docs-engineer explícito antes de @plan-critic, ramificação ESCALATED_HITL e sub-etapas 5a/5b (@security-reviewer + @code-review) |
| 3 | `.github/agents/workflows/workflow-feature-development.md` | 14983 B | 118 | L12–L48 | T2 (Execução Mutativa: Gate 1 + Gate 2 + 5b) | Ausência de @docs-engineer explícito antes de @plan-critic, ramificação ESCALATED_HITL e distinção visual entre 5a (Quality Gate) e 5b (Conformance Review) |
| 4 | `.github/agents/workflows/workflow-framework-migration.md` | 36349 B | 215 | L17–L47 | T2 (Execução Mutativa: Gate 1 + Gate 2 + 5b) | Ausência de @docs-engineer explícito nos Gates 1 e 2, ramificação ESCALATED_HITL e sub-etapas 5a/5b pós-execução |
| 5 | `.github/agents/workflows/workflow-governance-maintenance.md` | 13752 B | 107 | L12–L41 | T1 (Governança Meta-Agente) | Achados G1..G12: bypass Fail-Closed na rota Factory sem @plan-critic/HITL, @docs-engineer fundido com @governance-maintainer e rotulado (Read-Only), ausência de loop NEEDS_REVISION/ESCALATED_HITL, ausência de bifurcação Q3 (@python-router) e ausência de 5a/5b (@agent-auditor) + colisão 4b/5b |
| 6 | `.github/agents/workflows/workflow-prompt-synthesis.md` | 10563 B | 90 | L12–L32 | T3 (Analítico / Isenção Canônica) | Isento de @plan-critic (WORKFLOW_MERMAID_EXEMPTIONS), mas diagrama Mermaid pode explicitar os 3 Tiers de Confirmação Adaptativa (R-041: Baixo Risco / Alto Risco / Destrutivo) e o Handoff de Derivação |
| 7 | `.github/agents/workflows/workflow-refactoring.md` | 17677 B | 123 | L15–L45 | T2 (Execução Mutativa: Gate 1 + Gate 2 + 5b) | Ausência de @docs-engineer explícito nos Gates 1 e 2, ramificação ESCALATED_HITL e separação 5a/5b com retorno via @agent-router |
| 8 | `.github/agents/workflows/workflow-release-readiness.md` | 5925 B | 62 | L12–L32 | T3 (Analítico / Gate de Release) | Ausência de @docs-engineer como materializador DRAFT do parecer/plano antes de @plan-critic, ramificação ESCALATED_HITL e Gate HITL explícito |
| 9 | `.github/agents/workflows/workflow-technical-analysis.md` | 8470 B | 83 | L12–L38 | T3 (Analítico / Consultivo) | Ausência de @docs-engineer materializador DRAFT antes de @plan-critic, ramificação ESCALATED_HITL e Gate HITL explícito |
| 10 | `.github/agents/workflows/workflow-ui-layout.md` | 4214 B | 38 | L13–L21 | T3 (UI/Layout Mutativo) | Ausência de @docs-engineer materializador DRAFT antes de @plan-critic, ramificação ESCALATED_HITL, Gate 2 e sub-etapas 5a/5b (@code-review) |
| 11 | `.github/agents/workflows/invariantes-e-protocolos.md` | 61739 B | 503 | L261–L267 | T3 (Invariantes Transversais) | Diagrama mestre de recuperação e ciclo de vida não explicita a materialização R-064 via @docs-engineer nem a transição 5a -> 5b (REVIEW_PENDING -> Conformance Review) |
| 12 | `tests/governance_audit/test_workflows_parity_and_gates.py` | 15182 B | 259 | N/A (arquivo Python de teste) | T4 (Sensor Python Q3 — Plano-Filho) | Valida marcadores R-064/R-065/5b apenas no corpo textual Markdown, sem inspecionar o conteúdo interno dos blocos ```mermaid``` dos workflows |

### 1.2. Detalhamento dos Achados G1–G12 em `workflow-governance-maintenance.md` (Alvo da Tarefa T1)

1. **G1 (Bypass Fail-Closed na rota `Factory`)**: A aresta `Type -->|Factory| Factory[@governance-factory]` segue direto para `Sync[Executar tools/governance_sync.py --write]` sem passar por `@docs-engineer` (DRAFT), `@plan-critic` e Gate HITL (`ask_questions`), contrariando o passo 3 do texto (L49–L61) e a regra Fail-Closed.
2. **G2 (Fusão indevida `@docs-engineer / @governance-maintainer`)**: O nó `Maint[Etapa 2: @docs-engineer / @governance-maintainer — Plano em docs/plans/governance/]` mistura dois agentes que atuam em etapas distintas (Etapa 2 = `@docs-engineer` para persistência DRAFT; Etapa 5 = `@governance-maintainer` para mutação pós-HITL).
3. **G3 (Rótulo incorreto `(Read-Only)` em `@docs-engineer`)**: Na Etapa 6 (L128), o texto rotula `@docs-engineer (Read-Only)`, contradizendo o contrato canônico de `@docs-engineer` como único materializador de arquivos `.md` (R-064).
4. **G4 (Ausência de aresta de retorno `NEEDS_REVISION` e `ESCALATED_HITL`)**: O nó `Critic[@plan-critic: Revisão Cética]` possui apenas uma seta linear para `HITL`, omitindo o loop `NEEDS_REVISION (máx 2x)` e o desvio `ESCALATED_HITL -> HITL`.
5. **G5 (Ausência da bifurcação Q3 para `*.py`)**: O diagrama não representa a delegação obrigatória para `@python-router -> @python-test-engineer / @python-developer` quando a neutralização na fonte (Q3) exige alterar scripts ou testes Python (como `tests/governance_audit/**`).
6. **G6 (Ausência de separação visual entre `5a` e `5b`)**: O diagrama termina em `Sync -> Validate[Validar: pytest tests/governance_audit/ -q]`, omitindo o comando `python -m tools.governance_sync --check` na Subetapa `5a` e toda a Subetapa `5b` (`REVIEW_PENDING` -> `@agent-router` -> `@agent-auditor` -> `PASS | PASS_WITH_WARNINGS | FAIL`).
7. **G7 (Ausência do loop de reprovação `FAIL` na Subetapa `5b`)**: O diagrama não mostra o retorno de `@agent-auditor` (`FAIL`) via `@agent-router` para `@governance-maintainer` / `@governance-factory` (máx. 2 rodadas antes de `ESCALATED_HITL`).
8. **G8 (Colisão de numeração `4b / 5b` na seção de Autofix)**: A seção `### 4b / 5b. Protocolo de Autofix Bounded (Circuit Breaker — Máx 2 Tentativas)` (L111) colide diretamente com a `### Subetapa 5b — Revisão de Conformidade Pós-Execução` (L92), devendo ser renomeada para `### 5a-CB. Protocolo de Autofix Bounded na Validação 5a (Circuit Breaker — Máx 2 Tentativas)`.
9. **G9 (Ausência do nó `@docs-engineer` na Etapa 6 — Curadoria)**: O diagrama omite a etapa opcional de curadoria documental pós-validação (`Etapa 6: @docs-engineer / @governance-maintainer`).
10. **G10 (Omissão do gatilho `motivo: "plano_materializacao_pendente"`)**: A transição entre `@agent-auditor` (Etapa 1) e `@docs-engineer` (Etapa 2) no diagrama não explicita o handoff de materialização R-064.
11. **G11 (Omissão do gatilho `motivo: "revisao_conformidade_pos_execucao"`)**: A transição `5a -> 5b` no diagrama não explicita o status `REVIEW_PENDING` nem o motivo canônico de handoff R-065.
12. **G12 (Omissão da promoção de status do plano `APPROVED -> COMPLETED`)**: O diagrama não indica que o fechamento em `COMPLETED` somente ocorre após o veredito `PASS` ou `PASS_WITH_WARNINGS` na Subetapa `5b`.

---

## 2. Causa-Raiz (RCA Q0), Análise de Escape e Portão de Reúso Sistêmico (R-055)

- **Q0 — Origem Upstream da Deriva**: As atualizações normativas **R-064** (Materialização Universal de Planos em `docs/plans/<tipo>/` por `@docs-engineer`, Duplo Gate 1 + Gate 2 e Revisão Cética `@plan-critic` com `ESCALATED_HITL`) e **R-065** (Sub-etapas pós-execução `5a` e `5b` com `REVIEW_PENDING` e `motivo: "revisao_conformidade_pos_execucao"`) foram aplicadas ao corpo textual dos workflows sem atualização simultânea de todos os nós e transições internas dos blocos ```mermaid```.
- **Análise de Escape (`T2-RCA`)**:
  1. `tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py` (linhas 88–108, `test_workflow_mermaid_diagrams_include_plan_critic_and_valid_syntax`) verifica apenas a presença da substring `plan-critic` e sintaxe básica nos blocos Mermaid dos workflows fora de `WORKFLOW_MERMAID_EXEMPTIONS`.
  2. `tests/governance_audit/test_workflows_parity_and_gates.py` (15182 bytes, 259 linhas) valida a presença de `@docs-engineer`, `ESCALATED_HITL`, `Gate 2`, `REVIEW_PENDING` e `revisao_conformidade_pos_execucao` no arquivo Markdown global, mas **não isola o bloco ```mermaid```**, permitindo que o teste passe mesmo quando esses nós existem apenas na prosa e estão ausentes no diagrama.
- **Portão de Reúso Sistêmico (R-055 — Justificativa de Não-Criação de Novo Script)**: Não será criado nenhum script em `tools/` nem novo arquivo de teste isolado. O sensor existente `tests/governance_audit/test_workflows_parity_and_gates.py` já centraliza as invariantes de paridade dos 10 workflows canônicos e será estendido in-place (via Tarefa T4 / Plano-Filho Q3).
- **Neutralização na Fonte (Q3 / Tarefa T4)**: Como a governança proíbe agentes de manutenção Markdown (`@governance-maintainer`) de editar arquivos `*.py` (fronteira territorial C3), a evolução do sensor `tests/governance_audit/test_workflows_parity_and_gates.py` é formalmente desmembrada no plano-filho vinculado `docs/plans/implementation/20261116-143600-governance-maintenance-workflows-mermaid-sensor-q3.md` para execução via `@python-router` -> `@python-test-engineer`.

---

## 3. Decomposição de Tarefas (`[GOVERNANCE_TASKS]`)

### Tarefa T1 — Correção Integral de `workflow-governance-maintenance.md` (Achados G1–G12)
- **Agente Executor**: `@governance-maintainer` (Etapa 5 pós-aprovação HITL).
- **Arquivo-Alvo**: `.github/agents/workflows/workflow-governance-maintenance.md` (13752 B, 107 linhas, Mermaid atual em L12–L41).
- **Ações Determinísticas**:
  1. Reescrever o bloco ```mermaid``` para representar fielmente as Etapas 1 a 6:
     - Etapa 1: `@agent-auditor` (Diagnóstico Read-Only + RCA Q0/Q3) em ambas as rotas (`Maint` e `Factory`), emitindo `motivo: "plano_materializacao_pendente"`.
     - Etapa 2: `@docs-engineer` materializa `DRAFT` em `docs/plans/governance/` (e plano-filho em `docs/plans/implementation/` quando houver Q3 Python).
     - Etapa 3: `@plan-critic` com ramificações explícitas `APPROVED`, `NEEDS_REVISION (<= 2x) -> @agent-auditor / @docs-engineer` e `ESCALATED_HITL -> Gate HITL`.
     - Etapa 4: Gate HITL (`ask_questions` — aprovação humana obrigatória do plano).
     - Etapa 5: Bifurcação explícita entre mutação Markdown/YAML (`@governance-maintainer` ou `@governance-factory` + `tools/governance_sync.py --write`) e delegação Q3 Python (`@python-router -> @python-test-engineer / @python-developer`).
     - Subetapa `5a`: `pytest tests/governance_audit/ -q` + `python -m tools.governance_sync --check` (com Circuit Breaker `5a-CB` máx. 2x).
     - Subetapa `5b`: Transição para `REVIEW_PENDING` (`motivo: "revisao_conformidade_pos_execucao"`) via `@agent-router` -> `@agent-auditor` (`PASS | PASS_WITH_WARNINGS -> Etapa 6 / COMPLETED`; `FAIL (<= 2x) -> Etapa 5`).
     - Etapa 6: Curadoria opcional via `@docs-engineer` / `@governance-maintainer` e promoção do plano para `COMPLETED`.
  2. Renomear o subtítulo `### 4b / 5b. Protocolo de Autofix Bounded` (L111) para `### 5a-CB. Protocolo de Autofix Bounded na Validação 5a (Circuit Breaker — Máx 2 Tentativas)`.
  3. Corrigir na L128 o rótulo `@docs-engineer (Read-Only)` para `@docs-engineer (Modo Curate/Author — exclusivo para .md)`.

### Tarefa T2 — Sincronização Mermaid nos 5 Workflows Mutativos com Duplo Gate (Gate 1 + Gate 2 + 5a/5b)
- **Agente Executor**: `@governance-maintainer`.
- **Arquivos-Alvo**:
  1. `.github/agents/workflows/workflow-bug-fix.md` (24797 B, 173 linhas, Mermaid L16–L63)
  2. `.github/agents/workflows/workflow-dependency-vulnerability-remediation.md` (8846 B, 83 linhas, Mermaid L12–L31)
  3. `.github/agents/workflows/workflow-feature-development.md` (14983 B, 118 linhas, Mermaid L12–L48)
  4. `.github/agents/workflows/workflow-framework-migration.md` (36349 B, 215 linhas, Mermaid L17–L47)
  5. `.github/agents/workflows/workflow-refactoring.md` (17677 B, 123 linhas, Mermaid L15–L45)
- **Ações Determinísticas**:
  - Atualizar o bloco ```mermaid``` de cada um dos 5 arquivos para conter explicitamente os nós e rótulos:
    - `@docs-engineer` (materialização física DRAFT em `docs/plans/<tipo>/` no Gate 1 e `docs/plans/implementation/` no Gate 2);
    - `@plan-critic` com loop `NEEDS_REVISION` e desvio `ESCALATED_HITL`;
    - `HITL` / `ask_questions` nos Gates 1 e 2;
    - `5a` (Testes / Quality Gate) e `5b` (`REVIEW_PENDING` / `revisao_conformidade_pos_execucao` via `@agent-router` para `@code-review` / `@security-reviewer`, com retorno em caso de `FAIL` e promoção a `COMPLETED` em `PASS`).

### Tarefa T3 — Sincronização Mermaid nos 4 Workflows Analíticos/UI e em `invariantes-e-protocolos.md`
- **Agente Executor**: `@governance-maintainer`.
- **Arquivos-Alvo**:
  1. `.github/agents/workflows/workflow-technical-analysis.md` (8470 B, 83 linhas, Mermaid L12–L38)
  2. `.github/agents/workflows/workflow-release-readiness.md` (5925 B, 62 linhas, Mermaid L12–L32)
  3. `.github/agents/workflows/workflow-ui-layout.md` (4214 B, 38 linhas, Mermaid L13–L21)
  4. `.github/agents/workflows/workflow-prompt-synthesis.md` (10563 B, 90 linhas, Mermaid L12–L32)
  5. `.github/agents/workflows/invariantes-e-protocolos.md` (61739 B, 503 linhas, Mermaid L261–L267)
- **Ações Determinísticas**:
  - Em `workflow-technical-analysis.md` e `workflow-release-readiness.md`: incluir no bloco Mermaid a persistência DRAFT via `@docs-engineer`, a revisão `@plan-critic` (com `NEEDS_REVISION` e `ESCALATED_HITL`) e o Gate `HITL` (`ask_questions`).
  - Em `workflow-ui-layout.md`: incluir no bloco Mermaid `@docs-engineer` (DRAFT em `docs/plans/architecture/` e `docs/plans/implementation/`), `@plan-critic` (`ESCALATED_HITL`), `HITL` e sub-etapas `5a`/`5b` (`REVIEW_PENDING` -> `@code-review`).
  - Em `workflow-prompt-synthesis.md`: preservar a isenção canônica de `@plan-critic` (`WORKFLOW_MERMAID_EXEMPTIONS`), enriquecendo o bloco Mermaid com os 3 Tiers de Confirmação Adaptativa (R-041: Baixo Risco / Alto Risco / Destrutivo) e o Handoff de Derivação para o router de domínio.
  - Em `invariantes-e-protocolos.md`: atualizar o diagrama mestre (L261–L267) para explicitar a materialização R-064 via `@docs-engineer`, o desvio `ESCALATED_HITL` e a transição pós-execução `5a -> 5b (REVIEW_PENDING -> Conformance Review -> COMPLETED)`.

### Tarefa T4 — Evolução do Sensor de Paridade Mermaid em Python (Delegação Q3)
- **Agente Executor**: `@python-router` -> `@python-test-engineer`.
- **Plano-Filho Vinculado**: `docs/plans/implementation/20261116-143600-governance-maintenance-workflows-mermaid-sensor-q3.md`.
- **Arquivo-Alvo (exclusivo do plano-filho)**: `tests/governance_audit/test_workflows_parity_and_gates.py` (15182 B, 259 linhas).
- **Ação Resumida**: Adicionar teste parametrizado que extrai o bloco ```mermaid``` de cada workflow canônico e valida a presença obrigatória dos marcadores de estado (`docs-engineer`, `plan-critic`, `ESCALATED_HITL`, `HITL` e `5b` nos workflows mutativos).

---

## 4. Alternativas Rejeitadas (C2)

1. **Alternativa A (Rejeitada) — Remover os diagramas Mermaid dos workflows e manter apenas o texto normativo**:
   - *Consequência prática*: Eliminaria imediatamente a deriva entre diagrama e prosa em todos os 11 arquivos.
   - *Trade-off / Motivo da rejeição*: Quebraria o teste de invariantes `test_workflow_mermaid_diagrams_include_plan_critic_and_valid_syntax` em `tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py` e degradaria a legibilidade arquitetural dos fluxos de orquestração multi-agente.
2. **Alternativa B (Rejeitada) — Gerar diagramas Mermaid dinamicamente via script Python em tempo de build substituindo seções inteiras dos workflows**:
   - *Consequência prática*: Automatizaria a renderização dos blocos Mermaid a partir de um manifesto YAML.
   - *Trade-off / Motivo da rejeição*: Violaría o Portão de Reúso Sistêmico (R-055) ao introduzir um novo gerador em `tools/` com alto custo de manutenção para apenas 11 diagramas estáticos, além de perder nuances específicas de cada domínio (como rotas `Maint` vs `Factory` ou auditoria CVE/PII).

---

## 5. Blast Radius e Análise de Impacto (C2)

- **Escopo Direto**: 11 arquivos Markdown em `.github/agents/workflows/*.md` (plano pai) e 1 arquivo de teste em `tests/governance_audit/test_workflows_parity_and_gates.py` (plano-filho Q3).
- **Impacto em Runtime e Catálogo**: Zero impacto em contratos JSON/YAML de agentes (`.github/agents/catalog.yaml`), zero alteração no número de agentes (32), skills (50) ou workflows (10).
- **Risco de Regressão**: Baixo (`reversibility_tier: "T1"`, `blast_radius: "medium"`). O único risco técnico é introduzir erro de sintaxe Mermaid (parênteses ou colchetes não escapados em rótulos de nós), que é mitigado imediatamente pelos sensores `test_markdown_ssot_counts_and_mermaid_sync.py` e `test_workflows_parity_and_gates.py`.

---

## 6. Estratégia de Rollback (C2)

Caso qualquer validação em `5a` ou revisão de conformidade em `5b` aponte regressão documental ou falha de parser Mermaid não resolvida dentro do teto de autofix bounded (2 tentativas), o rollback completo e atômico dos 11 arquivos de workflow é executado sem afetar os planos persistidos em `docs/plans/**`:

```bash
git restore .github/agents/workflows/workflow-bug-fix.md .github/agents/workflows/workflow-dependency-vulnerability-remediation.md .github/agents/workflows/workflow-feature-development.md .github/agents/workflows/workflow-framework-migration.md .github/agents/workflows/workflow-governance-maintenance.md .github/agents/workflows/workflow-prompt-synthesis.md .github/agents/workflows/workflow-refactoring.md .github/agents/workflows/workflow-release-readiness.md .github/agents/workflows/workflow-technical-analysis.md .github/agents/workflows/workflow-ui-layout.md .github/agents/workflows/invariantes-e-protocolos.md
```

*(Em estrita observância à restrição C2, é terminantemente proibido executar `git clean -f` ou `rm -f` sobre `docs/plans/**`).*

---

## 7. Teste de Regressão, Verificação Executável e Cenários Gherkin (C4)

### 7.1. Cenários Comportamentais (Gherkin)

```gherkin
Funcionalidade: Paridade Estrutural entre Diagramas Mermaid e Texto Normativo R-064/R-065 nos Workflows

  Cenário: Diagrama Mermaid de workflow-governance-maintenance.md impede bypass na rota Factory e exibe 5a/5b
    Dado o arquivo ".github/agents/workflows/workflow-governance-maintenance.md"
    Quando o bloco "mermaid" é extraído e inspecionado
    Então tanto a rota "Maint" quanto a rota "Factory" convergem para "@docs-engineer" (DRAFT), "@plan-critic" e Gate "HITL" antes de qualquer mutação
    E o bloco "mermaid" contém explicitamente os nós "NEEDS_REVISION", "ESCALATED_HITL", "@python-router", "5a" e "5b" ("@agent-auditor")
    E não existe colisão de numeração "4b / 5b" no corpo do arquivo

  Cenário: Diagramas Mermaid dos workflows mutativos (T2 e UI Layout) refletem R-064 e R-065
    Dados os workflows mutativos "workflow-bug-fix.md", "workflow-dependency-vulnerability-remediation.md", "workflow-feature-development.md", "workflow-framework-migration.md", "workflow-refactoring.md" e "workflow-ui-layout.md"
    Quando cada bloco "mermaid" é extraído
    Então todos contêm os marcadores "docs-engineer", "plan-critic", "ESCALATED_HITL", "HITL" e "5b"
```

### 7.2. Comandos de Verificação Executável (Subetapa 5a)

1. **Verificação rápida via Node.js (`ctx_execute`) dos blocos Mermaid nos 11 arquivos**:
   ```javascript
   const fs = require('fs');
   const mutative = [
     'workflow-bug-fix.md',
     'workflow-dependency-vulnerability-remediation.md',
     'workflow-feature-development.md',
     'workflow-framework-migration.md',
     'workflow-governance-maintenance.md',
     'workflow-refactoring.md',
     'workflow-ui-layout.md'
   ];
   for (const f of mutative) {
     const text = fs.readFileSync('.github/agents/workflows/' + f, 'utf8');
     const m = text.match(/```mermaid([\s\S]*?)```/);
     if (!m) throw new Error('Bloco mermaid ausente em ' + f);
     for (const token of ['docs-engineer', 'plan-critic', 'ESCALATED_HITL', 'HITL', '5b']) {
       if (!m[1].includes(token)) throw new Error(`Token ${token} ausente no Mermaid de ${f}`);
     }
   }
   ```
2. **Suíte de Auditoria de Governança e Sincronização SSOT**:
   ```bash
   pytest tests/governance_audit/test_workflows_parity_and_gates.py tests/governance_audit/test_markdown_ssot_counts_and_mermaid_sync.py -q
   python -m tools.governance_sync --check
   ```

---

## 8. Segurança Agentic e Isolamento Territorial (C7 / C9 / C10 — OWASP ASI01/ASI06, R-043/R-044)

- **Mitigação OWASP ASI01 (Goal Hijacking) e ASI06 (Memory/Context Poisoning)**:
  - A correção do diagrama de `workflow-governance-maintenance.md` elimina a ambiguidade visual que sugeria execução direta de `@governance-factory` e `tools/governance_sync.py --write` sem passar por `@plan-critic` e Gate HITL (`ask_questions`).
  - Todo conteúdo lido de `handoff_summary`, `critic_rubric_gaps` e artefatos em `docs/plans/**` é tratado como dado informativo inerte, nunca como instrução imperativa capaz de contornar o Gate HITL.
- **Isolamento Territorial R-043 / R-044**:
  - Este plano opera exclusivamente sobre a governança global do repositório `deep-agents-copilot` (`.github/agents/workflows/*.md`).
  - Nenhum caminho em `.github/instructions/local/**` ou `*.local.*` é incluído em `allowed_files`, e nenhuma referência a identificadores de projetos externos é utilizada (qualquer alusão genérica a projetos consumidores utiliza o placeholder canônico `[PROJETO-ALVO]`, preservada a **Exceção Única Canônica** apenas para documentos criados diretamente dentro de `<path_externo>/docs/**`).

### Tarefa T0 — Prevenção Estrutural na Origem (Anti-Recorrência)

1. **Pilar 1 (Planejamento/Crítica)**: Regra em `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` (`C2`) e `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` exigindo paridade atômica Prosa ↔ Mermaid sempre que `workflow-*.md` ou `invariantes-e-protocolos.md` constar em `allowed_files`.
2. **Pilar 2 (Execução)**: Invariante normativa em `.github/agents/workflows/invariantes-e-protocolos.md` e `.github/agents/governance-maintainer.agent.md` proibindo mutar etapas textuais de workflows sem atualizar o bloco ```mermaid no mesmo diff.
3. **Pilar 3 (Verificação Contínua Q3)**: Sensor bidirecional em `tests/governance_audit/test_workflows_parity_and_gates.py` (especificado no Plano-Filho `docs/plans/implementation/20261116-143600-governance-maintenance-workflows-mermaid-sensor-q3.md`).
4. **Higienização de Resíduo Anterior**: Ajuste cosmético na L53 (`C1 a C9` → `C1 a C10`) e orçamento de largura da L55 (`<= 200 caracteres`) em `.github/prompts/plan-lessons-harvester.prompt.md`.

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Rodada**: 1 (`review_rounds: 1`)
- **Veredito**: `PASS_WITH_NITS` (`review_tier1: "PASS"`, `blockers: 0`, `majors: 0`, `minors: 1`, `nits: 2`)
- **Resolução dos Apontamentos (Incorporados antes da Execução)**:
  1. **MINOR-01 (Colisão de Nomenclatura `4b`/`5b` em `workflow-governance-maintenance.md`)**: Resolvido renomeando o Circuit Breaker de Autofix da Subetapa `5a` para `5a-CB` (com retorno mediado por `@agent-router`), reservando `5b` exclusivamente para a Revisão de Conformidade Pós-Execução (`REVIEW_PENDING` / `revisao_conformidade_pos_execucao`).
  2. **NIT-01 (Escopo de Blindagem na Origem T0)**: Resolvido adicionando os 4 arquivos da Tarefa T0 (`pre-hitl-skeptical-review-rubric.md`, `planner-preflight-checklist.md`, `governance-maintainer.agent.md` e `plan-lessons-harvester.prompt.md`) em `allowed_files` e `rollback_plan`.
  3. **NIT-02 (Rótulo de `@docs-engineer` e Bifurcação Q3 no Mermaid)**: Resolvido separando `@docs-engineer` (materializador único `DRAFT`, sem rótulo indevido `(Read-Only)`) do executor `@governance-maintainer` e explicitando a bifurcação Q3 (`@python-router` vs `@governance-maintainer`).
