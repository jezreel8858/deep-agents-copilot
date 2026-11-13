---
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
version: "2.0"
created_at: "2026-04-20"
updated_at: "2026-04-20"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
related-planning-doc: "N/A — plano raiz (WORKFLOW-GOVERNANCE-MAINTENANCE)"
allowed_files:
  - "docs/plans/governance/20260420-090000-slash-prompts-router-bypass.md"
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - "docs/ai-copilot/invariantes-e-protocolos.md"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/templates/router-agent.md"
  - "templates/router-agent.md"
  - ".github/prompts/templates/prompt-template.md"
  - ".github/prompts/add-project-context.prompt.md"
  - ".github/prompts/commit.prompt.md"
  - ".github/prompts/connect-integration-graphs.prompt.md"
  - ".github/prompts/craft-prompt.prompt.md"
  - ".github/prompts/deep-search.prompt.md"
  - ".github/prompts/del-project-context.prompt.md"
  - ".github/prompts/eval-workflows.prompt.md"
  - ".github/prompts/health.prompt.md"
  - ".github/prompts/implement.prompt.md"
  - ".github/prompts/init-context.prompt.md"
  - ".github/prompts/plan.prompt.md"
  - ".github/prompts/review.prompt.md"
  - ".github/prompts/strategic-review.prompt.md"
  - ".github/prompts/validate.prompt.md"
  - ".github/prompts/visualize-graph.prompt.md"
  - ".github/prompts/ctx-status.prompt.md"
  - ".github/prompts/ctx-doctor.prompt.md"
  - ".github/prompts/ctx-insight.prompt.md"
  - ".github/prompts/ctx-resume.prompt.md"
  - ".github/prompts/ctx-checkpoint.prompt.md"
  - ".github/prompts/ctx-start.prompt.md"
  - "tests/governance_audit/test_utility_slash_prompts_bypass.py"
  - "tests/governance_audit/test_root_orchestrator_silent_execution_governance.py"
---

## 1. Contexto e Motivacao (Evolucao v1 -> v2)
# Plano de Manutencao de Governanca (v2) — Bypass Universal de @agent-router para Slash Prompts Explicitos


Na **v1** deste plano, foi formalizado o Fast-Path restrito apenas aos **6 Slash Prompts utilitarios da familia `ctx-*`** (`ctx-status`, `ctx-doctor`, `ctx-insight`, `ctx-resume`, `ctx-checkpoint` e `ctx-start`) via metadado `router_bypass: utility`.

Contudo, a execucao de `/craft-prompt` e a inspecao integral dos demais Slash Prompts em `.github/prompts/*.prompt.md` demonstraram que **todos os outros 15 Slash Prompts explicitos do repositorio** (exceto `/agent-router`) continuavam acionando indevidamente o `@agent-router` na entrada. Quando o usuario invoca explicitamente qualquer Slash Prompt (`.github/prompts/<nome>.prompt.md` via `Follow instructions in [<nome>.prompt.md](.../<nome>.prompt.md)`), **exceto `/agent-router`**, o comando ja foi selecionado pelo usuario e possui seu proprio fluxo deterministico; portanto, o Orquestrador Raiz **NUNCA deve invocar `@agent-router`** na triagem inicial, devendo executar diretamente o fluxo/subagente determinado pelo proprio `.prompt.md`.

## 2. Diagnostico Completo da Causa Raiz

### 2.1. Por que `craft-prompt.prompt.md` (e os demais Slash Prompts exceto `agent-router.prompt.md`) acionaram `@agent-router` na entrada?

- Na v1, a excecao normativa em **R-037** e **R-063** em `CLAUDE.md` e `.github/copilot-instructions.md` cobria exclusivamente `ctx-*.prompt.md` (`router_bypass: utility`).
- Como `craft-prompt.prompt.md` e os demais 14 Slash Prompts nao-`ctx-*` rodam sob `agent: 'agent'` (Orquestrador Raiz) e carregam `CLAUDE.md` e `.github/copilot-instructions.md` em `source_docs`, o Orquestrador Raiz verificava que o prompt nao era `ctx-*` e aplicava literalmente a clausula de R-037/R-063 invocando `@agent-router` via `run_subagent` antes de iniciar o fluxo do proprio prompt.

### 2.2. Por que em `craft-prompt.prompt.md` apareceu tambem `codegraph-engine: Mapear frontmatter tools e naming de planos`?

- A leitura integral de `.github/prompts/craft-prompt.prompt.md` comprova que **o proprio `craft-prompt.prompt.md` determina expressamente invocar `@codegraph-engine` via `run_subagent` na Etapa 2 (`Etapa 2: Mineracao de Contexto e Grounding (@codegraph-engine)`)** do `WORKFLOW-PROMPT-SYNTHESIS`.
- Na secao `Checklist Antes de Apresentar` de `craft-prompt.prompt.md` consta literalmente: `- [ ] Subagente @codegraph-engine invocado formalmente via run_subagent na Etapa 2 (zero scripts manuais no sandbox).`
- Portanto, a chamada a `@codegraph-engine` para mapear frontmatter tools e naming de planos **faz parte legitima e intencional do Passo 2 de `craft-prompt.prompt.md`** (grounding deterministico no repositorio), enquanto a chamada inicial a `@agent-router` foi um desvio redundante causado pela ausencia de `router_bypass` nos prompts fora de `ctx-*`.

### 2.3. Como funciona cada Slash Prompt em `.github/prompts/*.prompt.md` e sua classificacao `router_bypass`

| Arquivo (`.github/prompts/`) | Comando | Funcionamento quando invocado via `/nome-do-prompt` | Subagentes acionados pelo proprio prompt | Classificacao `router_bypass` |
|---|---|---|---|---|
| `agent-router.prompt.md` | `/agent-router` | Ponto de entrada explicito para classificar intencao e delegar via `@agent-router` (com Health Check R-034 e Prompt Structuring R-041). | `@agent-router` (`@binding-initializer`, `@prompt-structuring`) | **Sem bypass** (unico prompt que invoca `@agent-router`) |
| `add-project-context.prompt.md` | `/add-project-context` | Valida binding context (R-034/R-043), delega scanner de stack ao `@adapter-generator` (Fase 1), confirma perfil via `ask_questions` e registra projeto em `projects.local.yaml`. | `@adapter-generator`, `@binding-initializer` | `router_bypass: slash_workflow` |
| `commit.prompt.md` | `/commit` | Inspeciona `git status`/`git diff` em lote via `context-mode` (read-only), valida atomicidade e gera mensagem Conventional Commits em PT-BR sem subagent. | Nenhum (utilitario read-only) | `router_bypass: utility` |
| `connect-integration-graphs.prompt.md` | `/connect-integration-graphs` | Mapeia fronteiras multi-repo (`manifesto.boundaries`) em `.codegraphrc.json` delegando a Fase 1 a `@tech-solution-architect` e a Fase 2 a `@codegraph-engine`. | `@tech-solution-architect`, `@codegraph-engine` | `router_bypass: slash_workflow` |
| `craft-prompt.prompt.md` | `/craft-prompt` | Executa o `WORKFLOW-PROMPT-SYNTHESIS` em 5 etapas: Elicitacao (`ask_questions`), Grounding obrigatorio no codebase via `@codegraph-engine` (Passo 2), Restricoes, Sintese e Emissao do bloco Markdown. | `@codegraph-engine` (Passo 2) | `router_bypass: slash_workflow` |
| `deep-search.prompt.md` | `/deep-search` | Executa pesquisa profunda multi-hop (codigo local + docs externas) delegando diretamente ao `@deep-researcher`. | `@deep-researcher` | `router_bypass: slash_workflow` |
| `del-project-context.prompt.md` | `/del-project-context` | Lista projetos de `projects.local.yaml`, confirma remocao via `ask_questions` e limpa artefatos locais do projeto. | Nenhum / fluxo guiado local | `router_bypass: slash_workflow` |
| `eval-workflows.prompt.md` | `/eval-workflows` | Executa bateria deterministica de avaliacao de casos de roteamento e workflows em `.github/agents/evals/`. | `@agent-auditor` / suite de evals | `router_bypass: slash_workflow` |
| `health.prompt.md` | `/health` | Executa diagnostico read-only de integridade do repositorio de governanca, catalogos e binding context. | Nenhum (diagnostico read-only) | `router_bypass: utility` |
| `implement.prompt.md` | `/implement` | Executa implementacao guiada por plano previamente aprovado em `docs/plans/`, delegando diretamente aos subagentes executores do plano. | Subagentes executores do plano aprovado | `router_bypass: slash_workflow` |
| `init-context.prompt.md` | `/init-context` | Inicializa ou repara o binding context e `projects.local.yaml` delegando a `@binding-initializer` / `@adapter-generator`. | `@binding-initializer`, `@adapter-generator` | `router_bypass: slash_workflow` |
| `plan.prompt.md` | `/plan` | Cria plano detalhado com DAG de dependencias e persiste em `docs/plans/<tipo>/` via `@docs-engineer` ou `@governance-maintainer` (R-064). | `@docs-engineer`, `@governance-maintainer` | `router_bypass: slash_workflow` |
| `review.prompt.md` | `/review` | Executa code review estruturado das alteracoes ativas delegando a `@code-review` / `@pr-gatekeeper`. | `@code-review`, `@pr-gatekeeper` | `router_bypass: slash_workflow` |
| `strategic-review.prompt.md` | `/strategic-review` | Executa revisao arquitetural/estrategica multi-perspectiva sobre design e trade-offs. | Consultores arquiteturais / `@tech-solution-architect` | `router_bypass: slash_workflow` |
| `validate.prompt.md` | `/validate` | Valida conformidade de implementacao/governanca frente ao plano e invariantes. | Validadores / auditoria | `router_bypass: slash_workflow` |
| `visualize-graph.prompt.md` | `/visualize-graph` | Consulta e gera visualizacao do grafo de codigo via `@codegraph-engine`. | `@codegraph-engine` | `router_bypass: slash_workflow` |
| `ctx-*.prompt.md` (6 arquivos) | `/ctx-*` | Utilitarios de sessao/diagnostico do Context Mode (`ctx-status`, `ctx-doctor`, `ctx-insight`, `ctx-resume`, `ctx-checkpoint`, `ctx-start`). | Nenhum (Fast-Path MCP de sessao) | `router_bypass: utility` (ja aplicado na v1) |

## 3. Fases de Execucao Detalhadas (Plano v2)

### Fase 1 — Excecao Canonica Universal de Slash Prompts Explicitos em `CLAUDE.md`, `.github/copilot-instructions.md` e `invariantes-e-protocolos.md`

1. Atualizar **R-037** e **R-063** em `CLAUDE.md`, `.github/copilot-instructions.md` e `.github/agents/workflows/invariantes-e-protocolos.md` (e `docs/ai-copilot/invariantes-e-protocolos.md` se aplicavel) para estabelecer:
   - Quando o usuario invoca explicitamente qualquer Slash Prompt (`.github/prompts/<nome>.prompt.md` via `Follow instructions in [<nome>.prompt.md](.../<nome>.prompt.md)`), **exceto `/agent-router` (`agent-router.prompt.md`)**, o comando ja foi selecionado pelo usuario e possui seu proprio fluxo deterministico; portanto, o Orquestrador Raiz **NUNCA deve invocar `@agent-router`** na triagem inicial, devendo executar diretamente o fluxo/subagente determinado pelo proprio `.prompt.md` (`router_bypass: utility` ou `router_bypass: slash_workflow` / `direct`).
   - Para qualquer solicitacao em chat livre (sem Slash Prompt explicito ou via `/agent-router`), a passagem inicial por `@agent-router` via `run_subagent` permanece 100% obrigatoria (R-037 / R-063).

### Fase 2 — Guard Defensivo em `.github/agents/agent-router.agent.md` e `templates/router-agent.md`

1. Adicionar Guard Defensivo em `.github/agents/agent-router.agent.md` e `.github/agents/templates/router-agent.md` (e `templates/router-agent.md`):
   - Caso `@agent-router` seja invocado acidentalmente com um payload de Slash Prompt explicito (`router_bypass` / `Follow instructions in [<nome>.prompt.md]`, exceto `agent-router.prompt.md`), devolver imediatamente a execucao direta do prompt ao Orquestrador Raiz sem reclassificar nem redirecionar para outro fluxo.

### Fase 3 — Atualizacao dos 15 Slash Prompts Nao-`ctx-*` (e Template Canonico `.github/prompts/templates/prompt-template.md`)

1. Adicionar `router_bypass` no frontmatter YAML e diretriz explicita no corpo proibindo invocar `@agent-router` na entrada em todos os 15 prompts nao-`ctx-*` (mantendo os 6 `ctx-*` já configurados, totalizando 21 prompts com `router_bypass`):
   - `router_bypass: utility`: `commit.prompt.md`, `health.prompt.md` (alem dos 6 `ctx-*.prompt.md`).
   - `router_bypass: slash_workflow`: `add-project-context.prompt.md`, `connect-integration-graphs.prompt.md`, `craft-prompt.prompt.md`, `deep-search.prompt.md`, `del-project-context.prompt.md`, `eval-workflows.prompt.md`, `implement.prompt.md`, `init-context.prompt.md`, `plan.prompt.md`, `review.prompt.md`, `strategic-review.prompt.md`, `validate.prompt.md`, `visualize-graph.prompt.md`.
2. Atualizar `.github/prompts/templates/prompt-template.md` documentando `router_bypass: utility | slash_workflow | direct`.

### Fase 4 — Blindagem Deterministica em Testes (`pytest`)

1. Atualizar `tests/governance_audit/test_utility_slash_prompts_bypass.py` e `tests/governance_audit/test_root_orchestrator_silent_execution_governance.py` para validar:
   - Que todos os 21 Slash Prompts (exceto `agent-router.prompt.md`) possuem `router_bypass` no frontmatter e proíbem acionar `@agent-router`;
   - Que `agent-router.prompt.md` NAO possui `router_bypass`;
   - Que `.github/agents/agent-router.agent.md` declara o Guard Defensivo de `router_bypass`;
   - Que `CLAUDE.md` e `.github/copilot-instructions.md` preservam 100% das invariantes R-037 e R-063 para solicitacoes em chat livre.

## 4. Portao de Reuso Sistemico Obrigatorio (R-055)

- **Q1 (Pares)**: Cobertura integral dos 22 arquivos `.github/prompts/*.prompt.md` (15 prompts de workflow/utilitarios + 6 `ctx-*` com `router_bypass`, e `agent-router.prompt.md` sem bypass).
- **Q2 (Templates)**: Atualizacao sincronizada de `.github/prompts/templates/prompt-template.md` e `.github/agents/templates/router-agent.md`.
- **Q3 (Testes)**: Validacao automatizada em `tests/governance_audit/test_utility_slash_prompts_bypass.py` e `tests/governance_audit/test_root_orchestrator_silent_execution_governance.py`.

## 5. Plano de Rollback e Criterios de Aceite

- **Rollback**: Reversao atomica via `git checkout -- CLAUDE.md .github/ docs/ tests/` caso qualquer teste da suite `pytest tests/governance_audit/` apresente regressao.
- **Criterios de Aceite**:
  - [x] Excecao Canonica de Slash Prompts Explicitos (`router_bypass`) documentada em R-037 e R-063 (`CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows/invariantes-e-protocolos.md`).
  - [x] Guard Defensivo adicionado em `.github/agents/agent-router.agent.md` e `.github/agents/templates/router-agent.md`.
  - [x] Todos os 21 Slash Prompts (exceto `agent-router.prompt.md`) configurados com `router_bypass` e proibicao expressa de acionar `@agent-router`.
  - [x] `pytest tests/governance_audit/` com 100% de aprovacao (0 falhas).
