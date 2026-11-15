---
title: "Consolidação de Guardrails Proporcionais por Agency Score (0-3) e Suíte Regressiva Two-Tier (OWASP ASI 2026)"
status: COMPLETED
approved: true
author: "@agent-auditor"
plan_type: governance
workflow: WORKFLOW-GOVERNANCE-MAINTENANCE
created_at: "2026-11-15T12:00:00Z"
related-planning-doc: "N/A"
review_verdict: PASS
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: PASS
allowed_files:
  - .github/skills/agent-safety-guardrails/SKILL.md
  - .github/skills/agent-safety-guardrails/references/agency-score-matrix.md
  - .github/skills/governance-audit-patterns/SKILL.md
  - .github/agents/agent-auditor.agent.md
  - .github/agents/governance-factory.agent.md
  - .github/agents/deep-search.agent.md
  - .github/agents/templates/agent-template.md
  - .github/agents/templates/research-agent.md
  - tests/governance_audit/test_agent_guardrails_regression.py
  - tests/governance_audit/test_ctx_execute_capability_profile.py
  - docs/plans/governance/20261115-120000-guardrails-agency-score-regression.md
rollback_plan:
  - git checkout -- .github/skills/agent-safety-guardrails/SKILL.md .github/skills/governance-audit-patterns/SKILL.md .github/agents/agent-auditor.agent.md .github/agents/governance-factory.agent.md .github/agents/deep-search.agent.md .github/agents/templates/agent-template.md .github/agents/templates/research-agent.md tests/governance_audit/test_ctx_execute_capability_profile.py
  - rm -f .github/skills/agent-safety-guardrails/references/agency-score-matrix.md tests/governance_audit/test_agent_guardrails_regression.py
---

# Plano de Governança: Consolidação de Guardrails Proporcionais por Agency Score (0-3) e Suíte Regressiva Two-Tier (OWASP ASI 2026)

## 1. Contexto e Diagnóstico Regressivo dos 63 Agents Atuais

A auditoria regressiva sobre os **63 contratos `.agent.md`** ativos em `.github/agents/` avaliou a cobertura de guardrails operacionais e de segurança frente ao framework **OWASP Top 10 for Agentic Applications (ASI01..ASI10 — 2026)** e ao modelo de **Proportional Guardrailing por Agency Score (0 a 3)**.

### 1.1 Classificação Completa dos 63 `.agent.md` por Agency Score

| Agency Score | Perfil de Agência e Superfície de Ferramentas | Qtd | Agents Classificados |
| :--- | :--- | :---: | :--- |
| **Score 0** | **Read-Only / Analítico / Planejador / Crítico** (sem `ctx_execute` e sem `run_in_terminal` — perfil R-025 / R-064) | **17** | `adr-sentinel`, `angular-arch-advisor`, `compliance-guardrails`, `database-arch-advisor`, `devops-engineer`, `ejb-arch-advisor`, `feature-planner`, `plan-critic`, `prompt-structuring`, `python-arch-advisor`, `react-arch-advisor`, `repo-hygiene-auditor`, `requirements-analyst`, `spring-boot-arch-advisor`, `spring-reactive-arch-advisor`, `struts-arch-advisor`, `test-strategy` |
| **Score 1** | **Roteador / Supervisor** (delegação via `run_subagent`, `CLAUSE_OTEL_PASSTHROUGH`, sem mutação direta — R-054) | **9** | `agent-router`, `angular-router`, `database-router`, `ejb-router`, `python-router`, `react-router`, `spring-boot-router`, `spring-reactive-router`, `struts-router` |
| **Score 2** | **Retriever Web / Externo** (ingestão de fontes externas não confiáveis + perfil Gather-only `ctx_batch`/`ctx_search`/`ctx_index`) | **1** | `deep-search` |
| **Score 3** | **Executor / Mutação** (execução via `ctx_execute` e/ou `run_in_terminal`, mutação em sandbox, git, MCP ou infraestrutura) | **36** | `adapter-generator`, `agent-auditor`, `angular-developer`, `angular-test-engineer`, `binding-initializer`, `bug-triage`, `business-rules-extractor`, `code-review`, `code-style-enforcer`, `codegraph-engine`, `database-specialist`, `ddd-bounded-context-mapper`, `debugger`, `docs-engineer`, `ejb-developer`, `ejb-test-engineer`, `governance-factory`, `governance-maintainer`, `informix-database-specialist`, `oracle-database-specialist`, `performance-agent`, `pr-gatekeeper`, `python-developer`, `python-test-engineer`, `react-developer`, `react-test-engineer`, `refactor-planner`, `runtime-verifier`, `security-reviewer`, `spring-boot-developer`, `spring-boot-test-engineer`, `spring-reactive-developer`, `spring-reactive-test-engineer`, `struts-developer`, `struts-test-engineer`, `tech-solution-architect` |
| **Total** | **Catálogo Canônico de Agents (`.github/agents/*.agent.md`)** | **63** | **100% dos agents mapeados** |

### 1.2 Diagnóstico de Gaps Reais (Verificados contra a Fonte Real)

1. **Gap G2 — Hardening ASI01/ASI06 e Terminal Read-Only em `deep-search.agent.md` (Score 2)**:
   - O agent `@deep-search` opera com perfil **Gather-only** (`context-mode/ctx_batch`, `context-mode/ctx_search`, `context-mode/ctx_index`, `web/fetch`, sem `ctx_execute` — validado por `tests/governance_audit/test_ctx_execute_capability_profile.py`).
   - Embora já possua diretrizes de não executar comandos destrutivos, carece de cláusula explícita de **isolamento de conteúdo externo não confiável (OWASP ASI01 — Agent Goal Hijacking / Indirect Prompt Injection e OWASP ASI06 — Memory & Context Poisoning)** antes de indexar dados via `ctx_index` e de restrição explícita de uso exclusivo de comandos read-only em `ctx_batch`.
2. **Gap G3 (Esclarecimento Factual — Falso Positivo Descartado)**:
   - Os 14 agents citados em análises preliminares já herdam o bloco canônico `<execution_protocol>` sincronizado com **R-046 (Subagent-Scoped Hooks)**, **R-059 (Plan-Then-Batch)**, **R-060 (Teto Rígido de Tool Turns <= 5 e Circuit Breaker)** e gates **HITL**. Portanto, não há necessidade de mutação em massa nos 63 contratos, evitando churn desnecessário.
3. **Gap G4 — Ausência de Suíte Regressiva `pytest` de Guardrails por Agency Score**:
   - A suíte `tests/governance_audit/` valida contratos estruturais e perfis de `ctx_execute`, mas não possui um teste regressivo dedicado (`test_agent_guardrails_regression.py`) que garanta invariantes por **Agency Score (0, 1, 2, 3)** sobre todos os 63 agents (frontmatter, presença de `<execution_protocol>`, proibições de escrita em Score 0, passthrough em Score 1, isolamento ASI01/ASI06 em Score 2 e limites de execução em Score 3).
4. **Gap G5 — Ausência de Matriz Normativa Agency Score ↔ OWASP ASI01..ASI10 nas Skills, Agents de Governança e Templates**:
   - A skill `.github/skills/agent-safety-guardrails/SKILL.md` (atualmente com 266 linhas, próxima ao teto de 300 linhas da R-066) e `.github/skills/governance-audit-patterns/SKILL.md` não formalizam a matriz **Agency Score (0–3) ↔ OWASP ASI01..ASI10** nem o padrão de **Two-Tier Guardrailing** (Tier 1 determinístico em `pytest`/pre-commit + Tier 2 semântico via `@agent-auditor` e `@plan-critic`).
   - Os templates `.github/agents/templates/agent-template.md` e `.github/agents/templates/research-agent.md`, bem como `.github/agents/agent-auditor.agent.md` e `.github/agents/governance-factory.agent.md`, precisam incorporar a classificação obrigatória por Agency Score no nascimento e na auditoria de qualquer agent.

---

## 2. Alternativas Avaliadas e Decisão Arquitetural

| Critério | Opção 1 (Recomendada): Evolução Incremental de Skills + Templates + Suíte `pytest` (Zero Agent Sprawl) | Opção 2: Criação de Novo Agent Dedicado (`@guardrail-auditor`) | Opção 3: Edição Manual em Massa nos 63 `.agent.md` |
| :--- | :--- | :--- | :--- |
| **Aderência a R-055 / Smell 2.5** | **Alta** — reutiliza `@deep-search`, `@agent-auditor` e `@governance-factory` sem inflar o catálogo de 63 agents. | **Baixa** — viola Smell 2.5 (Agent Sprawl) criando sobreposição direta com `@agent-auditor`. | **Média** — não cria agent, mas gera alto risco de regressão e conflito de merge em 63 arquivos. |
| **Custo de Contexto (R-066)** | **Ótimo** — aplica Progressive Disclosure extraindo a matriz detalhada para `references/agency-score-matrix.md`, mantendo `SKILL.md <= 300` linhas. | **Alto** — adiciona novo contrato, roteamento em `audit-router` e entradas em `catalog.yaml`. | **Alto** — aumenta o tamanho médio dos prompts de sistema sem ganho real (pois `<execution_protocol>` já está presente). |
| **Garantia Determinística** | **Alta** — institui Tier 1 automatizado via `tests/governance_audit/test_agent_guardrails_regression.py`. | **Baixa** — dependeria apenas de revisão LLM sem gate determinístico em CI. | **Média** — sem teste regressivo dedicado, a conformidade degradaria em futuras edições. |

**Decisão**: Adotar a **Opção 1**, evoluindo as skills normativas com Progressive Disclosure (R-066), endurecendo o contrato Score 2 (`deep-search.agent.md`), atualizando os agents/templates de governança (`agent-auditor`, `governance-factory`, `agent-template.md`, `research-agent.md`) e instituindo o gate determinístico `test_agent_guardrails_regression.py`.

---

## 3. Ondas de Execução Planejadas (B1 → B2 → B3)

Cada onda será validada incrementalmente com `pytest tests/governance_audit -q` e `get_errors` agrupado (R-051).

### Onda B1 — Evolução das Skills Normativas (Progressive Disclosure R-066)

1. **Criar `.github/skills/agent-safety-guardrails/references/agency-score-matrix.md`**:
   - Formalizar a escala **Agency Score (0 a 3)**:
     - **Score 0 (Read-Only / Analítico / Crítico — 18 agents)**: proibição de escrita/mutação (R-025), materialização delegada a `@docs-engineer`/`@governance-maintainer` (R-064), proteção contra sobreconfiança e alucinação (ASI09).
     - **Score 1 (Roteador / Supervisor — 9 agents)**: delegação estrita via `run_subagent`, `CLAUSE_OTEL_PASSTHROUGH`, proibição de chamadas `context-mode` no `@agent-router` (R-054), prevenção de loops/cascading failures (ASI08) e rogue routing (ASI07/ASI10).
     - **Score 2 (Retriever Web / Externo — 1 agent: `@deep-search`)**: perfil Gather-only (`ctx_batch`, `ctx_search`, `ctx_index`, sem `ctx_execute`), sanitização e marcação de conteúdo externo como dado inerte não confiável antes de `ctx_index` (ASI01 — Indirect Prompt Injection; ASI06 — Context Poisoning) e comandos estritamente read-only em `ctx_batch` (ASI02/ASI05).
     - **Score 3 (Executor / Mutação — 35 agents)**: escrita restrita a `allowed_files` (R-046/R-064), execução consolidada Plan-Then-Batch (R-059), teto de 5 turnos e Circuit Breaker (R-060), proibição de comandos destrutivos sem HITL (ASI02/ASI05) e privilégio mínimo (ASI03).
   - Mapear explicitamente **OWASP ASI01..ASI10 (2026)** para cada Score e definir a arquitetura **Two-Tier Guardrailing** (Tier 1: `pytest` estático/estrutural; Tier 2: auditoria semântica por `@agent-auditor` e `@plan-critic`).
2. **Atualizar `.github/skills/agent-safety-guardrails/SKILL.md`**:
   - Adicionar seção enxuta referenciando `references/agency-score-matrix.md` para a Matriz Agency Score (0–3) e Two-Tier Guardrailing, mantendo o arquivo estritamente **<= 300 linhas** (R-066).
3. **Atualizar `.github/skills/governance-audit-patterns/SKILL.md`**:
   - Incluir a verificação de **Proportional Guardrailing por Agency Score (0–3)** e conformidade com a suíte `test_agent_guardrails_regression.py` no checklist de auditoria estática de contratos `.agent.md`.
4. **Validação da Onda B1**:
   - Executar `pytest tests/governance_audit -q` (garantindo inclusive conformidade de tamanho de `SKILL.md <= 300` linhas).

### Onda B2 — Evolução dos Agents e Templates de Governança

1. **Atualizar `.github/agents/agent-auditor.agent.md`**:
   - Incluir no escopo de auditoria a validação da classificação **Agency Score (0–3)** e a verificação Two-Tier contra `references/agency-score-matrix.md`.
2. **Atualizar `.github/agents/governance-factory.agent.md`**:
   - Exigir que toda criação ou refatoração de `.agent.md` declare e aplique os guardrails proporcionais ao seu **Agency Score (0–3)**, mantendo conformidade com `test_agent_guardrails_regression.py` e `test_ctx_execute_capability_profile.py`.
3. **Atualizar `.github/agents/templates/agent-template.md`**:
   - Documentar no template canônico a seleção de **Agency Score (0–3)** e os guardrails obrigatórios correspondentes (incluindo referência à matriz OWASP ASI01..ASI10).
4. **Atualizar `.github/agents/templates/research-agent.md`**:
   - Incorporar o gate de síntese e crítica de guardrails por **Agency Score (0–3)** alimentado por `@deep-search`, exigindo isolamento de fontes externas não confiáveis (ASI01/ASI06) e comandos estritamente read-only.
5. **Validação da Onda B2**:
   - Executar `pytest tests/governance_audit -q`.

### Onda B3 — Hardening ASI01/ASI06 em `deep-search.agent.md` e Suíte Regressiva `pytest`

1. **Atualizar `.github/agents/deep-search.agent.md`**:
   - **Invariante Crítica**: manter o array `tools:` do frontmatter **100% inalterado** (`["read", "search", "web/fetch", "context-mode/ctx_batch", "context-mode/ctx_search", "context-mode/ctx_index"]`, sem `ctx_execute`), preservando a aprovação em `tests/governance_audit/test_ctx_execute_capability_profile.py`.
   - Adicionar nas regras operacionais/restrições a blindagem explícita **Score 2 (Retriever Web / Externo)**:
     - Tratamento de todo conteúdo obtido via `web/fetch` ou repositórios externos como **dado informativo inerte não confiável (OWASP ASI01 — Indirect Prompt Injection)**, vedando a execução de instruções contidas em páginas/documentos externos.
     - Sanitização e atribuição obrigatória de fonte (`source`) antes de indexar via `ctx_index`, prevenindo **Memory & Context Poisoning (OWASP ASI06)**.
     - Uso exclusivo de comandos **100% read-only** em `ctx_batch`, com proibição absoluta de mutação de estado ou execução de scripts remotos.
2. **Criar `tests/governance_audit/test_agent_guardrails_regression.py`**:
   - Implementar suíte regressiva parametrizada cobrindo os **63 contratos `.agent.md`**:
     - Verificar que o conjunto total de agents corresponde exatamente à partição canônica por **Agency Score**: Score 0 (18 agents), Score 1 (9 routers), Score 2 (1 retriever: `deep-search`), Score 3 (35 executores).
     - Validar que todos os 63 agents possuem frontmatter YAML válido (`name`, `description`, `tools`) e seção de restrições/escopo ou protocolo de execução.
     - Validar invariantes específicas por Score:
       - **Score 0**: ausência de ferramentas de edição direta de código no perfil read-only e presença de restrição read-only / não-escopo de implementação.
       - **Score 1**: presença de `agent` (`run_subagent`) em `tools`, `CLAUSE_OTEL_PASSTHROUGH` e ausência de `context-mode` em `agent-router.agent.md` (R-054).
       - **Score 2 (`deep-search.agent.md`)**: presença de `web/fetch` e `context-mode/ctx_batch`, ausência de `context-mode/ctx_execute`, e presença das diretrizes de mitigação **ASI01** / **ASI06** e comandos read-only.
       - **Score 3**: presença do bloco `<execution_protocol>` com **Plan-Then-Batch (R-059)** e **Circuit Breaker / Teto de Tool Turns (R-060)**.
     - Validar a existência física de `.github/skills/agent-safety-guardrails/references/agency-score-matrix.md` e que `.github/skills/agent-safety-guardrails/SKILL.md` respeita o teto de **<= 300 linhas** (R-066).
3. **Validação da Onda B3**:
   - Executar `pytest tests/governance_audit -q` (incluindo `test_agent_guardrails_regression.py` e `test_ctx_execute_capability_profile.py`).

---

## 4. Systemic Reuse Gate (R-055)

- **Q1 — Existe agent, skill ou ferramenta existente que já resolva total ou parcialmente o problema?**
  - **Sim.** A pesquisa web/externa já é atendida por `@deep-search`, a auditoria estática de contratos por `@agent-auditor`, a criação/padronização de contratos por `@governance-factory` e as diretrizes de segurança por `.github/skills/agent-safety-guardrails/SKILL.md` e `.github/skills/governance-audit-patterns/SKILL.md`.
- **Q2 — Por que evoluir os artefatos existentes em vez de criar um novo agent ou skill?**
  - Criar um novo agent (ex.: `@guardrail-auditor`) violaria diretamente o anti-padrão **Smell 2.5 (Agent Sprawl)** e duplicaria responsabilidades de `@agent-auditor`. Criar uma nova skill fragmentaria a fonte única de verdade de segurança agentic (`agent-safety-guardrails`). O uso de **Progressive Disclosure (R-066)** via `references/agency-score-matrix.md` permite expandir a cobertura normativa sem ultrapassar o limite de 300 linhas do `SKILL.md`.
- **Q3 — Como a solução garante reutilização sistêmica para futuros agents?**
  - A atualização simultânea dos templates (`agent-template.md` e `research-agent.md`), do criador (`governance-factory`), do auditor (`agent-auditor`) e do teste automatizado Tier 1 (`test_agent_guardrails_regression.py`) garante que qualquer novo agent criado no repositório nasça classificado por **Agency Score (0–3)** e seja validado continuamente em CI.

---

## 5. Riscos, Plano de Rollback (1:1) e Critérios de Aceitação Verificáveis

### 5.1 Matriz de Riscos e Mitigações

| Risco | Impacto | Mitigação |
| :--- | :---: | :--- |
| Estouro do limite de 300 linhas em `agent-safety-guardrails/SKILL.md` (R-066) | Alto (quebra CI) | Extrair a matriz detalhada para `references/agency-score-matrix.md` e manter apenas resumo executivo e link no `SKILL.md`. |
| Quebra de `test_ctx_execute_capability_profile.py` ao editar `deep-search.agent.md` | Alto (quebra CI) | Manter o frontmatter `tools:` de `deep-search.agent.md` inalterado (sem `ctx_execute`), restringindo a edição ao corpo normativo. |
| Falsos positivos em `test_agent_guardrails_regression.py` | Médio | Basear as asserções nos contratos reais dos 63 agents auditados e executar toda a suíte `tests/governance_audit` ao fim de cada onda. |

### 5.2 Plano de Rollback Determinístico (1:1 por Arquivo — Sem `git clean -fd`)

Em caso de falha não recuperável durante a execução das ondas B1–B3, reverter exclusivamente os artefatos do escopo autorizado:

```bash
git checkout -- \
  .github/skills/agent-safety-guardrails/SKILL.md \
  .github/skills/governance-audit-patterns/SKILL.md \
  .github/agents/agent-auditor.agent.md \
  .github/agents/governance-factory.agent.md \
  .github/agents/deep-search.agent.md \
  .github/agents/templates/agent-template.md \
  .github/agents/templates/research-agent.md \
  tests/governance_audit/test_ctx_execute_capability_profile.py

rm -f \
  .github/skills/agent-safety-guardrails/references/agency-score-matrix.md \
  tests/governance_audit/test_agent_guardrails_regression.py
```

### 5.3 Critérios de Aceitação Verificáveis

1. `references/agency-score-matrix.md` criado com a matriz completa **Agency Score (0–3) ↔ OWASP ASI01..ASI10** e definição de **Two-Tier Guardrailing**.
2. `.github/skills/agent-safety-guardrails/SKILL.md` e `.github/skills/governance-audit-patterns/SKILL.md` atualizados e com **<= 300 linhas** cada (R-066).
3. `agent-auditor.agent.md`, `governance-factory.agent.md`, `agent-template.md` e `research-agent.md` atualizados com referências explícitas ao Agency Score (0–3).
4. `deep-search.agent.md` endurecido contra **ASI01 (Indirect Prompt Injection)** e **ASI06 (Context Poisoning)**, preservando o perfil Gather-only (`ctx_batch` sem `ctx_execute`).
5. `tests/governance_audit/test_agent_guardrails_regression.py` criado e passando 100% junto com toda a suíte `pytest tests/governance_audit -q`.

---

## 6. Parecer do Revisor Cético Pré-HITL (R-064)

- **Reviewer**: `@plan-critic`
- **Review Verdict**: `PASS`
- **Review Rounds**: `2`
- **Review Tier 1**: `PASS`
- **Síntese da Revisão**:
  - **Round 1 → Round 2**: Ajustado o diagnóstico do Gap G3 (confirmado que os 14 agents já possuem `<execution_protocol>` sincronizado com R-046/R-059/R-060/HITL, eliminando edições desnecessárias fora do `allowed_files`), preservado o perfil Gather-only de `@deep-search` (sem `ctx_execute` para não violar `test_ctx_execute_capability_profile.py`), garantido o respeito ao teto de 300 linhas de `SKILL.md` via Progressive Disclosure (`references/agency-score-matrix.md`) e especificado rollback 1:1 sem `git clean -fd`.
  - **Status Pré-HITL**: Plano apto para submissão ao Gate de Aprovação Humana (R-027 / R-064) com `status: DRAFT` e `approved: false`.
