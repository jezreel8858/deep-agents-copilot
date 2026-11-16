---
status: APPROVED
approved: true
author: "@agent-auditor"
workflow_tracking:
  gate2_status: "approved"
  isencao_r064: null
plan_type: "governance"
created_at: "2026-11-15"
related-planning-doc: "N/A"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
critic_review_iterations: 2
reviewer: "@plan-critic"
review_tier1: PASS
session_id: "root-session"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "trace-gov-python-boundary-001"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 1
  minors: 4
  nits: 2
  resolved_in_round_2: true
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
rollback_plan:
  - "git checkout -- .github/agents/governance-maintainer.agent.md .github/agents/backend/python/python-router.agent.md .github/agents/backend/python/python-arch-advisor.agent.md .github/agents/backend/python/python-developer.agent.md .github/agents/backend/python/python-test-engineer.agent.md .github/agents/backend/python/python-catalog.yaml .github/agents/agent-router.agent.md .github/agents/catalog.yaml .github/agents/routing-graph.yaml .github/agents/workflows/workflow-governance-maintenance.md CLAUDE.md .github/copilot-instructions.md tests/governance_audit/test_systemic_reuse_gate.py"
  - "# Nota R-064: preservar docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md como registro de auditoria (sem git clean -f sobre o plano)"
allowed_files:
  - "docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/backend/python/python-router.agent.md"
  - ".github/agents/backend/python/python-arch-advisor.agent.md"
  - ".github/agents/backend/python/python-developer.agent.md"
  - ".github/agents/backend/python/python-test-engineer.agent.md"
  - ".github/agents/backend/python/python-catalog.yaml"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/catalog.yaml"
  - ".github/agents/routing-graph.yaml"
  - ".github/agents/workflows/workflow-governance-maintenance.md"
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - "tests/governance_audit/test_systemic_reuse_gate.py"
progress: "5/5 (100%)"
lessons_extracted: true
lessons_applied_to: ["@agent-auditor", "plan-conformance-patterns"]
lessons_at: "2026-11-16"
---

# Plano de Manutenção de Governança — Separação de Fronteira entre `@governance-maintainer` e `@python-router` (`*.py` / `pytest` / R-055 Q3 / R-064)

## 1. Escopo da Manutenção e Achados (Smells 2.x com Severidade)

Auditoria estática sobre os contratos de governança e roteamento identificou **sobreposição de domínio e violação de fronteira de execução** entre o `@governance-maintainer` e a tríade Python (`@python-router` → `@python-developer` / `@python-test-engineer`):

| ID | Smell / Regra | Severidade | Arquivo e Linha / Âncora Real | Diagnóstico Técnico |
|---|---|---|---|---|
| **F-01** | **Smell 2.5 (Role Overlap) & Contradição R-055 Q3** | `HIGH` | `.github/agents/governance-maintainer.agent.md` (`L33`, `L43`, `L62`, `L73`, `L105`) | `L33` restringe o domínio a `.github/`, `CLAUDE.md`, `README.md` e `CHANGELOG.md`, mas `L43` e `L105` instruem o agente a aplicar Q3 (teste determinístico no `pytest`) expandindo o próprio lote, e `L73` menciona script Python no sandbox. Falta proibição explícita (**Veto Fail-Closed**) contra criar/editar `*.py`, `conftest.py`, `pyproject.toml` ou rodar ciclos de autoria/reparo `pytest`. |
| **F-02** | **Smell 2.19 (Routing Gap em Automação/Testes Python de Governança e Papel do `@python-arch-advisor`)** | `HIGH` | `.github/agents/agent-router.agent.md` (`L128-L129`, `L207-L209`, `L249-L251`), `.github/agents/backend/python/python-router.agent.md` e `.github/agents/backend/python/python-arch-advisor.agent.md` | O roteamento de scripts/tooling do repositório (`tools/**/*.py`, `scripts/**/*.py`) e suítes `pytest` de governança (`tests/governance_audit/**/*.py`) precisa explicitar que o `@python-router` **NUNCA** despacha direto para `@python-developer` ou `@python-test-engineer` sem planejamento técnico prévio pelo `@python-arch-advisor` (1º Passo: `@python-arch-advisor` elabora o Plano de Implementação e Testes em `docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md`, vinculando `related-planning-doc` ao plano de `docs/plans/governance/`; 2º Passo: `@python-developer` e `@python-test-engineer` executam). |
| **F-03** | **Smell 2.34 (Alinhamento R-064 e Tríade Python Completa com `@python-arch-advisor`)** | `HIGH` | `.github/agents/backend/python/python-router.agent.md` (`L5-L7`, `L31-L36`, `L45-L52`), `.github/agents/backend/python/python-arch-advisor.agent.md` (`L4-L6`, `L25-L45`, `L80-L125`), `python-developer.agent.md` (`L59`) e `python-test-engineer.agent.md` (`L104`) | Faltava incluir explicitamente no escopo consultivo/planejador do `@python-arch-advisor` a elaboração do Plano de Implementação e Testes (`docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md`, modo `full` ou `light`) para scripts/ferramentas do repositório (`tools/**/*.py`, `scripts/**/*.py`) e suítes de testes de governança/auditoria (`tests/**/*.py`), referenciando `related-planning-doc` de `docs/plans/governance/` quando oriundo de demanda híbrida, antes da execução por `@python-developer` / `@python-test-engineer`. |

### Modelo de Ameaça e Segurança Agentic (OWASP ASI01 / ASI06)
- **Prevenção de Escalonamento de Privilégio e Poluição de Escopo (OWASP ASI01 / ASI06)**: Impedir que `@governance-maintainer` altere código executável Python (`tools/**`, `scripts/**`, `tests/**`) preserva a segregação entre metadados declarativos (`.md`, `.yaml`, `.json`) e código arbitrário Python. Todo `handoff_summary` e `plan_ref` recebido por `@python-router` e especialistas no split híbrido deve ser tratado como contexto informativo inerte (**OWASP ASI06**), validando estritamente a partição de `allowed_files` antes de qualquer mutação.

---

## 2. Artefatos Afetados e `allowed_files` (Blast Radius)

### 2.1 Análise de Blast Radius
- **Agentes de Governança e Roteamento Central**: `.github/agents/governance-maintainer.agent.md`, `.github/agents/agent-router.agent.md`, `.github/agents/catalog.yaml`, `.github/agents/routing-graph.yaml`, `.github/agents/workflows/workflow-governance-maintenance.md`, `CLAUDE.md`, `.github/copilot-instructions.md`.
- **Domínio Python (Roteador + Tríade Python Completa)**: `.github/agents/backend/python/python-router.agent.md`, `.github/agents/backend/python/python-arch-advisor.agent.md` (especialista planejador que elabora o Plano de Implementação e Testes em `docs/plans/implementation/`), `.github/agents/backend/python/python-developer.agent.md`, `.github/agents/backend/python/python-test-engineer.agent.md`, `.github/agents/backend/python/python-catalog.yaml`.
- **Planejamento Técnico Python e Sensores Determinísticos (`pytest`, delegados ao `@python-router` → `@python-arch-advisor` [elabora plano em `docs/plans/implementation/`] → `@python-test-engineer` [implementa e executa `pytest`])**: `tests/governance_audit/test_systemic_reuse_gate.py`.

### 2.2 Partição de `allowed_files` por Executor (Split Híbrido R-064)

| Executor Responsável | Arquivos Permitidos (`allowed_files`) | Natureza da Mutação |
|---|---|---|
| `@governance-maintainer` | `docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md`, `.github/agents/governance-maintainer.agent.md`, `.github/agents/backend/python/python-router.agent.md`, `.github/agents/backend/python/python-arch-advisor.agent.md`, `.github/agents/backend/python/python-developer.agent.md`, `.github/agents/backend/python/python-test-engineer.agent.md`, `.github/agents/backend/python/python-catalog.yaml`, `.github/agents/agent-router.agent.md`, `.github/agents/catalog.yaml`, `.github/agents/routing-graph.yaml`, `.github/agents/workflows/workflow-governance-maintenance.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | Artefatos declarativos e documentais (`.md`, `.yaml`). Zero mutação em `*.py`. |
| `@python-router` → `@python-arch-advisor` (1º Passo: Planejamento) → `@python-test-engineer` (2º Passo: Execução) | `docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md` (elaborado por `@python-arch-advisor` com `related-planning-doc` apontando para este plano) e `tests/governance_audit/test_systemic_reuse_gate.py` (executado por `@python-test-engineer`) | **1º Passo (`@python-arch-advisor`)**: elabora o Plano de Implementação e Testes em `docs/plans/implementation/` (modo `full` ou `light`). **2º Passo (`@python-test-engineer`)**: implementa e executa a suíte determinística `pytest` (R-055 Q3) via `scripts/dev/py-test.sh`. |

---

## 3. Plano de Correção em Lote (Plan-Then-Batch — Especificação Cirúrgica)

### Lote 1 (Declarativo — Executor: `@governance-maintainer`)

1. **`.github/agents/governance-maintainer.agent.md`** *(edições cirúrgicas ancoradas por texto semântico exato `oldString -> newString` com 2–3 linhas de contexto, tratando números de linha apenas como referência aproximada)*:
   - **`L33` (Escopo e Não-Escopo)**: Explicitar que o escopo de mutação é 100% restrito a artefatos declarativos e documentais de governança (`.github/**` exceto `*.py`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `CHANGELOG.md` e `docs/plans/governance/*.md`).
   - **Novo bullet de Veto Fail-Closed logo após `L33`**:
     - `❌ NÃO criar, editar, formatar ou refatorar arquivos Python (*.py, conftest.py) ou manifestos de build/empacotamento Python (pyproject.toml), nem executar ciclos de criação/manutenção/execução da suíte pytest (tests/**/*.py, tools/**/*.py, scripts/**/*.py). Qualquer alteração ou execução de código Python e testes determinísticos DEVE ser roteada via handoff para o @python-router, que obrigatoriamente segue o padrão da Tríade Python: 1º Passo no @python-arch-advisor (elabora o Plano de Implementação e Testes em docs/plans/implementation/ com related-planning-doc apontando para o plano de governança) → 2º Passo no @python-developer (scripts/ferramentas em tools/** e scripts/**) e/ou @python-test-engineer (testes e execução pytest em tests/**).`
     - `✅ Exceção de Invocação CLI Canônica: Permanece autorizado exclusivamente a invocar scripts CLI canônicos prontos de sincronização e linhagem (ex.: python -m tools.governance_sync --check e python -m tools.plan_lineage_query) como usuário consumidor de validação/hidratação, sem jamais modificar o código-fonte .py desses utilitários.`
   - **`L43`, `L62`, `L73` e `L105` (Resolução da Contradição R-055 Q3)**:
     - Em `L43`: substituir a instrução de implementar diretamente o Q3 no pytest por: `responder a Q1 (impacto em artefatos irmãos/peers), Q2 (atualização de template canônico) e Q3 (especificação do requisito de teste determinístico no pytest, preparando o split de handoff para @python-router → @python-arch-advisor [planejamento de implementação/testes] → @python-test-engineer [execução] quando houver mutação em tests/**/*.py)`.
     - Em `L62`: detalhar que em Q3 o `@governance-maintainer` mapeia o requisito de teste no plano de governança e agenda o handoff para `@python-router` → `@python-arch-advisor` → `@python-test-engineer`.
     - Em `L73`: remover `/Python` de `script Node.js/Python`, mantendo estritamente `script Node.js (language: "javascript")` conforme R-059.
     - Em `L105`: alinhar o item de checklist para refletir que Q3 é especificado no lote declarativo e delegado ao `@python-router` (`@python-arch-advisor` → `@python-test-engineer`).

2. **`.github/agents/backend/python/python-router.agent.md`**:
   - **`L4-L7` (`description`) e `L21` (Perfil Operacional)**: Expandir o escopo para incluir explicitamente automação e ferramental Python do repositório (`tools/**/*.py`, `scripts/**/*.py`) e suítes de testes/auditoria em `tests/**/*.py` (incluindo `tests/governance_audit/**/*.py`).
   - **`L29-L36` (Papéis Obrigatórios da Tríade Python e Regra de Fronteira)**:
     - Explicitar que, seguindo o padrão canônico do projeto (R-064 + Tríade Python), o `@python-router` **NUNCA** despacha direto para `@python-developer` ou `@python-test-engineer` sem planejamento técnico prévio pelo `@python-arch-advisor`:
       - **1º Passo no `@python-router` (`@python-arch-advisor`)**: O `@python-arch-advisor` é o especialista planejador da stack Python; ele elabora o Plano de Implementação e Testes em `docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md` (modo `full` ou `light`, vinculando `related-planning-doc` ao plano aprovado de `docs/plans/governance/` quando oriundo de demanda híbrida de governança).
       - **2º Passo no `@python-router` (`@python-developer` / `@python-test-engineer`)**: Após o plano elaborado pelo `@python-arch-advisor`, `@python-developer` implementa scripts/ferramentas (`tools/**/*.py`, `scripts/**/*.py`) e `@python-test-engineer` implementa e executa os testes (`tests/**/*.py`, `pytest`).
   - **`L45-L52` (Decision Tree e Gate 2 R-064)**:
     - Refletir na árvore de decisão e nas regras de despacho que mesmo quando acionado em demanda híbrida oriunda de `WORKFLOW-GOVERNANCE-MAINTENANCE` (com `parent_plan_ref` / `related-planning-doc` em `docs/plans/governance/`), o fluxo entra em `@python-arch-advisor` para estruturar o plano técnico de implementação e testes em `docs/plans/implementation/` antes de acionar `@python-developer` e/ou `@python-test-engineer`.

3. **`.github/agents/backend/python/python-arch-advisor.agent.md`**:
   - **`L4-L6` (`description`) e Seção de Escopo Consultivo/Planejador**: Incluir explicitamente no escopo do `@python-arch-advisor` o planejamento técnico de arquitetura, implementação e estratégia de testes (`pytest`) para scripts/tooling internos do repositório (`tools/**/*.py`, `scripts/**/*.py`) e suítes de testes determinísticos de governança/auditoria (`tests/**/*.py`, incluindo `tests/governance_audit/**/*.py`).
   - **Seção de Persistência e Planos de Implementação (R-064)**:
     - Especificar que o `@python-arch-advisor` elabora o Plano de Implementação e Testes em `docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md` (modo `full` ou `light` conforme R-064) tanto para código de aplicação Python quanto para ferramental/testes Python do repositório (`tools/**`, `scripts/**`, `tests/**`).
     - Quando a demanda for oriunda de um plano híbrido de governança (`docs/plans/governance/<arquivo>.md`), o `@python-arch-advisor` DEVE preencher `related-planning-doc` (e `parent_plan_ref` no envelope OTel) apontando para o plano de governança aprovado, detalhando o contrato técnico e os casos de teste antes da execução por `@python-developer` e `@python-test-engineer`.

4. **`.github/agents/backend/python/python-developer.agent.md` (`L59`) e `.github/agents/backend/python/python-test-engineer.agent.md` (`L104`)**:
   - Explicitar no Gate R-064 e no escopo operacional a atuação sobre `tools/**/*.py`, `scripts/**/*.py` (`@python-developer`) e `tests/**/*.py` / `tests/governance_audit/**/*.py` (`@python-test-engineer`) mediante Plano de Implementação e Testes elaborado previamente pelo `@python-arch-advisor` em `docs/plans/implementation/` (vinculado via `related-planning-doc` ao plano de `docs/plans/governance/` quando aplicável).

5. **`.github/agents/agent-router.agent.md`, `.github/agents/workflows/workflow-governance-maintenance.md`, `CLAUDE.md` e `.github/copilot-instructions.md`**:
   - Atualizar a tabela de roteamento, Decision Tree e o workflow `WORKFLOW-GOVERNANCE-MAINTENANCE` para explicitar a **Regra de Fronteira Híbrida (R-055 Q3 + R-064 + Tríade Python)**:
     - Alterações declarativas (`.github/**` exceto `*.py`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`) → `@governance-maintainer`.
     - Alterações ou execuções em arquivos Python (`tools/**/*.py`, `scripts/**/*.py`, `tests/**/*.py`, `conftest.py`, `pyproject.toml`, `pytest`) → handoff obrigatório para `@python-router`, que aciona **1º `@python-arch-advisor`** (elabora o plano de implementação e testes em `docs/plans/implementation/` vinculado via `related-planning-doc`) e **2º `@python-developer` / `@python-test-engineer`** (implementam código/testes e executam `pytest`).

6. **Sincronização Atômica de Catálogos (R-015 / R-040)**:
   - Atualizar `.github/agents/backend/python/python-catalog.yaml`, `.github/agents/catalog.yaml` e `.github/agents/routing-graph.yaml` para refletir o escopo de tooling/testes do repositório na Tríade Python (`@python-router` → `@python-arch-advisor` → `@python-developer` / `@python-test-engineer`), com as seguintes **âncoras exatas em `.github/agents/routing-graph.yaml`**:
     - **`L113-L115` (nó `id: python-router`)**: Atualizar `descricao` para explicitar a supervisão da Tríade Python (`@python-arch-advisor` → `@python-developer` / `@python-test-engineer`) cobrindo tanto código de aplicação Python Backend quanto ferramental e suítes de testes Python do próprio repositório (`tools/**/*.py`, `scripts/**/*.py`, `tests/**/*.py`).
     - **`L358-L363` (`WORKFLOW-TECHNICAL-ANALYSIS` → `etapa: 1` `specialist_analyst_dispatch` → `agents_permitidos`)**: Incluir `"python-arch-advisor"` na lista de `<stack>-arch-advisor` (onde hoje constam `angular-arch-advisor`, `spring-boot-arch-advisor`, `spring-reactive-arch-advisor`, `ejb-arch-advisor`, `struts-arch-advisor` e `database-arch-advisor`).
     - **`L986` e `L990` (arestas `test-strategy`)**: Preservar a delegação de execução de testes Python (`"executar testes python" # → python-router` em `L986` e `de: "... | python-router | ..."` em `L990`).
     - **`L1306-L1324` (aresta `de: agent-router` → `para: python-router`)**: Atualizar `condicoes.keywords` e `condicoes.sinal_r006` para abranger explicitamente solicitações do ecossistema Python Backend e automação/testes Python do repositório (`tools/**/*.py`, `scripts/**/*.py`, `tests/**/*.py`, `conftest.py`, `pyproject.toml`, R-055 Q3), despachando para os 3 especialistas em `.github/agents/backend/python/python-catalog.yaml` (iniciando obrigatoriamente por `@python-arch-advisor`).
   - Em seguida, executar `python -m tools.governance_sync --apply` e validar paridade com `python -m tools.governance_sync --check`.

### Pipeline de Execução Pós-Lote 1 desta Demanda (Planejamento Técnico via `@python-arch-advisor` → Lote 2 via `@python-test-engineer`)

7. **Etapa Intermediária Obrigatória — Planejamento Técnico Python (Executor: `@python-router` → `@python-arch-advisor`)**:
   - Concluído o Lote 1 declarativo pelo `@governance-maintainer`, o fluxo retorna ao `@agent-router`, que despacha para `@python-router` → `@python-arch-advisor`.
   - O `@python-arch-advisor` elabora o Plano de Implementação e Testes em `docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md` (vinculando `related-planning-doc: "docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md"`), especificando o design dos novos asserts determinísticos e a estratégia de execução para `tests/governance_audit/test_systemic_reuse_gate.py`.

8. **Lote 2 — Implementação e Execução de Testes Python (Executor: `@python-router` → `@python-test-engineer`)**:
   - Com o plano de implementação e testes elaborado pelo `@python-arch-advisor`, o `@python-router` despacha para `@python-test-engineer` atualizar `tests/governance_audit/test_systemic_reuse_gate.py`:
     - Validar que `governance-maintainer.agent.md` proíbe explicitamente a edição direta de `*.py`, `conftest.py` e `pyproject.toml` e delega Q3 (execução/manutenção de `pytest`) ao `@python-router` (`@python-arch-advisor` → `@python-test-engineer`).
     - Validar que `python-router.agent.md` e `python-arch-advisor.agent.md` contemplam o fluxo de 2 passos (1º `@python-arch-advisor` planeja em `docs/plans/implementation/` com `related-planning-doc`; 2º `@python-developer` / `@python-test-engineer` executam sobre `tools/**`, `scripts/**` e `tests/**`).
   - Executar a suíte via runner oficial: `bash scripts/dev/py-test.sh tests/governance_audit/test_systemic_reuse_gate.py tests/governance_audit/test_python_consolidation_governance.py tests/governance_audit/test_r064_arch_advisor_gate.py tests/governance_audit/test_r064_otel_correlation_fields.py`.

---

## 4. Alternativas Rejeitadas

1. **Alternativa A (Rejeitada) — Permitir que `@governance-maintainer` edite `tests/governance_audit/**/*.py` mas proibir `tools/**/*.py`**:
   - *Motivo da rejeição*: Mantém ambiguidade de fronteira sobre arquivos `.py`, exige que um agente desprovido de `run_in_terminal` e de skills de engenharia de testes Python mantenha código `pytest`, e viola a especialização da tríade `@python-router`.
2. **Alternativa B (Rejeitada) — Despachar `@python-router` direto para `@python-developer` / `@python-test-engineer` pulando o `@python-arch-advisor` em demandas de governança**:
   - *Motivo da rejeição*: Viola o padrão canônico da tríade Python (`python-router.agent.md` `L36`/`L46`) e o R-064, pois `@python-arch-advisor` é o especialista responsável por planejar a implementação e estratégia de testes antes da execução; a solução adotada mantém o `@python-arch-advisor` obrigatório no 1º passo do `@python-router` (emitindo plano `full` ou `light` em `docs/plans/implementation/` vinculado via `related-planning-doc` e persistido fisicamente via handoff read-only R-025).
3. **Alternativa C (Rejeitada) — Proibir `@governance-maintainer` até mesmo de invocar CLIs Python existentes via sandbox**:
   - *Motivo da rejeição*: Impediria a sincronização determinística pós-batch (`python -m tools.governance_sync --check`, `python -m tools.plan_lineage_query`), quebrando o protocolo operacional R-015/R-060. A distinção entre *invocar CLI pronta* vs *mutar código-fonte `.py`* preserva a automação sem violar a fronteira de domínio.

---

## 5. Reúso Sistêmico (R-055: Q1/Q2/Q3) e Sensores `tests/governance_audit/`

- **Q1 (Impacto Horizontal / Peers)**: Avaliado impacto em todos os agentes que interagem na fronteira Governança ↔ Python (`@governance-maintainer`, `@agent-router`, `@python-router`, `@python-developer`, `@python-test-engineer`) e nos catálogos/workflows (`catalog.yaml`, `python-catalog.yaml`, `routing-graph.yaml`, `workflow-governance-maintenance.md`, `CLAUDE.md`, `copilot-instructions.md`). Todos estão incluídos no mesmo plano para sincronização atômica (R-015).
- **Q2 (Prevenção Futura / Templates)**: Os templates genéricos (`.github/agents/templates/router-agent.md` e `agent-template.md`) já exigem escopo/não-escopo explícito e pré-condição R-064; a particularidade de aceitar `docs/plans/governance/` aplica-se especificamente à stack Python por ser a linguagem dos validadores e testes do próprio repositório de governança, não devendo poluir routers de stacks de aplicação pura (Angular, EJB, Struts).
- **Q3 (Blindagem por Teste / Quality Gate)**: Especificado o contrato determinístico para `tests/governance_audit/test_systemic_reuse_gate.py` (a ser implementado e executado via `@python-router` → `@python-test-engineer` na Etapa de Execução Python após o Lote 1 declarativo).

### Cenários Gherkin de Verificação Determinística (C4)

```gherkin
Funcionalidade: Separação estrita entre @governance-maintainer (declarativo) e @python-router (*.py e pytest)

  Cenário: Veto Fail-Closed de mutação Python no @governance-maintainer
    Dado o contrato ".github/agents/governance-maintainer.agent.md"
    Quando o teste "test_governance_maintainer_forbids_python_code_mutation_and_delegates_q3_to_python_router" em "tests/governance_audit/test_systemic_reuse_gate.py" inspecionar a seção "CRÍTICO: ESCOPO E NÃO-ESCOPO"
    Então deve validar a proibição explícita no escopo de mutação do "@governance-maintainer" contra criar, editar, formatar ou refatorar "*.py", "conftest.py" e "pyproject.toml"
    E deve existir autorização restrita apenas para invocação CLI de "python -m tools.governance_sync" e "python -m tools.agent_protocol_sync"
    E a regra R-055 Q3 deve delegar a autoria/execução de testes pytest ao "@python-router" e "@python-test-engineer"

  Cenário: Fluxo da Tríade Python (@python-arch-advisor -> @python-developer / @python-test-engineer) em demandas híbridas de governança
    Dado os contratos "python-router.agent.md", "python-arch-advisor.agent.md", "python-developer.agent.md" e "python-test-engineer.agent.md"
    Quando acionados pelo "@python-router" para atender requisitos Python ("tools/**/*.py", "scripts/**/*.py", "tests/**/*.py") oriundos de um plano aprovado em "docs/plans/governance/"
    Então o 1º passo obrigatório deve ser o "@python-arch-advisor" elaborar o Plano de Implementação e Testes em "docs/plans/implementation/" vinculando "related-planning-doc" ao plano de governança
    E o 2º passo deve ser "@python-developer" e/ou "@python-test-engineer" implementarem o código/testes e executarem o "pytest" sob validação R-064 ("allowed_files" e "approved: true")
```

---

## 6. Rollback e Critério de Pronto

### 6.1 Procedimento Executável de Rollback
Caso qualquer verificação pós-lote apresente regressão não sanável dentro do teto de tentativas (preservando `docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md` como registro de auditoria R-064, sem executar `git clean -f` sobre ele):
```bash
git checkout -- .github/agents/governance-maintainer.agent.md .github/agents/backend/python/python-router.agent.md .github/agents/backend/python/python-arch-advisor.agent.md .github/agents/backend/python/python-developer.agent.md .github/agents/backend/python/python-test-engineer.agent.md .github/agents/backend/python/python-catalog.yaml .github/agents/agent-router.agent.md .github/agents/catalog.yaml .github/agents/routing-graph.yaml .github/agents/workflows/workflow-governance-maintenance.md CLAUDE.md .github/copilot-instructions.md tests/governance_audit/test_systemic_reuse_gate.py
```

### 6.2 Critério de Pronto e Teste de Regressão
1. Plano `DRAFT` auditado pelo `@plan-critic` (Tier 1 + Tier 2) e aprovado pelo usuário no Gate 2 HITL (`status: APPROVED`, `approved: true`).
2. Lote 1 (artefatos declarativos `.md` e `.yaml`) aplicado por `@governance-maintainer` com `get_errors` retornando 0 erros e `python -m tools.governance_sync --check` verde.
3. Planejamento Técnico Python elaborado via handoff ao `@python-router` → `@python-arch-advisor` (gerando o Plano de Implementação e Testes em `docs/plans/implementation/` com `related-planning-doc` apontando para este plano), seguido do Lote 2 (`tests/governance_audit/test_systemic_reuse_gate.py`) implementado e validado por `@python-router` → `@python-test-engineer` executando `bash scripts/dev/py-test.sh tests/governance_audit/test_systemic_reuse_gate.py tests/governance_audit/test_python_consolidation_governance.py tests/governance_audit/test_r064_arch_advisor_gate.py tests/governance_audit/test_r064_otel_correlation_fields.py` com 100% de aprovação.

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: `PASS`
- **Tier 2 (`@plan-critic`)**: `PASS_WITH_NITS` (`critic_review_iterations: 2`, `review_rounds: 2`, `rounds: 2, blockers: 0, majors: 1, minors: 4, nits: 2, resolved_in_round_2: true, last_verdict: "PASS_WITH_NITS"`)
- **Histórico de Rodadas de Revisão Cética**:
  - **Rodada 1 (`critic_review_iterations: 1` — `PASS_WITH_NITS`)**:
    - **#1 (MEDIUM — Rollback R-064)**: Removido `git clean -f docs/plans/governance/20261115-120000-separacao-governance-maintainer-python-router.md` do `rollback_plan` e da §6.1 para preservar o artefato do plano como trilha de auditoria R-064.
    - **#2 (MEDIUM — Sincronização de Catálogo)**: Coberto no Lote 1 item 6 via sincronização atômica e validação `python -m tools.governance_sync --check`.
    - **#3 (LOW — Ancoragem Semântica)**: Explicitado no Lote 1 item 1 que as mutações em `governance-maintainer.agent.md` são ancoradas por texto semântico exato (`oldString -> newString`) e não apenas por linhas absolutas.
    - **#4 (NIT — Paridade Gherkin / Lote 2)**: Explicitado na descrição do Lote 2 (item 8) e no cenário Gherkin (C4) que `test_systemic_reuse_gate.py` valida a proibição explícita de `*.py`, `conftest.py` e `pyproject.toml` no escopo de mutação do `@governance-maintainer`.
  - **Rodada 2 (`critic_review_iterations: 2` — Revisão pós-inclusão do `@python-arch-advisor`, 100% saneada Pré-Gate 2 HITL)**:
    - **#1 (HIGH — Contradição em `## 4. Alternativas Rejeitadas`, Alternativa B)**: Substituída a Alternativa B obsoleta da Iteração 1 por *"Alternativa B — Despachar `@python-router` direto para `@python-developer` / `@python-test-engineer` pulando o `@python-arch-advisor` em demandas de governança"*, justificando que pular o advisor viola o padrão canônico da tríade Python (`python-router.agent.md` `L36`/`L46`) e o R-064, mantendo o `@python-arch-advisor` obrigatório no 1º passo do `@python-router` (emitindo plano `full` ou `light` em `docs/plans/implementation/` vinculado via `related-planning-doc` e persistido fisicamente via handoff read-only R-025).
    - **#2 (MEDIUM — Registro completo do Parecer da Rodada 2 no Frontmatter e na seção `## Parecer do Revisor Cético Pré-HITL (R-064)`)**: Atualizados `review_rounds: 2` e `critic_review_iterations: 2` no frontmatter e preenchida integralmente esta seção com o histórico consolidado das 2 rodadas e a resolução dos achados #1 HIGH, #2 MEDIUM e #3 MEDIUM.
    - **#3 (MEDIUM — Âncoras exatas para `.github/agents/routing-graph.yaml`)**: Especificadas no §3 (item 6) as âncoras exatas de `.github/agents/routing-graph.yaml`: `L113-L115` (descrição de `python-router`), `L358-L363` (inclusão de `"python-arch-advisor"` na lista de `<stack>-arch-advisor` de `WORKFLOW-TECHNICAL-ANALYSIS` onde hoje constam apenas angular, spring-boot, spring-reactive, ejb, struts e database), `L986`/`L990` (preservação das arestas `test-strategy`) e `L1306-L1324` (atualização da aresta `agent-router -> python-router`), seguidas da execução de `python -m tools.governance_sync --apply` e `python -m tools.governance_sync --check`.

## Checklist

- [x] Frontmatter R-064 completo (`plan_type: governance`, Schema v2 com correlação OTel) e promovido para `status: APPROVED` / `approved: true` pós-Gate 2 HITL.
- [x] Persistência por `@governance-maintainer`; auditor permanece Read-Only (R-057).
- [x] Conformidade com `docs/plans/<tipo>/` auditada (Smell 2.34) e Checklist Pré-Voo C1–C9 atendido.
- [x] Lote 1 Declarativo executado atomicamente em `.md` e `.yaml` sem mutação em `*.py` (Veto Fail-Closed cumprido) e sincronizado com `python -m tools.governance_sync --check`.
- [x] Etapa Intermediária e Lote 2 Python (`@python-router` → `@python-arch-advisor` [Plano materializado em `docs/plans/implementation/20261115-180000-governance-maintenance-systemic-reuse-gate.md`] → `@python-test-engineer` [`tests/governance_audit/test_systemic_reuse_gate.py` e execução `pytest`]).
