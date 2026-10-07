# Plano de Planejamento: Consolidação do Agent Sprawl nas Stacks de Domínio

**ID:** `20261006-governance-maintenance-consolidacao-agents-stacks`  
**Data:** 2026-10-06  
**Workflow:** WORKFLOW-GOVERNANCE-MAINTENANCE  
**Status:** Proposto para Aprovação (Gate R-064.1 — Plano de Planejamento)  
**Document Type:** Diátaxis Architecture / Governance Blueprint & RFC  

---

## 1. Contexto e Problema (RCA do Diagnóstico Aprovado)

O `@agent-auditor` identificou, em auditoria de integridade e conformidade de catálogo (`catalog.yaml` e sub-catálogos `<stack>-catalog.yaml`), um quadro de **Agent Sprawl** crítico distribuído de forma homogênea por todos os 8 routers de stack de domínio do repositório `deep-agents-copilot`.

Historicamente, a arquitetura de agentes adotou uma estratégia de ultra-especialização por método e micro-etapa do ciclo de vida de desenvolvimento (ex.: agentes exclusivos para escrever testes de unidade separados dos testes de integração, ou agentes isolados para corrigir bugs pontuais em oposição a desenvolver novas features). Essa fragmentação resultou em **56 agentes especialistas de stack**, além de 8 routers locais, totalizando 64 agentes dedicados a domínio tecnológico.

### 1.1 Sintomas Diagnosticados (Smells)

1. **Smell 2.15 — Over-fragmentação de Especialistas**: Papéis com ciclo de vida, ferramentas (`tools`) e modelos idênticos foram segregados em arquivos isolados, gerando cópias repetitivas de regras normativas em seus prompts base.
2. **Smell 2.17 — Explosão de Decisão nos Routers**: Routers de domínio operavam com árvores de decisão (`Decision Trees`) de 7 a 8 ramos, elevando o tempo de processamento semântico e o risco de desvios (drift) de roteamento.
3. **Smell 2.22 — Custo de Manutenção O(N)**: Cada novo padrão arquitetural ou evolução normativa transversal (ex.: R-008, R-021, R-056, R-059, R-066) demandava sincronização manual em dezenas de prompts de especialistas quase idênticos.
4. **Smell 2.25 — Drift de Contexto**: Conhecimentos específicos de frameworks (ex.: profiling de queries, patterns reativos, sintaxes de teste) residiam hardcoded no corpo dos agentes em vez de serem encapsulados em Skills dinâmicas sob Progressive Disclosure (R-066).

### 1.2 Objetivo

Consolidar o ecossistema de especialistas em todas as 8 stacks tecnológicas do projeto, reduzindo a sobrecarga cognitiva e operacional de **56 especialistas para exatamente 24 especialistas** (exatamente 3 especialistas canônicos por stack, totalizando 32 agentes de stack ao incluir os 8 routers), sem degradação funcional e preservando os invariantes arquiteturais (R-046, R-054, R-055, R-064, R-066).

### 1.3 Motivação Técnica e de Negócio

- **Eficiência de Manutenção**: Redução de **57.1%** no inventário de especialistas de stack, mitigando substancialmente o overhead de atualização normativa contínua.
- **Determinismo no Roteamento**: Decision Trees dos routers locais simplificadas de 7–8 ramificações para exatamente 3 ramos coesos e ortogonais.
- **Coesão e Reutilização**: Centralização das heurísticas específicas de stack em Skills dinâmicas carregadas sob demanda (`source_docs_lazy:`), em conformidade estrita com o padrão de Progressive Disclosure (R-066).
- **Otimização de Custos de Inferência**: Alinhamento à Política de Modelos Canônica (Claude Sonnet 5.5 como base universal e Matriz Biparadigma seletiva para tarefas determinísticas de teste).

## 2. Opções Consideradas

### Opção A — Status Quo (Não Intervir)
Manter os 56 especialistas como estão, confiando em disciplina manual e scripts de governança para propagação de regras.  
*Veredito:* **Rejeitada**. O esforço de governança cresce em $O(N)$ e a incidência de inconsistências em audits periódicos permanece inaceitavelmente alta.

### Opção B — Consolidação Radical (1 Agent Genérico por Stack)
Fundir todos os especialistas de cada stack em um único agente multifuncional "faz-tudo" por domínio (ex.: `spring-boot-expert`, `react-expert`).  
*Veredito:* **Rejeitada**. Viola o Princípio da Responsabilidade Única (R-046), destrói a separação mandatória entre papéis Read-Only e Mutativos, e elimina o duplo gate de planejamento e implementação (R-064).

### Opção C — Consolidação Moderada em 3 Papéis Coesos por Stack (ADOTADA)
Consolidar os especialistas de cada stack em exatamente **3 papéis arquetípicos canônicos**, alinhados ao ciclo real de engenharia de software:

| Papel Consolidado | Perfil de Acesso | Absorve (Papéis Legados) | Responsabilidade Nuclear |
|---|---|---|---|
| **`<stack>-arch-advisor`** | Read-Only | arch-advisor, query-tuner (banco), perf-advisor | Raciocínio arquitetural, blueprints técnicos (R-064.2), design de schema e revisão não-destrutiva. |
| **`<stack>-developer`** | Mutativo | feature-developer, bug-fixer, perf-tuner, ui-stylist, ddl-migration, plsql/spl expert | Implementação completa de código de produção, correções de bugs, refatoração de performance e DDL. |
| **`<stack>-test-engineer`** | Mutativo | unit-test-writer, integration-test-writer, component-test-writer, e2e-writer, test-fixer | Garantia de qualidade determinística (unitários, integração, E2E) e correção iterativa de testes (retry cap R-021). |

---

### 2.1 Decisão Técnica Adotada

Adota-se a **Opção C** de forma integral para todas as 8 stacks do projeto. A transição garante a preservação do Duplo Gate Documental (R-064), onde o `arch-advisor` atua obrigatoriamente no planejamento técnico antes que o `developer` ou `test-engineer` realizem modificações no código.

---

### 2.2 Mapeamento Canônico Exaustivo De -> Para por Stack (Todas as 8 Stacks)

A consolidação de cada uma das 8 stacks de domínio é estruturada conforme o mapeamento exaustivo a seguir:

#### 1. Stack: `spring-boot` (Backend)
- **Routers**: `spring-boot-router` (preservado com Baseline R-054 e Decision Tree simplificada de 3 branches).
- **Consolidação (7 → 3 especialistas)**:
  - `spring-boot-arch-advisor` (preservado como autor exclusivo de Planos de Implementação Técnica e Blueprints R-064.2; read-only).
  - `spring-boot-developer` (novo consolidador mutativo: absorve `spring-boot-feature-developer`, `spring-boot-bug-fixer` e `spring-boot-perf-tuner`).
  - `spring-boot-test-engineer` (novo consolidador mutativo: absorve `spring-boot-unit-test-writer`, `spring-boot-integration-test-writer` e `spring-boot-test-fixer`).

#### 2. Stack: `react` (Frontend)
- **Routers**: `react-router` (preservado com Baseline R-054 e Decision Tree simplificada de 3 branches).
- **Consolidação (8 → 3 especialistas)**:
  - `react-arch-advisor` (preservado para análise arquitetural, SSR/RSC, design de estado global e contratos; read-only).
  - `react-developer` (novo consolidador mutativo: absorve `react-feature-developer`, `react-bug-fixer` e `react-ui-stylist`).
  - `react-test-engineer` (novo consolidador mutativo: absorve `react-unit-test-writer`, `react-component-test-writer`, `react-e2e-writer` e `react-test-fixer`).

#### 3. Stack: `angular` (Frontend)
- **Routers**: `angular-router` (preservado com Baseline R-054 e Decision Tree simplificada de 3 branches).
- **Consolidação (8 → 3 especialistas)**:
  - `angular-arch-advisor` (preservado para arquitetura modular/standalone, Signals, RxJS e governança corporativa; read-only).
  - `angular-developer` (novo consolidador mutativo: absorve `angular-feature-developer`, `angular-bug-fixer` e `angular-ui-stylist`).
  - `angular-test-engineer` (novo consolidador mutativo: absorve `angular-unit-test-writer`, `angular-component-test-writer`, `angular-e2e-writer` e `angular-test-fixer`).

#### 4. Stack: `spring-reactive` (Backend Reativo)
- **Routers**: `spring-reactive-router` (preservado com Baseline R-054 e Decision Tree simplificada de 3 branches).
- **Consolidação (7 → 3 especialistas)**:
  - `spring-reactive-arch-advisor` (preservado para blueprints de fluxos não-bloqueantes, backpressure, R2DBC e WebFlux; read-only).
  - `spring-reactive-developer` (novo consolidador mutativo: absorve `spring-reactive-feature-developer`, `spring-reactive-bug-fixer` e `spring-reactive-perf-tuner`).
  - `spring-reactive-test-engineer` (novo consolidador mutativo: absorve `spring-reactive-unit-test-writer`, `spring-reactive-integration-test-writer` [StepVerifier] e `spring-reactive-test-fixer`).

#### 5. Stack: `ejb` (Backend Legado Enterprise)
- **Routers**: `ejb-router` (preservado com Baseline R-054 e Decision Tree simplificada de 3 branches).
- **Consolidação (7 → 3 especialistas)**:
  - `ejb-arch-advisor` (preservado para arquitetura JEE, transações distribuídas JTA, estratégias de modernização e CDI; read-only).
  - `ejb-developer` (novo consolidador mutativo: absorve `ejb-feature-developer`, `ejb-bug-fixer` e `ejb-perf-tuner`).
  - `ejb-test-engineer` (novo consolidador mutativo: absorve `ejb-unit-test-writer`, `ejb-integration-test-writer` [Arquillian/OpenEJB] e `ejb-test-fixer`).

#### 6. Stack: `struts` (Backend Legado MVC)
- **Routers**: `struts-router` (preservado com Baseline R-054 e Decision Tree simplificada de 3 branches).
- **Consolidação (7 → 3 especialistas)**:
  - `struts-arch-advisor` (preservado para mitigação de vulnerabilidades OGNL, interceptors, blueprints de migração e arquitetura de Actions; read-only).
  - `struts-developer` (novo consolidador mutativo: absorve `struts-feature-developer`, `struts-bug-fixer` e `struts-perf-tuner`).
  - `struts-test-engineer` (novo consolidador mutativo: absorve `struts-unit-test-writer`, `struts-integration-test-writer` [StrutsTestCase] e `struts-test-fixer`).

#### 7. Stack: `python` (Backend / Data Services)
- **Routers**: `python-router` (preservado com Baseline R-054 e Decision Tree simplificada de 3 branches).
- **Consolidação (7 → 3 especialistas)**:
  - `python-arch-advisor` (preservado para arquitetura assíncrona FastAPI/asyncio, tipagem estática Pydantic e microsserviços; read-only).
  - `python-developer` (novo consolidador mutativo: absorve `python-feature-developer`, `python-bug-fixer` e `python-perf-tuner`).
  - `python-test-engineer` (novo consolidador mutativo: absorve `python-unit-test-writer`, `python-integration-test-writer` [pytest/pytest-asyncio] e `python-test-fixer`).

#### 8. Stack: `database` (Persistência e Motores Relacionais Heterogêneos)
- **Routers**: `database-router` (preservado com Baseline R-054 e Decision Tree simplificada de 3 branches por escopo operacional).
- **Consolidação (6 → 3 especialistas)**:
  - `database-arch-advisor` (**NOVO consolidado read-only**: unifica `oracle-query-tuner` e `informix-query-tuner`, assumindo análise não-destrutiva de planos de execução EXPLAIN/SET EXPLAIN, otimização de índices, modelagem relacional e design de schema).
  - `oracle-database-specialist` (**NOVO consolidado mutativo**: unifica `oracle-migration-dev` e `oracle-plsql-expert`, absorvendo migrações DDL Flyway/Liquibase, procedures, packages, triggers e packages em PL/SQL).
  - `informix-database-specialist` (**NOVO consolidado mutativo**: unifica `informix-migration-dev` e `informix-spl-expert`, absorvendo migrações DDL de engine Informix, rotinas SPL e triggers relacionais).

### 2.3 Tabela Resumo Consolidada de Redução Quantitativa por Stack

A consolidação assegura rigidez matemática na arquitetura: exatamente 3 especialistas e 1 router por stack de domínio, sem exceções.

| Stack Tecnológica | Camada | Especialistas (Antes) | Routers (Antes) | Total Agentes (Antes) | Especialistas (Depois) | Routers (Depois) | Total Agentes (Depois) | Redução Especialistas (%) | Redução Total Stack (%) |
|---|---|---|---|---|---|---|---|---|---|
| `spring-boot` | Backend | 7 | 1 | 8 | 3 | 1 | 4 | -57.1% | -50.0% |
| `react` | Frontend | 8 | 1 | 9 | 3 | 1 | 4 | -62.5% | -55.6% |
| `angular` | Frontend | 8 | 1 | 9 | 3 | 1 | 4 | -62.5% | -55.6% |
| `spring-reactive` | Backend | 7 | 1 | 8 | 3 | 1 | 4 | -57.1% | -50.0% |
| `ejb` | Backend Legado | 7 | 1 | 8 | 3 | 1 | 4 | -57.1% | -50.0% |
| `struts` | Backend Legado | 7 | 1 | 8 | 3 | 1 | 4 | -57.1% | -50.0% |
| `python` | Backend / Data | 7 | 1 | 8 | 3 | 1 | 4 | -57.1% | -50.0% |
| `database` | Persistência | 6 | 1 | 7 | 3 | 1 | 4 | -50.0% | -42.9% |
| **TOTAL GERAL** | **Transversal** | **56** | **8** | **64** | **24** | **8** | **32** | **-57.1%** | **-50.0%** |

*Métrica Consolidada*: O inventário de especialistas encolhe de 56 para 24 (**redução líquida de 32 agentes especialistas**, ou -57.14%). O inventário total de stack passa de 64 para 32 agentes (**redução de 50.0%**), mantendo a integridade dos 8 routers canônicos de domínio.

---

## 3. Alternativas Rejeitadas

1. **Rejeitada: Eliminação total dos Routers de Stack**:
   - *Proposta*: O `@agent-router` central despachar diretamente para 24 especialistas.
   - *Motivo do Descarte*: Rompe o princípio da coesão contextual em árvore e satura a Decision Tree do roteador central (mais de 24 alvos diretos aumentam alucinações e erros de dispatch, violando R-054).
2. **Rejeitada: Fusão do Arch-Advisor com Developer**:
   - *Proposta*: 2 agentes por stack (`advisor-developer` + `test-engineer`).
   - *Motivo do Descarte*: Viola frontalmente a segregação de funções (Least Privilege) e anula o Duplo Gate Documental R-064 (um agente não pode emitir blueprint e implementar na mesma sessão sem segregação de contexto).
3. **Rejeitada: Fusão de Developer e Test-Engineer**:
   - *Proposta*: 2 agentes por stack (`arch-advisor` + `full-engineer`).
   - *Motivo do Descarte*: Desrespeita a barreira mandatória de independência de testes e o princípio Test-Last no Frontend (`test_frontend_test_last_governance.py`). Desenvolvedor e testador com o mesmo contexto geram testes tautológicos.
4. **Rejeitada: Divisão da Stack Database em 2 Stacks Autônomas (`oracle-router` e `informix-router`)**:
   - *Proposta*: Criar stacks separadas por motor de banco de dados.
   - *Motivo do Descarte*: Multiplica desnecessariamente os routers de stack e fragmenta a visão integrada de governança de dados e performance SQL. A unificação sob `database-router` com 3 especialistas especializados é estritamente coesa.

---

## 4. Escopo Delimitado

### 4.1 Em Escopo (In-Scope)

1. Consolidação sistemática e substituição atômica de arquivos `.agent.md` em todas as 8 stacks.
2. Atualização dos 8 sub-catálogos locais (`<stack>-catalog.yaml`) e dos 8 routers locais (`<stack>-router.agent.md`).
3. Migração das regras operacionais, heurísticas e restrições de cada papel eliminado para Skills dinâmicas sob Progressive Disclosure (R-066).
4. Sincronização atômica global (R-015): `catalog.yaml`, `routing-graph.yaml`, `agent-router.agent.md`, `README.md` geral e `.github/skills/.index.json`.
5. Criação e atualização de testes determinísticos de governança no framework `pytest`.

### 4.2 Fora de Escopo (Out-of-Scope)

1. Alteração da interface pública do `@agent-router` raiz (continua despachando exclusivamente para os routers de stack).
2. Modificação de agentes transversais fora de stacks de domínio (ex.: `security-reviewer`, `code-reviewer`, `pr-gatekeeper`, `governance-factory`, `docs-engineer`).
3. Alteração do Baseline R-054 estrutural de ferramentas dos routers locais (permanecem com 7 ferramentas canônicas).
4. Modificação em código-fonte de aplicação de negócio (escopo estritamente restrito a artefatos de governança).

## 5. Matriz de Migração de Conteúdo e Skills (Progressive Disclosure R-066)

A consolidação de agentes não descarta conhecimento técnico acumulado; ao contrário, extrai e desacopla as regras procedimentais dos arquivos `.agent.md` transferindo-as para Skills dinâmicas organizadas em `.github/skills/`.

Sob a regra **R-066 (Progressive Disclosure)**, os agentes consolidados mantêm prompts compactos e invocam as regras via `source_docs_lazy:` apenas no momento exato em que o modo de execução correspondente é disparado.

| Papel Eliminado | Stack | Conhecimento Técnico Absorvido | Destino no Agente Consolidado | Skill Reutilizável Associada (`.github/skills/`) |
|---|---|---|---|---|
| `*-perf-tuner` | Backend (Spring, Reactive, EJB, Struts, Python) | Profiling, otimização de queries, memory leaks, concurrency locks, connection pooling | Modo `performance` dentro do `<stack>-developer` (com análise prévia do arch-advisor) | `<stack>-performance-patterns/SKILL.md` |
| `*-bug-fixer` | Todas | Diagnóstico de causa-raiz (RCA), patch mínimo cirúrgico, preservação de regressão | Modo `bugfix` dentro do `<stack>-developer` | `clean-architecture-patterns/SKILL.md` e guidelines de RCA |
| `*-feature-developer` | Todas | Implementação idiomática, Clean Architecture, injeção de dependência, contratos de API | Modo `feature` dentro do `<stack>-developer` | `<stack>-idiomatic-patterns/SKILL.md` |
| `*-ui-stylist` | Frontend (`react`, `angular`) | Design tokens, CSS Modules, Tailwind/Sass, acessibilidade WCAG, layout responsivo | Modo `styling` dentro do `<stack>-developer` (sem quebra de test boundary) | `<stack>-responsive-ui-patterns/SKILL.md` |
| `*-unit-test-writer` | Todas | Mocking, fixtures isoladas, asserções de invariantes, cobertura de ramos | Módulo `unit` dentro do `<stack>-test-engineer` | `unit-test-patterns/SKILL.md` |
| `*-integration-test-writer` | Backend | Containers de teste (Testcontainers), transações, web clients, mocks parciais | Módulo `integration` dentro do `<stack>-test-engineer` | `<stack>-integration-test-patterns/SKILL.md` |
| `*-component-test-writer` | Frontend | Testing Library, renderização isolada de componentes, user events, asserções de acessibilidade | Módulo `component` dentro do `<stack>-test-engineer` | `<stack>-component-test-patterns/SKILL.md` |
| `*-e2e-writer` | Frontend | Cypress, Playwright, page objects, interceptação de rede, fluxos ponta-a-ponta | Módulo `e2e` dentro do `<stack>-test-engineer` | `e2e-automation-patterns/SKILL.md` |
| `*-test-fixer` | Todas | Análise determinística de stacktraces de falha, fixação de asserções, retry cap restrito (3 rounds) | Modo `test-fixer` dentro do `<stack>-test-engineer` | `test-failure-analysis-patterns/SKILL.md` |
| `*-query-tuner` (Oracle e Informix) | Database | Análise de EXPLAIN PLAN, estatísticas de tabelas, índices B-Tree e Bitmap, joins otimizados | Absorvido pelo `database-arch-advisor` (read-only) | `database-query-tuning-patterns/SKILL.md` |
| `oracle-migration-dev` + `oracle-plsql-expert` | Database | DDL idempotente, Liquibase/Flyway, packages, procedures, triggers, tipos compostos PL/SQL | Absorvido pelo `oracle-database-specialist` | `oracle-plsql-patterns/SKILL.md` e `database-migration-patterns/SKILL.md` |
| `informix-migration-dev` + `informix-spl-expert` | Database | DDL engine Informix, dbspaces, constraints, sintaxe SPL, procedures e triggers relacionais | Absorvido pelo `informix-database-specialist` | `informix-spl-patterns/SKILL.md` e `database-migration-patterns/SKILL.md` |

---

## 6. Política de Modelos Canônica (Matriz Biparadigma)

A política de modelos define a distribuição de capacidade computacional e raciocínio de IA, assegurando custo-benefício rigoroso sem concessão à qualidade arquitetural ou determinismo de código.

### 6.1 Regra Primária de Modelo Base

- **Routers de Stack (8)**: **Claude Sonnet 5.5** (100% mandatória). A triagem de intenção e o roteamento de alta precisão requerem raciocínio semântico avançado e aderência estrita a restrições normativas.
- **Arquitetos (`<stack>-arch-advisor` - 8)**: **Claude Sonnet 5.5** (100% mandatória). Responsáveis por decisões estruturais de design, blueprints técnicos R-064.2 e mitigação não-destrutiva de dívida técnica.
- **Desenvolvedores (`<stack>-developer` e specialists de banco - 8)**: **Claude Sonnet 5.5** (100% mandatória). Implementação de código de produção, correções complexas de concorrência e mutações estruturais demandam capacidade máxima de inferência.

### 6.2 Matriz Biparadigma para Engenheiros de Teste (`<stack>-test-engineer`)

Para o papel de garantia de qualidade (`<stack>-test-engineer`), aplica-se a estratégia biparadigma (R-021):

| Papel | Perfil de Operação | Modelo Canônico Base | Exceção Econômica Autorizada (R-021) | Critério de Escalonamento Automático (R-021.2) |
|---|---|---|---|---|
| **`<stack>-test-engineer`** | Planejamento de Casos, Triagem de Falhas, Mutation Testing, Testes de Integração e E2E | **Claude Sonnet 5.5** | Nenhuma. Mantém Sonnet 5 para raciocínio combinatório e arquitetura de testes. | N/A |
| **`<stack>-test-engineer`** | Geração Mecânica de Fixtures, DTOs de Mock, Asserções Unitárias Repetitivas e Boilerplate | **Claude Sonnet 5.5** | **Claude Haiku / Gemini Flash** (permitido exclusivamente em geração pontual de testes unitários simples e determinísticos) | **Escalonamento Mandatório**: Caso a suíte acuse erro de compilação ou falha em 2 execuções consecutivas do mesmo ciclo, o sub-agente é forçado imediatamente para **Claude Sonnet 5.5** para correção especializada. |

*Nota Operacional*: O campo `model:` declarado no frontmatter de catálogo de todos os 24 especialistas permanece **Claude Sonnet 5.5** como padrão canônico formal. A comutação econômica atua como otimização de runtime via header ou sub-tarefa subordinada.

## 7. Matriz de Rastreabilidade (Requisito → Artefato → Teste de Governança)

| Requisito do Plano | Artefatos Impactados | Testes de Governança Automatizados |
|---|---|---|
| Consolidação 3-por-stack em 8 stacks | `<stack>-catalog.yaml`, `.github/agents/*/*.agent.md` | `test_agent_count_per_stack_governance.py` (valida 3 especialistas + 1 router por stack) |
| Preservação de Baseline de Routers (R-054) | 8 arquivos `<stack>-router.agent.md` | `test_router_agents.py` e `test_baseline_r054_conformance.py` |
| Dynamic Skills & Progressive Disclosure (R-066) | `.github/skills/*`, `source_docs_lazy:` | `test_r066_progressive_disclosure_budget.py` |
| Política Biparadigma & Roteamento Zero Noise | `<stack>-test-engineer.agent.md` | `test_hybrid_model_routing_and_zero_noise_governance.py` |
| Duplo Gate Documental R-064 (Arch-Advisor) | `<stack>-arch-advisor.agent.md` | `test_r064_arch_advisor_gate.py` e `test_architectural_blueprint_gate_governance.py` |
| Isolamento de Test-Last no Frontend | `react-developer.agent.md`, `angular-developer.agent.md` | `test_frontend_test_last_governance.py` e `test_feature_developer_test_authoring_boundary.py` |
| Limite de Tentativas de Test Fixer (Retry Cap) | `<stack>-test-engineer.agent.md` | `test_test_fixer_retry_cap.py` |
| Sincronização Atômica Multi-Catálogo (R-015) | `catalog.yaml`, `routing-graph.yaml`, `agent-router.agent.md` | `test_governance_sync_core.py` e `test_sync_required_source_docs_invariants.py` |
| Verificação de Tamanho e Reutilização de Skills | `.github/skills/*` | `test_stack_skills_cross_reference_and_size_outlier.py` |

---

## 8. Trade-offs

| Dimensão | Vantagem Estrutural Conquistada | Custo / Risco Aceito | Mecanismo de Mitigação |
|---|---|---|---|
| **Manutenção Normativa** | Redução de 57.1% de arquivos para auditar e propagar invariantes de governança. | Agentes consolidados (`developer`, `test-engineer`) tornam-se moderadamente maiores em escopo interno. | Progressive Disclosure (R-066) mantém seções pesadas como skills externas lazy-loaded. |
| **Clareza de Despacho** | Decision Trees dos routers locais caem de 8 para 3 ramos determinísticos. | Perda do identificador de agente ultra-específico na telemetria (ex.: `spring-boot-perf-tuner`). | Tags contextuais de modo no payload de telemetria de handoff (R-042) registram o sub-modo ativo. |
| **Eficiência Financeira** | Adoção controlada de modelos rápidos em tarefas mecânicas de teste. | Risco de taxa de erro de assert se modelo mais barato for mal empregado. | Circuit Breaker R-021.2: escalonamento compulsório para Sonnet 5 na 2ª falha iterativa. |
| **Estabilidade de Execução** | Rollout fatiado em 5 fases lógicas isoladas. | Coexistência transitória de stacks consolidadas e não-consolidadas durante as fases. | Catálogo central (`catalog.yaml`) mantém flags de status da transição atômica por stack. |

---

## 9. Riscos, Consequências e Blast Radius

### 9.1 Riscos Técnicos

1. **Dangling References em Grafos de Roteamento**: Referências remanescentes aos agentes extintos em `routing-graph.yaml` ou prompts transversais.  
   *Mitigação*: Execução de linter de integridade referencial (`test_governance_sync_core.py`) em modo all-or-nothing (R-051).
2. **Quebra da Barreira Test-Last em Frontend**: O novo `react-developer` ou `angular-developer` gerar testes indevidamente ao absorver atribuições de tela.  
   *Mitigação*: Asserções negativas ativas no quality gate (`test_feature_developer_test_authoring_boundary.py`) vedando criação de specs de teste por desenvolvedores.
3. **Complexidade de Motores Heterogêneos de Banco**: Tentativa de forçar simetria idêntica de software na stack de banco.  
   *Mitigação*: Estruturação sob medida da stack `database` com `database-arch-advisor` (read-only unificado de tuning/schema) e 2 especialistas mutativos dedicados por motor (`oracle-database-specialist` e `informix-database-specialist`).

### 9.2 Blast Radius e Estratégia de Reversão (R-031)

- **Blast Radius**: Cada fase impacta um cluster restrito de diretórios em `.github/agents/`, seu respectivo sub-catálogo e as linhas correspondentes no catálogo central.
- **Rollback Determinístico (Tier 1 - R-031)**: Se qualquer fase falhar na suíte de testes `pytest tests/governance_audit/`, a reversão é puramente atômica via Git checkout do commit de checkpoint anterior:
  ```bash
  git checkout HEAD -- .github/agents/<camada>/<stack>/ catalog.yaml routing-graph.yaml
  ```

---

## 10. 🛡️ Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)

- **Princípio do Menor Privilégio (Least Privilege)**: Os arquitetos (`<stack>-arch-advisor`) permanecem com ferramentas 100% read-only. Em nenhuma hipótese ferramentas de mutação (`insert_edit_into_file`, `create_file`, `replace_string_in_file`) são concedidas a conselheiros arquiteturais.
- **Prevenção contra Tool Injection / Poisoning**: As ferramentas disponíveis para `developer` e `test-engineer` permanecem rigorosamente no baseline auditado da governança, sem adição de novos recursos de sistema ou execução desnecessária.
- **Validação All-or-Nothing (R-051)**: Atualizações de catálogo e deleções de agentes são processadas via scripts em lote com conferência pré e pós-estado (`pre_count - deleted + created === expected`).
- **Trilha de Auditoria Auditável**: Emissão de telemetria estruturada (`[HANDOFF]`) a cada transferência de contexto, validando os limites operacionais entre Router, Arquiteto, Desenvolvedor e Test-Engineer.

## 11. Roadmap Completo de Execução (Ordenado por Criticidade e Dependência)

O processo de migração compreende 5 Fases Sequenciais estritamente ordenadas, mantendo em cada fase a total integridade dos testes e invariantes de governança.

```text
Fase 1: Piloto Central ──────> Fase 2: Expansão Modern ────> Fase 3: Stacks Legadas ────> Fase 4: Database Multi-Engine ────> Fase 5: Quality Gates Globais
(spring-boot + react)          (angular + spring-reactive)   (python + ejb + struts)       (oracle + informix unificados)       (testes + templates + lock)
```

### Fase 1 — Piloto Representativo (Backend Core & Frontend Core)
- **Escopo**: 
  - `spring-boot`: 7 especialistas → 3 (`spring-boot-arch-advisor`, `spring-boot-developer`, `spring-boot-test-engineer`).
  - `react`: 8 especialistas → 3 (`react-arch-advisor`, `react-developer`, `react-test-engineer`).
- **Artefatos Entregues**: 
  - Criação dos 4 novos especialistas e preservação dos 2 arquitetos.
  - Atualização dos sub-catálogos `spring-boot-catalog.yaml` e `react-catalog.yaml`.
  - Reescrita das Decision Trees de `spring-boot-router.agent.md` e `react-router.agent.md`.
  - Remoção dos 9 especialistas legados correspondentes.
- **Gate de Saída**: Execução e aprovação 100% verde nos testes existentes de governança para as duas stacks piloto.

### Fase 2 — Expansão Frontend Espelhada & Backend Reativo
- **Escopo**:
  - `angular`: 8 especialistas → 3 (`angular-arch-advisor`, `angular-developer`, `angular-test-engineer`).
  - `spring-reactive`: 7 especialistas → 3 (`spring-reactive-arch-advisor`, `spring-reactive-developer`, `spring-reactive-test-engineer`).
- **Artefatos Entregues**:
  - Padronização simétrica da stack Angular alinhada à consolidação React.
  - Consolidação do backend reativo WebFlux/R2DBC alinhada à stack Spring Boot.
  - Atualização de `angular-catalog.yaml`, `spring-reactive-catalog.yaml` e seus respectivos routers.
  - Remoção de 9 especialistas legados.
- **Gate de Saída**: Validação cruzada de conformidade de frameworks web e reativos via `pytest`.

### Fase 3 — Stacks Legadas e Especializadas (Enterprise & Polyglot)
- **Escopo**:
  - `python`: 7 especialistas → 3 (`python-arch-advisor`, `python-developer`, `python-test-engineer`).
  - `ejb`: 7 especialistas → 3 (`ejb-arch-advisor`, `ejb-developer`, `ejb-test-engineer`).
  - `struts`: 7 especialistas → 3 (`struts-arch-advisor`, `struts-developer`, `struts-test-engineer`).
- **Artefatos Entregues**:
  - Criação dos 6 novos especialistas consolidados e preservação dos 3 arquitetos.
  - Atualização dos 3 sub-catálogos e 3 routers (`python-router`, `ejb-router`, `struts-router`).
  - Remoção de 12 especialistas legados.
- **Gate de Saída**: Verificação de integridade dos padrões de isolamento legado JEE/Struts e assincronismo Python.

### Fase 4 — Consolidação de Dados Multi-Engine (`database`)
- **Escopo**:
  - `database`: 6 especialistas de banco de dados → 3 especialistas de domínio unificado.
  - Criação de `database-arch-advisor` (read-only unificado para Oracle e Informix: planos de execução EXPLAIN, índices e modelagem).
  - Criação de `oracle-database-specialist` (mutativo: DDL migrations e PL/SQL).
  - Criação de `informix-database-specialist` (mutativo: DDL migrations e rotinas SPL).
- **Artefatos Entregues**:
  - Atualização estrutural de `database-catalog.yaml` e `database-router.agent.md`.
  - Remoção dos 6 especialistas legados sob as subpastas `informix/` e `oracle/`.
- **Gate de Saída**: Auditoria de regras de banco de dados, confirmação do caráter read-only do arquiteto de tuning e checagem de integridade de schemas.

### Fase 5 — Governança Global, Testes Determinísticos e Sincronização Atômica
- **Escopo**:
  - **Templates Canônicos**: Atualização de `templates/agent-template.md` e `templates/router-agent.md` com a regra mandatória de 3 especialistas por stack.
  - **Testes Determinísticos**: Implementação de `tests/governance_audit/test_agent_count_per_stack_governance.py` com asserção formal:
    `assert len(stack_specialists) == 3 and len(stack_routers) == 1` para cada uma das 8 stacks.
  - **Sincronização Atômica (R-015)**: Consolidação definitiva em `catalog.yaml` raiz, `routing-graph.yaml`, `agent-router.agent.md`, `README.md` central e índice de skills.
- **Gate de Saída**: Suíte `pytest tests/governance_audit/` 100% verde com zero warnings de schema e zero referências órfãs.

---

## 12. Invariantes de Governança Preservados

A execução de todas as fases vincula-se de modo inegociável aos seguintes invariantes:

1. **R-064 (Duplo Gate Documental)**: É expressamente proibido que agentes mutativos (`developer` ou `test-engineer`) iniciem modificações sem o parecer ou blueprint prévio aprovado pelo `arch-advisor` correspondente.
2. **R-066 (Progressive Disclosure & Context Budget)**: Prompts de agentes não devem ultrapassar orçamentos estritos de contexto. Conhecimentos especializados detalhados devem ser consumidos via `source_docs_lazy:`.
3. **R-046 (Single Responsibility & Coesão de Papel)**: A trindade (Arquiteto Read-Only / Desenvolvedor Mutativo de Aplicação / Engenheiro de Testes QA) é o limite mínimo indivisível de especialização.
4. **R-055 / R-054 (Baseline de Ferramentas e Router Contracts)**: Routers locais preservam seu baseline estrito de 7 ferramentas canônicas e contrato intacto com o `@agent-router` central.

---

## 13. Critérios de Aceite e Definition of Done

- [x] Inventário formalmente reestruturado: exatamente 24 especialistas + 8 routers (32 agentes totais de stack) ao término da Fase 5.
- [x] Mapeamento De -> Para de todas as 8 stacks documentado e validado.
- [x] Tabela comparativa comprovando redução de 57.1% de especialistas incorporada.
- [x] Matriz de Migração de Conteúdo e Skills mapeando 100% das heurísticas legadas para `.github/skills/`.
- [x] Política de Modelos Canônica (Sonnet 5 universal + Matriz Biparadigma sob R-021.2) formalizada.
- [x] Roadmap de 5 Fases sequenciadas com gates de entrada e saída claramente definidos.
- [x] Checkpoint HITL (R-064.1) submetido para aprovação humana antes de qualquer execução destrutiva de código.

---

## 14. Fechamento e Conclusão do Roadmap Geral (Fases 4 e 5 Concluídas)

Em conformidade com a Fase 4 (Consolidação da stack Python) e a Fase 5 (Quality Gate Geral e Sincronização Atômica):
1. **Stack Python consolidada no padrão Triádico 3+1**:
   - `python-developer`: unifica feature-developer e bug-fixer (FastAPI, Flask, Django, Pydantic, SQLAlchemy, RCA e diffs mínimos).
   - `python-test-engineer`: unifica unit-test-writer, integration-test-writer e test-fixer (pytest, TestClient/AsyncClient, Testcontainers, retry cap R-053).
   - `python-arch-advisor`: Read-Only, absorvendo profiling, mitigação de N+1 queries, tuning de event loop asyncio e tipagem PEP 484/mypy strict.
   - `python-router`: Decision Tree triádica, 7 tools R-054 canônicas.
   - Extirpação completa dos 6 especialistas legados.
2. **Quality Gates Determinísticos Criados e 100% Verdes**:
   - `test_python_consolidation_governance.py`: valida topologia, contratos de fronteira e quality gates da stack Python.
   - `test_agent_count_per_stack_governance.py`: valida formalmente o teto de exatamente 3 especialistas por router para todas as 8 stacks consolidadas (`spring-boot`, `react`, `angular`, `spring-reactive`, `ejb`, `struts`, `python`, `database`), totalizando 24 especialistas + 8 routers = 32 agentes de domínio.
3. **Sincronização Atômica Concluída**:
   - `catalog.yaml`, `routing-graph.yaml`, `agent-router.agent.md`, `protocol_roles.json`, AgentCards A2A em `.a2a/agentcards/`.
   - Suíte de governança executada com 100% de aprovação (zero falhas).

---

## 14. Próximos Passos (Pós-Aprovação)

1. Submissão formal deste Plano de Planejamento ao comitê de governança / usuário via checkpoint HITL.
2. Acionamento dos agentes arquitetos para emissão dos Planos de Implementação Técnica da Fase 1 (`@spring-boot-arch-advisor` e `@react-arch-advisor`).
3. Execução em lote via ferramentas sandbox do context-mode (Plan-Then-Batch, R-059).
4. Homologação contínua via suíte determinística de testes em `tests/governance_audit/`.
