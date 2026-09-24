# Skills — governança genérica

Skills são pacotes de conhecimento reutilizável para apoiar execução de tasks.

> Regras globais: `../../CLAUDE.md`
> Regras operacionais: `../copilot-instructions.md`

## 1) Front-matter Obrigatório (skill)

Toda skill deve declarar no topo:

- `name`
- `description`
- `triggers` (PT-BR, quando aplicável)
- `source_docs` (quando aplicável)
- `tools` (quando aplicável)

## 2) Tiers (uso recomendado)

- **Tier 1 (Core):** uso frequente e transversal.
- **Tier 2 (Support):** uso condicionado por cenário.
- **Tier 3 (Experimental):** uso restrito e validado caso a caso.

## 3) Skills Atuais (estado verificado)

| Skill | Tier sugerido | Quando usar |
|---|---|---|
| **`prompt-engineering-patterns`** | 🧠 **Tier 2** | Técnicas consolidadas (APE/OPRO/DSPy/Anthropic/OpenAI) para estruturar prompts em `<task>/<context>/<constraints>/<output_format>`, detectar ambiguidade objetivamente e aplicar self-critique — base do agent `prompt-structuring` |
| `harness-engineering-patterns` | Tier 1 | ⭐ (NEW) Fornece diretrizes e heurísticas de Harness Engineering: diagnóstico harness vs modelo, heurística da zona inteligente (~100k tokens), poda anti-bloat e execução autônoma Ralph Loop |
| `context-mode` | Tier 1 | Roteamento ctx-first, coleta em batch, busca indexada e processamento em sandbox com economia de tokens/créditos |
| `sonarqube-governance` | Tier 2 | Monitorar métricas de qualidade, cobertura e segurança via SonarQube |
| `tavily` | Tier 2 | Pesquisar documentação externa, changelog, versões e referências de terceiros |
| `context-compact` | Tier 2 | Compactar contexto pós-leitura, remover ruído e gerar resumos executáveis |
| `mermaid-diagrams` | Tier 2 | Criar diagramas Mermaid legíveis para documentação, ADRs e análises técnicas |
| `agent-contracts` | Tier 1 | Padronizar contrato de entrada, saída e não-escopo de agents |
| `handoff-governance` | Tier 1 | Definir critérios e payload mínimo de handoff entre agents |
| `confidence-fallback-policy` | Tier 1 | Definir score de confiança e regras de fallback/escalonamento |
| `agent-safety-guardrails` | Tier 1 | Aplicar guardrails de segurança e compliance em respostas de agents |
| `agent-observability-otel` | Tier 2 | Padronizar telemetria e rastreabilidade de execução de agents |
| `agent-evals-lab` | Tier 2 | Definir suíte de avaliação contínua e regressão de agents |
| `yaml-governance` | Tier 2 | Manipular, validar e governar arquivos YAML/YML com segurança, tipagem e schema |
| **`test-implementation-backend`** | ⭐ **Tier 2** | Padrões **genéricos** de testes backend (agnóstico de framework — pirâmide, AAA, mocks) |
| **`test-implementation-spring-boot`** | ⭐ **Tier 2** | Padrões **específicos** JUnit 5 + Mockito + JaCoCo para Spring Boot |
| **`test-implementation-frontend`** | ⭐ **Tier 2** | Padrões **genéricos** de testes frontend (agnóstico de framework — componentes, E2E) |
| **`test-implementation-angular-jasmine`** | ⭐ **Tier 2** | Padrões **específicos** Jasmine/Karma + Playwright para Angular 21 (legado/migração) |
| **`test-implementation-angular-vitest`** | ⭐ **Tier 2** | Padrões **específicos** Vitest 3+ + @angular/build:unit-test para Angular 20/21+ (oficial/novo padrão) |
| **`test-implementation-python`** | ⭐ **Tier 2** | Padrões **específicos** pytest + coverage.py para Python |
| `test-coverage-governance` | Tier 2 | Estratégia agnóstica de cobertura, métricas e priorização por risco |
| `project-scanner` | Tier 2 | Scanner automático de projetos para detecção de stack e convenções |
| `project-context-builder` | Tier 2 | Preparar, condensar e persistir contexto técnico multi-projeto |
| `git-governance` | Tier 2 | Convenções de git workflow, branch naming, commit standards e PR guidelines |
| **`git-worktree-governance`** | 🌲 **Tier 2** | ⭐ ***(NEW)*** Diretrizes de ciclo de vida e isolamento para execução de agentes paralelos e explorações especulativas via Git Worktrees |
| **`terminal-governance`** | 🔧 **Tier 1** | Boas práticas obrigatórias para uso de `run_in_terminal` — prevenção de poluição de contexto, truncamento de saída, não-interativo, lote e padrões proibidos |
| **`code-tracing`** | 🔧 **Tier 1** | Rastrear código do sintoma à causa raiz — grep vs semântico, stack trace parsing, call graph, rastreio de API/método, coleta mínima de evidências |
| **`business-rules-governance`** | 📋 **Tier 1** | Taxonomia, templates e protocolos para extrair, documentar e validar regras de negócio em markdown — ground truth para validação de refatorações |
| **`integration-contract-analysis`** | 🔗 **Tier 2** | Análise de contratos de integração (OpenAPI, AsyncAPI, gRPC, GraphQL): detecção de **breaking changes**, classificação BREAKING/COMPATIBLE/DEPRECIAÇÃO, consumidores afetados |
| **`agent-memory-policy`** | 🧠 **Tier 3** | Política de memória long-term para agents: tipos episódico, semântico e procedimental. Foco em memória procedimental (agents auto-adaptativos) com guardrails e aprovação humana obrigatória |
| **`frontend-componentization-patterns`** | 🧩 **Tier 2** | Padrões genéricos de componentização frontend (responsabilidade única, composição, contrato de componente, fronteiras de estado) |
| **`angular-frontend-patterns`** | 🅰️ **Tier 2** | Boas práticas/patterns de codificação Angular (standalone, template/binding, Signals+RxJS, segurança e consistência) |
| **`angular-performance-patterns`** | 🅰️⚡ **Tier 2** | ⭐ ***(NEW)*** Engenharia de performance Angular: Zoneless, Signals fine-grained, @defer, incremental hydration, Core Web Vitals e memory leaks — base dos especialistas do ecossistema `angular-router` |
| **`angular-responsive-ui-patterns`** | 📱 **Tier 2** | Responsividade Angular (mobile-first, breakpoints, container queries, layout fluido, imagens responsivas e validação multi-viewport) |
| **frontend-visual-feedback-loop** | 👁️ **Tier 2** | ⭐ ***(NEW)*** Visual Feedback Loop (VFL) agnóstico (Angular, React, Vue, Svelte): renderização isolada (Storybook/dev-server), inspeção multimodal (viewports 375/768/1440px), Árvore de Acessibilidade (AOM) e asserções visuais Playwright |
| **`design-system-component-contracts`** | 🧱 **Tier 2** | Governança de contratos de componente para design system: tokens, variantes/estados, Inputs/Outputs, semver, depreciação, breaking change e acessibilidade |
| **`spring-boot-backend-patterns`** | ☕ **Tier 2** | Baseline enterprise para análise/recomendação Spring Boot (arquitetura, observabilidade, segurança, performance e migração) |
| **`spring-boot-performance-patterns`** | ☕⚡ **Tier 2** | ⭐ ***(NEW)*** Engenharia de performance Spring Boot: Virtual Threads, pinning, HikariCP, N+1/EntityGraph, Caffeine+Redis, ZGC e AppCDS — base dos especialistas do ecossistema `spring-boot-router` |
| **`spring-boot-implementation-patterns`** | ☕⚙️ **Tier 2** | Padrões de mercado 2026 para **implementar** features/bugs em Spring Boot (virtual threads vs reativo, N+1/OSIV, DTOs de borda, testing-first) — contraparte de execução de `spring-boot-backend-patterns` |
| **`spring-reactive-webflux-patterns`** | ⚛️ **Tier 2** | Baseline enterprise para análise/recomendação WebFlux/Reactor (adequação reativa, backpressure, resiliência e operação) |
| **`spring-reactive-performance-patterns`** | ⚛️⚡ **Tier 2** | ⭐ ***(NEW)*** Engenharia de performance reativa: proteção event-loop com BlockHound, flatMap concurrency, backpressure, Netty memory e r2dbc-pool — base dos especialistas do ecossistema `spring-reactive-router` |
| **`spring-reactive-implementation-patterns`** | ⚛️⚙️ **Tier 2** | Padrões de mercado 2026 para **implementar** features/bugs em WebFlux/Reactor (composição não-bloqueante, tratamento de erro por operador, StepVerifier/WebTestClient) — contraparte de execução de `spring-reactive-webflux-patterns` |
| **`angular-implementation-patterns`** | 🅰️⚙️ **Tier 2** | Padrões de mercado 2026 para **implementar** features/bugs em Angular (fronteira Signals/RxJS, testing-first, checklist de PR) — contraparte de execução de `angular-frontend-patterns` |
| **`java-jdk-backend-governance`** | ☕ **Tier 1** | Governança de versões Java/JDK backend (LTS, compatibilidade, segurança, performance e trilha de migração) |
| **`documentation-writing-patterns`** | 📝 **Tier 2** | Diretrizes agnósticas de domínio para escrever documentação técnica em `.md` (Diátaxis, ADR/MADR, README, formatação chunking-friendly para IA) — base do agent `docs-engineer` |
| **`code-review-patterns`** | 🔎 **Tier 2** | Diretrizes de mercado para revisão de código por IA — severidade (bloqueador/alta/sugestão), dimensões (correção/segurança/convenções/impacto/testes/performance), critérios de bloqueio de merge — base do agent `code-review` |
| **`requirements-engineering-patterns`** | 🧾 **Tier 2** | Engenharia de Requisitos (ISO/IEC/IEEE 29148, EARS, INVEST, Gherkin/BDD, FURPS+) para elicitar e estruturar requisitos a partir de pedido ambíguo, com detecção de *solution-jumping* (Five Whys) — base do agent `requirements-analyst` |
| **`structured-intake-patterns`** | 📥 **Tier 2** | Padrão canônico de coleta estruturada via `ask_questions` (P1..PN), critério de "mínimo necessário para prosseguir" e template de consolidação — base de `bug-triage`, `test-strategy`, `business-rules-extractor`, `requirements-analyst` |
| **`governance-factory-patterns`** | 🏭 **Tier 1** | Fluxo canônico Factory Pattern (criar/revisar/auditar), checklist de qualidade estrutural e formato de saída ✅/❌ parametrizável — base do agent `governance-factory` |
| **`specialist-hybrid-advisory-implementation-patterns`** | 🧑‍🔧 **Tier 1** | Template canônico do perfil híbrido (Advisory + Implementação) para specialists de stack — base dos especialistas de domínio em frontend e backend |
| **`governance-audit-patterns`** | 🕵️ **Tier 1** | Catálogo dos 16 agent/governance smells (anti-padrão estrutural, gap de perfil, desalinhamento contratual perfil ↔ tools ↔ skills ↔ catálogo, R-046, R-044, R-051 e drift normativo R-0XX) com sintoma, detecção estática Tier 1, severidade e remediação — base do agent `agent-auditor` |
| **`reflection-self-critique-patterns`** | 🪞 **Tier 2** | Padrão generate→critique→revise (Reflection) de baixo custo — self-reflection 1 round grounded para agents Executores reexaminarem o próprio artefato antes de reportar sucesso — base de `docs-engineer`, `test-strategy` |
| **`repository-hygiene-patterns`** | 🧹 **Tier 2** | Diretrizes e matriz canônica para auditoria e garantia de higiene de repositório, documentação essencial (README, CONTRIBUTING, LICENSE), segurança de versionamento (.gitignore) e práticas de CI/CD — base do agent `repo-hygiene-auditor` |
| **`continuous-garbage-collection-patterns`** | 🧽 **Tier 2** | ⭐ ***(NEW)*** Varreduras periódicas de baixo custo (Janitor Tasks) para drift documental, referências órfãs, duplicação não consolidada e desalinhamento de catálogo — modo contínuo complementar de `repo-hygiene-auditor` e `governance-maintainer` |
| **`security-review-patterns`** | 🔒 **Tier 2** | ⭐ ***(NEW)*** OWASP Top 10:2025, ASVS 5.0, OWASP LLM/Agentic AI, SCA (CVE/CVSS), detecção de secrets e rubrica de triagem — base do agent `security-reviewer` |
| **`performance-engineering-patterns`** | ⚡ **Tier 2** | ⭐ ***(NEW)*** Core Web Vitals (LCP/INP/CLS), N+1 queries, profiling de latência e otimização de query — base do agent `performance-agent` |
| **`compliance-governance-patterns`** | 🛡️ **Tier 2** | ⭐ ***(NEW)*** SOC 2/GDPR/LGPD/HIPAA/ISO 27001, audit trails, least privilege e retenção de dado pessoal — base do agent `compliance-guardrails` |
| **`task-decomposition-patterns`** | 📋 **Tier 2** | ⭐ ***(NEW)*** Decomposição sequencial/hierárquica/paralela, granularidade 2-3 níveis, validação de dependências — base do agent `feature-planner` |
| **`refactoring-planning-patterns`** | 🏗️ **Tier 2** | ⭐ ***(NEW)*** Planejamento de refatoração estrutural (Mikado Method, Strangler Fig, Branch by Abstraction, Characterization Tests, DAG de etapas e rollback multicamada) — base do agent `refactor-planner` |
| **`devops-agent-patterns`** | 🐳 **Tier 2** | ⭐ ***(NEW)*** Checklists de revisão Dockerfile/Kubernetes/CI-CD/IaC e estratégias de deployment — base do agent `devops-engineer` |
| **`codegraph-optave-usage`** | 🕸️ **Tier 2** | ⭐ ***(NEW)*** Uso da lib externa `@optave/codegraph` (CLI local e MCP Server enxuto, zero API keys) como motor único de build/consulta de grafo de código — query, blast radius, ciclos, dead code, dataflow e CI gate. Base do agent `code-knowledge-graph` |
| **`efficient-batch-code-modification`** | ⚡ **Tier 1** | ⭐ ***(NEW)*** Edição em lote otimizada para economia de tokens e créditos Copilot — análise prévia (dry-run), tool calls agrupadas na mesma rodada, minimal diffs cirúrgicos e proteção anti-corrupção em arquivo único grande/estruturado via padrão verificado (R-051) |

## 4) Instructions associadas

| Documento | Escopo |
|---|---|
| `*.instructions.md` | Adapters específicos por projeto/stack (carregar sob demanda) |

## 5) Triggers em PT-BR

- Prefira termos acionáveis e objetivos.
- Evite frases ambíguas ou genéricas.
- Atualize triggers quando houver falso negativo recorrente.

## 6) Source Docs Mínimos

- `CLAUDE.md`
- `.github/copilot-instructions.md`
- Documentos específicos da própria skill

## 7) Regras de Manutenção

- Não inventariar skills inexistentes.
- Ao criar/alterar skill, atualizar este catálogo na mesma entrega.
- Manter instruções curtas e rastreáveis.

## 8) Índice Estruturado

- Fonte estruturada: `.github/skills/.index.json`.
- Em conflito entre texto e JSON, corrigir os dois na mesma entrega.