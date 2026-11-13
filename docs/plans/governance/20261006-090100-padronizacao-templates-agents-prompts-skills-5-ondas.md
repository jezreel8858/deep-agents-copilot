---
status: "COMPLETED"
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-10-06"
related-planning-doc: "docs/plans/implementation/20261006-090200-governance-padronizacao-templates-agents-prompts-skills-5-ondas.md"
allowed_files:
  - ".github/agents/**"
  - ".github/prompts/**"
  - ".github/skills/**"
  - ".a2a/agentcards/**"
  - "tools/agent_protocol_sync/**"
  - "tests/governance_audit/**"
  - "docs/plans/**"
  - "CHANGELOG.md"
  - "README.md"
  - "CLAUDE.md"
  - "AGENTS.md"
---

# Plano de Padronização Estrutural de Templates, Agents, Prompts e Skills (5 Ondas)

> **Regra R-064 (Plan Materialization & Conformance)**: Plano materializado fisicamente nos diretórios canônicos `docs/plans/governance/` e `docs/plans/implementation/` (sem uso do diretório legado `docs/implementation-plans/`, vedado por `test_universal_plan_materialization_governance.py`).

---

## 1. Resumo Executivo e Escopo

Este plano estrutura a padronização transversal dos templates oficiais e de todos os artefatos de governança do repositório (**6 templates**, **22 prompts**, **81 skills** e **62 agents**) em **5 Ondas sequenciais (`CA-01` a `CA-06`)**, garantindo:
- Alinhamento estrito aos contratos de governança (**R-008**, **R-015**, **R-025**, **R-028**, **R-040**, **R-042**, **R-051**, **R-054**, **R-055**, **R-056**, **R-059**, **R-060**, **R-064**, **R-066**).
- Adequação estrutural por arquetipo em templates, prompts (6 seções canônicas), skills (`description` em 3ª pessoa com `Use quando... Não use para...`, seções obrigatórias e teto R-066 ≤ 300 linhas) e agents (perfis `Router`, `Analítico/Read-Only/Advisor`, `Executor/Developer/Test-Engineer`).
- Sincronização atômica de catálogos, índices, `@governance-factory.agent.md` e sensores determinísticos em `tests/governance_audit/`.

---

## 2. Checklist Mestre de Execução — As 5 Ondas Canônicas

### [x] Onda 1 (`CA-01`): Atualização dos Templates Oficiais e Meta-Skills de Fábrica e Auditoria *(Concluída)*

- [x] **1.1** Atualizar templates oficiais de Agents (`.github/agents/templates/*.md`):
  - [x] `.github/agents/templates/agent-template.md` (211 linhas)
  - [x] `.github/agents/templates/operational-agent.md` (246 linhas)
  - [x] `.github/agents/templates/research-agent.md` (251 linhas)
  - [x] `.github/agents/templates/router-agent.md` (172 linhas)
- [x] **1.2** Atualizar template oficial de Prompt:
  - [x] `.github/prompts/templates/prompt-template.md` (141 linhas — definindo as 6 seções canônicas: `## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO`, `## 🎯 Objetivo e Invocação`, `## 📋 Fluxo de Execução Passo a Passo`, `## 📊 Formato de Saída Esperado`, `## ✅ Checklist Antes de Apresentar` e `## ⚙️ Protocolo de Execução Obrigatório`)
- [x] **1.3** Atualizar template oficial de Skill:
  - [x] `.github/skills/templates/skill-template.md` (129 linhas — definindo `description` em 3ª pessoa com `Use quando... Não use para...`, seções obrigatórias e Progressive Disclosure R-066 ≤ 300 linhas)
- [x] **1.4** Atualizar Meta-Skills de Governança com extração R-066 para `references/`:
  - [x] `.github/skills/governance-factory-patterns/SKILL.md` (132 linhas) + `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md` (390 linhas)
  - [x] `.github/skills/governance-audit-patterns/SKILL.md` (172 linhas) + `.github/skills/governance-audit-patterns/references/smells-catalog-detailed.md` (503 linhas)

---

### [x] Onda 2 (`CA-03`): Adequação em Lote dos 22 Prompts (`.github/prompts/*.prompt.md`) *(Concluída)*

> **Diagnóstico em disco**: Os 22 arquivos `.prompt.md` possuem hoje cabeçalhos heterogêneos herdados de ciclos anteriores (ex.: `del-project-context.prompt.md` e `health.prompt.md` sem `## ⚙️ Protocolo de Execução Obrigatório`; `ctx-*.prompt.md`, `commit.prompt.md`, `implement.prompt.md`, `plan.prompt.md` e `validate.prompt.md` com seções fora das 6 seções canônicas definidas em `prompt-template.md`). Todos os 22 prompts foram adequados em lote na Onda 2 (`[x]`).

- [x] **2.0** Adequar os **22 Prompts** em `.github/prompts/*.prompt.md` às **6 seções canônicas** do `prompt-template.md` (`## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO`, `## 🎯 Objetivo e Invocação`, `## 📋 Fluxo de Execução Passo a Passo`, `## 📊 Formato de Saída Esperado`, `## ✅ Checklist Antes de Apresentar`, `## ⚙️ Protocolo de Execução Obrigatório` + `<execution_protocol>`), preservando as regras específicas de domínio e invariantes testadas (ex.: R-046/R-051/R-064 em `plan.prompt.md` e `implement.prompt.md`):
    - [x] **2.1** `.github/prompts/add-project-context.prompt.md`
    - [x] **2.2** `.github/prompts/agent-router.prompt.md`
    - [x] **2.3** `.github/prompts/commit.prompt.md`
    - [x] **2.4** `.github/prompts/connect-integration-graphs.prompt.md`
    - [x] **2.5** `.github/prompts/craft-prompt.prompt.md`
    - [x] **2.6** `.github/prompts/ctx-checkpoint.prompt.md`
    - [x] **2.7** `.github/prompts/ctx-doctor.prompt.md`
    - [x] **2.8** `.github/prompts/ctx-insight.prompt.md`
    - [x] **2.9** `.github/prompts/ctx-resume.prompt.md`
    - [x] **2.10** `.github/prompts/ctx-start.prompt.md`
    - [x] **2.11** `.github/prompts/ctx-status.prompt.md`
    - [x] **2.12** `.github/prompts/deep-search.prompt.md`
    - [x] **2.13** `.github/prompts/del-project-context.prompt.md`
    - [x] **2.14** `.github/prompts/eval-workflows.prompt.md`
    - [x] **2.15** `.github/prompts/health.prompt.md`
    - [x] **2.16** `.github/prompts/implement.prompt.md`
    - [x] **2.17** `.github/prompts/init-context.prompt.md`
    - [x] **2.18** `.github/prompts/plan.prompt.md`
    - [x] **2.19** `.github/prompts/review.prompt.md`
    - [x] **2.20** `.github/prompts/strategic-review.prompt.md`
    - [x] **2.21** `.github/prompts/validate.prompt.md`
    - [x] **2.22** `.github/prompts/visualize-graph.prompt.md`

---

### [x] Onda 3 (`CA-04`): Adequação em Lote das 81 Skills (`.github/skills/*/SKILL.md`) *(Concluída)*

- [x] **3.1** Padronizar o frontmatter YAML (`name`, `description` em **3ª pessoa** contendo explicitamente `Use quando...` e `Não use para...`) e as seções obrigatórias do `skill-template.md` (`## Quando Usar (Gatilhos de Ativação)`, `## Regras de Ouro e Invariantes`, `## Padrões Canônicos de Execução`, `## Anti-Patterns (O Que NUNCA Fazer)`, `## Progressive Disclosure (`references/` e `examples/`)`) nas **81 Skills** (`.github/skills/*/SKILL.md`).
- [x] **3.2** Executar extração Progressive Disclosure (R-066) para `references/` nas **11 skills restantes > 300 linhas** (9 ainda > 300 linhas no disco + validação de paridade das 2 meta-skills extraídas na Onda 1), reduzindo cada `SKILL.md` para ≤ 300 linhas sem perda semântica:
    - [x] **3.2.1** `.github/skills/agent-contracts/SKILL.md` (423 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.2** `.github/skills/agent-evals-lab/SKILL.md` (362 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.3** `.github/skills/context-mode/SKILL.md` (335 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.4** `.github/skills/handoff-governance/SKILL.md` (422 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.5** `.github/skills/project-scanner/SKILL.md` (514 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.6** `.github/skills/terminal-governance/SKILL.md` (394 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.7** `.github/skills/test-implementation-angular-jasmine/SKILL.md` (311 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.8** `.github/skills/test-implementation-angular-vitest/SKILL.md` (406 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.9** `.github/skills/test-implementation-spring-boot/SKILL.md` (335 linhas → extrair para `references/` até ≤ 300 linhas)
    - [x] **3.2.10** `.github/skills/governance-factory-patterns/SKILL.md` (extraído na Onda 1 para `references/artifact-specs-and-stack-topology.md` — 132 linhas)
    - [x] **3.2.11** `.github/skills/governance-audit-patterns/SKILL.md` (extraído na Onda 1 para `references/smells-catalog-detailed.md` — 172 linhas)
- [x] **3.3** Validar as demais **70 skills** (que já possuem ≤ 300 linhas) quanto à paridade de seções obrigatórias e `description` em 3ª pessoa (`Use quando... Não use para...`).

---

### [x] Onda 4 (`CA-05`): Adequação em Lote dos 62 Agents (`.github/agents/**/*.agent.md`) *(Concluída)*

- [x] **4.1** Adequar os Agents de perfil **`Router`** (conforme `router-agent.md` — R-054: `agent-router`, `backend-router`, `frontend-router`, `database-router`, `migration-router`):
  - Frontmatter `tools` restrito de roteamento, `source_docs_lazy` (R-066), matriz de roteamento determinística, `## Retorno ao Router (R-042 — Anti Sticky-Session)` e `## ⚙️ Protocolo de Execução Obrigatório` + `<execution_protocol>` (R-059/R-060).
- [x] **4.2** Adequar os Agents de perfil **`Analítico/Read-Only/Advisor`** (conforme `research-agent.md` — R-025/R-064: planejadores, `*-arch-advisor`, `bug-triage`, `code-reviewer`, `agent-auditor`, `deep-search`, etc.):
  - Frontmatter `tools` estritamente Read-Only (sem tools de escrita), `source_docs_lazy` (R-066), contrato de materialização de planos em `docs/plans/<tipo>/` via delegação, `## Retorno ao Router (R-042)` e `## ⚙️ Protocolo de Execução Obrigatório` + `<execution_protocol>` (R-059/R-060).
- [x] **4.3** Adequar os Agents de perfil **`Executor/Developer/Test-Engineer`** (conforme `operational-agent.md` — R-051/R-064: `*-developer`, `*-test-engineer`, especialistas de banco, executores de migração, `governance-maintainer`, `governance-factory`, etc.):
  - Frontmatter `tools` calibrado por capability profile, `source_docs_lazy` (R-066), guarda de pré-condição de plano `plan_ref` (`pre_condicao_plano` R-064), validação agrupada `get_errors` (R-051), `## Retorno ao Router (R-042)` e `## ⚙️ Protocolo de Execução Obrigatório` + `<execution_protocol>` (R-059/R-060).
- [x] **4.4** Executar `tools/agent_protocol_sync/sync_execution_protocol.py` sobre todos os **62 agents** (`.github/agents/**/*.agent.md`) garantindo paridade 100% do bloco `<execution_protocol>`.

---

### [x] Onda 5 (`CA-06`): Sincronização de Catálogos/Índices, Blindagem de `@governance-factory` e Testes de Contrato *(Concluída)*

- [x] **5.1** Sincronizar catálogos e índices globais e de domínio (R-015 / R-040):
  - [x] `.github/agents/catalog.yaml`
  - [x] `.github/agents/routing-graph.yaml`
  - [x] `.github/skills/.index.json`
  - [x] Catálogos de domínio `*-catalog.yaml` (`.github/agents/backend/backend-catalog.yaml`, `.github/agents/frontend/frontend-catalog.yaml`, `.github/agents/database/database-catalog.yaml`, `.github/agents/migration/migration-catalog.yaml`) e AgentCards (`.a2a/agentcards/*.json`).
- [x] **5.2** Blindar `.github/agents/governance-factory.agent.md` para que toda criação futura de agent, skill, prompt ou stack exija obrigatoriamente a estrutura das Ondas 1 a 4 (`CA-01` a `CA-05`).
- [x] **5.3** Fortalecer os testes de contrato em `tests/governance_audit/` para validar deterministicamente os templates (`CA-01`), os 22 prompts (`CA-03`), as 81 skills e teto ≤ 300 linhas (`CA-04`), os 62 agents (`CA-05`) e a paridade de catálogos (`CA-06`).
- [x] **5.4** Atualizar documentação raiz (`CHANGELOG.md`, `README.md`, `CLAUDE.md`, `AGENTS.md`) e executar validação final consolidada (`pytest tests/governance_audit/` + `get_errors`).

---

## 3. Resumo de Estado no Disco por Onda

| Onda | Código CA | Escopo | Total de Alvos | Status Atual |
|---|---|---|---:|---|
| **Onda 1** | `CA-01` | Templates Oficiais (6) + Meta-Skills (2 SKILL.md + 2 references) | 10 arquivos | `[x]` Concluída |
| **Onda 2** | `CA-03` | Adequação em lote dos Prompts (`.github/prompts/*.prompt.md`) | 22 prompts | `[x]` Concluída |
| **Onda 3** | `CA-04` | Adequação em lote das Skills (`.github/skills/*/SKILL.md` + 11 extrações > 300 linhas) | 81 skills | `[x]` Concluída |
| **Onda 4** | `CA-05` | Adequação em lote dos Agents (`.github/agents/**/*.agent.md` por perfil) | 62 agents | `[x]` Concluída |
| **Onda 5** | `CA-06` | Catálogos/Índices + Blindagem `@governance-factory` + Testes `tests/governance_audit/` | Catálogos + Testes | `[x]` Concluída |

---

## 4. Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)

- **Prevenção de Context Bloat e Denial of Wallet (OWASP Agentic Top 10)**: O teto de 300 linhas (R-066) nas 81 skills e o `source_docs_lazy` nos 62 agents impedem a injeção desnecessária de referências pesadas na janela de contexto.
- **Isolamento de Privilégios por Perfil (R-025 / R-054)**: Routers e Advisors/Planners permanecem estritamente sem ferramentas de escrita nos templates e nas 62 instâncias de agents.
- **Integridade de Diretórios de Planos (R-064)**: Proibição estrita do diretório legado `docs/implementation-plans/` (validada por `test_ca01_legacy_plan_directories_do_not_exist` em `tests/governance_audit/test_universal_plan_materialization_governance.py`).

---

## 5. Alternativas Rejeitadas

1. **Inverter ou fundir as Ondas 2 (`CA-03` Prompts), 3 (`CA-04` Skills) e 4 (`CA-05` Agents)**: Rejeitada — a ordem canônica `CA-01 → CA-03 → CA-04 → CA-05 → CA-06` garante validação incremental do menor para o maior acoplamento antes do fechamento dos catálogos na Onda 5.
2. **Manter cópia em `docs/implementation-plans/`**: Rejeitada — `tests/governance_audit/test_universal_plan_materialization_governance.py` proíbe expressamente a existência de `docs/implementation-plans/` (`LEGACY_PLAN_DIRS`).
3. **Executar edições unitárias fora do sandbox `context-mode`**: Rejeitada por violar R-008, R-056, R-059 e R-060.

---

## 6. Portão de Reúso Sistêmico (R-055: Q1 / Q2 / Q3)

- **Q1 (Artefatos Irmãos/Peers)**: Cobertura integral dos 22 prompts (Onda 2), 81 skills (Onda 3) e 62 agents (Onda 4).
- **Q2 (Templates Canônicos)**: Atualizados na Onda 1 (`.github/agents/templates/*.md`, `.github/prompts/templates/prompt-template.md`, `.github/skills/templates/skill-template.md`) e nas meta-skills `governance-factory-patterns` e `governance-audit-patterns`.
- **Q3 (Testes Determinísticos no Pytest)**: Fortalecimento na Onda 5 (`CA-06`) em `tests/governance_audit/`.
