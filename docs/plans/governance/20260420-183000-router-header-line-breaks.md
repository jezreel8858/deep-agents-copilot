---
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-04-20"
related-planning-doc: "N/A"
review_verdict: PASS_WITH_NITS
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: PASS
session_id: "sess-20260420-router-header-line-breaks"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-trace-20260420-router-header-line-breaks"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 0
  minors: 0
  nits: 1
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
allowed_files:
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/templates/router-agent.md"
  - ".github/agents/backend/database/database-router.agent.md"
  - ".github/agents/backend/ejb/ejb-router.agent.md"
  - ".github/agents/backend/python/python-router.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-router.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-router.agent.md"
  - ".github/agents/backend/struts/struts-router.agent.md"
  - ".github/agents/frontend/angular/angular-router.agent.md"
  - ".github/agents/frontend/react/react-router.agent.md"
  - ".github/skills/agent-contracts/SKILL.md"
  - "tools/headless-governance-runner/src/governance_runner/synth/evaluator.py"
  - "tools/headless-governance-runner/tests/synth_unit/test_synth_workflows_b2_extraction.py"
  - "tests/governance_audit/test_router_agents.py"
  - "docs/plans/governance/20260420-183000-router-header-line-breaks.md"
lessons_extracted: true
lessons_applied_to: ["@agent-auditor", "plan-conformance-patterns"]
lessons_at: "2026-11-15"
---

# Plano de Manutenção de Governança — Quebras de Linha no Header do Formato de Saída dos Routers

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/governance/20260420-183000-router-header-line-breaks.md`.
- O agent planejador/advisor (`@agent-auditor`) permanece **100% Read-Only**: emite o plano estruturado segundo o template canônico; a **materialização física `.md`** ocorre no step de persistência do workflow, executado por `@governance-maintainer`. O planejador NUNCA escreve o arquivo diretamente nem terceiriza edição manual ao usuário (R-057).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após aprovação humana (Gate R-064) passa a `APPROVED`/`true`.

---

## 1. Escopo da Manutenção e Achados (Diagnóstico Completo)

### 1.1 Problema de Renderização CommonMark no Header dos Routers (Smell 2.13 — Severidade: MEDIUM)

Em `.github/agents/agent-router.agent.md` (linhas 303–317), bem como no template canônico `.github/agents/templates/router-agent.md` e nos 8 supervisores de domínio (`*-router.agent.md`), os campos da seção `## Formato de Saída` (de `Agente Ativo` até `Nível de Routing` / `Confidence Score`) estão declarados como linhas adjacentes de texto puro sem prefixo de lista Markdown (`- `) nem espaçamento de parágrafo:

```markdown
Agente Ativo: <@agent delegado nesta resposta — auditoria de R-042>
Transição: <"Nova triagem (1º turno)" | "<agent-anterior> → <agent-atual> (motivo: deriva_de_intencao)" | "Sem mudança — mesmo agent do turno anterior">
Workflow: <WORKFLOW-BUG-FIX|...|N/A>
Etapa do Workflow: <1..N — nome da etapa inicial conforme workflows.md>
Rota: <bug_fix|...>
[Model] Delegando para @<agent> — modelo solicitado: <model-alvo>
Delegado: <@agent>
Motivo: <1 frase objetiva — incluir "deriva_de_intencao" se este turno veio de re-triagem>
Confiança: <alta|média|baixa>
Confidence Score: <0.00–1.00>
Nível de Routing: <rule-based|semantic|llm-based|escalonamento>
```

Quando o LLM emite esse bloco diretamente no chat da IDE (fora de code fence), o renderizador Markdown (especificação CommonMark para *soft line breaks*) colapsa quebras de linha simples (`\n`) em espaços simples dentro de um único parágrafo HTML (`<p>`), exibindo todos os metadados concatenados em uma única linha contínua e ilegível.

### 1.2 Inspeção de Parsers e Expressões Regulares (`tools/` e `tests/`)

A varredura estática em `tools/` e `tests/` identificou os pontos exatos que consomem os campos do header:

1. **`tools/headless-governance-runner/src/governance_runner/synth/evaluator.py` (linhas 47–63)**:
   - `_REGEX_WORKFLOW_STRICT` e `_REGEX_WORKFLOW_LINHA` **já aceitam** o prefixo opcional `(?:[-*+]\s+)?` antes de `Workflow:`.
   - Contudo, `_REGEX_BANNER["Delegado"]`, `_REGEX_BANNER["Rota"]` e `_REGEX_ETAPA_WORKFLOW` usam `^\s*Delegado\s*:`, `^\s*Rota\s*:` e `^\s*(?i:etapa do workflow)\s*:` ancorados no início da linha **sem** aceitar `(?:[-*+]\s+)?`. Ao converter os metadados para lista Markdown (`- Delegado: ...`, `- Rota: ...`, `- Etapa do Workflow: ...`), é obrigatório atualizar essas 3 expressões regulares em `evaluator.py` com `(?:[-*+]\s+)?` (e adicionar cobertura em `test_synth_workflows_b2_extraction.py`) para impedir regressão no extrator do runner sintético.
2. **`tools/context-insight-visualizer/generator/extractor.py` e `tests/context_insight_visualizer/test_agent_invocations.py`**:
   - Utilizam busca de substring/padrão não ancorado no início da linha para `Delegado:` e `Delegando para @`, permanecendo 100% compatíveis com prefixo `- `.
3. **`tests/governance_audit/test_router_agents.py` (linhas 180–215)**:
   - Valida a presença de `Agente Ativo: <router_name>`, `Delegado:`, `Motivo:` e `[Model] Delegando para @`. Deve ser fortalecido para exigir que os metadados após `Agente Ativo:` utilizem itens de lista Markdown (`- Transição:`, `- Delegado:`, `- Motivo:`, etc.).
4. **`tests/governance_audit/test_router_return_sync_invariants.py` e `tools/agent_router_return_sync/sync_router_return.py`**:
   - Inspecionados e **100% compatíveis** (nenhuma modificação necessária): atuam exclusivamente sobre a seção `## Retorno ao Router (R-042 — Anti Sticky-Session)` (delimitada por `ROUTER_SECTION_RE` até o próximo `## `), sem tocar na seção `## Formato de Saída` dos routers.

---

## 2. Artefatos Afetados e `allowed_files`

| Artefato | Papel | Tipo de Alteração |
|---|---|---|
| `.github/agents/agent-router.agent.md` | Orquestrador Central | Linha em branco após `Agente Ativo:` + prefixo `- ` nos campos `Transição` até `Nível de Routing` em `## Formato de Saída` |
| `.github/agents/templates/router-agent.md` | Template Canônico de Domain Router | Linha em branco após `Agente Ativo:` + prefixo `- ` nos campos `Transição` até `Confidence Score` |
| `.github/agents/backend/database/database-router.agent.md` | Domain Router (Database) | Linha em branco após `Agente Ativo:` + prefixo `- ` nos metadados do header |
| `.github/agents/backend/ejb/ejb-router.agent.md` | Domain Router (EJB) | Linha em branco após `Agente Ativo:` + prefixo `- ` nos metadados do header |
| `.github/agents/backend/python/python-router.agent.md` | Domain Router (Python) | Linha em branco após `Agente Ativo:` + prefixo `- ` nos metadados do header |
| `.github/agents/backend/spring-boot/spring-boot-router.agent.md` | Domain Router (Spring Boot) | Linha em branco após `Agente Ativo:` + prefixo `- ` nos metadados do header |
| `.github/agents/backend/spring-reactive/spring-reactive-router.agent.md` | Domain Router (Spring Reactive) | Linha em branco após `Agente Ativo:` + prefixo `- ` nos metadados do header |
| `.github/agents/backend/struts/struts-router.agent.md` | Domain Router (Struts) | Linha em branco após `Agente Ativo:` + prefixo `- ` nos metadados do header |
| `.github/agents/frontend/angular/angular-router.agent.md` | Domain Router (Angular) | Linha em branco após `Agente Ativo:` + prefixo `- ` nos metadados do header |
| `.github/agents/frontend/react/react-router.agent.md` | Domain Router (React) | Linha em branco após `Agente Ativo:` + prefixo `- ` nos metadados do header |
| `.github/skills/agent-contracts/SKILL.md` | Contrato Universal de Saída | Alinhamento documental da referência ao banner `Agente Ativo:` + lista de metadados de roteamento |
| `tools/headless-governance-runner/src/governance_runner/synth/evaluator.py` | Parser do Runner Sintético | Suporte a prefixo opcional `(?:[-*+]\s+)?` em `_REGEX_BANNER` e `_REGEX_ETAPA_WORKFLOW` |
| `tools/headless-governance-runner/tests/synth_unit/test_synth_workflows_b2_extraction.py` | Testes Unitários do Runner | Casos de teste parametrizados para `- Workflow:`, `- Etapa do Workflow:`, `- Delegado:` e `- Rota:` |
| `tests/governance_audit/test_router_agents.py` | Sensor Determinístico de Governança | Asserções garantindo linha isolada para `Agente Ativo:` e formato de lista Markdown (`- `) nos metadados do header de todos os routers |

*(Nota de inventário físico: a especificação mencionou "12 `*-router.agent.md`", porém o repositório possui exatamente 8 domain routers físicos + 1 `agent-router.agent.md` central = 9 arquivos `*-router.agent.md` ativos no catálogo, além do template `.github/agents/templates/router-agent.md`. Todos os routers físicos existentes estão cobertos acima).*

---

## 3. Plano de Correção em Lote (Plan-Then-Batch)

### 3.1 Solução Proposta para `.github/agents/agent-router.agent.md`

Manter `Agente Ativo: <...>` isolado na primeira linha, seguido de linha em branco, e formatar todos os metadados do header (`Transição` até `Nível de Routing`) como lista Markdown (`- `), preservando intactas todas as substrings exigidas pelos testes:

```markdown
## Formato de Saída

```markdown
Agente Ativo: <@agent delegado nesta resposta — auditoria de R-042>

- Transição: <"Nova triagem (1º turno)" | "<agent-anterior> → <agent-atual> (motivo: deriva_de_intencao)" | "Sem mudança — mesmo agent do turno anterior">
- Workflow: <WORKFLOW-BUG-FIX|WORKFLOW-REFACTORING|WORKFLOW-TECHNICAL-ANALYSIS|WORKFLOW-FEATURE-DEVELOPMENT|WORKFLOW-GOVERNANCE-MAINTENANCE|WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION|WORKFLOW-FRAMEWORK-MIGRATION|WORKFLOW-RELEASE-READINESS|WORKFLOW-PROMPT-SYNTHESIS|WORKFLOW-REQUIREMENTS-ELICITATION|N/A>
- Etapa do Workflow: <1..N — nome da etapa inicial conforme workflows.md>
- Rota: <bug_fix|environment_check|root_cause_analysis|code_review|security_review|performance_review|compliance|devops|code_style|requirements|feature_planning|code_summarization|codegraph_engine|specialist_advisory|specialist_implementation|database_migration|test_strategy|test_implementation|business_rules|refactor_plan|refactor_execution|pr_preparation|documentation|governance|memory_management|impact_analysis|deep_search|integration_fallback>
- [Model] Delegando para @<agent> — modelo solicitado: <model-alvo>
- Delegado: <@agent>
- Motivo: <1 frase objetiva — incluir "deriva_de_intencao" se este turno veio de re-triagem>
- Confiança: <alta|média|baixa>
- Confidence Score: <0.00–1.00>
- Nível de Routing: <rule-based|semantic|llm-based|escalonamento>
```

### 3.2 Solução Proposta para `.github/agents/templates/router-agent.md` e Domain Routers (`*-router.agent.md`)

No template canônico `.github/agents/templates/router-agent.md`:

```markdown
## Formato de Saída

```markdown
Agente Ativo: <dominio>-router

- Transição: <"Triagem de domínio" | "Handoff recebido de agent-router">
- Rota: <especialista_alvo>
- [Model] Delegando para @<agent> — modelo solicitado: <model-alvo>
- Delegado: <@<dominio>-*>
- Motivo: <1 frase justificando a escolha técnica do especialista>
- Confiança: <alta|média|baixa>
- Confidence Score: <0.00–1.00>

Entradas consideradas:
- <item 1>
- <item 2>

Próximo passo mínimo:
- <ação do especialista delegado>
```

Nos 8 domain routers físicos (`database-router`, `ejb-router`, `python-router`, `spring-boot-router`, `spring-reactive-router`, `struts-router`, `angular-router`, `react-router`), aplicar o mesmo padrão: `Agente Ativo: <dominio>-router` na primeira linha, linha em branco logo abaixo, e prefixo `- ` em `[CURRENT_STATE_LOCK: ...]`, `Transição:`, `SGBD Alvo:` / `Rota <Domínio>:`, `[Model] Delegando para @...`, `Delegado:`, `Motivo:`, `Confiança:` e `Confidence Score:`, seguido de linha em branco antes de `Entradas consideradas:`.

### 3.3 Ajuste de Compatibilidade em `evaluator.py`

Em `tools/headless-governance-runner/src/governance_runner/synth/evaluator.py`, atualizar `_REGEX_BANNER` e `_REGEX_ETAPA_WORKFLOW` para aceitar `(?:[-*+]\s+)?` opcional no início da linha (alinhado ao que `_REGEX_WORKFLOW_STRICT` já faz):

```python
_REGEX_BANNER = {
    "Delegado": re.compile(r"^\s*(?:[-*+]\s+)?(?:\*{1,2})?Delegado(?:\*{1,2})?\s*:(?:\*{1,2})?\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "Rota": re.compile(r"^\s*(?:[-*+]\s+)?(?:\*{1,2})?Rota(?:\*{1,2})?\s*:(?:\*{1,2})?\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "Agente Ativo": re.compile(r"^\s*(?:[-*+]\s+)?(?:\*{1,2})?Agente Ativo(?:\*{1,2})?\s*:(?:\*{1,2})?\s*(.+)$", re.IGNORECASE | re.MULTILINE),
}
_REGEX_ETAPA_WORKFLOW = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:\*{1,2})?(?i:etapa do workflow)(?:\*{1,2})?\s*:(?:\*{1,2})?\s*(\d+)",
    re.MULTILINE,
)
```

---

## 4. Alternativas Rejeitadas

1. **Dois espaços no final de cada linha (*hard line break* CommonMark `  \n`)**:
   - *Motivo da rejeição*: LLMs frequentemente descartam *trailing spaces* durante a geração de tokens, e formatadores/editores removem espaços em branco finais ao salvar (`trim_trailing_whitespace`), tornando a quebra de linha frágil e invisível na revisão de código.
2. **Envolver o header inteiro da resposta do router em um bloco de código (```text ... ```) no chat**:
   - *Motivo da rejeição*: Degrada a experiência visual do usuário no chat e impede a formatação rica de links/menções (`@agent`) e seções subsequentes como o Pipeline de Execução do Workflow.
3. **Inserir linha em branco dupla (`\n\n`) entre cada um dos 10 campos do header**:
   - *Motivo da rejeição*: Cria 10 parágrafos espaçados verticalmente de forma excessiva, ocupando espaço desproporcional na janela do chat em comparação a uma lista Markdown compacta (`<ul><li>`).

---

## 5. Reúso Sistêmico (R-055: Q1/Q2/Q3) e Sensores `tests/governance_audit/`

- **Q1 (Impacto em Artefatos Irmãos / Peers)**:
  - Além do `agent-router.agent.md`, todos os supervisores de domínio (`database-router`, `ejb-router`, `python-router`, `spring-boot-router`, `spring-reactive-router`, `struts-router`, `angular-router`, `react-router`) possuem exatamente a mesma estrutura de `## Formato de Saída` e sofrem do mesmo colapso de linha em CommonMark. O lote aplica a padronização de forma atômica em todos os routers do catálogo.
- **Q2 (Atualização de Templates e Contratos Canônicos)**:
  - Atualização de `.github/agents/templates/router-agent.md` para que novos domain routers criados pelo `@governance-factory` já nasçam com lista Markdown no header de saída.
  - Alinhamento de `.github/skills/agent-contracts/SKILL.md` documentando a separação por linha em branco após `Agente Ativo:` e o uso de lista Markdown para os campos de telemetria/transição de roteamento.
- **Q3 (Sensor Determinístico no Pytest)**:
  - Atualização de `tests/governance_audit/test_router_agents.py` para validar que o bloco `## Formato de Saída` de `agent-router.agent.md`, `templates/router-agent.md` e de todos os `*-router.agent.md` mantém `Agente Ativo:` isolado na primeira linha e formata os campos de metadados subsequentes (`- Transição:`, `- Delegado:`, `- Motivo:`, `- Confiança:`, `- Confidence Score:`) com prefixo `- `.
  - Atualização de `tools/headless-governance-runner/tests/synth_unit/test_synth_workflows_b2_extraction.py` testando a extração de `capturar_workflow` e `capturar_rota` com itens prefixados por `- `.

---

## 6. Rollback e Critério de Pronto

- **Plano de Rollback**: Reversão atômica restrita exatamente aos caminhos declarados em `allowed_files` via:
  ```bash
  git checkout -- \
    .github/agents/agent-router.agent.md \
    .github/agents/templates/router-agent.md \
    .github/agents/backend/database/database-router.agent.md \
    .github/agents/backend/ejb/ejb-router.agent.md \
    .github/agents/backend/python/python-router.agent.md \
    .github/agents/backend/spring-boot/spring-boot-router.agent.md \
    .github/agents/backend/spring-reactive/spring-reactive-router.agent.md \
    .github/agents/backend/struts/struts-router.agent.md \
    .github/agents/frontend/angular/angular-router.agent.md \
    .github/agents/frontend/react/react-router.agent.md \
    .github/skills/agent-contracts/SKILL.md \
    tools/headless-governance-runner/src/governance_runner/synth/evaluator.py \
    tools/headless-governance-runner/tests/synth_unit/test_synth_workflows_b2_extraction.py \
    tests/governance_audit/test_router_agents.py
  ```
- **Critério de Pronto (DoD)**:
  1. `pytest tests/governance_audit/test_router_agents.py tests/governance_audit/test_router_return_sync_invariants.py tests/governance_audit/test_pre_hitl_skeptical_plan_gate.py` com 100% de aprovação.
  2. Caso de teste explícito em `tools/headless-governance-runner/tests/synth_unit/test_synth_workflows_b2_extraction.py` que importa, compila sem `re.error` e executa `_REGEX_BANNER["Delegado"]`, `_REGEX_BANNER["Rota"]`, `_REGEX_BANNER["Agente Ativo"]` e `_REGEX_ETAPA_WORKFLOW` contra linhas prefixadas com `- ` (ex.: `- Delegado: @python-router`, `- Rota: specialist_implementation`, `- Etapa do Workflow: 1`, incluindo variações com `*bold*`/`**bold**`).
  3. `pytest tools/headless-governance-runner/tests/synth_unit/test_synth_workflows_b2_extraction.py tests/context_insight_visualizer/test_agent_invocations.py` com 100% de aprovação.
  4. Zero regressões na suíte completa de auditoria de governança (`pytest tests/governance_audit/`).

---

## Parecer do Revisor Cético Pré-HITL (R-064)
- **Tier 1 (Determinístico)**: `PASS`
- **Tier 2 (`@plan-critic`)**: `PASS_WITH_NITS` (`review_rounds: 2`, 0 BLOCKER, 0 HIGH, 0 MEDIUM, 1 NIT)
- **Findings e Resoluções**:
  - **Rodada 1 (`NEEDS_REVISION`, 1 HIGH)** — Cobertura de teste determinístico do regex do extrator B2 (`tools/headless-governance-runner/tests/synth_unit/test_synth_workflows_b2_extraction.py`): resolvido na Rodada 2 com inclusão do arquivo em `allowed_files` e especificação do caso de teste unitário verificando compilação e extração com prefixo `- `.
  - **Rodada 2 (`PASS_WITH_NITS`, 0 BLOCKER, 0 HIGH, 1 NIT)** — `NIT-001`: observação menor não-bloqueante registrada pelo `@plan-critic`; plano apto para apresentação no gate HITL (`status: DRAFT`, `approved: false`).

## Checklist

- [x] Frontmatter R-064 completo (`plan_type: governance`, `status: DRAFT`, `approved: false`).
- [x] Persistência por `@governance-maintainer`; código e catálogos em `.github/` e `tests/` intocados antes do HITL (R-057 / R-064).
- [x] Conformidade com `docs/plans/governance/` auditada (Smell 2.34).
