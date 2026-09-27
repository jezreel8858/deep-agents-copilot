# Mapa do Repositório (Repo Map) — deep-agents-copilot

> **Fonte de verdade para navegação determinística de arquivos.**
> Este mapa documenta a localização exata de todos os componentes de governança, agents, skills, prompts, adapters e documentação deste repositório, eliminando buscas cegas e falhas de localização (`0 matches`).

---

## Metadados do Mapa
- **Última Atualização:** 2026-09-27
- **Versão:** v2.42.0
- **Alinhamento Normativo:** R-015 (Atualização Atômica de Catálogo), R-037/R-040 (Roteamento), R-043 (Overlay Local) e R-064 (Duplo Gate Documental de Planejamento e Implementação)

---

## 1) Princípio de Localização Direta (Zero Blind Searches)

Agentes de IA devem sempre priorizar **caminhos canônicos diretos** (`read_file` ou `ctx_execute` com o caminho relativo exato) em vez de buscas exploratórias especulativas (`file_search` ou `grep_search`).

Quando for estritamente necessário buscar por padrão:
- Use glob com curinga inicial: `**/<nome-do-arquivo>` (essencial em workspaces multi-root).
- Os arquivos de busca `.ignore` e `.rgignore` na raiz liberam a indexação de `.github/` para ferramentas baseadas em ripgrep.

---

## 2) Desambiguação Crítica: Catálogos e Binding

| Arquivo | Localização Canônica | Propósito Exclusivo | O que contém |
|---|---|---|---|
| **Catálogo de Agents** | `.github/agents/catalog.yaml` | Metadados dos 36 agents do ecossistema | Modelos recomendados (Gemini, Claude), prioridades, domínios, related_skills, source_docs |
| **Manifest de Binding e Adapters** | `.github/instructions/README.md` | Carregamento hierárquico e stacks de tecnologia | Lista de adapters canônicos por stack, convenções e regras de binding |
| **Overlay Local de Projetos** | `.github/projects.local.yaml` | Projetos locais conectados (gitignored, R-043) | Configurações locais privadas de repositórios do desenvolvedor |
| **Template de Overlay Local** | `.github/projects.local.yaml.example` | Modelo rastreado para novos workspaces | Estrutura de exemplo para configuração local sem vazamento |

> ⚠️ **ATENÇÃO AGENTES**: Ao buscar o modelo de um agent (`[Model] Delegando para @<agent>`), consulte EXCLUSIVAMENTE `.github/agents/catalog.yaml`. NUNCA procure agents em outros catálogos.

---

## 3) Guia Rápido de Localização (Quick File Finder)

| Se você precisa de... | Caminho Canônico no Repositório |
|---|---|
| **Regras Globais de Governança (Ground Truth)** | `CLAUDE.md` |
| **Instruções Operacionais e Roteamento** | `.github/copilot-instructions.md` |
| **Catálogo Completo de Agents (ÚNICO)** | `.github/agents/catalog.yaml` |
| **Grafo Estruturado de Roteamento (R-040)** | `.github/agents/routing-graph.yaml` |
| **Workflows Operacionais Canônicos** | `.github/agents/workflows.md` |
| **Suíte de Evals de Roteamento** | `.github/agents/evals/casos-roteamento.yaml` |
| **Manifest de Binding e Adapters** | `.github/instructions/README.md` |
| **Índice Estruturado de Skills** | `.github/skills/.index.json` |
| **Catálogo Textual de Skills** | `.github/skills/README.md` |
| **Índice Completo de Prompts** | `.github/prompts/README.md` |
| **Planos de Planejamento por Workflow (R-064)** | `docs/plans/` |
| **Planos de Implementação Técnica (R-064)** | `docs/implementation-plans/` |
| **Portal Unificado de Documentação (Diátaxis)** | `docs/README.md` |
| **Mapa Estrutural do Repositório** | `docs/repo-map.md` |

---

## 4) Estrutura Física de Diretórios

```
deep-agents-copilot/
├── CLAUDE.md                                    # Governança global (regras R-001..R-064)
├── README.md                                    # Visão geral do repositório e estrutura física
├── CHANGELOG.md                                 # Histórico SemVer de versões e mudanças
├── .ignore / .rgignore                          # Whitelist para ripgrep indexar .github/
│
├── .github/
│   ├── copilot-instructions.md                  # Instruções operacionais Copilot e fast-paths
│   ├── projects.local.yaml                      # Overlay local de projetos (gitignored, R-043)
│   ├── projects.local.yaml.example              # Template rastreado do overlay local (R-043)
│   │
│   ├── agents/                                  # 36 Agents de IA
│   │   ├── catalog.yaml                         # ⭐ Catálogo com modelos e metadados dos agents (ÚNICO)
│   │   ├── routing-graph.yaml                   # ⭐ Grafo estrutural de transições (R-040)
│   │   ├── workflows.md                         # ⭐ Especificação dos Workflows Canônicos e de Ciclo de Vida
│   │   ├── agent-router.agent.md                # Entry point obrigatório (R-037/R-042)
│   │   ├── prompt-structuring.agent.md          # Refinamento de prompt (R-041)
│   │   ├── bug-triage.agent.md                  # Triagem e RCA de bugs
│   │   ├── pr-gatekeeper.agent.md               # Preparação de PR e commit
│   │   ├── governance-maintainer.agent.md      # Manutenção transversal e execuções em lote
│   │   ├── ... (outros agents raiz)
│   │   │
│   │   ├── evals/                               # Suíte de regressão de roteamento
│   │   │   └── casos-roteamento.yaml            # Casos canônicos, ambíguos e regressões
│   │   │
│   │   ├── frontend/angular/                    # Domínio Frontend Angular (sub-catálogo + 8 especialistas)
│   │   └── backend/                             # Domínios Backend (Spring Boot, Reactive, EJB, Python, DB)
│   │
│   ├── skills/                                  # 60 Skills Especializadas
│   │   ├── .index.json                          # Índice estruturado JSON de skills
│   │   ├── README.md                            # Catálogo descritivo de skills
│   │   └── ... (skills especializadas)
│   │
│   ├── prompts/                                 # Prompts Canônicos de Workflow (/init-context, /add-project-context...)
│   │   └── README.md                            # Índice de prompts
│   │
│   ├── hooks/                                   # Hooks de continuidade de contexto
│   │   ├── context-mode.json                    # Definições de hooks para MCP context-mode
│   │   └── README.md                            # Documentação dos hooks
│   │
│   └── instructions/                            # Adapters de Stack de Código
│       ├── README.md                            # ⭐ SSOT de Binding e Adapters
│       ├── angular-v21-frontend.instructions.md # Convenções Angular
│       ├── spring-boot-backend.instructions.md  # Convenções Spring Boot
│       ├── python-backend.instructions.md       # Convenções Python
│       ├── database.instructions.md             # Convenções Banco de Dados
│       ├── devops.instructions.md               # Convenções DevOps
│       └── local/                               # Adapters locais de projetos (gitignored, R-043)
│
├── docs/                                        # Documentação Técnica e Arquitetural (Diátaxis)
│   ├── README.md                                # Portal unificado de documentação
│   ├── repo-map.md                              # ⭐ Este Mapa do Repositório (Zero Blind Searches)
│   │
│   ├── plans/                                   # ⭐ Planos de Planejamento por workflow (R-064)
│   │   └── README.md                            # Convenções de nomenclatura e template de plano
│   │
│   ├── implementation-plans/                    # ⭐ Planos de Implementação técnica (R-064)
│   │   └── README.md                            # Convenções de nomenclatura e template técnico
│   │
│   ├── architecture/                            # Guias de Arquitetura e Governança
│   │   ├── ARCHITECTURE_AND_GOVERNANCE_GUIDE.md # Guia Canônico arc42
│   │   ├── AI_GOVERNANCE_DOCUMENTATION_GUIDE.md # Alinhamento NIST AI RMF e ISO 42001
│   │   ├── APPLICATION_SECURITY_GUIDE.md        # Matriz AppSec e OWASP Top 10
│   │   ├── BLUEPRINT_AGENT_OBSERVABILITY.md     # Arquitetura de observabilidade e tracing
│   │   └── EVALS_TEST_STRATEGY.md               # Estratégia de testes para evals de IA
│   │
│   ├── plan/                                    # Blueprints de Arquitetura e Pesquisas
│   │   ├── agent-profiles-taxonomy.md           # Taxonomia consolidada de agents de mercado
│   │   ├── plano-motor-migracao-agnostica.md    # Blueprint do motor de migração baseado em IR
│   │   └── plano-persistencia-incidentes-workflows.md # Blueprint de telemetria de incidentes
│   │
│   ├── agent-context/                           # Guias operacionais de ferramentas
│   │   ├── codegraph-guia-uso.md                # Guia de uso do CodeGraph
│   │   ├── context-mode.md                      # Guia operacional do Context Mode MCP
│   │   └── templates/                           # Templates de contexto de stack e codegraph
│   │
│   ├── context/                                 # Guias de configuração de ambiente e IDEs
│   │   ├── setup-context-mode-intellij.md       # Setup de context-mode no JetBrains
│   │   └── setup-telemetry-copilot.md           # Setup de telemetria OpenTelemetry / Langfuse
│   │
│   ├── ai-copilot/                              # Instruções auxiliares para IA
│   │   └── global-git-commit-instructions.md    # Convenções de Conventional Commits
│   │
│   ├── requirements/                            # Requisitos formais do sistema (EARS / INVEST)
│   │   ├── REQ-migration-engine.md              # Requisitos do motor de migração
│   │   └── REQ-workflow-incident-persistence.md # Requisitos de persistência de incidentes
│   │
│   └── schemas/                                 # Schemas JSON canônicos
│       ├── agentcard.schema.json                # Schema A2A Agent Card
│       ├── migration-ir.schema.json             # Schema da Representação Intermediária (IR)
│       └── workflow-incident.schema.json        # Schema de persistência de incidentes
│
├── tools/                                       # Ferramentas Utilitárias e Telemetria
│   ├── incident_recorder/                       # Motor de persistência de incidentes (SQLite + Supabase)
│   ├── codegraph-visualizer/                    # Visualizador de grafos de código
│   ├── context-insight-visualizer/              # Visualizador de insights de contexto
│   └── otel-langfuse/                           # Coletor OpenTelemetry proxy para Langfuse Cloud
│
└── tests/                                       # Suíte de Testes Automatizados (pytest)
    ├── governance_audit/                        # Auditoria de regras e smells de governança
    ├── routing_gate/                            # Quality gate de roteamento
    ├── operational_flow/                        # Testes de workflows operacionais
    ├── evals/                                   # Evals de acurácia de roteamento e seleção de tools
    ├── codegraph_visualizer/                    # Testes do visualizador de codegraph
    ├── context_insight_visualizer/              # Testes do visualizador de context-insight
    └── otel_langfuse/                           # Testes da suíte de telemetria Langfuse
```

---

## 5) Mapeamento Detalhado da Pasta `docs/`

A pasta `docs/` organiza o conhecimento técnico e os artefatos de governança e planejamento em subdiretórios especializados:

| Diretório / Arquivo | Finalidade e Descrição | Convenção / Regra |
|---|---|---|
| **`docs/plans/`** | **Planos de Planejamento por workflow (R-064)**. Registra a análise funcional, objetivos, blast radius e estratégia do workflow. | Convenção: `<AAAAMMDD>-<workflow>-<identificador-curto>.md` |
| **`docs/implementation-plans/`** | **Planos de Implementação técnica por workflow (R-064)**. Autorados por `<stack>-arch-advisor` com contratos de métodos, diffs cirúrgicos e comandos de teste. | Convenção: `<AAAAMMDD>-<workflow>-<identificador-curto>.md` |
| **`docs/architecture/`** | Guias canônicos de arquitetura técnica (`ARCHITECTURE_AND_GOVERNANCE_GUIDE.md` em formato arc42, AppSec, observabilidade). | Governança Global arc42 / NIST |
| **`docs/plan/`** | Blueprints arquiteturais, estudos de mercado (`agent-profiles-taxonomy.md`) e planos de componentes centrais do sistema. | Blueprints / ADRs |
| **`docs/agent-context/`** | Guias operacionais e manuais de ferramentas do ecossistema (`codegraph`, `context-mode`, templates de contexto). | Documentação Operacional |
| **`docs/context/`** | Configurações de setup de ambiente, integração com IDEs JetBrains e telemetria OTLP/Langfuse. | Setup de Ambiente |
| **`docs/ai-copilot/`** | Guias transversais para agentes de IA (ex.: instruções globais de Conventional Commits). | Diretrizes de IA |
| **`docs/requirements/`** | Especificações formais de requisitos de sistema baseadas em sintaxes EARS e critérios INVEST. | Requisitos Formais |
| **`docs/schemas/`** | Schemas JSON canônicos de validação estrutural (`agentcard`, `migration-ir`, `workflow-incident`). | Schemas de Validação |
| **`docs/README.md`** | Portal central de documentação indexado conforme o framework internacional Diátaxis. | Portal Diátaxis |
| **`docs/repo-map.md`** | Mapa do repositório para navegação determinística de arquivos (Zero Blind Searches). | SSOT de Localização |

---

## 6) Histórico de Atualizações do Mapa

| Data | Versão | Modificações Principais |
|---|---|---|
| **2026-09-27** | **v2.42.0** | Inclusão das pastas `docs/plans/` e `docs/implementation-plans/` para fechamento de gap da regra **R-064** (Duplo Gate Documental de Planejamento e Implementação). Atualização da árvore física e do Quick File Finder. |
| **2026-09-11** | **v2.6.0** | Consolidação arquitetural em `.github/`, extinção de catálogos redundantes e unificação do catálogo de agents em `.github/agents/catalog.yaml`. |
| **2026-09-10** | **v2.5.0** | Publicação inicial do Repo Map como infraestrutura canônica de navegação determinística para agentes de IA (Zero Blind Searches). |
