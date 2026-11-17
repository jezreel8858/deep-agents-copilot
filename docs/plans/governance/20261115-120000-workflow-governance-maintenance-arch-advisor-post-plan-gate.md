---
plan_id: "20261115-120000-workflow-governance-maintenance-arch-advisor-post-plan-gate"
plan_type: "governance"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
status: "APPROVED"
approved: true
author: "@agent-auditor"
materialized_by: "@docs-engineer"
reviewer: "@plan-critic"
review_verdict: "PASS_WITH_NITS"
review_tier1: "PASS"
review_rounds: 1
created_at: "2026-11-15T12:00:00Z"
rollback_plan: "git checkout -- .github/agents/agent-router.agent.md .github/agents/backend/database/database-router.agent.md .github/agents/backend/ejb/ejb-router.agent.md .github/agents/backend/python/python-router.agent.md .github/agents/backend/spring-boot/spring-boot-router.agent.md .github/agents/backend/spring-reactive/spring-reactive-router.agent.md .github/agents/backend/struts/struts-router.agent.md .github/agents/frontend/angular/angular-router.agent.md .github/agents/frontend/react/react-router.agent.md .github/agents/backend/database/database-arch-advisor.agent.md .github/agents/backend/ejb/ejb-arch-advisor.agent.md .github/agents/backend/python/python-arch-advisor.agent.md .github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md .github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md .github/agents/backend/struts/struts-arch-advisor.agent.md .github/agents/frontend/angular/angular-arch-advisor.agent.md .github/agents/frontend/react/react-arch-advisor.agent.md .github/agents/tech-solution-architect.agent.md .github/agents/agent-auditor.agent.md .github/agents/docs-engineer.agent.md .github/agents/governance-maintainer.agent.md .github/copilot-instructions.md .github/instructions/README.md .github/instructions/angular-v21-frontend.instructions.md .github/instructions/database.instructions.md .github/instructions/devops.instructions.md .github/instructions/python-backend.instructions.md .github/instructions/react-frontend.instructions.md .github/instructions/spring-boot-backend.instructions.md .github/skills/agent-contracts/SKILL.md .github/skills/agent-contracts/references/detailed-patterns-and-examples.md .github/skills/handoff-governance/SKILL.md .github/skills/handoff-governance/references/detailed-patterns-and-examples.md .github/skills/plan-conformance-patterns/SKILL.md .github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md .github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md .github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md AGENTS.md README.md docs/README.md docs/adr/0011-mcp-server-java-framework-agnostico-langchain4j-agentic.md tests/context_insight_visualizer/test_agent_invocations.py tests/governance_audit/_embedded_runtime_common.py .github/agents/governance-factory.agent.md .github/skills/governance-factory-patterns/SKILL.md .github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md .github/agents/templates/agent-template.md .github/agents/templates/research-agent.md .github/agents/templates/router-agent.md .github/agents/feature-planner.agent.md .github/agents/refactor-planner.agent.md .github/agents/test-strategy.agent.md .github/agents/bug-triage.agent.md .github/agents/requirements-analyst.agent.md tests/governance_audit/test_agent_guardrails_regression.py tests/governance_audit/_helpers.py .github/agents/plan-critic.agent.md .github/agents/pr-gatekeeper.agent.md docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md tests/governance_audit/test_local_project_isolation.py"
allowed_files:
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/backend/database/database-router.agent.md"
  - ".github/agents/backend/ejb/ejb-router.agent.md"
  - ".github/agents/backend/python/python-router.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-router.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-router.agent.md"
  - ".github/agents/backend/struts/struts-router.agent.md"
  - ".github/agents/frontend/angular/angular-router.agent.md"
  - ".github/agents/frontend/react/react-router.agent.md"
  - ".github/agents/backend/database/database-arch-advisor.agent.md"
  - ".github/agents/backend/ejb/ejb-arch-advisor.agent.md"
  - ".github/agents/backend/python/python-arch-advisor.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md"
  - ".github/agents/backend/struts/struts-arch-advisor.agent.md"
  - ".github/agents/frontend/angular/angular-arch-advisor.agent.md"
  - ".github/agents/frontend/react/react-arch-advisor.agent.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/agent-auditor.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/copilot-instructions.md"
  - ".github/instructions/README.md"
  - ".github/instructions/angular-v21-frontend.instructions.md"
  - ".github/instructions/database.instructions.md"
  - ".github/instructions/devops.instructions.md"
  - ".github/instructions/python-backend.instructions.md"
  - ".github/instructions/react-frontend.instructions.md"
  - ".github/instructions/spring-boot-backend.instructions.md"
  - ".github/skills/agent-contracts/SKILL.md"
  - ".github/skills/agent-contracts/references/detailed-patterns-and-examples.md"
  - ".github/skills/handoff-governance/SKILL.md"
  - ".github/skills/handoff-governance/references/detailed-patterns-and-examples.md"
  - ".github/skills/plan-conformance-patterns/SKILL.md"
  - ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md"
  - ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md"
  - ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
  - "AGENTS.md"
  - "README.md"
  - "docs/README.md"
  - "docs/adr/0011-mcp-server-java-framework-agnostico-langchain4j-agentic.md"
  - "tests/context_insight_visualizer/test_agent_invocations.py"
  - "tests/governance_audit/_embedded_runtime_common.py"
  - ".github/agents/governance-factory.agent.md"
  - ".github/skills/governance-factory-patterns/SKILL.md"
  - ".github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md"
  - ".github/agents/templates/agent-template.md"
  - ".github/agents/templates/research-agent.md"
  - ".github/agents/templates/router-agent.md"
  - ".github/agents/feature-planner.agent.md"
  - ".github/agents/refactor-planner.agent.md"
  - ".github/agents/test-strategy.agent.md"
  - ".github/agents/bug-triage.agent.md"
  - ".github/agents/requirements-analyst.agent.md"
  - "tests/governance_audit/test_agent_guardrails_regression.py"
  - "tests/governance_audit/_helpers.py"
  - ".github/agents/plan-critic.agent.md"
  - ".github/agents/pr-gatekeeper.agent.md"
  - "docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md"
  - "tests/governance_audit/test_local_project_isolation.py"
lessons_extracted: true
lessons_applied_to: ["@agent-auditor", "plan-conformance-patterns"]
lessons_at: "2026-11-16"
related-planning-doc: "N/A"
session_id: "sess-20261115-120000-workflow-governance-maintenance-arch-advisor"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-trace-20261115-120000-workflow-governance-maintenance-arch-advisor"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
---

# Plano de Manutencao de Governanca: Unificacao da Cadeia Pos-Plano dos Consultores Arquiteturais (R-064 + R-065)

## 1. Contexto, Diagnostico e Critica Tecnica da Proposta

### 1.1 Diagnostico Empirico Verificado no Workspace

A auditoria estatica realizada sobre os arquivos reais do workspace (`D:/workspace/deep-agents-copilot/`) confirma duas assimetrias operacionais na cadeia de persistencia fisica de planos (R-064) e critica pre-execucao (teto de 2 rodadas definido em `docs/adr/0014-quality-gate-revisor-cetico-universal-pre-hitl-r064.md` e `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`):

1. **Dualidade Residual de Agente Materializador na Etapa 2 de Governanca**:
   - Em `.github/agents/docs-engineer.agent.md` (linha 118) e `.github/copilot-instructions.md` (linha 32), o `@docs-engineer` e estabelecido como o Executor Canonico Universal de Materializacao Fisica para os 14 agentes planejadores, consultores arquiteturais (`*-arch-advisor`), analistas de requisitos e agentes de triagem (todos 100% Read-Only sob R-025).
   - Entretanto, em `.github/agents/agent-router.agent.md` (âncora textual `WORKFLOW-GOVERNANCE-MAINTENANCE` na tabela de workflows canônicos, ~linha 244) e no item `docs/plans/governance/` de `.github/agents/docs-engineer.agent.md` (linha 118), persiste a mencao dupla `@governance-maintainer ou @docs-engineer` para persistencia do plano de governanca, gerando ambiguidade entre a Etapa 2 (materializacao do plano DRAFT em disco) e a Etapa 5 (execucao das mutacoes aprovadas pelo humano).

2. **Ausencia de Gate Pos-Plano Uniforme nos Consultores Arquiteturais (`*-arch-advisor`) e Routers**:
   - Os consultores arquiteturais verificados em disco — `.github/agents/backend/database/database-arch-advisor.agent.md` (linha 58), `.github/agents/backend/ejb/ejb-arch-advisor.agent.md` (linha 62), `.github/agents/backend/python/python-arch-advisor.agent.md` (linha 66), `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md` (linha 74), `.github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md` (linha 60), `.github/agents/backend/struts/struts-arch-advisor.agent.md` (linha 66), `.github/agents/frontend/angular/angular-arch-advisor.agent.md` (linha 66), `.github/agents/frontend/react/react-arch-advisor.agent.md` (linha 81), `.github/agents/tech-solution-architect.agent.md` (linha 1) — estruturam planos arquiteturais (`plan_type: architecture`) e planos de implementacao no Gate 2 (`plan_type: implementation`), mas nao declaram de forma simetrica o retorno obrigatorio ao router com `motivo: "plano_materializacao_pendente"` para acionar `@docs-engineer` → `@plan-critic` → Gate Humano antes do despacho para o desenvolvedor da stack (`stack-developer`).
   - De modo correlato, os routers do sistema — `.github/agents/agent-router.agent.md` (linha 51), `.github/agents/backend/database/database-router.agent.md` (linha 7), `.github/agents/backend/ejb/ejb-router.agent.md` (linha 7), `.github/agents/backend/python/python-router.agent.md` (linha 8), `.github/agents/backend/spring-boot/spring-boot-router.agent.md` (linha 7), `.github/agents/backend/spring-reactive/spring-reactive-router.agent.md` (linha 7), `.github/agents/backend/struts/struts-router.agent.md` (linha 7), `.github/agents/frontend/angular/angular-router.agent.md` (linha 7), `.github/agents/frontend/react/react-router.agent.md` (linha 7) — precisam explicitar essa sequencia pos-plano e distinguir formalmente entre consulta conceitual pura (Q&A) e emissao de plano/blueprint.


- **Âncoras Textuais e Linhas Exatas Verificadas em Disco (Pós-Auditoria Rodada 1)**:
  - `.github/agents/docs-engineer.agent.md:118-130 (especificamente L118 `## 📄 Persistência Física Universal de Planos em docs/plans/<tipo>/ (R-064)`, L120 `Executor Canônico de Materialização Física`, L124 `docs/plans/architecture/`, L125 `docs/plans/implementation/`, L129 `docs/plans/governance/ (plan_type: governance — emitido por @agent-auditor, persistido por @governance-maintainer ou @docs-engineer)` e L130 `Validação Obrigatória de Frontmatter R-064`)`.
  - `.github/agents/agent-router.agent.md (linhas exatas verificadas em disco: `WORKFLOW-GOVERNANCE-MAINTENANCE` em L46, L51, L129, L139, L315; referências a `*-arch-advisor` / `<stack>-arch-advisor` em L51, L208, L250, L424, L425, L426, L427, L428, L429, L430, L431; referências a `@plan-critic` em L237, L238, L437)`.
  - `.github/agents/frontend/angular/angular-router.agent.md (total 114 linhas; referências verificadas em L7, L30, L35, L36, L44, L45, L47, L49, L66)`.
  - Consultores `*-arch-advisor`: `.github/agents/frontend/angular/angular-arch-advisor.agent.md (referências verificadas em L24, L36, L37, L66, L68, L71, L79, L81, L116, L119, L122, L126, L127, L128, L129), .github/agents/backend/python/python-arch-advisor.agent.md (L22, L30, L66, L68, L71, L79, L81, L106, L109, L112, L116, L117, L118, L119, L120, L121, L143) e .github/agents/frontend/react/react-arch-advisor.agent.md (L25, L37, L38, L47, L69, L81, L83, L86, L94, L96, L131, L134, L137, L141, L142, L143, L144)`.
  - `.github/agents/plan-critic.agent.md` (155 linhas totais: L5–L8 escopo nas 8 categorias, L36 Dupla Lente Gate 1/Gate 2, L39–L40 Read-Only R-025 com gravação física por `@docs-engineer`/`@governance-maintainer`, L46–L70 protocolo Two-Tier e enum `review_verdict: PASS | PASS_WITH_NITS | NEEDS_REVISION | ESCALATED_HITL`): **já 100% aderente em disco**, razão pela qual foi removido de `allowed_files` e não possui tarefa de mutação neste plano.

### 1.2 Critica Tecnica da Proposta do Usuario e Refinamentos Incorporados

| Eixo da Proposta | Proposta do Usuario | Avaliacao Tecnica e Refinamento Incorporado |
|---|---|---|
| **Unificacao da Materializacao em `@docs-engineer`** | Tornar `@docs-engineer` o unico agente responsavel por persistir planos em `docs/plans/`, inclusive em `WORKFLOW-GOVERNANCE-MAINTENANCE`. | **Aceito integralmente.** Elimina sobreposicao de responsabilidade: `@docs-engineer` atua na Etapa 2 (persistencia R-064) e `@governance-maintainer` atua na Etapa 5 (mutacao de governanca pos-aprovacao). |
| **Cadeia Pos-Plano para `*-arch-advisor`** | Submeter o plano emitido pelo `*-arch-advisor` a `@docs-engineer` → `@plan-critic` → Gate Humano → `stack-developer`. | **Aceito com salvaguarda Flat Delegation (R-037).** O `*-arch-advisor` nao invoca subagentes diretamente; ele devolve o controle ao router com `motivo: "plano_materializacao_pendente"`. |
| **Isencao de Q&A Consultivo Puro** | Aplicar revisao na saida dos consultores arquiteturais. | **Melhoria Incorporada:** Formalizada a separacao entre **Modo Consultivo Q&A Puro** (duvidas conceituais e trade-offs sem geracao de plano, isento de R-064/R-065) e **Modo Emissao de Blueprint/Plano (Gate 2 / Architecture Plan)** (sujeito obrigatoriamente a R-064 + R-065). |
| **Compatibilidade com `WORKFLOW-BUG-FIX` (R-063)** | Aplicar nos fluxos que acionam `*-arch-advisor`. | **Melhoria Incorporada:** Preserva a proibicao de `docs/plans/architecture/` em bug-fix (R-063), aplicando a cadeia `@docs-engineer` → `@plan-critic` → Gate Humano sobre o plano de implementacao do Gate 2 (`docs/plans/implementation/`). |

---

### 1.3 Análise Crítica da Melhoria: Shift-Left na Factory e Templates para Novos Agents Planejadores e Novas Stacks (R-055 Q1/Q2/Q3)

A auditoria complementar conduzida pelo `@agent-auditor` sobre a solicitação do usuário (*"para novos agents de stacks planejadores também devem nascer com essa definição"*) identificou **3 lacunas estruturais de Shift-Left** que impediriam que futuras stacks ou novos agents planejadores nascessem nativamente com o protocolo pós-plano (`plano_materializacao_pendente` → `@docs-engineer` → `@plan-critic` → Gate de Aprovação Humana R-028/R-064):

1. **Gap (a) — Ausência de injeção pós-plano e detecção de perfil na Factory (`governance-factory.agent.md` e `governance-factory-patterns`)**:
   - Nem `.github/agents/governance-factory.agent.md` nem `.github/skills/governance-factory-patterns/SKILL.md` (e sua referência `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md`) possuíam a regra de **"Detecção de Perfil Arch-Advisor / Planejador R-064"** nos fluxos `type: stack` e `type: agent`. Como resultado, a criação de uma 9ª stack ou de um novo agent planejador geraria prompts sem a cadeia obrigatória de retorno pós-plano ao router com `motivo: "plano_materializacao_pendente"`.
2. **Gap (b) — Templates base incompletos em `.github/agents/templates/`**:
   - Os 3 templates canônicos (`.github/agents/templates/agent-template.md`, `.github/agents/templates/research-agent.md` e `.github/agents/templates/router-agent.md`) não continham o passo completo da cadeia pós-plano (emissão de `plano_materializacao_pendente` pelo planejador/advisor Read-Only R-025 e recepção/encaminhamento no router para `@docs-engineer` → `@plan-critic` → Gate HITL antes de qualquer handoff para implementadores).
3. **Gap (c) — Assimetria nos 5 planejadores transversais Score 0 e listas estáticas nos testes de regressão**:
   - Os 5 planejadores transversais Score 0 (`feature-planner.agent.md`, `refactor-planner.agent.md`, `test-strategy.agent.md`, `bug-triage.agent.md` e `requirements-analyst.agent.md`) já referenciam a materialização física R-064 via `@docs-engineer`, mas ainda não padronizam o gatilho canônico `motivo: "plano_materializacao_pendente"` + sequência explícita `@docs-engineer` → `@plan-critic` → Gate HITL em paridade com os `*-arch-advisor`.
   - Adicionalmente, os testes em `tests/governance_audit/` (`tests/governance_audit/test_agent_guardrails_regression.py` e `test_agent_guardrails_regression.py`) dependiam de listas estáticas de 8 stacks em vez de descoberta dinâmica via `rglob("*-arch-advisor.agent.md")` e `rglob("*-router.agent.md")`, permitindo que uma nova stack fosse adicionada sem cobertura automática do contrato pós-plano.

### 1.4 Diagnóstico e Blindagem Estrutural contra Vazamento de Projetos Locais (R-043 / R-044 — Gaps 1 a 5) (Rastreamento: Gaps 1 a 4 → G-07 | Gap 5 → P-02)

O bloqueio acionado pelo hook `.githooks/pre-commit` evidenciou uma falha sistêmica de isolamento entre o contexto local da IDE e os artefatos versionados do repositório público: a IDE injeta automaticamente os arquivos de `.github/instructions/local/<projeto>.instructions.md` na tag `<instructions>` da sessão de todos os agentes, e faltava um filtro determinístico R-043/R-044 nos planejadores e no materializador (`@docs-engineer`), no Tier 1 do `@plan-critic`, no executor (`@governance-maintainer`) e no porteiro de commit (`@pr-gatekeeper`). Adicionalmente, a auditoria identificou menção nominal a projeto local em `docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md`.

#### Regra de Fronteira Territorial da R-044 e sua Exceção Única Canônica

- **Escopo Bloqueado (Repositório `deep-agents-copilot`)**: A proibição de referenciar nominalmente projetos locais externos (listados em `.github/projects.local.yaml` ou `.github/instructions/local/*.instructions.md` com `path_externo` fora da raiz do `deep-agents-copilot`) e de incluir `.github/instructions/local/**` ou `*.local.*` em `allowed_files` vale **exclusivamente para artefatos e documentos criados dentro da árvore do repositório `deep-agents-copilot`** (`docs/**`, `.github/**`, `tests/**`, `README.md`, `AGENTS.md`, `CLAUDE.md`).
- **Exceção Única Canônica à R-044 (`<path_externo>/docs/**` do Projeto Local)**: Quando um agente (`@docs-engineer`, planejadores, `@plan-critic`) gera ou audita um plano (`<path_externo>/docs/plans/<tipo>/...`) ou documento `.md` (`<path_externo>/docs/...`) **dentro da pasta `docs/` do próprio projeto local externo**, é **100% válido, normal e esperado** referenciar nominalmente o próprio projeto local e listar seus arquivos reais em `allowed_files` e no corpo do documento!

Para erradicar a causa-raiz em todas as camadas do ciclo de vida dos planos e da manutenção de governança — respeitando estritamente essa fronteira territorial —, este plano incorpora a correção dos **5 Gaps Estruturais de Isolamento (R-043 / R-044)**:

- **Gap 1 (Planejadores e `@docs-engineer`)**: Inclusão de cláusula obrigatória tratando `.github/instructions/local/**` e `.github/projects.local.yaml` como contexto local estritamente inerte (gitignored por R-043) para artefatos do repositório `deep-agents-copilot`, terminantemente proibido em `allowed_files` e proibido de ter seus slugs nominais citados em qualquer documento versionado dentro da árvore do `deep-agents-copilot` (`docs/**`, `.github/**`, `tests/**`, `README.md`, `AGENTS.md`, `CLAUDE.md`), exigindo sempre o uso de placeholders genéricos como `[PROJETO-ALVO]` ou `[PROJETO-EXEMPLO]` (R-044) — **com a Exceção Única Canônica** para planos e documentos `.md` gerados dentro da pasta `docs/` do próprio projeto local externo (`<path_externo>/docs/**`), onde referências nominais e arquivos reais em `allowed_files` do projeto local são 100% válidos e esperados.
- **Gap 2 (`@plan-critic` Tier 1 + Rubrica/Checklist C10)**: No Tier 1 determinístico do `@plan-critic` (`.github/agents/plan-critic.agent.md`, `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`, `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` item C10 e `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`), distinguir pelo `plan_path` / caminho de destino:
  - Se o caminho do documento/plano está **dentro do repositório `deep-agents-copilot`** → **BLOQUEAR (`FAIL` / `BLOCKER`)** qualquer referência nominal a projeto local externo (R-044) e qualquer caminho `.github/instructions/local/**` ou `*.local.*` em `allowed_files` (R-043), varrendo o conteúdo integral do plano contra os slugs extraídos dinamicamente de `.github/instructions/local/` e `.github/projects.local.yaml`.
  - Se o caminho do documento/plano está **na pasta `docs/` do próprio projeto local externo (`<path_externo>/docs/**`)** → **PERMITIR (Exceção Única R-044)** referências nominais ao próprio projeto local e caminhos reais de `allowed_files` pertencentes àquele projeto local.
- **Gap 3 (Guardrail Pré-Gravação em `@docs-engineer` e `@governance-maintainer`)**: Proibição estrita de gravar slugs de projetos locais em documentos dentro da árvore do repositório `deep-agents-copilot` (`docs/**` ou `.github/**`) — preservando a Exceção Única para `<path_externo>/docs/**` do próprio projeto local — e proibição de modificar `.github/instructions/local/**` durante manutenções de governança global (R-038 / R-043), além de reverter no disco local qualquer marcação indevida em `.github/instructions/local/*.instructions.md` e sanear o histórico em `docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md`.
- **Gap 4 (`@pr-gatekeeper` Guardrail Pré-Commit R-044)**: Antes de emitir mensagem/comando de commit ou PR no repositório `deep-agents-copilot`, `@pr-gatekeeper` (`.github/agents/pr-gatekeeper.agent.md`) deve executar obrigatoriamente a verificação determinística de isolamento R-043/R-044 sobre os artefatos da árvore do `deep-agents-copilot` (equivalente aos Checks 2, 3 e 5 de `.githooks/pre-commit`) em adição ao guardrail de segredos.
- **Gap 5 (Blindagem em `tests/governance_audit/test_local_project_isolation.py` e `tests/governance_audit/test_agent_guardrails_regression.py`)**: Adicionar asserção estrutural automatizada garantindo que nenhum plano dentro de `docs/plans/**` (árvore do `deep-agents-copilot`) contenha caminhos `.github/instructions/local/**` ou `*.local.*` em `allowed_files` nem slugs de projetos locais, e que `@plan-critic`, `@docs-engineer`, `@governance-maintainer`, `@pr-gatekeeper`, `plan-frontmatter-r064.md` e `planner-preflight-checklist.md` declarem explicitamente tanto o bloqueio R-043/R-044 para a árvore do `deep-agents-copilot` quanto a **Exceção Única R-044 para a pasta `docs/` do projeto local externo (`<path_externo>/docs/**`)**.

## 2. Escopo Estrito (allowed_files) e Blast Radius

Todos os 60 arquivos listados em `allowed_files` foram verificados fisicamente em `D:/workspace/deep-agents-copilot/` via `fs.existsSync`. Nenhum arquivo de `.github/instructions/local/**` integra este escopo (isolamento estrito R-043 / R-044). A tabela abaixo mantém paridade 1:1 absoluta com o array `allowed_files` do frontmatter:

| # | Caminho Relativo (`allowed_files`) | Categoria | Bloco / Tarefa | Status de Verificação e Escopo |
|---|---|---|---|---|
| 1 | `.github/agents/agent-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 2 | `.github/agents/backend/database/database-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 3 | `.github/agents/backend/ejb/ejb-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 4 | `.github/agents/backend/python/python-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 5 | `.github/agents/backend/spring-boot/spring-boot-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 6 | `.github/agents/backend/spring-reactive/spring-reactive-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 7 | `.github/agents/backend/struts/struts-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 8 | `.github/agents/frontend/angular/angular-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 9 | `.github/agents/frontend/react/react-router.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 10 | `.github/agents/backend/database/database-arch-advisor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 11 | `.github/agents/backend/ejb/ejb-arch-advisor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 12 | `.github/agents/backend/python/python-arch-advisor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 13 | `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 14 | `.github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 15 | `.github/agents/backend/struts/struts-arch-advisor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 16 | `.github/agents/frontend/angular/angular-arch-advisor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 17 | `.github/agents/frontend/react/react-arch-advisor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 18 | `.github/agents/tech-solution-architect.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 19 | `.github/agents/agent-auditor.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 20 | `.github/agents/docs-engineer.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 21 | `.github/agents/governance-maintainer.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 22 | `.github/copilot-instructions.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 23 | `.github/instructions/README.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 24 | `.github/instructions/angular-v21-frontend.instructions.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 25 | `.github/instructions/database.instructions.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 26 | `.github/instructions/devops.instructions.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 27 | `.github/instructions/python-backend.instructions.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 28 | `.github/instructions/react-frontend.instructions.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 29 | `.github/instructions/spring-boot-backend.instructions.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 30 | `.github/skills/agent-contracts/SKILL.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 31 | `.github/skills/agent-contracts/references/detailed-patterns-and-examples.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 32 | `.github/skills/handoff-governance/SKILL.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 33 | `.github/skills/handoff-governance/references/detailed-patterns-and-examples.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 34 | `.github/skills/plan-conformance-patterns/SKILL.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 35 | `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 36 | `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 37 | `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 38 | `AGENTS.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 39 | `README.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 40 | `docs/README.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 41 | `docs/adr/0011-mcp-server-java-framework-agnostico-langchain4j-agentic.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 42 | `tests/context_insight_visualizer/test_agent_invocations.py` | Suite de Auditoria Pytest (.py) | P-01 (`[PYTHON_TASKS]`) | Verificacao automatizada de regressao e isolamento R-043/R-044 |
| 43 | `tests/governance_audit/_embedded_runtime_common.py` | Suite de Auditoria Pytest (.py) | P-01 (`[PYTHON_TASKS]`) | Verificacao automatizada de regressao e isolamento R-043/R-044 |
| 44 | `.github/agents/governance-factory.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 45 | `.github/skills/governance-factory-patterns/SKILL.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 46 | `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md` | Artefato de Governanca (.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 47 | `.github/agents/templates/agent-template.md` | Template de Agente (.md) | G-06 / G-07 (`[GOVERNANCE_TASKS]`) | Verificado fisicamente (`fs.existsSync` = true) |
| 48 | `.github/agents/templates/research-agent.md` | Template de Agente (.md) | G-06 / G-07 (`[GOVERNANCE_TASKS]`) | Verificado fisicamente (`fs.existsSync` = true) |
| 49 | `.github/agents/templates/router-agent.md` | Template de Agente (.md) | G-06 / G-07 (`[GOVERNANCE_TASKS]`) | Verificado fisicamente (`fs.existsSync` = true) |
| 50 | `.github/agents/feature-planner.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 51 | `.github/agents/refactor-planner.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 52 | `.github/agents/test-strategy.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 53 | `.github/agents/bug-triage.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 54 | `.github/agents/requirements-analyst.agent.md` | Contrato de Agente (.agent.md) | `[GOVERNANCE_TASKS]` | Verificado fisicamente (`fs.existsSync` = true) |
| 55 | `tests/governance_audit/test_agent_guardrails_regression.py` | Suite de Auditoria Pytest (.py) | P-01 (`[PYTHON_TASKS]`) | Verificacao automatizada de regressao e isolamento R-043/R-044 |
| 56 | `tests/governance_audit/_helpers.py` | Suite de Auditoria Pytest (.py) | P-01 (`[PYTHON_TASKS]`) | Verificacao automatizada de regressao e isolamento R-043/R-044 |
| 57 | `.github/agents/plan-critic.agent.md` | Contrato de Agente (.agent.md) | G-07 (`[GOVERNANCE_TASKS]`) | Blindagem estrutural anti-vazamento de projetos locais (R-043 / R-044) |
| 58 | `.github/agents/pr-gatekeeper.agent.md` | Contrato de Agente (.agent.md) | G-07 (`[GOVERNANCE_TASKS]`) | Blindagem estrutural anti-vazamento de projetos locais (R-043 / R-044) |
| 59 | `docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md` | Plano Historico Saneado (.md) | G-07 (`[GOVERNANCE_TASKS]`) | Saneamento de mencao nominal a projeto local (R-044) |
| 60 | `tests/governance_audit/test_local_project_isolation.py` | Suite de Auditoria Pytest (.py) | P-02 (`[PYTHON_TASKS]`) | Verificacao automatizada de regressao e isolamento R-043/R-044 |

## 3. Decomposicao de Tarefas ([GOVERNANCE_TASKS] e [PYTHON_TASKS])

### 3.1 Bloco `[GOVERNANCE_TASKS]` (Execucao exclusiva por `@governance-maintainer` e `@docs-engineer`)

- **Tarefa G-01 — Router Raiz (`.github/agents/agent-router.agent.md` linha 51)**:
  - Explicitar na secao de Orquestracao Universal de Planos (R-064 / R-065) que qualquer retorno de `*-arch-advisor` ou `@tech-solution-architect` em Modo Emissao de Blueprint/Plano (`motivo: "plano_materializacao_pendente"`) exige a sequencia estrita: `@docs-engineer` (materializacao em `docs/plans/architecture/` ou `docs/plans/implementation/`) → `@plan-critic` (Tier 1 + Tier 2, maximo 2 rodadas) → Gate de Aprovacao Humana (`ask_questions`) → `stack-developer`.
  - Definir `@docs-engineer` como materializador unico das 8 subpastas de `docs/plans/`.

- **Tarefa G-02 — Domain Routers (`.github/agents/agent-router.agent.md`, `.github/agents/backend/database/database-router.agent.md`, `.github/agents/backend/ejb/ejb-router.agent.md`, `.github/agents/backend/python/python-router.agent.md`, `.github/agents/backend/spring-boot/spring-boot-router.agent.md`, `.github/agents/backend/spring-reactive/spring-reactive-router.agent.md`, `.github/agents/backend/struts/struts-router.agent.md`, `.github/agents/frontend/angular/angular-router.agent.md`, `.github/agents/frontend/react/react-router.agent.md`)**:
  - Atualizar a tabela de roteamento e o protocolo pos-consultoria arquitetural nos routers para:
    1. Distinguir **Modo Consultivo Q&A Puro** (resposta direta ao usuario) de **Modo Emissao de Blueprint/Plano (Gate 2 / Architecture Plan)**.
    2. Determinar que, no Modo Emissao de Blueprint/Plano, o router recebe `motivo: "plano_materializacao_pendente"` do `*-arch-advisor`, aciona `@docs-engineer`, aciona `@plan-critic`, apresenta o Gate Humano e somente entao despacha para o `stack-developer` com `active_plan_ref` preenchido e aprovado.
    3. Em `.github/agents/agent-router.agent.md` (âncora textual `WORKFLOW-GOVERNANCE-MAINTENANCE` na tabela de workflows canônicos, ~linha 244): substituir `@governance-maintainer ou @docs-engineer` na Etapa 2 exclusivamente por `@docs-engineer`, mantendo `@governance-maintainer` na Etapa 5.

- **Tarefa G-03 — Familia `*-arch-advisor` e `@tech-solution-architect` (`.github/agents/backend/database/database-arch-advisor.agent.md`, `.github/agents/backend/ejb/ejb-arch-advisor.agent.md`, `.github/agents/backend/python/python-arch-advisor.agent.md`, `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md`, `.github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md`, `.github/agents/backend/struts/struts-arch-advisor.agent.md`, `.github/agents/frontend/angular/angular-arch-advisor.agent.md`, `.github/agents/frontend/react/react-arch-advisor.agent.md`, `.github/agents/tech-solution-architect.agent.md`)**:
  - Padronizar nos 9 agentes a secao **Cadeia Pos-Plano Obrigatoria (R-064 + R-065)**:
    - Reafirmar perfil 100% Read-Only (R-025) e proibicao de invocar `run_subagent` diretamente (Flat Delegation R-037).
    - Exigir que todo blueprint/plano emitido no Gate 2 (`plan_type: implementation`) ou plano arquitetural (`plan_type: architecture`) contenha frontmatter R-064 completo (`author`, `materialized_by: "@docs-engineer"`, `reviewer: "@plan-critic"`, `status: "DRAFT"`, `approved: false`) e encerre com handoff de retorno ao router (`motivo: "plano_materializacao_pendente"`).
    - Proibir encaminhamento direto para `stack-developer` sem `active_plan_ref` revisado por `@plan-critic` e aprovado pelo usuario.

- **Tarefa G-04 — Agentes de Governanca e Materializacao (`.github/agents/docs-engineer.agent.md`, `.github/agents/governance-maintainer.agent.md`, `.github/agents/agent-auditor.agent.md`)**:
  - Em `.github/agents/docs-engineer.agent.md` (linha 118): consolidar `@docs-engineer` como unico materializador das 8 subpastas de `docs/plans/` e documentar o requisito de usar caminho absoluto do workspace no sandbox `ctx_execute`.
  - Em `.github/agents/governance-maintainer.agent.md` e `.github/agents/agent-auditor.agent.md`: alinhar a fronteira entre Etapa 1 (auditoria Read-Only por `@agent-auditor`), Etapa 2 (materializacao fisica por `@docs-engineer`) e Etapa 5 (execucao de `[GOVERNANCE_TASKS]` por `@governance-maintainer`).

  - Atualizar R-064 e R-065 nas instrucoes globais, nas skills estruturais e nos catalogos do repositorio para refletir a cadeia unificada.


#### G-06 — Shift-Left na Factory (`governance-factory`), Templates (`.github/agents/templates/`) e Paridade nos 5 Planejadores Transversais Score 0

- **Contagem Consolidada de Escopo**: `44 arquivos base da cadeia pós-plano + 11 artefatos declarativos de governança (G-06) + 3 artefatos de blindagem R-043/R-044 (G-07) + 2 arquivos de teste pytest (P-01 e P-02) = 60 arquivos únicos`.

- **Arquivos-alvo (11 arquivos)**:
  - `.github/agents/governance-factory.agent.md` (âncoras: `### Detecção de Perfil Router` e `### type: stack — Sub-Catálogo de Domínio Completo`)
  - `.github/skills/governance-factory-patterns/SKILL.md` (âncoras: `### 3.6) Agentes Planejadores e Consultores Read-Only (Materialização Universal R-064 / CA-04)` e `## 6) Topologia para Novas Stacks (Pattern Replicável)`)
  - `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md` (âncora: `### 2.1) Agents de Planejamento — Enforcement R-064 (CA-04)`)
  - `.github/agents/templates/agent-template.md` (âncora: `### 2. Checagem de Escopo, Quando Delegar e Deriva de Intenção (R-042)`)
  - `.github/agents/templates/research-agent.md` (âncora: `### 2. Checagem de Deriva de Intenção (R-042)`)
  - `.github/agents/templates/router-agent.md` (âncora: `## Retorno ao Router (R-042 — Anti Sticky-Session)`)
  - `.github/agents/feature-planner.agent.md` (âncora: `### 4. Halting Condition e Persistência Opt-In (R-033)`)
  - `.github/agents/refactor-planner.agent.md` (âncora: `## 📄 Materialização Universal de Planos e Contrato Read-Only (R-064)`)
  - `.github/agents/test-strategy.agent.md` (âncora: `### 1. Ingestão de Escopo e Identificação de Fluxo`)
  - `.github/agents/bug-triage.agent.md` (âncora: `## Fluxo de Validação de Hipótese`)
  - `.github/agents/requirements-analyst.agent.md` (âncora: `### 4. Persistência de Artefato e Ground Truth (Híbrido Documental)`)
- **Ação canônica**:
  1. **Factory (`governance-factory.agent.md` + `governance-factory-patterns/SKILL.md` + `references/artifact-specs-and-stack-topology.md`)**: Adicionar a diretriz obrigatória **"Detecção de Perfil Arch-Advisor / Planejador R-064"** nos fluxos `type: stack` e `type: agent`. Sempre que o artefato criado for um `<stack>-arch-advisor`, um planejador R-064 (Score 0 Read-Only R-025) ou um `<stack>-router`, injetar compulsoriamente o contrato pós-plano (`motivo: "plano_materializacao_pendente"` → `@docs-engineer` para persistência em `docs/plans/<tipo>/` → `@plan-critic` para validação taxonómica R-055/R-064 → Gate de Aprovação Humana R-028 antes de qualquer handoff de implementação).
  2. **Templates (`agent-template.md`, `research-agent.md`, `router-agent.md`)**: Incluir nos templates base o passo completo da cadeia pós-plano na seção de Retorno ao Router / Roteamento Pós-Plano, garantindo que qualquer novo agent ou router instanciado a partir dos templates já nasça com a cláusula `plano_materializacao_pendente`.
  3. **5 Planejadores Transversais Score 0 (`feature-planner`, `refactor-planner`, `test-strategy`, `bug-triage`, `requirements-analyst`)**: Padronizar a seção `## Retorno ao Router (R-042 — Anti Sticky-Session)` / `## 📄 Persistência Física de Planos (R-064)` para declarar explicitamente o handoff de conclusão de plano com `motivo: "plano_materializacao_pendente"` encadeando `@docs-engineer` → `@plan-critic` → Gate HITL, em paridade 1:1 com os `*-arch-advisor`.


#### G-07 — Blindagem Estrutural Anti-Vazamento de Projetos Locais (R-043 / R-044 — Gaps 1 a 4, Fronteira Territorial e Exceção Única) e Saneamento Histórico [Gaps 1 a 4 → G-07 | Gap 5 → P-02]
- **Alvos Declarativos e Documentais**:
  - `.github/agents/plan-critic.agent.md`, `.github/agents/docs-engineer.agent.md`, `.github/agents/governance-maintainer.agent.md`, `.github/agents/pr-gatekeeper.agent.md`, `.github/agents/agent-auditor.agent.md`, `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`, `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` (item C10) e `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`: inserir cláusula explícita distinguindo a aplicação da R-043/R-044 pelo `plan_path` / caminho de destino do documento ou plano:
    - **Se o caminho do documento/plano está dentro do repositório `deep-agents-copilot`** (`docs/**`, `.github/**`, `tests/**`, `README.md`, `AGENTS.md`, `CLAUDE.md`) → **BLOQUEAR (`FAIL` / `BLOCKER`)** qualquer referência nominal a projeto local externo extraída dinamicamente de `.github/instructions/local/` ou `.github/projects.local.yaml` (R-044, exigindo placeholders neutros como `[PROJETO-ALVO]` ou `[PROJETO-EXEMPLO]`) e **BLOQUEAR (`FAIL` / `BLOCKER`)** qualquer caminho `.github/instructions/local/**` ou `*.local.*` em `allowed_files` (R-043).
    - **Se o caminho do documento/plano está na pasta `docs/` do próprio projeto local externo (`<path_externo>/docs/**`)** → **PERMITIR (Exceção Única R-044)** referências nominais ao próprio projeto local e caminhos reais de `allowed_files` pertencentes àquele projeto local externo, pois é normal, válido e esperado gerar planos (`<path_externo>/docs/plans/<tipo>/...`) ou documentos `.md` (`<path_externo>/docs/...`) no projeto local referenciando seus próprios arquivos.
  - `.github/agents/docs-engineer.agent.md`, `.github/agents/governance-maintainer.agent.md`, `.github/agents/agent-auditor.agent.md`, `.github/agents/templates/agent-template.md`, `.github/agents/templates/research-agent.md` e `.github/agents/templates/router-agent.md`: incorporar guardrail pré-gravação aplicando o bloqueio de escrita de slugs locais exclusivamente aos artefatos versionados dentro do repositório `deep-agents-copilot` (preservando a Exceção Única R-044 para `<path_externo>/docs/**`) e vedando alteração de `.github/instructions/local/**` em workflows de governança global (R-038 / R-043 / R-044), além de reverter no disco local qualquer modificação residual nos arquivos gitignored de `.github/instructions/local/*.instructions.md`.
  - `.github/agents/pr-gatekeeper.agent.md`: exigir execução pré-commit dos checks de isolamento R-043/R-044 sobre o repositório `deep-agents-copilot` (equivalentes aos Checks 2, 3 e 5 de `.githooks/pre-commit`).
  - `docs/plans/bug-triage/20261114-180000-correcao-falhas-github-actions-ci.md`: substituir menção nominal a projeto local pelo placeholder canônico `[PROJETO-ALVO]` (R-044).

### 3.2 Bloco `[PYTHON_TASKS]` (Execucao exclusiva pela triade Python via `@python-developer` → `@python-reviewer`)

- **Tarefa P-01 — Testes de Invariantes de Governanca (`tests/context_insight_visualizer/test_agent_invocations.py`, `tests/governance_audit/_embedded_runtime_common.py`, `tests/governance_audit/_helpers.py`)**:
  - Adicionar testes parametrizados Pytest garantindo que:
    1. Todos os agentes `*-arch-advisor` e `tech-solution-architect` contem referencia explicita a `@docs-engineer`, `@plan-critic` e `plano_materializacao_pendente`.
    2. Todos os routers exigem a passagem por `@docs-engineer` e `@plan-critic` antes do Gate Humano e antes da delegacao para agentes executores.
    3. `.github/agents/agent-router.agent.md` e `.github/agents/docs-engineer.agent.md` atribuem exclusivamente ao `@docs-engineer` a persistencia fisica em `docs/plans/governance/`.

---


- **Extensão de Descoberta Dinâmica e Shift-Left (Melhoria Auditada)**:
  - **Arquivos-alvo de teste**: `tests/governance_audit/test_agent_guardrails_regression.py` e `tests/governance_audit/test_agent_guardrails_regression.py` (âncora: `def test_exhaustive_and_mutually_exclusive_agency_score_classification(all_agents):`).
  - Substituir/complementar listas estáticas de 8 stacks por **descoberta dinâmica** via `Path(".github/agents").rglob("*-arch-advisor.agent.md")` e `Path(".github/agents").rglob("*-router.agent.md")`, garantindo que qualquer 9ª stack futura seja automaticamente auditada no primeiro `pytest`.
  - Adicionar asserções diretas validando que:
    1. Os 5 planejadores transversais Score 0 (`feature-planner.agent.md`, `refactor-planner.agent.md`, `test-strategy.agent.md`, `bug-triage.agent.md`, `requirements-analyst.agent.md`) declaram `plano_materializacao_pendente`, `@docs-engineer` e `@plan-critic`.
    2. Os 3 templates (`.github/agents/templates/{agent-template,research-agent,router-agent}.md`) e a factory (`governance-factory.agent.md`, `governance-factory-patterns/SKILL.md`, `references/artifact-specs-and-stack-topology.md`) contêm a cláusula pós-plano e a regra de Detecção de Perfil Arch-Advisor / Planejador R-064.


- **Tarefa P-02 — Blindagem Automatizada de Isolamento Local em Planos e Guardrails (`tests/governance_audit/test_local_project_isolation.py` e `tests/governance_audit/test_agent_guardrails_regression.py`)**:
  - Adicionar asserções em `tests/governance_audit/test_local_project_isolation.py` verificando:
    1. **Bloqueio na árvore do `deep-agents-copilot`**: nenhum arquivo em `docs/plans/**` (dentro do repositório `deep-agents-copilot`) referencia `.github/instructions/local/**` ou `*.local.*` em `allowed_files` (R-043) nem contém slugs nominais de projetos locais extraídos dinamicamente de `.github/instructions/local/` ou `.github/projects.local.yaml` (R-044).
    2. **Presença documentada da Exceção Única R-044 para `<path_externo>/docs/**`**: as referências normativas `plan-frontmatter-r064.md` e `planner-preflight-checklist.md` (item C10) documentam explicitamente tanto o bloqueio exclusivo para documentos dentro da árvore do `deep-agents-copilot` quanto a **Exceção Única R-044 para a pasta `docs/` do projeto local externo (`<path_externo>/docs/**`)**.
  - Adicionar asserções em `tests/governance_audit/test_agent_guardrails_regression.py` garantindo que `@plan-critic`, `@docs-engineer`, `@governance-maintainer` e `@pr-gatekeeper` declaram explicitamente a guarda de isolamento R-043/R-044 para artefatos do `deep-agents-copilot` e a **Exceção Única R-044 para a pasta `docs/` do projeto local externo (`<path_externo>/docs/**`)**.

## 4. Portao de Reuso Sistemico (R-055 — Q1, Q2, Q3)

- **Q1 (Peers / Agentes da Mesma Familia)**:
  - A mudanca e aplicada simultaneamente em todos os consultores arquiteturais (`.github/agents/backend/database/database-arch-advisor.agent.md`, `.github/agents/backend/ejb/ejb-arch-advisor.agent.md`, `.github/agents/backend/python/python-arch-advisor.agent.md`, `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md`, `.github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md`, `.github/agents/backend/struts/struts-arch-advisor.agent.md`, `.github/agents/frontend/angular/angular-arch-advisor.agent.md`, `.github/agents/frontend/react/react-arch-advisor.agent.md`, `.github/agents/tech-solution-architect.agent.md`) e em todos os routers (`.github/agents/agent-router.agent.md`, `.github/agents/backend/database/database-router.agent.md`, `.github/agents/backend/ejb/ejb-router.agent.md`, `.github/agents/backend/python/python-router.agent.md`, `.github/agents/backend/spring-boot/spring-boot-router.agent.md`, `.github/agents/backend/spring-reactive/spring-reactive-router.agent.md`, `.github/agents/backend/struts/struts-router.agent.md`, `.github/agents/frontend/angular/angular-router.agent.md`, `.github/agents/frontend/react/react-router.agent.md`). Nenhum consultor ou router irmao fica desatualizado.
- **Q2 (Templates, Skills e Catalogos)**:
- **Q3 (Testes Automatizados Pytest)**: (Soma exata: `47 arquivos originais + 11 artefatos declarativos de governança (G-06) + 1 arquivo de teste pytest (P-01: test_agent_guardrails_regression.py) = 60 arquivos únicos`)
  - Os arquivos de teste (`tests/context_insight_visualizer/test_agent_invocations.py`, `tests/governance_audit/_embedded_runtime_common.py`, `tests/governance_audit/_helpers.py`) recebem assercoes de regressao para bloquear em CI qualquer desvio futuro na cadeia `*-arch-advisor` → `@docs-engineer` → `@plan-critic` → Gate Humano → `stack-developer`.

---


- **Complemento Shift-Left (Factory, Templates e Planejadores Transversais — Q1/Q2/Q3)**:
  - **Q1 (Necessidade Real)**: Corrigir apenas os 8 `*-arch-advisor` existentes deixaria uma brecha geracional: ao executar `@governance-factory` (`type: stack` ou `type: agent`), novos planejadores ou uma 9ª stack nasceriam sem `plano_materializacao_pendente`, recriando o mesmo bug estrutural.
  - **Q2 (Conflitos e Sobreposições)**: Não há conflito com o perfil Read-Only (R-025) nem com o teto de tool turns (R-060); ao contrário, padronizar `plano_materializacao_pendente` nos 5 planejadores transversais Score 0, nos 3 templates e na factory elimina a divergência semântica entre planejadores transversais e consultores arquiteturais de stack.
  - **Q3 (Custo vs Benefício)**: O acréscimo de 12 arquivos (`47 arquivos originais + 11 artefatos declarativos de governança (G-06) + 1 arquivo de teste pytest (P-01: test_agent_guardrails_regression.py) = 60 arquivos únicos` em `allowed_files`) tem custo zero de runtime e protege permanentemente a criação de futuros artefatos via descoberta dinâmica `rglob("*-arch-advisor.agent.md")` e `rglob("*-router.agent.md")` na suíte `tests/governance_audit/`.

## 5. Alternativas Consideradas e Rejeitadas

1. **Alternativa A — Criar um agente novo `@plan-persister` dedicado apenas a gravar planos**:
   - **Veredito**: Rejeitada. Infla a topologia de agentes sem ganho de especializacao real, pois `@docs-engineer` ja detem a responsabilidade canonica de autoria e persistencia de artefatos Markdown sob R-064.
2. **Alternativa B — Permitir que `*-arch-advisor` invoque `@docs-engineer` e `@plan-critic` diretamente via `run_subagent`**:
   - **Veredito**: Rejeitada. Viola a invariante de Flat Delegation (R-037) e descaracteriza o perfil estritamente Read-Only (R-025) dos consultores arquiteturais folha.
3. **Alternativa C — Submeter respostas de Q&A conceitual dos `*-arch-advisor` a materializacao e critica formal**:
   - **Veredito**: Rejeitada. Gera latencia e consumo desnecessario de turnos quando o usuario solicita apenas explicacao arquitetural sem emissao de blueprint nem implementacao.
4. **Alternativa D — Manter `@governance-maintainer` como co-materializador na Etapa 2 de Governanca**:
   - **Veredito**: Rejeitada. Mantem ambiguidade de papeis entre quem persiste o plano DRAFT (Etapa 2) e quem executa as mutacoes de governanca apos aprovacao humana (Etapa 5).

---


4. **Alternativa Rejeitada 4 — Corrigir apenas as 8 stacks atuais sem atualizar `governance-factory`, templates e descoberta dinâmica via `rglob`**:
   - *Motivo da rejeição*: Violará a invariante R-064/R-028 assim que uma 9ª stack ou novo agent planejador for instanciado via `@governance-factory` a partir de `.github/agents/templates/`. Além disso, listas estáticas nos testes não detectariam a omissão em novos arquivos `*-arch-advisor.agent.md` ou `*-router.agent.md`.

## 6. Seguranca Agentic (OWASP Top 10 for Agentic Applications 2026)

- **ASI01 (Agent Goal Hijacking)**:
  - Mitigado pelo bloqueio nos routers que proibe acionar `stack-developer` ou `@governance-maintainer` (Etapa 5) quando `active_plan_ref` for `"N/A — pré-plano"`, quando `review_verdict` nao for `APPROVED`/`PASS_WITH_NITS`, ou quando `approved` for `false`.
- **ASI06 (Context & Memory Poisoning)**:
  - Mitigado pela exigencia de persistencia fisica em disco por `@docs-engineer` antes da avaliacao do `@plan-critic`, garantindo que a auditoria opere sobre o arquivo versionavel real e trate `handoff_summary` como contexto informativo inerte (`CLAUSE_CONTEXT_HYDRATION`).
- **ASI07 (Insecure Inter-Agent Communication)**:
  - Mitigado pelo repasse integral do `correlation_context` (`session_id`, `workflow_id`, `workflow_trace_id`, `active_plan_ref`, `parent_plan_ref`) em todos os handoffs entre router, `*-arch-advisor`, `@docs-engineer` e `@plan-critic` (R-042).
- **ASI08 (Cascading Failures)**:
  - Mitigado pelo teto rigido de 2 rodadas de revisao (`review_rounds ≤ 2`) no `@plan-critic` (teto de 2 rodadas definido em `docs/adr/0014-quality-gate-revisor-cetico-universal-pre-hitl-r064.md` e `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`), acionando Circuit Breaker com escalacao humana via `ask_questions` caso persista reprovacao na 2a rodada.

---

## 7. Estrategia de Rollback e Mitigacao de Riscos (C2)
- **Procedimento Deterministico de Rollback Dirigido (Preservando o Plano de Governanca)**:
  Caso qualquer teste da suite de governanca apresente regressao durante ou apos a Etapa 5, a reversao deve atingir exclusivamente os 60 arquivos-alvo do escopo de manutencao listados em `allowed_files` (sem descartar `docs/plans/governance/20261115-120000-workflow-governance-maintenance-arch-advisor-post-plan-gate.md`):
  ```bash
  ```
- **Validacao Exata Pos-Rollback e Quality Gate Pytest**:
  ```bash
  pytest tests/governance_audit/test_universal_plan_materialization_governance.py tests/governance_audit/test_r064_arch_advisor_gate.py tests/governance_audit/test_pre_hitl_skeptical_plan_gate.py tests/governance_audit/test_agent_guardrails_regression.py -q
  ```
- **Controle de Blast Radius**:
  Como a mudanca afeta exclusivamente contratos Markdown/YAML de governanca e testes estaticos Pytest listados em `allowed_files`, o risco para codigo de aplicacao em producao e zero.

---

## 8. Criterios de Aceite e Cenarios Gherkin (C4)

### Cenario 1: Fluxo Completo Pos-Plano de Consultor Arquitetural (`*-arch-advisor`)
- **Dado** que um consultor da familia `*-arch-advisor` elaborou um plano de implementacao (`plan_type: implementation` no Gate 2) ou plano arquitetural (`plan_type: architecture`)
- **Quando** o consultor concluir sua resposta Read-Only e retornar ao router com `motivo: "plano_materializacao_pendente"`
- **Entao** o router deve delegar ao `@docs-engineer` a gravacao fisica do arquivo em `docs/plans/` com `materialized_by: "@docs-engineer"`
- **E** apos a gravacao deve delegar ao `@plan-critic` a validacao Tier 1 e Tier 2
- **E** somente após o `@plan-critic` emitir `review_verdict: "PASS"` ou `review_verdict: "PASS_WITH_NITS"` (persistido no plano por `@docs-engineer`) e o humano confirmar via `ask_questions` no Gate 2 (transicionando o frontmatter para `status: "APPROVED"` e `approved: true`), o router deve acionar o `stack-developer`.

### Cenario 2: Reprovacao pelo `@plan-critic` (`NEEDS_REVISION`)
- **Dado** um plano materializado em `docs/plans/` por `@docs-engineer`
- **Quando** o `@plan-critic` identificar falha em qualquer rubrica normativa (conforme `docs/adr/0014-quality-gate-revisor-cetico-universal-pre-hitl-r064.md`, `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` e `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`) e emitir `review_verdict: "NEEDS_REVISION"` na rodada 1
- **Entao** o router deve interromper o avanco para o Gate de Aprovacao Humana e para o `stack-developer`
- **E** deve retornar os achados para ajuste e re-materializacao por `@docs-engineer` respeitando o limite maximo de 2 rodadas (teto de 2 rodadas definido em `docs/adr/0014-quality-gate-revisor-cetico-universal-pre-hitl-r064.md` e `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`).

### Cenario 3: Bloqueio de Execucao Sem Plano Aprovado
- **Dado** um pedido de implementacao em qualquer stack que exija Gate 2
- **Quando** `active_plan_ref` estiver ausente ou o plano possuir `approved: false`
- **Entao** o router deve bloquear a invocacao do `stack-developer` e iniciar obrigatoriamente a cadeia `*-arch-advisor` → `@docs-engineer` → `@plan-critic` → Gate Humano.

### Cenario 4: Isencao para Consulta Conceitual Pura (Q&A)
- **Dado** que o usuario formulou uma duvida conceitual de arquitetura sem solicitar blueprint nem implementacao de codigo
- **Quando** o `*-arch-advisor` atuar em Modo Consultivo Q&A Puro
- **Entao** a resposta deve ser apresentada diretamente ao usuario sem materializacao em `docs/plans/` e sem acionamento do `@plan-critic`.

---


### Cenario 5: Propagacao Shift-Left na Factory e Templates para Novos Agentes
- **Dado** que `@governance-factory` cria ou audita um template/contrato de consultor arquitetural ou planejador
- **Quando** as invariantes R-064/R-065 e R-043/R-044 sao verificadas
- **Entao** o contrato gerado ja nasce com o handoff pos-plano (`@docs-engineer` → `@plan-critic` → Gate HITL) e com o filtro de isolamento de projetos locais integrado.

### Cenario 6: Bloqueio Deterministico de Vazamento de Projetos Locais na Arvore do `deep-agents-copilot` e Excecao Unica para `<path_externo>/docs/**` (R-043 / R-044)
- **Dado** um plano ou documento `.md` submetido a materializacao (`@docs-engineer`), revisao cetica Tier 1 (`@plan-critic` — item C10 de `planner-preflight-checklist.md` e `plan-frontmatter-r064.md`) ou preparacao de commit/PR (`@pr-gatekeeper`)
- **Quando** o `plan_path` / caminho de destino estiver **dentro da arvore do repositorio `deep-agents-copilot`** (`docs/**`, `.github/**`, `tests/**`, `README.md`, `AGENTS.md`, `CLAUDE.md`) e `allowed_files` contiver qualquer caminho `.github/instructions/local/**` ou `*.local.*`, ou o corpo do documento contiver qualquer slug nominal extraido dinamicamente de `.github/instructions/local/` ou `.github/projects.local.yaml`
- **Entao** o Tier 1 deterministico do `@plan-critic` deve reprovar imediatamente o plano com `review_tier1: "FAIL"` (`BLOCKER` — item C10) antes do Gate HITL e o `@pr-gatekeeper` deve bloquear a emissao do commit/PR exigindo saneamento para `[PROJETO-ALVO]`
- **Mas quando** o `plan_path` / caminho de destino do plano ou documento `.md` estiver **dentro da pasta `docs/` do proprio projeto local externo (`<path_externo>/docs/**`)**, o `@docs-engineer` e o `@plan-critic` devem **permitir integralmente (Excecao Unica Canonica a R-044)** referencias nominais ao proprio projeto local e caminhos reais de `allowed_files` pertencentes aquele projeto local externo.
---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Revisor**: `@plan-critic`
- **Veredito**: `PASS_WITH_NITS` (`review_tier1: "PASS"`, `review_rounds: 1`)
- **Contagem de Achados**: `0 BLOCKER`, `0 HIGH`, `2 LOW (Nits incorporados)`
- **Resumo da Revisão**:
  1. **Conformidade Estrutural e R-064 (Tier 1 — PASS)**: Frontmatter YAML válido com `status: "DRAFT"`, `approved: false`, `author: "@agent-auditor"`, `plan_type: "governance"` e `allowed_files` completo cobrindo os 12 arquivos do escopo.
  2. **Isolamento Zero-Contaminação (R-013 / G-06 — PASS)**: Verificado que o plano e os artefatos propostos permanecem com 0 menções a slugs de projetos locais em `.github/instructions/local/` (utilizando apenas placeholders neutros como `[PROJETO-ALVO]` ou `<slug-local>`).
  3. **Ajustes Incorporados (Nits)**:
     - **Ajuste #1**: Explicitado o rastreamento `Gaps 1 a 4 → G-07 | Gap 5 → P-02` na Seção 1.4 e no cabeçalho de `G-07`.
     - **Ajuste #2**: Removido o campo `approved_at` do frontmatter enquanto o plano aguarda deliberação no Gate Humano (HITL) em `status: "DRAFT"`.
