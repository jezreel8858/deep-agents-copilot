# CHANGELOG — Deep Agents Copilot (Estrutura de Governança Genérica e Reutilizável

Todas as mudanças significativas nesta base de governança são documentadas aqui.

Formato: [Semantic Versioning](https://semver.org/) | [Conventional Commits](https://www.conventionalcommits.org/)

---

## [2.0.0] — 2026-09-06

### Adicionado
- **Arquitetura Hierárquica de Routers de Domínio**: Decomposição de agentes monolíticos em ecossistemas de domínio com sub-catálogos locais e isolamento em pastas:
  - **Frontend Angular (`.github/agents/frontend/angular/`)**: Supervisor `angular-router` + sub-catálogo `angular-catalog.yaml` + 8 especialistas (`angular-arch-advisor`, `angular-feature-developer`, `angular-bug-fixer`, `angular-ui-stylist`, `angular-unit-test-writer`, `angular-component-test-writer`, `angular-test-fixer`, `angular-e2e-writer`).
  - **Backend Spring Boot (`.github/agents/backend/spring-boot/`)**: Supervisor `spring-boot-router` + sub-catálogo `spring-boot-catalog.yaml` + 7 especialistas (`spring-boot-arch-advisor`, `spring-boot-feature-developer`, `spring-boot-bug-fixer`, `spring-boot-perf-tuner`, `spring-boot-unit-test-writer`, `spring-boot-integration-test-writer`, `spring-boot-test-fixer`).
  - **Backend Spring Reactive (`.github/agents/backend/spring-reactive/`)**: Supervisor `spring-reactive-router` + sub-catálogo `spring-reactive-catalog.yaml` + 7 especialistas (`spring-reactive-arch-advisor`, `spring-reactive-feature-developer`, `spring-reactive-bug-fixer`, `spring-reactive-resilience-tuner`, `spring-reactive-unit-test-writer`, `spring-reactive-integration-test-writer`, `spring-reactive-test-fixer`).
  - **Backend Java Legado EJB (`.github/agents/backend/ejb/`)**: Supervisor `ejb-router` + sub-catálogo `ejb-catalog.yaml` + 7 especialistas (`ejb-arch-advisor`, `ejb-feature-developer`, `ejb-bug-fixer`, `ejb-perf-tuner`, `ejb-unit-test-writer`, `ejb-integration-test-writer`, `ejb-test-fixer`).
- **Suporte a `type: stack` no `@governance-factory`**: Nova capacidade de geração de ecossistemas tecnológicos completos estruturados em pastas de domínio com sub-catálogo, router e especialistas canônicos, com pesquisa prévia compulsória via `@deep-search` e sincronização atômica global (R-015).
- **Smell 2.7 (Desalinhamento Contratual: Perfil ↔ Tools ↔ Skills ↔ Catálogo) em `governance-audit-patterns`**: Nova regra de conformidade com Matriz Canônica § 2.7.1 auditando papéis, permissões de escrita, tooling de terminal (`terminal-governance`), MCP `context-mode` e sincronismo atômico com o catálogo. Remediação executada com 100% de conformidade nos 33 agentes de frontend e backend.
- **Dois Fluxos Canônicos de TDD com `@test-strategy`**:
  - *Fluxo 1 (Cross-cutting Gateway)*: `@agent-router` aciona `@test-strategy` para matriz unificada antes de despachar aos routers de frontend/backend.
  - *Fluxo 2 (Consulta Interna de Domínio)*: Routers de domínio consultam `@test-strategy` internamente via `run_subagent` antes de acionar seus test-writers.

### Removido
- Descomissionamento dos agentes monolíticos substituídos pela nova topologia hierárquica: `angular-engineer.agent.md`, `spring-boot-engineer.agent.md`, `spring-reactive-engineer.agent.md` e `test-engineer.agent.md`.

---

## [1.9.0] — 2026-09-04

### Adicionado
- **`tools/context-insight-visualizer/`**: Suíte analítica completa e dashboard standalone (HTML/CSS/JS puro com design tokens do Angular Material 3 Dark Theme e gerador em Python) para métricas locais do Context Mode MCP (`sessions/*.db`, `stats-pid-*.json`, `content/*.db`). Replicando a arquitetura validada de `tools/codegraph-visualizer/` (zero dependências npm em runtime, zero lock-in SaaS, execução offline via `file://`).
  - **Sidebar M3 com 5 Visões Profissionais**:
    - `Dashboard`: Top KPIs (Sessões, R:W Ratio, Compact Rate, Error Rate, PPS), Heatmap 24h ("When You Code"), Volume temporal e cards de Insights determinísticos (`Nice`, `Heads up`, `Fix this`, `FYI`).
    - `Knowledge Base`: Catálogo de 250+ fontes indexadas agrupadas por recência (*Hoje, Ontem, Esta Semana, Anteriores*), proporção de código e modal de inspeção de chunks.
    - `Sessions & Decisions`: Auditoria cronológica de sessões, timeline de eventos com prioridade e **Diário de Decisões Técnicas** com exportação direta para Markdown (`.md`).
    - `Search`: Mecanismo de busca unificado na memória local com destaque em tempo real sobre fontes, decisões técnicas e sessões.
    - `Enterprise`: Painel executivo com matriz de personas de liderança (CTO, EM, DevEx, CISO, QA, Developer) calculando ROI, economia financeira e conformidade.
  - `schemas/insight-data.schema.json`: contrato formal de dados unificado (JSON Schema draft 2020-12) validando todas as estruturas.
  - `generator/`: motor de extração multi-DB com fallback de diretórios, cálculo de KPIs executivos, diário de decisões e empacotador de HTML.

---

## [1.8.0] — 2026-08-30

### Adicionado
- **`agent-contracts/SKILL.md` § 0 — Banner Universal de Identidade (Visibilidade de Fluxo)**: nova regra de ouro — toda resposta de TODO agent (não apenas `agent-router`) abre com `Agente Ativo: <name>`; se resultado de handoff/re-triagem, uma segunda linha declara `Handoff: <origem> → <destino> (motivo: ...)`. Baseado em pesquisa de mercado 2026 (Tavily): LangGraph "Stream the Active Agent" (campo `active_agent` no state, streamado ao usuário) e OpenAI Agents SDK (`HandoffOutputItem` imprimindo "Handed off from X to Y").
- **`agent-router.agent.md`**: novo campo `Transição` no Formato de Saída, explicitando "Nova triagem (1º turno)" | "`<origem>` → `<atual>` (motivo: deriva_de_intencao)" | "Sem mudança".

### Corrigido
- **Gap de visibilidade em R-042**: antes desta correção, apenas o `agent-router` declarava "Agente Ativo" — um agent downstream em `task_mode` por vários turnos consecutivos não reafirmava quem estava respondendo, deixando o usuário sem visibilidade do fluxo. Corrigido nos 23 agents downstream (parágrafo "Banner obrigatório" inserido na seção já existente "Retorno ao Router", via script Node.js determinístico) e nos 2 templates (`research-agent.md`, `operational-agent.md`) usados pelo `agent-factory` para gerar novos agents.

### Alterado
- **`agent-factory.agent.md`**: Padrões Obrigatórios (item 10), Checklist e Formato de Saída passam a validar a presença do banner em todo agent criado/revisado.
- **`CLAUDE.md` (R-042)**, **`copilot-instructions.md`** (fluxo garantido) e **`agents/README.md`** § 8 — formalizam a exigência de visibilidade turno a turno.
- **`handoff-governance/SKILL.md`** § 5.2 — referência cruzada ao banner de identidade.

---

## [1.7.0] — 2026-08-30

### Corrigido
- **Gap estrutural de tooling para R-042**: `run_subagent` era ausente no frontmatter `tools:` de 3 agents (`agent-factory`, `adapter-generator`, `binding-initializer`) — sem essa tool, o handoff de retorno a `@agent-router` descrito em prosa na seção "Retorno ao Router" nunca era executável de fato. Corrigido nos 3 agents.
- **Causa raiz nos templates**: `templates/research-agent.md` (tools com nomenclatura não-canônica `[Read, Grep, Glob]`, sem `run_subagent`, sem seção "Retorno ao Router") e `templates/operational-agent.md` (sem `run_subagent`, seção "Retorno ao Router" totalmente ausente) — todo agent novo criado por `agent-factory` herdava o gap. Ambos corrigidos.

### Adicionado
- **`agent-contracts/SKILL.md` § 9 — Ferramentas Mínimas por Agent (Tooling Baseline)**: tabela de tools mínimas obrigatórias por perfil (Router, Analista, Especialista, Operacional); regra de ouro — `run_subagent` é obrigatório e bloqueante em TODO agent, sem exceção.
- **`agent-factory.agent.md`**: valida a nova regra em Padrões Obrigatórios (itens 8-9), Checklist Antes de Codar e Formato de Saída — nenhum agent é finalizado sem `run_subagent` no frontmatter e sem a seção "Retorno ao Router".

### Alterado
- **`CLAUDE.md` (R-042)**, **`copilot-instructions.md`** e **`agents/README.md`** § 8 — adicionado o pré-requisito estrutural: o handoff de retorno só é efetivo via chamada real de `run_subagent`, não apenas descrito em texto.

---

## [1.6.0] — 2026-08-30

### Alterado
- **Especialistas `angular`, `spring-boot`, `spring-reactive` migrados de perfil "advisory puro" para perfil HÍBRIDO (v2.0.0)**: além de análise/recomendação, agora também implementam feature nova e correção de bug dentro do próprio domínio de stack, seguindo padrões de mercado consolidados via pesquisa Tavily 2026.
- **Testing-first obrigatório** em modo Implementação: nenhum dos 3 agents pode reportar sucesso sem teste escrito/atualizado e suíte executada localmente.
- **`agent-router` / `routing-graph.yaml` / `CLAUDE.md` (R-042)**: condição `intent_drift_detected` ajustada — implementação **dentro** do domínio de stack do specialist não é mais deriva de intenção; deriva só ocorre em pivô **cross-stack** (ex.: `@angular` recebe pedido de código Spring Boot) ou pedido fora do domínio técnico.

### Adicionado
- **3 novas skills de implementação** (Tier 2, pesquisa de mercado 2026 via Tavily):
  - `angular-implementation-patterns` — fronteira Signals/RxJS, testing-first, checklist de PR.
  - `spring-boot-implementation-patterns` — matriz de decisão virtual threads vs reativo, N+1/OSIV, DTOs de borda.
  - `spring-reactive-implementation-patterns` — composição não-bloqueante, operadores de erro (`onErrorResume`/`onErrorMap`/`retryWhen`), `StepVerifier`/`WebTestClient`.
- **`tools:`** dos 3 agents expandidas com `create_file`, `insert_edit_into_file`, `get_errors`, `run_in_terminal`.
- **`docs/ai-context/evals/casos-roteamento.yaml`**: `canon-018` (implementação direta de bugfix), `regr-014` corrigido (implementação no próprio domínio não é deriva), `regr-016` novo (deriva real cross-stack) — suíte 40 → 42 casos.

### Corrigido
- **SYNC (R-015)**: `.github/skills/.index.json` — corrigido gap pré-existente onde as 3 skills de análise (`angular-frontend-patterns`, `spring-boot-backend-patterns`, `spring-reactive-webflux-patterns`) nunca haviam sido registradas; total_skills 39 → 45 (3 análise + 3 implementação novas).
- **SYNC**: `catalog.yaml` (agents), `agents/README.md`, `copilot-instructions.md`, `handoff-governance/SKILL.md` § 5 — todas as referências a "sem implementação"/"advisory puro" para os 3 specialists atualizadas para refletir o perfil híbrido.

---



### Adicionado
- **R-042 (Re-triagem Obrigatória por Turno — Anti Sticky-Session)**: R-037 passa a se aplicar explicitamente a **cada novo turno**, não só ao primeiro. Fecha o gap relatado onde um agent downstream (ex.: `requirements-analyst`) continuava respondendo sozinho mesmo quando o pedido do usuário mudava de fase (requisito→implementação, análise→código, revisão→correção).
- **Seção "Retorno ao Router"** adicionada nos 23 agents downstream/specialist (atualização atômica, R-015): cada agent declara gatilho objetivo de deriva de intenção e retorna a `@agent-router` via handoff (`handoff-governance` § 2.1, `motivo: "deriva_de_intencao"`) em vez de prosseguir fora do próprio escopo.
- **`agent-router.agent.md` v1.5.0**: novo PASSO 0.3 na Decision Tree (checagem de deriva quando há agent ativo de turno anterior); output com campo `Agente Ativo` para auditoria; roteamento direto para `angular`/`spring-boot`/`spring-reactive` (antes órfãos — só alcançáveis por `@menção` manual, nunca roteados pelo próprio router).
- **`docs/ai-context/routing-graph.yaml`**: 3 novos nós `specialist_advisory` (`angular`, `spring-boot`, `spring-reactive`) + arestas de entrada a partir do router; nova aresta reversa universal `de: *downstream → para: agent-router` (condição `intent_drift_detected`, prioridade 0) aplicável a todo nó `downstream`/`specialist_advisory`.
- **`handoff-governance/SKILL.md`**: § 5 nova linha de escalonamento para mudança de fase na mesma conversa; nova § 5.2 "Anti Sticky-Session (R-042)".
- **`docs/ai-context/evals/casos-roteamento.yaml`**: `canon-015/016/017` (specialists agora roteáveis) + `regr-014/015` (regressão de sticky-session, 2 turnos) — suíte passa de 35 para 40 casos.

### Corrigido
- Gap de catálogo: `angular`, `spring-boot` e `spring-reactive` já existiam em `catalog.yaml`/`README.md` mas nunca haviam sido registrados como nós roteáveis em `routing-graph.yaml` nem na Decision Tree do `agent-router` — corrigido.
- **SYNC (R-015)**: `agents/catalog.yaml` (`related_agents: agent-router` adicionado aos 3 specialists), `agents/README.md` (nota R-042 em Diretrizes Transversais), `CLAUDE.md`, `.github/copilot-instructions.md`.

### Pesquisa de mercado (base da decisão)
- OpenAI Agents SDK — padrão `handoff()` + `transfer_back_to_*` (retorno explícito de controle).
- LangGraph `langgraph-supervisor` — `create_handoff_tool` + `add_handoff_back_messages`.
- Padrão de state machine de 2 modos (`orchestrator_mode`/`task_mode`) com detecção conservadora de deriva de tópico (Orchestrator Pattern, 2026).

---



### Adicionado
- **Agent `requirements-analyst`**: perfil de elicitação prospectiva para transformar pedido de negócio ambíguo em requisitos funcionais/não-funcionais estruturados e testáveis, com rastreabilidade da fonte; aplica mediação contra *solution-jumping* (Five Whys) antes de qualquer decisão técnica
- **Skill `requirements-engineering-patterns`** (Tier 2): base de conhecimento consolidada via pesquisa de mercado (ISO/IEC/IEEE 29148, EARS, INVEST, Gherkin/BDD, FURPS+, regra de singularidade INCOSE)
- **`docs/ai-context/routing-graph.yaml`**: novo nó + aresta `agent-router → requirements-analyst` (R-040), com `nao_confundir_com` cruzado para evitar colisão com `business-rules-extractor` e `impact-architect`
- **`docs/ai-context/evals/casos-roteamento.yaml`**: `canon-014` (roteamento correto para `requirements-analyst`), `regr-012` e `regr-013` (não-confusão `requirements-analyst` × `business-rules-extractor`) — suíte passa de 32 para 35 casos
- **`agent-router.agent.md`**: nova ramificação na Decision Tree para elicitação de requisito novo; bump `version: 1.3.0 → 1.4.0`

### Corrigido
- **SYNC de catálogos (R-015/R-040)**: atualização atômica de `agents/catalog.yaml` (23 → 24 agents), `skills/.index.json` (38 → 39 skills), `agents/README.md` e `skills/README.md` para refletir o novo perfil de requisitos
- **`README.md`** consolidado para refletir o estado real: 24 agents, 39 skills, 35 casos de roteamento e distinção explícita de escopo entre `requirements-analyst` (pedido → requisito) e `business-rules-extractor` (código → regra)

### Conformidade
- Mantida separação de responsabilidades sem duplicação (R-003): `requirements-analyst` opera em requisito **novo/prospectivo**; `business-rules-extractor` permanece no fluxo **reverso** (código existente)

---

## [1.3.0] — 2026-08-29

### Adicionado
- **Agent `docs-writer`**: Perfil documentador agnóstico de domínio — gera/atualiza documentação técnica em Markdown (Diátaxis, ADR/MADR, README, runbook, postmortem); produz exclusivamente arquivos `.md`; nunca alucina comportamento não verificado no código-fonte
- **Skill `documentation-writing-patterns`** (Tier 2): base de conhecimento consolidada via pesquisa de mercado (Diátaxis, Google/Microsoft Style Guide, MADR, standard-readme, `llms.txt`, anti-alucinação Anthropic/Copilot/Cursor) — base do `docs-writer`
- **`docs/ai-context/routing-graph.yaml`**: novo nó + aresta `agent-router → docs-writer` (R-040), com `nao_confundir_com` cruzado em relação a `docs-curator`
- **`docs/ai-context/evals/casos-roteamento.yaml`**: `canon-012` (roteamento correto para `docs-writer`), `regr-008` e `regr-009` (não-confusão `docs-writer` × `docs-curator`) — suíte passa de 23 para 29 casos
- **`agent-router.agent.md`**: nova ramificação na Decision Tree (escrita de doc nova vs. curadoria existente) — bump `version: 1.1.0 → 1.2.0`

### Corrigido
- **SYNC (auditoria de tools/perfis dos 21 agents)**: corrigido typo `@analysis-integration-architect` → `@analysis-architect` em 2 skills (`dependency-graph-mapping`, `integration-contract-analysis`) no `.index.json`
- **SYNC**: `related_agents` de `context-mode`, `tavily`, `code-tracing` e `prompt-engineering-patterns` expandidos no `.index.json` para refletir `tools:` reais declaradas em cada agent
- **SYNC**: seção "Docs Sempre Anexadas" (pre-fetch) completada em 8 agents (`research-router`, `agent-router`, `analysis-architect`, `impact-architect`, `refactor-planner`, `test-strategy`, `bug-triage`, `skill-factory`) — skills usadas nas `tools:` não estavam referenciadas no pre-fetch
- **SYNC**: `catalog.yaml` (`related_skills`) alinhado ao pre-fetch de `impact-architect`, `refactor-planner` e `test-strategy`
- **README.md**: consolidado para refletir estado real — 22 agents (antes citava 17), 37 skills (antes citava 29), remoção de referência ao agent já unificado `analysis-integration-architect`, contagem de casos de evals (23 → 29), diagrama Mermaid atualizado com `docs-writer`

### Conformidade
- Decisão de escopo registrada: **não** foi adicionado campo `profile:` no frontmatter dos agents — `agent-contracts/SKILL.md` § 8 já é fonte única de verdade para o mapeamento perfil → template de saída (evita duplicação — R-003)

---

## [1.2.0] — 2026-06-12

### Adicionado
- **Prompt `/commit`**: Gera mensagem Conventional Commits (PT-BR) sem executar git autonomamente
- **Prompt `/review`**: Revisão de código por qualidade, convenções e impacto com relatório por severidade
- **Prompt `/health`**: Health check completo da governança (binding, agents, skills, R-038)
- **Agent `skill-factory`**: Criar/revisar skills com padrão SKILL.md e atualização atômica do `.index.json`
- **Skill `git-governance`**: Convenções de branch naming, commit standards e PR guidelines
- **`docs/ai-context/catalog.yaml`**: Binding instanciado para o ecossistema
- **`docs/ai-context/binding.md`**: Documentação do binding ativo
- Diagrama Mermaid no README.md mostrando fluxo completo de agents

### Corrigido
- **SYNC**: `.index.json` com `total_agents: 10` (corrigido para 15) e 2 skills sem entrada (`project-scanner`, `project-context-builder`)
- **SYNC**: `copilot-instructions.md` § 4.1 ainda mencionava "5 perguntas" após simplificação para 1

### Conformidade R-038
- Todos os arquivos de governança agora seguem o padrão de genericidade obrigatória (R-038)
---

## [1.1.0] — 2026-06-11

### Adicionado
- **Prompt `/init-context` v1.1**: PASSO 2 informativo (não bloqueante), PASSO 3 condicional por sessão, PASSO 4 lista projetos por nome
- **Simplificação `binding-initializer`**: 5 perguntas → 1 pergunta (só nome do ecossistema)
- **Desacoplamento `adapter-generator`**: Removido auto-disparo pelo `binding-initializer` — apenas chamado por `/add-project-context`
- **Guardrail de confinamento**: Todos os arquivos gerados ficam exclusivamente no repositório de governança
- **Naming de adapters**: Padrão `<nome-projeto>.instructions.md` (sem sufixo de stack)
- Source_docs do `/init-context` agora inclui `docs/ai-context/catalog.yaml`
- PASSO 3 do `/init-context` condicional: sessão recorrente mostra top-5; primeira execução mostra todas

### Corrigido
- `add-project-context`: reduzido de 4 para 3 perguntas (Q2 tipo removida — inferida pelo scanner)
- `QUICK-START.md`: exemplos atualizados com caminhos corretos de projeto

---

## [1.0.0] — 2026-06-10

### Adicionado
- Estrutura inicial de governança (`CLAUDE.md`, `copilot-instructions.md`)
- 14 agents: `agent-router`, `bug-triage`, `test-strategy`, `test-implementation`, `refactor-planner`, `impact-architect`, `docs-curator`, `research-router`, `analysis-architect`, `agent-factory`, `context-builder`, `binding-initializer`, `adapter-generator`
- 17 skills: `context-mode`, `context-builder`, `context-compact`, `sonarqube-governance`, `tavily`, `mermaid-diagrams`, `agent-contracts`, `handoff-governance`, `confidence-fallback-policy`, `agent-safety-guardrails`, `agent-observability-otel`, `agent-evals-lab`, `yaml-governance`, `test-implementation-angular`, `test-implementation-backend`, `test-coverage-governance`
- Prompts de workflow: `/research`, `/plan`, `/implement`, `/validate` (renomeados de PT→EN em 2026-08-29)
- Prompts de Context Mode: `/ctx-checkpoint`, `/ctx-resume`, `/ctx-doctor`, `/ctx-insight`, `/ctx-status`
- Prompts de binding: `/init-context`, `/add-project-context`, `/del-project-context`
- Templates base: `catalog-base.yaml`, `binding-base.md`
- Adapters: `spring-boot-backend.instructions.md` (Java/Spring), `angular-v21-frontend.instructions.md` (Angular 21)
- Regras normativas R-001..R-039 em CLAUDE.md

