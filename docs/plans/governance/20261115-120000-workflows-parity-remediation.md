---
plan_id: "20261115-120000-workflows-parity-remediation"
plan_type: "governance"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
status: "APPROVED"
approved: true
author: "@agent-auditor"
materialized_by: "@docs-engineer"
created_at: "2026-11-15T12:00:00Z"
updated_at: "2026-11-16T00:00:00Z"
tier: "governance"
approved_by: "user_hitl"
approved_at: "2026-11-16T00:00:00Z"
review_verdict: "PASS_WITH_NITS"
review_rounds: 3
reviewer: "@plan-critic"
review_tier1: "PASS"
allowed_files:
  - "docs/plans/governance/20261115-120000-workflows-parity-remediation.md"
  - ".github/agents/workflows.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - ".github/agents/workflows/workflow-bug-fix.md"
  - ".github/agents/workflows/workflow-refactoring.md"
  - ".github/agents/workflows/workflow-feature-development.md"
  - ".github/agents/workflows/workflow-governance-maintenance.md"
  - ".github/agents/workflows/workflow-dependency-vulnerability-remediation.md"
  - ".github/agents/workflows/workflow-framework-migration.md"
  - ".github/agents/routing-graph.yaml"
  - ".github/skills/governance-factory-patterns/references/workflow-invariants.md"
  - ".github/skills/governance-factory-patterns/SKILL.md"
  - ".github/agents/governance-factory.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/skills/governance-audit-patterns/SKILL.md"
  - "tests/governance_audit/test_workflows_parity_and_gates.py"
lessons_extracted: true
lessons_applied_to: ["@agent-auditor", "plan-conformance-patterns"]
lessons_at: "2026-11-16"
related-planning-doc: "N/A — plano primário de governança"
session_id: "sess-20261115-120000-workflows-parity-remediation"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-trace-20261115-120000-workflows-parity-remediation"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 3
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
---

# Plano de Governança: Remediação de Paridade de Workflows, Gates R-064/R-065 e Sincronia com Routing Graph

## 1. Contexto e Escopo

Este plano de governança foi elaborado a partir do diagnóstico da Etapa 1 (`@agent-auditor`) no âmbito do `WORKFLOW-GOVERNANCE-MAINTENANCE` e materializado fisicamente na Etapa 2 por `@docs-engineer` sob a regra **R-064** (`status: "APPROVED"`, `approved: true`).

O objetivo é eliminar assimetrias documentais e estruturais entre o índice canônico (`.github/agents/workflows.md`), o documento de invariantes (`.github/agents/workflows/invariantes-e-protocolos.md`), os 6 sub-arquivos detalhados de workflows com planos R-064 (`.github/agents/workflows/workflow-*.md`), o grafo executável (`.github/agents/routing-graph.yaml`) e a suíte de testes automatizados de auditoria de governança (`tests/governance_audit/test_workflows_parity_and_gates.py`).

### 1.1 Resumo Executivo dos Achados Cobertos

| ID | Severidade | Alvo Principal | Síntese do Desvio |
| :--- | :--- | :--- | :--- |
| **H1** | `HIGH` | 6 sub-arquivos `workflow-*.md` com plano R-064 | Ausência de menção explícita ao passo de revisão cética pré-HITL pelo `@plan-critic` (Two-Tier Hybrid Gate, ref. `§ 10.7` de `invariantes-e-protocolos.md`) antes do `ask_questions`. |
| **M1** | `MEDIUM` | `workflow-governance-maintenance.md`, `workflows.md`, `invariantes-e-protocolos.md` | Numeração duplicada de `Estado 3` em `workflow-governance-maintenance.md:55-64` e referências desatualizadas ao número de etapas (4 vs 5) em `workflows.md:100` e `invariantes-e-protocolos.md:153-155`. |
| **M2** | `MEDIUM` | `workflows.md`, `workflow-framework-migration.md`, `invariantes-e-protocolos.md` | Divergência na contagem/numeração de etapas de `WORKFLOW-FRAMEWORK-MIGRATION` entre `workflows.md:100`, `workflows.md:113` (Mermaid), `workflows.md:136` (Tabela § 2.1), `workflow-framework-migration.md:109-141` e `invariantes-e-protocolos.md` (§ 6.2). |
| **M3** | `MEDIUM` | `workflows.md`, `invariantes-e-protocolos.md`, 3 sub-arquivos `workflow-*.md` | Ambiguidade na citação de `R-065` em `workflows.md:84, 199` e `invariantes-e-protocolos.md:461` e falta de referência explícita ao Guard de Severidade Arquitetural (R-065) nos estados de `quality_review_loop` de `workflow-refactoring.md`, `workflow-feature-development.md` e `workflow-framework-migration.md`. |
| **M4** | `MEDIUM` | `workflow-framework-migration.md:51-82` | Verificação e substituição de prefixos legados `PLAN-` / `REQ-` em nomes/referências de arquivos de plano pelo formato canônico `<AAAAMMDD-HHMMSS>-<slug>.md` (preservando IDs de requisitos EARS `REQ-01` que não sejam caminhos em `docs/plans/`). |
| **L1** | `LOW` | `routing-graph.yaml:185` | Comentário legado `"Define os 5 workflows operacionais determinísticos..."` defasado frente aos 9 workflows canônicos (+ 3.A auxiliar). |
| **L2** | `LOW` | `workflow-governance-maintenance.md:66-69` | Contagens defasadas (`"17 smells"` / `"60 casos"`) em vez da faixa canônica `Smells 2.1 a 2.34`. |
| **Q3** | `R-055` | `tests/governance_audit/test_workflows_parity_and_gates.py` | Necessidade de testes de regressão em `pytest` cobrindo paridade de estados, Regra 7 da § 1.5, presença de `@plan-critic` nos sub-arquivos e sincronia com `routing-graph.yaml`. |

---

## 2. Diagnóstico Detalhado: Encontrado vs. Proposto

### 2.1 Achado H1 (HIGH) — Explicitação do `@plan-critic` (Two-Tier Hybrid Gate, § 10.7) nos Sub-Arquivos R-064

- **Arquivos afetados**:
  1. `.github/agents/workflows/workflow-bug-fix.md`
  2. `.github/agents/workflows/workflow-refactoring.md`
  3. `.github/agents/workflows/workflow-feature-development.md`
  4. `.github/agents/workflows/workflow-governance-maintenance.md`
  5. `.github/agents/workflows/workflow-dependency-vulnerability-remediation.md`
  6. `.github/agents/workflows/workflow-framework-migration.md`
- **Evidência encontrada nos sub-arquivos**:
  - Os 6 sub-arquivos detalham a materialização física do plano por `@docs-engineer` em `docs/plans/<tipo>/` e o `CHECKPOINT DE APROVAÇÃO HUMANA (R-034 / R-064)` via `ask_questions`, mas omitem a transição intermediária obrigatória de revisão cética pré-HITL pelo `@plan-critic` definida em `invariantes-e-protocolos.md` (`§ 10.7 — Protocolo Universal de Revisão Cética Pré-HITL via @plan-critic (Two-Tier Hybrid Gate)`).
- **Proposta de alteração (Proposto)**:
  - Em cada um dos 6 sub-arquivos acima, inmediatamente antes do `CHECKPOINT DE APROVAÇÃO HUMANA` (Gate 1 e, quando aplicável, Gate 2), explicitar o passo obrigatório de revisão pré-HITL pelo `@plan-critic` (`Two-Tier Hybrid Gate`, ref. `invariantes-e-protocolos.md § 10.7`), declarando que `ask_questions` só é invocado após veredito `PASS` ou `PASS_WITH_WARNINGS` (ou escalonamento após `max_critic_rounds = 2`).

### 2.2 Achado M1 (MEDIUM) — Numeração Duplicada de `Estado 3` em `WORKFLOW-GOVERNANCE-MAINTENANCE` e Paridade de Contagem de Etapas

- **Evidência encontrada (`workflow-governance-maintenance.md:30-75`)**:
```text
L30: 
L31:     Factory --> MaintainerSync["<b>3b. Sincronização Quádrupla SSOT</b><br/>Atualização atômica de catálogos e grafos (R-015)"]
L32:     MaintainerSync --> GateGov["<b>4. Quality Gate de Governança (Tier 1)</b><br/>Validação via pytest: smells, routing e isolamento"]
L33:     Maintainer --> GateGov
L34: 
L35:     GateGov --> CheckGov{"Suíte de Governança<br/>100% verde?"}
L36:     CheckGov -- "Sim" --> EndDone(["✅ Governança Atualizada & Consistente"])
L37:     CheckGov -- "Falha (tentativa N/3)" --> CheckAutoFixCap{"Tentativas<br/>autofix < 3?"}
L38:     CheckAutoFixCap -- "Sim" --> AutoFix["Autocorreção cirúrgica pelo @governance-maintainer"]
L39:     AutoFix --> GateGov
L40:     CheckAutoFixCap -- "Não (teto esgotado)" --> GovEscalate["<b>4b. Escalonamento</b><br/>ask_questions: revisão manual do diff"]
L41: ```
L42: 
L43: #### Cadeia Sequencial e Papéis:
L44: - **Portão de Reúso e Generalização Sistêmica (R-055 — Prioritário & Mandatório)**: Toda demanda de manutenção, revisão, novo padrão ou correção técnica que envolva agents, prompts ou skills DEVE obrigatoriamente respond [...]
L45:   - **Q1 (Impacto Horizontal / Peers)**: *Esta melhoria ou correção se aplica a outros artefatos do mesmo perfil, camada ou família (ex.: outros routers, outros testers, outros advisors)?* Se sim, expandir compulsoriamen [...]
L46:   - **Q2 (Prevenção Futura / Templates)**: *O template canônico em `templates/` (`router-agent.md`, `operational-agent.md`, etc.) reflete essa nova exigência?* Se não, o template correspondente DEVE ser atualizado na mes [...]
L47:   - **Q3 (Blindagem por Teste / Quality Gate — Regra de Fronteira Híbrida com Tríade Python)**: *A suíte determinística em `tests/governance_audit/` já valida essa regra?* Se não, o requisito de teste DEVE ser especifica [...]
L48: - **Protocolo de Avaliação de Pertinência de Importação de Skills (R-067 — Prioritário em Pedidos de Importação Externa)**: Toda solicitação de importação de skill externa aciona compulsoriamente, no Estado 1, a avaliaçã [...]
L49: 1. **Estado 1 — Diagnóstico Read-Only ou Pesquisa Prévia**:
L50:    - *Diagnóstico de Smells & Reúso*: O `@agent-auditor` executa auditoria estática e comportamental contra os smells canônicos de governança e avalia compulsoriamente Q1, Q2 e Q3.
L51:    - *Auditoria de Higiene & Documentação*: O `@repo-hygiene-auditor` audita a saúde do repositório, licença e segurança de versionamento; o `@docs-engineer` mapeia a integridade documental, alinhamento técnico de manuai [...]
L52:    - *Pesquisa Prévia Compulsória (Criação de Artefatos / Stack)*: O `@governance-factory` delega compulsoriamente ao `@deep-search` a investigação de mercado antes de escrever novos prompts, skills ou agents.
L53: 2. **Estado 2 — Materialização Física do Plano R-064 em `docs/plans/governance/` (`status: DRAFT`)**:
L54:    - *Autoria e Persistência Pré-Checkpoint*: O `@agent-auditor` estrutura o plano (`plan_type: "governance"`) e aciona `@docs-engineer` ou `@governance-maintainer` para materializá-lo fisicamente em `docs/plans/governan [...]
L55: 3. **Estado 3 — Checkpoint Humano R-064 (`ask_questions` sobre `plan_ref`)**:
L56:    - Toda manutenção estrutural ou criação de stack exige aprovação humana explícita via `ask_questions` referenciando o `plan_ref` já gravado em `docs/plans/governance/` antes de qualquer mutação na malha (modo **Fail-C [...]
L57: 3. **Estado 3 — Execução e Sincronização em Lote por Tipo de Artefato (R-015 / R-046 — requires_plan: true)**:
L58:    - O `@governance-maintainer` aplica as alterações declarativas (`.github/**` exceto `*.py`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`) em lote único (*Single-Turn Batching*) utilizando o `context-mode` MCP no sandbox p [...]
L59:    - **Sincronização Atômica por Tipo (R-015 — gap corrigido)**: o conjunto de arquivos sincronizados depende do tipo de artefato, nunca uma lista fixa de 4 arquivos:
L60:      - **Novo Agent**: `catalog.yaml` + `routing-graph.yaml` (nós/arestas) + **novo caso em `.github/agents/evals/casos-roteamento.yaml`** (exigência formal de R-040, antes omitida desta lista) + `agent-router.agent.md`  [...]
L61:      - **Nova Skill**: `.github/skills/.index.json` + `.github/skills/README.md` + `source_docs:` dos agents consumidores.
L62:      - **Novo Prompt**: `.github/prompts/README.md`.
L63:      - **Nova Stack**: todos os itens acima aplicados ao sub-catálogo de domínio (`*-catalog.yaml`) + domain router correspondente.
L64: 4. **Estado 4 — Quality Gate de Governança (Tier 1 Automático)**:
L65:    - Execução determinística dos testes de governança:
L66:      - `test_governance_smells.py` (conformidade com templates e 17 smells).
L67:      - `test_local_project_isolation.py` (100% isolamento de projetos locais — R-038/R-043/R-044).
L68:      - `test_routing_quality_gate.py` (integridade do grafo e alcançabilidade).
L69:    - **Suíte de Evals Comportamental**: para nova rota/agent, valida adicionalmente contra os 60 casos de `.github/agents/evals/casos-roteamento.yaml` (`agent-evals-lab`) — regressão estrutural (pytest) não substitui reg [...]
L70:    - **Circuit Breaker (Estado 4b)**: teto de **3 tentativas** de autocorreção. Havendo regressão, o `@governance-maintainer` executa autocorreção cirúrgica; se a 3ª tentativa ainda falhar, escala via `ask_questions` par [...]
L71:    - *Loop de Revisão de Qualidade*: Se o Avaliador Cético reprovar por achados de qualidade não-bloqueantes, aplica-se o Loop de Revisão de Qualidade (§ 1.5), teto de 3 iterações.
L72: 
L73: #### Typed State Bag (`workflow_state`):
L74: ```yaml
L75: workflow_state:
```
- **Evidência encontrada (`workflows.md:80-140` e `invariantes-e-protocolos.md:150-180`)**:
```text
L80:     HumanDecision -- "(b) Ajustar critério/rubrica" --> AdjustRubric["Ajusta rubrica e reavalia"] --> Eval
L81:     HumanDecision -- "(c) Cancelar / Reverter" --> Rollback["Reversão do diff / Rollback"] --> EndCancel(["🛑 Fluxo Interrompido"])
L82: ```
L83: 
L84: **Regras Normativas do Mecanismo**:
L85: 
L86: 1. **Gatilho**: O Avaliador Cético (§ 1.4) reprova o artefato por achados de qualidade **não-bloqueantes** (ex.: legibilidade, convenções de estilo, cobertura de casos de borda adicionais, documentação interna ou modular [...]
L87: 2. **Ciclo de Refinamento com Mesmo Avaliador**: O Gerador original recebe o feedback estruturado do Avaliador Cético, aplica as correções cirúrgicas e submete o artefato revisado compulsoriamente para o **mesmo Avaliado [...]
L88: 3. **Teto Rígido de 3 Iterações (R-055 / Anti-Silo Reuse)**: O loop é estritamente limitado ao teto de **3 iterações** (idêntico ao limiar do Circuit Breaker R-050.2, reaproveitado deliberadamente para coerência e integr [...]
L89: 4. **Critério de Corte Objetivo**: A reavaliação utiliza a mesma rubrica com limiar de corte (`threshold`) pré-estabelecida no Estado de avaliação (§ 1.4) — qualquer critério abaixo do corte mantém a reprovação, sendo te [...]
L90: 5. **Escalonamento Humano Obrigatório ao Esgotar**: Se a 3ª iteração for concluída sem aprovação integral, o Avaliador Cético interrompe o ciclo e aciona compulsoriamente `ask_questions`, apresentando ao usuário o relató [...]
L91: 6. **Rastreamento no `workflow_state`**: Todo workflow que executa este loop declara e atualiza o bloco estruturado no State Bag:
L92: ```yaml
L93: quality_review_loop:
L94:   iteracao_atual: 1  # 1 a 3
L95:   max_iteracoes: 3
L96:   achados_pendentes:
L97:     - "achado de qualidade ou estilo"
L98:   veredito: "em_andamento | aprovado | escalado_para_humano"
L99: ```
L100: 7. **Aplicabilidade Restrita**: Mecanismo opt-in por workflow, com aplicação formalizada nos seguintes Estados: `WORKFLOW-BUG-FIX` (Estado 5), `WORKFLOW-REFACTORING` (Estado 5), `WORKFLOW-FEATURE-DEVELOPMENT` (Estado 6), [...]
L101: 
L102: ---
L103: 
L104: 
L105: ## 2. Matriz Geral de Roteamento de Workflows
L106: 
L107: ```mermaid
L108: flowchart TD
L109:     UserReq["Solicitação do Usuário (Turno N)"] --> Router["@agent-router\n(R-037 & Health Check R-034)"]
L110:     Router --> IntentEval{"Classificação de Intenção\n& Fast-Path Check"}
L111: 
L112:     IntentEval -- "Bug / Erro / Layout / 500" --> WF1["⚡ WORKFLOW-BUG-FIX\nFast-Path direto para @bug-triage"]
L113:     IntentEval -- "Refatoração Estrutural" --> WF2["⚡ WORKFLOW-REFACTORING\nFast-Path direto para @refactor-planner"]
L114:     IntentEval -- "Análise Técnica / Grafo / Segurança" --> WF3["⚡ WORKFLOW-TECHNICAL-ANALYSIS\nFast-Path direto para Especialista"]
L115:     IntentEval -- "Governança / Auditoria de Agents" --> WF5["⚡ WORKFLOW-GOVERNANCE-MAINTENANCE\nFast-Path direto para @agent-auditor"]
L116:     IntentEval -- "CVE / Atualizar Dependência" --> WF6["⚡ WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION\nFast-Path direto para @security-reviewer"]
L117:     IntentEval -- "Pre-Flight Release / Deploy" --> WF8["⚡ WORKFLOW-RELEASE-READINESS\nFast-Path direto para @tech-solution-architect"]
L118:     IntentEval -- "Migração de Framework / Major Version" --> WF7["🚀 WORKFLOW-FRAMEWORK-MIGRATION\nDireto para @tech-solution-architect (6 etapas)"]
L119:     IntentEval -- "Síntese / Refino de Prompt / Novo Chat" --> WF9["⚡ WORKFLOW-PROMPT-SYNTHESIS\nDireto para @prompt-structuring (5 etapas)"]
L120:     IntentEval -- "Feature Nova / Pedido Ambíguo" --> Structuring["@prompt-structuring\n(R-041 — loop máx. 5x)"]
L121: 
L122:     Structuring --> RouterRet["@agent-router\n(Retomada com Prompt Refinado)"]
L123:     RouterRet --> WF4["🚀 WORKFLOW-FEATURE-DEVELOPMENT\nPipeline Completo E2E"]
L124: ```
L125: 
L126: ### 2.1 Resumo dos Pipelines Determinísticos & Quality Gates
L127: 
L128: | Workflow | Fast-Path | Pipeline Canônico & Quality Gate |
L129: | :--- | :--- | :--- |
L130: | `WORKFLOW-BUG-FIX` | `⚡ Sim` | `1. Triagem (RCA 2 fontes) -> 2. Red Test -> [Plano de Implementação R-064] -> 3. Fix Cirúrgico -> 4. Green Test -> [5. Quality Gate & Quality Review Loop (§ 1.5)]` |
L131: | `WORKFLOW-REFACTORING` | `⚡ Sim` | `1. Ground Truth -> 2. Blast Radius & Contratos -> 3. Plano Mikado -> [Plano de Implementação R-064] -> 4. Execução em Lote -> [5. Validação & Quality Review Loop (§ 1.5)]` |
L132: | `WORKFLOW-TECHNICAL-ANALYSIS` | `⚡ Sim` | `1. Despacho Especialista -> 2. Coleta Read-Only -> 3. Síntese Técnica & Propostas` |
L133: | `WORKFLOW-FEATURE-DEVELOPMENT` | `❌ Não (R-041)` | `1. Prompt Structuring -> 2. Requisitos -> 3. Blueprint -> 4. Estratégia Testes -> [Plano de Implementação R-064] -> 5. TDD -> [6. Duplo Gate & Quality Review Loop (§  [...]
L134: | `WORKFLOW-GOVERNANCE-MAINTENANCE` | `⚡ Sim` | `1. Diagnóstico (@agent-auditor) -> 2. Materialização Física do Plano R-064 em docs/plans/governance/ (@docs-engineer / @governance-maintainer, status: DRAFT) -> 3. Checkpo [...]
L135: | `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION` | `⚡ Sim` | `1. Triagem SCA -> 2. Blast Radius -> [Plano de Implementação R-064] -> 3. Bump & Lockfile -> 4. Adaptação Breaking -> [5. Quality Gate SCA & Quality Review L [...]
L136: | `WORKFLOW-FRAMEWORK-MIGRATION` | `⚡ Sim` | `1. 5D & Símbolos -> 2. Blueprint & De-Para -> 3. Plano de Implementação R-064 -> 4. Codemod Lote -> 5. Paridade Dual -> 6. Baseline Gate -> [7. Redundancy Gate & Quality Revi [...]
L137: | `WORKFLOW-RELEASE-READINESS` | `⚡ Sim` | `1. Contratos OpenAPI -> 2. Rollout DDL -> 3. Segredos & Higiene -> 4. Changelog & SemVer -> 5. Veredito Go/No-Go` |
L138: | `WORKFLOW-PROMPT-SYNTHESIS` | `⚡ Sim` | `1. Elicitação -> 2. Context Grounding -> 3. Restrições -> 4. Síntese Estruturada -> 5. Quality Gate (.md)` |
L139: 
L140: ---
---
L150: - [⏳] **Etapa 6: Duplo Quality Gate, Quality Review Loop (§ 1.5) & PR Preparation** → `Gate 1 (Lógica/Sec) + Gate 2 (UI Parity) → @pr-gatekeeper` *(Pendente: validação dupla, loop de qualidade até 3x se achados não-bloqu [...]
L151: ```
L152: 
L153: #### WORKFLOW 5: `WORKFLOW-GOVERNANCE-MAINTENANCE` (4 etapas)
L154: ```markdown
L155: ### 🗺️ Pipeline de Execução: WORKFLOW-GOVERNANCE-MAINTENANCE (4 etapas)
L156: - [▶] **Etapa 1: Diagnóstico Read-Only ou Pesquisa Prévia** → `@agent-auditor` / `@repo-hygiene-auditor` / `@docs-engineer` / `@deep-search` *(Em Andamento: auditoria estrutural, documental e pesquisa prévia)*
L157: - [⏳] **Etapa 2: Checkpoint de Aprovação Humana** → `ask_questions` *(Pendente: aprovação explícita do plano)*
L158: - [⏳] **Etapa 3: Execução Governada em Lote** → `@governance-maintainer` / `@governance-factory` / `@docs-engineer` *(Pendente: sincronização atômica SSOT R-015/R-046 e documentação técnica)*
L159: - [⏳] **Etapa 4: Quality Gate de Governança & Quality Review Loop (§ 1.5)** → `pytest (Tier 1)` / `@agent-auditor` *(Pendente: validação determinística de smells, routing, isolamento e loop de qualidade até 3x)*
L160: ```
L161: 
L162: #### WORKFLOW 6: `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION` (5 etapas)
L163: ```markdown
L164: ### 🗺️ Pipeline de Execução: WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION (5 etapas)
L165: - [▶] **Etapa 1: Triagem de Vulnerabilidade & Advisory** → `@security-reviewer` *(Em Andamento: análise de CVE, CVSS e changelog)*
L166: - [⏳] **Etapa 2: Mapeamento de Blast Radius da Dependência** → `@codegraph-engine` *(Pendente: mapa de impacto e consumidores R-045)*
L167: - [⏳] **Etapa 3: Bump de Manifesto & Sincronização de Lockfile** → `specialist-developer` *(Pendente: atualização de dependências e lockfile)*
L168: - [⏳] **Etapa 4: Adaptação de Breaking Changes & Compilação** → `<stack>-developer` / `<stack>-test-engineer` *(Pendente: compatibilização de APIs e compilação limpa)*
L169: - [⏳] **Etapa 5: Verificação de Regressão, SCA & Quality Review Loop (§ 1.5)** → `runtime-verifier` + `@code-review` + `@security-reviewer` *(Pendente: 100% testes verdes, scan SCA limpo e loop de qualidade até 3x)*
L170: ```
L171: 
L172: #### WORKFLOW 7: `WORKFLOW-FRAMEWORK-MIGRATION` (6 etapas — Cross-Stack exige Router Origem + Destino + Grafo)
L173: ```markdown
L174: ### 🗺️ Pipeline de Execução: WORKFLOW-FRAMEWORK-MIGRATION (6 etapas)
L175: - [▶] **Etapa 1: Pre-Flight Assessment, 5D & Symbol Exhaustion** → `@tech-solution-architect` + `@codegraph-engine` (obrigatório) + `@domain-router-ORIGEM` (ex.: `@ejb-router`) + `@business-rules-extractor` *(Em Andament [...]
L176: - [⏳] **Etapa 2: Migration Phasing & Blueprint com Matriz De-Para** → `@tech-solution-architect` + `@domain-router-ORIGEM` + `@domain-router-DESTINO` (ex.: `@spring-boot-router`) *(Pendente: mapeamento de 100% dos símbol [...]
L177: - [⏳] **Etapa 3: Codemod & Transformação em Lote com Anti-Omission** → `@domain-router-DESTINO` (executor) + `@domain-router-ORIGEM` (oráculo consultivo contínuo) + `@codegraph-engine` (obrigatório, blast radius por lote [...]
L178: - [⏳] **Etapa 4: Refinamento & Paridade Funcional (Dual-Verification Expandido)** → `@domain-router-DESTINO` + `@domain-router-ORIGEM` + `@business-rules-extractor` + `@codegraph-engine` (obrigatório, find_cycles/dead-co [...]
L179: - [⏳] **Etapa 5: Baseline & Quality Gate de Migração** → `runtime-verifier` + `@code-review` + sign-off de `@domain-router-ORIGEM` + sign-off de `@codegraph-engine` *(Pendente: build limpo, testes verdes e PR preliminar) [...]
L180: - [⏳] **Etapa 6: Post-Migration Verification, Redundancy Gate & Quality Review Loop (§ 1.5)** → `@code-review` + `@test-strategy` + `@business-rules-extractor` + `@runtime-verifier` *(Pendente: tríplice auditoria: revers [...]
```
- **Diagnóstico**:
  - Em `workflow-governance-maintenance.md`, o item `3.` aparece duas vezes: linha 55 (`3. @docs-engineer — Materialização do Plano de Governança (R-064)...`) e linha 60 (`3. @governance-maintainer — Execução (Escrita Declarativa)`), seguido de `4. @agent-auditor — Quality Gate Pós-Mudança (Verificação)` na linha 64 e `4b.` na linha 70.
  - Na tabela de `workflows.md:140`, o pipeline já consta com 5 etapas (`1. @agent-auditor -> 2. @docs-engineer + @plan-critic + Gate Humano -> 3. @governance-maintainer -> 4. @agent-auditor -> 5. @eval-Gate`), e no `routing-graph.yaml` existem 5 estados (`Estado 1` a `Estado 5`). Porém, `workflows.md:100` (Regra 7 da § 1.5) cita `WORKFLOW-GOVERNANCE-MAINTENANCE (Estado 4)` e `invariantes-e-protocolos.md:153-155` ainda descreve `WORKFLOW-GOVERNANCE-MAINTENANCE` com 4 estados sem o estado intermediário de materialização/aprovação R-064.
- **Proposta de alteração (Proposto)**:
  1. Em `.github/agents/workflows/workflow-governance-maintenance.md:55-72`: manter `3. @docs-engineer + @plan-critic — Materialização do Plano de Governança (R-064) + Revisão Cética Pré-HITL (§ 10.7) + CHECKPOINT DE APROVAÇÃO HUMANA`, renumerar `@governance-maintainer — Execução (Escrita Declarativa)` para `4.`, e renumerar `@agent-auditor — Quality Gate Pós-Mudança (Verificação)` para `5.` (e a etapa condicional de testes sintéticos para `5b.`).
  2. Em `.github/agents/workflows.md:100` (Regra 7 da § 1.5): atualizar `WORKFLOW-GOVERNANCE-MAINTENANCE (Estado 4)` para `WORKFLOW-GOVERNANCE-MAINTENANCE (Estado 5)`.
  3. Em `.github/agents/workflows/invariantes-e-protocolos.md:153-155` (§ 6.2): atualizar a listagem de estados de `WORKFLOW-GOVERNANCE-MAINTENANCE` para refletir as 5 etapas canônicas (`Estado 1 (Diagnóstico)`, `Estado 2 (Classificação)`, `Estado 3 (Materialização R-064 via @docs-engineer + @plan-critic + Gate Humano)`, `Estado 4 (Execução Declarativa via @governance-maintainer)`, `Estado 5 (Quality Gate via @agent-auditor)`).

### 2.3 Achado M2 (MEDIUM) — Unificação da Contagem/Numeração de Etapas de `WORKFLOW-FRAMEWORK-MIGRATION`

- **Evidência encontrada (`workflow-framework-migration.md:45-145`)**:
```text
L45:     RollbackGap --> BatchCodemod
L46:     CheckRedundancy -- "Zero Gaps (100% Paridade)" --> EndMigDone(["✅ Migração de Framework Concluída com Sucesso & Cutover Certificado (Zero Gaps)"])
L47: ```
L48: 
L49: #### A Estratégia de Prevenção de Gaps em 5 Dimensões Críticas:
L50: A causa raiz de migrações incompletas com dezenas de gaps descobertos tardiamente é a inspeção superficial restrita ao "happy path" do ponto de entrada principal. O workflow exige a decomposição exaustiva do artefato leg [...]
L51: 1. **Dimensão 1: Borda, Contratos de Entrada & Validações Fail-Fast**:
L52:    - Mapeamento de 100% das interfaces de entrada (APIs síncronas, endpoints RPC/REST, listeners de mensageria/eventos, handlers de UI/CLI).
L53:    - Levantamento de todas as validações pré-voo (ex.: pré-condições de estado, validação de payload/parâmetros, regras de bloqueio de entrada, validações de concorrência ou versão).
L54:    - Mapeamento exaustivo de todos os códigos de erro, mensagens descritivas e exceções de domínio disparadas.
L55: 2. **Dimensão 2: Regras de Negócio e Ramificações Condicionais**:
L56:    - Todas as decisões de fluxo e bifurcações condicionais (ex.: flags de tipo de cliente/canal, fluxos alternativos de exceção, regras de cálculo e desvios por perfil ou segmento).
L57:    - Mapeamento reverso de regras em formato declarativo (EARS/INVEST) via `@business-rules-extractor`.
L58: 3. **Dimensão 3: Pegada de Persistência Relacional & Transações (Database/State Touches)**:
L59:    - 100% dos repositórios, entidades e tabelas tocadas:
L60:      - Entidades/tabelas principais ou agregados raiz (ex.: `ENTIDADE_PRINCIPAL_LEGADA`, `ENTIDADE_VERSAO_LEGADA`).
L61:      - Entidades/tabelas filhas e itens em cascata (ex.: `ENTIDADE_ITEM_FILHO`, `ENTIDADE_DETALHE`).
L62:      - Entidades/tabelas de rateio, agregação ou valores consolidados (ex.: `ENTIDADE_TOTAL_RATEIO`, `ENTIDADE_TOTAL_CONSOLIDADO`).
L63:      - Entidades/tabelas de auditoria, histórico de movimentação e snapshots de estado (ex.: `ENTIDADE_HISTORICO_MOVIMENTO`, `ENTIDADE_SNAPSHOT_VALOR`).
L64:      - Entidades/tabelas de anotações técnicas, comentários e regras de visibilidade (ex.: `ENTIDADE_NOTAS_AUDITORIA`, `ENTIDADE_VISIBILIDADE`).
L65:      - Sequências de persistência, chaves primárias compostas, índices e triggers de banco.
L66:    - Demarcações transacionais (escopos de transação autônoma, níveis de isolamento, garantias ACID/consistência eventual, condições de rollback).
L67: 4. **Dimensão 4: Efeitos Colaterais & Integrações Downstream**:
L68:    - Clientes legados de integração remota (protocolos legados, chamadas RPC/SOAP, stubs de rede).
L69:    - Clientes modernos de comunicação síncrona e reativa.
L70:    - Publicação/consumo de mensagens e eventos (tópicos, filas, message brokers).
L71:    - Motores de geração de relatórios, binários ou documentos (migração para engines e templates declarativos modernos).
L72:    - Notificações de saída (e-mails, mensagens formatadas, assuntos dinâmicos e anexos).
L73:    - Processos secundários de ingestão/upload de arquivos e documentos.
L74:    - Webhooks de alerta e observabilidade ativa (canais de monitoramento e alertas de incidentes) em caso de falha.
L75: 5. **Dimensão 5: Contratos de Saída & DTOs de Resposta**:
L76:    - Código de sucesso explícito e padronizado.
L77:    - Payloads de retorno aos clientes da API/interface.
L78:    - Headers, status codes e formatação padronizada de responses.
L79: 
L80: #### O Symbol Exhaustion Gate e Anti-Omission AST Validator:
L81: Para erradicar a dependência de inferência humana ou de IA sobre o que foi esquecido, o workflow institui dois mecanismos determinísticos de engenharia de compiladores:
L82: 1. **Symbol Exhaustion Gate (Inventário Mecânico de Símbolos — Etapa 1/2)**:
L83:    - O `@codegraph-engine` extrai a contagem exata e a listagem de 100% dos símbolos do módulo legado: `total_simbolos = {classes, metodos_publicos, metodos_privados, queries_sql, rotas_endpoints, campos_dto}`.
L84:    - A Matriz De-Para gerada na Etapa 2 deve mapear obrigatoriamente $100\%$ desses símbolos. É proibido avançar com qualquer símbolo omitido sem status formal (`[MIGRADO]`, `[DESACOPLADO]` ou `[OBSOLETO]`).
L85: 2. **Anti-Omission AST Validator (Pós-Codemod — Etapa 3)**:
L86:    - Após a geração do código pelo especialista de destino, um validador no sandbox (`ctx_execute`) analisa a AST do código moderno contra os nós mapeados na Representação Intermediária (IR).
L87:    - Se o modelo sofrer de *truncation* ou *silent omission* (ex.: omitir branches de erro, persistência em tabelas secundárias de auditoria ou rateio), o validador emite a lista de nós faltantes (`Missing AST Nodes`) e  [...]
L88: 
L89: #### A Matriz De-Para de Migração & Rastreabilidade de Gaps (Padrão Canônico):
L90: Documentada em `docs/migrations/matriz-de-para-<alvo>.md` (ou incorporada ao blueprint canônico em `docs/`), constitui a **Single Source of Truth** visual e auditável da paridade:
L91: 
L92: | ID | Dimensão | Elemento Legado (Módulo.Método / Tabela) | Regra / Comportamento Observável | Elemento Destino (Módulo.Método / Tabela) | Status Paridade | Evidência de Paridade | Fase Alvo |
L93: |:---:|---|---|---|---|:---:|---|:---:|
L94: | `GAP-01` | Borda | `ServicoOrigemLegado.atualizarStatusProcesso` | Transição de status legado conforme condição A/B | `StatusEnumDestino` + `PersistirStatusDestinoFunction` | `[✅ MIGRADO]` | `PersistirStatusDestinoFunc [...]
L95: | `GAP-02` | Saída | `ServicoOrigemLegado.processarOperacao` (sucesso) | Retorno de código de sucesso e mensagem canônica | `ContextChainDestino.andFinallyExecute` | `[✅ MIGRADO]` | `OperacaoParityTest` | Fase B1 |
L96: | `GAP-03` | Persistência | `DominioOrigemBusiness.salvarNotasAuditoria` | Gravação sequencial de notas em `ENTIDADE_NOTAS_AUDITORIA` | `NotaAuditoriaRepository` + `PersistirDadosDestinoFunction` | `[✅ MIGRADO]` | `Persi [...]
L97: | `GAP-04` | Downstream | `GeradorRelatorioLegado.gerarDocumento` | Relatório corporativo gerado via template moderno | `GerarRelatorioDestinoServiceImpl` | `[✅ MIGRADO]` | `GerarRelatorioDestinoServiceImplTest` | Fase B [...]
L98: | `GAP-05` | Persistência | `DominioOrigemBusiness.calcularRateioDivisao` | Rateio de valores totais em `ENTIDADE_TOTAL_RATEIO` | `DivisaoTotalRepository` + `PersistirDadosDestinoFunction` | `[✅ MIGRADO]` | `PersistirDad [...]
L99: | `GAP-06` | Downstream | `ServicoAssincronoLegado.dispararScoreRisco` | Predição assíncrona desacoplada em serviço externo | Microsserviço de Analytics / IA | `[ℹ️ DESACOPLADO]` | Desacoplado no pipeline assíncrono corr [...]
L100: 
L101: ##### Taxonomia Estrita de Status da Matriz:
L102: - `[✅ MIGRADO]`: Portado com paridade comprovada por teste automatizado verde.
L103: - `[⏳ PENDENTE]`: Inventariado no escopo da migração, aguardando execução na fase alvo.
L104: - `[⚠️ DIVERGENTE]`: Portado parcialmente (ex.: stub com retorno fixo, tratamento incompleto de status ou divergência contratual).
L105: - `[ℹ️ DESACOPLADO]`: Intencionalmente extraído para outro serviço/módulo moderno na arquitetura, com justificativa técnica documentada.
L106: - `[🚫 OBSOLETO]`: Código morto ou descontinuado no legado, com aprovação explícita de descarte.
L107: 
L108: #### Cadeia Sequencial e Papéis:
L109: 1. **Estado 0 — Identificação de Stacks & Detecção de Cenário (`@tech-solution-architect`)**:
L110:    - *Ação*: O arquiteto classifica a migração em duas dimensões determinísticas:
L111:      1. **Classificação Tecnológica**: **cross-stack** (stack de origem e de destino distintas — legado→moderno) ou **in-stack** (mesma stack, apenas major version). Determina a obrigatoriedade da colaboração dual-stack.
L112:      2. **Classificação de Cenário**: **greenfield** (projeto do zero, sem código moderno prévio) ou **brownfield_in_flight** (migração já iniciada ou incompleta no repositório moderno).
L113: 2. **Estado 1 — Pre-Flight Compatibility Assessment, 5D & Symbol Exhaustion (`@tech-solution-architect` + `@codegraph-engine` + `domain-router-ORIGEM` + `@business-rules-extractor`)**:
L114:    - *Ação*: `@codegraph-engine` (co-agente **obrigatório**, R-045) extrai a árvore completa de chamadas (`callees`/`callers`), referências, ciclos e o inventário completo de símbolos do legado (Symbol Exhaustion Gate).  [...]
L115:    - *Sub-rotina 1a (obrigatória se cross-stack)*: `domain-router-ORIGEM` (ex.: `@ejb-router`, `@struts-router`) atua como oráculo legado, validando a semântica da stack legada (gestão transacional, contratos remotos, co [...]
L116: 3. **Estado 1b — Reconciliação Delta & Auditoria de Gaps Pré-Existentes (Obrigatório em Cenários `brownfield in-flight`)**:
L117:    - *Ação*: Quando a migração já estiver em andamento (cenário *brownfield in-flight* com código parcial ou inacabado no destino), o arquiteto cruza o inventário 5D do legado contra o código moderno já implementado no r [...]
L118:    - *Saída*: Produz a **Matriz De-Para Preliminar**, catalogando e numerando de imediato todos os gaps encontrados (`GAP-01..GAP-NN`) com status `[⚠️ DIVERGENTE]` (stubs, implementações parciais) ou `[⏳ PENDENTE]` (iten [...]
L119: 4. **Estado 2 — Migration Phasing & Blueprint com Matriz De-Para (`@tech-solution-architect` + `domain-router-ORIGEM` + `domain-router-DESTINO`)**:
L120:    - *Ação*: Elaboração do Technical Blueprint canônico e consolidação da **Matriz De-Para de Migração**, garantindo correspondência para 100% dos símbolos extraídos no Symbol Exhaustion Gate.
L121:    - *Phased Architecture Ancorada*: A decomposição em fases autônomas entregáveis (Fases B1..BN — ex.: Fase B1: Validações Pré-Voo, Fase B2: Persistência Relacional Core, Fase B3: Integrações Downstream, Fase B4: Efeito [...]
L122:    - *Checkpoint Humano (Estado 2b)*: Apresentação da estratégia e aprovação obrigatória do plano via `ask_questions`, exibindo o **Dashboard Executivo da Matriz De-Para**:
L123:      ```
L124:      📊 Dashboard Executivo da Matriz De-Para:
L125:      - Total de Itens: <N> | ✅ Migrados: <N> (<%>)| ⏳ Pendentes: <N> (<%>) | ⚠️ Divergentes: <N> (<%>) | ℹ️ Desacoplados: <N> (<%>)
L126:      ```
L127:    - **Gate Anti-Continuação-Genérica (Invariante 11, § 5)**: Se o Dashboard listar qualquer item `⏳ PENDENTE` ou `⚠️ DIVERGENTE` (stubs, implementações parciais, itens não implementados), o Estado 2b NÃO é considerado s [...]
L128: 5. **Estado 3 — Codemod & Transformação em Lote com Anti-Omission AST Validator (`domain-router-DESTINO` + `<stack>-developer`)**:
L129:    - *Ação*: Execução dos codemods oficiais (`ng update`, OpenRewrite recipes) ou transformações cirúrgicas via sandbox `context-mode` (R-046) estritamente restritas aos IDs De-Para da fase ativa.
L130:    - *Validação Anti-Omission*: Um validador no sandbox (`ctx_execute`) inspeciona o código transformado garantindo que nenhuma branch, exception handler ou persistência secundária mapeada na IR foi omitida. Em caso de o [...]
L131:    - *Colaboração Contínua*: `domain-router-ORIGEM` permanece ativo como oráculo consultivo validando paridade regra a regra; `@codegraph-engine` recalcula blast radius antes de cada micro-lote.
L132: 6. **Estado 4 — Refinamento, Paridade Funcional & Resolução De-Para (`domain-router-DESTINO` + `<stack>-test-engineer`)**:
L133:    - *Ação*: Ajuste idiomático da nova versão e execução de testes comprovando comportamento idêntico ao baseline.
L134:    - *Gate de Dual-Verification Expandido*: exige **(1)** testes de caracterização (Golden Master) 100% verdes, **(2)** resolução de 100% dos IDs De-Para da fase corrente (zero `PENDENTE` ou `DIVERGENTE`), **(3)** confir [...]
L135:    - Se aprovado, transiciona os itens da fase para `[✅ MIGRADO]` e avança para a próxima fase (loop até a última fase).
L136: 7. **Estado 5 — Baseline & Quality Gate de Migração (`runtime-verifier` + `@code-review`)**:
L137:    - *Ação*: Build limpo, execução de 100% da suíte de testes de ponta a ponta e preparação de PR semântico preliminar pelo `@pr-gatekeeper`.
L138:    - *Auditoria de Fechamento da Matriz De-Para*: Confirmação de que 100% dos itens inventariados no módulo estão em `[✅ MIGRADO]` ou `[ℹ️ DESACOPLADO]` (com link de rastreabilidade). Zero gaps órfãos ou pendentes.
L139:    - *Sign-off Final Conjunto*: `domain-router-ORIGEM` (paridade funcional e ausência de perdas confirmadas) + `@codegraph-engine` (zero ciclos novos e zero dead-code) + `domain-router-DESTINO` (conformidade com padrões  [...]
L140:    - *Nota de Avaliador Cético (Governança)*: O avaliador cético confirmado nesta etapa é exclusivamente `@code-review`; `@adr-sentinel` NÃO participa deste pipeline por padrão (achado de auditoria de governança, 2026-10 [...]
L141: 8. **Estado 6 — Post-Migration Verification & Redundancy Gate (`@code-review` + `@test-strategy` + `@business-rules-extractor` + `@runtime-verifier`)**:
L142:    - *Ação*: Camada autônoma de redundância e certificação pós-migração para garantir totalidade absoluta e zero código esquecido antes do cutover final para produção:
L143:      - **Sub-rotina 6a: Reverse Orphan Audit (Auditoria Reversa de Órfãos)**: O `@code-review` em conjunto com o `@codegraph-engine` varre todo o código-fonte legado contra o código moderno e a Matriz De-Para. Se existir [...]
L144:      - **Sub-rotina 6b: Mutation Parity Resilience (Testes de Mutação de Paridade)**: O `@test-strategy` orienta a injeção de mutantes sintéticos controlados no código moderno (inversão de operadores booleanos, omissão p [...]
L145:      - **Sub-rotina 6c: Differential Shadow Replay & Invariant Comparator**: Execução em paralelo das fixtures canônicas Golden Master nas duas aplicações (legada e moderna), comparando semanticamente via comparador norm [...]
```
- **Diagnóstico**:
  - Em `workflow-framework-migration.md`, os estados estão numerados como `1.`, `1.5.`, `2.`, `2.5.`, `3.`, `4.`, `5.`, `5.5.`, `6.` (totalizando 9 estágios operacionais quando contados os sub-estágios `.5`, ou 6 macro-estados numerados de 1 a 6).
  - Em `workflows.md:100` (Regra 7 da § 1.5), cita-se `WORKFLOW-FRAMEWORK-MIGRATION (Estado 6)`.
  - Em `workflows.md:113` (Mermaid), cita-se `7. Framework Migration (7 etapas + Dual Gate + Cutover)`.
  - Em `workflows.md:136` (Tabela § 2.1), listam-se 8 passos numerados (`1.` a `8.`).
  - Em `invariantes-e-protocolos.md:153-175` (§ 6.2) e `routing-graph.yaml`, é necessário alinhar a nomenclatura/contagem para que todas as referências reflitam de forma unívoca a estrutura real sincronizada com `routing-graph.yaml`.
- **Proposta de alteração (Proposto)**:
  - Padronizar e unificar a descrição da contagem/numeração de etapas de `WORKFLOW-FRAMEWORK-MIGRATION` entre:
    1. `workflows.md:100` (Regra 7 da § 1.5 — indicar explicitamente o estado final de verificação pós-migração/paridade conforme numeração canônica unificada),
    2. `workflows.md:113` (Mermaid),
    3. `workflows.md:136` (Tabela § 2.1),
    4. `workflow-framework-migration.md:45-145`, e
    5. `invariantes-e-protocolos.md` (§ 6.2),
    garantindo correspondência explícita e determinística com os estados declarados em `routing-graph.yaml`.

### 2.4 Achado M3 (MEDIUM) — Desambiguação de `R-065` e Referência Explícita ao Guard de Severidade Arquitetural nos Loops de Qualidade

- **Evidência encontrada (`workflows.md:84, 199` e `invariantes-e-protocolos.md:458-466`)**:
```text
L195: > referenciados acima residem em `source_docs_lazy:` e são consultados exclusivamente
L196: > via `context-mode/ctx_search` sob demanda pelo workflow ativo — nunca via `read_file`
L197: > integral de todos os workflows de uma vez.
L198: 
L199: > **Árvore Universal R-064**: Subpastas tipadas canônicas de `docs/plans/<tipo>/`: `docs/plans/feature/`, `docs/plans/refactor/`, `docs/plans/architecture/`, `docs/plans/implementation/`, `docs/plans/test-strategy/`, `do [...]
L200: 
---
L458: ### 10.7 Quality Gate Universal de Revisão Cética Pré-HITL (`@plan-critic` / ADR-0014)
L459: 
L460: - **Two-Tier Hybrid Gate antes de `ask_questions` (Gate 1 e Gate 2)**: Todo plano persistido como `DRAFT` nas 8 categorias de `docs/plans/<tipo>/` DEVE passar por: **(Tier 1)** validação estrutural determinística (frontm [...]
L461: - **Política de Iteração e Noise Budget**: Fast-Pass 1x quando Tier 1 = `PASS` e 0 findings `BLOCKER`/`HIGH`; teto máximo de 2 rodadas (3 em `tier: full`); Noise Budget ≤ 5 findings acionáveis (`BLOCKER`/`HIGH` apenas, R [...]
L462: 
```
- **Diagnóstico**:
  - `workflows.md:84` usa `R-065` para a regra anti-prefixo redundante (`PROIBIDO usar prefixos redundantes como PLAN- ou REQ-`), enquanto `workflows.md:199` e `invariantes-e-protocolos.md:461` usam `R-065` para o **Guard de Severidade Arquitetural no Quality Review Loop** (e `invariantes-e-protocolos.md:507` trata da nomenclatura sob R-064/§ 10.6).
  - Além disso, os sub-arquivos com `quality_review_loop` (`workflow-refactoring.md`, `workflow-feature-development.md`, `workflow-framework-migration.md`) não citam explicitamente o Guard de Severidade Arquitetural (`R-065` / `invariantes-e-protocolos.md § 10.2`) no estado de revisão pós-implementação.
- **Proposta de alteração (Proposto)**:
  1. Em `workflows.md:84`: vincular a regra de nomenclatura sem prefixo `PLAN-`/`REQ-` a **R-064 (§ 10.6)**, reservando **R-065** exclusivamente para o **Guard de Severidade Arquitetural no Quality Review Loop** (em consonância com `workflows.md:199` e `invariantes-e-protocolos.md:461`).
  2. Em `invariantes-e-protocolos.md:461`: manter e explicitar que **R-065** designa canonicamente o Guard de Severidade Arquitetural (§ 10.2), enquanto a proibição de prefixos `PLAN-`/`REQ-` (§ 10.6) integra a convenção de persistência física de **R-064**.
  3. Nos sub-arquivos `workflow-refactoring.md`, `workflow-feature-development.md` e `workflow-framework-migration.md`: adicionar referência explícita ao **Guard de Severidade Arquitetural (R-065 / § 10.2)** nos respectivos estados de `quality_review_loop` (`@code-critic` / `@adr-sentinel`), distinguindo desvios táticos (`LOW`/`MEDIUM` -> implementador com `max_iterations: 2`) de violações estruturais (`HIGH`/`CRITICAL` -> retorno ao advisor/planejador com invalidação do Gate 2).

### 2.5 Achado M4 (MEDIUM) — Eliminação de Prefixos Legados `PLAN-` / `REQ-` em Caminhos de Arquivos de Plano em `workflow-framework-migration.md`

- **Evidência encontrada (`workflow-framework-migration.md:51-82`)**:
  - Em `workflow-framework-migration.md:55`, consta `docs/plans/requirements/<AAAAMMDD-HHMMSS>-<modulo>.md` (já canônico), e em `workflow-framework-migration.md:81`, consta `docs/plans/architecture/<AAAAMMDD-HHMMSS>-migracao-<alvo>.md` (já canônico), enquanto nas linhas 52 e 75 aparece `IDs de requisitos (`REQ-01`, `REQ-02`...)` referindo-se aos identificadores EARS de regras de negócio.
- **Proposta de alteração (Proposto)**:
  - Inspecionar integralmente `workflow-framework-migration.md:51-82` (e demais linhas do arquivo): substituir qualquer eventual referência residual a nome de arquivo com prefixo `PLAN-` ou `REQ-` em `docs/plans/` pelo formato `<AAAAMMDD-HHMMSS>-<slug>.md`, **preservando intactos** os identificadores de requisitos de negócio EARS (`REQ-01`, `REQ-02`) e adicionando nota explícita de que `REQ-01` refere-se ao ID interno da regra na Matriz De-Para (e nunca a prefixo de nome de arquivo em `docs/plans/`, proibido por R-064 § 10.6).

### 2.6 Achado L1 (LOW) — Atualização de Comentário Legado em `routing-graph.yaml:185`

- **Evidência encontrada (`routing-graph.yaml:183-187`)**:
```text
L183: # ─────────────────────────────────────────────
L184: # WORKFLOWS — Máquinas de Estado Canônicas (R-050)
L185: # Define os 5 workflows operacionais determinísticos e suas sequências estritas
L186: # ─────────────────────────────────────────────
L187: convencao_papeis_genericos:
```
- **Proposta de alteração (Proposto)**:
  - Substituir na linha 185 de `.github/agents/routing-graph.yaml`:
    - **Encontrado**: `# Define os 5 workflows operacionais determinísticos e suas sequências estritas`
    - **Proposto**: `# Define os 9 workflows canônicos (+ 3.A auxiliar) operacionais determinísticos e suas sequências estritas`

### 2.7 Achado L2 (LOW) — Atualização de Contagens de Smells em `workflow-governance-maintenance.md:66-69`

- **Evidência encontrada (`workflow-governance-maintenance.md:65-72`)**:
  - Linha 66: `Executa checklist C1–C9 e varredura dos 17 smells sobre os arquivos alterados.`
  - Linha 69: `Executa a bateria de testes de roteamento em .github/agents/evals/ (60 casos, 9 categorias) e verifica se os casos afetados pela mudança passam.`
- **Proposta de alteração (Proposto)**:
  - Atualizar a linha 66 para `Executa checklist C1–C9 e varredura do catálogo canônico de Smells (Smells 2.1 a 2.34) sobre os arquivos alterados.` e atualizar a linha 69 para remover o número hardcoded defasado (`60 casos`), referenciando a suíte canônica vigente em `.github/agents/evals/` e `tests/governance_audit/`.

### 2.8 Achado Q3 (R-055) — Suíte de Testes de Regressão em `tests/governance_audit/test_workflows_parity_and_gates.py`

- **Arquivo-alvo**: `tests/governance_audit/test_workflows_parity_and_gates.py`
- **Diagnóstico**:
  - Atualmente não há teste automatizado dedicado que valide simultaneamente: (a) a ausência de estados duplicados nos sub-arquivos `workflow-*.md`, (b) a paridade entre a Regra 7 da § 1.5 de `workflows.md`, `invariantes-e-protocolos.md` e `routing-graph.yaml`, (c) a presença obrigatória de `@plan-critic` nos 6 sub-arquivos com plano R-064, (d) a desambiguação de R-064 vs R-065 e (e) o comentário atualizado de workflows em `routing-graph.yaml`.
- **Proposta de alteração (Proposto)**:
  - Especificar a criação/atualização de `tests/governance_audit/test_workflows_parity_and_gates.py` contendo testes parametrizados em `pytest` para:
    1. `test_subworkflows_with_r064_include_plan_critic_gate`: verifica que todos os 6 sub-arquivos R-064 referenciam `@plan-critic` antes do Gate HITL (`ask_questions`).
    2. `test_workflow_governance_maintenance_state_numbering_no_duplicates`: garante numeração sequencial `1.` a `5.` sem duplicidade de `Estado 3` em `workflow-governance-maintenance.md` e paridade com `workflows.md:100` (`Estado 5`) e `invariantes-e-protocolos.md`.
    3. `test_workflow_framework_migration_stage_parity`: valida alinhamento de contagem/estados de `WORKFLOW-FRAMEWORK-MIGRATION` entre `workflows.md`, `workflow-framework-migration.md`, `invariantes-e-protocolos.md` e `routing-graph.yaml`.
    4. `test_r065_architectural_severity_guard_disambiguation_and_references`: valida que `R-065` designa exclusivamente o Guard de Severidade Arquitetural e está referenciado em `workflow-refactoring.md`, `workflow-feature-development.md` e `workflow-framework-migration.md`.
    5. `test_routing_graph_workflows_header_comment_is_current`: valida que `routing-graph.yaml` declara `9 workflows canônicos (+ 3.A auxiliar)` e que o YAML possui os 9 workflows na lista `workflows:`.

### 2.9 [ORIGEM - R-055 Q2] Blindagem na Origem (Factory, Maintainer e Catálogo de Smells)

- **Severidade**: **HIGH (Prevenção Estrutural na Origem — R-055 Q2)**
- **Crítica Arquitetural (Anti-Overengineering / R-066)**:
  - **Por que NÃO criar `type: workflow` separado em `@governance-factory`**: A criação de um novo workflow canônico é um evento arquitetural raro (o ecossistema possui 9 workflows estabilizados), diferente da criação recorrente de `agent`, `skill`, `prompt`, `instruction` ou `hook`. Introduzir um 6º tipo formal `type: workflow` na árvore de decisão do `@governance-factory` e no corpo principal de `.github/skills/governance-factory-patterns/SKILL.md` inflaria permanentemente o contexto estático (system prompt) com instruções raramente acionadas, violando o princípio de *Context Economy* e a regra anti-overengineering (`R-066`).
  - **Solução Canônica via *Progressive Disclosure* (Lazy Reference + Ponteiros Enxutos + Smell de Auditoria)**:
    1. Ancorar as **8 Regras Invariantes de Origem de Workflow** em um arquivo lazy dedicado (`< 150 linhas`): `.github/skills/governance-factory-patterns/references/workflow-invariants.md`.
    2. Adicionar ponteiro enxuto (~3 linhas) na seção de sincronização atômica de `.github/skills/governance-factory-patterns/SKILL.md` e em `.github/agents/governance-factory.agent.md` determinando a leitura sob demanda de `references/workflow-invariants.md` sempre que um workflow for criado ou estruturalmente evoluído.
    3. Adicionar item obrigatório no Checklist de Sincronização de `.github/agents/governance-maintainer.agent.md` exigindo validação contra `references/workflow-invariants.md` e paridade quádrupla ao editar qualquer arquivo em `workflows/*.md`.
    4. Formalizar o **Smell 2.35 — Drift de Paridade e Invariantes de Workflow** em `.github/skills/governance-audit-patterns/SKILL.md`, garantindo que auditorias futuras do `@agent-auditor` inspecionem sistematicamente a paridade quádrupla (`workflows.md` ↔ `workflow-*.md` ↔ `invariantes-e-protocolos.md` ↔ `routing-graph.yaml`), o gate pré-HITL do `@plan-critic` (R-064) e a referência a `R-065` nos loops de revisão.
- **As 8 Regras Invariantes de Origem de Workflow (a constar em `.github/skills/governance-factory-patterns/references/workflow-invariants.md`)**:
  1. **Invariante 1 — Sincronia Quádrupla Obrigatória (R-050)**: Todo workflow criado ou modificado deve manter paridade exata de ID, nome, contagem e numeração de etapas entre: (a) `.github/agents/workflows.md` (índice e matriz), (b) `.github/agents/workflows/workflow-<id>.md` (sub-arquivo detalhado), (c) `.github/agents/workflows/invariantes-e-protocolos.md` (contratos transversais, ex.: § 6.2) e (d) `.github/agents/routing-graph.yaml` (`workflows:` e `metadata.total_workflows`).
  2. **Invariante 2 — Numeração Sequencial Monotônica de Estados**: Os estados em `workflow-<id>.md` devem seguir numeração inteira sequencial estrita (`Estado 1`, `Estado 2`, `Estado 3`...), admitindo sufixo alfabético apenas para sub-ramificações explícitas (ex.: `Estado 5b`), sendo proibida a repetição de números de estado.
  3. **Invariante 3 — Gate Cético Pré-HITL Obrigatório (`@plan-critic` / R-064 / § 10.7)**: Todo workflow que materialize plano em `docs/plans/<tipo>/` via `@docs-engineer` deve incluir explicitamente o passo de revisão cética pré-HITL pelo `@plan-critic` (`Two-Tier Hybrid Gate`, máx. 2 rodadas) **antes** do Gate de Aprovação Humana (`ask_questions`). Exceção canônica única: `WORKFLOW-REQUIREMENTS-TO-CODE` na etapa de requisitos puros.
  4. **Invariante 4 — Guard de Severidade Arquitetural Explícito (R-065 / § 10.2)**: Todo workflow que contenha etapa `quality_review_loop` deve referenciar explicitamente a regra `R-065` (bloqueio por achados `CRITICAL`/`HIGH` dos consultores `*-arch-advisor` e limite de 2 iterações antes de escalonamento humano), mantendo distinção semântica estrita em relação a `R-064` (persistência física de planos, § 10.6).
  5. **Invariante 5 — Nomenclatura Canônica de Planos sem Prefixos Legados (R-064)**: Caminhos de artefatos em `docs/plans/<tipo>/` citados dentro de workflows devem usar exclusivamente o padrão `<AAAAMMDD-HHMMSS>-<slug>.md` (vedados prefixos legados `PLAN-` ou `REQ-` em nomes de arquivos), reservando `REQ-NN` exclusivamente para identificadores internos de requisitos EARS.
  6. **Invariante 6 — Segregação de Execução Pós-HITL por Extensão de Arquivo**: Quando um plano de manutenção ou evolução abranger simultaneamente arquivos declarativos de governança (`.md`, `.yaml`) e testes automatizados (`.py`), o workflow deve particionar a execução pós-HITL em ondas separadas (`@governance-maintainer`/`@governance-factory` restritos a `.md`/`.yaml`; `@python-router` → `@python-test-engineer` para `.py`).
  7. **Invariante 7 — Atualização Atômica de Contadores e Ranges de Catálogo**: Qualquer alteração no total de workflows ou no catálogo de smells deve atualizar no mesmo lote `metadata.total_workflows` em `routing-graph.yaml` e os ranges documentados nos sub-arquivos (ex.: `Smells 2.1 a 2.35`).
  8. **Invariante 8 — Rastreabilidade em Suíte de Testes de Auditoria (`pytest`)**: Toda regra estrutural de workflow deve possuir cobertura automatizada correspondente em `tests/governance_audit/test_workflows_parity_and_gates.py`.
- **Especificação Exata das Mudanças nos 5 Arquivos de Origem**:
  - **Arquivo 1 (NOVO)**: `.github/skills/governance-factory-patterns/references/workflow-invariants.md` — criar documento de referência lazy (`< 150 linhas`) contendo o cabeçalho de escopo e as 8 Invariantes de Criação/Evolução de Workflows listadas acima, além do checklist rápido pré-commit de paridade quádrupla.
  - **Arquivo 2**: `.github/skills/governance-factory-patterns/SKILL.md` — adicionar ponteiro enxuto (~3 linhas) na seção de Sincronização Atômica:
    > `- **Criação ou evolução estrutural de Workflows (.github/agents/workflows*.md)**: carregar obrigatoriamente [references/workflow-invariants.md](references/workflow-invariants.md) e validar as 8 invariantes de origem (paridade quádrupla com routing-graph.yaml, gate @plan-critic R-064 e guard R-065).`
  - **Arquivo 3**: `.github/agents/governance-factory.agent.md` — adicionar ponteiro enxuto (~3 linhas) nas diretrizes de sincronização atômica orientando que demandas esporádicas de criação/evolução de workflow sigam `references/workflow-invariants.md` (sem criar novo `type: workflow`).
  - **Arquivo 4**: `.github/agents/governance-maintainer.agent.md` — adicionar item no Checklist de Sincronização obrigando validar `.github/skills/governance-factory-patterns/references/workflow-invariants.md` e a paridade quádrupla (`workflows.md` ↔ `workflow-*.md` ↔ `invariantes-e-protocolos.md` ↔ `routing-graph.yaml`) sempre que qualquer arquivo de workflow for editado.
  - **Arquivo 5**: `.github/skills/governance-audit-patterns/SKILL.md` — adicionar na seção de Code Smells de Governança o **Smell 2.35 — Drift de Paridade e Invariantes de Workflow**:
    > `### Smell 2.35 — Drift de Paridade e Invariantes de Workflow`
    > `- **Sintoma**: Divergência de contagem/numeração de etapas entre .github/agents/workflows.md, sub-arquivos .github/agents/workflows/workflow-*.md, invariantes-e-protocolos.md e routing-graph.yaml; omissão do passo pré-HITL do @plan-critic em workflows com plano R-064; ou omissão/colisão de R-065 nos estados de quality_review_loop.`
    > `- **Remediação**: Aplicar as 8 invariantes de .github/skills/governance-factory-patterns/references/workflow-invariants.md e validar via pytest tests/governance_audit/test_workflows_parity_and_gates.py.`

---

## 3. Verificação Tridimensional de Impacto Cruzado (R-055: Q1 Peers, Q2 Templates, Q3 Testes) e Checklist C1–C9

### 3.1 Matriz R-055 (Q1, Q2, Q3)

| Dimensão R-055 | Escopo Inspecionado | Resultado da Análise e Ação Planejada |
| :--- | :--- | :--- |
| **Q1 — Peers (Pares Horizontais)** | Todos os sub-arquivos em `.github/agents/workflows/workflow-*.md`, índice `.github/agents/workflows.md`, `.github/agents/workflows/invariantes-e-protocolos.md` e `.github/agents/routing-graph.yaml`. | Os 6 sub-arquivos que materializam planos R-064 foram incluídos em `allowed_files` para receberem simetricamente o passo do `@plan-critic` (H1) e os 3 com `quality_review_loop` receberão a referência explícita a `R-065` (M3). |
| **Q2 — Templates / Origem (Factory, Maintainer e Audit Skill)** | `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`, `.github/agents/workflows/invariantes-e-protocolos.md` (§ 6.2, § 10.2, § 10.6, § 10.7), `.github/skills/governance-factory-patterns/references/workflow-invariants.md` (novo), `.github/skills/governance-factory-patterns/SKILL.md`, `.github/agents/governance-factory.agent.md`, `.github/agents/governance-maintainer.agent.md` e `.github/skills/governance-audit-patterns/SKILL.md`. | Frontmatter R-064 preservado; desambiguação R-065 vs R-064 nos contratos transversais; e **blindagem na origem (§ 2.9)** ancorando as 8 invariantes de workflow em `references/workflow-invariants.md`, ponteiros enxutos no Factory/Maintainer (sem inflar `type: workflow` — R-066) e adição do **Smell 2.35** no catálogo de auditoria. |
| **Q3 — Testes e Validação Automatizada** | `tests/governance_audit/test_workflows_parity_and_gates.py`. | Inclusão de suíte `pytest` dedicada garantindo prevenção de regressão para H1, M1, M2, M3, M4, L1 e L2. |

### 3.2 Conformidade com o Checklist C1–C9 (`agent-conformance-audit`)

| Item | Critério | Status Planejado |
| :--- | :--- | :--- |
| **C1** | Consistência de IDs e referências de agents entre docs e `routing-graph.yaml` | ✅ Preservado (`@plan-critic`, `@docs-engineer`, `@governance-maintainer`, `@agent-auditor`). |
| **C2** | Sincronia de estados e transições de workflows (R-050) | ✅ Corrigido por M1 e M2. |
| **C3** | Preservação de Frontmatter e metadados obrigatórios (R-064) | ✅ Validado. |
| **C4** | Invariantes de Segurança e Guardrails Read-Only (R-025) | ✅ Respeitado (`@agent-auditor` e `@plan-critic` permanecem 100% read-only). |
| **C5** | Confinamento de Escopo de Escrita por Agente | ✅ `@governance-maintainer` edita apenas `.md`/`.yaml`; `.py` segregado para `@python-router`. |
| **C6** | Numeração de Regras Sem Colisão (`R-064` vs `R-065`) | ✅ Corrigido por M3. |
| **C7** | Alinhamento com Catálogo de Smells (`Smells 2.1 a 2.34` + novo `Smell 2.35`) | ✅ Corrigido por L2 e § 2.9 (Q2). |
| **C8** | Conformidade de Nomenclatura de Planos (sem `PLAN-` / `REQ-`) | ✅ Corrigido por M3/M4. |
| **C9** | Cobertura de Testes de Auditoria de Governança (`pytest`) | ✅ Coberto por Q3. |

---

## 4. Separação Estrita de Execução Pós-HITL (Etapa 4)

Em estrita observância ao confinamento de ferramentas e extensões do ecossistema:

1. **Onda 4A — Artefatos Declarativos de Governança e Blindagem na Origem (`@governance-maintainer` / `@governance-factory`)**:
   - Escopo exclusivo de escrita (14 arquivos `.md` e `.yaml` — 9 arquivos de workflow/grafo + 5 arquivos de origem R-055 Q2):
     - `.github/agents/workflows.md`
     - `.github/agents/workflows/invariantes-e-protocolos.md`
     - `.github/agents/workflows/workflow-bug-fix.md`
     - `.github/agents/workflows/workflow-refactoring.md`
     - `.github/agents/workflows/workflow-feature-development.md`
     - `.github/agents/workflows/workflow-governance-maintenance.md`
     - `.github/agents/workflows/workflow-dependency-vulnerability-remediation.md`
     - `.github/agents/workflows/workflow-framework-migration.md`
     - `.github/agents/routing-graph.yaml`
     - `.github/skills/governance-factory-patterns/references/workflow-invariants.md` *(novo arquivo lazy < 150 linhas)*
     - `.github/skills/governance-factory-patterns/SKILL.md`
     - `.github/agents/governance-factory.agent.md`
     - `.github/agents/governance-maintainer.agent.md`
     - `.github/skills/governance-audit-patterns/SKILL.md`
   - **Restrição Crítica**: `@governance-maintainer` e `@governance-factory` **NÃO** podem criar ou editar arquivos `.py`.

2. **Onda 4B — Suíte de Testes Python (`@python-router` -> `@python-arch-advisor` -> `@python-test-engineer`)**:
   - Escopo exclusivo de escrita (1 arquivo `.py`):
     - `tests/governance_audit/test_workflows_parity_and_gates.py`
   - Executado via handoff separado para `@python-router` após ou em coordenação com a atualização declarativa da Onda 4A, respeitando o confinamento de arquivos Python fora de `@governance-maintainer`.

---

## 5. Critérios de Aceite Objetivos e Estratégia de Rollback

### 5.1 Critérios de Aceite (Definition of Done)

- [ ] **CA-01 (H1)**: Todos os 6 sub-arquivos `workflow-*.md` com plano R-064 declaram explicitamente o passo de revisão cética pré-HITL pelo `@plan-critic` (`Two-Tier Hybrid Gate`, ref. `§ 10.7` de `invariantes-e-protocolos.md`) antes da chamada a `ask_questions`.
- [ ] **CA-02 (M1)**: `workflow-governance-maintenance.md` possui estados numerados sequencialmente de `1` a `5` (e `5b`) sem duplicação do `Estado 3`; `workflows.md:100` referencia `WORKFLOW-GOVERNANCE-MAINTENANCE (Estado 5)`; `invariantes-e-protocolos.md:153-155` reflete as 5 etapas.
- [ ] **CA-03 (M2)**: A contagem e numeração de etapas de `WORKFLOW-FRAMEWORK-MIGRATION` estão unificadas entre `workflows.md:100`, `workflows.md:113`, `workflows.md:136`, `workflow-framework-migration.md:109-141`, `invariantes-e-protocolos.md` (§ 6.2) e `routing-graph.yaml`.
- [ ] **CA-04 (M3)**: `R-065` designa sem ambiguidade o Guard de Severidade Arquitetural em `workflows.md` e `invariantes-e-protocolos.md`, e está explicitamente referenciado nos estados de `quality_review_loop` de `workflow-refactoring.md`, `workflow-feature-development.md` e `workflow-framework-migration.md`.
- [ ] **CA-05 (M4)**: Nenhuma referência de arquivo em `docs/plans/` dentro de `workflow-framework-migration.md` utiliza prefixo legado `PLAN-` ou `REQ-`, preservando IDs EARS (`REQ-01`) com nota desambiguadora.
- [ ] **CA-06 (L1 & L2)**: `routing-graph.yaml:185` atualizado para `"9 workflows canônicos (+ 3.A auxiliar)"` e `workflow-governance-maintenance.md:66-69` atualizado para `Smells 2.1 a 2.34` (ou `2.35` após inclusão do novo smell de paridade de workflow).
- [ ] **CA-07 (Q3)**: `pytest tests/governance_audit/test_workflows_parity_and_gates.py` executa com 100% de aprovação (verde).
- [ ] **CA-08 (Origem R-055 Q2 & Smell 2.35)**: Arquivo lazy `.github/skills/governance-factory-patterns/references/workflow-invariants.md` criado (`< 150 linhas`) com as 8 Invariantes de Origem de Workflow; ponteiros enxutos (~3 linhas) adicionados em `.github/skills/governance-factory-patterns/SKILL.md`, `.github/agents/governance-factory.agent.md` (sem criar `type: workflow`) e no Checklist de Sincronização de `.github/agents/governance-maintainer.agent.md`; e **Smell 2.35 — Drift de Paridade e Invariantes de Workflow** documentado em `.github/skills/governance-audit-patterns/SKILL.md`.

### 5.2 Estratégia de Rollback

Caso qualquer validação da §5.1 falhe de forma irrecuperável durante a Etapa 5:

1. **Reversão dos 13 arquivos já rastreados pelo Git (9 de workflow/grafo + 4 de origem)**:
   ```powershell
   git checkout -- .github/agents/workflows.md .github/agents/workflows/invariantes-e-protocolos.md .github/agents/workflows/workflow-bug-fix.md .github/agents/workflows/workflow-refactoring.md .github/agents/workflows/workflow-feature-development.md .github/agents/workflows/workflow-governance-maintenance.md .github/agents/workflows/workflow-dependency-vulnerability-remediation.md .github/agents/workflows/workflow-framework-migration.md .github/agents/routing-graph.yaml .github/skills/governance-factory-patterns/SKILL.md .github/agents/governance-factory.agent.md .github/agents/governance-maintainer.agent.md .github/skills/governance-audit-patterns/SKILL.md
   ```
2. **Remoção explícita dos 2 arquivos novos (não rastreados previamente — referência lazy de invariantes + suíte de teste)**:
   ```powershell
   git clean -f .github/skills/governance-factory-patterns/references/workflow-invariants.md tests/governance_audit/test_workflows_parity_and_gates.py
   Remove-Item -Force .github/skills/governance-factory-patterns/references/workflow-invariants.md, tests/governance_audit/test_workflows_parity_and_gates.py -ErrorAction SilentlyContinue
   ```
3. **Validação de integridade pós-rollback**:
   ```powershell
   git status --porcelain
   pytest tests/governance_audit/ -q
   ```

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Revisor**: `@plan-critic`
- **Tier 1 (Determinístico)**: `PASS`
- **Tier 2 (Semântico/Estrutural)**: `PASS` (após saneamento na Rodada 2/2)
- **Rodadas de Revisão**: `2`
- **Histórico de Rodadas**:
  - **Rodada 1/2 (`NEEDS_REVISION`)**: Identificados 5 apontamentos (1 HIGH em §5.2 sobre comando de rollback com placeholder e tratamento de arquivo untracked; 1 MEDIUM sobre `tier: "standard"` vs `"governance"`; 1 LOW sobre inclusão do próprio plano em `allowed_files`; 2 NITs sobre chaves canônicas de revisão R-064 no frontmatter e nomenclatura `snake_case` do teste `test_subworkflows_with_r064_include_plan_critic_gate`).
  - **Rodada 2/2 (`PASS`)**: Todos os 5 apontamentos foram integralmente saneados por `@docs-engineer`, mantendo `status: "DRAFT"` e `approved: false` até deliberação no Gate de Aprovação Humana (HITL).
