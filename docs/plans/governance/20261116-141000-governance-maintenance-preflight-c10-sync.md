---
plan_id: "20261116-141000-governance-maintenance-preflight-c10-sync"
plan_type: "governance"
status: "APPROVED"
approved: true
author: "@agent-auditor"
tier: "governance"
created_at: "2026-11-16T14:10:00Z"
updated_at: "2026-11-16T14:20:00Z"
related-planning-doc: "docs/plans/governance/20261116-123000-governance-maintenance-plan-lessons-harvester.md"
parent_plan_ref: "N/A — plano raiz"
session_id: "sess-20261116-plan-lessons-harvester"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-plan-lessons-harvester-01"
allowed_files:
  - ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md"
  - ".github/skills/plan-conformance-patterns/SKILL.md"
  - ".github/prompts/plan-lessons-harvester.prompt.md"
  - ".github/agents/governance/agent-auditor.agent.md"
  - ".github/agents/planning/feature-planner.agent.md"
  - ".github/agents/planning/refactor-planner.agent.md"
  - ".github/agents/planning/test-strategy.agent.md"
  - ".github/agents/architecture/tech-solution-architect.agent.md"
rollback_plan: "git restore .github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md .github/skills/plan-conformance-patterns/SKILL.md .github/prompts/plan-lessons-harvester.prompt.md .github/agents/governance/agent-auditor.agent.md .github/agents/planning/feature-planner.agent.md .github/agents/planning/refactor-planner.agent.md .github/agents/planning/test-strategy.agent.md .github/agents/architecture/tech-solution-architect.agent.md"
lessons_extracted: true
lessons_applied_to: []
lessons_at: "2026-11-16"
---

# Plano de Manutenção de Governança — Sincronização do Invariante `C10` e Compactação de Tokens em `planner-preflight-checklist.md` (Rodada 2)

## 1. Contexto e Objetivo

Durante a primeira execução real de colheita de lições via `/plan-lessons-harvester`, o arquivo canônico `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` recebeu a regra `C10` (Isolamento Territorial R-043/R-044 + `Exceção Única Canônica` `<path_externo>/docs/**`) e o reforço de `C4` (`source_docs_lazy` em `handoff-governance`, `agent-contracts` e `terminal-governance`).

A auditoria pós-colheita identificou dois desvios de governança que precisam ser neutralizados:
1. **Estouro de orçamento de tokens (S4 / R-029)**: `planner-preflight-checklist.md` passou de `1714 B` para `2153 B` (acima do teto `<= 1900 B` exigido pela seção `Orçamento de Contexto e Tokens (S4 / R-029)` de `plan-lessons-harvester.prompt.md`).
2. **Assimetria de ponteiros `C1`–`C9` vs `C1`–`C10`**: `SKILL.md` (linha 41), `plan-lessons-harvester.prompt.md` (linhas 15, 29 e 73) e os 5 agents planejadores (`agent-auditor`, `feature-planner`, `refactor-planner`, `test-strategy`, `tech-solution-architect`) continuaram referenciando `C1`–`C9` enquanto o arquivo-fonte já operava com `C1`–`C10`.

### 1.1 Evidência Física Capturada dos 8 `allowed_files` (Pré-Execução)

| # | Arquivo (`allowed_files`) | Existe em Disco? | Tamanho Atual (Bytes) | Linhas Totais | Linha(s) de Ocorrência (`C1`–`C9` / `C10`) | Contagem de Chars da Linha do Ponteiro |
|---|---|---|---|---|---|---|
| 1 | `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` | 2.040 B | `2153 B` | `31` | `L3` (`C1–C10`), `L22` (`C4`), `L28` (`C10`) | `L3: 90 chars`, `L22: 334 chars`, `L28: 256 chars` |
| 2 | `.github/skills/plan-conformance-patterns/SKILL.md` | 16.328 B | `4227 B` | `71` | `L41` (`invariantes C1–C9`) | `L41: 238 chars` |
| 3 | `.github/prompts/plan-lessons-harvester.prompt.md` | 11.906 B | `6259 B` | `103` | `L15` (`C1–C9`), `L29` (`C1–C9`), `L73` (`C1–C9`) | `L15: 259 chars`, `L29: 215 chars`, `L73: 245 chars` |
| 4 | `.github/agents/governance/agent-auditor.agent.md` | `true` | `24014 B` | `347` | `L39` (`invariantes C1–C9`) | `L39: 253 chars` (folga de `27 chars` até `<= 280`) |
| 5 | `.github/agents/planning/feature-planner.agent.md` | `true` | `31569 B` | `437` | `L68` (`invariantes C1–C9`) | `L68: 253 chars` (folga de `27 chars` até `<= 280`) |
| 6 | `.github/agents/planning/refactor-planner.agent.md` | `true` | `19718 B` | `304` | `L32` (`invariantes C1–C9`) | `L32: 253 chars` (folga de `27 chars` até `<= 280`) |
| 7 | `.github/agents/planning/test-strategy.agent.md` | `true` | `27539 B` | `380` | `L210` (`invariantes C1–C9`) | `L210: 253 chars` (folga de `27 chars` até `<= 280`) |
| 8 | `.github/agents/architecture/tech-solution-architect.agent.md` | `true` | `22555 B` | `365` | `L77` (`invariantes C1–C9`) | `L77: 253 chars` (folga de `27 chars` até `<= 280`) |

---

## 2. Causa-Raiz e Portão de Reúso Sistêmico (R-065 / Q0)

- **Qual sistema ou mecanismo existente deveria ter prevenido este problema?**
  1. O contrato de orçamento e sincronização em `.github/prompts/plan-lessons-harvester.prompt.md` (seção `Orçamento de Contexto e Tokens (S4 / R-029)` e Fase 3 de Consolidação), que prescrevia `<= 1900 B` mas não instruía explicitamente o executor a: (a) condensar a prosa existente antes de inserir um novo invariante `CN`, e (b) atualizar o intervalo de invariantes (`C1`–`C10`) nos ponteiros de 1 linha caso um novo código `CN` fosse criado.
  2. A suíte de auditoria automatizada `tests/governance_audit/test_plan_lessons_harvester_governance.py`, que atua como sensor de regressão da arquitetura de colheita de lições.

### 2.1 Análise de Escape (Por que o Sensor Existente Não Detectou)

A inspeção direta do código-fonte de `tests/governance_audit/test_plan_lessons_harvester_governance.py` comprova por que a suíte existente passou (`5 passed`) sem detectar a deriva e por que falhou apenas no teto de bytes quando executada isoladamente após o harvester:
1. **Escape de `C10` e tokens de `C4` no Teste `T2` (`test_t2_checklist_exists_within_budget_and_contains_c1_to_c9` — linhas 45–63)**:
   - O loop `for idx in range(1, 10): assert f"C{idx}" in content` (linhas 54–55) validava exclusivamente `C1` a `C9`, ignorando a existência de `C10` e não verificando os novos tokens obrigatórios de `C4` (`source_docs_lazy`, `handoff-governance`, `agent-contracts`, `terminal-governance`) nem os tokens de `C10` (`R-043`, `R-044`, `<path_externo>/docs/**`, `Exceção Única Canônica`).
2. **Escape de Assimetria de Ponteiros nos Testes `T3` e `T4` (linhas 66–89)**:
   - `T3` (`test_t3_prompt_exists_and_enforces_token_budget_and_schema`) checava apenas `assert CHECKLIST_REL in content`, sem verificar se o prompt referenciava `C1`–`C10` de forma consistente com o checklist.
   - `T4` (`test_t4_planners_have_single_line_pointer_within_char_budget`) filtrava `pointer_lines = [line for line in lines if CHECKLIST_REL in line]` e checava `len(pointer_lines[0]) <= 280`, mas **não asseria** `"C1`–`C10"` no texto do ponteiro de cada um dos 5 agents planejadores e **não inspecionava** o Nível 3 em `.github/skills/plan-conformance-patterns/SKILL.md` (linha 41).

### 2.2 Neutralização na Fonte (Tarefa T4 — Handoff Formal para `@python-router`)

Para cumprir integralmente a Regra da Neutralização na Fonte (R-065 / Q0 / Q3) mantendo `allowed_files` deste plano de governança 100% restrito a arquivos de governança Markdown (`C3` — proibido misturar `*.py` com `.github/agents/**`, `.github/skills/**` e `.github/prompts/**`):
- **Ação 1 (Neste plano — Tarefa T2)**: Endurecer `.github/prompts/plan-lessons-harvester.prompt.md` na Fonte (Fase 3 + Guardrails S4/R-029) exigindo re-verificação de `Buffer.byteLength <= 1900` pós-edição e sincronização do intervalo `C1`–`C10` nos ponteiros.
- **Ação 2 (Delegação Formal Q3 — Tarefa T4)**: Evoluir o sensor automatizado `tests/governance_audit/test_plan_lessons_harvester_governance.py` por meio de handoff formal para `@python-router` → `@python-test-engineer`, regido pelo plano-filho de implementação já materializado em `docs/plans/implementation/20261116-142000-governance-maintenance-preflight-c10-sensor-q3.md` (`parent_plan_ref: "docs/plans/governance/20261116-141000-governance-maintenance-preflight-c10-sync.md"`, mesmo `workflow_trace_id: "wt-20261116-plan-lessons-harvester-01"`).

---

## 3. Tarefas de Execução

| ID | Alvo | Ação | Agente Executor | Restrições |
|---|---|---|---|---|
| **T1** | `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` | Compactar redação para `<= 1900 B` (meta `~1750 B`) e `<= 40` linhas, mantendo 100% dos invariantes `C1`–`C10`, `R-043`, `R-044`, `R-065`, `Q0`, `<path_externo>/docs/**`, `Exceção Única Canônica` e `source_docs_lazy` (`handoff-governance`, `agent-contracts`, `terminal-governance`). | `@governance-maintainer` (Etapa 5 pós-HITL) | Proibido remover qualquer regra `C1`–`C10` ou token semântico auditado. |
| **T2** | `.github/skills/plan-conformance-patterns/SKILL.md` e `.github/prompts/plan-lessons-harvester.prompt.md` | Atualizar referências `C1`–`C9` para `C1`–`C10` (`SKILL.md` L41 e `plan-lessons-harvester.prompt.md` L15, L29, L73) e adicionar cláusula de verificação de bytes pós-edição na Fase 3 do prompt. | `@governance-maintainer` (Etapa 5 pós-HITL) | Manter `plan-lessons-harvester.prompt.md` enxuto e sem blocos redundantes. |
| **T3** | 5 agents planejadores (`agent-auditor`, `feature-planner`, `refactor-planner`, `test-strategy`, `tech-solution-architect`) | Atualizar o ponteiro de 1 linha de `invariantes `C1`–`C9`` para `invariantes `C1`–`C10`` (`253` → `254 chars`). | `@governance-maintainer` (Etapa 5 pós-HITL) | Linha do ponteiro `<= 280 chars` e exatamente 1 ocorrência do ponteiro por agent. |
| **T4** | `tests/governance_audit/test_plan_lessons_harvester_governance.py` (via Plano-Filho Q3) | Handoff pós-Etapa 5 para `@python-router` → `@python-test-engineer` executar `docs/plans/implementation/20261116-142000-governance-maintenance-preflight-c10-sensor-q3.md`, atualizando `T2` (`range(1, 11)` + tokens `C4`/`C10`), `T3` (`C1`–`C10` no prompt e `SKILL.md`) e `T4` (`C1`–`C10` nos 5 agents). | `@python-router` → `@python-test-engineer` | Segregação C3: executado exclusivamente sob o `allowed_files` do plano-filho de implementação. |

---

## 4. Alternativas Consideradas e Rejeitadas (C5)

1. **Aumentar o teto de `planner-preflight-checklist.md` de `1900 B` para `2500 B`**:
   - *Motivo da rejeição*: Viola diretamente a diretriz S4 / R-029 de contenção de inflação de contexto e quebraria o contrato de orçamento estabelecido no plano pai `20261116-123000-governance-maintenance-plan-lessons-harvester.md`.
2. **Incluir `tests/governance_audit/test_plan_lessons_harvester_governance.py` diretamente no `allowed_files` deste plano `plan_type: "governance"`**:
   - *Motivo da rejeição*: Viola o invariante `C3` de `planner-preflight-checklist.md`, que proíbe misturar código/testes Python (`*.py`) com arquivos de governança (`.github/agents/**`, `.github/skills/**`, `.github/prompts/**`) no mesmo plano, exigindo plano-filho vinculado (`parent_plan_ref` + mesmo `workflow_trace_id`).

---

## 5. Blast Radius e Análise de Impacto (C6)

- **Arquivos modificados neste plano**: 8 arquivos Markdown de governança listados em `allowed_files`.
- **Impacto em runtime de código**: Zero impacto em código Python ou hooks em produção.
- **Impacto nos testes de auditoria**: A compactação de `planner-preflight-checklist.md` para `<= 1900 B` restaura imediatamente o passe de `test_t2_checklist_exists_within_budget_and_contains_c1_to_c9`, enquanto o plano-filho Q3 (`20261116-142000-governance-maintenance-preflight-c10-sensor-q3.md`) evolui as asserções para cobrir `C10` e a simetria de ponteiros.

---

## 6. Estratégia de Rollback (C7)

Em caso de falha na validação pós-edição ou regressão na suíte `pytest`, reverter atomicamente os 8 arquivos via:

```bash
git restore .github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md .github/skills/plan-conformance-patterns/SKILL.md .github/prompts/plan-lessons-harvester.prompt.md .github/agents/governance/agent-auditor.agent.md .github/agents/planning/feature-planner.agent.md .github/agents/planning/refactor-planner.agent.md .github/agents/planning/test-strategy.agent.md .github/agents/architecture/tech-solution-architect.agent.md
```

---

## 7. Teste de Regressão, Verificação Executável de Tokens e Cenários Gherkin (C8)

### 7.1 Comandos de Verificação Automatizada (Node.js + Pytest)

1. **Verificação Executável de Orçamento, Tokens Semânticos (`C1`–`C10`) e Simetria de Ponteiros (Node.js)**:

```bash
node -e "const fs=require('fs'); const p='.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md'; const c=fs.readFileSync(p,'utf8'); const b=Buffer.byteLength(c,'utf8'); const lines=c.split(/\r?\n/).length; if(b>1900||lines>40) throw new Error('Budget exceeded: '+b+'B, '+lines+' lines'); const tokens=['C1','C2','C3','C4','C5','C6','C7','C8','C9','C10','R-043','R-044','R-065','Q0','<path_externo>/docs/**','Exceção Única Canônica','source_docs_lazy','handoff-governance','agent-contracts','terminal-governance']; for(const t of tokens){ if(!c.includes(t)) throw new Error('Missing token: '+t); } const ptrFiles=['.github/skills/plan-conformance-patterns/SKILL.md','.github/prompts/plan-lessons-harvester.prompt.md','.github/agents/governance/agent-auditor.agent.md','.github/agents/planning/feature-planner.agent.md','.github/agents/planning/refactor-planner.agent.md','.github/agents/planning/test-strategy.agent.md','.github/agents/architecture/tech-solution-architect.agent.md']; for(const f of ptrFiles){ const fc=fs.readFileSync(f,'utf8'); if(fc.includes('C1`–`C9')||!fc.includes('C1`–`C10')) throw new Error('Pointer drift in '+f); } console.log('ALL_CHECKS_PASSED:', b, 'bytes', lines, 'lines');"
```

2. **Execução da Suíte Pytest de Governança**:
   - `pytest tests/governance_audit/test_plan_lessons_harvester_governance.py -q`

### 7.2 Cenários Gherkin (Sucesso + Falha/Contorno)

```gherkin
Funcionalidade: Sincronização do invariante C10 e orçamento de tokens do checklist de preflight

  Cenário: Sucesso — Checklist contém C1 a C10 dentro do orçamento de 1900 bytes e ponteiros sincronizados
    Dado que ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md" inclui os invariantes "C1" até "C10" e os tokens de C4 ("source_docs_lazy", "handoff-governance", "agent-contracts", "terminal-governance")
    Quando a verificação executável Node.js e a suíte "tests/governance_audit/test_plan_lessons_harvester_governance.py" são executadas
    Então o tamanho em UTF-8 de "planner-preflight-checklist.md" é menor ou igual a 1900 bytes e possui no máximo 40 linhas
    E "SKILL.md", "plan-lessons-harvester.prompt.md" e os 5 agents planejadores referenciam "C1"–"C10" com ponteiros de 1 linha de no máximo 280 caracteres

  Cenário: Falha/Contorno — Tentativa de adicionar ou expandir invariante excedendo 1900 bytes ou quebrando ponteiro
    Dado que uma edição em "planner-preflight-checklist.md" eleva o arquivo acima de 1900 bytes ou omite o token "C10" / "source_docs_lazy"
    Quando o comando de verificação Node.js ou o teste T2 de "test_plan_lessons_harvester_governance.py" é executado
    Então a validação falha imediatamente apontando estouro de orçamento S4/R-029 ou ausência de token obrigatório
    E o rollback restaura o estado íntegro dos 8 arquivos
```

---

## 8. Segurança Agentic (OWASP ASI01 / ASI06) e Isolamento Territorial (R-043 / R-044 — C9 / C10)

- **Prevenção de Goal Hijacking (OWASP ASI01) e Memory Poisoning (OWASP ASI06)**:
  - Toda informação oriunda de planos passados ou de `handoff_summary` foi tratada como dado inerte e verificada contra o código-fonte real no disco.
  - A atualização de `planner-preflight-checklist.md` preserva apenas regras normativas declarativas curtas (`C1`–`C10`), proibindo instruções imperativas externas ou payloads executáveis.
- **Isolamento Territorial (R-043 / R-044 — C10)**:
  - Nenhum arquivo em `.github/instructions/local/**` ou `*.local.*` integra `allowed_files`.
  - Nenhum slug de projeto externo real é mencionado; o invariante `C10` utiliza exclusivamente o placeholder canônico `<path_externo>/docs/**` para documentar a `Exceção Única Canônica`.

---

## 9. Histórico de Revisão Cética Pré-HITL (`@plan-critic`)

| Rodada | Severidade | Código / Achado | Resolução Aplicada na Rodada 2 |
|---|---|---|---|
| **Rodada 1** | **BLOCKER** | `T2-RCA` — Seção 2 sem Análise de Escape explícita do sensor `test_plan_lessons_harvester_governance.py` e sem Tarefa T4 de delegação Q3 para `@python-router`. | Adicionadas as subseções `### 2.1 Análise de Escape` (com linhas exatas `L45–63` e `L66–89` do teste) e `### 2.2 Neutralização na Fonte (Tarefa T4 — Handoff Formal para @python-router)`, além da Tarefa **T4** na Seção 3 e da materialização do plano-filho `docs/plans/implementation/20261116-142000-governance-maintenance-preflight-c10-sensor-q3.md`. |
| **Rodada 1** | **MEDIUM** | `tier` no frontmatter estava definido como `"standard"` em vez de `"governance"`. | Atualizado `tier: "governance"` no frontmatter YAML deste plano. |
| **Rodada 1** | **MEDIUM** | `Verificação Executável de Tokens` — Falta de comando automatizado verificando os novos tokens de `C4` e `C10`. | Adicionado comando executável `node -e "..."` na Seção 7.1 validando `<= 1900 B`, `<= 40` linhas, todos os 20 tokens semânticos (`C1`..`C10`, `R-043`, `R-044`, `R-065`, `Q0`, `<path_externo>/docs/**`, `Exceção Única Canônica`, `source_docs_lazy`, `handoff-governance`, `agent-contracts`, `terminal-governance`) e sincronia `C1`–`C10` nos 7 arquivos consumidores. |
| **Rodada 1** | **LOW** | `Evidência Física Capturada dos 8 allowed_files` — Ausência de tabela com existência, linhas exatas e contagem de chars dos ponteiros. | Adicionada a subseção `### 1.1 Evidência Física Capturada dos 8 allowed_files (Pré-Execução)` com métricas reais extraídas via Node.js `fs`. |
