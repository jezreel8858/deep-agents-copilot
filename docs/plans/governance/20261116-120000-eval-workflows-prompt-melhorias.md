---
status: "APPROVED"
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-16"
allowed_files:
  - ".github/prompts/eval-workflows.prompt.md"
  - ".github/prompts/catalog.yaml"
  - ".github/prompts/templates/prompt-template.md"
  - "tests/README.md"
reviewer: "@plan-critic"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
review_tier1: "PASS"
lessons_extracted: true
lessons_applied_to: ["plan-conformance-patterns"]
lessons_at: "2026-11-16"
related-planning-doc: "N/A — plano primário da manutenção de governança"
session_id: "sess-20261116-eval-workflows-gov"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-eval-workflows-gov-01"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
---

# Plano de Evolução de Governança — Melhorias Estruturais e Operacionais em `eval-workflows.prompt.md`

## 1. Contexto, Escopo e Grounding Físico Verificado

Este plano de governança (`plan_type: "governance"`) consolida o diagnóstico de auditoria emitido por `@agent-auditor` para evolução estrutural, semântica e de sincronismo documental do comando utilitário `/eval-workflows` (`.github/prompts/eval-workflows.prompt.md`) e seus artefatos correlatos.

### 1.1 Inventário Físico dos Arquivos em Escopo (`allowed_files`)

Leitura física verificada via sandbox `ctx_execute` (`fs.readFileSync`):

| Arquivo em `allowed_files` | Linhas Reais (sem / com trailing newline) | Papel no Escopo | Ancoragem Física Verificada |
| :--- | :--- | :--- | :--- |
| `.github/prompts/eval-workflows.prompt.md` | 129 linhas (130 no split com newline final) | Prompt utilitário avaliador de trajetórias (R-050) | Frontmatter nas L1–16; Corpo nas L18–115; `<execution_protocol>` nas L117–129 |
| `.github/prompts/catalog.yaml` | 123 linhas (124 no split com newline final) | Catálogo SSOT de prompts utilitários | Entrada `eval-workflows` nas L69–73 (L71 com `description` desatualizada citando `Gemini 3.8 Flash`; L72 já com `model: "Gemini 4 Argon"`) |
| `.github/prompts/templates/prompt-template.md` | 145 linhas (146 no split com newline final) | Template estrutural canônico de prompts | Define as seções obrigatórias e diretrizes de variáveis nativas (validado por `tests/governance_audit/test_template_sections.py`) |
| `tests/README.md` | 219 linhas (220 no split com newline final) | Documentação da pirâmide de avaliação e suíte de testes | L17 no diagrama ASCII da Camada 3 refere-se a `/eval-workflows` mencionando `Gemini 3.8 Flash como juiz de avaliação` |

### 1.2 Mapa de Linhas Reais de `.github/prompts/eval-workflows.prompt.md`

Ancoragem linha a linha verificada diretamente no arquivo físico (`129` linhas de conteúdo):

- **L1–16 (Frontmatter YAML)**:
  - **L3**: `description: "Avalia a conformidade de trajetórias dos workflows canônicos (R-050) por micro-cenários isolados com Gemini 3.8 Flash."` (dessincronizada em relação ao modelo da L6).
  - **L6**: `model: "Gemini 4 Argon"`.
  - **L7**: `tools: [read, search, execute, todo]`.
  - **L8**: `argument-hint: '[cenario-id | todos]'`.
  - **L9–15**: `source_docs:` contendo exatamente 6 entradas:
    - **L10**: `- ".github/skills/harness-eval/SKILL.md"`
    - **L11**: `- "CLAUDE.md"`
    - **L12**: `- ".github/copilot-instructions.md"`
    - **L13**: `- ".github/skills/agent-evals-lab/SKILL.md"`
    - **L14**: `- ".github/skills/handoff-governance/SKILL.md"`
    - **L15**: `- ".github/skills/context-mode/SKILL.md"`
    *(Nota de grounding: `AI-INSTRUCTIONS.md` não existe neste arquivo nem no repositório).*
- **L18–24 (Título e Propósito)**:
  - **L18**: `# Avaliação de Trajetórias de Workflows Canônicos`
  - **L20**: `## Propósito` (parágrafo descritivo nas L22–24).
- **L26–35 (Variáveis Nativas)**:
  - **L26**: `## Variáveis Nativas`
  - **L28–31**: Primeiro bloco de bullets (`${input:cenario:...`, `${file}`, `${selection}`, `${workspaceFolder}`).
  - **L32–35**: Segundo bloco de bullets duplicando os mesmos conceitos sem fechamento da tabela/fluxo de precedência com `argument-hint` da L8.
- **L37–51 (Quando Usar / Escopo e Não-Escopo)**:
  - **L39**: `### CRÍTICO: ESCOPO E NÃO-ESCOPO`
  - **L41**: `- ✅ Executar cada cenário de teste invocando o subagente de simulação com contexto limpo.` (contradição com a ausência de `agent` em `tools:` na L7 e com o bypass R-062).
  - **L43**: `- ❌ NUNCA avaliar todos os workflows em uma única resposta monolítica.` (tensão com `argument-hint: '[cenario-id | todos]'` na L8).
  - **L51**: `- ⚠️ **Circuit Breaker**: Máximo de 2 tentativas de re-execução por cenário em caso de falha transitória. Na 2ª falha, registrar `FAIL` com causa raiz e avançar.`
- **L53–73 (Como Executar / Fluxo Passo a Passo)**:
  - **L55**: `### Fluxo Passo a Passo`
  - **L59**: `2. **Seleção do Escopo**: Se o usuário informou um `cenario-id`, filtrar apenas esse caso. Caso contrário, selecionar o primeiro pendente ou iterar sequencialmente usando a lista `todo`.` ("primeiro pendente" carece de estado persistido entre sessões).
  - **L62–63**: `- Comparar o comportamento observado na sessão ou nos artefatos contra os critérios do cenário.` (ambiguidade sobre qual é a fonte primária de evidência da trajetória).
- **L75–81 (Checklist Antes de Finalizar)**:
  - Bullets de verificação pré-conclusão nas L77–81.
- **L83–101 (Formato de Saída)**:
  - **L85–101**: Bloco markdown de relatório de avaliação.
  - **L91–95**: Tabela `### Trajetória Observada vs. Esperada` com colunas `Passo | Esperado | Observado | Status`.
  - **L98**: `**Score de Aderência**: `<X/Y critérios atendidos (Z%)>`` (sem fórmula explícita para penalidades parciais ou violações críticas).
- **L103–115 (Exemplos e Combina Com)**:
  - **L112–115**: `## 🔗 Combina Com` referenciando `/audit`, `/validate` e `@agent-auditor`.
- **L117–129 (`<execution_protocol>`)**:
  - **L119**: `<execution_protocol>`
  - **L123–125**: Item 4 definindo `Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)` (que coexiste sem distinção explícita com o Circuit Breaker de re-execução de cenário da L51).
  - **L127**: Item 6 definindo `Validação Agrupada com `get_errors` (R-051)` sobre "mutações em processo único" e "arquivos alterados", embora o prompt seja estritamente Read-Only (L49).

---

## 2. Diagnóstico Técnico e Melhorias Propostas (M1 a M8)

### M1 — Sincronismo de Modelo entre Frontmatter, Catálogo e Documentação de Testes (Crítico)

- **Evidência Física**:
  - `.github/prompts/eval-workflows.prompt.md` L3 declara `Gemini 3.8 Flash` na `description`, enquanto a L6 declara `model: "Gemini 4 Argon"`.
  - `.github/prompts/catalog.yaml` L71 declara `description: "Avalia a conformidade de trajetórias dos workflows canônicos (R-050) por micro-cenários isolados com Gemini 3.8 Flash."`, enquanto a L72 já define `model: "Gemini 4 Argon"`.
  - `tests/README.md` L17 exibe `[/eval-workflows — Gemini 3.8 Flash como juiz de avaliação]`.
- **Ação Planejada**:
  - Atualizar `.github/prompts/eval-workflows.prompt.md` (L3), `.github/prompts/catalog.yaml` (L71) e `tests/README.md` (L17) para refletir de forma uníssona o modelo canônico `Gemini 4 Argon`.

### M2 — Deduplicação da Seção `## Variáveis Nativas` e Alinhamento com `argument-hint` (Alto)

- **Evidência Física**:
  - Em `.github/prompts/eval-workflows.prompt.md`, as L28–31 e L32–35 repetem as mesmas 4 variáveis nativas (`${input:cenario:...}`, `${file}`, `${selection}`, `${workspaceFolder}`) com redações ligeiramente diferentes.
  - A L8 define `argument-hint: '[cenario-id | todos]'`, mas as L28–35 não explicam a ordem de precedência entre o argumento posicional passado na invocação `/eval-workflows <arg>`, a variável `${input:cenario}` e o fallback de seleção.
- **Ação Planejada**:
  - Consolidar as L28–35 em uma única lista canônica de variáveis nativas, mantendo conformidade estrita com `.github/prompts/templates/prompt-template.md` (validado por `tests/governance_audit/test_template_sections.py`), e documentar explicitamente a precedência de entrada.

### M3 — Resolução da Contradição de "Subagente de Simulação" vs. `tools: [read, search, execute, todo]` e R-062 (Crítico)

- **Evidência Física**:
  - A L41 instrui: `Executar cada cenário de teste invocando o subagente de simulação com contexto limpo.`
  - Contudo, a L7 declara `tools: [read, search, execute, todo]` (sem `agent`/`run_subagent`), e a regra R-062 (validada por `tests/governance_audit/test_utility_slash_prompts_bypass.py`) estabelece execução direta e determinística para slash prompts utilitários.
  - Na prática do repositório, a simulação determinística e a validação de trajetórias residem em `tests/operational_flow/workflow_eval_simulator.py` e `tests/operational_flow/test_workflow_trajectories.py`, ou na inspeção via sandbox `ctx_execute` sobre os contratos dos agents/skills e `tests/operational_flow/casos-workflows.yaml`.
- **Ação Planejada**:
  - Substituir a menção a "subagente de simulação" na L41 por execução direta e isolada por cenário via sandbox `context-mode` (`ctx_execute` / `ctx_batch`) e/ou invocação do simulador determinístico (`tests/operational_flow/workflow_eval_simulator.py`), preservando `tools: [read, search, execute, todo]` na L7.

### M4 — Desambiguação do Modo `todos` (L8) vs. Regra Anti-Monolítica (L43) e "Primeiro Pendente" (L59) (Alto)

- **Evidência Física**:
  - L8 oferece `[cenario-id | todos]`, mas L43 proíbe avaliar todos os workflows em uma única resposta monolítica, e L59 fala em "selecionar o primeiro pendente" sem que exista arquivo de estado de pendências em disco.
- **Ação Planejada**:
  - Definir semântica operacional determinística nas L43 e L59:
    1. Quando um `cenario-id` específico é informado (ex.: `wf-001`), avaliar profundamente esse micro-cenário.
    2. Quando `todos` (ou nenhum argumento) é informado, executar a varredura em lote estruturada via `ctx_execute` (apoiada em `tests/operational_flow/casos-workflows.yaml` e `tests/operational_flow/workflow_eval_simulator.py`), rastreando cada item na ferramenta `todo` e emitindo tabela consolidada por cenário sem colapsar as evidências individuais.

### M5 — Especificação da Fonte Primária de Evidência da Trajetória nas L62–63 (Alto)

- **Evidência Física**:
  - As L62–63 dizem apenas: `Comparar o comportamento observado na sessão ou nos artefatos contra os critérios do cenário`, sem especificar quais artefatos constituem a evidência verificável.
- **Ação Planejada**:
  - Explicitar nas L60–68 as 3 fontes verificáveis de evidência em ordem de prioridade:
    1. **Simulação Determinística / Contratos Físicos**: validação de `tests/operational_flow/casos-workflows.yaml` contra as definições reais em `.github/agents/*.agent.md`, `.github/skills/**/SKILL.md` e `tests/operational_flow/workflow_eval_simulator.py`.
    2. **Telemetria de Sessão e Spans OTEL**: consulta via `ctx_search` por `[HANDOFF]` / `workflow_trace_id` e `tools.plan_lineage_query` quando avaliando uma sessão recém-executada.
    3. **Artefatos de Planos Materializados**: inspeção de `docs/plans/<tipo>/` para aferir conformidade R-064 e gates arquiteturais.

### M6 — Harmonização dos Dois Circuit Breakers (L51 vs. L123–125) e Escopo Read-Only no `<execution_protocol>` (Médio)

- **Evidência Física**:
  - A L51 define Circuit Breaker de cenário (máximo de 2 tentativas de re-execução por falha transitória).
  - As L123–125 definem o Circuit Breaker de orçamento de turnos (R-060: teto rígido ≤ 5 tool turns).
  - A L127 menciona `Validação Agrupada com get_errors (R-051)` para mutações, mas o prompt é Read-Only (L49), e o bloco `<execution_protocol>` (L117–129) é auditado por `tests/governance_audit/test_sync_execution_protocol_invariants.py`.
- **Ação Planejada**:
  - Clarificar na L51 que o limite de re-execução de cenário opera **estritamente subordinado** ao teto global de ≤ 5 tool turns (R-060) das L123–125.
  - Preservar intacta a estrutura obrigatória de `<execution_protocol>` exigida por `test_sync_execution_protocol_invariants.py`, mantendo na L127 a ressalva `(quando aplicável)` já presente no protocolo canônico.

### M7 — Rubrica Matemática para o `Score de Aderência` (L98) e Tabela de Trajetória (L91–95) (Médio)

- **Evidência Física**:
  - A L98 pede `**Score de Aderência**: <X/Y critérios atendidos (Z%)>`, mas não define como classificar desvios críticos de governança (ex.: pular `@plan-critic`, violar R-025 Read-Only, omitir `allowed_files`).
- **Ação Planejada**:
  - Documentar junto ao Formato de Saída (L91–101) a regra de veredito:
    - `PASS`: 100% dos passos obrigatórios (`expected_trajectory`) e invariantes críticos atendidos.
    - `WARN`: 100% dos invariantes críticos atendidos, mas com desvio menor não-bloqueante (`Score >= 80%`).
    - `FAIL`: qualquer violação de guardrail crítico (R-025, R-042, R-060, R-064) ou `Score < 80%`, mesmo que passos parciais tenham sido cumpridos.

### M8 — Orçamento de Progressive Disclosure R-066 e Paridade com `prompt-template.md` (Baixo)

- **Evidência Física**:
  - O arquivo `.github/prompts/eval-workflows.prompt.md` possui atualmente 129 linhas (~5,3 KB), dentro do orçamento R-066 para prompts (`tests/governance_audit/test_r066_progressive_disclosure_budget.py`).
  - Caso o refinamento de `.github/prompts/templates/prompt-template.md` (145 linhas) seja necessário para clarificar a não-duplicação de `## Variáveis Nativas`, a edição será pontual e manterá todas as seções exigidas por `tests/governance_audit/test_template_sections.py`.
- **Ação Planejada**:
  - Garantir que a versão final de `.github/prompts/eval-workflows.prompt.md` permaneça enxuta (~125–145 linhas) e com 100% das seções obrigatórias de `prompt-template.md`.

---

## 3. Respostas Técnicas de Conformidade (Q1, Q2, Q3)

### Q1 — Impacto em Contratos e Invariantes de Prompts Utilitários (R-062 / R-066)

- As alterações em `.github/prompts/eval-workflows.prompt.md` preservam integralmente:
  - As 6 entradas de `source_docs` nas L9–15 (verificadas por `tests/governance_audit/test_sync_required_source_docs_invariants.py`).
  - O bloco `<execution_protocol>` nas L117–129 (verificado por `tests/governance_audit/test_sync_execution_protocol_invariants.py`).
  - As seções estruturais obrigatórias de `.github/prompts/templates/prompt-template.md` (verificadas por `tests/governance_audit/test_template_sections.py`).
  - O perfil de execução direta sem handoff para `@agent-router` (verificado por `tests/governance_audit/test_utility_slash_prompts_bypass.py`).

### Q2 — Estratégia de Sincronismo SSOT (Catálogo e README de Testes)

- A atualização ocorrerá em lote atômico via `ctx_execute` (`language: "javascript"`) abrangendo:
  1. `.github/prompts/eval-workflows.prompt.md` (L3 e corpo L26–101).
  2. `.github/prompts/catalog.yaml` (L71 — sincronizando `description` com `model: "Gemini 4 Argon"` da L72).
  3. `tests/README.md` (L17 — sincronizando o rótulo da Camada 3 da pirâmide de testes para `Gemini 4 Argon`).
  4. `.github/prompts/templates/prompt-template.md` (apenas se necessário ajuste pontual de comentário/guia na seção `## Variáveis Nativas`, preservando suas 145 linhas e marcadores).

### Q3 — Portão de Qualidade e Sensores de Regressão Existentes (R-055)

- **Sensores Reais Existentes em Disco** (confirmados via `fs.readdirSync`):
  - Em `tests/governance_audit/`:
    - `test_utility_slash_prompts_bypass.py`
    - `test_r066_progressive_disclosure_budget.py`
    - `test_template_sections.py`
    - `test_agent_guardrails_regression.py`
    - `test_ctx_execute_capability_profile.py`
    - `test_sync_execution_protocol_invariants.py`
    - `test_sync_required_source_docs_invariants.py`
    - `test_model_allowlist_governance.py`
  - Em `tests/operational_flow/`:
    - `workflow_eval_simulator.py`
    - `test_workflow_trajectories.py`
    - `casos-workflows.yaml`
- **Cobertura e Fronteira de Domínio (C3)**:
  - Os sensores existentes (`test_utility_slash_prompts_bypass.py`, `test_r066_progressive_disclosure_budget.py`, `test_template_sections.py` e `test_workflow_trajectories.py`) já validam automaticamente os contratos declarativos de prompts utilitários, orçamento de tamanho, seções de template e trajetórias operacionais.
  - Caso no futuro seja desejado um teste Python dedicado exclusivamente à paridade textual `description`/`model` entre `.github/prompts/catalog.yaml` e o frontmatter de cada `.github/prompts/*.prompt.md`, essa demanda será roteada via `@python-router` → `@python-arch-advisor` → `@python-test-engineer` em workflow Python próprio, respeitando a restrição canônica (C3) de não incluir arquivos `*.py` em planos `plan_type: "governance"`.

---

## 4. Plano de Execução Faseado (Pós-Aprovação HITL)

1. **Etapa 3 (Revisão Cética)**: Submeter este plano em `status: "DRAFT"` ao `@plan-critic` para verificação de grounding físico e conformidade R-064.
2. **Etapa 4 (Gate Humano — HITL)**: Aguardar aprovação explícita do usuário antes de qualquer mutação nos arquivos de governança.
3. **Etapa 5 (Materialização por `@governance-maintainer` / `@docs-engineer`)**:
   - Aplicar em lote único via `ctx_execute` (`language: "javascript"`) as melhorias M1–M8 em `.github/prompts/eval-workflows.prompt.md`, `.github/prompts/catalog.yaml`, `tests/README.md` e (se aplicável) `.github/prompts/templates/prompt-template.md`.
4. **Etapa 6 (Validação Determinística)**:
   - Executar via `ctx_execute` a suíte de auditoria existente:
     `./runtime/python/python.exe -m pytest tests/governance_audit/test_utility_slash_prompts_bypass.py tests/governance_audit/test_r066_progressive_disclosure_budget.py tests/governance_audit/test_template_sections.py tests/governance_audit/test_agent_guardrails_regression.py tests/governance_audit/test_ctx_execute_capability_profile.py tests/operational_flow/test_workflow_trajectories.py -q`
