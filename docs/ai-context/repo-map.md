# Mapa do Repositório (Repo Map) — deep-agents-copilot

> **Fonte de verdade para navegação determinística de arquivos.**
> Este mapa documenta a localização exata de todos os componentes de governança, agents, skills, prompts, adapters e documentação deste repositório, eliminando buscas cegas e falhas de localização (`0 matches`).

---

## 1) Princípio de Localização Direta (Zero Blind Searches)

Agentes de IA devem sempre priorizar **caminhos canônicos diretos** (`read_file` com o caminho relativo exato) em vez de buscas exploratórias especulativas (`file_search` ou `grep_search`).

Quando for estritamente necessário buscar por padrão:
- Use glob com curinga inicial: `**/<nome-do-arquivo>` (essencial em workspaces multi-root).
- Os arquivos de busca `.ignore` e `.rgignore` na raiz liberam a indexação de `.github/` para ferramentas baseadas em ripgrep.

---

## 2) Desambiguação Crítica: Os Dois Catálogos (`catalog.yaml`)

| Arquivo | Localização Canônica | Propósito Exclusivo | O que contém |
|---|---|---|---|
| **Catálogo de Agents** | `.github/agents/catalog.yaml` | Metadados dos 37 agents do ecossistema | Modelos recomendados (Gemini, Claude), prioridades, domínios, related_skills, source_docs |
| **Catálogo de Binding / Adapters** | `docs/ai-context/catalog.yaml` | Manifest de carregamento hierárquico e stacks | Bindings globais, lista de adapters genéricos por stack, regras de descoberta |
| **Overlay Local de Projetos** | `docs/ai-context/catalog.local.yaml` | Projetos locais conectados (gitignored, R-043) | Configurações locais privadas de repositórios do desenvolvedor |

> ⚠️ **ATENÇÃO AGENTES**: Ao buscar o modelo de um agent (`[Model] Delegando para @<agent>`), leia EXCLUSIVAMENTE `.github/agents/catalog.yaml`. NUNCA procure agents em `docs/ai-context/catalog.yaml`.

---

## 3) Guia Rápido de Localização (Quick File Finder)

| Se você precisa de... | Caminho Canônico no Repositório |
|---|---|
| **Regras Globais de Governança** | `CLAUDE.md` |
| **Instruções Operacionais e Roteamento** | `.github/copilot-instructions.md` |
| **Catálogo Completo de Agents** | `.github/agents/catalog.yaml` |
| **Grafo Estruturado de Roteamento** | `.github/agents/routing-graph.yaml` |
| **Workflows Operacionais Canônicos** | `.github/agents/workflows.md` |
| **Suíte de Evals de Roteamento** | `.github/agents/evals/casos-roteamento.yaml` |
| **Manifest de Binding e Adapters** | `docs/ai-context/catalog.yaml` |
| **Guia de Binding Hierárquico** | `docs/ai-context/binding.md` |
| **Índice Estruturado de Skills** | `.github/skills/.index.json` |
| **Catálogo Textual de Skills** | `.github/skills/README.md` |
| **Índice Completo de Prompts** | `.github/prompts/README.md` |
| **Índice de Adapters de Código** | `.github/instructions/README.md` |

---

## 4) Estrutura Física de Diretórios

```
deep-agents-copilot/
├── CLAUDE.md                                    # Governança global (regras R-001..R-051)
├── README.md                                    # Visão geral do repositório
├── .ignore / .rgignore                          # Whitelist para ripgrep indexar .github/
│
├── .github/
│   ├── copilot-instructions.md                  # Instruções operacionais Copilot
│   │
│   ├── agents/                                  # 37 Agents de IA
│   │   ├── catalog.yaml                         # ⭐ Catálogo com modelos e metadados dos agents
│   │   ├── routing-graph.yaml                   # ⭐ Grafo estrutural de transições
│   │   ├── workflows.md                         # ⭐ Especificação dos 5 Workflows Canônicos
│   │   ├── agent-router.agent.md                # Entry point obrigatório (R-037/R-042)
│   │   ├── prompt-structuring.agent.md          # Refinamento de prompt (R-041)
│   │   ├── bug-triage.agent.md                  # Triagem de bugs
│   │   ├── pr-gatekeeper.agent.md               # Preparação de PR e commit
│   │   ├── ... (outros agents raiz)
│   │   │
│   │   ├── evals/                               # Suíte de regressão de roteamento
│   │   │   ├── casos-roteamento.yaml            # Casos canônicos, ambíguos e regressões
│   │   │   └── casos-code-summarizer.yaml
│   │   │
│   │   ├── frontend/angular/                    # Domínio Frontend Angular
│   │   │   ├── angular-catalog.yaml             # Sub-catálogo dos 8 especialistas Angular
│   │   │   ├── angular-router.agent.md          # Supervisor hierárquico Angular
│   │   │   └── angular-*.agent.md               # Especialistas (feature, bug, test, style...)
│   │   │
│   │   └── backend/                             # Domínios Backend
│   │       ├── spring-boot/                     # Sub-catálogo e especialistas Spring Boot
│   │       ├── spring-reactive/                 # Sub-catálogo e especialistas Spring Reactive
│   │       ├── ejb/                             # Sub-catálogo e especialistas Java Legado EJB
│   │       └── database/                        # Sub-catálogo e especialistas Oracle/Informix
│   │
│   ├── skills/                                  # 50+ Skills Especializadas
│   │   ├── .index.json                          # Índice estruturado JSON de skills
│   │   ├── README.md                            # Catálogo descritivo de skills
│   │   ├── agent-contracts/SKILL.md             # Padrões contratuais de agents
│   │   ├── handoff-governance/SKILL.md          # Protocolos de delegação
│   │   ├── terminal-governance/SKILL.md         # Governança de execução em terminal
│   │   ├── context-mode/SKILL.md                # Práticas de Context Mode
│   │   └── ... (demais skills)
│   │
│   ├── prompts/                                 # Prompts Canônicos de Workflow
│   │   ├── README.md                            # Índice de prompts
│   │   ├── commit.prompt.md                     # SSOT de commit semântico
│   │   ├── plan.prompt.md                       # Planejamento
│   │   └── ... (demais prompts)
│   │
│   └── instructions/                            # Adapters de Stack de Código
│       ├── README.md                            # Índice de adapters
│       ├── angular-v21-frontend.instructions.md # Convenções Angular
│       ├── spring-boot-backend.instructions.md  # Convenções Spring Boot
│       ├── python-backend.instructions.md       # Convenções Python
│       ├── database.instructions.md             # Convenções Banco de Dados
│       ├── devops.instructions.md               # Convenções DevOps
│       └── local/                               # Adapters de projetos locais (gitignored, R-043)
│
├── docs/
│   ├── ai-context/                              # Contexto de Binding de IA
│   │   ├── catalog.yaml                         # ⭐ Catálogo de Binding (Adapters e Stacks)
│   │   ├── binding.md                           # Guia de binding hierárquico
│   │   ├── repo-map.md                          # ⭐ Este Mapa do Repositório
│   │   ├── catalog.local.yaml.example           # Template de overlay de projetos
│   │   └── catalog.local.yaml                   # Projetos locais (gitignored, R-043)
│   ├── agent-context/                           # Guias de uso de ferramentas
│   ├── plan/                                    # Planos arquiteturais
│   └── requirements/                            # Requisitos de sistema
│
└── tests/                                       # Suíte de Testes Automatizados (pytest)
    ├── governance_audit/                        # Auditoria de regras e smells (R-001..R-051)
    ├── routing_gate/                            # Quality gate de roteamento
    ├── operational_flow/                        # Testes de workflows operacionais
    └── code-summarizer/                         # Testes do summarizer
```

