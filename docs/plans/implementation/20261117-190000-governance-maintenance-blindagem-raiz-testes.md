---
plan_id: "20261117-190000-governance-maintenance-blindagem-raiz-testes"
plan_type: "implementation"
title: "Plano de Implementação — Sensores de Teste da Blindagem do Raiz (R-068)"
status: "APPROVED"
approved: true
author: "@python-arch-advisor"
created_at: "2026-11-17"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
tier: "light"
plan_ref: "docs/plans/governance/20261117-160000-blindagem-aderencia-raiz-workflow.md"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-20261117-blindagem-raiz"
related-planning-doc: "docs/plans/governance/20261117-160000-blindagem-aderencia-raiz-workflow.md"
parent_plan_ref: "docs/plans/governance/20261117-160000-blindagem-aderencia-raiz-workflow.md"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: "PASS"
critic_rubric_gaps: []
rollback_plan: "git revert do commit do lote; pré-commit: git restore -- tests/governance_audit/test_root_instruction_file_budget.py tests/governance_audit/test_workflows_parity_and_gates.py"
allowed_files:
  - "tests/governance_audit/test_root_instruction_file_budget.py"
  - "tests/governance_audit/test_workflows_parity_and_gates.py"
---

# Plano de Implementação — Sensores de Teste da Blindagem do Raiz (R-068)

## 1. Contexto

Etapa 5 do `WORKFLOW-GOVERNANCE-MAINTENANCE` (trace `wf-20261117-blindagem-raiz`). Os 8 arquivos de governança do plano pai já foram alterados. Este plano cobre apenas os testes `.py`, executados por `@python-test-engineer` (2º passo da cadeia R-055 Q3, após `@python-arch-advisor`), com escopo estrito de `allowed_files`.

### 1.1 Estado aplicado (fonte para os limites)

| Item | Valor |
| :--- | :--- |
| Kernel `## Raiz = Executor de Workflow (R-068)` em `.github/copilot-instructions.md` | 1.209 B |
| `.github/copilot-instructions.md` | 19.001 B (baseline 17.509 B; +1.492 B); 146 linhas (< 250); medição em bytes UTF-8 (`read_bytes`), mesmo método em M1 e M2 |
| `CLAUDE.md` | índice `**R-068` e cabeçalhos R-001..R-068 |
| `routing-graph.yaml` | `gate:` em todas as 51 etapas |
| `casos-roteamento.yaml` | casos regr-029..032 inseridos |

Nota: a etapa `refinement_and_parity_testing` do `framework-migration` já tinha gate em texto livre, lido por `tests/operational_flow/test_operational_workflows.py` (~:538); o novo teste exige somente a presença da chave.

## 2. Tarefas

### 2.1 `tests/governance_audit/test_root_instruction_file_budget.py`

| # | Tarefa | Especificação |
| :--- | :--- | :--- |
| T1 | Atualizar continuidade | Docstrings (~:4, ~:44) → R-068; em `test_claude_md_normative_rules_continuity`: `max(rule_numbers) == 68` e `range(1, 69)`. |
| T2 | Teste M1 (kernel) | Extrair a seção `## Raiz = Executor de Workflow (R-068)` até o próximo `## `; assert `len(secao.encode("utf-8")) <= 2048`. |
| T3 | Teste M2 (crescimento) | `BASELINE_BYTES = 17509`; assert `len(path.read_bytes()) <= BASELINE_BYTES + 2048` para `.github/copilot-instructions.md`. M1 e M2 medidos em bytes UTF-8 (`read_bytes`; M1 via `encode("utf-8")` sobre a seção), mesmo método (CRLF/emojis). |
| T4 | Teste CLAUDE.md | Contém `**R-068` e NÃO contém o texto do loop do kernel (ex.: `Alvo = 1ª etapa`). |
| T5 | Teste termos proibidos | Asserção simples de ausência de `pulam` e `contextual/implicita` (0 ocorrências hoje) em `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/routing-graph.yaml`, `.github/agents/evals/casos-roteamento.yaml`. Sem exceções. |

### 2.2 `tests/governance_audit/test_workflows_parity_and_gates.py`

| # | Tarefa | Especificação |
| :--- | :--- | :--- |
| T6 | Teste único de gate por etapa | Percorrer a estrutura real `workflows[*].estados[*]` do `routing-graph.yaml` (cada estado com `nome`); assert `"gate" in estado` (presença, não valor), alinhado a `tests/operational_flow/test_operational_workflows.py:538`; mensagem de falha cita o `nome` do estado. Reutilizar helpers e `yaml.safe_load` existentes. Rebasear sobre o plano de 20261116 (`20261116-143600-governance-maintenance-workflows-mermaid-sensor-q3.md`), que também edita este arquivo: anexar ao final, sem alterar testes existentes. |

### 2.3 Revisão final

| # | Tarefa | Especificação |
| :--- | :--- | :--- |
| T7 | Revisão estática | `get_errors` agrupado nos 2 arquivos e releitura dos diffs. |

## 3. Riscos

| # | Risco | Mitigação |
| :--- | :--- | :--- |
| R1 | `test_governance_smells.py` usa regex `R-001\.\.R-\d{3}` (~:438–463) e varredura em ~:118 | Rodar a suíte `governance_audit` completa. |
| R2 | Testes com `67`/`R-067` literal podem falhar após T1 | R-067 (Importação de Skills) permanece válida; `test_skill_import_viability_gate.py` NÃO deve ser tocado. |
| R3 | Conflito de merge com o plano de 20261116 no mesmo arquivo | Rebasear; adicionar apenas ao final. |

## 4. Execução e Validação

Sem execução de terminal pelo agente. Comandos para o usuário:

- `pytest tests/governance_audit -q --tb=short` — valida os novos sensores e regressões.
- `pytest tests/evals -q` — evals íntegros.

## 5. Critérios de Aceite

- M1 ≤ 2048 B.
- M2 ≤ baseline + 2048 B.
- Continuidade de regras até R-068.
- Toda etapa do `routing-graph.yaml` com `gate`.
- Suíte `governance_audit` verde.
- Alterações restritas aos 2 arquivos de `allowed_files`.

## 6. Rollback

`git revert` do commit do lote; pré-commit: `git restore` dos 2 arquivos.

## 7. Incertezas (UNKNOWN)

- UNKNOWN: a prova de `gate` por estado cabe ao executor; 51 `gate:` vs 51 `nome:` no `routing-graph.yaml` é apenas indício.

## 8. Parecer do @plan-critic

### Rodada 1/2 — NEEDS_REVISION (Tier 1 FAIL)

| # | Severidade | Achado | Correção aplicada |
| :--- | :--- | :--- | :--- |
| 1 | BLOCKER | Frontmatter sem `tier` e `plan_ref` | Adicionados `tier: "light"` e `plan_ref` (R2-2: plano pai; ver Rodada 2) |
| 2 | HIGH | Placeholder `<commit-do-lote>` em `rollback_plan` | Reescrito sem `<...>` |
| 3 | MEDIUM | Números inconsistentes (linhas/bytes/método) | 146 linhas, 19.001 B, kernel 1.209 B, bytes UTF-8 em M1 e M2 |
| 4 | LOW | Exceção especulativa em T5/R4 | Removida; asserção simples de ausência |
| 5 | LOW | T6 sem estrutura real | `workflows[*].estados[*]`, `"gate" in estado`; UNKNOWN registrado |

### Rodada 2/2 — PASS_WITH_NITS (Tier 1 PASS; sem BLOCKER/HIGH; sem escalonamento)

| # | Severidade | Achado | Correção aplicada |
| :--- | :--- | :--- | :--- |
| R2-1 | MEDIUM | `plan_ref` auto-referência | Corrigido para o plano pai |
| R2-2 | LOW | Parecer persistido (frontmatter e §8); linha que cristalizava "próprio plano" | Linha da Rodada 1 corrigida; frontmatter atualizado |
| R2-3 | LOW | "51 n:" na nota da §7 | Trocado por "51 nome:" |
| R2-4 | NIT | Referência a `test_operational_workflows.py:538` | Aceitável; sem ação |

## 9. Decisão do Gate Humano (Gate 2)
- 2026-11-17: Gate humano aprovou o plano (`status: APPROVED`, `approved: true`); execução por `@python-test-engineer` restrita a `allowed_files`.
