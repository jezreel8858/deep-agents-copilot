---
title: "Plano de Manutenção de Governança — Migração de Modelos Deprecated (Gemini 4 Argon e Gemini 3.8 Flash)"
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-17"
related-planning-doc: "N/A"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
parent_plan_ref: "N/A — plano raiz"
review_rounds: 2
review_verdict: "PASS_WITH_NITS"
reviewer: "@plan-critic"
review_tier1: "PASS"
allowed_files:
  - ".a2a/agentcards/adapter-generator.agentcard.json"
  - ".a2a/agentcards/binding-initializer.agentcard.json"
  - ".a2a/agentcards/code-style-enforcer.agentcard.json"
  - ".a2a/agentcards/codegraph-engine.agentcard.json"
  - ".a2a/agentcards/docs-engineer.agentcard.json"
  - ".a2a/agentcards/governance-maintainer.agentcard.json"
  - ".a2a/agentcards/pr-gatekeeper.agentcard.json"
  - ".a2a/agentcards/prompt-structuring.agentcard.json"
  - ".a2a/agentcards/runtime-verifier.agentcard.json"
  - ".github/agents/adapter-generator.agent.md"
  - ".github/agents/backend/ejb/ejb-developer.agent.md"
  - ".github/agents/backend/ejb/ejb-test-engineer.agent.md"
  - ".github/agents/backend/python/python-developer.agent.md"
  - ".github/agents/backend/python/python-test-engineer.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-developer.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-developer.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-test-engineer.agent.md"
  - ".github/agents/backend/struts/struts-developer.agent.md"
  - ".github/agents/backend/struts/struts-test-engineer.agent.md"
  - ".github/agents/binding-initializer.agent.md"
  - ".github/agents/catalog.yaml"
  - ".github/agents/code-style-enforcer.agent.md"
  - ".github/agents/codegraph-engine.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/agents/frontend/angular/angular-developer.agent.md"
  - ".github/agents/frontend/angular/angular-test-engineer.agent.md"
  - ".github/agents/frontend/react/react-developer.agent.md"
  - ".github/agents/frontend/react/react-test-engineer.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/pr-gatekeeper.agent.md"
  - ".github/agents/prompt-structuring.agent.md"
  - ".github/agents/runtime-verifier.agent.md"
  - ".github/agents/templates/agent-template.md"
  - ".github/agents/templates/operational-agent.md"
  - ".github/prompts/add-project-context.prompt.md"
  - ".github/prompts/catalog.yaml"
  - ".github/prompts/commit.prompt.md"
  - ".github/prompts/craft-prompt.prompt.md"
  - ".github/prompts/ctx-checkpoint.prompt.md"
  - ".github/prompts/ctx-doctor.prompt.md"
  - ".github/prompts/ctx-insight.prompt.md"
  - ".github/prompts/ctx-resume.prompt.md"
  - ".github/prompts/ctx-start.prompt.md"
  - ".github/prompts/ctx-status.prompt.md"
  - ".github/prompts/del-project-context.prompt.md"
  - ".github/prompts/eval-workflows.prompt.md"
  - ".github/prompts/health.prompt.md"
  - ".github/prompts/init-context.prompt.md"
  - ".github/prompts/plan-lessons-harvester.prompt.md"
  - ".github/prompts/README.md"
  - ".github/prompts/review.prompt.md"
  - ".github/prompts/synth-waves.prompt.md"
  - ".github/prompts/templates/prompt-template.md"
  - ".github/prompts/validate.prompt.md"
  - ".github/prompts/visualize-graph.prompt.md"
  - ".github/skills/agent-contracts/references/detailed-patterns-and-examples.md"
  - ".github/skills/governance-audit-patterns/references/smells-catalog-detailed.md"
  - ".github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md"
  - ".github/skills/governance-factory-patterns/SKILL.md"
  - ".github/skills/handoff-governance/references/detailed-patterns-and-examples.md"
  - "docs/architecture/model-profiles-allowlist.md"
  - "docs/guides/model-profiles.md"
  - "docs/guides/synth-routing-eval-copilot-sdk-guide.md"
  - "model-profiles.yaml"
  - "tests/governance_audit/test_agent_model_tier_governance.py"
  - "tests/governance_audit/test_hybrid_model_routing_and_zero_noise_governance.py"
  - "tests/governance_audit/test_model_profiles_parity.py"
  - "tests/governance_audit/test_plan_lessons_harvester_governance.py"
  - "tests/model_allowlist/conftest.py"
  - "tests/model_allowlist/fixtures/reordered_columns.html"
  - "tests/model_allowlist/fixtures/valid_supported_models.html"
  - "tests/model_allowlist/test_diff.py"
  - "tests/model_allowlist/test_parse.py"
  - "tests/model_allowlist/test_write.py"
  - "tests/model_profiles/_helpers.py"
  - "tests/model_profiles/test_suspend_resume.py"
  - "tests/operational_flow/workflow_eval_simulator.py"
  - "tests/README.md"
excluded_files:
  - "CHANGELOG.md"
  - "docs/plans/governance/20261115-123014-governance-maintenance-plan-critic-lessons-shielding.md"
  - "docs/plans/governance/20261115-183000-synth-waves-prompt.md"
  - "docs/plans/governance/20261116-120000-eval-workflows-prompt-melhorias.md"
  - "docs/plans/governance/20261116-123000-pre-commit-r044-tb34-fix.md"
  - "docs/plans/implementation/20261010-090000-feature-development-model-profiles-allowlist.md"
  - "model-profiles.local.yaml"
  - ".cache/_gather.txt"
  - ".idea/**"
  - ".model-profiles/state.json"
  - "tmp/**"
  - "deploy/local-chat-gateway/data/gateway.dev.db"
  - "tools/context-insight-visualizer/dist/context-insight.html"
---

# Plano de Manutenção de Governança — Migração de Modelos Deprecated

## 1. Contexto, Motivação e Mapeamento Canônico

Este plano de manutenção de governança formaliza a substituição determinística de dois modelos descontinuados/deprecated em todo o ecossistema declarativo, configurações, documentações vivas e suítes de testes do repositório, preservando a integridade histórica de registros de auditoria passados (`CHANGELOG.md` e planos `APPROVED`).

### 1.1. Mapeamento Explícito de Substituição

| Modelo Deprecated (Origem) | Modelo Canônico Substituto (Destino) | Escopo de Aplicação |
| :--- | :--- | :--- |
| `Gemini 4 Argon` | `Gemini 4 Carbon` | Agentes (`.github/agents/**`), Prompts (`.github/prompts/**`), Skills (`.github/skills/**`), AgentCards (`.a2a/agentcards/**`), Perfis de Modelo, Documentação Viva e Testes |
| `Gemini 3.8 Flash` | `Gemini Hydrogen 4` | Agentes (`.github/agents/**`), Prompts (`.github/prompts/**`), Skills (`.github/skills/**`), AgentCards (`.a2a/agentcards/**`), Perfis de Modelo, Documentação Viva e Testes |

### 1.2. Síntese Quantitativa da Auditoria (`@agent-auditor`)

| Categoria de Arquivos | Quantidade de Arquivos | Ocorrências `Gemini 4 Argon` | Ocorrências `Gemini 3.8 Flash` | Tratamento |
| :--- | :---: | :---: | :---: | :--- |
| **Escopo Ativo a Atualizar (`allowed_files` + template §3.10)** | **79** em `allowed_files` (+1 template `.local.yaml.example` em §3.10) | **88** | **138** | Atualização governada por perfil de executor |
| **Histórico / Audit Trail (`excluded_files` — preservar)** | **6** | **11** | **55** | Preservação estrita (zero mutação em histórico aprovado) |
| **Efêmeros / Gitignored / Não Versionados (`excluded_files`)** | **19** | **8** | **77** | Ignorar (apenas reportar `model-profiles.local.yaml` L25 ao usuário) |
| **Total Global Auditado** | **105** | **107** | **270** | Cobertura 100% mapeada |

---

## 2. Portão de Reúso e Generalização Sistêmica (R-055 — Q0, Q1, Q2, Q3)

- **Q0 (Origem Upstream / RCA)**: A atualização da allowlist oficial (`model-allowlist.yaml`) substituiu os identificadores `Gemini 4 Argon` por `Gemini 4 Carbon` e `Gemini 3.8 Flash` por `Gemini Hydrogen 4`. Artefatos declarativos, catálogos, templates, snapshots A2A e testes de paridade que referenciavam os nomes antigos precisam convergir atomicamente para evitar deriva de catálogo (R-015) e falhas de paridade.
- **Q1 (Peers / Artefatos Análogos)**: A varredura cobriu 100% dos peers em `.github/agents/**` (root 9, backend 10, frontend 4), `.github/prompts/**` (18 prompts + catálogo/README), `.github/skills/**` (5 arquivos), `model-profiles.yaml`, `model-profiles.local.yaml.example` (registrado em §3.10 fora de `allowed_files` para não acionar o filtro `*.local.*` do Tier 1 C10), `.a2a/agentcards/**` (9 snapshots) e documentações vivas em `docs/**` e `tests/README.md` (4 arquivos).
- **Q2 (Templates Canônicos)**: Incluídos explicitamente no escopo ativo os templates canônicos `.github/agents/templates/agent-template.md`, `.github/agents/templates/operational-agent.md` e `.github/prompts/templates/prompt-template.md` para impedir a reintrodução dos modelos antigos na criação de novos agentes/prompts.
- **Q3 (Sensores Automatizados no `pytest` e Fronteira Python)**:
  - Toda mutação em arquivos `tests/**/*.py` (11 arquivos) e avaliação de fixtures `tests/model_allowlist/fixtures/*.html` (2 arquivos) **NÃO** será executada diretamente pelo `@governance-maintainer`, mas via handoff obrigatório ao subgrafo Python (`@python-router` → 1º `@python-arch-advisor` [plano de implementação em `docs/plans/implementation/` com `related-planning-doc` apontando para este plano] → 2º `@python-test-engineer`).
  - Inclui a correção da contradição pré-existente em `tests/governance_audit/test_model_profiles_parity.py#L119` (`economico.orchestration` esperava `Gemini 3.8 Flash` enquanto `model-profiles.yaml` já define `Gemini Hydrogen 4`) e a adição do sensor automatizado de paridade `model:` vs. `model-allowlist.yaml` especificamente dentro do arquivo existente `tests/governance_audit/test_model_profiles_parity.py` (já listado entre os 4 arquivos de `tests/governance_audit/` em `allowed_files`), evitando criação ou edição de arquivo não listado.

### 2.1. Análise de Escape (T2-RCA — Por que a Deriva Não Foi Bloqueada Automaticamente Antes)

1. **Ausência de Sensor Cruzado Allowlist ↔ Frontmatters/Catálogos**: Os testes existentes em `tests/governance_audit/` verificavam a paridade interna entre os contratos `.github/agents/**/*.agent.md` e `.github/agents/catalog.yaml`, bem como valores pontuais de `model-profiles.yaml` em `tests/governance_audit/test_model_profiles_parity.py`, mas **não validavam sistematicamente se 100% dos atributos `model:` declarados em `.github/agents/**/*.agent.md`, `.github/agents/catalog.yaml`, `.github/prompts/*.prompt.md`, `.github/prompts/catalog.yaml` e `model-profiles.yaml` pertenciam ao conjunto ativo de `model-allowlist.yaml`**.
2. **Atualização Parcial na Fonte Upstream (`model-allowlist.yaml` e `model-profiles.yaml`)**: Quando `model-allowlist.yaml` removeu `Gemini 4 Argon` e `Gemini 3.8 Flash` e `model-profiles.yaml` foi parcialmente atualizado na working tree, a ausência desse contrato automatizado permitiu que 80 artefatos continuassem referenciando identificadores descontinuados sem acusar falha imediata de allowlist nos frontmatters e catálogos.

### 2.2. Neutralização na Fonte (T2-RCA — Prevenção Definitiva de Recorrência)

1. **Implementação do Sensor de Paridade `model:` vs. `model-allowlist.yaml` em `tests/governance_audit/test_model_profiles_parity.py`**:
   - O sensor será implementado diretamente em `tests/governance_audit/test_model_profiles_parity.py` (um dos 4 arquivos de `tests/governance_audit/` já declarados em `allowed_files`, juntamente com `test_agent_model_tier_governance.py`, `test_hybrid_model_routing_and_zero_noise_governance.py` e `test_plan_lessons_harvester_governance.py`), garantindo estrita conformidade de escopo sem tocar em arquivos fora de `allowed_files`.
   - O teste carregará os modelos vigentes de `model-allowlist.yaml` e validará que todos os identificadores `model:` em `.github/agents/**/*.agent.md`, `.github/agents/catalog.yaml`, `.github/prompts/*.prompt.md`, `.github/prompts/catalog.yaml` e `model-profiles.yaml` existem na allowlist ativa, além de bloquear regressões de `Gemini 4 Argon` e `Gemini 3.8 Flash` nos templates canônicos (`.github/agents/templates/*.md` e `.github/prompts/templates/prompt-template.md`).

---

## 3. Inventário Detalhado de Escopo Ativo (`allowed_files` — 79 arquivos + 1 template versionado em §3.10)

### 3.1. Contratos de Agentes (`.github/agents/**/*.agent.md` — 23 arquivos)

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `.github/agents/adapter-generator.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 2 | `.github/agents/backend/ejb/ejb-developer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 3 | `.github/agents/backend/ejb/ejb-test-engineer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 4 | `.github/agents/backend/python/python-developer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 5 | `.github/agents/backend/python/python-test-engineer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 6 | `.github/agents/backend/spring-boot/spring-boot-developer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 7 | `.github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 8 | `.github/agents/backend/spring-reactive/spring-reactive-developer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 9 | `.github/agents/backend/spring-reactive/spring-reactive-test-engineer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 10 | `.github/agents/backend/struts/struts-developer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 11 | `.github/agents/backend/struts/struts-test-engineer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 12 | `.github/agents/binding-initializer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 13 | `.github/agents/code-style-enforcer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 14 | `.github/agents/codegraph-engine.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 15 | `.github/agents/docs-engineer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 16 | `.github/agents/frontend/angular/angular-developer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 17 | `.github/agents/frontend/angular/angular-test-engineer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 18 | `.github/agents/frontend/react/react-developer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 19 | `.github/agents/frontend/react/react-test-engineer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 20 | `.github/agents/governance-maintainer.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 21 | `.github/agents/pr-gatekeeper.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 22 | `.github/agents/prompt-structuring.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |
| 23 | `.github/agents/runtime-verifier.agent.md` | 1 | 0 | `@governance-maintainer` | Substituir em frontmatter `model:` e corpo via `ctx_execute` JS |

### 3.2. Catálogo SSoT e Templates de Agentes (`.github/agents/` — 3 arquivos)

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `.github/agents/catalog.yaml` | 9 | 7 | `@governance-maintainer` | Atualizar SSoT `catalog.yaml` e templates R-055/Q2 via `ctx_execute` JS |
| 2 | `.github/agents/templates/agent-template.md` | 1 | 1 | `@governance-maintainer` | Atualizar SSoT `catalog.yaml` e templates R-055/Q2 via `ctx_execute` JS |
| 3 | `.github/agents/templates/operational-agent.md` | 1 | 1 | `@governance-maintainer` | Atualizar SSoT `catalog.yaml` e templates R-055/Q2 via `ctx_execute` JS |

### 3.3. Slash Prompts (`.github/prompts/*.prompt.md` — 18 arquivos)

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `.github/prompts/add-project-context.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 2 | `.github/prompts/commit.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 3 | `.github/prompts/craft-prompt.prompt.md` | 1 | 0 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 4 | `.github/prompts/ctx-checkpoint.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 5 | `.github/prompts/ctx-doctor.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 6 | `.github/prompts/ctx-insight.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 7 | `.github/prompts/ctx-resume.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 8 | `.github/prompts/ctx-start.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 9 | `.github/prompts/ctx-status.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 10 | `.github/prompts/del-project-context.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 11 | `.github/prompts/eval-workflows.prompt.md` | 1 | 0 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 12 | `.github/prompts/health.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 13 | `.github/prompts/init-context.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 14 | `.github/prompts/plan-lessons-harvester.prompt.md` | 1 | 0 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 15 | `.github/prompts/review.prompt.md` | 1 | 0 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 16 | `.github/prompts/synth-waves.prompt.md` | 1 | 0 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 17 | `.github/prompts/validate.prompt.md` | 1 | 0 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |
| 18 | `.github/prompts/visualize-graph.prompt.md` | 0 | 1 | `@governance-maintainer` | Substituir `model:` no frontmatter via `ctx_execute` JS |

### 3.4. Catálogo, README e Template de Prompts (`.github/prompts/` — 3 arquivos)

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `.github/prompts/catalog.yaml` | 6 | 13 | `@governance-maintainer` | Sincronizar catálogo, tabela README e template via `ctx_execute` JS |
| 2 | `.github/prompts/README.md` | 0 | 1 | `@governance-maintainer` | Sincronizar catálogo, tabela README e template via `ctx_execute` JS |
| 3 | `.github/prompts/templates/prompt-template.md` | 1 | 1 | `@governance-maintainer` | Sincronizar catálogo, tabela README e template via `ctx_execute` JS |

### 3.5. Skills e Referências Normativas (`.github/skills/**` — 5 arquivos)

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `.github/skills/agent-contracts/references/detailed-patterns-and-examples.md` | 0 | 6 | `@governance-maintainer` | Atualizar exemplos e tabelas normativas via `ctx_execute` JS |
| 2 | `.github/skills/governance-audit-patterns/references/smells-catalog-detailed.md` | 0 | 2 | `@governance-maintainer` | Atualizar exemplos e tabelas normativas via `ctx_execute` JS |
| 3 | `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md` | 0 | 3 | `@governance-maintainer` | Atualizar exemplos e tabelas normativas via `ctx_execute` JS |
| 4 | `.github/skills/governance-factory-patterns/SKILL.md` | 1 | 1 | `@governance-maintainer` | Atualizar exemplos e tabelas normativas via `ctx_execute` JS |
| 5 | `.github/skills/handoff-governance/references/detailed-patterns-and-examples.md` | 0 | 1 | `@governance-maintainer` | Atualizar exemplos e tabelas normativas via `ctx_execute` JS |

### 3.6. Configuração Canônica de Perfis de Modelo (`model-profiles.yaml` — 1 arquivo em `allowed_files`)

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `model-profiles.yaml` | 0 | 1 | `@governance-maintainer` | Atualizar `economico.tiers.stack-arch` (L118) preservando alterações válidas pré-existentes na working tree |

### 3.7. Artefatos Derivados A2A AgentCards (`.a2a/agentcards/*.agentcard.json` — 9 arquivos)

> **Regra Crítica de Integridade (R-051)**: Estes 9 arquivos derivados **NÃO** devem ser editados manualmente. Devem ser regenerados deterministicamente via `tools/agentcard_exporter/export_agentcards.py` após a atualização de `.github/agents/**` e `.github/agents/catalog.yaml`.

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `.a2a/agentcards/adapter-generator.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |
| 2 | `.a2a/agentcards/binding-initializer.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |
| 3 | `.a2a/agentcards/code-style-enforcer.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |
| 4 | `.a2a/agentcards/codegraph-engine.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |
| 5 | `.a2a/agentcards/docs-engineer.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |
| 6 | `.a2a/agentcards/governance-maintainer.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |
| 7 | `.a2a/agentcards/pr-gatekeeper.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |
| 8 | `.a2a/agentcards/prompt-structuring.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |
| 9 | `.a2a/agentcards/runtime-verifier.agentcard.json` | 1 | 0 | `@governance-maintainer` | Regenerar via `tools/agentcard_exporter/export_agentcards.py` |

### 3.8. Documentação Viva (`docs/**` e `tests/README.md` — 4 arquivos)

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `docs/architecture/model-profiles-allowlist.md` | 4 | 2 | `@docs-engineer` | Atualizar tabelas e referências de documentação viva (R-033) |
| 2 | `docs/guides/model-profiles.md` | 0 | 3 | `@docs-engineer` | Atualizar tabelas e referências de documentação viva (R-033) |
| 3 | `docs/guides/synth-routing-eval-copilot-sdk-guide.md` | 1 | 1 | `@docs-engineer` | Atualizar tabelas e referências de documentação viva (R-033) |
| 4 | `tests/README.md` | 0 | 3 | `@docs-engineer` | Atualizar tabelas e referências de documentação viva (R-033) |

### 3.9. Suíte de Testes Python e Fixtures HTML (`tests/**` — 13 arquivos)

> **Fronteira Territorial R-055/Q3**: Mutações em `*.py` exigem handoff para `@python-router` → `@python-arch-advisor` (criação de plano em `docs/plans/implementation/` vinculado via `related-planning-doc`) → `@python-test-engineer`. As 2 fixtures HTML (`tests/model_allowlist/fixtures/*.html`) têm decisão explícita submetida ao Gate HITL (atualizar junto aos testes do scraper ou preservar como amostra sintética histórica da página upstream).

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `tests/governance_audit/test_agent_model_tier_governance.py` | 0 | 1 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 2 | `tests/governance_audit/test_hybrid_model_routing_and_zero_noise_governance.py` | 3 | 5 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 3 | `tests/governance_audit/test_model_profiles_parity.py` | 0 | 9 | `@python-test-engineer (via @python-router)` | Atualizar asserções (incluindo L119) e adicionar sensor de paridade `model:` vs. `model-allowlist.yaml` (§2.2 / R-055 Q3) |
| 4 | `tests/governance_audit/test_plan_lessons_harvester_governance.py` | 1 | 0 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 5 | `tests/model_allowlist/conftest.py` | 0 | 1 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 6 | `tests/model_allowlist/test_diff.py` | 0 | 3 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 7 | `tests/model_allowlist/test_parse.py` | 0 | 2 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 8 | `tests/model_allowlist/test_write.py` | 0 | 4 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 9 | `tests/model_profiles/_helpers.py` | 0 | 1 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 10 | `tests/model_profiles/test_suspend_resume.py` | 0 | 1 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 11 | `tests/operational_flow/workflow_eval_simulator.py` | 0 | 1 | `@python-test-engineer (via @python-router)` | Atualizar asserções/mocks e avaliar sensor de allowlist (R-055/Q3) |
| 12 | `tests/model_allowlist/fixtures/reordered_columns.html` | 0 | 1 | `@python-test-engineer (via @python-router)` | **Decisão Gate HITL**: (1ª opção Recomendada) Preservar intacta se amostra sintética histórica do scraper; ou (2ª opção) atualizar se acoplada à allowlist vigente |
| 13 | `tests/model_allowlist/fixtures/valid_supported_models.html` | 1 | 1 | `@python-test-engineer (via @python-router)` | **Decisão Gate HITL**: (1ª opção Recomendada) Preservar intacta se amostra sintética histórica do scraper; ou (2ª opção) atualizar se acoplada à allowlist vigente |

### 3.10. Template Versionado de Overlay Local (Fora de `allowed_files` por Filtro Tier 1 C10 — 1 arquivo)

> **Conformidade Tier 1 (Gate C10)**: O validador pré-HITL proíbe padrões `*.local.*` dentro de `allowed_files` no frontmatter YAML para evitar inclusão acidental de overlays locais gitignored (R-043). Como `model-profiles.local.yaml.example` é um template versionado no Git (sem segredos ou bindings locais), ele fica removido de `allowed_files` e registrado nesta seção própria para atualização em conjunto na Etapa 2 (mediante confirmação no Gate HITL).

| # | Arquivo | Argon | Flash | Executor | Ação |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `model-profiles.local.yaml.example` | 0 | 1 | `@governance-maintainer` | Atualizar exemplo de perfil local (L22: `Gemini 3.8 Flash` → `Gemini Hydrogen 4`) em conjunto ou mediante confirmação no Gate HITL |

---

## 4. Escopo Excluído (`excluded_files` — 25 arquivos)

### 4.1. Histórico e Audit Trail Versionado a Preservar (6 arquivos — Proibida Edição)

Estes **6 arquivos** (`CHANGELOG.md` + **5 planos históricos** já aprovados/executados em `docs/plans/`) registram entregas históricas fechadas e **não devem sofrer mutação retroativa** (R-001):

| # | Arquivo | Argon | Flash | Classificação e Justificativa |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `CHANGELOG.md` | 2 | 12 | Registro histórico imutável de releases passadas |
| 2 | `docs/plans/governance/20261115-123014-governance-maintenance-plan-critic-lessons-shielding.md` | 3 | 12 | Plano histórico (`APPROVED`) — registro de auditoria |
| 3 | `docs/plans/governance/20261115-183000-synth-waves-prompt.md` | 2 | 10 | Plano histórico (`APPROVED`) — registro de auditoria |
| 4 | `docs/plans/governance/20261116-120000-eval-workflows-prompt-melhorias.md` | 2 | 11 | Plano histórico (`APPROVED`) — registro de auditoria |
| 5 | `docs/plans/governance/20261116-123000-pre-commit-r044-tb34-fix.md` | 2 | 9 | Plano histórico (`APPROVED`) — registro de auditoria |
| 6 | `docs/plans/implementation/20261010-090000-feature-development-model-profiles-allowlist.md` | 0 | 1 | Plano de implementação histórico/preservado (`APPROVED`) — imutável (R-001) |

### 4.2. Arquivos Não Versionados / Gitignored / Artefatos de Build / Efêmeros a Ignorar (19 arquivos)

- **Overlay Local do Usuário (1 arquivo — R-043)**:
  - `model-profiles.local.yaml` (0 `Argon`, 1 `Flash` na L25): arquivo local gitignored do desenvolvedor. Não deve ser modificado autonomamente por agentes; será apenas reportado ao usuário no resumo final para atualização opcional.
- **Artefato de Build Gitignored (1 arquivo — fora do escopo de mutação manual)**:
  - `tools/context-insight-visualizer/dist/context-insight.html`: artefato compilado/empacotado em `dist/` (gitignored, gerado por build). Excluído de mutação manual (R-001).
- **Caches, Estado Runtime, IDE e Temporários (17 arquivos)**:
  - `.cache/_gather.txt`, `.model-profiles/state.json`, `deploy/local-chat-gateway/data/gateway.dev.db`, `.idea/workspace.xml` e arquivos temporários em `tmp/**`.

---

## 5. Riscos Mapeados, Pre-Mortem (ASI08), Estratégia de Rollback e Decisões do Gate HITL

| Risco / Vetor | Severidade | Mitigação Determinística |
| :--- | :---: | :--- |
| **Dessincronização entre `.agent.md`, `catalog.yaml` e `.a2a/agentcards/*.json`** | ALTA | Atualizar `.agent.md` e `catalog.yaml` no mesmo script `ctx_execute` JS e regenerar os 9 AgentCards exclusivamente via `tools/agentcard_exporter/export_agentcards.py`. |
| **Perda de alterações pré-existentes na working tree (`model-allowlist.yaml` e `model-profiles.yaml`)** | ALTA | **Estratégia de Rollback Seletivo (Pre-Mortem ASI08)**: Antes de iniciar qualquer mutação, registrar o `git status --porcelain` e `git diff` inicial separando as alterações pré-existentes em `model-allowlist.yaml` e `model-profiles.yaml`. Em caso de falha de paridade durante o lote, é **proibido** usar `git reset --hard` ou `git checkout .`; reverter apenas os arquivos tocados na etapa via `git restore <arquivos-da-etapa>` seletivo (e restaurar o diff pré-existente de `model-profiles.yaml` se necessário). |
| **Violação de Fronteira Territorial em `tests/**/*.py` (R-055/Q3)** | ALTA | `@governance-maintainer` atua estritamente nos artefatos declarativos/configuração; toda edição em `tests/**/*.py` e execução do `pytest` de código de aplicação ocorre via handoff para `@python-router` → `@python-arch-advisor` → `@python-test-engineer`. |
| **Quebra de testes do scraper HTML em `tests/model_allowlist/fixtures/*.html`** | MÉDIA | Submeter decisão explícita no Gate HITL (ver §5.1 abaixo) com recomendação técnica de preservação caso sejam amostras sintéticas históricas do parser. |

### 5.1. Deliberação Recomendada e Decisões Registradas no Gate HITL (`ask_questions` — R-027)

**Decisões Registradas pelo Usuário no Gate HITL (2026-11-17)**:
1. **Aprovação do Plano**: Plano aprovado (`status: APPROVED`, `approved: true`).
2. **`tests/model_allowlist/fixtures/*.html`**: **Preservar intactas** como amostras sintéticas históricas do parser do scraper (`reordered_columns.html` e `valid_supported_models.html` não devem ser alteradas).
3. **`model-profiles.local.yaml.example`**: **Autorizado atualizar** para o modelo vigente (`Gemini 3.8 Flash` → `Gemini Hydrogen 4`).

**Contexto da Deliberação Submetida**:

No Gate de Aprovação Humana (Etapa 4 do `WORKFLOW-GOVERNANCE-MAINTENANCE`), além da aprovação global do plano e da atualização do template `model-profiles.local.yaml.example` (§3.10), submeter a decisão sobre as 2 fixtures HTML (`tests/model_allowlist/fixtures/reordered_columns.html` e `tests/model_allowlist/fixtures/valid_supported_models.html`):
1. **1ª Opção `(Recomendado)` — Preservar as 2 fixtures HTML intactas se forem amostras sintéticas históricas do scraper**: Evita falso-positivo e preserva a fidelidade do teste de regressão caso `test_parse.py` valide o parsing de snapshots HTML históricos da documentação upstream, atualizando apenas se algum teste cruzar os nomes da fixture com `model-allowlist.yaml` vigente.
2. **2ª Opção — Atualizar as 2 fixtures HTML com os novos nomes canônicos (`Gemini 4 Carbon` / `Gemini Hydrogen 4`)**: Alinha os literais HTML aos mocks atualizados em `tests/model_allowlist/conftest.py` e `test_parse.py`, indicado apenas se os testes exigirem igualdade estrita entre a fixture HTML e a allowlist ativa.

---

## 6. Ordem de Execução Determinística (Pipeline Pós-Aprovação HITL)

1. **Etapa 1 — Baseline Pré-Mutação e Snapshot de Rollback Seletivo (Pre-Mortem ASI08)**:
   - Registrar `git status --porcelain` e salvar snapshot em memória/temporário do diff pré-existente de `model-allowlist.yaml` e `model-profiles.yaml`;
   - Executar `pytest tests/governance_audit` via `ctx_batch` para registrar o estado inicial (incluindo a divergência pré-existente em `test_model_profiles_parity.py#L119`).
2. **Etapa 2 — Mutação Declarativa em Lote (`@governance-maintainer`, R-046 / R-051 / R-059)**:
   - Executar script único em `ctx_execute` (`language: "javascript"`, `fs` nativo) aplicando o mapeamento (`Gemini 4 Argon` → `Gemini 4 Carbon` e `Gemini 3.8 Flash` → `Gemini Hydrogen 4`) nos 53 arquivos declarativos/configuração em `allowed_files` (mais `model-profiles.local.yaml.example` conforme §3.10 / Gate HITL):
     - 23 arquivos `.github/agents/**/*.agent.md`;
     - 1 arquivo `.github/agents/catalog.yaml`;
     - 2 templates `.github/agents/templates/*.md`;
     - 18 arquivos `.github/prompts/*.prompt.md`;
     - 3 arquivos `.github/prompts/catalog.yaml`, `.github/prompts/README.md` e `.github/prompts/templates/prompt-template.md`;
     - 5 arquivos em `.github/skills/**`;
     - 1 arquivo de configuração em `allowed_files` (`model-profiles.yaml`) + 1 template versionado (`model-profiles.local.yaml.example`, §3.10).
   - **Procedimento de Rollback em Caso de Falha**: Se a verificação pós-escrita acusar erro de paridade ou corrupção, executar `git restore` seletivo exclusivamente sobre os arquivos modificados nesta etapa, preservando `model-allowlist.yaml` e o estado inicial de `model-profiles.yaml`.
3. **Etapa 3 — Regeneração Determinística de AgentCards (`@governance-maintainer`, R-051)**:
   - Executar `python tools/agentcard_exporter/export_agentcards.py` para atualizar os 9 arquivos `.a2a/agentcards/*.agentcard.json` sem edição manual.
4. **Etapa 4 — Atualização de Documentação Viva (`@docs-engineer`, R-033)**:
   - Atualizar em lote via `ctx_execute` JS os 4 arquivos de documentação viva: `docs/architecture/model-profiles-allowlist.md`, `docs/guides/model-profiles.md`, `docs/guides/synth-routing-eval-copilot-sdk-guide.md` e `tests/README.md`.
5. **Etapa 5 — Handoff Python para Testes, Fixtures e Sensor de Allowlist (`@python-router` → `@python-arch-advisor` → `@python-test-engineer`, R-055/Q3)**:
   - Elaborar o plano de implementação Python em `docs/plans/implementation/` com `related-planning-doc: "docs/plans/governance/20261117-120000-migracao-modelos-deprecated.md"`;
   - Atualizar os 11 arquivos `tests/**/*.py` listados em `allowed_files` (e tratar as 2 fixtures `tests/model_allowlist/fixtures/*.html` conforme decisão do Gate HITL §5.1);
   - Implementar na fonte o sensor automatizado de paridade `model:` vs. `model-allowlist.yaml` dentro do arquivo existente `tests/governance_audit/test_model_profiles_parity.py` (§2.2).
6. **Etapa 6 — Quality Gate e Validação Final Consolidada**:
   - Executar `python -m tools.governance_sync --check`;
   - Executar `pytest tests/governance_audit`;
   - Executar `pytest tests/model_allowlist tests/model_profiles tests/operational_flow`;
   - Executar varredura final em `ctx_execute` JS confirmando **0 ocorrências** de `Gemini 4 Argon` e `Gemini 3.8 Flash` nos arquivos do escopo ativo e preservação intacta dos **6 arquivos históricos** (`CHANGELOG.md` + 5 planos `APPROVED` em `docs/plans/`, incluindo `docs/plans/implementation/20261010-090000-feature-development-model-profiles-allowlist.md`);
   - Executar `get_errors` agrupado.

---

## 7. Critérios de Aceite (Definition of Done)

- [ ] 0 ocorrências de `Gemini 4 Argon` e `Gemini 3.8 Flash` nos 79 arquivos do escopo ativo (`allowed_files`) e no template versionado `model-profiles.local.yaml.example` (§3.10), respeitada a deliberação do Gate HITL para as 2 fixtures HTML (`tests/model_allowlist/fixtures/*.html`).
- [ ] Sensor automatizado de paridade `model:` vs. `model-allowlist.yaml` implementado e passando em `tests/governance_audit/test_model_profiles_parity.py` (validando que 100% dos atributos `model:` em `.github/agents/**`, `.github/prompts/**` e `model-profiles.yaml` pertencem à allowlist vigente e bloqueando regressão em templates canônicos — Neutralização na Fonte §2.2).
- [ ] Paridade 100% preservada entre `.github/agents/**/*.agent.md`, `.github/agents/catalog.yaml` e `.a2a/agentcards/*.agentcard.json`.
- [ ] Paridade 100% preservada entre `.github/prompts/*.prompt.md`, `.github/prompts/catalog.yaml` e `.github/prompts/README.md`.
- [ ] **6 arquivos de histórico** (`CHANGELOG.md` e **5 planos `APPROVED`** em `docs/plans/`, incluindo `docs/plans/implementation/20261010-090000-feature-development-model-profiles-allowlist.md`) intactos com 0 diffs no `git status`, e `tools/context-insight-visualizer/dist/context-insight.html` preservado sem mutação manual (artefato de build gitignored).
- [ ] Alterações pré-existentes na working tree em `model-allowlist.yaml` e `model-profiles.yaml` preservadas sem perda acidental (estratégia de rollback seletivo via `git restore` respeitada).
- [ ] `python -m tools.governance_sync --check` aprovado com código de saída 0.
- [ ] Suítes `pytest tests/governance_audit`, `pytest tests/model_allowlist`, `pytest tests/model_profiles` e `pytest tests/operational_flow` com 100% de aprovação.

---

## 8. Histórico de Revisão Pré-HITL (`@plan-critic` — R-064 / R-065)

- **Rodada 1 (`review_rounds: 1`, `review_verdict: NEEDS_REVISION` → Endereçado para Rodada 2)**:
  1. **[BLOCKER — C10]**: Removido `model-profiles.local.yaml.example` de `allowed_files` no frontmatter (evitando violação do filtro `*.local.*` do Tier 1) e registrado na seção dedicada §3.10 como template versionado a ser atualizado em conjunto / mediante confirmação no Gate HITL.
  2. **[HIGH — T2-RCA]**: Adicionadas as seções formais **§2.1 Análise de Escape** e **§2.2 Neutralização na Fonte**, com critério verificável explícito no DoD (§7).
  3. **[HIGH — Consistência]**: Especificado que o sensor de paridade `model:` vs. `model-allowlist.yaml` será implementado no arquivo existente `tests/governance_audit/test_model_profiles_parity.py` (já listado em `allowed_files`), sem criar arquivo fora da lista autorizada.
  4. **[MEDIUM — Inventário R-001]**: Classificado explicitamente `docs/plans/implementation/20261010-090000-feature-development-model-profiles-allowlist.md` como plano histórico/preservado em §4.1 (ajustando a contagem exata para 6 arquivos históricos: `CHANGELOG.md` + 5 planos `APPROVED` no §4.1 e no DoD §7) e classificado `tools/context-insight-visualizer/dist/context-insight.html` em §4.2 como artefato de build gitignored fora do escopo de mutação manual.
  5. **[MEDIUM — Rollback / Pre-Mortem ASI08]**: Adicionada estratégia explícita de rollback seletivo em §5 e §6 (Etapa 1 e Etapa 2), separando alterações pré-existentes em `model-allowlist.yaml` e `model-profiles.yaml` via `git status` inicial e revertendo apenas arquivos da execução via `git restore` seletivo.
  6. **[LOW — HITL Fixtures]**: Formulada em §5.1 e §3.9 a decisão recomendada para `tests/model_allowlist/fixtures/*.html` com 1ª opção `(Recomendado)` para preservar as 2 fixtures HTML intactas caso sejam amostras sintéticas históricas do scraper vs. 2ª opção para atualizar apenas se os testes validarem nomes vigentes da allowlist.

- **Rodada 2 (`review_rounds: 2`, `review_verdict: PASS_WITH_NITS`, `reviewer: "@plan-critic"`, `review_tier1: "PASS"`)**:
  - **Resumo do Parecer**: `PASS_WITH_NITS` (0 `BLOCKER`, 0 `HIGH`, 1 `MEDIUM`, 2 `LOW` nits). Todos os achados bloqueantes e de alta severidade da Rodada 1 foram integralmente sanados; plano apto a avançar para o Gate HITL (`ask_questions`).
  1. **[MEDIUM — Decisão HITL para `model-profiles.local.yaml.example`]**: Como `model-profiles.local.yaml.example` permanece fora de `allowed_files` no frontmatter por restrição do filtro `*.local.*` do validador Tier 1 (C10), a atualização sincronizada do template versionado deve ser submetida à confirmação explícita no Gate HITL (§3.10 / §5.1).
  2. **[LOW — Nit #1]**: Observação menor de rastreabilidade documental sem impacto bloqueante na execução.
  3. **[LOW — Nit #2 — Paridade de `excluded_files`]**: Adicionado `tools/context-insight-visualizer/dist/context-insight.html` explicitamente em `excluded_files` no frontmatter para espelhar a listagem de artefatos locais/gitignored da seção §4.2.
