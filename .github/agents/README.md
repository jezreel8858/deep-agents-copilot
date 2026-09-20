# Agents — governança genérica

- Perfis especializados para tarefas com orquestração, triagem e execução guiada.

> Regras globais: consulte `../../CLAUDE.md`.
> Regras operacionais: consulte `../copilot-instructions.md`.

## 1) Agent vs Skill

- **Agent**: usado quando a tarefa exige decisão de rota, escopo e entrega estruturada.
- **Skill**: usado quando a tarefa é conhecimento pontual/checklist reutilizável.
- Regra prática: se precisa classificar intenção e escolher fluxo, use agent.
- **Workflows Operacionais Determinísticos (R-050)**: toda tarefa segue rigorosamente um dos 8 pipelines determinísticos especificados em [`workflows.md`](workflows.md) (`WORKFLOW-BUG-FIX`, `WORKFLOW-REFACTORING`, `WORKFLOW-TECHNICAL-ANALYSIS`, `WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-GOVERNANCE-MAINTENANCE`, `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION`, `WORKFLOW-FRAMEWORK-MIGRATION`, `WORKFLOW-RELEASE-READINESS`).
  - **Paridade de Endurecimento Determinístico**: Bugfix (`WORKFLOW-BUG-FIX`) e Refatoração (`WORKFLOW-REFACTORING`) operam sob o mesmo rigor determinístico e blindagem já consolidados para a migração de frameworks:
    - *Bugfix*: RCA estruturado (5 Whys / Fishbone) exigindo dupla fonte independente de evidência técnica observável (*evidence before hypothesis*), classificação determinística `flaky` vs `regressao_real`, pré-declaração de `blast_radius_estimado` e `rollback_plan` no `workflow_state`, mini mutation-check proporcional ao risco (anti falso-verde) e observação pós-fix / canary gate para defeitos críticos.
    - *Refatoração*: Contract Testing formal (Pact-style consumer-driven ou OpenAPI / JSON Schema Diff) no gate de contratos (Estado 2a), camada de redundância proporcional ao blast radius no Estado 5 (auditoria reversa de símbolos `reverse_symbol_audit` via grafo, mini mutation gate e differential replay leve) e rollback com registro e reporte de `blast_radius_revertido`.

## 2) Catálogo Atual (estado verificado)

| Tipo | Nome | Quando usar |
|---|---|---|
| Agent | `agent-router` | Entry point obrigatório para classificar intenção e delegar para downstream |
| Agent | `prompt-structuring` | ⚠️ ***(NEW)*** Passo mandatório pós-`agent-router` (R-041) — refina o prompt em loop controlado (máx. 5 iterações) antes de retornar para classificação de intenção |
| Agent | `bug-triage` | Triagem de bugs/regressões com reprodução e severidade |
| Agent | `test-strategy` | Estratégia de testes, cobertura por risco e critérios de aceitação |
| Agent | `refactor-planner` | Planejamento e decomposição macro de refatoração estrutural com blast radius e rollback (delega execução aos especialistas de stack) |
| Agent | `deep-search` | 🔎 ***(NEW)*** Retriever/Researcher para pesquisa interna (repo + context-mode + terminal read-only) e externa (Tavily), com decomposição paralela de pesquisa composta |
| Agent | `tech-solution-architect` | 📐 ***(v2.1.0)*** Arquiteto de solução técnica: viabilidade, Technical Blueprint, contratos OpenAPI/AsyncAPI, modelo de dados e divisão de tarefas em seções isoladas (`[BACKEND_TASKS]`, `[FRONTEND_TASKS]`) com metodologia B1/B2/B3 |
| Agent | `agent-auditor` | 🧪 ***(NEW)*** Auditoria semântica de governança do próprio catálogo (agents/skills/prompts): detecta smells e gaps, classifica severidade e recomenda handoff para executores, sempre read-only |
| Agent | `governance-factory` | 🏭 ***(v1.2.0)*** Criação/revisão de agent, skill, prompt ou nova stack via parâmetro `type`; na criação de qualquer artefato/stack, delega compulsoriamente pesquisa prévia de mercado/skills ao `deep-search` antes de materializar os arquivos |
| Agent | `governance-maintainer` | 🛠️ ***(NEW)*** Especialista executor em manutenção atômica, refatoração estrutural e sincronização em lote de governança via context-mode e diffs cirúrgicos |
| Agent | `context-builder` | Coletar, condensar e persistir contexto técnico em `docs/context/` |
| Agent | `binding-initializer` | ⚡ Inicializar overlay local e templates de governança para novo repositório (1 pergunta — Health Check R-034) |
| Agent | `adapter-generator` | ⚡ ***(NEW)*** Gerar automaticamente adapters em `.github/instructions/` via `/add-project-context` |
| Agent | `business-rules-extractor` | 📋 ***(NEW)*** Extrair regras de negócio de código e documentar em `.md`; validar refatorações contra regras documentadas |
| Agent | `runtime-verifier` | 🩺 ***(NEW)*** Verifica saúde do ambiente (build limpo, dependências, serviços dependentes) antes de disparar testes/codificadores; read-only, nunca corrige |
| Agent | `pr-gatekeeper` | 📦 ***(NEW)*** Prepara PR pós-aprovação do quality gate (v1.1.0) — diff, commit semântico SSOT (`/commit` Formato A/B + guardrail), matriz de risco, `CHANGELOG.md`; nunca executa `git commit`/`push` |
| Agent | `database-specialist` | 🗄️ ***(NEW)*** Migrações de schema (Flyway/Liquibase/Alembic), otimização de query e integridade referencial; rollback sempre documentado |
| Agent | `angular-router` | 🅰️ **Frontend Angular Router** (`frontend/angular/`) — supervisor hierárquico do ecossistema Angular; orquestra e despacha para os 8 especialistas de frontend mapeados em `.github/agents/frontend/angular/angular-catalog.yaml` (`arch-advisor`, `feature-developer`, `bug-fixer`, `ui-stylist`, `unit-test-writer`, `component-test-writer`, `test-fixer`, `e2e-writer`) |
| Agent | `spring-boot-router` | ☕ **Backend Spring Boot Router** (`backend/spring-boot/`) — supervisor hierárquico do ecossistema Spring Boot; orquestra e despacha para os 7 especialistas backend mapeados em `.github/agents/backend/spring-boot/spring-boot-catalog.yaml` (`arch-advisor`, `feature-developer`, `bug-fixer`, `perf-tuner`, `unit-test-writer`, `integration-test-writer`, `test-fixer`) |
| Agent | `spring-reactive-router` | ⚛️ **Backend Spring Reactive Router** (`backend/spring-reactive/`) — supervisor hierárquico do ecossistema WebFlux/Reactor; orquestra e despacha para os 7 especialistas reativos mapeados em `.github/agents/backend/spring-reactive/spring-reactive-catalog.yaml` (`arch-advisor`, `feature-developer`, `bug-fixer`, `resilience-tuner`, `unit-test-writer`, `integration-test-writer`, `test-fixer`) |
| Agent | `ejb-router` | 🏛️ **Backend Java Legado EJB Router** (`backend/ejb/`) — supervisor hierárquico do ecossistema Java Legado EJB; orquestra e despacha para os 7 especialistas backend mapeados em `.github/agents/backend/ejb/ejb-catalog.yaml` (`arch-advisor`, `feature-developer`, `bug-fixer`, `perf-tuner`, `unit-test-writer`, `integration-test-writer`, `test-fixer`) |
| Agent | `database-router` | 🗄️ **Backend Database Router** (`backend/database/`) — supervisor hierárquico do ecossistema de Banco de Dados; orquestra e despacha para os 6 especialistas Oracle e Informix mapeados em `.github/agents/backend/database/database-catalog.yaml` (`oracle-migration-dev`, `oracle-plsql-expert`, `oracle-query-tuner`, `informix-migration-dev`, `informix-spl-expert`, `informix-query-tuner`) |
| Agent | `python-router` | 🐍 **Backend Python Router** (`backend/python/`) — supervisor hierárquico do ecossistema Python Backend; orquestra e despacha para os 7 especialistas backend mapeados em `.github/agents/backend/python/python-catalog.yaml` (`arch-advisor`, `feature-developer`, `bug-fixer`, `perf-tuner`, `unit-test-writer`, `integration-test-writer`, `test-fixer`) |
| Agent | `struts-router` | ☕ **Backend Java Legado Struts Router** (`backend/struts/`) — supervisor hierárquico do ecossistema Java Legado Struts; orquestra e despacha para os 7 especialistas backend mapeados em `.github/agents/backend/struts/struts-catalog.yaml` (`arch-advisor`, `feature-developer`, `bug-fixer`, `perf-tuner`, `unit-test-writer`, `integration-test-writer`, `test-fixer`) |
| Agent | `docs-engineer` | 📝 ***(FUSÃO)*** Autoria e curadoria de documentação técnica em `.md` — modos `author`/`curate`; substitui docs-writer + docs-curator, que já delegavam entre si a mesma decisão |
| Agent | `code-review` | 🔎 Revisa código (diff/PR) antes do merge por correção, segurança, convenções, impacto, testes e performance; classifica achados por severidade; read-only; delega para `bug-triage`/`tech-solution-architect`/`test-strategy`/`refactor-planner` |
| Agent | `requirements-analyst` | 🧾 ***(NEW)*** Elicita e estrutura requisitos funcionais/não-funcionais a partir de pedido de negócio ambíguo (EARS, INVEST, Gherkin, FURPS+); detecta *solution-jumping* via Five Whys; prospectivo (não confundir com `business-rules-extractor`, que é reverso) |
| Agent | `code-knowledge-graph` | 🕸️ Ponto de entrada único para construção/consulta do grafo de conhecimento de código-fonte cross-projeto. Motor único baseado na lib externa **`@optave/codegraph`** (CLI local e MCP Server enxuto, Node.js/TypeScript nativo, Tree-sitter/Rust, zero API keys/LLM). Suporta dataflow/CFG interprocedural, dead-code, complexity metrics, co-change analysis, detecção de ciclos e visualização interativa via `codegraph plot`. Skill de uso: `codegraph-optave-usage` |
| Agent | `security-reviewer` | 🔒 ***(NEW)*** Revisa código de aplicação por segurança especializada (OWASP Top 10:2025, ASVS 5.0, SCA/CVE, secrets) — complementa `code-review` (dimensão genérica) com profundidade de security specialist; read-only |
| Agent | `performance-agent` | ⚡ ***(NEW)*** Revisa código por performance especializada — Core Web Vitals (frontend), N+1/latência (backend), otimização de query (banco); read-only |
| Agent | `compliance-guardrails` | 🛡️ ***(NEW)*** Avalia conformidade regulatória de aplicação (SOC 2, GDPR/LGPD, HIPAA, ISO 27001) — audit trails, least privilege, retenção de dado pessoal; distinto de `agent-safety-guardrails` (segurança do próprio agent de IA); read-only |
| Agent | `feature-planner` | 📋 ***(NEW)*** Decompõe requisito de feature nova em subtasks executáveis com dependências e paralelização; distinto de `refactor-planner` (refatoração de código existente) |
| Agent | `devops-engineer` | 🐳 ***(NEW)*** Revisa Dockerfile, Kubernetes, CI/CD e IaC por segurança/resiliência/boas práticas; read-only |
| Agent | `debugger` | 🐛 ***(NEW)*** Investiga causa raiz a partir de stack trace/log — call graph, hipótese testável, reprodução mínima; não corrige, complementa `bug-triage` com investigação mais profunda |
| Agent | `code-style-enforcer` | 🎨 ***(NEW)*** Verifica aderência a convenções de estilo documentadas no adapter de stack; nunca bloqueador, apenas sugestão |
| Agent | `ddd-bounded-context-mapper` | 🗺️ ***(NEW)*** Mapeia Bounded Contexts (DDD) por domínio de negócio a partir de nomenclatura, detectando fronteiras invadidas e God Classes; read-only |
| Agent | `adr-sentinel` | 📜 ***(NEW)*** Audita propostas técnicas, blueprints e diffs contra Architectural Decision Records (ADRs) documentados no projeto; read-only |
| Agent | `repo-hygiene-auditor` | 🧹 ***(NEW)*** Audita higiene estrutural, documentação essencial (README/CONTRIBUTING/LICENSE) e práticas de CI/CD; read-only |

## 3) Roteamento Rápido

| Cenário | Rota |
|---|---|
| Entrada padrão no chat | `agent-router` |
| ⚠️ Toda solicitação (pós Health Check R-034) | `prompt-structuring` (mandatório, retorna ao `agent-router`) |
| Bug, erro, regressão | `bug-triage` |
| Estratégia de testes por risco e matriz de cenários | `test-strategy` |
| Planejamento de refactor | `refactor-planner` |
| Impacto técnico local ou Technical Blueprint | `tech-solution-architect` (tier B1) |
| Curadoria/autoria de documentação | `docs-engineer` (`mode: curate`/`author`) |
| Pesquisa interna aprofundada (repo/context-mode/terminal) ou pesquisa externa composta | `deep-search` |
| Análise técnica, blueprint, contratos OpenAPI, integrações cross-sistema | `tech-solution-architect` |
| 🧪 Auditoria semântica de governança do catálogo (smells/gaps em agents, skills e prompts) | `agent-auditor` |
| Criação/revisão de agent, skill, prompt ou nova stack (com pesquisa prévia via `@deep-search` na criação) | `governance-factory` (`type: agent\|skill\|prompt\|stack`) |
| Manutenção atômica, refatoração em cascata ou sincronização em lote de governança | `governance-maintainer` |
| ⚡ Binding context faltando (Health Check) | `binding-initializer` |
| ⚡ Gerar adapters após /add-project-context | `adapter-generator` |
| 📋 Extrair/documentar/validar regras de negócio | `business-rules-extractor` |
| 🅰️ Frontend Angular Router (supervisor que despacha para os 8 especialistas em `frontend/angular/`) | `angular-router` |
| ☕ Backend Spring Boot Router (supervisor que despacha para os 7 especialistas em `backend/spring-boot/`) | `spring-boot-router` |
| ⚛️ Backend Spring Reactive Router (supervisor que despacha para os 7 especialistas em `backend/spring-reactive/`) | `spring-reactive-router` |
| 🏛️ Backend Java Legado EJB Router (supervisor que despacha para os 7 especialistas em `backend/ejb/`) | `ejb-router` |
| 🐍 Backend Python Router (supervisor que despacha para os 7 especialistas em `backend/python/`) | `python-router` |
| ☕ Backend Java Legado Struts Router (supervisor que despacha para os 7 especialistas em `backend/struts/`) | `struts-router` |
| 📝 Escrever/gerar/curar documentação técnica em `.md` (qualquer domínio) | `docs-engineer` |
| 🔎 Revisar código (diff/PR) antes do merge, por severidade | `code-review` |
| 🧾 Elicitar/estruturar requisitos a partir de pedido ambíguo (pré-técnico) | `requirements-analyst` |
| 🕸️ Construir/consultar grafo de conhecimento de código — nível código (arquivo/classe/função, import/chamada/herança/tabela-SQL) e nível arquitetural (sistema/serviço, blast radius, ciclo, acoplamento, risco, diagrama Mermaid), cross-projeto | `code-knowledge-graph` |
| 🔒 Revisão especializada de segurança de aplicação (OWASP, CVE, secrets), read-only | `security-reviewer` |
| ⚡ Revisão especializada de performance (Core Web Vitals, N+1, query), read-only | `performance-agent` |
| 🛡️ Avaliação de conformidade regulatória de aplicação (SOC 2, GDPR/LGPD, HIPAA), read-only | `compliance-guardrails` |
| 📋 Decomposição de feature nova em subtasks executáveis | `feature-planner` |
| 🐳 Revisão de artefatos DevOps (Dockerfile/K8s/CI-CD/IaC), read-only | `devops-engineer` |
| 🐛 Investigação de causa raiz a partir de stack trace/log | `debugger` |
| 🎨 Verificação de aderência a convenções de estilo documentadas | `code-style-enforcer` |
| 🩺 Verificação de saúde do ambiente (build/deps/serviços) antes de testes/codificadores | `runtime-verifier` |
| 📦 Preparação de PR pós-aprovação (diff, commit semântico SSOT, matriz de risco, changelog) | `pr-gatekeeper` |
| 🗄️ Migrações de schema, otimização de query e integridade referencial | `database-specialist` |
| 🗺️ Mapeamento semântico de Bounded Contexts (DDD) e God Classes | `ddd-bounded-context-mapper` |
| 📜 Auditoria de propostas técnicas contra ADRs | `adr-sentinel` |
| 🧹 Auditoria de higiene de repositório e documentação essencial | `repo-hygiene-auditor` |

## 4) Pre-fetch Recomendado

Antes de tarefas não triviais, anexar ao contexto:

- `../../CLAUDE.md`
- `../copilot-instructions.md`
- `./README.md`
- `./catalog.yaml`
- `../skills/README.md`
- `./workflows.md` — especificação canônica dos 8 workflows operacionais determinísticos e de ciclo de vida (R-050)
- `./routing-graph.yaml` — grafo de roteamento estrutural (R-040)

## 5) Regras de Catálogo

- Não listar agent inexistente.
- Mudou governança? Atualizar este arquivo e `catalog.yaml` na mesma entrega.
- Em conflito entre texto e YAML, corrigir ambos no mesmo commit.

## 6) Catálogo Estruturado

- Fonte estruturada: `.github/agents/catalog.yaml`.
- `metadata.total_agents` deve refletir exatamente os agents ativos.

## 7) Templates

- Template de pesquisa: `.github/agents/templates/research-agent.md`
- Template operacional: `.github/agents/templates/operational-agent.md`

## 8) Diretrizes Transversais (obrigatórias)

- Todo agent deve manter contrato explícito de entrada/saída e não-escopo.
- Todo handoff deve usar o schema formal v1.0 (`versao`, `para`, `emissor`, `contexto`) — ver `handoff-governance/SKILL.md` seção 2.1.
- Toda execução deve declarar **confidence score numérico** (0.00–1.00) **e nível de routing** (`rule-based|semantic|llm-based`) — não apenas `alta|média|baixa`.
- Toda decisão operacional deve seguir menor privilégio de tools.
- Todo agent deve preservar rastreabilidade (rota, evidências e próximo passo mínimo).
- Todo agent pode declarar `version:` no frontmatter para rastrear mudanças de comportamento.
- Nova rota de roteamento → atualizar `.github/agents/routing-graph.yaml` **antes** de editar a Decision Tree (R-040).
- **Re-triagem por turno (R-042)**: todo agent downstream deve declarar seção **"Retorno ao Router"** com gatilho objetivo de deriva de intenção — roteamento não é evento único da conversa.
- **Ferramentas mínimas obrigatórias (Tooling Baseline)**: TODO agent deve incluir `run_subagent` no frontmatter `tools:` — sem essa tool, o handoff de retorno exigido por R-042 não é executável (descrever em texto não basta). Ver tabela de baseline por perfil em `agent-contracts/SKILL.md` § 9. `agent-factory` valida essa regra em toda criação/revisão de agent.
- **Visibilidade de fluxo (Banner de Identidade)**: TODO agent — não apenas o `agent-router` — abre toda resposta com `Agente Ativo: <name>`, mesmo continuando em `task_mode` sem handoff neste turno; se houve handoff/re-triagem, adiciona `Handoff: <origem> → <destino> (motivo: ...)`. Padrão de mercado (OpenAI Agents SDK `HandoffOutputItem`, LangGraph `active_agent` streaming) — detalhes em `agent-contracts/SKILL.md` § 0. Sem isso, o usuário perde visibilidade do fluxo assim que a conversa passa a ser respondida por um downstream por vários turnos.
- **Endurecimento Determinístico e Paridade de Governança (Invariantes 13, 14 e 15)**: É terminantemente vedado aplicar correções de bugs ou refatorações estruturais sem as salvaguardas contratuais equivalentes à migração de frameworks — RCA de dupla evidência, blast radius e rollback plan declarados e mini mutation em bugfix; contract testing de contratos públicos, camada de redundância proporcional ao blast radius e registro de `blast_radius_revertido` em refatoração.

## 9) Skills-base por função

| Função de agent | Skills mínimas recomendadas |
|---|---|
| Router/triagem | `agent-contracts`, `handoff-governance`, `confidence-fallback-policy` |
| Análise/impacto | `agent-contracts`, `confidence-fallback-policy`, `agent-evals-lab` |
| Pesquisa | `agent-contracts`, `handoff-governance`, `tavily` |
| Curadoria/governança | `agent-contracts`, `agent-safety-guardrails`, `agent-evals-lab` |
| Operação com métricas | `agent-observability-otel` |
| Agents com memória adaptativa | `agent-memory-policy` (Tier 3 — experimental) |
| Documentação (escrita) | `documentation-writing-patterns`, `mermaid-diagrams`, `agent-contracts` |
| Revisão de código | `code-review-patterns`, `code-tracing`, `agent-contracts` |
| Elicitação de requisitos | `requirements-engineering-patterns`, `agent-contracts` |
| Segurança de aplicação (especialista) | `security-review-patterns`, `agent-contracts` |
| Performance (especialista) | `performance-engineering-patterns`, `agent-contracts` |
| Compliance/auditoria de aplicação | `compliance-governance-patterns`, `agent-contracts` |
| Planejamento/decomposição de feature | `task-decomposition-patterns`, `agent-contracts` |
| Memória long-term de agent | `agent-memory-policy`, `agent-contracts` |
| Revisão DevOps | `devops-agent-patterns`, `agent-contracts` |
| Investigação de causa raiz | `code-tracing`, `agent-contracts` |