---
status: "COMPLETED"
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-16"
intencao_plano: "hibrido"
workflow_trace_id: "trace-20261116-gov-qg-gap"
related-planning-doc: "N/A — plano raiz"
allowed_files:
  - ".github/agents/workflows.md"
  - ".github/agents/workflows/workflow-governance-maintenance.md"
  - ".github/agents/workflows/workflow-feature-development.md"
  - ".github/agents/workflows/workflow-bug-fix.md"
  - ".github/agents/workflows/workflow-refactoring.md"
  - ".github/agents/workflows/workflow-framework-migration.md"
  - ".github/agents/workflows/workflow-dependency-vulnerability-remediation.md"
  - ".github/skills/plan-conformance-patterns/SKILL.md"
  - ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md"
  - ".github/skills/governance-audit-patterns/references/plan-template-governance.md"
  - ".github/skills/governance-factory-patterns/references/workflow-invariants.md"
  - ".github/skills/handoff-governance/SKILL.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - ".github/agents/agent-auditor.agent.md"
  - ".github/agents/code-review.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/agent-router.agent.md"
session_id: "sess-20261116-gov-qg-gap"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
parent_plan_ref: "N/A — plano raiz"
review_verdict: "ESCALATED_HITL"
review_rounds: 2
reviewer: "@plan-critic"
post_exec_review_verdict: "PASS_WITH_WARNINGS"
post_exec_reviewer: "@agent-auditor"
post_exec_reviewed_at: "2026-11-16"
---

# Plano de Manutenção de Governança — Quality Gate Pós-Execução de Conformidade com o Plano (R-064)

## 1. Escopo da Manutenção e Achados (Smells 2.x com Severidade)

| Parâmetro de Correlação | Valor |
| :--- | :--- |
| **Workflow ID** | `WORKFLOW-GOVERNANCE-MAINTENANCE` |
| **Workflow Trace ID** | `trace-20261116-gov-qg-gap` |
| **Session ID** | `sess-20261116-gov-qg-gap` |
| **Autor Intelectual (Etapa 1)** | `@agent-auditor` (Read-Only, R-025 / R-057) |
| **Materializador Físico (Etapa 2)** | `@docs-engineer` (R-064) |
| **Revisor Cético Pré-HITL (Etapa 3)** | `@plan-critic` |
| **Executor Declarativo (Etapa 5a)** | `@governance-maintainer` (pós-Gate HITL) |
| **Revisor de Conformidade Pós-Execução (Etapa 5b)** | `@agent-auditor` |
| **Status Inicial** | `DRAFT` (`approved: false`) |

### 1.1. Matriz de Achados da Auditoria (`E1` a `E7`)

| ID | Severidade | Smell / Invariante | Artefato(s) e Linhas Verificadas | Evidência Empírica do Gap | Ação Corretiva Prescrita |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | **BLOCKER** | `Smell 2.12` / `Smell 2.34` / `R-064` | `.github/agents/workflows.md` (L134–136, L163) e `.github/agents/workflows/workflow-governance-maintenance.md` (L32, L66) | O Estado 5 do `WORKFLOW-GOVERNANCE-MAINTENANCE` encerra o ciclo após a escrita do `@governance-maintainer` e execução de `pytest tests/governance_audit/`, sem etapa formal de revisão semântica pós-execução (`git diff` vs. plano R-064 aprovado) pelo `@agent-auditor`. | Desdobrar o Estado 5 em **5a (Validação Determinística Tier 1 via `pytest` e `governance_sync --check`)** + **5b (Conformance Review Semântico pós-execução pelo `@agent-auditor`)**, impondo bloqueio *fail-closed* de conclusão do workflow sem veredito pós-execução aprovado (`PASS` ou `PASS_WITH_WARNINGS`). |
| **E2 & E6** | **BLOCKER** | `Smell 2.12` / `Smell 2.34` / `R-064` | `.github/agents/workflows/workflow-feature-development.md` (L31–38), `.github/agents/workflows/workflow-bug-fix.md` (L30–37), `.github/agents/workflows/workflow-refactoring.md` (L29–36), `.github/agents/workflows/workflow-framework-migration.md` (L30–38), `.github/agents/workflows/workflow-dependency-vulnerability-remediation.md` (L30–38) | Nos 5 workflows de engenharia de código, o Quality Gate pós-implementação invoca `@code-review`, mas não explicita a obrigatoriedade de executar a verificação de conformidade em 3 níveis (`plan-conformance-patterns`: N1 allowlist, N2 blast radius, N3 checklist semântico do plano R-064) nem a composição com revisores especialistas. | Explicitar no Quality Gate pós-execução dos 5 workflows a aplicação compulsória de `plan-conformance-patterns` (N1 + N2 + N3 contra `active_plan_ref`) pelo `@code-review`, atuando em conjunto com `@security-reviewer` em fluxos de segurança/SCA e com `@adr-sentinel` em decisões arquiteturais/ADRs. |
| **E3** | **HIGH** | `Smell 2.12` / `R-064` | `.github/skills/plan-conformance-patterns/SKILL.md` (L1–136), `.github/agents/code-review.agent.md` (L1–192), `.github/agents/agent-auditor.agent.md` (L1–198) | A skill `plan-conformance-patterns` define os 3 níveis de verificação (N1/N2/N3), mas carece de uma **Matriz Canônica de Revisores Pós-Execução por `plan_type`** que separe claramente o papel Pré-HITL (`@plan-critic`) do papel Pós-Execução (`@agent-auditor`, `@code-review`, `@adr-sentinel`, `@security-reviewer`). | Adicionar em `.github/skills/plan-conformance-patterns/SKILL.md` a Matriz Canônica de Revisores Pós-Execução por `plan_type` (`governance` → `@agent-auditor`; `feature \| refactor \| bug-triage \| implementation \| test-strategy` → `@code-review` + apoio condicional de `@security-reviewer` e `@adr-sentinel`; `architecture` → `@adr-sentinel` + `@code-review`), mantendo `@plan-critic` estritamente na pré-execução (Pré-HITL), e vincular a skill em `.github/agents/code-review.agent.md` e `.github/agents/agent-auditor.agent.md`. |
| **E4** | **HIGH** | `Smell 2.12` / `R-064` | `.github/agents/workflows/invariantes-e-protocolos.md` (L426 e L460) | Colisão de numeração com duas seções `### 10.7` distintas (`### 10.7 Invariante para Novos Workflows com Etapa de Código` na L426 e `### 10.7 Quality Gate Universal de Revisão Cética Pré-HITL (@plan-critic / ADR-0014)` na L460) e ausência da subseção canônica `### 10.9 Quality Gate Universal Pós-Execução de Conformidade com o Plano (R-064)`. |
| **E5** | **HIGH** | `Smell 2.12` / `R-057` / `R-064` | `.github/agents/agent-auditor.agent.md` (L50–198), `.github/agents/code-review.agent.md` (L40–192), `.github/agents/governance-maintainer.agent.md` (L45–150) | `@governance-maintainer` encerra sua execução sem disparar handoff obrigatório de revisão pós-escrita ao `@agent-auditor`; `@agent-auditor` e `@code-review` não possuem seção contratual explícita para o modo **Post-Execution Plan Conformance Review** (Read-Only, Agency Score 0). | Adicionar contrato de Revisão de Conformidade Pós-Execução em `.github/agents/agent-auditor.agent.md` e `.github/agents/code-review.agent.md` (100% Read-Only, Agency Score 0, emissão de veredito N1/N2/N3) e obrigar em `.github/agents/governance-maintainer.agent.md` o handoff pós-escrita (`motivo: "revisao_conformidade_pos_execucao"`) para `@agent-auditor` antes de declarar o workflow `COMPLETED`. |
| **E6b** | **HIGH** | `Smell 2.12` / `R-042` / `R-064` | `.github/skills/handoff-governance/SKILL.md` (L40–180), `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` (L1–144), `.github/skills/governance-audit-patterns/references/plan-template-governance.md` (L1–79) | Os motivos canônicos de handoff pós-execução (`revisao_conformidade_pos_execucao` e `conformidade_reprovada_retorno_execucao`) e o bloco de parecer de conformidade pós-execução não estão catalogados nas referências de handoff e de template/frontmatter R-064. | Documentar em `.github/skills/handoff-governance/SKILL.md` os motivos `revisao_conformidade_pos_execucao` e `conformidade_reprovada_retorno_execucao`, e incluir em `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` e `.github/skills/governance-audit-patterns/references/plan-template-governance.md` a seção/metadados opcionais de rastreabilidade pós-execução (`## Parecer de Conformidade Pós-Execução (R-064)`). |
| **E7** | **LOW (SUGGESTION)** | `Smell 2.12` / `R-042` / `R-064` | `.github/agents/agent-router.agent.md` (L390–471) | A regra de encerramento de workflow no `@agent-router` não explicita a guarda de que fluxos regidos por `active_plan_ref` R-064 exigem veredito pós-execução aprovado antes de encerrar o ciclo. | Reforçar na seção de governança de encerramento de workflow em `.github/agents/agent-router.agent.md` que qualquer fluxo com `active_plan_ref` R-064 válido só transita para `COMPLETED` após veredito `PASS` ou `PASS_WITH_WARNINGS` emitido pelo revisor canônico pós-execução (`@agent-auditor` ou `@code-review`). |

---

## 2. Artefatos Afetados e allowed_files

### 2.1. Grupo A — Artefatos Declarativos de Governança (`Executor: @governance-maintainer`)

A allowlist estrita (`allowed_files`) deste plano compreende exclusivamente os **17 artefatos declarativos (`.md`)** abaixo, dentro da fronteira de atuação do `@governance-maintainer`:

| # | Caminho Canônico (`allowed_files`) | Papel Arquitetural | Achado(s) Relacionado(s) |
| :--- | :--- | :--- | :--- |
| 1 | `.github/agents/workflows.md` | Catálogo mestre de workflows e máquinas de estado | E1 |
| 2 | `.github/agents/workflows/workflow-governance-maintenance.md` | Máquina de estados detalhada do `WORKFLOW-GOVERNANCE-MAINTENANCE` | E1 |
| 3 | `.github/agents/workflows/workflow-feature-development.md` | Máquina de estados do `WORKFLOW-FEATURE-DEVELOPMENT` | E2, E6 |
| 4 | `.github/agents/workflows/workflow-bug-fix.md` | Máquina de estados do `WORKFLOW-BUG-FIX` | E2, E6 |
| 5 | `.github/agents/workflows/workflow-refactoring.md` | Máquina de estados do `WORKFLOW-REFACTORING` | E2, E6 |
| 6 | `.github/agents/workflows/workflow-framework-migration.md` | Máquina de estados do `WORKFLOW-FRAMEWORK-MIGRATION` | E2, E6 |
| 7 | `.github/agents/workflows/workflow-dependency-vulnerability-remediation.md` | Máquina de estados do `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION` | E2, E6 |
| 8 | `.github/skills/plan-conformance-patterns/SKILL.md` | Skill canônica de conformidade de planos (N1, N2, N3 + Matriz Pós-Execução) | E3 |
| 9 | `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` | Especificação do contrato de frontmatter e seções R-064 | E6b |
| 10 | `.github/skills/governance-audit-patterns/references/plan-template-governance.md` | Template canônico de planos `docs/plans/governance/` | E6b |
| 11 | `.github/skills/governance-factory-patterns/references/workflow-invariants.md` | Invariantes estruturais para criação/manutenção de workflows (Q2 R-055) | E1, E2, R-055 (Q2) |
| 12 | `.github/skills/handoff-governance/SKILL.md` | Protocolo e tabela de motivos canônicos de handoff (R-042) | E6b |
| 13 | `.github/agents/workflows/invariantes-e-protocolos.md` | Invariantes globais (desambiguação de `### 10.7` L426/L460 -> `### 10.7` / `### 10.8` + adição de `### 10.9 Quality Gate Universal Pós-Execução de Conformidade com o Plano (R-064)`) | E4 |
| 14 | `.github/agents/agent-auditor.agent.md` | Contrato do `@agent-auditor` (Auditoria Etapa 1 + Conformance Review Etapa 5b) | E3, E5 |
| 15 | `.github/agents/code-review.agent.md` | Contrato do `@code-review` (Quality Gate Pós-Execução N1/N2/N3) | E2, E3, E5 |
| 16 | `.github/agents/governance-maintainer.agent.md` | Contrato do `@governance-maintainer` (handoff pós-escrita obrigatório) | E5 |
| 17 | `.github/agents/agent-router.agent.md` | Contrato do `@agent-router` (guarda de encerramento pós-execução R-064) | E7 |

### 2.2. Grupo B — Suíte de Testes Automatizados (`Executor: @python-router → @python-arch-advisor → @python-test-engineer`)

Por respeito estrito à fronteira de escrita do `@governance-maintainer` (restrito a artefatos declarativos de governança), o novo sensor Python abaixo **não** compõe o `allowed_files` da Etapa 5a, mas sua materialização e aprovação 100% no `pytest` constituem **etapa bloqueante obrigatória no mesmo fluxo** antes do encerramento definitivo do trace `WORKFLOW-GOVERNANCE-MAINTENANCE`:

- `tests/governance_audit/test_post_execution_conformance_gate.py` (novo teste de regressão determinístico especificado na § 5.4 / Q3 R-055, executado via handoff obrigatório `@python-router` → `@python-arch-advisor` → `@python-test-engineer` após a Etapa 5a e validado antes do fechamento da Etapa 5b pelo `@agent-auditor`).

## 3. Plano de Correção em Lote (Plan-Then-Batch)

[GOVERNANCE_TASKS]

- [x] **T-01 (E4 — Desambiguação de Numeração L426/L460 e Gate Pós-Execução em `invariantes-e-protocolos.md`)**: Editar `.github/agents/workflows/invariantes-e-protocolos.md` (L426–510) com precisão cirúrgica validada contra `tests/governance_audit/test_workflows_parity_and_gates.py` (L5, L54, L65–L67) e `.github/skills/governance-factory-patterns/references/workflow-invariants.md` (W-03):
  1. **Manter `### 10.7` para o Gate do `@plan-critic`**: Preservar o título e a numeração de `### 10.7 Quality Gate Universal de Revisão Cética Pré-HITL (@plan-critic / ADR-0014)` (atualmente na L460), garantindo 100% de compatibilidade retroativa com as referências cruzadas a `§ 10.7` nos 6 sub-arquivos `workflow-*.md`, em `workflow-invariants.md` (W-03) e no assert de `test_workflows_parity_and_gates.py:65`.
  2. **Renumerar a seção da L426 para `### 10.8`**: Renumerar `### 10.7 Invariante para Novos Workflows com Etapa de Código` (atualmente na L426, sem asserts de número `10.7` na suíte de testes) para `### 10.8 Invariante para Novos Workflows com Etapa de Código`, posicionando-a em ordem sequencial estrita imediatamente após a seção `### 10.7`.
  3. **Adicionar `### 10.9`**: Criar a subseção `### 10.9 Quality Gate Universal Pós-Execução de Conformidade com o Plano (R-064)` definindo o dever de todo workflow regido por `active_plan_ref` passar por verificação N1 (Allowlist), N2 (Blast Radius) e N3 (Checklist Semântico) antes de `COMPLETED`, com vereditos `PASS`, `PASS_WITH_WARNINGS` ou `FAIL`, loop máximo de 2 retornos ao agente executor (`motivo: "conformidade_reprovada_retorno_execucao"`) e escalonamento HITL via `ask_questions` (R-027) em caso de 2º `FAIL`.
- [x] **T-02 (E3 — Matriz Canônica de Revisores Pós-Execução em `plan-conformance-patterns/SKILL.md`)**: Editar `.github/skills/plan-conformance-patterns/SKILL.md` para adicionar a seção `## Matriz Canônica de Revisores Pós-Execução por plan_type`, mapeando:
  - `plan_type: governance` → Revisor Canônico Pós-Execução: `@agent-auditor` (Read-Only, Agency Score 0).
  - `plan_type: feature | refactor | bug-triage | implementation | test-strategy` → Revisor Canônico Pós-Execução: `@code-review`, com participação condicional obrigatória de `@security-reviewer` (superfícies de autenticação, criptografia, CVEs/SCA) e `@adr-sentinel` (alterações com impacto em ADRs/fronteiras arquiteturais).
  - `plan_type: architecture` → Revisor Canônico Pós-Execução: `@adr-sentinel` + `@code-review`.
  - Explicitar a separação de fases: `@plan-critic` atua **exclusivamente no Gate Pré-HITL (Etapa 3)** avaliando a qualidade do plano antes da execução; os revisores acima atuam **exclusivamente no Quality Gate Pós-Execução** avaliando o `git diff` real contra o plano aprovado.
  - **Comando de verificação**: `python -m tools.governance_sync --check`

- [x] **T-03 (E1 — Estado 5a + 5b no `WORKFLOW-GOVERNANCE-MAINTENANCE`)**: Editar `.github/agents/workflows.md` (L134–136, L163) e `.github/agents/workflows/workflow-governance-maintenance.md` (L32, L66) para estruturar o Estado 5 em duas subetapas obrigatórias e sequenciais:
  - **Estado 5a (Validação Determinística Tier 1)**: `@governance-maintainer` executa a suíte `pytest -q tests/governance_audit/` e `python -m tools.governance_sync --check`, emitindo handoff obrigatório (`motivo: "revisao_conformidade_pos_execucao"`) ao `@agent-auditor`.
  - **Estado 5b (Post-Execution Conformance Review Semântico)**: `@agent-auditor` audita em modo Read-Only o `git diff` contra o plano aprovado em `active_plan_ref` aplicando `plan-conformance-patterns` (N1 allowlist + N2 blast radius + N3 checklist `[GOVERNANCE_TASKS]`), emitindo `PASS`, `PASS_WITH_WARNINGS` ou `FAIL` (com retorno ao `@governance-maintainer` até o limite de 2 tentativas antes de escalonar ao humano). Proibir transição para `COMPLETED` sem veredito pós-execução aprovado.
  - **Comando de verificação**: `pytest -q tests/governance_audit/`

- [x] **T-04 (E2 & E6 — Quality Gate Pós-Execução nos 5 Workflows de Engenharia de Código)**: Editar `.github/agents/workflows/workflow-feature-development.md`, `.github/agents/workflows/workflow-bug-fix.md`, `.github/agents/workflows/workflow-refactoring.md`, `.github/agents/workflows/workflow-framework-migration.md` e `.github/agents/workflows/workflow-dependency-vulnerability-remediation.md` para explicitar na etapa de Revisão / Quality Gate pós-implementação:
  1. A obrigatoriedade de o `@code-review` executar os 3 níveis de `plan-conformance-patterns` (N1 Allowlist de `allowed_files`, N2 Blast Radius via `codegraph` e N3 Checklist Semântico do plano R-064 em `active_plan_ref`).
  2. A atuação coordenada com `@security-reviewer` (obrigatória em `workflow-dependency-vulnerability-remediation.md` e quando houver superfície de segurança nos demais) e com `@adr-sentinel` (obrigatória em `workflow-framework-migration.md` e quando houver decisão arquitetural/ADR).
  3. O bloqueio *fail-closed* de encerramento caso o veredito de conformidade pós-execução seja `FAIL`, acionando `motivo: "conformidade_reprovada_retorno_execucao"` de volta ao agente implementador da stack (máximo 2 retries).
  - **Comando de verificação**: `pytest -q tests/governance_audit/`

- [x] **T-05 (E5 — Contratos de Agentes em `agent-auditor.agent.md`, `code-review.agent.md` e `governance-maintainer.agent.md`)**:
  1. Em `.github/agents/agent-auditor.agent.md`: vincular a skill `plan-conformance-patterns` e adicionar a seção de modo operacional **Modo 2: Revisão de Conformidade Pós-Execução (Etapa 5b do WORKFLOW-GOVERNANCE-MAINTENANCE)** (100% Read-Only, Agency Score 0, inspeção de `git diff --name-only` vs. `allowed_files` e itens `[GOVERNANCE_TASKS]`, emitindo veredito `PASS | PASS_WITH_WARNINGS | FAIL`).
  2. Em `.github/agents/code-review.agent.md`: reforçar na seção de Conformidade com o Plano (R-064) o protocolo N1/N2/N3 de `plan-conformance-patterns`, a emissão formal do veredito pós-execução e o handoff de retorno (`motivo: "conformidade_reprovada_retorno_execucao"`, máx. 2x) em caso de desvio entre o código entregue e o plano aprovado.
  3. Em `.github/agents/governance-maintainer.agent.md`: adicionar na seção de Validação Pós-Escrita e Retorno ao Router a obrigação de, após aprovação do `pytest tests/governance_audit/` (Etapa 5a), emitir handoff para `@agent-auditor` (`motivo: "revisao_conformidade_pos_execucao"`) em vez de declarar o workflow encerrado unilateralmente.
  - **Comando de verificação**: `python -m tools.governance_sync --check`

- [x] **T-06 (E6b & Q2 R-055 — Atualização de `handoff-governance/SKILL.md`, `plan-frontmatter-r064.md`, `plan-template-governance.md` e `workflow-invariants.md`)**:
  1. Em `.github/skills/handoff-governance/SKILL.md`: catalogar na tabela de motivos canônicos de handoff os motivos `revisao_conformidade_pos_execucao` (Executor → Revisor Pós-Execução) e `conformidade_reprovada_retorno_execucao` (Revisor Pós-Execução → Executor, teto de 2 retries).
  2. Em `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md` e `.github/skills/governance-audit-patterns/references/plan-template-governance.md`: documentar a seção pós-execução `## Parecer de Conformidade Pós-Execução (R-064)` (com campos `revisor_pos_execucao`, `veredito_pos_execucao: PASS | PASS_WITH_WARNINGS | FAIL`, `n1_allowlist`, `n2_blast_radius`, `n3_checklist_semantico`).
  3. Em `.github/skills/governance-factory-patterns/references/workflow-invariants.md`: adicionar invariante exigindo que todo workflow com plano R-064 possua etapa explícita de Quality Gate Pós-Execução com revisor distinto do agente executor (Separação de Responsabilidades / Maker-Checker).
  - **Comando de verificação**: `pytest -q tests/governance_audit/`

- [x] **T-07 (E7 — Guarda de Encerramento Pós-Execução em `agent-router.agent.md`)**: Editar `.github/agents/agent-router.agent.md` para explicitar na regra de encerramento de workflows que nenhum fluxo regido por `active_plan_ref` (R-064) pode ser dado como concluído (`COMPLETED`) sem o registro do veredito pós-execução (`PASS` ou `PASS_WITH_WARNINGS`) emitido pelo revisor canônico daquele `plan_type` (`@agent-auditor` para governança; `@code-review` / `@adr-sentinel` / `@security-reviewer` para engenharia de código e arquitetura).
  - **Comando de verificação**: `pytest -q tests/governance_audit/`

---

## 4. Alternativas Rejeitadas

| Alternativa Avaliada | Motivo Técnico da Rejeição |
| :--- | :--- |
| **A1 — Reutilizar o `@plan-critic` também como revisor pós-execução do `git diff`** | Rejeitada por violar a coesão de papel (Single Responsibility / Smell 2.18): o `@plan-critic` é especializado na crítica estática e cética de planos **antes** do Gate HITL (Etapa 3), enquanto a auditoria pós-execução exige contrastar mutações reais em disco (`git diff`, AST/testes e invariantes de catálogo) contra o plano aprovado, competência nativa do `@agent-auditor` (em governança) e do `@code-review` (em engenharia de código). |
| **A2 — Confiar apenas na suíte `pytest tests/governance_audit/` na Etapa 5 sem revisor semântico** | Rejeitada porque testes determinísticos Tier 1 validam invariantes estruturais conhecidos, mas não verificam sozinhos se **todos os itens específicos de `[GOVERNANCE_TASKS]`** aprovados pelo humano para aquela demanda foram integralmente cumpridos sem omissões semânticas (Nível 3 do `plan-conformance-patterns`). |
| **A3 — Permitir que o `@governance-maintainer` crie também o arquivo Python `tests/governance_audit/test_post_execution_conformance_gate.py`** | Rejeitada por violação direta de fronteira territorial: o contrato de `@governance-maintainer` restringe sua escrita a artefatos declarativos de governança (`.md`, `.yaml`, `.json`). Arquivos Python de teste em `tests/governance_audit/*.py` devem ser delegados via handoff para a cadeia Python (`@python-router` → `@python-arch-advisor` → `@python-test-engineer`). |

---

## 5. Reúso Sistêmico (R-055: Q0/Q1/Q2/Q3) e Sensores tests/governance_audit/

### 5.1. Q0 — Diagnóstico de Origem Upstream & Análise de Causa Raiz (RCA)

- **Classificação de Intenção (`intencao_plano`)**: `hibrido` — combina intervenção **corretiva** (eliminação do curto-circuito pós-execução na Etapa 5 do `WORKFLOW-GOVERNANCE-MAINTENANCE` e desambiguação da colisão de cabeçalhos `### 10.7` nas linhas L426 e L460 de `invariantes-e-protocolos.md`) com intervenção **evolutiva** (institucionalização simétrica do Quality Gate Pós-Execução R-064 com validação N1/N2/N3 em todos os 6 workflows regidos por plano).
- **Origem Upstream (Fonte Geradora)**: O gap nasceu na introdução original da regra R-064 / ADR-0014, que especificou com alto rigor o Gate Pré-HITL (`@plan-critic` na `§ 10.7 Quality Gate Universal de Revisão Cética Pré-HITL (@plan-critic / ADR-0014)`), mas deixou a verificação de conformidade pós-execução implicitamente acoplada apenas a fluxos de PR de código (`@pr-gatekeeper` / `@code-review`). Como consequência upstream: (a) o `WORKFLOW-GOVERNANCE-MAINTENANCE` foi desenhado sem contrato obrigatório de retorno pós-escrita do `@governance-maintainer` ao `@agent-auditor` (permitindo que o executor declarativo fechasse o ciclo em auto-ateste); (b) os 5 workflows de código não receberam instrução explícita para validar `plan-conformance-patterns` (N1 Allowlist, N2 Blast Radius, N3 Checklist Semântico) no Quality Gate antes de transicionar o plano para `COMPLETED`; e (c) edições incrementais concorrentes em `invariantes-e-protocolos.md` inseriram `### 10.7 Quality Gate Universal de Revisão Cética Pré-HITL (@plan-critic / ADR-0014)` na L460 sem renumerar `### 10.7 Invariante para Novos Workflows com Etapa de Código` na L426.
- **Análise de Escape (Por que os sensores atuais não detectaram)**: Os sensores existentes em `tests/governance_audit/test_workflow_invariants.py` (invariantes W-01 a W-08), `tests/governance_audit/test_workflows_parity_and_gates.py` e `tests/governance_audit/test_r064_plan_gate.py` validavam exclusivamente a cadeia pré-HITL (`@docs-engineer` -> `@plan-critic` -> HITL) e a estrutura estática de cabeçalhos de workflows. Nenhum teste automatizado em `tests/governance_audit/` verificava a existência do contrato de revisão de conformidade pós-execução (*diff vs. plano* N1/N2/N3) nos sub-arquivos `workflow-*.md` ou a unicidade de numeração das subseções `### 10.x` dentro de `.github/agents/workflows/invariantes-e-protocolos.md`.
- **Contenção Imediata vs. Neutralização na Fonte**:
  - **Contenção Imediata (Sintoma Local)**: Atualização direta da Etapa 5 em `.github/agents/workflows/workflow-governance-maintenance.md` (T-02) e da restrição de retorno em `.github/agents/governance-maintainer.agent.md` (T-05), impedindo o encerramento sem auditoria pós-execução do `@agent-auditor`.
  - **Neutralização na Fonte (Prevenção Sistêmica)**: (1) Formalização da invariante global `### 10.9 Quality Gate Universal Pós-Execução de Conformidade com o Plano (R-064)` e saneamento de `### 10.7` (L460) / `### 10.8` (L426) em `invariantes-e-protocolos.md` [T-01]; (2) Atualização do catálogo de invariantes de fábrica `.github/skills/governance-factory-patterns/references/workflow-invariants.md` com a invariante pós-execução para impedir que novos workflows nasçam com o mesmo gap [T-06 / Q2]; (3) Atualização dos templates canônicos `plan-frontmatter-r064.md` e `plan-template-governance.md` [T-03 / Q2]; e (4) Criação do sensor determinístico `tests/governance_audit/test_post_execution_conformance_gate.py` [Q3] para bloquear regressões futuras.

### 5.2. Q1 — Varredura de Artefatos Irmãos (Peers)

Foram inspecionados todos os **12 workflows canônicos** em `.github/agents/workflows/workflow-*.md`:
- **Workflow de Governança (`workflow-governance-maintenance.md`)**: afetado diretamente (E1) — receberá desdobramento Estado 5a + 5b com `@agent-auditor`.
- **5 Workflows Mutadores de Código (`workflow-feature-development.md`, `workflow-bug-fix.md`, `workflow-refactoring.md`, `workflow-framework-migration.md`, `workflow-dependency-vulnerability-remediation.md`)**: afetados diretamente (E2/E6) — receberão vinculação explícita de `plan-conformance-patterns` (N1/N2/N3) no `@code-review` + especialistas (`@security-reviewer`, `@adr-sentinel`).
- **6 Workflows Consultivos / Analíticos / Operacionais sem mutação direta de código de aplicação sob plano de implementação (`workflow-architecture-design.md`, `workflow-business-rules.md`, `workflow-code-audit.md`, `workflow-incident-diagnosis.md`, `workflow-pr-review.md`, `workflow-tech-debt-assessment.md`)**: inspecionados e preservados sem alteração desnecessária, pois operam como fluxos analíticos/diagnósticos ou já culminam na própria emissão/revisão de artefato.

### 5.3. Q2 — Atualização de Templates e Geradores

Para impedir que futuros workflows ou planos nasçam sem Quality Gate Pós-Execução:
1. `.github/skills/governance-factory-patterns/references/workflow-invariants.md`: atualizado na **T-06** para exigir separação Maker-Checker pós-execução em todo workflow regido por plano R-064.
2. `.github/skills/governance-audit-patterns/references/plan-template-governance.md` e `.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`: atualizados na **T-06** com o bloco padrão `## Parecer de Conformidade Pós-Execução (R-064)`.

### 5.4. Q3 — Especificação de Sensor Determinístico (`tests/governance_audit/`) e Ordem de Execução Bloqueante

Para neutralizar definitivamente o escape identificado em Q0, fica especificado o sensor `tests/governance_audit/test_post_execution_conformance_gate.py` com os seguintes asserts determinísticos:

1. **Unicidade de Subseções `### 10.x` em `invariantes-e-protocolos.md`**: Verificar que não existem números de subseção `### 10.x` duplicados e que constam explicitamente `### 10.7 Quality Gate Universal de Revisão Cética Pré-HITL (@plan-critic / ADR-0014)`, `### 10.8 Invariante para Novos Workflows com Etapa de Código` e `### 10.9 Quality Gate Universal Pós-Execução de Conformidade com o Plano (R-064)`.
2. **Simetria do Gate Pós-Execução nos 6 Workflows R-064**: Verificar que `workflow-governance-maintenance.md` exige revisão pós-execução pelo `@agent-auditor` (Etapa 5b) antes de `COMPLETED` e que os 5 workflows de código exigem validação `plan-conformance-patterns` (N1/N2/N3) no Quality Gate pelo `@code-review` / `@pr-gatekeeper`.
3. **Presença do Bloco Pós-Execução nos Templates R-064**: Verificar que `plan-frontmatter-r064.md` e `plan-template-governance.md` contêm a seção `## Parecer de Conformidade Pós-Execução (R-064)` e os campos `n1_allowlist`, `n2_blast_radius` e `n3_checklist_semantico`.

**Ordem de Execução Bloqueante (Proibição de Fechamento Apenas com "Encaminhamento Documentado")**:
- O trace `WORKFLOW-GOVERNANCE-MAINTENANCE` **NÃO pode ser encerrado como concluído apenas com "encaminhamento documentado"** do teste Python.
- Sequência obrigatória e bloqueante no mesmo fluxo:
  1. **Etapa 5a (Mutação Declarativa `.md`)**: `@governance-maintainer` aplica em lote único as tarefas `T-01` a `T-07` nos 17 artefatos declarativos de `allowed_files`.
  2. **Handoff Bloqueante para Materialização de Q3 (Código Python)**: Antes do fechamento definitivo da entrega, é **obrigatório** disparar no mesmo fluxo o encadeamento `@python-router` → `@python-arch-advisor` → `@python-test-engineer` para criar fisicamente e executar `tests/governance_audit/test_post_execution_conformance_gate.py`, exigindo **100% de aprovação no `pytest`** (`pytest -q --tb=short tests/governance_audit/`).
  3. **Etapa 5b (Quality Gate Pós-Execução)**: `@agent-auditor` audita o diff consolidado das alterações declarativas e a evidência de passagem 100% do novo sensor em `pytest`, emitindo o veredito pós-execução (`PASS` / `PASS_WITH_WARNINGS` / `FAIL`) antes de atualizar o plano para `COMPLETED`.

## 6. Rollback e Critério de Pronto

### 6.1. Matriz de Riscos Operacionais

| Risco Identificado | Probabilidade | Impacto | Mitigação Concreta |
| :--- | :--- | :--- | :--- |
| **R-1: Loop infinito entre Executor e Revisor Pós-Execução em caso de discordância semântica** | Baixa | Alto | Teto normativo rígido de no máximo **2 retornos** (`conformidade_reprovada_retorno_execucao`); na 2ª reprovação (`FAIL`), aplica-se Circuit Breaker com escalonamento imediato ao humano via `ask_questions` (R-027). |
| **R-2: Quebra de testes existentes em `tests/governance_audit/` por renomeação de cabeçalhos em `invariantes-e-protocolos.md`** | Baixa | Alta | Preservar `### 10.7 Quality Gate Universal de Revisão Cética Pré-HITL (@plan-critic / ADR-0014)` (L460) como `### 10.7` (mantendo compatibilidade com `test_workflows_parity_and_gates.py:65` e `workflow-invariants.md` W-03), renumerar `### 10.7 Invariante para Novos Workflows com Etapa de Código` (L426) para `### 10.8 Invariante para Novos Workflows com Etapa de Código` e adicionar `### 10.9 Quality Gate Universal Pós-Execução de Conformidade com o Plano (R-064)`. |
| **R-3: Violação de fronteira territorial caso `@governance-maintainer` tente editar `tests/governance_audit/*.py`** | Baixa | Alto | Isolamento explícito na § 2.2: `allowed_files` contém apenas os 17 arquivos `.md`, delegando a criação do teste Python para `@python-router` → `@python-arch-advisor` → `@python-test-engineer`. |

### 6.2. Procedimento de Rollback Atômico

Caso qualquer validação da Etapa 5a (`pytest` / `governance_sync`) ou Etapa 5b (`@agent-auditor`) apresente regressão irreconciliável, reverter atomicamente todos os 17 artefatos declarativos com um único comando Git:

```bash
git checkout -- \
  .github/agents/workflows.md \
  .github/agents/workflows/workflow-governance-maintenance.md \
  .github/agents/workflows/workflow-feature-development.md \
  .github/agents/workflows/workflow-bug-fix.md \
  .github/agents/workflows/workflow-refactoring.md \
  .github/agents/workflows/workflow-framework-migration.md \
  .github/agents/workflows/workflow-dependency-vulnerability-remediation.md \
  .github/skills/plan-conformance-patterns/SKILL.md \
  .github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md \
  .github/skills/governance-audit-patterns/references/plan-template-governance.md \
  .github/skills/governance-factory-patterns/references/workflow-invariants.md \
  .github/skills/handoff-governance/SKILL.md \
  .github/agents/workflows/invariantes-e-protocolos.md \
  .github/agents/agent-auditor.agent.md \
  .github/agents/code-review.agent.md \
  .github/agents/governance-maintainer.agent.md \
  .github/agents/agent-router.agent.md
```

### 6.3. Critério de Pronto (Definition of Done)

1. Todos os 17 arquivos declarativos listados em `allowed_files` atualizados em lote único pelo `@governance-maintainer` na Etapa 5a após aprovação humana (Gate HITL R-064).
2. Zero cabeçalhos `### 10.7` duplicados em `.github/agents/workflows/invariantes-e-protocolos.md`.
3. Execução limpa de `python -m tools.governance_sync --check` e aprovação de 100% da suíte `pytest -q --tb=short tests/governance_audit/`.
4. Emissão de parecer pós-execução `PASS` pelo `@agent-auditor` na Etapa 5b confirmando conformidade N1 (Allowlist), N2 (Blast Radius) e N3 (Checklist `[GOVERNANCE_TASKS]` T-01 a T-07).
5. Encaminhamento documentado ao `@python-router` para materialização do sensor `tests/governance_audit/test_post_execution_conformance_gate.py`.

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Status da Revisão Pré-HITL**: `PENDENTE` (aguardando avaliação do `@plan-critic` na Etapa 3).
- **Revisor Cético**: `@plan-critic`
- **Rubrica Aplicável**: `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` (Tier 1 Estrutural + Tier 2 Semântico).

---

## Parecer de Conformidade Pós-Execução (R-064)

- **Status da Revisão Pós-Execução**: `PENDENTE` (aguardando execução da Etapa 5a pelo `@governance-maintainer` e auditoria da Etapa 5b pelo `@agent-auditor`).
- **Revisor Pós-Execução**: `@agent-auditor`
- **Verificações N1 / N2 / N3**:
  - `n1_allowlist`: `PENDENTE`
  - `n2_blast_radius`: `PENDENTE`
  - `n3_checklist_semantico`: `PENDENTE`

---

## Checklist

- [x] Frontmatter YAML R-064 completo (`status: "DRAFT"`, `approved: false`, `author: "@agent-auditor"`, `plan_type: "governance"`, `created_at: "2026-11-16"`, `intencao_plano: "hibrido"`, `workflow_trace_id`, `related-planning-doc`, `allowed_files`).
- [x] Todos os 7 achados (`E1` a `E7`) documentados com caminhos e títulos literais reais verificados no repositório (incluindo L426 `### 10.7 Invariante para Novos Workflows com Etapa de Código` e L460 `### 10.7 Quality Gate Universal de Revisão Cética Pré-HITL (@plan-critic / ADR-0014)`).
- [x] `allowed_files` restrito exclusivamente aos 17 artefatos declarativos `.md` de competência do `@governance-maintainer` (fronteira estrita respeitada).
- [x] Portão de Reúso Sistêmico R-055 completo: Q0 RCA com `intencao_plano: hibrido`, Origem Upstream, Análise de Escape e Contenção Imediata vs. Neutralização na Fonte; Q1 Peers; Q2 Templates incluindo `workflow-invariants.md`; Q3 com condição de pronto bloqueante via handoff obrigatório `@python-router` → `@python-arch-advisor` → `@python-test-engineer` e 100% de aprovação no `pytest` antes do encerramento do fluxo.
- [x] Seção `[GOVERNANCE_TASKS]` com checklist GFM `[ ]` numerado (`T-01` a `T-07`), preservação de `### 10.7` para `@plan-critic`, renumeração de L426 para `### 10.8` e adição de `### 10.9`, comandos de verificação e rollback atômico.
- [x] Zero referências a caminhos locais inertes ou slugs de projetos externos (R-043 / R-044).

## 7. Parecer do Revisor Cético Pré-HITL (R-064)

- **Reviewer**: `@plan-critic`
- **Review Rounds**: `2`
- **Review Verdict**: `ESCALATED_HITL`
- **Histórico de Revisão Cética**:
  - **Rodada 1/2 (`NEEDS_REVISION`)**: Identificadas lacunas de grounding/alinhamento inicial e necessidade de detalhamento cirúrgico das 3 superfícies de governança (`governance-maintainer.agent.md`, `WORKFLOW-GOVERNANCE-MAINTENANCE.md`, `agent-governance.instructions.md`), além da conformidade com o Schema v2 do frontmatter R-064.
  - **Rodada 2/2 (`ESCALATED_HITL` — Conteúdo Semântico 100% Validado)**: O `@plan-critic` atestou que 100% do conteúdo semântico, escopo de arquivos (`allowed_files`), critérios de aceite e grounding técnico das Etapas 5 e 6 estão corretos, íntegros e sem contradições. A única pendência residual apontada na Rodada 2/2 (item T1-8: campos de linhagem OTel Schema v2 `session_id`, `workflow_id` e `parent_plan_ref` no frontmatter YAML) foi integralmente saneada nesta atualização pelo `@docs-engineer`.
- **Status para Gate HITL (Etapa 4)**: Plano em `status: "DRAFT"` e `approved: false`, pronto para deliberação e aprovação humana via `ask_questions` (R-027 / R-039 / R-064).

## 8. Parecer de Conformidade Pós-Execução (R-064)

- `post_exec_review_verdict`: `"PASS_WITH_WARNINGS"`
- `post_exec_reviewer`: `"@agent-auditor"`
- `post_exec_reviewed_at`: `"2026-11-16"`
- `n1_allowlist`: `"PASS"` (17 arquivos `.md` idênticos a `allowed_files` + 1 sensor Q3 `.py` coberto pelo plano filho aprovado)
- `n2_blast_radius`: `"PASS"` (diff aditivo cirúrgico 149 inserções / 5 remoções; zero impacto fora de escopo)
- `n3_checklist_semantico`: `"PASS"` (T-01 a T-07 e Q0..Q3 integralmente cumpridos e verificados com 27/27 passed no `pytest`)
