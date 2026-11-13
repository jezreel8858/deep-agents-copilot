---
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-12"
date: "2026-11-12"
related-planning-doc: "N/A — plano raiz (WORKFLOW-GOVERNANCE-MAINTENANCE)"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
allowed_files:
  - "docs/plans/**"
  - "docs/plans/implementation/**"
  - "docs/plans/requirements/**"
  - "docs/plans/test-strategy/**"
  - "docs/README.md"
  - "CLAUDE.md"
  - "AGENTS.md"
  - ".github/copilot-instructions.md"
  - ".github/agents/**"
  - ".github/skills/**"
  - ".github/prompts/**"
  - "tools/**"
  - "tests/**"
---
# Plano de Governança: Padronização e Materialização Universal de Planos em `docs/plans/<tipo>/` (R-064)

> **Nota de Ciclo de Vida**: Na Etapa 3 do `WORKFLOW-GOVERNANCE-MAINTENANCE` (após aprovação humana R-064), este próprio arquivo será movido de `docs/plans/governance/20261112-090200-governance-maintenance-universal-plan-materialization.md` para `docs/plans/governance/20261112-090200-governance-maintenance-universal-plan-materialization.md` junto com os demais planos de governança.

---

## 1. Contexto e Objetivo

### 1.1 Problema Diagnosticado
Atualmente, a persistência de artefatos de planejamento no repositório encontra-se fragmentada em 5 diretórios distintos (`docs/plans/`, `docs/plans/implementation/`, `docs/plans/`, `docs/plans/requirements/` e `docs/plans/test-strategy/`), com convenções heterogêneas de nomenclatura, ausência de subdiretórios tipados por domínio de planejamento (`plan_type`) e templates diluídos ou ausentes nas skills especializadas de planejamento.

Adicionalmente, os agentes planejadores, consultores arquiteturais (`*-arch-advisor`), analistas de requisitos e agentes de triagem operam sob perfil estritamente **100% Read-Only** (R-025), mas careciam de um contrato unificado de delegação de persistência física via `@docs-engineer` (ou `@governance-maintainer` em fluxos de governança) que garantisse que **todo** planejamento gerado em qualquer workflow canônico (R-050) seja materializado em disco antes do checkpoint de aprovação humana (R-064).

### 1.2 Objetivo
1. Consolidar todos os artefatos de planejamento sob uma árvore canônica única em `docs/plans/<tipo>/`, extinguindo os diretórios paralelos legados (`docs/plans/implementation/`, `docs/plans/`, `docs/plans/requirements/`, `docs/plans/test-strategy/`).
2. Instituir o campo obrigatório `plan_type` no frontmatter YAML R-064 comum a todas as 8 categorias de plano (`feature`, `refactor`, `architecture`, `implementation`, `test-strategy`, `bug-triage`, `requirements`, `governance`).
3. Embutir templates especializados de plano nas respectivas skills de domínio sem ultrapassar o teto rígido de 500 linhas por `SKILL.md`.
4. Formalizar o contrato de delegação de materialização física (planejadores 100% Read-Only diagnosticam/estruturam o plano → `@docs-engineer` / `@governance-maintainer` persistem o arquivo `.md` em `docs/plans/<tipo>/` → `ask_questions` coleta aprovação humana R-064).

### 1.3 Opções Consideradas e Decisão Técnica Adotada
- **Opção A (Adotada)**: Consolidar toda a persistência em `docs/plans/<tipo>/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md`, mantendo frontmatter YAML R-064 unificado com discriminador `plan_type` e templates especializados nas skills de cada domínio.
- **Opção B (Rejeitada)**: Manter diretórios separados na raiz de `docs/` (`docs/plans/`, `docs/plans/implementation/`, `docs/plans/requirements/`, `docs/plans/test-strategy/`, `docs/plans/`).
- **Opção C (Rejeitada)**: Conceder permissão de escrita em disco (`ctx_execute` / `edit`) diretamente aos 14 agentes planejadores/advisors/triagem.

### 1.4 Alternativas Rejeitadas
- **Descarte da Opção B**: A pulverização em 5 pastas raiz sob `docs/` gera deriva documental, dificulta a validação determinística de Gate 1 / Gate 2 (R-064) em scripts de auditoria e cria ambiguidade sobre onde persistir planos de refatoração, arquitetura ou triagem de bugs.
- **Descarte da Opção C**: Viola o Princípio da Segregação de Funções (R-025 / Smell 2.13). Agentes analíticos, planejadores e `*-arch-advisor` devem permanecer 100% Read-Only para impedir mutações acidentais de código ou bypass do Gate R-064 durante a fase de descoberta e desenho.

---

## 2. Escopo e Critérios de Aceitação (CA-01 a CA-06)

### 2.1 Escopo Delimitado
- Reestruturação física de `docs/plans/` em 8 subpastas tipadas e migração integral dos arquivos de `docs/plans/` (raiz), `docs/plans/implementation/`, `docs/plans/`, `docs/plans/requirements/` e `docs/plans/test-strategy/`.
- Atualização de `docs/plans/README.md` e `docs/README.md` refletindo a taxonomia `docs/plans/<tipo>/`.
- Padronização dos templates de plano nas skills de planejamento e arquitetura.
- Atualização das referências de caminho de planos em `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, `tools/**` e `tests/**`.

### 2.2 Não-Escopo Explícito
- Alteração de lógica funcional de negócio ou runtime de aplicação fora de `tools/` e `tests/` (scripts de validação de governança).
- Concessão de ferramentas de escrita para agentes consultivos/planejadores (permanecem 100% Read-Only).
- Remoção de documentos de arquitetura perenes em `docs/architecture/` ou ADRs em `docs/adr/` (que pertencem à categoria Referência/Decisão Arquitetural, não a Planos de Execução R-064).

### 2.3 Critérios de Aceitação (CA-01 a CA-06)

| ID | Critério de Aceitação | Verificação Objetiva |
| :--- | :--- | :--- |
| **CA-01** | **Taxonomia Canônica `docs/plans/<tipo>/` criada e populada**: As 8 subpastas (`feature`, `refactor`, `architecture`, `implementation`, `test-strategy`, `bug-triage`, `requirements`, `governance`) existem em `docs/plans/` e contêm os respectivos planos migrados. | Inspeção de diretório e `docs/plans/README.md` atualizado. |
| **CA-02** | **Extinção de Diretórios Paralelos Legados**: Os diretórios `docs/plans/implementation/`, `docs/plans/`, `docs/plans/requirements/` e `docs/plans/test-strategy/` são removidos após migração de 100% dos seus artefatos para `docs/plans/<tipo>/`, restando na raiz de `docs/plans/` apenas `README.md` e as 8 subpastas. | Verificação de inexistência dos diretórios legados e zero arquivos órfãos na raiz de `docs/plans/`. |
| **CA-03** | **Frontmatter Comum R-064 com `plan_type`**: O contrato de frontmatter YAML R-064 exige `status`, `approved`, `author`, `plan_type`, `created_at`, `related-planning-doc`, `workflow` e `allowed_files` em todos os templates e novos planos. | Validação de schema YAML nos templates e no plano de governança. |
| **CA-04** | **Skills com Templates Especializados e Teto ≤ 500 Linhas**: Cada skill de planejamento/arquitetura mapeada possui o template especializado correspondente ao seu `plan_type` e respeita o limite máximo de 500 linhas por `SKILL.md`. | Contagem de linhas de todos os `.github/skills/**/SKILL.md` ≤ 500. |
| **CA-05** | **14 Agentes Planejadores/Advisors/Triagem 100% Read-Only com Delegação Explícita**: Nenhum dos 14 agentes planejadores/advisors/triagem possui tools de escrita, e todos documentam a materialização física via delegação para `@docs-engineer` (ou `@governance-maintainer`) em `docs/plans/<tipo>/`. | Auditoria de frontmatter `tools:` e corpo dos `.agent.md`. |
| **CA-06** | **Integridade de Referências e Suíte de Testes Verde**: Todas as referências a `docs/plans/implementation/`, `docs/plans/`, `docs/plans/requirements/` e `docs/plans/test-strategy/` em prompts, skills, agents, instruções globais, `tools/` e `tests/` são atualizadas para `docs/plans/<tipo>/`, com `sync-check` e `pytest` passando integralmente. | Execução de `pytest` e scripts de validação sem falhas. |

---

## 3. Taxonomia Alvo (`docs/plans/<tipo>/`) e Tabela de Migração de Legado

### 3.1 Taxonomia Alvo das 8 Subpastas de `docs/plans/`

| Subpasta (`docs/plans/<tipo>/`) | `plan_type` | Propósito Canônico | Workflows Principais (R-050) |
| :--- | :--- | :--- | :--- |
| `docs/plans/feature/` | `feature` | Planos funcionais de feature, fatiamento de épicos/histórias e escopo de entrega. | `WORKFLOW-FEATURE-DEVELOPMENT` |
| `docs/plans/refactor/` | `refactor` | Planos de refatoração estrutural em ondas, extração de módulos e redução de dívida técnica. | `WORKFLOW-CODE-REFACTORING` |
| `docs/plans/architecture/` | `architecture` | Blueprints de solução multi-stack, migração de frameworks e topologia arquitetural. | `WORKFLOW-FRAMEWORK-MIGRATION`, `WORKFLOW-TECHNICAL-ANALYSIS` |
| `docs/plans/implementation/` | `implementation` | Planos técnicos de implementação por stack (Gate 2 R-064) com allowlist de arquivos e passos TDD. | Todos os workflows com mutação de código (Etapa de Plano de Implementação) |
| `docs/plans/test-strategy/` | `test-strategy` | Planos de estratégia de testes, pirâmide de cobertura, contratos de integração e E2E. | `WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-BUG-FIX` (testes) |
| `docs/plans/bug-triage/` | `bug-triage` | Planos de RCA (Root Cause Analysis), reprodução determinística, blast radius e hipótese de fix. | `WORKFLOW-BUG-FIX`, `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION` |
| `docs/plans/requirements/` | `requirements` | Documentos de elicitação de requisitos, critérios Given/When/Then e matriz de rastreabilidade. | `WORKFLOW-FEATURE-DEVELOPMENT` (Etapa 1) |
| `docs/plans/governance/` | `governance` | Planos de manutenção de governança, auditoria de catálogo, evolução de skills/agents/prompts. | `WORKFLOW-GOVERNANCE-MAINTENANCE` |

### 3.2 Tabela de Migração de Legado

| Origem Legada | Destino Canônico em `docs/plans/<tipo>/` | `plan_type` | Regra de Resolução de Colisão |
| :--- | :--- | :--- | :--- |
| `docs/plans/governance/20260927-090000-governance-maintenance-session-checkpoint-recovery.md` | `docs/plans/governance/20260927-090000-governance-maintenance-session-checkpoint-recovery.md` | `governance` | Mover direto para `governance/`. |
| `docs/plans/governance/20260927-090100-workflow-governance-maintenance-prompt-synthesis-redesign.md` | `docs/plans/governance/20260927-090100-workflow-governance-maintenance-prompt-synthesis-redesign.md` | `governance` | Mover direto para `governance/`. |
| `docs/plans/governance/20260929-090000-governance-maintenance-harness-bloat-audit.md` | `docs/plans/governance/20260929-090000-governance-maintenance-harness-bloat-audit.md` | `governance` | Mover direto para `governance/`. |
| `docs/plans/feature/20261001-090000-feature-development-governance-runner-sdk-integration.md` | `docs/plans/feature/20261001-090000-feature-development-governance-runner-sdk-integration.md` | `feature` | Plano macro vai para `feature/`; par homônimo de `docs/plans/implementation/` vai para `implementation/`. |
| `docs/plans/bug-triage/20261002-090000-bugfix-mcp-tools-headless-sdk.md` | `docs/plans/bug-triage/20261002-090000-bugfix-mcp-tools-headless-sdk.md` | `bug-triage` | Plano de RCA vai para `bug-triage/`; par homônimo de `docs/plans/implementation/` vai para `implementation/`. |
| `docs/plans/bug-triage/20261003-090000-bugfix-anti-truncamento-changelog-hook-falso-positivo.md` | `docs/plans/bug-triage/20261003-090000-bugfix-anti-truncamento-changelog-hook-falso-positivo.md` | `bug-triage` | Mover direto para `bug-triage/`. |
| `docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md` | `docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md` | `governance` | Plano de governança vai para `governance/`; par de implementação vai para `implementation/`. |
| `docs/plans/governance/20261003-090100-governance-maintenance-progressive-disclosure-source-docs.md` | `docs/plans/governance/20261003-090100-governance-maintenance-progressive-disclosure-source-docs.md` | `governance` | Plano de governança vai para `governance/`; par de implementação vai para `implementation/`. |
| `docs/plans/bug-triage/20261004-090000-bugfix-shell-permission-persistente-logging-arquivo.md` | `docs/plans/bug-triage/20261004-090000-bugfix-shell-permission-persistente-logging-arquivo.md` | `bug-triage` | Plano de RCA vai para `bug-triage/`; par de implementação vai para `implementation/`. |
| `docs/plans/governance/20261005-090000-gov-import-harness-eval.md` | `docs/plans/governance/20261005-090000-gov-import-harness-eval.md` | `governance` | Plano de governança vai para `governance/`; par de implementação vai para `implementation/`. |
| `docs/plans/governance/20261005-090100-gov-retrofit-harness-eval-and-skill-creation-flow.md` | `docs/plans/governance/20261005-090100-gov-retrofit-harness-eval-and-skill-creation-flow.md` | `governance` | Plano de governança vai para `governance/`; par de implementação vai para `implementation/`. |
| `docs/plans/governance/20261006-090000-governance-maintenance-consolidacao-agents-stacks.md` | `docs/plans/governance/20261006-090000-governance-maintenance-consolidacao-agents-stacks.md` | `governance` | Mover direto para `governance/`. |
| `docs/plans/governance/20261112-090200-governance-maintenance-universal-plan-materialization.md` | `docs/plans/governance/20261112-090200-governance-maintenance-universal-plan-materialization.md` | `governance` | Movido na Etapa 3 após aprovação R-064. |
| `docs/plans/implementation/*.md` (exceto `README.md`, 17 planos técnicos) | `docs/plans/implementation/<mesmo-nome>.md` | `implementation` | Todos os planos técnicos de `docs/plans/implementation/` migram para `docs/plans/implementation/`; `docs/plans/implementation/README.md` é consolidado em `docs/plans/README.md`. |
| `docs/plans/architecture/20260830-090000-agent-profiles-taxonomy.md` | `docs/plans/governance/20260830-090000-agent-profiles-taxonomy.md` | `governance` | Estudo/plano de taxonomia de perfis de agentes migra para `governance/`. |
| `docs/plans/architecture/20260902-090000-analise-arquitetura-multi-agent-alinhamento.md` | `docs/plans/architecture/20260902-090000-analise-arquitetura-multi-agent-alinhamento.md` | `architecture` | Análise/blueprint de alinhamento arquitetural migra para `architecture/`. |
| `docs/plans/architecture/20260830-090100-categorizacao-agents-mercado.md` | `docs/plans/governance/20260830-090100-categorizacao-agents-mercado.md` | `governance` | Plano de categorização do catálogo de agentes migra para `governance/`. |
| `docs/plans/architecture/20260830-090200-plano-grafico-invocacao-agents.md` | `docs/plans/architecture/20260830-090200-plano-grafico-invocacao-agents.md` | `architecture` | Plano arquitetural do grafo de invocação migra para `architecture/`. |
| `docs/plans/implementation/20260830-090000-architecture-plano-implementacao-orquestracao.md` | `docs/plans/implementation/20260830-090000-architecture-plano-implementacao-orquestracao.md` | `implementation` | Plano de implementação de orquestração migra para `implementation/`. |
| `docs/plans/architecture/20260830-090300-plano-motor-migracao-agnostica.md` | `docs/plans/architecture/20260830-090300-plano-motor-migracao-agnostica.md` | `architecture` | Blueprint do motor de migração agnóstica migra para `architecture/`. |
| `docs/plans/governance/20260830-090000-plano-otimizacao-catalogo-agents.md` | `docs/plans/governance/20260830-090000-plano-otimizacao-catalogo-agents.md` | `governance` | Plano de otimização de governança de agentes migra para `governance/`. |
| `docs/plans/architecture/20260830-090400-proposta-orquestracao-langchain.md` | `docs/plans/architecture/20260830-090400-proposta-orquestracao-langchain.md` | `architecture` | Proposta arquitetural de orquestração migra para `architecture/`. |
| `docs/plans/requirements/20260830-090000-migration-engine.md` | `docs/plans/requirements/20260830-090000-migration-engine.md` | `requirements` | Documento de requisitos migra para `docs/plans/requirements/`. |
| `docs/plans/test-strategy/` (diretório vazio) | `docs/plans/test-strategy/` | `test-strategy` | Diretório vazio legado removido e substituído por `docs/plans/test-strategy/`. |

---

## 4. Mapeamento Skill → Template Especializado (`plan_type`) e Frontmatter Comum R-064

### 4.1 Frontmatter Comum R-064 (Obrigatório para todos os `plan_type`)

```yaml
---
status: DRAFT | APPROVED | IN_PROGRESS | COMPLETED | REJECTED
approved: false | true
author: "@<agent-autor-canonico>"
plan_type: "feature" | "refactor" | "architecture" | "implementation" | "test-strategy" | "bug-triage" | "requirements" | "governance"
created_at: "AAAA-MM-DD"
related-planning-doc: "docs/plans/<tipo>/<arquivo>.md | N/A — plano raiz (<WORKFLOW>)"
workflow: "<WORKFLOW-CANONICO-R050>"
allowed_files:
  - "<glob-ou-caminho-explicito>"
---
```

### 4.2 Mapeamento de Skills para Templates Especializados

| `plan_type` | Pasta Canônica | Skill Dono do Template Especializado | Seções Específicas do Template Especializado |
| :--- | :--- | :--- | :--- |
| `requirements` | `docs/plans/requirements/` | `.github/skills/requirements-engineering/SKILL.md` | Atores/Personas, Requisitos Funcionais (RF), Requisitos Não-Funcionais (RNF), Critérios Given/When/Then, Matriz de Rastreabilidade e Ambiguidades Resolvidas. |
| `feature` | `docs/plans/feature/` | `.github/skills/agile-Work-Item-Planning/SKILL.md` | Épico/Objetivo de Negócio, Fatiamento Vertical de Histórias/Cards, Dependências Funcionais, Critérios de Aceitação de Produto e Escopo/Não-Escopo. |
| `refactor` | `docs/plans/refactor/` | `.github/skills/refactoring-patterns/SKILL.md` | Code Smells Diagnosticados, Análise de Blast Radius, Plano em Ondas Atômicas (Strangler/Mikado), Invariantes de Comportamento e Rollback por Onda. |
| `architecture` | `docs/plans/architecture/` | `.github/skills/architecture-patterns/SKILL.md` | Contexto de Sistema, Opções Arquiteturais Avaliadas, Alternativas Rejeitadas, Contratos de Integração/Fronteiras, Requisitos Não-Funcionais e Modelagem de Ameaças (Shift-Left). |
| `implementation` | `docs/plans/implementation/` | `.github/skills/documentation-writing-patterns/SKILL.md` (e referência nas skills de stack) | Vínculo com Gate 1 (`related-planning-doc`), Allowlist Estrita (`allowed_files`), Mudanças por Camada/Arquivo, Estratégia TDD, Comandos de Verificação e Checklist de Qualidade. |
| `test-strategy` | `docs/plans/test-strategy/` | `.github/skills/test-strategy-and-piramide/SKILL.md` | Pirâmide de Testes Alvo (Unit/Integration/Contract/E2E), Matriz de Cenários Críticos, Dados/Fixtures de Teste, Isolamento de Dependências e Critérios de Cobertura. |
| `bug-triage` | `docs/plans/bug-triage/` | `.github/skills/debugging-strategies/SKILL.md` | Sintoma e Evidência de Falha, Passos de Reprodução Determinística, Análise de Causa Raiz (RCA / 5 Porquês), Escopo de Impacto (Blast Radius) e Hipótese de Correção Mínima. |
| `governance` | `docs/plans/governance/` | `.github/skills/agent-governance-standards/SKILL.md` | Diagnóstico de Governança/Conformidade, Regras Impactadas (R-XXX), Catálogo de Artefatos Afetados, Plano de Execução em Lotes (R-059) e Critérios de Validação (`sync-check`/testes). |

---

## 5. Mapeamento dos 14 Agents Planejadores/Advisors/Triagem (100% Read-Only) e Delegação de Persistência Física

Todos os 14 agentes abaixo operam em modo **100% Read-Only** (sem ferramentas de edição de arquivos ou execução destrutiva). Eles elaboram o conteúdo estruturado do plano seguindo o template da respectiva skill e delegam a persistência física do arquivo `.md` em `docs/plans/<tipo>/` ao `@docs-engineer` (ou `@governance-maintainer` em fluxos de governança) via orquestração do `@agent-router` / subagente dedicado.

| # | Agent (100% Read-Only) | Papel Canônico | `plan_type` Primário (e Secundário) | Destino de Materialização Física | Agente Executor da Persistência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `@requirements-analyst` | Elicitação e engenharia de requisitos | `requirements` | `docs/plans/requirements/` | `@docs-engineer` |
| 2 | `@feature-planner` | Planejamento funcional de features e épicos | `feature` | `docs/plans/feature/` | `@docs-engineer` |
| 3 | `@refactor-planner` | Planejamento de refatoração em ondas e blast radius | `refactor` | `docs/plans/refactor/` | `@docs-engineer` |
| 4 | `@tech-solution-architect` | Arquitetura de solução agnóstica e migração | `architecture` | `docs/plans/architecture/` | `@docs-engineer` |
| 5 | `@bug-triage` | Triagem de defeitos e Root Cause Analysis (RCA) | `bug-triage` | `docs/plans/bug-triage/` | `@docs-engineer` |
| 6 | `@agent-auditor` | Auditoria de governança, catálogo e conformidade | `governance` | `docs/plans/governance/` | `@docs-engineer` / `@governance-maintainer` |
| 7 | `@repo-hygiene-auditor` | Auditoria de higiene estrutural do repositório | `governance` | `docs/plans/governance/` | `@docs-engineer` / `@governance-maintainer` |
| 8 | `@python-arch-advisor` | Consultor arquitetural e plano técnico Python | `implementation` (`test-strategy`) | `docs/plans/implementation/` (`docs/plans/test-strategy/`) | `@docs-engineer` |
| 9 | `@spring-boot-arch-advisor` | Consultor arquitetural e plano técnico Spring Boot | `implementation` (`test-strategy`) | `docs/plans/implementation/` (`docs/plans/test-strategy/`) | `@docs-engineer` |
| 10 | `@spring-reactive-arch-advisor` | Consultor arquitetural e plano técnico WebFlux | `implementation` (`test-strategy`) | `docs/plans/implementation/` (`docs/plans/test-strategy/`) | `@docs-engineer` |
| 11 | `@ejb-arch-advisor` | Consultor arquitetural e plano técnico Jakarta/EJB | `implementation` (`test-strategy`) | `docs/plans/implementation/` (`docs/plans/test-strategy/`) | `@docs-engineer` |
| 12 | `@struts-arch-advisor` | Consultor arquitetural e plano técnico Struts legado | `implementation` (`test-strategy`) | `docs/plans/implementation/` (`docs/plans/test-strategy/`) | `@docs-engineer` |
| 13 | `@react-arch-advisor` | Consultor arquitetural e plano técnico React | `implementation` (`test-strategy`) | `docs/plans/implementation/` (`docs/plans/test-strategy/`) | `@docs-engineer` |
| 14 | `@angular-arch-advisor` | Consultor arquitetural e plano técnico Angular | `implementation` (`test-strategy`) | `docs/plans/implementation/` (`docs/plans/test-strategy/`) | `@docs-engineer` |

> **Nota complementar de cobertura**: Consultores de domínio especializado como `@database-arch-advisor` seguem rigorosamente a mesma invariante Read-Only, emitindo planos técnicos em `docs/plans/implementation/` materializados via `@docs-engineer`.

---

## 6. Plano de Execução em Fases (Lote R-046/R-059)

A execução na Etapa 3 (após aprovação humana R-064 na Etapa 2) será conduzida por `@governance-maintainer` em lotes atômicos via `ctx_execute` / `ctx_batch_execute`:

### Fase 1 — Criação da Taxonomia `docs/plans/<tipo>/` e Migração Física de Arquivos (Lote 1)
1. Criar os 8 subdiretórios canônicos em `docs/plans/`: `feature`, `refactor`, `architecture`, `implementation`, `test-strategy`, `bug-triage`, `requirements`, `governance`.
2. Mover todos os arquivos de `docs/plans/*.md` (exceto `README.md`), `docs/plans/implementation/*.md`, `docs/plans/*.md` e `docs/plans/requirements/*.md` para suas respectivas subpastas conforme a Tabela de Migração (Seção 3.2), incluindo a promoção deste próprio plano para `docs/plans/governance/20261112-090200-governance-maintenance-universal-plan-materialization.md` com `status: APPROVED` e `approved: true`.
3. Injetar/normalizar o campo `plan_type` no frontmatter dos planos migrados quando aplicável e remover os diretórios legados esvaziados (`docs/plans/implementation/`, `docs/plans/`, `docs/plans/requirements/`, `docs/plans/test-strategy/`).

### Fase 2 — Atualização de Documentação de Governança e Templates em Skills (Lote 2)
1. Atualizar `docs/plans/README.md` e `docs/README.md` com a nova taxonomia `docs/plans/<tipo>/`, regras de nomenclatura, frontmatter comum R-064 e tabela de delegação Read-Only → `@docs-engineer`.
2. Atualizar as skills mapeadas na Seção 4.2 com as seções de template especializado para cada `plan_type`, garantindo que nenhuma skill ultrapasse 500 linhas (aplicando compactação semântica se necessário).

### Fase 3 — Atualização em Lote de Agents, Prompts, Instruções Globais e Ferramentas (Lote 3)
1. Atualizar os 14 agentes planejadores/advisors/triagem (e `@database-arch-advisor`, `@agent-router`, `@docs-engineer`, `@governance-maintainer`) para referenciar `docs/plans/<tipo>/` e explicitar o fluxo de materialização delegada.
2. Atualizar referências de `docs/plans/implementation/`, `docs/plans/`, `docs/plans/requirements/` e `docs/plans/test-strategy/` em `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `.github/prompts/**`, `tools/**` e `tests/**`.

### Fase 4 — Validação de Qualidade e Testes Automatizados (Etapa 4)
1. Executar validação de links/referências, contagem de linhas de `SKILL.md` (≤ 500), auditoria de frontmatter dos agents e execução da suíte `pytest`.

---

## 7. Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)

- **Vetores de Risco & Superfície de Ataque (STRIDE / CWE)**:
  - *Tampering / Privilege Escalation (CWE-284)*: Risco de agentes consultivos Read-Only receberem permissões de escrita indevidas ou executores alterarem arquivos fora do escopo aprovado no plano.
  - *Path Traversal / Referências Quebradas (CWE-22)*: Risco de scripts em `tools/` ou testes aceitarem caminhos fora de `docs/plans/<tipo>/` ou falharem silenciosamente após a remoção de `docs/plans/implementation/`.
- **Requisitos de Segurança Mandatórios**:
  - Preservação estrita da invariante **100% Read-Only** nos 14 agentes planejadores/advisors/triagem (verificação automatizada de ausência de tools de escrita e ausência de `terminal-governance` em `source_docs`).
  - Obrigatoriedade de `allowed_files` e `approved: true` no frontmatter R-064 antes de qualquer mutação de código ou governança na Etapa 3.
- **Validações de Borda**:
  - Validação determinística de que todos os `SKILL.md` permanecem com ≤ 500 linhas após a inclusão dos templates especializados.
  - Verificação de zero arquivos residuais nos diretórios legados antes de sua remoção.

---

## 8. Riscos, Mitigações e Estratégia de Rollback

| Risco | Impacto | Probabilidade | Mitigação |
| :--- | :--- | :--- | :--- |
| Colisão de nomes entre planos de `docs/plans/` e `docs/plans/implementation/` (ex.: pares Gate 1 e Gate 2 com mesmo nome de arquivo) | Médio | Alta (confirmada em 6 pares) | Isolamento natural por subpasta: os planos macro permanecem em `docs/plans/governance/`, `docs/plans/feature/` ou `docs/plans/bug-triage/`, enquanto todos os planos de `docs/plans/implementation/` migram exclusivamente para `docs/plans/implementation/`. |
| Quebra de asserções em testes automatizados (`tests/`) que validam caminhos hardcoded como `docs/plans/implementation/` ou `docs/plans/` | Alto | Média | Mapeamento prévio e atualização sincronizada das referências em `tools/` e `tests/` no Lote 3 antes do gate final de testes. |
| Estouro do limite de 500 linhas em `SKILL.md` ao adicionar templates especializados | Médio | Baixa | Verificação prévia de contagem de linhas e uso de templates enxutos orientados a schema YAML + seções canônicas. |

### Estratégia de Rollback
- Caso qualquer validação crítica de integridade (`pytest` ou auditoria de referências) falhe na Etapa 4 e não possa ser corrigida dentro do orçamento do loop de qualidade (R-050.4), reverter atomicamente as movimentações e edições via `git checkout -- docs/ CLAUDE.md AGENTS.md .github/ tools/ tests/` e restaurar o estado anterior da árvore de trabalho.
