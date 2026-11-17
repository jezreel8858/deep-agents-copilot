---
plan_id: "gov-ctx-execute-profile-revisao-20261117"
plan_type: "governance"
intencao_plano: "hibrido"
status: "APPROVED"
approved: true
author: "@agent-auditor"
materialized_by: "@docs-engineer"
created_at: "2026-11-17"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261117-ctx-execute-profile-revisao-01"
session_id: "sess-20261117-ctx-execute-profile-audit"
related-planning-doc: "docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md"
parent_plan_ref: "docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md"
review_verdict: "PASS_WITH_WARNINGS"
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: "PASS"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 0
  minors: 1
  nits: 2
  last_verdict: "PASS_WITH_WARNINGS"
  author_ref: "@agent-auditor"
post_exec_review_verdict: "PASS_WITH_WARNINGS"
post_exec_reviewer: "@agent-auditor"
post_exec_reviewed_at: "2026-11-17"
allowed_files:
  - ".github/agents/database-specialist.agent.md"
  - ".github/agents/agent-auditor.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/adr-sentinel.agent.md"
  - ".github/agents/bug-triage.agent.md"
  - ".github/agents/code-review.agent.md"
  - ".github/agents/code-style-enforcer.agent.md"
  - ".github/agents/compliance-guardrails.agent.md"
  - ".github/agents/debugger.agent.md"
  - ".github/agents/deep-search.agent.md"
  - ".github/agents/devops-engineer.agent.md"
  - ".github/agents/feature-planner.agent.md"
  - ".github/agents/plan-critic.agent.md"
  - ".github/agents/pr-gatekeeper.agent.md"
  - ".github/agents/repo-hygiene-auditor.agent.md"
  - ".github/agents/requirements-analyst.agent.md"
  - ".github/agents/runtime-verifier.agent.md"
  - ".github/agents/security-reviewer.agent.md"
  - ".github/agents/test-strategy.agent.md"
  - ".github/agents/backend/database/database-arch-advisor.agent.md"
  - ".github/agents/backend/ejb/ejb-arch-advisor.agent.md"
  - ".github/agents/backend/python/python-arch-advisor.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md"
  - ".github/agents/backend/struts/struts-arch-advisor.agent.md"
  - ".github/agents/frontend/angular/angular-arch-advisor.agent.md"
  - ".github/agents/frontend/react/react-arch-advisor.agent.md"
  - ".github/agents/README.md"
  - ".github/agents/catalog.yaml"
  - ".github/prompts/validate.prompt.md"
  - ".github/prompts/strategic-review.prompt.md"
  - ".github/prompts/README.md"
  - ".github/prompts/catalog.yaml"
  - ".github/skills/governance-audit-patterns/SKILL.md"
  - ".github/skills/context-mode/SKILL.md"
  - ".github/skills/governance-factory-patterns/SKILL.md"
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - "tools/agent_protocol_sync/sync_execution_protocol.py"
  - "tools/agent_protocol_sync/_execution-protocol-fragment.md"
  - "tools/agent_protocol_sync/protocol_roles.json"
  - "tools/agent_protocol_sync/README.md"
  - "tests/governance_audit/test_ctx_execute_capability_profile.py"
  - "tests/governance_audit/test_context_mode_precedence_governance.py"
  - "tests/governance_audit/test_governance_smells.py"
  - "docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md"
  - "docs/plans/governance/20261117-120000-governance-maintenance-ctx-execute-profile-revisao.md"
---

# Plano de Manutenção de Governança — Revisão Crítica e Calibragem do Perfil de Capacidade `context-mode/ctx_execute` em Agents e Prompts (R-008 / R-054 / R-055 / R-056 / R-064)

> **Workflow Canônico**: `WORKFLOW-GOVERNANCE-MAINTENANCE` (R-050 / R-064)  
> **Autor Intelectual**: `@agent-auditor` (Diagnóstico e Auditoria Crítica — Etapa 1)  
> **Materialização Física**: `@docs-engineer` (Persistência Canônica R-064 — Etapa 2)  
> **Revisão Cética Pré-HITL Concluída (`PASS_WITH_WARNINGS` — Rodada 2/2)**: `@plan-critic` (Etapa 3: `review_tier1: "PASS"`, `review_verdict: "PASS_WITH_WARNINGS"`, `review_rounds: 2`) → Aguardando Gate de Aprovação Humana (Etapa 4) → Execução Segregada: Wave 1 por `@governance-maintainer` / `@docs-engineer` e Wave 2 exclusivamente via Trilha Python R-055 (`@python-router` → 1º `@python-arch-advisor` → 2º `@python-developer` / `@python-test-engineer`) (Etapa 5)

---

## 1. Contexto, Diagnóstico Factual e Análise Crítica (C1)

Este plano responde de forma exaustiva, empírica e verificada em disco ao questionamento do usuário sobre os efeitos colaterais da regra que removeu/restringiu `context-mode/ctx_execute` de um subconjunto de agents e prompts (originada no plano `docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md`), avaliando:
1. Se agents ou prompts que precisam alterar arquivos foram prejudicados;
2. Quais cenários operacionais não foram previstos no corte original;
3. Quais correções estruturais e melhorias sistêmicas devem ser aplicadas.

### 1.1. Diagnóstico Crítico Consolidado (7 Eixos e Achados A1 a A7)

- **Intenção do Plano (`intencao_plano`)**: `"hibrido"` — combina evolução normativa/estrutural de contratos de governança e templates (`sync_execution_protocol.py`, `_execution-protocol-fragment.md`, `protocol_roles.json`, skills e prompts) com calibragem de suíte de testes de auditoria (`tests/governance_audit/`).

#### Eixo 1 — Mito vs. Realidade sobre Agents que Alteram Arquivos (**Achado A1 — Exceção Crítica em `database-specialist`**)
- **Realidade Factual no Catálogo (63 agents)**:
  - **28 agents possuem `context-mode/ctx_execute`** ativo no frontmatter `tools:`, cobrindo **96,5% dos agentes mutadores/computacionais**: todos os `*-developer` (`python-developer`, `spring-boot-developer`, `spring-reactive-developer`, `ejb-developer`, `struts-developer`, `angular-developer`, `react-developer`), todos os `*-test-engineer`, todos os `*-perf-tuner`, `legacy-migration-dev`, `docs-engineer`, `governance-factory`, `governance-maintainer`, `adapter-generator`, `binding-initializer`, `oracle-database-specialist` e `informix-database-specialist`, além dos agentes computacionais Read-Only (`agent-auditor`, `tech-solution-architect`, `performance-agent`, `refactor-planner`, `business-rules-extractor`, `codegraph-engine`, `ddd-bounded-context-mapper`).
  - **10 agents são isentos por R-054** (9 roteadores puros + `prompt-structuring`, que não utilizam ferramentas MCP `context-mode`).
  - **25 agents estão bloqueados sem `ctx_execute`** na lista `GATHER_ONLY_AGENTS` de `tests/governance_audit/test_ctx_execute_capability_profile.py`.
- **Exceção Crítica Encontrada (Achado A1 — `database-specialist`)**:
  - O agente `.github/agents/database-specialist.agent.md` é definido contratualmente em sua descrição e corpo como ***"Perfil híbrido: analisa e implementa migrações/queries"*** (distinto de `database-arch-advisor`, que é o consultor puramente Read-Only da trilha de banco de dados, e par direto de `oracle-database-specialist` e `informix-database-specialist`, que possuem `ctx_execute`).
  - Entretanto, `database-specialist` foi incluído indevidamente na lista `GATHER_ONLY_AGENTS` em `tests/governance_audit/test_ctx_execute_capability_profile.py` (linha 26) e teve `context-mode/ctx_execute` removido de seu frontmatter, não possuindo `ctx_execute` nem ferramentas nativas de escrita (`editFiles`). Como resultado, `database-specialist` ficou **100% incapaz de implementar migrações SQL/Flyway/Liquibase ou scripts de banco**, violando sua missão operacional e R-056.

#### Eixo 2 — Cenário Não Previsto 1: Paradoxo do Runtime Windows Defender/AMSI (`language: "javascript"` vs. `ctx_batch`)
- A diretriz global em `.github/copilot-instructions.md` (§ 6) e `CLAUDE.md` determina que, em ambiente Windows, `ctx_execute` com `language: "javascript"` (`fs`/`path` nativos do Node.js) é o mecanismo preferencial de I/O porque evita spawns repetidos de subprocessos shell/Python interceptados pelo Windows Defender/AMSI (`ETIMEDOUT` / `taskkill`).
- Em contrapartida, `ctx_batch(commands, queries)` executa arrays de comandos shell (`cmd.exe` / `powershell` / utilitários CLI) e realiza indexação textual por busca FTS5.
- **Impacto não previsto**: Ao remover `ctx_execute` dos 24 agents genuinamente Gather-only (como `code-review`, `security-reviewer`, `plan-critic`, `bug-triage`, `*-arch-advisor`), esses agents ficaram restritos a `ctx_batch` (comandos shell leves) + `ctx_search`. Quando precisam inspecionar dezenas de arquivos no Windows ou fazer parsing estruturado preciso (YAML frontmatter, JSON, AST, contagem exata de linhas/bytes para Grounding C1 do `@plan-critic`), o `ctx_batch` via shell é mais lento, propenso a bloqueios do Windows Defender se usar comandos complexos e menos preciso que um script Node.js Read-Only em `ctx_execute`.
- **Calibragem necessária**: Documentar claramente os limites operacionais de `ctx_batch` no Windows e avaliar a criação de um perfil intermediário auditado ou manter `ctx_batch` estritamente com comandos nativos leves documentados por catálogo (sem induzir o agente a tentar usar Node.js onde `ctx_execute` não existe).

#### Eixo 3 — Cenário Não Previsto 2: Esquizofrenia Instrucional nos Agents Gather-Only (**Achado A2**)
- Embora `tools/agent_protocol_sync/sync_execution_protocol.py` injete `CLAUSE_GATHER_ONLY` dentro da tag `<execution_protocol>` para os agentes que só têm `ctx_batch`, **o corpo principal (fora da tag `<execution_protocol>`, especialmente na seção `## CRÍTICO: ESCOPO E NÃO-ESCOPO`)** de múltiplos agents Gather-only (como `code-review.agent.md`, `debugger.agent.md`, `security-reviewer.agent.md`, `devops-engineer.agent.md`, `bug-triage.agent.md`, `database-specialist.agent.md`) **continua ordenando literalmente**:
  - *"O uso de `context-mode` (`ctx_execute`, `ctx_batch`, `ctx_search`, `ctx_index`) é 100% OBRIGATÓRIO para ler e modificar arquivos (R-008 / R-056 / Smell 2.24)."*
  - *"É terminantemente PROIBIDO chamar `ctx_execute` arquivo por arquivo... Toda operação multi-arquivo DEVE ser consolidada em UMA ÚNICA chamada de `ctx_execute` via script iterativo em lote... Executar inspeções compulsoriamente via script no sandbox do `context-mode` (`ctx_batch`, `ctx_execute` (com `file`))"*
- **Consequência prática**: O prompt de sistema do agente ordena que ele use `ctx_execute (com file)`, mas o schema de tools do agente não expõe `ctx_execute`. Isso gera confusão contratual (Esquizofrenia Instrucional), levando o LLM a tentar invocar uma tool inexistente, alucinar parâmetros em `ctx_batch` ou degradar raciocínio.

#### Eixo 4 — Cenário Não Previsto 3: Drift entre Plano Anterior (26 agents), Teste (25 agents), Saída de `database-specialist` (24 agents) e Ausência de `COMPUTE_READONLY_AGENTS` (**Achado A3**)
- No plano histórico `docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md`, afirmou-se que a remoção aplicar-se-ia a **26 agents** (incluindo `docs-engineer`, `agent-auditor` e `tech-solution-architect`).
- Na implementação real em `tests/governance_audit/test_ctx_execute_capability_profile.py`, a docstring ainda menciona *"Lista canônica dos 26 agents"*, mas a constante `GATHER_ONLY_AGENTS` contém **25 agents** (pois `docs-engineer`, `agent-auditor` e `tech-solution-architect` mantiveram `ctx_execute`, enquanto `database-specialist` e `prompt-engineer` entraram na lista).
- **Verdade Factual sobre Fonte Única (SSOT)**: `tests/governance_audit/test_context_mode_precedence_governance.py` (linha 22) e `tests/governance_audit/test_governance_smells.py` (linha 829) **JÁ importam `GATHER_ONLY_AGENTS` como fonte única** a partir de `tests/governance_audit/test_ctx_execute_capability_profile.py` (não existe constante `NO_CTX_EXECUTE_AGENTS` duplicada).
- O problema real em **A3** consiste exclusivamente em:
  1. **Presença indevida de `database-specialist` em `GATHER_ONLY_AGENTS`**: reduzindo a lista canônica de **25 para 24 agents**;
  2. **Drift documental com o plano histórico `20261003-090000`** e com a docstring de `test_ctx_execute_capability_profile.py` (que falavam em 26 agents incluindo `docs-engineer`, `agent-auditor` e `tech-solution-architect`);
  3. **Ausência da constante explícita `COMPUTE_READONLY_AGENTS` (7 agents)** em `test_ctx_execute_capability_profile.py` (`agent-auditor`, `tech-solution-architect`, `performance-agent`, `refactor-planner`, `business-rules-extractor`, `codegraph-engine`, `ddd-bounded-context-mapper`) para validar o guardrail anti-mutação (`CLAUSE_BATCH_OR_EXEC_READONLY`).

#### Eixo 5 — Cenário Não Previsto 4: Ausência de Guardrail Anti-Mutação em Agents Read-Only com `ctx_execute` / `ctx_batch` (**Achado A4**)
- Existem **7 agents estritamente Read-Only (Score 0 / R-025)** que retêm legitimamente `context-mode/ctx_execute` para computação e agregação analítica:
  1. `agent-auditor`
  2. `tech-solution-architect`
  3. `performance-agent`
  4. `refactor-planner`
  5. `business-rules-extractor`
  6. `codegraph-engine`
  7. `ddd-bounded-context-mapper`
- **Lacuna de segurança**: Atualmente, `sync_execution_protocol.py` injeta nesses 7 agents exatamente a mesma cláusula `CLAUSE_BATCH_OR_EXEC` usada para desenvolvedores mutadores (*"para I/O, inspeção e mutação de arquivos"*). Não há uma variante `CLAUSE_BATCH_OR_EXEC_READONLY` que proíba explicitamente chamadas de escrita em disco (`fs.writeFileSync`, `fs.appendFileSync`, `fs.unlinkSync`, `fs.rmSync`, `fs.renameSync` ou redirecionamento shell `>`/`>>` em `ctx_batch`) para agents Read-Only.

#### Eixo 6 — Cenário Não Previsto 5: Prompts `.prompt.md` (`validate`, `strategic-review`, `ctx-*`) (**Achado A5**)
- Dos **24 arquivos `.prompt.md`** em `.github/prompts/`:
  - **16 prompts possuem `context-mode/ctx_execute`** (incluindo todos os prompts que criam/alteram artefatos ou executam workflows de mutação: `add-project-context`, `del-project-context`, `commit`, `connect-integration-graphs`, `craft-prompt`, `ctx-start`, `deep-search`, `eval-workflows`, `health`, `implement`, `init-context`, `plan`, `plan-lessons-harvester`, `review`, `synth-waves`, `visualize-graph`).
  - **8 prompts NÃO possuem `context-mode/ctx_execute`**:
    - 5 utilitários leves `ctx-*` (`ctx-checkpoint.prompt.md`, `ctx-doctor.prompt.md`, `ctx-insight.prompt.md`, `ctx-resume.prompt.md`, `ctx-status.prompt.md`) + `agent-router.prompt.md` — **corretamente sem `ctx_execute`** por serem utilitários de sessão/roteamento.
    - **2 prompts analíticos de workflow (`validate.prompt.md` e `strategic-review.prompt.md`)** — declaram `read_file`, `ctx_batch`, `ctx_search`, `ctx_index`, `ctx_resume`, mas **não declaram `context-mode/ctx_execute`**.
- **Anomalia em `validate.prompt.md` e `strategic-review.prompt.md`**:
  - `validate.prompt.md` é o workflow canônico `/validate` que executa checklists determinísticos multi-arquivo, cruzamento de contratos, validação de links/frontmatters e inspeção de conformidade. Sem `ctx_execute`, não pode executar scripts Node.js Read-Only de verificação estrutural em lote no Windows (R-056/R-059) e cai no fallback de `read_file` ou subshells `ctx_batch`.
  - `strategic-review.prompt.md` realiza auditoria arquitetural transversal de múltiplos documentos e código; sua restrição deve ser explicitamente alinhada ou receber `ctx_execute` em modo Read-Only computacional.

#### Eixo 7 — Cenário Não Previsto 6: Drift Documental e Redundância de Título no `Smell 2.32` e Regra `R-008` sem Ressalva de Perfil (**Achados A6 e A7**)
- **Achado A6 (Saneamento do `Smell 2.32` em `.github/skills/governance-audit-patterns/SKILL.md`)**: O catálogo de smells em `SKILL.md` já está numerado sequencialmente de `2.31` a `2.35` (`2.31` R-066, `2.32` Capability Overreach de `ctx_execute`, `2.33` R-067, `2.34` R-064 e `2.35` R-050/R-064/R-065) — logo, **não existe colisão de numeração** e o ID **`Smell 2.32` deve ser mantido** (sem renumerar para `2.33`). Os problemas reais no `Smell 2.32` são:
  - Título/texto com redundância residual (`ctx_execute / ctx_execute`) a ser limpa;
  - Contagem e descrição de `GATHER_ONLY_AGENTS` desatualizadas (**25 → 24 agents** após a saída de `database-specialist`);
  - Ausência de documentação explícita dos **4 perfis de capacidade** (`COMPUTE_MUTATE`, `COMPUTE_READONLY`, `GATHER_ONLY`, `ROUTER_EXEMPT`).
- **Achado A7 (Ambiguidade normativa em R-008)**: Tanto `CLAUDE.md` quanto `.github/copilot-instructions.md` enunciam R-008 como obrigação universal de usar `ctx_execute` para leitura, sem distinguir explicitamente os **3 Perfis Operacionais de Context-Mode**:
  1. **Perfil 1 — Mutator / Executor (`COMPUTE_MUTATE`)**: Possui `ctx_execute` + `ctx_batch` (22 agents mutadores/fábrica/docs, incluindo `database-specialist` restaurado).
  2. **Perfil 2 — Read-Only Computacional (`COMPUTE_READONLY`)**: Possui `ctx_execute` + `ctx_batch` sob cláusula estrita Anti-Mutação Read-Only (7 agents analíticos de agregação/grafo + prompts `validate` e `strategic-review`).
  3. **Perfil 3 — Gather-Only (`GATHER_ONLY`)**: Possui `ctx_batch` + `ctx_search` + `ctx_index` + `ctx_resume`, **sem `ctx_execute`**, e com corpo instrucional 100% livre de menções obrigatórias a `ctx_execute` (24 agents revisores/consultores/planejadores).
  4. **Perfil 4 — Isentos R-054 (`ROUTER_EXEMPT`)**: 9 routers + `prompt-structuring` (0 tools `context-mode`).

---

### 1.2. Inventário de Grounding Físico (Bytes, Linhas e Estado Atual em Disco)

#### A. Arquivos Nucleares de Governança, Testes, Scripts e Prompts em Escopo

| # | Caminho do Arquivo | Tamanho Atual (Bytes) | Linhas Atuais | Papel na Revisão |
|---|---|---|---|---|
| 1 | `tests/governance_audit/test_ctx_execute_capability_profile.py` | 3449 B | 100 linhas | Verificado em disco |
| 2 | `tests/governance_audit/test_context_mode_precedence_governance.py` | 46689 B | 1040 linhas | Verificado em disco |
| 3 | `tests/governance_audit/test_governance_smells.py` | 55180 B | 991 linhas | Verificado em disco (importa `GATHER_ONLY_AGENTS` na linha 829) |
| 4 | `.github/agents/database-specialist.agent.md` | 13888 B | 171 linhas | Verificado em disco |
| 5 | `.github/agents/agent-auditor.agent.md` | 22462 B | 208 linhas | Verificado em disco |
| 6 | `.github/agents/docs-engineer.agent.md` | 15529 B | 164 linhas | Verificado em disco |
| 7 | `.github/agents/tech-solution-architect.agent.md` | 30547 B | 328 linhas | Verificado em disco |
| 8 | `.github/prompts/validate.prompt.md` | 11854 B | 203 linhas | Verificado em disco |
| 9 | `.github/prompts/strategic-review.prompt.md` | 15665 B | 213 linhas | Verificado em disco |
| 10 | `.github/prompts/ctx-checkpoint.prompt.md` | 10887 B | 189 linhas | Verificado em disco |
| 11 | `.github/prompts/ctx-doctor.prompt.md` | 7642 B | 127 linhas | Verificado em disco |
| 12 | `.github/prompts/ctx-insight.prompt.md` | 7262 B | 123 linhas | Verificado em disco |
| 13 | `.github/prompts/ctx-resume.prompt.md` | 12850 B | 260 linhas | Verificado em disco |
| 14 | `.github/prompts/ctx-status.prompt.md` | 7561 B | 126 linhas | Verificado em disco |
| 15 | `.github/prompts/agent-router.prompt.md` | 11635 B | 154 linhas | Verificado em disco |
| 16 | `tools/agent_protocol_sync/sync_execution_protocol.py` | 15208 B | 356 linhas | Verificado em disco |
| 17 | `tools/agent_protocol_sync/_execution-protocol-fragment.md` | 11760 B | 63 linhas | Verificado em disco |
| 18 | `tools/agent_protocol_sync/protocol_roles.json` | 2249 B | 66 linhas | Verificado em disco |
| 19 | `tools/agent_protocol_sync/README.md` | 5241 B | 62 linhas | Verificado em disco |
| 20 | `.github/skills/governance-audit-patterns/SKILL.md` | 16838 B | 185 linhas | Verificado em disco |
| 21 | `.github/skills/context-mode/SKILL.md` | 31702 B | 299 linhas | Verificado em disco |
| 22 | `.github/skills/governance-factory-patterns/SKILL.md` | 13835 B | 139 linhas | Verificado em disco |
| 23 | `CLAUDE.md` | 44569 B | 227 linhas | Verificado em disco |
| 24 | `.github/copilot-instructions.md` | 16848 B | 133 linhas | Verificado em disco |
| 25 | `docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md` | 10896 B | 107 linhas | Verificado em disco |

#### B. Os 25 Agents Atualmente Listados em `GATHER_ONLY_AGENTS` (Verificados em Disco)

| # | Agent | Caminho Canônico | Bytes / Linhas | Diagnóstico Factual Verificado |
|---|---|---|---|---|
| 26 | `adr-sentinel` | `.github/agents/adr-sentinel.agent.md` | 13476 B / 140 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 27 | `bug-triage` | `.github/agents/bug-triage.agent.md` | 30820 B / 439 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 28 | `code-review` | `.github/agents/code-review.agent.md` | 16314 B / 202 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 29 | `code-style-enforcer` | `.github/agents/code-style-enforcer.agent.md` | 11440 B / 145 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 30 | `compliance-guardrails` | `.github/agents/compliance-guardrails.agent.md` | 12684 B / 165 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 31 | `database-specialist` | `.github/agents/database-specialist.agent.md` | 13888 B / 171 linhas | **ACHADO A1 (Anomalia)**: Definido como "Perfil híbrido: analisa e implementa migrações/queries", mas podado para Gather-only sem `ctx_execute`. |
| 32 | `debugger` | `.github/agents/debugger.agent.md` | 12635 B / 161 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 33 | `deep-search` | `.github/agents/deep-search.agent.md` | 15756 B / 177 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 34 | `devops-engineer` | `.github/agents/devops-engineer.agent.md` | 11442 B / 158 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 35 | `feature-planner` | `.github/agents/feature-planner.agent.md` | 16933 B / 179 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 36 | `plan-critic` | `.github/agents/plan-critic.agent.md` | 19454 B / 161 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 37 | `pr-gatekeeper` | `.github/agents/pr-gatekeeper.agent.md` | 16679 B / 194 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 38 | `repo-hygiene-auditor` | `.github/agents/repo-hygiene-auditor.agent.md` | 13190 B / 145 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 39 | `requirements-analyst` | `.github/agents/requirements-analyst.agent.md` | 19442 B / 211 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 40 | `runtime-verifier` | `.github/agents/runtime-verifier.agent.md` | 13557 B / 152 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 41 | `security-reviewer` | `.github/agents/security-reviewer.agent.md` | 13328 B / 173 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 42 | `test-strategy` | `.github/agents/test-strategy.agent.md` | 16456 B / 156 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 43 | `database-arch-advisor` | `.github/agents/backend/database/database-arch-advisor.agent.md` | 15985 B / 135 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 44 | `ejb-arch-advisor` | `.github/agents/backend/ejb/ejb-arch-advisor.agent.md` | 15766 B / 140 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 45 | `python-arch-advisor` | `.github/agents/backend/python/python-arch-advisor.agent.md` | 17173 B / 144 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 46 | `spring-boot-arch-advisor` | `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md` | 15165 B / 146 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 47 | `spring-reactive-arch-advisor` | `.github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md` | 15070 B / 138 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 48 | `struts-arch-advisor` | `.github/agents/backend/struts/struts-arch-advisor.agent.md` | 16115 B / 144 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 49 | `angular-arch-advisor` | `.github/agents/frontend/angular/angular-arch-advisor.agent.md` | 17167 B / 154 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |
| 50 | `react-arch-advisor` | `.github/agents/frontend/react/react-arch-advisor.agent.md` | 17403 B / 163 linhas | Gather-only no frontmatter, mas corpo pré-protocolo ainda cita `ctx_execute` (**Achado A2**). |

---

## 2. Causa-Raiz (RCA Q0), Análise de Escape e Portão de Reúso Sistêmico (R-055)

- **Q0 — Causa-Raiz Sistêmica (Por que os 6 cenários escaparam no plano `20261003-090000`?)**:
  1. **Classificação Unidimensional**: O plano anterior dividiu o ecossistema em apenas 2 grupos (Mutadores vs. Read-Only) sem separar (a) agents híbridos que implementam migrações SQL (`database-specialist`), (b) agents Read-Only que precisam de `ctx_execute` para scripts analíticos em lote (os 7 `COMPUTE_READONLY`), e (c) agents puramente Gather-Only (24 agents).
  2. **Sincronização Cega de Template (`sync_execution_protocol.py`)**: O script injetava um único texto de `CLAUSE_BATCH_OR_EXEC` (com menção a `ctx_execute` e *"mutação de arquivos"*) em todos os 53 agents não-routers e mantinha `## CRÍTICO: ESCOPO E NÃO-ESCOPO` exigindo `ctx_execute` nos 24 agents Gather-only.
  3. **Omissão dos Prompts Operacionais (`.prompt.md`)**: A revisão anterior inspecionou apenas `.github/agents/*.agent.md`, deixando `validate.prompt.md` e `strategic-review.prompt.md` sem `context-mode/ctx_execute`.
  4. **Calibragem Incompleta da Fonte Única de Testes (A3) e Drift Documental no `Smell 2.32` (A6)**: Embora `test_context_mode_precedence_governance.py` (linha 22) e `test_governance_smells.py` (linha 829) **já importem `GATHER_ONLY_AGENTS` como fonte única (SSOT)** a partir de `test_ctx_execute_capability_profile.py` (não existindo `NO_CTX_EXECUTE_AGENTS` duplicada), a lista incluiu indevidamente `database-specialist` (25 → 24 agents), manteve drift documental frente ao plano histórico `20261003-090000` (que falava em 26 agents incluindo `docs-engineer`, `agent-auditor` e `tech-solution-architect`), não definiu a constante explícita `COMPUTE_READONLY_AGENTS` (7 agents) para validar o guardrail anti-mutação (`CLAUSE_BATCH_OR_EXEC_READONLY`), e deixou o `Smell 2.32` em `governance-audit-patterns/SKILL.md` com contagem desatualizada (25 → 24) e sem os 4 perfis documentados.
- **Portão de Reúso e Prevenção Sistêmica (R-055)**:
  - Preservação do nome e módulo de `GATHER_ONLY_AGENTS` (24 agents após restauração de `database-specialist`) e adição de `COMPUTE_READONLY_AGENTS` (7 agents) em `tests/governance_audit/test_ctx_execute_capability_profile.py`, mantendo compatibilidade com os imports existentes em `test_context_mode_precedence_governance.py` e `test_governance_smells.py`.
  - Novo teste determinístico de **Coerência Instrucional Interna**: nenhum agente em `GATHER_ONLY_AGENTS` pode conter exigência de uso de `ctx_execute` no corpo, e todos os 7 agentes em `COMPUTE_READONLY_AGENTS` devem conter proibição explícita de mutação física (`CLAUSE_BATCH_OR_EXEC_READONLY` / `R-025`).
  - Saneamento do `Smell 2.32` em `.github/skills/governance-audit-patterns/SKILL.md` (mantendo o ID `2.32` dentro da sequência `2.31`–`2.35`, limpando `ctx_execute / ctx_execute`, atualizando 25 → 24 e documentando os 4 perfis).

---

## 3. Decomposição em Ondas de Execução (`[GOVERNANCE_TASKS]`)

### Wave 1 — Governança Declarativa, Restauração de Capacidade e Alinhamento Documental (`@governance-maintainer` / `@docs-engineer`)

#### Tarefa W1.1 — Restauração de `context-mode/ctx_execute` em `database-specialist.agent.md` (Correção do Achado A1)
- **Alvo**: `.github/agents/database-specialist.agent.md`, `.github/agents/catalog.yaml`, `.github/agents/README.md`.
- **Ação**:
  - Readicionar `'context-mode/ctx_execute'` ao array `tools:` do frontmatter de `database-specialist.agent.md`, equiparando-o aos seus pares híbridos `oracle-database-specialist` e `informix-database-specialist`.
  - Atualizar a cláusula `<execution_protocol>` de `database-specialist.agent.md` para `CLAUSE_BATCH_OR_EXEC`.

#### Tarefa W1.2 — Eliminação da Esquizofrenia Instrucional nos 24 Agents Gather-Only (Correção do Achado A2)
- **Alvo**: Os 24 arquivos `.agent.md` genuinamente Gather-only (todos os listados na Tabela 1.2.B exceto `database-specialist`).
- **Ação**:
  - Na seção `## CRÍTICO: ESCOPO E NÃO-ESCOPO` (e diretrizes de corpo pré-`<execution_protocol>`) dos 24 agents Gather-only, substituir a instrução contraditória que exige `ctx_execute (com file)` por instrução compatível com o perfil Gather-only:
    - `❌ NÃO usar ferramentas nativas de editor (read_file, insert_edit_into_file, replace_string_in_file, create_file) nem comandos de leitura/inspeção em terminal quando o context-mode estiver disponível. O uso de context-mode (ctx_batch, ctx_search, ctx_index, ctx_resume) é 100% OBRIGATÓRIO para inspeção e coleta de contexto em lote (R-008 / R-056 / Smell 2.24).`
    - `❌ NÃO encadear chamadas unitárias sequenciais de ctx_batch no chat (MCP Tool Chaining / Smell 2.26). Toda operação multi-arquivo de leitura/inspeção DEVE ser consolidada em chamada única de ctx_batch(commands, queries) + ctx_search.`

#### Tarefa W1.3 — Blindagem Anti-Mutação nos 7 Agents Read-Only que Detêm `ctx_execute` (Correção do Achado A4)
- **Alvo**: `agent-auditor.agent.md`, `tech-solution-architect.agent.md`, `performance-agent.agent.md`, `refactor-planner.agent.md`, `business-rules-extractor.agent.md`, `codegraph-engine.agent.md`, `ddd-bounded-context-mapper.agent.md`.
- **Ação**:
  - Ajustar a cláusula de protocolo e não-escopo desses 7 agents Read-Only para explicitar que o uso de `ctx_execute` (`language: "javascript"`) destina-se **exclusivamente a leitura, parsing, agregação computacional e inspeção Read-Only (R-025)**, sendo terminantemente proibido invocar `fs.writeFileSync`, `fs.appendFileSync`, `fs.unlinkSync`, `fs.rmSync` ou mutação de arquivos.

#### Tarefa W1.4 — Calibragem dos Prompts Analíticos `validate.prompt.md` e `strategic-review.prompt.md` (Correção do Achado A5)
- **Alvo**: `.github/prompts/validate.prompt.md`, `.github/prompts/strategic-review.prompt.md`, `.github/prompts/catalog.yaml`, `.github/prompts/README.md`.
- **Ação**:
  - Adicionar `'context-mode/ctx_execute'` ao frontmatter de `validate.prompt.md` e `strategic-review.prompt.md` sob perfil **Read-Only Computacional (`COMPUTE_READONLY`)**, permitindo que os workflows `/validate` e `/strategic-review` executem scripts Node.js (`fs` nativo) de verificação estrutural, checagem cruzada de frontmatters/links e auditoria multi-arquivo em lote no Windows sem depender de `read_file` unitário nem sofrer bloqueio do Windows Defender/AMSI.
  - Manter os 5 utilitários `ctx-*` (`ctx-checkpoint`, `ctx-doctor`, `ctx-insight`, `ctx-resume`, `ctx-status`) e `agent-router.prompt.md` estritamente sem `ctx_execute`.

#### Tarefa W1.5 — Saneamento do `Smell 2.32` e Taxonomia de 4 Perfis em `CLAUDE.md` / `copilot-instructions.md` / Skills (Correção dos Achados A6 e A7)
- **Arquivos-Alvo**:
  - `.github/skills/governance-audit-patterns/SKILL.md`
  - `.github/skills/context-mode/SKILL.md`
  - `.github/skills/governance-factory-patterns/SKILL.md`
  - `CLAUDE.md`
  - `.github/copilot-instructions.md`
  - `docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md`
- **Ações**:
  - Manter em `.github/skills/governance-audit-patterns/SKILL.md` o ID **`Smell 2.32`** (preservando intacta a numeração `2.31` a `2.35`, pois `2.33` já é R-067), limpando o título/texto redundante (`ctx_execute / ctx_execute`), atualizando a contagem e descrição de `GATHER_ONLY_AGENTS` de **25 para 24 agents** (após a saída de `database-specialist`) e documentando os **4 perfis** (`COMPUTE_MUTATE`, `COMPUTE_READONLY`, `GATHER_ONLY`, `ROUTER_EXEMPT`).
  - Atualizar `CLAUDE.md` (R-008 / R-056), `.github/copilot-instructions.md`, `.github/skills/context-mode/SKILL.md` e `.github/skills/governance-factory-patterns/SKILL.md` com a tabela canônica dos 4 perfis (`COMPUTE_MUTATE` = 19, `COMPUTE_READONLY` = 7, `GATHER_ONLY` = 24, `ROUTER_EXEMPT` = 10).
  - Adicionar nota de errata/reconciliação no plano histórico `docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md` esclarecendo o drift de 26 → 25 → **24 agents** em `GATHER_ONLY_AGENTS` (confirmando que `docs-engineer`, `agent-auditor`, `tech-solution-architect` e `database-specialist` detêm `ctx_execute`).

---

### Wave 2 — Evolução de Scripts de Sincronização e Sensores Pytest via Trilha Python R-055 (`@python-router` → `@python-arch-advisor` → `@python-developer` / `@python-test-engineer`)

> **Governança de Domínio e Segregação Estrita de Executores (R-055)**: A **Wave 1** (`.md` / `.yaml`) é executada exclusivamente por `@governance-maintainer` / `@docs-engineer`. Já a **Wave 2** (`tools/**/*.py`, `tools/**/*.json`, `tests/governance_audit/*.py`) é executada **exclusivamente** pela trilha especialista Python R-055 (`@python-router` → 1º `@python-arch-advisor` → 2º `@python-developer` / `@python-test-engineer`), sendo terminantemente vedada a edição direta de scripts `.py`, configurações `.json` de ferramentas ou suítes `pytest` por agentes de manutenção documental.

#### Tarefa W2.1 — Evolução de `tools/agent_protocol_sync/sync_execution_protocol.py` e `protocol_roles.json`
- **Alvo**: `tools/agent_protocol_sync/sync_execution_protocol.py`, `tools/agent_protocol_sync/_execution-protocol-fragment.md`, `tools/agent_protocol_sync/protocol_roles.json`, `tools/agent_protocol_sync/README.md`.
- **Ação**:
  - Adicionar em `sync_execution_protocol.py` a constante `CLAUSE_BATCH_OR_EXEC_READONLY` para agents Read-Only (Score 0) que possuem `ctx_execute`, substituindo *"para I/O, inspeção e mutação de arquivos"* por *"para leitura, parsing estruturado e agregação computacional Read-Only de arquivos (sendo terminantemente PROIBIDO usar fs.writeFileSync, fs.appendFileSync, fs.unlinkSync ou mutar qualquer arquivo em disco — R-025)"*.
  - **Interação explícita entre `protocol_roles.json` e `sync_execution_protocol.py` (Preservação de Schema)**: Como `protocol_roles.json` é um dicionário plano `Record<string, "STANDARD" | "CUSTOM">` consumido por `load_roles() -> dict[str, str]`, **não** deve ser introduzida uma chave aninhada com array que quebre a tipagem plana. Em vez disso, `sync_execution_protocol.py` detecta o perfil `COMPUTE_READONLY` diretamente a partir da combinação do frontmatter YAML do agente (`context-mode/ctx_execute` presente em `tools:`) com o marcador de perfil Read-Only (`Score 0 (Read-Only)` / constante canônica `COMPUTE_READONLY_AGENTS = {"agent-auditor", "tech-solution-architect", "performance-agent", "refactor-planner", "business-rules-extractor", "strategic-review", "validate"}` em `sync_execution_protocol.py`), e/ou estende os valores de papel plano em `protocol_roles.json` (ex.: `"STANDARD"`, `"CUSTOM"`, `"COMPUTE_READONLY"`) mantendo 100% de compatibilidade com `dict[str, str]`.

#### Tarefa W2.2 — Calibragem de `GATHER_ONLY_AGENTS` (24 Agents), Adição de `COMPUTE_READONLY_AGENTS` (7 Agents) e Testes em `tests/governance_audit/` (Correção do Achado A3)
- **Arquivos-Alvo**:
  - `tests/governance_audit/test_ctx_execute_capability_profile.py`
  - `tests/governance_audit/test_context_mode_precedence_governance.py`
  - `tests/governance_audit/test_governance_smells.py`
- **Ações**:
  - Preservar o nome e o módulo da constante `GATHER_ONLY_AGENTS` em `tests/governance_audit/test_ctx_execute_capability_profile.py` como fonte única (SSOT) já importada em `test_context_mode_precedence_governance.py` (linha 22) e `test_governance_smells.py` (linha 829), removendo `"database-specialist"` (25 → **24 agents**) e alinhando a docstring do módulo.
  - Declarar e exportar `COMPUTE_READONLY_AGENTS` (7 agents: `agent-auditor`, `tech-solution-architect`, `performance-agent`, `refactor-planner`, `business-rules-extractor`, `codegraph-engine`, `ddd-bounded-context-mapper`) em `test_ctx_execute_capability_profile.py`.
  - Adicionar `test_gather_only_agents_have_no_instructional_schizophrenia()`: verifica que nenhum dos 24 agents `GATHER_ONLY_AGENTS` exige `ctx_execute` em `## CRÍTICO: ESCOPO E NÃO-ESCOPO` ou `<execution_protocol>`.
  - Adicionar `test_compute_readonly_agents_enforce_no_mutation_guardrail()`: verifica que todos os 7 agents em `COMPUTE_READONLY_AGENTS` contêm `CLAUSE_BATCH_OR_EXEC_READONLY` proibindo `fs.writeFileSync` / mutação em disco (R-025).
  - Adicionar `test_smell_2_32_profile_and_count_consistency_in_governance_audit_skill()`: verifica que `.github/skills/governance-audit-patterns/SKILL.md` mantém o ID `Smell 2.32` sem redundância `ctx_execute / ctx_execute`, reflete 24 agents em `GATHER_ONLY_AGENTS` e documenta os 4 perfis (`COMPUTE_MUTATE`, `COMPUTE_READONLY`, `GATHER_ONLY`, `ROUTER_EXEMPT`).

---

## 4. Alternativas Rejeitadas (C2)

1. **Alternativa A (Rejeitada): Devolver `context-mode/ctx_execute` irrestritamente para todos os 53 agents operacionais (reverter integralmente o plano `20261003-090000`)**:
   - *Motivo da rejeição*: Como o hook `preToolUse` do host IDE não intercepta chamadas de `run_subagent`, devolver `ctx_execute` irrestritamente a todos os 24 agentes consultivos/revisores reabriria a superfície de *Capability Overreach* (Smell 2.33) e *Tool Chaining* em agentes que não realizam agregação algorítmica pesada nem mutação.
2. **Alternativa B (Rejeitada): Manter `database-specialist` sem `ctx_execute` e alterar sua descrição para Read-Only**:
   - *Motivo da rejeição*: Já existe `database-arch-advisor` como agente consultivo Read-Only de banco de dados. Transformar `database-specialist` em Read-Only deixaria o ecossistema sem executor de migrações/queries para bancos relacionais gerais (PostgreSQL, MySQL, SQL Server), quebrando a simetria com `oracle-database-specialist` e `informix-database-specialist`.
3. **Alternativa C (Rejeitada): Ignorar as menções a `ctx_execute` na seção `## CRÍTICO: ESCOPO E NÃO-ESCOPO` dos 24 agents Gather-only**:
   - *Motivo da rejeição*: Manter instruções contraditórias no mesmo arquivo `.agent.md` (frontmatter proibindo `ctx_execute` + seção de escopo exigindo `ctx_execute` 100% obrigatório) degrada a confiabilidade de tool-calling do modelo e viola a higiene contratual R-039.

---

## 5. Blast Radius, Riscos e Análise de Impacto (C2)

- **Escopo Total (`allowed_files`)**: **48 arquivos** mapeados (25 contracts `.agent.md` = `database-specialist` + 24 `GATHER_ONLY_AGENTS`; 7 agents `COMPUTE_READONLY`; 2 prompts `.prompt.md`; 4 arquivos em `tools/agent_protocol_sync/`; 3 arquivos de teste em `tests/governance_audit/` incluindo `test_governance_smells.py`; 3 skills; `CLAUDE.md`; `.github/copilot-instructions.md`; e o plano histórico `20261003-090000`).
- **Preservação Estrita de Contrato de Importação (`GATHER_ONLY_AGENTS`)**: O nome e o módulo da constante `GATHER_ONLY_AGENTS` em `tests/governance_audit/test_ctx_execute_capability_profile.py` serão **estritamente preservados** para não quebrar os imports existentes em `tests/governance_audit/test_context_mode_precedence_governance.py` (linha 22) e `tests/governance_audit/test_governance_smells.py` (linha 829: `from tests.governance_audit.test_ctx_execute_capability_profile import GATHER_ONLY_AGENTS`).
- **Risco de Regressão em `sync_execution_protocol.py --check`**: Mitigado pela atualização atômica de `protocol_roles.json`, `_execution-protocol-fragment.md` e `sync_execution_protocol.py` antes de rodar `--write` e `pytest`.
- **Risco de Conflito com Regras de Segurança (R-025)**: Mitigado pela cláusula `CLAUSE_BATCH_OR_EXEC_READONLY` nos 7 agents `COMPUTE_READONLY_AGENTS`.

---

## 6. Estratégia de Rollback Cirúrgico (C2 / R-064)

Caso qualquer teste em `pytest tests/governance_audit/` ou `python -m tools.agent_protocol_sync.sync_execution_protocol --check` apresente regressão não sanável durante a execução:
1. **Reversão Cirúrgica Exclusiva dos Caminhos em `allowed_files`** (proibido `git checkout --` genérico por diretório):
   ```bash
   git checkout -- \
     ".github/agents/database-specialist.agent.md" \
     ".github/agents/agent-auditor.agent.md" \
     ".github/agents/docs-engineer.agent.md" \
     ".github/agents/tech-solution-architect.agent.md" \
     ".github/agents/adr-sentinel.agent.md" \
     ".github/agents/bug-triage.agent.md" \
     ".github/agents/code-review.agent.md" \
     ".github/agents/code-style-enforcer.agent.md" \
     ".github/agents/compliance-guardrails.agent.md" \
     ".github/agents/debugger.agent.md" \
     ".github/agents/deep-search.agent.md" \
     ".github/agents/devops-engineer.agent.md" \
     ".github/agents/feature-planner.agent.md" \
     ".github/agents/plan-critic.agent.md" \
     ".github/agents/pr-gatekeeper.agent.md" \
     ".github/agents/repo-hygiene-auditor.agent.md" \
     ".github/agents/requirements-analyst.agent.md" \
     ".github/agents/runtime-verifier.agent.md" \
     ".github/agents/security-reviewer.agent.md" \
     ".github/agents/test-strategy.agent.md" \
     ".github/agents/backend/database/database-arch-advisor.agent.md" \
     ".github/agents/backend/ejb/ejb-arch-advisor.agent.md" \
     ".github/agents/backend/python/python-arch-advisor.agent.md" \
     ".github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md" \
     ".github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md" \
     ".github/agents/backend/struts/struts-arch-advisor.agent.md" \
     ".github/agents/frontend/angular/angular-arch-advisor.agent.md" \
     ".github/agents/frontend/react/react-arch-advisor.agent.md" \
     ".github/agents/README.md" \
     ".github/agents/catalog.yaml" \
     ".github/prompts/validate.prompt.md" \
     ".github/prompts/strategic-review.prompt.md" \
     ".github/prompts/README.md" \
     ".github/prompts/catalog.yaml" \
     ".github/skills/governance-audit-patterns/SKILL.md" \
     ".github/skills/context-mode/SKILL.md" \
     ".github/skills/governance-factory-patterns/SKILL.md" \
     "CLAUDE.md" \
     ".github/copilot-instructions.md" \
     "tools/agent_protocol_sync/sync_execution_protocol.py" \
     "tools/agent_protocol_sync/_execution-protocol-fragment.md" \
     "tools/agent_protocol_sync/protocol_roles.json" \
     "tools/agent_protocol_sync/README.md" \
     "tests/governance_audit/test_ctx_execute_capability_profile.py" \
     "tests/governance_audit/test_context_mode_precedence_governance.py" \
     "tests/governance_audit/test_governance_smells.py" \
     "docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md" \
     "docs/plans/governance/20261117-120000-governance-maintenance-ctx-execute-profile-revisao.md"
   ```
2. **Tratamento Seguro de Arquivos Novos (Proibido `git clean` irrestrito — R-064)**: Este plano edita exclusivamente arquivos já rastreados em `allowed_files`. Caso algum artefato temporário não rastreado seja gerado acidentalmente durante a execução, sua remoção deverá ser feita **exclusivamente por caminho nominal explícito** (`rm -f "<caminho_exato>"`), sendo **terminantemente proibido** o uso de `git clean -fd` ou `git clean` irrestrito para proteger planos em `docs/plans/` e artefatos locais do workspace.
3. Reexecutar `pytest tests/governance_audit/` para confirmar restauração do baseline verde.

---

## 7. Estratégia de Execução Plan-Then-Batch (R-046 / R-059), Critérios de Aceitação e Cenários Gherkin (C4)

### 7.1. Critérios de Aceitação Verificáveis (Escopo: 48 arquivos em `allowed_files`)

- [ ] **Cobertura Integral de Escopo (`allowed_files`)**: Todos os **48 arquivos** listados em `allowed_files` no frontmatter YAML (nenhuma menção residual ao escopo preliminar de 17 artefatos `.md`) auditados, sincronizados e validados sem regressão.
- [ ] **Segregação Estrita de Executores (R-055)**: Wave 1 (`.md` e `.yaml`) executada exclusivamente por `@governance-maintainer` / `@docs-engineer`; Wave 2 (`tools/**/*.py`, `tools/**/*.json`, `tests/governance_audit/*.py`) executada exclusivamente pela trilha Python R-055 (`@python-router` → 1º `@python-arch-advisor` → 2º `@python-developer` / `@python-test-engineer`).

1. `database-specialist.agent.md` declara `'context-mode/ctx_execute'` no frontmatter e possui perfil `COMPUTE_MUTATE`.
2. A lista canônica `GATHER_ONLY_AGENTS` em `tests/governance_audit/test_ctx_execute_capability_profile.py` preserva seu nome e módulo, contém exatamente **24 agents** (sem `database-specialist`) e continua sendo importada como fonte única por `test_context_mode_precedence_governance.py` (linha 22) e `test_governance_smells.py` (linha 829), acompanhada da nova constante `COMPUTE_READONLY_AGENTS` (7 agents).
3. Nenhum dos 24 agents em `GATHER_ONLY_AGENTS` contém instrução exigindo `ctx_execute` na seção `## CRÍTICO: ESCOPO E NÃO-ESCOPO` ou em `<execution_protocol>`.
4. Os 7 agents Read-Only com `ctx_execute` (`COMPUTE_READONLY_AGENTS`: `agent-auditor`, `tech-solution-architect`, `performance-agent`, `refactor-planner`, `business-rules-extractor`, `codegraph-engine`, `ddd-bounded-context-mapper`) declaram proibição explícita de mutação física em disco (`fs.writeFileSync` / `R-025` / `CLAUSE_BATCH_OR_EXEC_READONLY`) dentro de `<execution_protocol>`.
5. `validate.prompt.md` e `strategic-review.prompt.md` declaram `'context-mode/ctx_execute'` para verificação/inspeção em lote Read-Only.
6. `.github/skills/governance-audit-patterns/SKILL.md` mantém o ID `Smell 2.32` (preservando a sequência `2.31`–`2.35` onde `2.33` já é R-067), sem o título redundante (`ctx_execute / ctx_execute`), atualizando a contagem/descrição de `GATHER_ONLY_AGENTS` de 25 para 24 (após saída de `database-specialist`) e documentando os 4 perfis (`COMPUTE_MUTATE`, `COMPUTE_READONLY`, `GATHER_ONLY`, `ROUTER_EXEMPT`).
7. `python -m tools.agent_protocol_sync.sync_execution_protocol --check` retorna exit code `0`.
8. `pytest tests/governance_audit/` (incluindo `test_ctx_execute_capability_profile.py`, `test_context_mode_precedence_governance.py` e `test_governance_smells.py`) passa com 0 falhas.

### 7.2. Cenários Comportamentais (Gherkin)

```gherkin
Feature: Calibragem e Coerência do Perfil de Capacidade context-mode/ctx_execute

  Scenario: S1 - Agente híbrido database-specialist possui capacidade de implementar migrações
    Given o contrato do agente ".github/agents/database-specialist.agent.md"
    When o parser de auditoria extrai a lista "tools" do frontmatter YAML
    Then "context-mode/ctx_execute" e "context-mode/ctx_batch" devem estar presentes
    And "database-specialist" não deve constar em GATHER_ONLY_AGENTS

  Scenario: S2 - Ausência de esquizofrenia instrucional nos 24 agentes Gather-Only e preservação de SSOT
    Given a lista canônica dos 24 agentes GATHER_ONLY_AGENTS exportada por "test_ctx_execute_capability_profile.py"
    And importada por "test_context_mode_precedence_governance.py" e "test_governance_smells.py"
    When o teste estático inspeciona o frontmatter e o corpo de cada agente
    Then nenhum deles deve declarar "context-mode/ctx_execute" no frontmatter
    And nenhum deles deve exigir o uso de "ctx_execute" em "## CRÍTICO: ESCOPO E NÃO-ESCOPO" ou "<execution_protocol>"

  Scenario: S3 - Guardrail anti-mutação nos 7 agentes Read-Only com ctx_execute
    Given a lista dos 7 agentes COMPUTE_READONLY_AGENTS que retêm "context-mode/ctx_execute"
    When o sincronizador "sync_execution_protocol.py --check" e o pytest validam seus blocos "<execution_protocol>"
    Then todos devem conter a cláusula "CLAUSE_BATCH_OR_EXEC_READONLY" proibindo "fs.writeFileSync" e mutação de arquivos (R-025)

  Scenario: S4 - Saneamento documental do Smell 2.32 e preservação da sequência 2.31-2.35 na skill governance-audit-patterns
    Given o arquivo ".github/skills/governance-audit-patterns/SKILL.md"
    When o teste inspeciona o cabeçalho e o corpo do "Smell 2.32" e a sequência "2.31" a "2.35"
    Then o ID "Smell 2.32" deve ser mantido (preservando "2.33" para R-067 até "2.35") sem título redundante "ctx_execute / ctx_execute"
    And o Smell 2.32 deve refletir 24 agentes em "GATHER_ONLY_AGENTS" (sem "database-specialist") e os 4 perfis ("COMPUTE_MUTATE", "COMPUTE_READONLY", "GATHER_ONLY", "ROUTER_EXEMPT")
```

---

## 8. Segurança Agentic e Isolamento Territorial (C7 / C9 / C10 — OWASP ASI01/ASI06, R-043/R-044)

- **Mitigação OWASP ASI01 (Excessive Agency) & Least Privilege**: Mantém os 24 agents puramente consultivos sem execução arbitrária de código (`ctx_execute`), enquanto fecha a brecha onde 7 agents Read-Only com `ctx_execute` recebiam texto de protocolo permitindo *"mutação de arquivos"*.
- **Mitigação OWASP ASI06 (Context Poisoning / Instructional Conflict)**: Elimina a contradição interna entre frontmatter e corpo nos 24 agents Gather-only, evitando prompts conflitantes que degradam a obediência às guardrails de segurança.
- **Isolamento Territorial R-043 / R-044**: Nenhum arquivo em `.github/instructions/local/**` ou `*.local.*` faz parte de `allowed_files` nem é referenciado neste plano global de governança.

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Revisor**: `@plan-critic`
- **Veredito Final**: `PASS_WITH_WARNINGS` (`review_verdict: "PASS_WITH_WARNINGS"`)
- **Rodadas de Revisão**: `2` (`review_rounds: 2` — Rodada 1/2: `NEEDS_REVISION`; Rodada 2/2: `PASS_WITH_WARNINGS`)
- **Validação Estrutural Determinística (Tier 1)**: `PASS` (`review_tier1: "PASS"`)
- **Status do Plano**: `DRAFT` (`approved: false` — aguardando Gate de Aprovação Humana / HITL na Etapa 4)

### Histórico e Resolução dos Apontamentos (Rodada 1/2 → Rodada 2/2)

| Rodada | ID / Severidade | Escopo | Descrição e Resolução Aplicada no Plano | Status |
| :--- | :--- | :--- | :--- | :--- |
| **R1** | `B1` — BLOCKER | `allowed_files` vs Wave 1/Wave 2 | Sincronizados todos os **48 arquivos** em `allowed_files` cobrindo 100% dos alvos das Waves 1 e 2 (incluindo os 24 agentes Gather-Only, catálogos, skills, scripts Python e testes). | ✅ Resolvido |
| **R1** | `B2` — BLOCKER | Coerência interna (25 vs 24 agentes) | Unificada a cardinalidade em **24 agentes** `GATHER_ONLY_AGENTS` (excluindo `database-specialist`, restaurado ao perfil `COMPUTE_MUTATE`) e **7 agentes/prompts** `COMPUTE_READONLY`. | ✅ Resolvido |
| **R1** | `B3` — BLOCKER | SSOT de `GATHER_ONLY_AGENTS` | Definido `tests/governance_audit/test_ctx_execute_capability_profile.py` como SSOT exportador de `GATHER_ONLY_AGENTS` e `COMPUTE_READONLY_AGENTS`, importado por `test_context_mode_precedence_governance.py` e `test_governance_smells.py`. | ✅ Resolvido |
| **R1** | `M1` — MAJOR | Preservação da sequência Smell 2.31–2.35 | Mantido o identificador `Smell 2.32` em `.github/skills/governance-audit-patterns/SKILL.md` (preservando `2.33` para R-067 até `2.35`), corrigindo apenas o título redundante e o corpo. | ✅ Resolvido |
| **R2** | `Item 1` — MEDIUM | `tools/agent_protocol_sync/protocol_roles.json` (W2.1) | Explicitado em **W2.1** como `protocol_roles.json` (`dict[str, str]` plano) e `sync_execution_protocol.py` interagem: detecção de `COMPUTE_READONLY` via frontmatter `tools:` + `Score 0 (Read-Only)` / constante `COMPUTE_READONLY_AGENTS` e/ou papel plano `"COMPUTE_READONLY"` sem aninhar listas que quebrem `load_roles()`. | ✅ Incorporado |
| **R2** | `Item 2` — LOW | Checklist no corpo (48 arquivos) | Removida qualquer menção residual a "17 artefatos `.md`" e explicitado no checklist da Seção 7.1 o escopo exato dos **48 arquivos** de `allowed_files`. | ✅ Incorporado |
| **R2** | `Item 3` — LOW | Segregação de Executores R-055 | Reafirmado em Wave 1, Wave 2 e Seção 7.1 que a **Wave 1** (`.md` / `.yaml`) é executada por `@governance-maintainer` / `@docs-engineer` e a **Wave 2** (`tools/**/*.py`, `.json`, `tests/governance_audit/*.py`) é executada **exclusivamente** pela trilha Python R-055 (`@python-router` → 1º `@python-arch-advisor` → 2º `@python-developer` / `@python-test-engineer`). | ✅ Incorporado |

---

## Parecer de Conformidade Pós-Execução (R-064 — Etapa 5b)

- **Revisor Pós-Execução**: `@agent-auditor` (`post_exec_reviewer: "@agent-auditor"`)
- **Data da Revisão**: `2026-11-17` (`post_exec_reviewed_at: "2026-11-17"`)
- **Veredito Pós-Execução**: `PASS_WITH_WARNINGS` (`post_exec_review_verdict: "PASS_WITH_WARNINGS"`)

### Rastreabilidade de Execução Segregada (R-055 / R-064)

| Onda | Executor(es) | Escopo Materializado | Status |
| :--- | :--- | :--- | :--- |
| **Wave 1** | `@governance-maintainer` (e documentação final Etapa 5b por `@docs-engineer`) | Restauração de `context-mode/ctx_execute` em `database-specialist.agent.md` (`COMPUTE_MUTATE`), habilitação sob perfil `COMPUTE_READONLY` em `validate.prompt.md` e `strategic-review.prompt.md`, sincronização do template `_execution-protocol-fragment.md`, atualização de `governance-audit-patterns/SKILL.md` (`Smell 2.32`), `catalog.yaml` e `.github/agents/README.md`. | ✅ Concluído |
| **Wave 2** | `@python-developer` e `@python-test-engineer` via `@python-router` (precedidos por `@python-arch-advisor`) | Evolução de `tools/agent_protocol_sync/protocol_roles.json` e `sync_execution_protocol.py` (`CLAUSE_COMPUTE_READONLY` e propagação aos 24 agents `GATHER_ONLY`), calibragem do SSOT `test_ctx_execute_capability_profile.py` (`GATHER_ONLY_AGENTS` = 24, `COMPUTE_READONLY_AGENTS` = 7) e sincronização com `test_context_mode_precedence_governance.py` e `test_governance_smells.py`. | ✅ Concluído |

### Validação Determinística e Quality Gates

- **Sincronização de Protocolo**: `python tools/agent_protocol_sync/sync_execution_protocol.py --check` → `exit 0` (63 agents sincronizados sem drift).
- **Suíte de Auditoria de Governança**: `97 passed` em `tests/governance_audit/` (`test_ctx_execute_capability_profile.py`, `test_context_mode_precedence_governance.py` e `test_governance_smells.py`).
