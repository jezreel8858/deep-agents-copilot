---
title: "Guia Canônico de Arquitetura e Governança — deep-agents-copilot"
version: "1.1.0"
date: "2026-11-20"
standard: "arc42 v8.2 / IEEE 42010 / Diátaxis Framework (Explanation & Reference)"
status: "Living Document / Production Standard"
ecosystem: "Multi-Agent AI Coding Governance"
---

# Guia Canônico de Arquitetura e Governança
## `deep-agents-copilot` — Sistema de Orquestração e Governança Multi-Agente para Engenharia de Software

> **Fonte de verdade operacional**: Este documento consolida a visão arquitetural, o modelo estático e dinâmico, os guardrails normativos e os padrões de resiliência e segurança do ecossistema `deep-agents-copilot`. Todas as decisões de design aqui documentadas são fundamentadas em normas internacionais e pesquisas de ponta do setor em 2026.

---

## 1. Introdução e Metas de Qualidade (arc42 §1)

O `deep-agents-copilot` é uma infraestrutura de governança reutilizável, desacoplada e independente de plataforma, projetada para orquestrar agentes autônomos de IA (GitHub Copilot, Claude Code, Cursor) em tarefas complexas de engenharia de software corporativo.

### 1.1 Metas de Negócio e Engenharia
1. **Orquestração Agent-First Determinística**: Substituir prompts genéricos e chatbots monolíticos por uma divisão de trabalho especializada (64 Agents totais / 40 no catálogo raiz), onde cada agente possui papéis, ferramentas e restrições estritamente delimitadas.
2. **Eficiência e Token Budget**: Eliminar context bloat e desperdício de créditos por meio do paradigma *Think-in-Code* (processamento em sandbox via `context-mode` MCP), *Progressive Disclosure* (`R-066`) e *Artifact Offloading* (`overflow_ref`).
3. **Resiliência e Contenção de Falhas**: Garantir que agentes nunca entrem em loops infinitos de tentativa e erro ou corrompam o workspace do desenvolvedor (Circuit Breakers com Retry Budget, *Plan Drift Detection* `R-064` e Rollback Atômico).
4. **Segurança e Menor Privilégio**: Assegurar conformidade com a taxonomia OWASP Agentic AI 2026 e aplicar zoneamento estrito de permissões MCP (separação física entre agentes de consulta e agentes de mutação de código).
5. **Interoperabilidade Aberta**: Disponibilizar capacidades e identidades via padrão aberto A2A (*Agent-to-Agent* v1.0.0 / Linux Foundation).

### 1.2 Árvore de Qualidade Arquitetural
- **Confiabilidade (ISO 25010 / Reliability)**: 100% de previsibilidade nas rotas através de um Grafo de Roteamento formal (`routing-graph.yaml`), máquina de estados plana no `agent-root` (`R-068`) e suíte determinística no `pytest`.
- **Segurança (ISO 25010 / Security)**: Zero vazamento de segredos, zero execução arbitrária fora do workflow e confinamento de privilégios.
- **Manutenibilidade (ISO 25010 / Maintainability)**: Separação estrita de responsabilidades: Governança Global (`CLAUDE.md`), Instruções Operacionais enxutas (`copilot-instructions.md`), Adapters de Stack (`.instructions.md`) e Overlay Privado (`projects.local.yaml`).

---

## 2. Restrições e Limitações Arquiteturais (arc42 §2)

### 2.1 Restrições Normativas Globais
- **R-002 / R-031 — Zero Ação Autônoma Crítica**: Proibição terminante de `git push`, `git commit` autônomos ou criação de arquivos desnecessários sem aprovação humana expressa.
- **R-037 / R-063 — Agent Router First**: Todo turno ou nova intenção inicia no `agent-root` invocando o `@agent-router` antes de qualquer ação técnica (salvo `router_bypass` de Slash Prompts).
- **R-042 — Re-triagem Obrigatória por Turno (Anti Sticky-Session)**: Prevenção de ancoragem em sessões antigas ou deriva de intenção silenciosa.
- **R-043 / R-044 — Isolamento Local e Anonimização**: Dados específicos de projetos corporativos reais vivem exclusivamente em arquivos gitignored (`projects.local.yaml`), vedando commit de caminhos reais no repositório de governança.
- **R-049 — Governança Compulsória de Terminal**: Vedada a execução de terminal sem vinculação à skill `terminal-governance` e sem o uso obrigatório de comandos não-interativos (`--no-pager`).
- **R-064 / R-068 — Orquestração Plana, Recibo Estruturado & Plan Drift**: O `agent-root` despacha 1 etapa por vez via `run_subagent`, exige `receipt` + `step_delta` aderente ao `receipt-step-delta-schema.yaml` e bloqueia imediatamente desvios de escopo (`plan_drift_detected`).
- **R-066 — Orçamento de Instruções (Instruction Budget)**: Prompts sempre carregados (`copilot-instructions.md`, `<execution_protocol>`, `agent-root.agent.md`) permanecem telegráficos, delegando detalhes extensos a `source_docs_lazy:` e `references/` sob guarda determinística (`test_instruction_budget.py`).

---

## 3. Contexto e Fronteiras do Sistema (arc42 §3)

```mermaid
flowchart TB
    subgraph Host["Ambiente do Desenvolvedor (IDE / CLI)"]
        User["Desenvolvedor / Tech Lead"]
        Copilot["GitHub Copilot Chat (VS Code / JetBrains)"]
    end

    subgraph DeepAgents["deep-agents-copilot (Governança Central)"]
        Root["agent-root\n(Orquestrador Plano — R-068)"]
        Router["@agent-router\n(Triagem & Health Check R-034)"]
        Graph["Grafo de Roteamento\n(routing-graph.yaml — 40 nós)"]
        Workflows["10 Workflows Canônicos\n(Máquinas de Estados)"]
        Agents["64 Agents Totais\n(40 no catalog.yaml raiz + 8 Stacks)"]
        Skills["81 Skills Especializadas\n(15 Tier 1, 65 Tier 2, 1 Tier 3)"]
    end

    subgraph External["Projetos & Ferramentas Externas"]
        LocalApps["Aplicações de Negócio\n(Angular, Spring Boot, Python, etc.)"]
        MCP["Servidores MCP\n(context-mode, codegraph, tavily)"]
        A2A["Plataformas A2A Externas\n(LangGraph, CrewAI, Gateways)"]
    end

    User <-->|Prompts & Comandos| Copilot
    Copilot <-->|Turno Raiz| Root
    Root <-->|Triagem Inicial / Deriva| Router
    Router -->|Consulta Nós & Arestas| Graph
    Router -->|Emite ordem_execucao| Workflows
    Root -->|Delegação Plana + step_delta| Agents
    Agents -->|Retornam receipt + step_delta| Root
    Agents -->|Consomem| Skills
    Agents <-->|Inspeção & Edição Cirúrgica| LocalApps
    Agents <-->|Processamento em Sandbox & wf:state| MCP
    Agents -.->|Descoberta via AgentCards| A2A
```

---

## 4. Estratégia de Solução (arc42 §4)

A arquitetura do `deep-agents-copilot` apoia-se em seis pilares estratégicos validados pela indústria:

1. **Delegação Plana (*Flat Delegation* — R-068) vs. Aninhamento Profundo**:
   - O `@agent-router` atua como classificador e supervisor de alto nível, emitindo `ordem_execucao` para que o `agent-root` despache cada agente downstream em nível plano, transportando `step_delta` entre etapas consecutivas.
   - *Fundamentação*: Elimina os custos de token e o risco de cascading failures decorrentes do aninhamento recursivo (`router -> subagente -> subagente`).
2. **Workflows Determinísticos Baseados em Máquinas de Estados**:
   - Todo ciclo de desenvolvimento segue um dos 10 Workflows Canônicos (`WORKFLOW-BUG-FIX`, `WORKFLOW-REFACTORING`, `WORKFLOW-FEATURE-DEVELOPMENT`, etc.), com transições estritas, Gate Cético Pré-HITL (`@plan-critic` / R-064) e Quality Gates formais.
3. **Paradigma *Think-in-Code* via Sandboxing (R-008 / R-059 / R-060)**:
   - Toda leitura volumosa, agregação ou mutação em lote acontece dentro do sandbox do `context-mode` MCP (`ctx_execute` JS `fs`/`path`, `ctx_batch`, `ctx_search`) sob teto rígido de 5 tool turns por ciclo. Apenas o sumário executivo entra na janela de conversação.
4. **Isolamento Físico de Execução via Git Worktrees**:
   - Para execuções concorrentes ou explorações paralelas, cada agente mutante opera em um worktree isolado (`.worktrees/<task>`), protegendo lockfiles e compilações contra concorrência destrutiva.
5. **Context Engineering, Instruction Budget (R-066) e Claim-Check (`overflow_ref`)**:
   - Adoção dos 4 pilares (*Write, Select, Compress, Isolate*), sincronização centralizada do `<execution_protocol>` (`tools/agent_protocol_sync/`), limite de **10 itens inline** por lista no `step_delta` (com transbordo via `ctx_index` `wf:<trace>:delta:step-<n>`) e referências tipadas por ponteiro/hash (`tipo: "pointer"`) para artefatos superiores a 2 KB / 50 linhas.
6. **Alinhamento Normativo Aberto**:
   - Implementação das taxonomias internacionais de segurança (OWASP ASI01..ASI10:2026), MCP Security da NSA e especificação A2A AgentCard da Linux Foundation.

---

## 5. Visão de Blocos de Construção — *Building Blocks* (arc42 §5)

```mermaid
graph TD
    subgraph Camada1["Camada 1: Orquestração Raiz, Entrada e Triagem"]
        ROOT["agent-root (Orquestrador Plano R-068)"]
        AR["@agent-router (Roteador Universal R-037/R-054)"]
        PS["@prompt-structuring (Loop de Refinamento R-041)"]
        BI["@binding-initializer (Health Check R-034)"]
    end

    subgraph Camada2["Camada 2: Supervisores de Domínio (Domain Routers)"]
        FrontendR["@angular-router"]
        ReactR["@react-router"]
        SpringR["@spring-boot-router"]
        ReactiveR["@spring-reactive-router"]
        EjbR["@ejb-router"]
        PythonR["@python-router"]
        StrutsR["@struts-router"]
        DbR["@database-router"]
    end

    subgraph Camada3["Camada 3: Especialistas de Execução (Advisors, Implementers, Fixers, Testers)"]
        SpecAdvisors["Arch Advisors (Read-Only)"]
        SpecDevs["Feature Developers (Mutating)"]
        SpecFixers["Bug & Test Fixers"]
        SpecTesters["Unit & Integration Writers"]
    end

    subgraph Camada4["Camada 4: Agentes Transversais de Governança & Qualidade"]
        CKG["@codegraph-engine (Grafo de Código)"]
        SR["@security-reviewer (OWASP/CVE)"]
        PA["@performance-agent (CWV/N+1)"]
        TSA["@tech-solution-architect (Blueprints)"]
        PC["@plan-critic (Gate Pré-HITL R-064)"]
        PRG["@pr-gatekeeper (Release & PR)"]
        DOCS["@docs-engineer (Documentação .md)"]
    end

    ROOT <-->|Triagem & ordem_execucao| AR
    AR -->|Ambíguo| PS
    AR -->|Binding Ausente| BI
    ROOT -->|Frontend Angular| FrontendR
    ROOT -->|Frontend React| ReactR
    ROOT -->|Backend Spring| SpringR
    ROOT -->|Backend Reativo| ReactiveR
    ROOT -->|Legado EJB| EjbR
    ROOT -->|Python| PythonR
    ROOT -->|Legado Struts| StrutsR
    ROOT -->|Banco de Dados| DbR
    ROOT -->|Transversal| Camada4

    FrontendR & ReactR & SpringR & ReactiveR & EjbR & PythonR & StrutsR & DbR --> Camada3
```

### 5.1 Catálogo de Domínios e Papéis dos Agentes

| Categoria | Componente / Router | Papéis Especialistas Contidos |
|---|---|---|
| **Orquestração & Roteamento Central** | `agent-root` / `@agent-router` | Orquestração plana (`R-068`), validação de `receipt` + `step_delta`, triagem universal, Health Check (`R-034`), Fast-Path (`R-041`/`R-050`) |
| **Frontend Angular / React** | `@angular-router` / `@react-router` | angular-arch-advisor, angular-developer, angular-test-engineer, react-arch-advisor, react-developer, react-test-engineer |
| **Backend Spring Boot** | `@spring-boot-router` | spring-boot-arch-advisor, spring-boot-developer, spring-boot-test-engineer |
| **Backend Reativo** | `@spring-reactive-router` | spring-reactive-arch-advisor, spring-reactive-developer, spring-reactive-test-engineer |
| **Backend Legado Java** | `@ejb-router` / `@struts-router` | Especialistas canônicos para EJB (2.x/3.x, CMT/JTA) e Struts (1.x/2.x, Actions, FormBeans) |
| **Backend Python** | `@python-router` | python-arch-advisor, python-developer, python-test-engineer |
| **Banco de Dados** | `@database-router` | database-specialist, oracle-migration-dev, oracle-plsql-expert, oracle-query-tuner, informix-migration-dev, informix-spl-expert, informix-query-tuner |
| **Qualidade, Planos & Segurança** | Transversais | `@plan-critic`, `@security-reviewer`, `@performance-agent`, `@code-review`, `@compliance-guardrails` |
| **Arquitetura & Grafo** | Transversais | `@codegraph-engine`, `@tech-solution-architect`, `@ddd-bounded-context-mapper`, `@adr-sentinel` |

---

## 6. Visão de Execução e Dinâmica — *Runtime View* (arc42 §6)

### 6.1 Os 10 Workflows Canônicos Determinísticos (R-050)

Todo desenvolvimento de software é executado através de uma máquina de estados finitos que proíbe desvios informais:

1. **`WORKFLOW-BUG-FIX`**: Triagem com RCA estruturado (5 Whys / Fishbone) e regra *evidence before hypothesis* (mínimo de 2 fontes independentes de evidência observável) + classificação determinística `flaky` vs `regressao_real` (`@bug-triage`) → Caracterização e Reprodução Automatizada via Red Test isolado ou spec de layout/VFL (`<stack>-test-engineer`/`<stack>-developer`) com pré-voo de baseline → Declaração antecipada de `blast_radius_estimado` e `rollback_plan` atômico + Correção Cirúrgica Mínima (`<stack>-developer`) → Green Test, Linter e **Mini Mutation-Check** proporcional ao risco (1 a 3 mutantes sintéticos eliminados pelo Red Test contra falsos-verdes) (`runtime-verifier`) → Quality Gate com **Loop de Revisão de Qualidade** (R-050.4, máx. 3 iterações), autorreflexão documental (R-033) e **Observação Pós-Fix / Canary Gate** para defeitos críticos (P0/P1, auth, integridade de dados) (`@code-review` / `@pr-gatekeeper`).
2. **`WORKFLOW-REFACTORING`**: Mapeamento de Regras Vigentes / Ground Truth (`@business-rules-extractor`) → Blast Radius determinístico via grafo (`@codegraph-engine`, R-045) com **Contract Testing (Pact-style consumer-driven ou OpenAPI / JSON Schema Diff)** no gate de contratos (Estado 2a) e Golden Master Safety Net (Estado 2b) → Plano Macro Mikado com árvore de pré-requisitos e pontos de rollback (`@refactor-planner` + `@test-strategy`) com checkpoint humano se alto risco → Execução Incremental em Lote cirúrgico (`domain router / specialists`, R-046) → Validação de Ground Truth (100% preservadas), **Loop de Revisão de Qualidade** (R-050.4) e **Camada de Redundância Proporcional ao Blast Radius** (Auditoria Reversa de Símbolos `reverse_symbol_audit` via grafo, Mini Mutation Gate `mini_mutation_gate` e Differential Replay Leve `differential_replay_leve`) (`@business-rules-extractor` + `@code-review`), com governança de Rollback no Estado 5b calculando e registrando formalmente o **`blast_radius_revertido`** (nós Mikado, arquivos e callers restaurados) no `workflow_state`.
3. **`WORKFLOW-TECHNICAL-ANALYSIS`**: Despacho analítico Read-Only → Coleta determinística via AST/Grafo → Relatório com Propostas Acionáveis (`[PROPOSTA-1..N]`) → Fast-Chaining (R-050.1).
4. **`WORKFLOW-FEATURE-DEVELOPMENT`**: Elicitação de Requisitos (`@requirements-analyst`) → Technical Blueprint (`@tech-solution-architect`) → Estratégia de Testes (`@test-strategy`) → Implementação Domain TDD (com desenvolvimento de UI via `@angular-developer`) → Duplo Quality Gate (Gate 1: Lógica/OWASP; Gate 2: Design System & Paridade UI) com **Loop de Revisão de Qualidade** (R-050.4, máx. 3 iterações).
5. **`WORKFLOW-GOVERNANCE-MAINTENANCE`**: Auditoria estrutural de smells (`@agent-auditor`) → Aprovação humana → Execução atômica em lote (`@governance-maintainer`) → Quality Gate de Governança (Tier 1) com **Loop de Revisão de Qualidade** (R-050.4).
6. **`WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION`**: Scan e triagem de severidade (`@security-reviewer`) → Blast Radius de breaking changes → Bump cirúrgico → Adaptação de código → Quality Gate SCA com **Loop de Revisão de Qualidade** (R-050.4).
7. **`WORKFLOW-FRAMEWORK-MIGRATION`**: Pre-Flight Assessment com 5D e Symbol Exhaustion Gate (`@tech-solution-architect` + `@codegraph-engine` + router de origem) → Migration Phasing com Matriz De-Para → Codemod em Lote por Fase com Anti-Omission AST Validator → Paridade Funcional Dual-Verification → Baseline Quality Gate → Post-Migration Verification & Redundancy Gate (Estado 6: Tríplice Redundância com Reverse Orphan Audit, Mutation Parity e Differential Shadow Replay) com **Loop de Revisão de Qualidade** (R-050.4).
8. **`WORKFLOW-RELEASE-READINESS`**: Verificação de contratos de API e integridade de schema → Auditoria de segurança e higiene de repositório (`@repo-hygiene-auditor`) → Geração de CHANGELOG e PR (`@pr-gatekeeper`) → Veredito de Release.

### 6.2 Ciclo de Vida do Handoff, Banner Universal & Contrato `receipt` + `step_delta` (R-042 / R-048 / R-068)

Todo agente emite obrigatoriamente no início da resposta o banner de rastreabilidade para garantir auditoria em tempo real:

```markdown
Agente Ativo: @<agente-executor>
Handoff: @<origem> → @<destino> (motivo: <motivo_declarado>)
Workflow: <NOME-DO-WORKFLOW>
Etapa do Workflow: <N> — <Nome da Etapa>
Skills Carregadas: <skill-1>, <skill-2>
```

Ao encerrar a etapa, o agente emite o bloco estruturado `receipt` + `step_delta` conforme o schema canônico [`.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml`](../../.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml):
- **Paridade de Escopo:** Agentes executores (`Agency Score >= 1`) preenchem `mode: mutation` e validam `plan_conformance` (`within_allowed_files`, `out_of_scope_files` — R-064); agentes analíticos (`Score 0`) emitem `mode: readonly_analysis` com listas de mutação vazias.
- **Teto Inline & Claim-Check (`overflow_ref`):** Cada lista de `step_delta` comporta até **10 itens inline**; lotes maiores gravam o inventário integral no `ctx_index` (`wf:<trace>:delta:step-<n>`) e referenciam a chave em `overflow_ref`.
- **Bloqueio de Deriva:** Se `within_allowed_files == false` ou `out_of_scope_files != []`, o `agent-root` interrompe o pipeline e retorna ao `@agent-router` com `motivo: "plan_drift_detected"`.

### 6.3 Mecanismo de Circuit Breaker Stateful e Rollback

```mermaid
stateDiagram-v2
    [*] --> CLOSED: Inicialização da Etapa
    CLOSED --> CLOSED: Execução bem-sucedida ou 1ª falha (retry budget: 1/2)
    CLOSED --> OPEN: 2ª falha consecutiva na mesma etapa (budget esgotado)
    
    state OPEN {
        [*] --> InterromperExecucao
        InterromperExecucao --> ExecutarRollback: Descarte de worktree ou git checkout
        ExecutarRollback --> EscalonarHumano: Disparar ask_questions (R-047)
    }

    OPEN --> HALF_OPEN: Usuário fornece nova instrução / contexto corrigido
    HALF_OPEN --> CLOSED: Teste passa (Green Test)
    HALF_OPEN --> OPEN: Nova falha imediata
```

### 6.4 Endurecimento Determinístico e Paridade de Governança nos Workflows Operacionais

O ecossistema multi-agente estabelece **paridade horizontal de rigor determinístico** entre fluxos de migração, correção de defeitos e modernização estrutural:

| Conceito-Chave | `WORKFLOW-BUG-FIX` | `WORKFLOW-REFACTORING` | `WORKFLOW-FRAMEWORK-MIGRATION` |
|---|---|---|---|
| **Investigação Baseada em Fatos** | **RCA Estruturado (5 Whys / Fishbone)** com regra estrita de *evidence before hypothesis* (mínimo de 2 fontes observáveis: stack trace, runtime log, payload HTTP, APM). | **Mapeamento de Regras Vigentes / Ground Truth** extraído formalmente via `@business-rules-extractor` antes de qualquer mutação. | **Symbol Exhaustion Gate**: inventário mecânico via AST/Grafo de 100% dos métodos públicos/privados, queries e nós. |
| **Classificação & Pré-Voo** | **Classificação `flaky` vs `regressao_real`** no Estado 1; pré-voo limpo na suíte vizinha para isolar instabilidade de ambiente/concorrência. | **Análise de Blast Radius via Grafo** (`@codegraph-engine`, R-045) identificando callers, callees e acoplamento transitivo. | **5 Dimensões Críticas & Brownfield Delta**: reconciliação delta obrigatória antes do blueprint. |
| **Blindagem de Contratos** | **Pré-declaração de `blast_radius_estimado` e `rollback_plan`** no `workflow_state` antes de autorizar qualquer diff cirúrgico. | **Contract Testing (Pact-style / consumer-driven ou OpenAPI / JSON Schema Diff)** no Estado 2a para APIs públicas e contratos compartilhados. | **Matriz De-Para Unívoca**: rastreabilidade 100% dos contratos e entidades mapeadas entre origem e destino. |
| **Resiliência contra Falsos-Verdes** | **Mini Mutation-Check** proporcional ao risco no Estado 4 (1 a 3 mutantes sintéticos eliminados pelo Red Test). | **Mini Mutation Gate** no Estado 5 validando a sensibilidade e precisão da suíte Golden Master / caracterização. | **Mutation Parity Resilience**: injeção de mutantes sintéticos comprovando resiliência da suíte Golden Master. |
| **Redundância & Verificação Pós-Execução** | **Observação Pós-Fix / Canary Gate** no Estado 5 com métricas de telemetria (5xx, APM, latência) para bugs críticos (P0/P1, auth, integridade). | **Camada de Redundância Proporcional ao Blast Radius** no Estado 5 (Auditoria Reversa de Símbolos, Mini Mutation Gate e Differential Replay Leve). | **Tríplice Redundância Pós-Migração**: Reverse Orphan Audit + Mutation Parity + Differential Shadow Replay (Estado 6). |
| **Governança de Rollback** | Circuit Breaker (teto de 3 iterações) com reversão atômica estritamente amparada pelo `rollback_plan`. | Reversão atômica dos nós do DAG Mikado com cálculo, registro e auditoria quantitativa de **`blast_radius_revertido`**. | Reversão completa de cutover amparada pela preservação integral do sistema e testes de paridade dual. |

---

## 7. Visão de Implantação e Ambiente (arc42 §7)

```mermaid
flowchart LR
    subgraph LocalMachine["Estação de Desenvolvedor (Local Developer Workspace)"]
        IDE["JetBrains IDEA / VS Code"]
        GitRepo["Repositório Git Principal"]
        Worktrees[".worktrees/<task-id>\n(Worktrees Isolados R-049)"]
        LocalOverlay[".github/projects.local.yaml\n(Overlay Privado R-043)"]
    end

    subgraph Runtimes["Runtimes Locais & Sandboxes"]
        BunNode["Node.js / Bun (Execução context-mode)"]
        Optave["@optave/codegraph CLI (Local Rust/Tree-sitter)"]
        TestRunners["Runners de Teste (pytest, mvn, ng test, npm)"]
    end

    IDE --> GitRepo
    GitRepo -.->|Criação sob Demanda| Worktrees
    IDE --> LocalOverlay
    IDE --> BunNode
    IDE --> Optave
    IDE --> TestRunners
```

---

## 8. Conceitos Transversais e Boas Práticas (arc42 §8)

### 8.1 Context Engineering, Instruction Budget (R-066) e Offloading de Artefatos
- **Os 4 Pilares**:
  1. *Write*: Instruções declarativas concisas sem prosa redundante, governadas por tetos rígidos (`tests/governance_audit/test_instruction_budget.py`) e sincronizadas a partir de `_execution-protocol-fragment.md`.
  2. *Select*: Consulta de dados pontuais via busca indexada FTS5 (`ctx_search`) e carregamento sob demanda (`source_docs_lazy:`).
  3. *Compress*: Compactação pós-leitura de evidências (`context-compact`) e limite de 10 itens inline no `step_delta` (`overflow_ref`).
  4. *Isolate*: Isolamento de contexto por subagente com transporte explícito de `step_delta`.
- **Regra dos 2 KB / 50 Linhas**: Artefatos que excedem esse limiar são gravados em arquivo ou indexados no context-mode e trafegam no handoff exclusivamente como ponteiro estruturado:
  ```yaml
  evidencias:
    - tipo: "pointer"
      artifact_ref: "docs/architecture/spec.md"
      hash: "sha256:e3b0c442..."
      resumo_executivo: "Resumo executivo em 2 linhas."
  ```

### 8.2 Edições em Lote Único e Diffs Cirúrgicos (R-046 / R-051)
- **Single-Turn Batching**: Edições de múltiplos arquivos são enviadas em lote na mesma rodada de tool calls.
- **Diff Cirúrgico**: Uso de 2-3 linhas de contexto exclusivo para garantir unicidade e evitar loops de re-submissão.
- **Proteção Anti-Corrupção e Unicidade de Âncora (R-051)**: Para arquivos >200 linhas, formato `.yaml`/`.yml`/`.json` ou **Markdown estruturado** (`.agent.md`, `.instructions.md`, tabelas com entradas parecidas), é proibido usar `insert_edit_into_file` ou `replace_string_in_file` com âncoras ambíguas. O agente deve verificar a unicidade estrita da âncora em memória (`count === 1`), abortando caso haja risco de colisão (evitando o fallback de casamento aproximado/fuzzy da tool que pode corromper ou apagar blocos inteiros), e validar imediatamente a integridade estrutural pós-escrita.

### 8.3 Segurança e Zoneamento de Ferramentas MCP (NSA CSI MCP Security 2026)
- **Zona 1 (Read-Only)**: `ctx_search`, `ctx_batch` (leitura), `ast_query`. Obrigatória para agentes consultivos (`GATHER_ONLY`).
- **Zona 2 (Mutating)**: `ctx_execute` (script JS `fs`/`path`), `replace_string_in_file`, `create_file` (fallback). Restrita a Implementers em workflows autorizados (`COMPUTE_MUTATE`).
- **Zona 3 (Execution)**: `run_in_terminal` estritamente controlado por `terminal-governance` (R-049).

### 8.4 Visual Feedback Loop (VFL) e Paridade de UI (2026)
Para eliminar a "cegueira visual" de testes headless (Smell 2.21), o ecossistema adota o ciclo **Visual Feedback Loop (VFL)** agnóstico de tecnologia (`frontend-visual-feedback-loop`):
1. **Renderização Isolada (Component-Driven)**: Componentes são executados em sandbox (Storybook CSF3 / rota efêmera) desacoplados de backend.
2. **Dupla Representação**: Inspeção semântica via Árvore de Acessibilidade (AOM) para garantir que nomes de ícone não vazem como texto literal, combinada com capturas nos 3 viewports canônicos (`375px`, `768px`, `1440px`).
3. **Protocolo "Canonical Sibling First"**: Nenhum componente ou diálogo é criado a partir do zero; agentes inspecionam obrigatoriamente um componente irmão canônico homologado no repositório para clonar hierarquia de tags, grid responsivo e classes utilitárias de scroll.
4. **Duplo Quality Gate no Workflow de Features**:
   - **Gate 1**: Lógica, contratos, testes unitários verdes e auditoria OWASP.
   - **Gate 2**: Design System, paridade visual, validação estrita de `@Input()` em arquivos `.ts` de componentes compartilhados e proibição estrita de cores hexadecimais inline.

### 8.5 Sincronização Automática de Documentação Viva e Autorreflexão de DoD (R-033)
Para erradicar o "drift documental" e dispensar ordens manuais do desenvolvedor para atualização de documentação, o ecossistema estabelece o princípio da **Living Documentation Orientada a Autorreflexão**:
- **Gatilho de Autorreflexão**: Antes de finalizar qualquer entrega em `WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-BUG-FIX` ou `WORKFLOW-REFACTORING`, os agentes executores e o `@pr-gatekeeper` avaliam compulsoriamente: *"Esta entrega introduziu novas rotas, modelos de dados, componentes de UI, padrões visuais ou regras de negócio?"*
- **Sincronização Atômica Compulsória**: Se afirmativo, os documentos correspondentes em `docs/`, `README.md`, catálogos de componentes compartilhados e ADRs são atualizados e comitados na mesma entrega como critério de *Definition of Done (DoD)*.
- **Distinção Normativa (R-033)**: Permanece terminantemente proibido criar arquivos `.md` especulativos ou relatórios prolixos desconectados da alteração real; a regra autoriza e exige exclusivamente a **manutenção da documentação viva existente**.

---

## 9. Registro de Decisões Arquiteturais e Validações de Mercado (ADRs / arc42 §9)

A tabela a seguir correlaciona as principais decisões arquiteturais adotadas no `deep-agents-copilot` com as publicações e padrões de referência da indústria que as validam:

| ID | Decisão Arquitetural Adotada | Problema Resolvido | Padrão / Publicação de Mercado que Valida a Decisão |
|---|---|---|---|
| **ADR-01** | **Orquestração Flat Delegation com `agent-root` & Router Central (R-037/R-042/R-068)** | Loops recursivos descontrolados e consumo exponencial de tokens em subagentes aninhados. | **Anthropic (2026)**: *Agentic Coding Trends Report 2026* & *Building Effective Agents* (Recomendação de orquestrador central com despacho plano para workers especializados). |
| **ADR-02** | **Máquinas de Estados Finitos para Workflows (R-050)** | Imprevisibilidade e comportamento emergente caótico de agentes sem fluxo determinístico. | **LangChain / LangGraph (2025-2026)**: Paradigma de grafos cíclicos dirigidos com persistência de estado e checkpoints determinísticos. |
| **ADR-03** | **Think-in-Code via Sandboxing Context Mode & Instruction Budget (R-008/R-066)** | Esgotamento da janela de contexto e diluição de atenção por excesso de prosa nos prompts. | **LangChain (2026)**: *Context Engineering Guide* & Denis Rothman (*Context Engineering for Multi-Agent Systems*, 2026). |
| **ADR-04** | **Circuit Breakers com Retry Budget e Rollback Atômico** | Agentes que entram em loops infinitos tentando consertar testes quebrados sem intervenção. | **Enterprise MAS Design Patterns (2026)** & **Gartner Top Strategic Technology Trends 2026**: Contenção de falhas em cascata e circuit breakers para IA autônoma. |
| **ADR-05** | **Isolamento de Agentes Mutantes via Git Worktrees (R-049)** | Conflito em lockfiles (`package.json`, `pom.xml`), concorrência de compilação e travas de git index. | **Augment Code & Cursor (2026)**: Arquiteturas de execução paralela de agentes em worktrees efêmeros com merge controlado. |
| **ADR-06** | **Taxonomia OWASP Top 10 for Agentic Applications 2026** | Vulnerabilidades específicas de sistemas agênticos autônomos (ASI01 a ASI10:2026). | **OWASP GenAI Security Project (Dez/2025 - 2026)**: *OWASP Top 10 for Agentic Applications 2026* (ratificado para ASI01..ASI10). |
| **ADR-07** | **Zoneamento e Segurança de Ferramentas MCP (Least Privilege)** | Injeção indireta de parâmetros (CVE-2025-6514), Tool Squatting e elevação de privilégio. | **NSA (Maio/2026)**: *CSI Model Context Protocol (MCP): Security Design Considerations* & **Cloud Security Alliance (CSA)**: *Agentic MCP Security Best Practices v1*. |
| **ADR-08** | **Padronização e Exportação A2A AgentCard** | Dependência de catálogo proprietário e falta de interoperabilidade com plataformas externas. | **Linux Foundation (Março/2026)**: *A2A Protocol Specification v1.0.0* & **IETF (Abril/2026)**: *draft-aevum-agentcard-00*. |
| **ADR-09** | **Isolamento de Contexto de Projetos Locais (R-043/R-044)** | Vazamento de nomes de classes, repositórios e regras de negócio proprietárias em templates globais. | **12-Factor App & OWASP Privacy by Design**: Segregação de código de controle (governança) e dados de instância (código cliente). |
| **ADR-10** | **Proibição de Pagers Interativos no Terminal (R-035)** | Bloqueio e congelamento de agentes em comandos Git que disparam `less` (ex: `git diff`). | **IEEE Standard for Portable Operating System Interfaces (POSIX)**: Execução não-interativa e desacoplamento de TTY para processos automatizados. |

---

## 10. Requisitos de Qualidade e Conformidade (arc42 §10)

```mermaid
graph LR
    subgraph Gates["Mecanismos de Quality Gate"]
        G1["G1: Health Check Binding (R-034)"]
        G2["G2: Router Precedents Gate (casos-roteamento.yaml)"]
        G3["G3: Testing-First Quality Gate (Red-Green TDD)"]
        G3b["G3b: Pre-HITL Skeptical Plan Gate (@plan-critic / R-064)"]
        G4["G4: Least-Privilege MCP Tool Gate & Instruction Budget (R-066)"]
        G5["G5: PR & Governance Release Gate (@pr-gatekeeper)"]
    end

    G1 --> G2 --> G3 --> G3b --> G4 --> G5
```

- **Cobertura de Testes**: 100% de aprovação na suíte global de testes (`pytest`), cobrindo conformidade de smells de governança, orçamento de instruções (`test_instruction_budget.py`), integridade de rotas, isolamento de projetos locais, rastreabilidade de incidentes e conformidade com o schema A2A AgentCard.
- **Verificação Contínua de Regressão**: Toda alteração no roteador deve manter pontuação mínima e conformidade com os casos canônicos e de regressão declarados em `evals/casos-roteamento.yaml`.

---

## 11. Riscos Técnicos e Dívida Arquitetural (arc42 §11)

| Risco Arquitetural | Severidade | Estratégia de Mitigação Implementada |
|---|:---:|---|
| **Esgotamento de Janela de Contexto (Context Bloat / Instruction Budget)** | Alta | Aplicação do limiar de 2 KB / 50 linhas para offloading de artefatos, teto de 10 itens inline no `step_delta` (`overflow_ref`), *Progressive Disclosure* (`R-066`) e sandboxing no `context-mode`. |
| **Loops de Tentativa de Correção Infinitos** | Alta | Multi-Agent Circuit Breaker desarmando em `state: OPEN` após 2 falhas consecutivas e bloqueio automático de *Plan Drift* (`R-064`). |
| **Divergência de Modelos entre IDEs (JetBrains vs VS Code)** | Média | Protocolo de Model Awareness no catálogo (`model-profiles.yaml`) e testes agnósticos validados via IDE API e terminal neutro. |
| **Incompatibilidade em Ferramentas MCP Externas** | Média | Zoneamento formal de ferramentas (Zona 1/2/3) e validação estrita de schemas contra injeção de parâmetros (ASI02). |

---

## 12. Glossário Terminológico (arc42 §12)

- **Agent Root (`agent-root`)**: Identidade raiz executora de workflow (`R-068`) que invoca o `@agent-router` para triagem, despacha 1 etapa por vez via `run_subagent`, valida `receipt` + `step_delta` e espelha o estado em `ctx_index` (`wf:<trace>:state`).
- **Agent Router**: Ponto de entrada obrigatório (`R-037`) que classifica a intenção do usuário e decide a rota ideal no catálogo.
- **Flat Delegation**: Padrão de orquestração onde o router apenas declara a rota e o `agent-root` despacha cada especialista em nível plano, sem aninhamento de subagentes.
- **Step Delta (`step_delta`)**: Sub-bloco estruturado do `receipt` (`receipt-step-delta-schema.yaml`) contendo arquivos modificados/criados, assinaturas exportadas, `plan_conformance` e `overflow_ref` (claim-check para lotes > 10 itens).
- **Fast-Path**: Atalho determinístico de roteamento que direciona pedidos claros de bugs, refatorações com alvo ou análises técnicas diretamente para a etapa 1 do workflow canônico, sem passar por `@prompt-structuring`.
- **Fast-Chaining**: Transição imediata de um diagnóstico analítico (Etapa 3 do `WORKFLOW-TECHNICAL-ANALYSIS`) para a execução tática em `WORKFLOW-REFACTORING` ou `FEATURE-DEVELOPMENT` com transporte de estado.
- **Typed State Bag (`workflow_state`)**: Estrutura tipada de dados compartilhada entre etapas de um workflow para preservar artefatos, hipóteses e resultados sem perda de fidelidade.
- **Context Offloading**: Técnica de substituir grandes cargas úteis de dados no chat por referências tipadas por ponteiro (`tipo: "pointer"`) associadas a arquivos ou hashes do `context-mode`.
- **Circuit Breaker**: Mecanismo de resiliência que monitora falhas de etapas e interrompe a automação ao atingir o teto de 2 tentativas consecutivas.
- **A2A AgentCard**: Especificação aberta padronizada pela Linux Foundation para declaração de identidade, capacidades e contratos de agentes de IA.
- **Git Worktree Isolation**: Técnica de checkout paralelo em pastas isoladas (`.worktrees/`) para permitir que agentes mutantes alterem código sem colisão de lockfiles ou concorrência de compilação.
