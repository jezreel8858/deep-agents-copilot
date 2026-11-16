---
plan_id: "20261116-142000-governance-maintenance-preflight-c10-sensor-q3"
plan_type: "implementation"
status: "APPROVED"
approved: true
author: "@python-arch-advisor"
tier: "light"
created_at: "2026-11-16T14:20:00Z"
updated_at: "2026-11-16T14:20:00Z"
related-planning-doc: "docs/plans/governance/20261116-141000-governance-maintenance-preflight-c10-sync.md"
parent_plan_ref: "docs/plans/governance/20261116-141000-governance-maintenance-preflight-c10-sync.md"
session_id: "sess-20261116-plan-lessons-harvester"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-plan-lessons-harvester-01"
allowed_files:
  - "tests/governance_audit/test_plan_lessons_harvester_governance.py"
rollback_plan: "git restore tests/governance_audit/test_plan_lessons_harvester_governance.py"
lessons_extracted: true
lessons_applied_to: []
lessons_at: "2026-11-16"
---

# Plano de Implementação (Plano-Filho Q3) — Evolução do Sensor `test_plan_lessons_harvester_governance.py` para Invariante `C10` e Simetria de Ponteiros

## 1. Contexto e Escopo (C1 / C2 / C3)

Este plano-filho de implementação materializa a **Delegação Formal Q3 (Tarefa T4)** originada do plano de governança pai `docs/plans/governance/20261116-141000-governance-maintenance-preflight-c10-sync.md` (sob o mesmo `workflow_trace_id: "wt-20261116-plan-lessons-harvester-01"`).

Em estrita conformidade com o invariante `C3` de `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` (Segregação de Domínios), a evolução do arquivo Python `tests/governance_audit/test_plan_lessons_harvester_governance.py` é segregada neste plano `plan_type: "implementation"` para execução pelo domínio Python (`@python-router` → `@python-test-engineer`).

### 1.1 Evidência Física do Alvo (`allowed_files`)

| Arquivo (`allowed_files`) | Existe em Disco? | Linhas Totais | Funções de Teste Atuais |
|---|---|---|---|
| `tests/governance_audit/test_plan_lessons_harvester_governance.py` | `true` | `103` | `test_t1_catalog_registers_plan_lessons_harvester` (L34), `test_t2_checklist_exists_within_budget_and_contains_c1_to_c9` (L45), `test_t3_prompt_exists_and_enforces_token_budget_and_schema` (L66), `test_t4_planners_have_single_line_pointer_within_char_budget` (L80), `test_t5_plan_frontmatter_documents_lessons_fields` (L92) |

---

## 2. Causa-Raiz (RCA Q0), Análise de Escape e Neutralização na Fonte (R-065 / C2)

- **Qual sistema ou mecanismo existente deveria ter prevenido este problema?**
  A suíte de regressão `tests/governance_audit/test_plan_lessons_harvester_governance.py`, criada especificamente para auditar o contrato de colheita de lições (`/plan-lessons-harvester`), o orçamento S4/R-029 do checklist e a consistência dos ponteiros nos agents planejadores.
- **Análise de Escape (Por que o sensor existente não detectou a deriva semântica)**:
  1. Na linha 54 de `test_plan_lessons_harvester_governance.py`, o teste `T2` executava `for idx in range(1, 10): assert f"C{idx}" in content`, verificando apenas `C1`..`C9`. Quando `C10` (Isolamento R-043/R-044 + `Exceção Única Canônica`) e o reforço de `C4` (`source_docs_lazy`) foram introduzidos em `planner-preflight-checklist.md`, `T2` não auditava a presença de `C10` nem dos tokens de `C4`/`C10`.
  2. Nas linhas 66–89, `T3` e `T4` validavam apenas a presença da substring `planner-preflight-checklist.md` e o teto `<= 280 chars`, sem asserir se o intervalo anunciado nos ponteiros (`C1`–`C10`) correspondia ao último invariante real do checklist e sem auditar o Nível 3 de `.github/skills/plan-conformance-patterns/SKILL.md` (linha 41).
- **Neutralização na Fonte**:
  Atualizar diretamente `tests/governance_audit/test_plan_lessons_harvester_governance.py` para validar `C1`..`C10`, os tokens obrigatórios de `C4` e `C10`, e a presença de `C1`–`C10` no prompt, na `SKILL.md` e nos 5 agents planejadores.

---

## 3. Tarefas de Implementação

| ID | Arquivo Alvo | Modificação | Executor |
|---|---|---|---|
| **T1** | `tests/governance_audit/test_plan_lessons_harvester_governance.py` | Em `T2` (`L45–63`), atualizar o loop para `for idx in range(1, 11): assert f"C{idx}" in content` e asserir os tokens de `C4` (`"source_docs_lazy"`, `"handoff-governance"`, `"agent-contracts"`, `"terminal-governance"`) e de `C10` (`"R-043"`, `"R-044"`, `"<path_externo>/docs/**"`, `"Exceção Única Canônica"`). | `@python-test-engineer` |
| **T2** | `tests/governance_audit/test_plan_lessons_harvester_governance.py` | Em `T3` (`L66–77`), asserir que `.github/prompts/plan-lessons-harvester.prompt.md` e `.github/skills/plan-conformance-patterns/SKILL.md` referenciam `"C1`–`C10"` e não contêm a referência defasada `"C1`–`C9"`. | `@python-test-engineer` |
| **T3** | `tests/governance_audit/test_plan_lessons_harvester_governance.py` | Em `T4` (`L80–89`), asserir que a linha do ponteiro em cada um dos 5 agents planejadores (`PLANNERS`) contém `"C1`–`C10"` além de respeitar `len(pointer_lines[0]) <= 280`. | `@python-test-engineer` |

---

## 4. Alternativas Consideradas e Rejeitadas (C5)

1. **Criar um segundo arquivo de teste separado (`test_plan_lessons_harvester_c10.py`)**:
   - *Motivo da rejeição*: Fragmentaria as invariantes do mesmo subsistema (`plan-lessons-harvester`) em dois arquivos distintos e manteria asserções obsoletas (`range(1, 10)`) no arquivo original.
2. **Validar apenas via script ad-hoc de terminal sem atualizar o `pytest`**:
   - *Motivo da rejeição*: Viola a Regra da Neutralização na Fonte (R-065 / Q0 / Q3), pois deixaria o sensor permanente de CI cego a regressões futuras de `C10` e de deriva nos ponteiros.

---

## 5. Blast Radius e Análise de Impacto (C6)

- **Arquivos modificados**: Exclusivamente `tests/governance_audit/test_plan_lessons_harvester_governance.py` (1 arquivo).
- **Dependência de Ordem de Execução**: Deve ser executado após a conclusão da Etapa 5 do plano pai `20261116-141000-governance-maintenance-preflight-c10-sync.md` (quando os 8 arquivos Markdown já estiverem sincronizados em `C1`–`C10` e `<= 1900 B`).

---

## 6. Estratégia de Rollback (C7)

Reversão imediata e isolada do arquivo de teste caso haja falha inesperada na suíte:

```bash
git restore tests/governance_audit/test_plan_lessons_harvester_governance.py
```

---

## 7. Teste de Regressão e Cenários Gherkin (C8)

### 7.1 Comando de Validação

```bash
pytest tests/governance_audit/test_plan_lessons_harvester_governance.py -q
```

### 7.2 Cenários Gherkin (Sucesso + Falha/Contorno)

```gherkin
Funcionalidade: Sensor automatizado de auditoria de C1-C10 e simetria de ponteiros

  Cenário: Sucesso — Suíte aprova checklist <= 1900 B com C1-C10 e ponteiros sincronizados
    Dado que "planner-preflight-checklist.md" possui tamanho <= 1900 bytes e contém C1 a C10 e os tokens de C4/C10
    E "SKILL.md", "plan-lessons-harvester.prompt.md" e os 5 agents planejadores referenciam "C1"–"C10"
    Quando "pytest tests/governance_audit/test_plan_lessons_harvester_governance.py -q" é executado
    Então todos os 5 testes (T1 a T5) passam com código de saída 0

  Cenário: Falha/Contorno — Sensor detecta regressão de ponteiro para C1-C9 ou remoção de C10
    Dado que um dos 5 agents planejadores ou "SKILL.md" regride o ponteiro para "C1"–"C9" ou "C10" é removido do checklist
    Quando "pytest tests/governance_audit/test_plan_lessons_harvester_governance.py -q" é executado
    Então o pytest falha com AssertionError identificando exatamente o arquivo ou token ausente
```

---

## 8. Segurança Agentic (OWASP ASI01 / ASI06) e Isolamento Territorial (R-043 / R-044 — C9 / C10)

- **OWASP ASI01 / ASI06**: O teste realiza apenas leitura estática (`Path.read_text(encoding="utf-8")`) e asserções determinísticas de substrings/tamanhos em arquivos versionados do repositório, sem execução dinâmica de conteúdo lido (`eval`/`exec`).
- **Isolamento Territorial (R-043 / R-044 — C10)**: `allowed_files` contém exclusivamente `tests/governance_audit/test_plan_lessons_harvester_governance.py`, sem qualquer referência a `.github/instructions/local/**`, `*.local.*` ou slugs de projetos locais externos (usando apenas o placeholder canônico `<path_externo>/docs/**`).
