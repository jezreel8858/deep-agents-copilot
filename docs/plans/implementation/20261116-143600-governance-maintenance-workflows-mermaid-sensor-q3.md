---
plan_id: "20261116-143600-governance-maintenance-workflows-mermaid-sensor-q3"
plan_type: "implementation"
title: "Plano-Filho Q3 — Sensor Determinístico de Paridade Interna dos Blocos Mermaid em test_workflows_parity_and_gates.py"
status: "APPROVED"
approved: true
author: "@python-arch-advisor"
created_at: "2026-11-16"
updated_at: "2026-11-16"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
tier: "light"
reversibility_tier: "T1"
blast_radius: "low"
plan_ref: "docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md"
related-planning-doc: "docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md"
parent_plan_ref: "docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md"
allowed_files:
  - "tests/governance_audit/test_workflows_parity_and_gates.py"
rollback_plan: "git restore tests/governance_audit/test_workflows_parity_and_gates.py"
review_verdict: "PASS_WITH_NITS"
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: "PASS"
session_id: "sess-20261116-plan-lessons-harvester"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-workflows-mermaid-audit-01"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 0
  minors: 1
  nits: 1
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@python-arch-advisor"
lessons_extracted: true
lessons_applied_to: []
lessons_at: "2026-11-16"
---

# Plano de Implementação (Gate 2 / Q3) — Sensor de Paridade Interna dos Blocos Mermaid (`test_workflows_parity_and_gates.py`)

## 1. Contexto e Grounding Físico (C1)

Este plano de implementação (`plan_type: "implementation"`, `tier: "light"`) materializa a **Tarefa T4 (Neutralização na Fonte Q3)** do plano pai de governança `docs/plans/governance/20261116-143500-governance-maintenance-workflows-mermaid-parity.md`, garantindo o isolamento estrito de fronteira territorial (C3): enquanto `@governance-maintainer` atualiza exclusivamente os 11 arquivos `.md` em `.github/agents/workflows/`, a evolução do sensor automatizado em Python é delegada via `@python-router` ao `@python-test-engineer`.

### 1.1. Medição Física Real em Disco (`fs.statSync`)

| # | Caminho do Arquivo | Tamanho Real (Bytes) | Linhas Reais | Escopo da Modificação |
| :--- | :--- | :---: | :---: | :--- |
| 1 | `tests/governance_audit/test_workflows_parity_and_gates.py` | 15182 B | 259 | Adicionar helper `_extract_mermaid_blocks(text: str) -> str` e testes parametrizados validando os nós obrigatórios R-064/R-065 dentro do bloco ```mermaid``` dos workflows canônicos e de `invariantes-e-protocolos.md`. |

---

## 2. Causa-Raiz do Escape (`T2-RCA`) e Reúso Sistêmico (R-055)

- **Por que o teste atual não detectou a deriva visual**: Em `tests/governance_audit/test_workflows_parity_and_gates.py` (linhas 1–259), todas as asserções atuais operam sobre `content = path.read_text(encoding="utf-8")` completo. Como o texto em prosa das seções já continha `@docs-engineer`, `ESCALATED_HITL` e `revisao_conformidade_pos_execucao`, os testes passavam mesmo quando o bloco ```mermaid``` omitia esses estados ou possuía rotas em bypass (como a rota `Factory` em `workflow-governance-maintenance.md`).
- **Portão de Reúso (R-055)**: Reutiliza-se integralmente o arquivo `tests/governance_audit/test_workflows_parity_and_gates.py`, evitando a proliferação de novos arquivos de teste em `tests/governance_audit/`.

---

## 3. Especificação da Mudança (Tarefa T4 — `@python-test-engineer`)

Adicionar ao final de `tests/governance_audit/test_workflows_parity_and_gates.py`:

1. Função auxiliar `_extract_mermaid_content(md_text: str) -> str` usando `re.findall(r"```mermaid\s*\n(.*?)\n```", md_text, flags=re.DOTALL)`.
2. Teste parametrizado `test_workflows_mermaid_blocks_enforce_r064_materializer_and_critic_escalation` sobre os 9 workflows não isentos (`WORKFLOW-PROMPT-SYNTHESIS` é isento de `@plan-critic`):
   - Verifica que o bloco Mermaid extraído contém `docs-engineer`, `plan-critic`, `ESCALATED_HITL` e `HITL`.
3. Teste parametrizado `test_mutative_workflows_mermaid_blocks_enforce_step_5a_and_5b_conformance` sobre os 7 workflows mutativos (`workflow-bug-fix.md`, `workflow-dependency-vulnerability-remediation.md`, `workflow-feature-development.md`, `workflow-framework-migration.md`, `workflow-governance-maintenance.md`, `workflow-refactoring.md`, `workflow-ui-layout.md`):
   - Verifica que o bloco Mermaid extraído contém explicitamente `5a` e `5b`.
4. Teste específico `test_governance_maintenance_mermaid_closes_factory_bypass_and_includes_q3_python_router`:
   - Verifica no bloco Mermaid de `workflow-governance-maintenance.md` a presença de `@python-router` e que `@governance-factory` só é acionado após `HITL` (e não antes de `@docs-engineer` / `@plan-critic`), além de garantir ausência da string `### 4b / 5b.` no arquivo.

---

## 4. Alternativas Rejeitadas (C2)

1. **Alternativa A (Rejeitada) — Criar um parser AST completo da gramática Mermaid em `tools/`**:
   - *Consequência prática*: Validaria grafos direcionados completos em Python.
   - *Trade-off / Motivo da rejeição*: Complexidade desproporcional (viola R-055) quando asserções determinísticas sobre o bloco ```mermaid``` isolado e suas arestas críticas são 100% suficientes e executam em `< 50ms`.
2. **Alternativa B (Rejeitada) — Colocar esses testes em `test_markdown_ssot_counts_and_mermaid_sync.py`**:
   - *Consequência prática*: Concentraria todos os testes Mermaid em um único módulo.
   - *Trade-off / Motivo da rejeição*: `test_workflows_parity_and_gates.py` é o módulo semântico dedicado especificamente às invariantes R-064/R-065/5a/5b dos 10 workflows canônicos.

---

## 5. Blast Radius e Rollback (C2)

- **Blast Radius**: Restrito a 1 único arquivo de teste (`tests/governance_audit/test_workflows_parity_and_gates.py`, `blast_radius: "low"`, `reversibility_tier: "T1"`).
- **Ordem de Execução**: Deve ser executado **após** (ou em conjunto com) as Tarefas T1, T2 e T3 do plano pai, para que os diagramas Mermaid já estejam atualizados quando o novo sensor rodar na Subetapa `5a`.
- **Comando de Rollback**:
  ```bash
  git restore tests/governance_audit/test_workflows_parity_and_gates.py
  ```
  *(Sem uso de `git clean -f` ou remoção de arquivos em `docs/plans/**`).*

---

## 6. Verificação Executável e Cenários Gherkin (C4)

```gherkin
Funcionalidade: Sensor Automatizado de Paridade Interna dos Blocos Mermaid (Q3)

  Cenário: Detecção imediata de omissão de @docs-engineer ou 5b dentro do bloco Mermaid
    Dado o sensor "tests/governance_audit/test_workflows_parity_and_gates.py"
    Quando "pytest tests/governance_audit/test_workflows_parity_and_gates.py -q" é executado após as Tarefas T1, T2, T3 e T4
    Então 100% dos testes passam com código de saída 0
```

Comando de verificação:
```bash
pytest tests/governance_audit/test_workflows_parity_and_gates.py -q
```

---

## 7. Segurança Agentic e Isolamento Territorial (C7 / C9 / C10 — OWASP ASI01/ASI06, R-043/R-044)

- **OWASP ASI01 / ASI06**: O teste de auditoria impede regressões silenciosas nos diagramas que orientam o roteamento e os gates de segurança (`@plan-critic` e `HITL`), tratando metadados como `critic_rubric_gaps` como dados inertes.
- **Fronteira Territorial R-043 / R-044**: `allowed_files` contém exclusivamente `tests/governance_audit/test_workflows_parity_and_gates.py`, sem globs, sem referências a `.github/instructions/local/**` e utilizando `[PROJETO-ALVO]` para qualquer referência genérica (respeitada a **Exceção Única Canônica** para `<path_externo>/docs/**`).

### Especificação de Regexes com Fronteira de Palavra e Ordem Fail-Closed (Pós-Crítica)

- **Regexes de Estados Obrigatórios no Bloco Mermaid**:
  - Gate HITL (excluindo falso positivo de `ESCALATED_HITL`): `r"(?<!ESCALATED_)\bHITL\b"`
  - Subetapa 5a (Testes / Validação Determinística): `r"\b5a\b"`
  - Circuit Breaker de Autofix 5a-CB: `r"\b5a-CB\b"`
  - Subetapa 5b (Revisão de Conformidade Pós-Execução): `r"\b5b\b"`
  - Ramo de Rejeição no Gate HITL: `r"\bREJECTED\b"`
- **Verificação de Ordem Fail-Closed (`workflow-governance-maintenance.md`)**:
  - O índice da primeira ocorrência do Gate `HITL` (`r"(?<!ESCALATED_)\bHITL\b"`) no bloco Mermaid DEVE preceder a etapa de execução mutativa/sincronização de `@governance-factory` (garantindo que a rota Factory passe obrigatoriamente por `@docs-engineer` → `@plan-critic` → `HITL` antes da execução).

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Rodada**: 1 (`review_rounds: 1`)
- **Veredito**: `PASS_WITH_NITS` (`review_tier1: "PASS"`, `blockers: 0`, `majors: 0`, `minors: 1`, `nits: 1`)
- **Resolução dos Apontamentos**:
  1. **MINOR-01 (Falso Positivo de Substring `HITL` em `ESCALATED_HITL`)**: Resolvido exigindo regex com negative lookbehind e word boundary `r"(?<!ESCALATED_)\bHITL\b"`, além de `r"\b5a\b"`, `r"\b5a-CB\b"`, `r"\b5b\b"` e `r"\bREJECTED\b"`.
  2. **NIT-01 (Asserção de Precedência Fail-Closed na Rota Factory)**: Resolvido adicionando asserção explícita de que o Gate `HITL` precede a execução de `@governance-factory` no diagrama Mermaid de `workflow-governance-maintenance.md`.
