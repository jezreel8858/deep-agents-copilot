# CHANGELOG — Deep Agents Copilot (Estrutura de Governança Genérica e Reutilizável

Todas as mudanças significativas nesta base de governança são documentadas aqui.

Formato: [Semantic Versioning](https://semver.org/) | [Conventional Commits](https://www.conventionalcommits.org/)

---

## [2.7.0] — 2026-09-11

### Refatorado & Simplificado
- **Coesão em `.github/` — Simplificação Arquitetural e Desacoplamento Definitivo (Cenário 2)**:
  - **Extinção de `docs/ai-context/catalog.yaml` e `docs/ai-context/binding.md`**: Eliminação de manifestos intermediários redundantes. Os adapters genéricos agora são 100% autodeclaratórios via frontmatter YAML nativo `applyTo` nos próprios arquivos `.instructions.md`, lidos diretamente pelo GitHub Copilot e demais IDEs.
  - **Catálogo Único de Agents (`.github/agents/catalog.yaml`)**: Fim da colisão de nomes. O repositório passa a ter estritamente **um** arquivo `catalog.yaml`, eliminando a necessidade de desambiguações em prompts e no `repo-map.md`.
  - **Migração do Overlay Local de Projetos**: Substituição de `docs/ai-context/catalog.local.yaml` por `.github/projects.local.yaml` (gitignored, R-043) e de seu template rastreado para `.github/projects.local.yaml.example`.
  - **SSOT de Binding Consolidado (`.github/instructions/README.md`)**: O índice de instructions absorveu formalmente todas as definições da hierarquia de 3 camadas (Global $\rightarrow$ Stack $\rightarrow$ Projeto), discovery de IDEs e ciclo de vida de projetos locais.
  - **Extinção do `repo-map.md` e Consolidação Nativa**: O arquivo `repo-map.md` foi integralmente absorvido e extinto. A árvore física oficial do repositório foi incorporada ao `README.md` raiz (para humanos) e os caminhos canônicos consolidados na seção 7 de `CLAUDE.md` e `.github/copilot-instructions.md` (para IAs), eliminando mais um ponto de manutenção e duplicação.
  - **Remoção Completa do Diretório `docs/ai-context/`**: Diretório extinto por completo, concentrando toda a configuração e governança de IA sob `.github/`.
  - **Sincronização em Cascata (R-015/R-043/R-046)**: Atualização atômica de `.gitignore`, `.githooks/pre-commit`, `CLAUDE.md` (R-034 e R-043), `.github/copilot-instructions.md`, todos os agents e prompts operacionais, scripts de tooling e suíte de testes (`test_local_project_isolation.py`, `test_governance_smells.py`, `test_routing_quality_gate.py`), mantendo 100% de conformidade e 89/89 testes aprovados no pytest.

---

## [2.6.2] — 2026-09-11

### Adicionado
- **Prompt `/init-context` — Verificação de Deriva de Stack e Instruções Locais (Drift Detection)**:
  - Adicionado novo PASSO 7 (expandindo a execução para 9 passos) para detectar discrepâncias entre os manifestos reais dos projetos locais externos (`package.json`, `pom.xml`, `build.gradle`, `pyproject.toml`) e os adapters locais em `.github/instructions/local/<projeto>.instructions.md` (R-043).
  - Identifica automaticamente upgrades de versão major de frameworks (ex.: Angular 20 → 21, Spring Boot 2.x → 3.x) e migrações de test runners/bibliotecas (ex.: Karma/Jasmine → Vitest, JUnit 4 → JUnit 5, Jest → Vitest).
  - Adiciona remediação guiada interativa via `ask_questions` (R-009) para sincronização do adapter local, linha dedicada na tabela de checklist consolidada, recomendações e troubleshooting.
  - Inclusão da tool `ask_questions` em `tools:` e de `.github/skills/project-scanner/SKILL.md` em `source_docs:` do prompt.

---

## [2.6.1] — 2026-09-11

### Refatorado
- **Desacoplamento de Cardinalidade Normativa (Herança Aberta de Governança)**:
  - Substituição da referência rígida ao contador fechado (`R-001..R-051`) pela herança aberta desacoplada (`regras normativas globais em CLAUDE.md`) em 45 agents/templates e todos os prompts, skills e catálogos.
  - Eliminação definitiva do problema de *Shotgun Surgery* (manutenção em cascata e gasto desnecessário de créditos Copilot a cada nova regra adicionada ao `CLAUDE.md`).
- **Redefinição do Smell 2.15 (`governance-audit-patterns/SKILL.md` & `test_governance_smells.py`)**:
  - Inversão de sentido do Smell 2.15 de "range desatualizado" para "Acoplamento Rígido de Range Normativo (Hardcoded Range Coupling)".
  - Nova validação automatizada em `test_smell_2_15_no_hardcoded_normative_rule_range`: exige que todo agent herde `CLAUDE.md` e proíbe a reintrodução de ranges numéricos hardcoded em agents.

---

## [2.6.0] — 2026-09-10

### Adicionado
- **Suíte de Testes de Conformidade de Templates (Disjunção 1-de-N)**:
  - `tests/governance_audit/test_template_sections.py`: Implementação estática da regra de conformidade polimórfica (Smells 2.9, 2.10 e 2.11), validando seções de agents, prompts e skills contra os templates canônicos com extração dinâmica e normalização semântica.
  - `tests/governance_audit/test_router_agents.py`: Validação determinística especializada para os 6 agents com perfil de Router / Supervisor (`agent-router`, `angular-router`, `spring-boot-router`, `spring-reactive-router`, `ejb-router`, `database-router`), exigindo as 6 seções obrigatórias e menor privilégio de ferramentas.
  - Template canônico oficial para roteadores em `.github/agents/templates/router-agent.md`.
- **Suíte de Testes de Trajetórias de Workflows Canônicos (R-050) & Simulador MAS**:
  - `tests/operational_flow/casos-workflows.yaml`: Catálogo declarativo com 8 cenários de ponta a ponta (E2E) cobrindo os 5 workflows canônicos, detecção de deriva de intenção (R-042), circuit breaker (R-050.2) e fast-chaining (R-050.1).
  - `tests/operational_flow/test_workflow_trajectories.py`: Validação determinística das transições de estados, isolamento de ferramentas por etapa e thresholds de cobertura (100% workflows, ≥85% etapas, ≥15 agentes).
  - `tests/operational_flow/workflow_eval_simulator.py`: Motor CLI para auditoria estática de trajetórias em lote e cálculo em tempo real das 5 dimensões de cobertura de MAS (`--coverage`).
  - `.github/prompts/eval-workflows.prompt.md`: Prompt operacional parametrizado para avaliação de trajetórias via modelo `Gemini 3.8 Flash`.
- **Documentação Arquitetural de Testes MAS (`tests/README.md`)**:
  - Documentação completa da Pirâmide de Testes de Sistemas Multi-Agentes (MAS), detalhamento arquivo por arquivo, objetivos de qualidade, métricas de cobertura e guia de execução.

### Alterado
- **Configuração do Pytest (`pytest.ini`)**:
  - Inclusão da diretiva `pythonpath = .` garantindo resolução determinística da raiz do projeto independente da forma de invocação do runner.

---

## [2.5.0] — 2026-09-10

### Adicionado
- **Mapa do Repositório Canônico (`docs/ai-context/repo-map.md`)**:
  - Fonte de verdade de navegação determinística de arquivos (princípio Zero Blind Searches), contendo guia de localização direta, tabela rápida de arquivos de governança (Quick File Finder) e árvore física estrutural do projeto.
- **Whitelist de Busca e Indexação para ripgrep (`.ignore` e `.rgignore`)**:
  - Arquivos de configuração na raiz liberando a varredura de `!.github/` e `!.github/**` pelas ferramentas de busca (`file_search` e `grep_search`), sanando falhas de localização com 0 matches de agents e skills em workspaces multi-root.

### Alterado
- **Desambiguação Canônica dos Catálogos (`catalog.yaml`)**:
  - Formalizada a distinção unívoca entre o Catálogo de Agents (`.github/agents/catalog.yaml` — metadados, modelos Gemini/Claude, prioridades) e o Catálogo de Binding (`docs/ai-context/catalog.yaml` — manifest de stacks e adapters).
  - Atualizadas as instruções em `CLAUDE.md`, `.github/copilot-instructions.md` e `.github/agents/agent-router.agent.md` proibindo explicitamente que o router busque modelos em `docs/ai-context/catalog.yaml`.
  - Inclusão do `repo-map.md` como leitura de infraestrutura mandatória no `@agent-router`.

---

## [2.4.0] — 2026-09-10

### Adicionado
- **Novos Smells de Governança (20 Smells Canônicos)** — originados de auditoria real do primeiro ciclo completo de `WORKFLOW-FEATURE-DEVELOPMENT` (feature de Gestão de Usuários/Auditoria Global no projeto de referência):
  - **Smell 2.18 (Gap de Definição de Pronto — Feature Não-Alcançável / Rota Órfã de Navegação)**: nenhum artefato do pipeline (blueprint, implementer, test-strategy, code-review) tratava "alcançabilidade via navegação" como critério de conclusão — feature entregue com testes verdes e build íntegro, porém sem entrada correspondente no menu/sidenav do projeto.
  - **Smell 2.19 (Ausência de Verificação de Reuso de Design System / Componentes Compartilhados)**: agent implementer de UI criou HTML/CSS customizado (`<select>` nativo, cards/badges ad-hoc) ignorando catálogo interno de componentes compartilhados já documentado no projeto (`docs/componentes-shared.md`, `docs/padrao-angular-material.md`).
  - **Smell 2.20 (Duplicação por Aninhamento de Router — Nested Subagent Sprawl)**: identificada e eliminada a duplicação na cadeia de orquestração onde o `@agent-router` invocava executores downstream via `run_subagent` por dentro de si mesmo e, ao retornar ao Orquestrador Raiz com o bloco de decisão, o orquestrador re-disparava o mesmo downstream. Formalizada a regra de Delegação Plana (Flat Delegation) em R-047, R-037, `agent-router.agent.md` e `handoff-governance/SKILL.md` (§ 2.3), acompanhada de teste estático determinístico no Tier 1 (`test_smell_2_20_router_flat_delegation_rule`).
- **Reforço de Definition of Done em Frontend**: `angular-implementation-patterns/SKILL.md` ganha passo 0 (Reuse-First) e passo 7 (Navegabilidade) no Workflow — Feature Nova, com checklist de PR e anti-padrões correspondentes.
- **Princípio Reuse-First**: `frontend-componentization-patterns/SKILL.md` ganha nova seção "Reuso-First: Antes de Criar Componente Novo" com processo objetivo de busca em `shared/`/documentação interna antes de qualquer HTML/CSS customizado.
- **8ª Dimensão de Code Review**: `code-review-patterns/SKILL.md` § 2 ganha dimensão "UX/Design System & Navegabilidade", cobrindo os Smells 2.18/2.19 na revisão de diffs de frontend.
- **Template Canônico Completado em 2 Agents**: `angular-feature-developer.agent.md` e `angular-ui-stylist.agent.md` — únicos 2 agents do catálogo Angular sem `Decision Tree`/`Checklist Antes de Entregar`/`Quando Delegar` — receberam as 3 seções ausentes (Smell 2.9 aplicado retroativamente).
- **Reforço em `tech-solution-architect.agent.md`**: Context Firewall `[FRONTEND_TASKS]` e Checklist Antes de Entregar agora exigem explicitamente tarefa de integração ao shell de navegação e consulta prévia a design system compartilhado quando a feature introduzir rota(s)/UI nova(s).
- **Reforço em `code-review.agent.md`**: novo branch no Decision Tree e item 6 nos Padrões Obrigatórios para validar navegabilidade e reuso de design system antes do veredito em diffs de frontend.
- **Reforço em `test-strategy.agent.md`**: item 5 dos Padrões Obrigatórios exige cenário de Navegabilidade na Matriz de Cenários Frontend quando houver rota nova.
- **Adapter Local Corrigido (`[PROJETO-ALVO].instructions.md`)**: novas seções § 1.1 (Design System Interno — Consulta Obrigatória) e § 1.2 (Navegação — SidenavComponent/Shell como Única Fonte de Verdade), referenciando explicitamente a documentação interna de componentes/design system e o componente de shell de navegação do projeto — o adapter não continha nenhuma dessas referências antes desta correção, apesar de os documentos já existirem no projeto.

### Autocrítica de Processo (Achado de Execução)
- Identificado e documentado que a fidelidade de handoff da Etapa 5 (`tdd_domain_implementation`) de `WORKFLOW-FEATURE-DEVELOPMENT` depende de invocação **real** de `run_subagent` para o specialist correspondente — rotular a resposta com `Agente Ativo: <specialist>` sem a invocação real não carrega o contrato/checklist do agent, tornando as correções de conteúdo insuficientes por si só sem a disciplina de delegação genuína já normatizada em R-042.

---

## [2.3.0] — 2026-09-10

### Adicionado
- **Regra Normativa R-051 (Proteção Anti-Corrupção em Edição de Arquivo Único Grande/Estruturado)**: Formalizada em `CLAUDE.md` e `efficient-batch-code-modification/SKILL.md` (§ 5). Veda o uso de `insert_edit_into_file` em arquivos com mais de 200 linhas, formato YAML/JSON ou consumidos por CI/testes, exigindo o Padrão de Edição Segura Verificada (leitura integral, contagem unívoca de ocorrência da âncora, all-or-nothing write e releitura de confirmação).
- **Snippet Canônico de Edição Segura (`safe-single-file-edit-pattern.js`)**: Materializado em `.github/skills/efficient-batch-code-modification/snippets/safe-single-file-edit-pattern.js` como template reutilizável para context-mode (`ctx_execute`), em estrita conformidade com R-026 (código real fora do corpo da skill).
- **Novos Smells de Governança (17 Smells Canônicos)**:
  - **Smell 2.15 (Citação de Range Normativo Desatualizado — Drift de R-0XX)**: Formalizada em `governance-audit-patterns/SKILL.md` e amparada por teste determinístico no Tier 1 (`test_smell_2_15_no_stale_normative_rule_range`), que lê dinamicamente o maior R-0XX de `CLAUDE.md` e bloqueia desatualizações nos agents.
  - **Smell 2.16 (Agent Mutativo Sem Skill de Edição Segura Referenciada)**: Formalizada em `governance-audit-patterns/SKILL.md` e amparada por teste determinístico no Tier 1 (`test_smell_2_16_mutating_agents_reference_safe_editing_skill`), exigindo que todo agent com tools mutativas referencie `efficient-batch-code-modification`.
- **Transparência de Base de Conhecimento — Terceira Linha do Banner Universal (`Skills Carregadas`)**: Estendido o Banner Universal de Identidade em `CLAUDE.md` (R-042), `agent-contracts/SKILL.md` (§ 0 e § 8), `.github/copilot-instructions.md` e `handoff-governance/SKILL.md` (§ 5.2) para exibir compulsoriamente a linha `Skills Carregadas: <skill-1>, ...` em cada resposta, garantindo visibilidade no chat sobre quais skills foram pre-fetched e consultadas a cada turno.

### Evoluído
- **Auditoria e Refinamento Profundo dos 5 Workflows Canônicos (`workflows.md` e `routing-graph.yaml`)**:
  - **Resolução de Papéis Genéricos (`specialist-<papel>`)**: Formalizada convenção em `workflows.md` § 1.3 mapeando papéis agnósticos de stack (fixer, tester, stylist, implementer, advisory) para os agentes concretos dos sub-catálogos locais (`angular-catalog.yaml`, `spring-boot-catalog.yaml`, `spring-reactive-catalog.yaml`, `ejb-catalog.yaml`).
  - **Princípio Arquitetural de Separação Declarador/Executor em Circuit Breakers**: Formalizado em `workflows.md` § 5 (Invariante #6) e § 8.1. Agentes estritamente read-only (`runtime-verifier`, `refactor-planner`) apenas detectam e declaram vereditos de bloqueio; a execução física de reversão atômica (`git checkout`/`git restore`) é sempre executada pelo especialista de implementação correspondente via `run_subagent`.
  - **WF1 (`WORKFLOW-BUG-FIX`)**: Repro Gate com teto de 2 tentativas e estado terminal Não-Reproduzível; distinção entre testes unitários puros vs testes exigindo contexto de framework/DOM; checkpoint de segurança condicional (R-048.1) para correções que toquem autenticação/identidade.
  - **WF2 (`WORKFLOW-REFACTORING`)**: Safety net com cobertura orientada a risco (`test-coverage-governance/SKILL.md`) em substituição ao threshold plano de 80%; checkpoint de aprovação humana para breaking change, schema ou blast radius grande; limite de escala do DAG Mikado em 15 nós; rollback atômico e incremental decidido pelo planner e executado pelos specialists.
  - **WF3 (`WORKFLOW-TECHNICAL-ANALYSIS`)**: Inclusão de `devops-engineer` e `code-style-enforcer` no dispatch analítico; suporte a Fan-out/Fan-in multidimensional (`[P]`); teto de profundidade em sub-rotinas (`MAX_DEPTH = 3`); escape hatch formal para análises sem achados (`"nenhuma_proposta_necessaria_conformidade_validada"`).
  - **WF4 (`WORKFLOW-FEATURE-DEVELOPMENT`)**: Sequenciamento de requisitos (`@requirements-analyst`) e decomposição (`@feature-planner`); sub-rotina de banco (`@database-specialist`); particionamento com tags de stack; shift-left de testes de segurança em TDD; circuit breaker de 2 tentativas no loop de remediação de segurança.
  - **WF5 (`WORKFLOW-GOVERNANCE-MAINTENANCE`)**: Sincronização atômica estruturada por tipo de artefato, corrigindo a omissão de `evals/casos-roteamento.yaml` para novos agents (R-040); circuit breaker de 3 tentativas no loop de autofix.
- **Sincronização de Ranges Normativos**: Atualizados 100% dos 44 agents com seção de regras herdadas e todos os prompts e catálogos para a numeração consolidada `R-001..R-051`.
- **Expansão de Isolamento Read-Only**: `READONLY_ADVISORY_AGENTS` expandido de 8 para 17 agents em `test_operational_workflows.py`, blindando especialistas consultivos contra tools mutativas.

---

## [2.2.0] — 2026-09-10

### Adicionado
- **Regra Normativa R-050 (Workflows Operacionais Determinísticos — Pipelines de Estado Finito)**: Formalizada em `CLAUDE.md` a obrigatoriedade de vincular e executar toda solicitação técnica através de um dos 5 Workflows Canônicos:
  1. `WORKFLOW-BUG-FIX` (Bugs, Erros 500/NPE, Falhas de Layout e Regressões em 5 etapas).
  2. `WORKFLOW-REFACTORING` (Refatoração Estrutural, Modernização e Desacoplamento em 5 etapas).
  3. `WORKFLOW-TECHNICAL-ANALYSIS` (Análise Técnica, Diagnóstico e Auditoria Especializada em 3 etapas).
  4. `WORKFLOW-FEATURE-DEVELOPMENT` (Nova Feature e Evolução Funcional E2E em 6 etapas).
  5. `WORKFLOW-GOVERNANCE-MAINTENANCE` (Auditoria, Padronização e Manutenção de Governança em 3 etapas).
- **Especificação Canônica dos 5 Workflows (`.github/agents/workflows.md`)**: Novo artefato canônico com diagramas Mermaid em `flowchart TD`, matrizes de entrada/saída, regras de não-desvio e invariantes de execução.
- **Roadmap Visual de Execução no Chat (Anti-Cegueira de Fluxo)**: Padronizada no `@agent-router`, `agent-contracts` (§ 0.1) e `workflows.md` (§ 6) a exibição compulsória do bloco visual `### 🗺️ Pipeline de Execução do Workflow (<total> etapas)` com marcadores `[✅]` (Concluído), `[▶]` (Em Andamento) e `[⏳]` (Pendente) para eliminar a cegueira do usuário durante o fluxo.
- **Extensão de Handoff v1.2 (`workflow_tracking`)**: Adicionado ao schema formal de `handoff-governance` o bloco `workflow_tracking` (`workflow_id`, `etapa_atual`, `total_etapas`, `nome_etapa`, `proximos_agentes_permitidos`, `politica_desvio: "strict"`).
- **Protocolo de Encadeamento de Workflows (Fast-Chaining — R-050.1)**: Reconhecimento de aprovações/ordens de execução de diagnósticos prévios no `@agent-router`, transferindo `carry_over_state` diretamente para a Etapa 1 do workflow de implementação sem desvio para `@prompt-structuring`.
- **Estados de Contingência & Circuit Breaker (R-050.2)**: Inclusão de caminhos formais de rollback (4b em bugfix e 5b em refatoração) nos diagramas e contratos para reversão atômica de diffs sujos e escalação humana via `ask_questions` após esgotar o teto de 3 tentativas de teste ou violar regras de negócio.
- **Rastreamento Multi-Projeto no Handoff (v1.3 — R-050.3)**: Extensão do `workflow_tracking` com `projeto_alvo` (`id`, `root_path`, `adapter_ref`) e `chaining` para garantir isolamento em workspaces multi-repositório.
- **Nova Suíte de Testes de Isolamento de Projetos Locais (`test_local_project_isolation.py`)**: 5 novos testes automatizados determinísticos cobrindo 100% das regras R-038, R-043 e R-044 (varredura de git-tracked files, gitignore guardrails, caminhos de máquina reais e genericidade de placeholders).
- **Verificação #5 no Pre-commit Hook (`.githooks/pre-commit`)**: Bloqueio ativo no commit contra menções a projetos registrados em `catalog.local.yaml`.
- **Testes de Conformidade de Workflows**: 8 testes determinísticos em `tests/operational_flow/test_operational_workflows.py` validando workflows, integridade de `workflows.md`, declaração no grafo, fast-chaining, circuit breaker e rastreamento de projeto-alvo.
- **Novos Casos na Suíte de Evals**: `canon-043` (layout e erro runtime), `canon-044` (refactor com alvo) e `regr-026` (bloqueio de desvio de bugs para `prompt-structuring`) em `.github/agents/evals/casos-roteamento.yaml`.

### Evoluído
- **Regra Normativa R-041 (Fast-Path Determinístico)**: Ajustada em `CLAUDE.md`, `copilot-instructions.md`, `routing-graph.yaml` e `agent-router.agent.md` para permitir que solicitações com intenções operacionais evidentes (bugs, refatoração com alvo, diagnósticos diretos) bypassam o `@prompt-structuring` diretamente para a etapa 1 do workflow, eliminando latência e perguntas redundantes.
- **Agent Router (`@agent-router` v2.0.0)**: Inserido Passo 0.4 (Classificação de Fast-Path) antes do Passo 0.5 e inclusão de `Workflow:` e `Etapa do Workflow:` no Formato de Saída.
- **Grafo Estrutural (`routing-graph.yaml`)**: Adicionado bloco de primeira classe `workflows:` declarando estados finitos e inclusão de `fast_path_bypass` na aresta de `prompt-structuring`.

---

## [2.1.0] — 2026-09-06

### Adicionado
- **Regra Normativa R-046 (Injeção Compulsória de Modificação de Código em Lote)**: Formalizada em `CLAUDE.md` a obrigatoriedade da skill operacional `efficient-batch-code-modification` em toda tarefa que envolva escrita, refatoração ou alteração em massa de código, erradicando loops sequenciais de roundtrip e reenvio recursivo de contexto.
- **Injeção Compulsória em `prompt-structuring` (R-046)**: Adicionado mecanismo no refinamento de prompt para injetar nativamente a constraint de dry-run prévio em memória, single-turn batching e diffs cirúrgicos em `<constraints>` para qualquer tarefa de código sem exigir intervenção manual do usuário.
- **Novo Agente `@governance-maintainer` (v1.0.0)**: Especialista executor em manutenção atômica, refatoração estrutural e sincronização em lote de artefatos de governança (`.github/agents`, `.github/skills`, `.github/prompts`, catálogos e grafo de roteamento). Opera sob o protocolo de single-turn batching e priorização de context-mode sobre terminal.
- **Nova Skill `efficient-batch-code-modification` (Tier 1, Process)**: Protocolo operacional para economia de tokens e créditos Copilot — análise prévia em memória (dry-run), tool calls de escrita emitidas em lote na mesma rodada e diffs cirúrgicos mínimos.

### Evoluído
- **Agents Executores de Código Alinhados a R-046**: Inclusão explícita de `efficient-batch-code-modification` em `source_docs`, `skills:` e diretrizes operacionais de 26 agents (database-specialist e 25 especialistas de domínio em frontend/angular, backend/spring-boot, backend/spring-reactive e backend/ejb).
- **Evolução de `analysis-architect` para `tech-solution-architect` (v2.1.0)**:
  - Adotado o padrão consolidado de mercado *Spec-First / Technical Blueprint* e *Context Firewall* (particionamento isolado `[BACKEND_TASKS]` e `[FRONTEND_TASKS]` para eliminar alucinações e perda de contexto downstream).
  - Escopo: Viabilidade técnica, elaboração de Blueprint, contratos OpenAPI/AsyncAPI, modelo de dados (Flyway) e divisão de tarefas por stack antes do despacho aos Domain Routers.
  - Sincronização atômica de governança (R-015/R-040): atualizados `catalog.yaml`, `routing-graph.yaml`, `agent-router.agent.md`, `casos-roteamento.yaml` (novo `canon-036`), `requirements-analyst.agent.md`, `feature-planner.agent.md`, `refactor-planner.agent.md`, `code-review.agent.md`, `test-strategy.agent.md`, `bug-triage.agent.md`, `code-knowledge-graph.agent.md`, `copilot-instructions.md`, `CLAUDE.md`, `README.md` e `.index.json`.
  - Substituição do arquivo `analysis-architect.agent.md` por `tech-solution-architect.agent.md`.

### Consolidado
- **Consolidação Biparadigma de Modelos nos Agents e Prompts**:
  - **Paradigma do Prompt Procedural (SLMs / Alta Velocidade — Padrão Base)**: Definido `"Gemini 3.8 Flash"` como escolha padrão em toda a base (54 agents e 16 prompts procedurais/determinísticos: implementadores TDD, fixers, test-writers, geradores de adapters, linters/enforcers, scanners e roteadores de domínio).
  - **Paradigma do Prompt Decompositivo / Raciocínio Guiado (Pensamento Profundo)**: Reservado `"Claude Sonnet 5"` exclusivamente para perfis deliberativos de alta complexidade:
    - **Orquestração e Triagem Central**: `@agent-router` (agent e prompt `/agent-router`).
    - **Arquitetura Técnica & Blueprint**: `@tech-solution-architect`.
    - **Planejamento Decompositivo & Rollback**: `@refactor-planner` e prompt `/plan`.
    - **Elicitação & Decomposição Crítica de Requisitos**: `@requirements-analyst`.
    - **Pesquisa Multi-hop & Síntese Deliberativa**: `@deep-search` (agent e prompt `/deep-search`).
    - **Especialistas de Arquitetura Consultiva (Advisors)**: `@angular-arch-advisor`, `@spring-boot-arch-advisor`, `@spring-reactive-arch-advisor`, `@ejb-arch-advisor`.
  - Sincronização atômica (R-015) em todos os catálogos (`catalog.yaml`, `angular-catalog.yaml`, `spring-boot-catalog.yaml`, `spring-reactive-catalog.yaml`, `ejb-catalog.yaml`) e na skill `governance-factory-patterns/SKILL.md` (§ 9.1).
  - Validação via `get_errors` com 0 erros em todos os arquivos modificados.

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
- **`docs/ai-context/evals/casos-roteamento.yaml`**: `canon-018` (implementação direta de bugfix), `regr-014` corrigido (implementação no próprio domínio não é deriva), `regr-016` novo (deriva real cross-stack) — suíte passa de 35 para 40 casos.

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

## [1.3.0] — 2026-08-29

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
