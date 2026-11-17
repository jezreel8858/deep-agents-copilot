---
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-04-19"
review_verdict: PASS_WITH_NITS
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: PASS
allowed_files:
  - "docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md"
  - ".github/agents/adapter-generator.agent.md"
  - ".github/agents/backend/database/database-router.agent.md"
  - ".github/agents/backend/ejb/ejb-router.agent.md"
  - ".github/agents/backend/python/python-router.agent.md"
  - ".github/agents/backend/spring-boot/spring-boot-router.agent.md"
  - ".github/agents/backend/spring-reactive/spring-reactive-router.agent.md"
  - ".github/agents/backend/struts/struts-router.agent.md"
  - ".github/agents/binding-initializer.agent.md"
  - ".github/agents/bug-triage.agent.md"
  - ".github/agents/business-rules-extractor.agent.md"
  - ".github/agents/code-review.agent.md"
  - ".github/agents/code-style-enforcer.agent.md"
  - ".github/agents/codegraph-engine.agent.md"
  - ".github/agents/compliance-guardrails.agent.md"
  - ".github/agents/database-specialist.agent.md"
  - ".github/agents/debugger.agent.md"
  - ".github/agents/deep-search.agent.md"
  - ".github/agents/devops-engineer.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/agents/feature-planner.agent.md"
  - ".github/agents/frontend/angular/angular-router.agent.md"
  - ".github/agents/frontend/react/react-router.agent.md"
  - ".github/agents/governance-factory.agent.md"
  - ".github/agents/performance-agent.agent.md"
  - ".github/agents/plan-critic.agent.md"
  - ".github/agents/prompt-structuring.agent.md"
  - ".github/agents/refactor-planner.agent.md"
  - ".github/agents/requirements-analyst.agent.md"
  - ".github/agents/runtime-verifier.agent.md"
  - ".github/agents/security-reviewer.agent.md"
  - ".github/agents/tech-solution-architect.agent.md"
  - ".github/agents/test-strategy.agent.md"
  - ".github/agents/templates/agent-template.md"
  - ".github/agents/templates/operational-agent.md"
  - ".github/agents/templates/research-agent.md"
  - ".github/skills/agent-contracts/SKILL.md"
  - "tests/governance_audit/test_router_agents.py"
lessons_extracted: true
lessons_applied_to: ["@agent-auditor", "plan-conformance-patterns"]
lessons_at: "2026-11-15"
related-planning-doc: "docs/plans/governance/20260420-183000-router-header-line-breaks.md"
session_id: "sess-20260420-router-header-line-breaks"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-trace-20260420-router-header-line-breaks"
parent_plan_ref: "docs/plans/governance/20260420-183000-router-header-line-breaks.md"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 0
  minors: 0
  nits: 3
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
---

# Plano de Manutenção de Governança — Padronização Anti-Colapso CommonMark do Bloco `Formato de Saída` em Todos os Agents, Templates e Contratos

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md`.
- O agent planejador/auditor (`@agent-auditor`) permanece **100% Read-Only**: emite o diagnóstico e plano estruturado segundo o template canônico `.github/skills/governance-audit-patterns/references/plan-template-governance.md`; a **materialização física `.md`** em estado `DRAFT` (`approved: false`) é executada exclusivamente nesta Etapa 2 por `@governance-maintainer` sob a exceção canônica R-064 (sem tocar em nenhum arquivo de `.github/`, `tools/` ou `tests/` antes do Gate HITL).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após revisão pré-HITL pelo `@plan-critic` (Gate 1) e aprovação humana explícita via `ask_questions` (Gate 2 / R-064) passa a `APPROVED`/`true` para execução em lote na Etapa 4.

---

## 1. Escopo da Manutenção e Achados (Smells 2.x com Severidade)

Na auditoria transversal de todos os **63 arquivos `.github/agents/**/*.agent.md`**, **4 templates `.github/agents/templates/*.md`**, **16 prompts `.github/prompts/**/*.prompt.md`**, `.github/skills/agent-contracts/SKILL.md` e `.github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md`, constatou-se que em CommonMark (especificação usada pelo renderizador Markdown do VS Code Copilot Chat) linhas consecutivas de texto puro sem prefixo de lista (`- `) e sem linha em branco intermediária (`\n\n`) são fundidas em um único parágrafo corrido (*lazy paragraph continuation*).

- **Prompts (`.github/prompts/*.prompt.md`) e `specialist-hybrid-advisory-implementation-patterns/SKILL.md`**: **100% CONFORMES** (todos os 16 prompts já utilizam listas Markdown `- **Comando Executado**: ...` e `specialist-hybrid-advisory-implementation-patterns/SKILL.md` já separa `Agente Ativo:` com linha em branco seguida de headings `###` e bullets `- `).
- **Artefatos com colapso de linhas adjacentes ou formatação indevida no `Formato de Saída`**: **36 arquivos** (`32 agents` + `3 templates` + `1 skill`), classificados nos **5 Padrões (A–E)** abaixo:

| ID / Smell | Padrão Detectado | Severidade | Quantidade | Descrição Técnica do Problema |
| :--- | :--- | :---: | :---: | :--- |
| **Padrão A** (Smell 2.13 / R-042) | `Agente Ativo: ...` colado a `[Se aplicável] Handoff: ...` / `Handoff: ...` / `Skills Carregadas: ...` | **ALTO** | 20 arquivos (16 agents + 3 templates + 1 skill) | As 2 ou 3 linhas do Banner Universal R-042 estão em linhas consecutivas sem linha em branco entre si, colapsando em linha única no chat. |
| **Padrão B** (Smell 2.13 / R-028 / R-050) | `[CURRENT_STATE_LOCK: ...]` com bullet `- ` indevido nos 8 domain routers ou colado a `Agente Ativo:` em 5 planners/analistas | **ALTO** | 13 agents (8 domain routers + 5 agents) | Nos 8 domain routers, `- [CURRENT_STATE_LOCK: ...]` recebeu prefixo `- ` indevido em vez de ficar como marcador de bloco isolado por linha em branco (ex.: posicionado após uma linha em branco abaixo de `- Confidence Score: ...`, mantendo o bloco de bullets de `- Transição:` até `- Confidence Score:` contíguo, ou após `Agente Ativo:` com ajuste correspondente no teste). Em `feature-planner`, `refactor-planner`, `requirements-analyst`, `tech-solution-architect` (3 blocos) e `test-strategy`, `[CURRENT_STATE_LOCK: ...]` está colado imediatamente abaixo de `Agente Ativo:` sem linha em branco. |
| **Padrão C** (Smell 2.13 / R-064) | Metadados de revisão adjacentes em `plan-critic.agent.md` | **ALTO** | 1 agent | Em `plan-critic.agent.md`, `Agente Ativo: plan-critic` está colado a `Abordagem:` (L89-90) e `review_verdict: ...` está colado a `review_rounds: ...` (L94-95) sem linha em branco nem lista `- `. |
| **Padrão D** (Smell 2.13 / R-055 Q2) | Templates canônicos e contrato universal (`agent-contracts/SKILL.md`) | **ALTO** | 4 arquivos (3 templates + 1 skill) | `agent-template.md`, `operational-agent.md`, `research-agent.md` e `agent-contracts/SKILL.md` (§ 0) contêm linhas adjacentes no banner, propagando o colapso para novos agents criados pela fábrica. |
| **Padrão E** (Smell 2.13 / R-028) | Cabeçalhos/metadados chave-valor (`Campo: valor`) adjacentes sem `- ` e sem linha em branco | **MÉDIO** | 14 agents | Campos consecutivos como `Arquivo(s):`/`Convenções aplicadas:`, `Veredito:`/`Confiança:`, `Rota:`/`Motivo:`/`Confiança:`/`Score:`/`Nível de routing:`, `Tier Operacional:`/`Loop:`/`Status:`, `Tipo de artefato:`/`Ação:`/`Caminho final:`, `Causa:`/`Local:`/`Ação sugerida:` colapsam em parágrafo único no chat. |

---

## 2. Inventário Completo de Artefatos Afetados e `allowed_files`

Nenhum glob é utilizado em `allowed_files`. Os **38 arquivos** autorizados para este plano são:

### 2.1. Padrão A + Padrão E (16 Agents Operacionais, Revisores e Especialistas)
1. `.github/agents/bug-triage.agent.md` — **Padrão A** (L299-300: separar `Agente Ativo:` e `[Se aplicável] Handoff:` com linha em branco).
2. `.github/agents/business-rules-extractor.agent.md` — **Padrão A** (L284-285: separar `Agente Ativo:` e `[Se aplicável] Handoff:` com linha em branco).
3. `.github/agents/code-review.agent.md` — **Padrão A + E** (L88-89: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L93-94 e L109-110: prefixar `- Arquivo(s):`, `- Convenções aplicadas:`, `- Veredito:`, `- Confiança:` e isolar separadores `━━━` com linha em branco).
4. `.github/agents/code-style-enforcer.agent.md` — **Padrão A + E** (L67-68: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L71-81: isolar separadores `━━━` e prefixar `- Adapter aplicado:`, `- Confiança:`).
5. `.github/agents/codegraph-engine.agent.md` — **Padrão A** (L149-150: separar `Agente Ativo:` e `[Se aplicável] Handoff:` com linha em branco).
6. `.github/agents/compliance-guardrails.agent.md` — **Padrão A + E** (L70-71: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L75-76 e L91-92: isolar separadores `━━━` e prefixar `- Framework(s) aplicável(is):`, `- Escopo avaliado:`, `- Veredito:`, `- Confiança:`).
7. `.github/agents/database-specialist.agent.md` — **Padrão A + E** (L70-71: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L74-75: isolar separador `━━━` e prefixar `- Tipo:`).
8. `.github/agents/debugger.agent.md` — **Padrão A + E** (L73-74: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L78-79 e L91: isolar separadores `━━━` e prefixar `- Sintoma:`, `- Evidência:`, `- Confiança:`).
9. `.github/agents/deep-search.agent.md` — **Padrão A + E** (L75-76: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L78-82: converter `Rota:`, `Motivo:`, `Confiança:`, `Score:`, `Nível de routing:` para lista Markdown `- `; L92-93: prefixar `- <resposta objetiva com citação>` sob `Síntese:`).
10. `.github/agents/devops-engineer.agent.md` — **Padrão A + E** (L68-69: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L73 e L88-89: isolar separadores `━━━` e prefixar `- Artefato:`, `- Veredito:`, `- Confiança:`).
11. `.github/agents/docs-engineer.agent.md` — **Padrão A** (L65-66: separar `Agente Ativo:` e `[Se aplicável] Handoff:` com linha em branco).
12. `.github/agents/governance-factory.agent.md` — **Padrão A + E** (L216-217: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L219-226: converter `Tipo de artefato:`, `Ação:`, `Pesquisa prévia...`, `Caminho final:`, `Catálogo(s) atualizado(s):`, `Modelo escolhido...`, `[Se type: stack]...`, `[Se router]...` para lista Markdown `- `).
13. `.github/agents/performance-agent.agent.md` — **Padrão A + E** (L69-70: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L74-75 e L90-91: isolar separadores `━━━` e prefixar `- Camada revisada:`, `- Métricas aplicadas:`, `- Veredito:`, `- Confiança:`).
14. `.github/agents/prompt-structuring.agent.md` — **Padrão A + E** (L88-89: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L91-93 e L110-111: converter `Tier Operacional:`, `Loop:`, `Status:`, `Retorno:`, `Próximo passo mínimo:` para lista Markdown `- `).
15. `.github/agents/runtime-verifier.agent.md` — **Padrão A + E** (L70-71: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L74-75 e L83-84: isolar separadores `━━━` e prefixar `- Stack:`, `- Veredito:`).
16. `.github/agents/security-reviewer.agent.md` — **Padrão A + E** (L74-75: separar `Agente Ativo:` e `[Se aplicável] Handoff:`; L79-80 e L95-96: isolar separadores `━━━` e prefixar `- Superfície revisada:`, `- Standards aplicados:`, `- Veredito:`, `- Confiança:`).

### 2.2. Padrão B (8 Domain Routers + 5 Agents com `[CURRENT_STATE_LOCK: ...]`)
17. `.github/agents/backend/database/database-router.agent.md` — **Padrão B** (L62: remover prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` — mantendo o parágrafo de bullets contíguo de `- Transição:` a `- Confidence Score:` — ou isolado por linha em branco com ajuste em `test_router_agents.py`).
18. `.github/agents/backend/ejb/ejb-router.agent.md` — **Padrão B** (L62: remover prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` — mantendo o parágrafo de bullets contíguo de `- Transição:` a `- Confidence Score:` — ou isolado por linha em branco com ajuste em `test_router_agents.py`).
19. `.github/agents/backend/python/python-router.agent.md` — **Padrão B** (L62: remover prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` — mantendo o parágrafo de bullets contíguo de `- Transição:` a `- Confidence Score:` — ou isolado por linha em branco com ajuste em `test_router_agents.py`).
20. `.github/agents/backend/spring-boot/spring-boot-router.agent.md` — **Padrão B** (L62: remover prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` — mantendo o parágrafo de bullets contíguo de `- Transição:` a `- Confidence Score:` — ou isolado por linha em branco com ajuste em `test_router_agents.py`).
21. `.github/agents/backend/spring-reactive/spring-reactive-router.agent.md` — **Padrão B** (L62: remover prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` — mantendo o parágrafo de bullets contíguo de `- Transição:` a `- Confidence Score:` — ou isolado por linha em branco com ajuste em `test_router_agents.py`).
22. `.github/agents/backend/struts/struts-router.agent.md` — **Padrão B** (L62: remover prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` — mantendo o parágrafo de bullets contíguo de `- Transição:` a `- Confidence Score:` — ou isolado por linha em branco com ajuste em `test_router_agents.py`).
23. `.github/agents/frontend/angular/angular-router.agent.md` — **Padrão B** (L63: remover prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` — mantendo o parágrafo de bullets contíguo de `- Transição:` a `- Confidence Score:` — ou isolado por linha em branco com ajuste em `test_router_agents.py`).
24. `.github/agents/frontend/react/react-router.agent.md` — **Padrão B** (L63: remover prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` — mantendo o parágrafo de bullets contíguo de `- Transição:` a `- Confidence Score:` — ou isolado por linha em branco com ajuste em `test_router_agents.py`).
25. `.github/agents/feature-planner.agent.md` — **Padrão B** (L79-80: inserir linha em branco entre `Agente Ativo: feature-planner` e `[CURRENT_STATE_LOCK: ...]`).
26. `.github/agents/refactor-planner.agent.md` — **Padrão B** (L96-97: inserir linha em branco entre `Agente Ativo: refactor-planner` e `[CURRENT_STATE_LOCK: ...]`).
27. `.github/agents/requirements-analyst.agent.md` — **Padrão B + E** (L93-94: inserir linha em branco entre `Agente Ativo: requirements-analyst` e `[CURRENT_STATE_LOCK: ...]`; L115-117: prefixar `- Dado`, `- Quando`, `- Então` para evitar colapso).
28. `.github/agents/tech-solution-architect.agent.md` — **Padrão B** (L122-123, L155-156 e L208-209: inserir linha em branco entre `Agente Ativo: tech-solution-architect` e `[CURRENT_STATE_LOCK: ...]` nos 3 templates de saída).
29. `.github/agents/test-strategy.agent.md` — **Padrão B** (L71-72: inserir linha em branco entre `Agente Ativo: test-strategy` e `[CURRENT_STATE_LOCK: ...]`).

### 2.3. Padrão C (1 Agent Revisor de Planos)
30. `.github/agents/plan-critic.agent.md` — **Padrão C** (L89-96: separar `Agente Ativo: plan-critic` de `Abordagem:` com linha em branco e formatar `- Tier 1: PASS | FAIL (...)`, `- review_verdict: ...` e `- review_rounds: ...` como itens de lista Markdown ou blocos separados por linha em branco).

### 2.4. Padrão E Exclusivo (2 Agents Operacionais de Inicialização/Adapters)
31. `.github/agents/adapter-generator.agent.md` — **Padrão E** (L329-330 e L355-357: separar avisos `⚠️` e prefixar `- Causa:`, `- Local:`, `- Ação sugerida:`, `- Confiança:` no bloco de falha).
32. `.github/agents/binding-initializer.agent.md` — **Padrão E** (L168-169, L178-180 e L194-197: separar avisos `⚠️`, linhas `→` e prefixar `- Causa:`, `- Local:`, `- Ação sugerida:`, `- Confiança:` no bloco de falha).

### 2.5. Padrão D (3 Templates Canônicos + 1 Skill de Contrato Universal)
33. `.github/agents/templates/agent-template.md` — **Padrão D / A** (L113-114: separar `Agente Ativo: <slug-kebab-case>` e `[Se aplicável] Handoff: ...` com linha em branco).
34. `.github/agents/templates/operational-agent.md` — **Padrão D / A** (L97-98: separar `Agente Ativo: <slug-kebab-case>` e `[Se aplicável] Handoff: ...` com linha em branco).
35. `.github/agents/templates/research-agent.md` — **Padrão D / A** (L98-100: separar `Agente Ativo: <slug-kebab-case>`, `[Se aplicável] Handoff: ...` e `Skills Carregadas: ...` com linhas em branco).
36. `.github/skills/agent-contracts/SKILL.md` — **Padrão D / A** (L46-48 e L56-57 na Seção 0: separar `Agente Ativo:`, `Handoff:` e `Skills Carregadas:` com linha em branco nos exemplos canônicos).

### 2.6. Suíte de Testes e Plano de Governança
37. `tests/governance_audit/test_router_agents.py` — **Sensor de Regressão (Q3)**: (a) garantir compatibilidade de `test_all_routers_formato_de_saida_uses_markdown_list_for_header_metadata` com o Padrão B nos 8 domain routers (posicionando `[CURRENT_STATE_LOCK: ...]` após uma linha em branco abaixo de `- Confidence Score: ...` para que o parágrafo de bullets do header fique contíguo de `- Transição:` até `- Confidence Score:`, onde a regex de `test_all_routers_formato_de_saida_uses_markdown_list_for_header_metadata` já para em `Confidence Score:`, e/ou ajustando a validação de `block_lines[2:]` para permitir `[CURRENT_STATE_LOCK: ...]` sem `- ` isolado por linha em branco); e (b) adicionar teste determinístico validando que nenhum arquivo em `.github/agents/**/*.agent.md`, `.github/agents/templates/*.md`, `.github/prompts/*.prompt.md` ou `.github/skills/agent-contracts/SKILL.md` possui linhas de cabeçalho (`Agente Ativo:`, `Handoff:`, `Skills Carregadas:`, `[CURRENT_STATE_LOCK:`, `Tier 1:`, `review_verdict:`, `review_rounds:`) coladas sem linha em branco ou com bullet `- ` indevido em `[CURRENT_STATE_LOCK: ...]`.
38. `docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md` — Este plano de governança R-064.

---

## 3. Plano de Correção em Lote (Plan-Then-Batch — R-059)

Após o Gate HITL (`approved: true`), a Etapa 4 será executada por `@governance-maintainer` em **turno único** via `ctx_execute` (`language: "javascript"`):

1. **Passo 1 (Atualização do Status do Plano)**: Atualizar `docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md` para `status: APPROVED` e `approved: true`.
2. **Passo 2 (Transformação Cirúrgica em Lote nos 36 Artefatos)**:
   - **Padrão A / D**: Inserir `\n\n` entre `Agente Ativo: ...`, `[Se aplicável] Handoff: ...` (ou `Handoff: ...`) e `Skills Carregadas: ...` nos 16 agents, 3 templates e `agent-contracts/SKILL.md`.
   - **Padrão B**: Nos 8 domain routers, remover o prefixo `- ` de `[CURRENT_STATE_LOCK: ...]` e posicioná-lo após uma linha em branco abaixo de `- Confidence Score: ...` (mantendo o bloco de bullets do header contíguo de `- Transição:` até `- Confidence Score:`, onde a captura da regex de `test_all_routers_formato_de_saida_uses_markdown_list_for_header_metadata` encerra na linha `Confidence Score:`, além de ajustar `test_router_agents.py` se necessário para reconhecer `[CURRENT_STATE_LOCK: ...]` isolado sem bullet). Nos 5 agents (`feature-planner`, `refactor-planner`, `requirements-analyst`, `tech-solution-architect`, `test-strategy`), inserir linha em branco entre `Agente Ativo: ...` e `[CURRENT_STATE_LOCK: ...]`.
   - **Padrão C**: Em `plan-critic.agent.md`, inserir linha em branco após `Agente Ativo: plan-critic` e converter `Tier 1:`, `review_verdict:` e `review_rounds:` em itens de lista Markdown (`- Tier 1: ...`, `- review_verdict: ...`, `- review_rounds: ...`).
   - **Padrão E**: Converter sequências de metadados chave-valor adjacentes em listas Markdown (`- Campo: valor`) e isolar linhas divisórias (`━━━`) com linha em branco nos 14 agents identificados.
3. **Passo 3 (Blindagem Determinística Pytest)**: Adicionar `test_all_agents_and_templates_formato_de_saida_no_adjacent_collapsing_header_lines()` em `tests/governance_audit/test_router_agents.py`.
4. **Passo 4 (Validação Consolidada)**: Executar `pytest tests/governance_audit/ tests/operational_flow/` e `get_errors` único com todos os 38 arquivos.

---

## 4. Alternativas Rejeitadas

1. **Usar dois espaços no fim da linha (*hard line break* `  \n`) em vez de linha em branco (`\n\n`) ou lista Markdown (`- `)**:
   - *Motivo da rejeição*: Invisível em diffs, frequentemente removido por formatadores/editores (`trimTrailingWhitespace`) e pelos próprios LLMs ao gerar respostas no chat.
2. **Manter prefixo `- ` em `[CURRENT_STATE_LOCK: ...]` nos domain routers**:
   - *Motivo da rejeição*: O token `[CURRENT_STATE_LOCK: ...]` é um marcador estrutural de máquina de estados (R-050), devendo manter paridade com os demais agents (`feature-planner`, `tech-solution-architect`, etc.) onde aparece isolado por linha em branco sem bullet.
3. **Envolver os cabeçalhos internos em sub-blocos de código aninhados**:
   - *Motivo da rejeição*: Viola a regra de não aninhar cercas de código desnecessárias dentro do template `Formato de Saída` e prejudica a legibilidade no chat.

---

## 5. Reúso Sistêmico (R-055: Q1 / Q2 / Q3) e Compatibilidade de Testes

- **Q1 (Impacto Horizontal / Peers)**: A varredura cobriu 100% dos 63 agents, 4 templates, 16 prompts e 2 skills de contrato/padrão de saída. Todos os 36 arquivos com ocorrências reais dos Padrões A–E foram incluídos no mesmo lote atômico.
- **Q2 (Prevenção Futura / Templates)**: Os 3 templates canônicos afetados (`agent-template.md`, `operational-agent.md`, `research-agent.md`) e a fonte da verdade (`.github/skills/agent-contracts/SKILL.md`) estão incluídos no lote, impedindo que `@governance-factory` gere novos agents com cabeçalhos colados.
- **Q3 (Blindagem por Teste / Quality Gate)**: Verificou-se `tests/governance_audit/` e `tests/operational_flow/` (incluindo `test_router_agents.py` e `test_architectural_plan_hardening.py`). Em `tests/governance_audit/test_router_agents.py`, a função `test_all_routers_formato_de_saida_uses_markdown_list_for_header_metadata` usa a regex `r"```(?:markdown|text)?\r?\n(Agente Ativo:[^\r\n]+\r?\n+(?:[\s\S]*?)?(?:Confidence Score|Nível de Routing):[^\r\n]+)"` (ou captura até `Confidence Score:`) e valida que as linhas não vazias em `block_lines[2:]` começam com `- `. Portanto, ao remover o `- ` de `[CURRENT_STATE_LOCK: ...]` nos 8 domain routers, posicionaremos `[CURRENT_STATE_LOCK: ...]` após uma linha em branco abaixo de `- Confidence Score: ...` (de modo que o parágrafo de bullets do header permaneça 100% contíguo de `- Transição:` até `- Confidence Score:`, onde a regex de `test_all_routers_formato_de_saida_uses_markdown_list_for_header_metadata` já para em `Confidence Score:`) e ajustaremos `test_all_routers_formato_de_saida_uses_markdown_list_for_header_metadata` em `tests/governance_audit/test_router_agents.py` para também aceitar/validar `[CURRENT_STATE_LOCK: ...]` sem `- ` isolado por linha em branco nos domain routers. Além disso, será adicionado novo teste determinístico cobrindo todos os agents, templates e `agent-contracts/SKILL.md`.

---

## 6. Rollback e Critério de Pronto

- **Comando de Rollback Exato**:
  ```bash
  git checkout -- .github/agents/adapter-generator.agent.md .github/agents/backend/database/database-router.agent.md .github/agents/backend/ejb/ejb-router.agent.md .github/agents/backend/python/python-router.agent.md .github/agents/backend/spring-boot/spring-boot-router.agent.md .github/agents/backend/spring-reactive/spring-reactive-router.agent.md .github/agents/backend/struts/struts-router.agent.md .github/agents/binding-initializer.agent.md .github/agents/bug-triage.agent.md .github/agents/business-rules-extractor.agent.md .github/agents/code-review.agent.md .github/agents/code-style-enforcer.agent.md .github/agents/codegraph-engine.agent.md .github/agents/compliance-guardrails.agent.md .github/agents/database-specialist.agent.md .github/agents/debugger.agent.md .github/agents/deep-search.agent.md .github/agents/devops-engineer.agent.md .github/agents/docs-engineer.agent.md .github/agents/feature-planner.agent.md .github/agents/frontend/angular/angular-router.agent.md .github/agents/frontend/react/react-router.agent.md .github/agents/governance-factory.agent.md .github/agents/performance-agent.agent.md .github/agents/plan-critic.agent.md .github/agents/prompt-structuring.agent.md .github/agents/refactor-planner.agent.md .github/agents/requirements-analyst.agent.md .github/agents/runtime-verifier.agent.md .github/agents/security-reviewer.agent.md .github/agents/tech-solution-architect.agent.md .github/agents/test-strategy.agent.md .github/agents/templates/agent-template.md .github/agents/templates/operational-agent.md .github/agents/templates/research-agent.md .github/skills/agent-contracts/SKILL.md tests/governance_audit/test_router_agents.py
  ```
  - **Preservação de Evidência de Auditoria (R-064)**: O artefato de plano `docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md` **não** é removido no rollback (`rm -f` vedado), sendo preservado em disco como registro histórico e evidência rastreável de auditoria.
- **Critério de Pronto (DoD)**:
  - [ ] 100% dos 36 artefatos (`.github/agents/`, `.github/agents/templates/`, `.github/skills/agent-contracts/SKILL.md`) sem linhas de cabeçalho/metadados colapsáveis no `Formato de Saída`.
  - [ ] 8 domain routers com `[CURRENT_STATE_LOCK: ...]` isolado por linha em branco e sem prefixo `- `.
  - [ ] Novo teste de regressão em `tests/governance_audit/test_router_agents.py` passando com `0 failed`.
  - [ ] `get_errors` sem erros nos 38 arquivos de `allowed_files`.

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: `PASS` (`review_tier1: PASS`, frontmatter R-064 íntegro, `status: DRAFT`, `approved: false`, `created_at: "2026-04-19"`, 38 entradas explícitas em `allowed_files`).
- **Tier 2 (`@plan-critic`)**: `PASS_WITH_NITS` (Rodada 2 — `review_rounds: 2`, `reviewer: "@plan-critic"`, `blockers: 0`, `majors: 0`, `minors: 0`, `nits: 3`).
- **Findings e Resoluções**:
  - **Rodada 1 (`NEEDS_REVISION` → Resolvido na Rodada 2)**: Corrigidos os apontamentos estruturais de escopo horizontal, pareamento exato de `allowed_files` (38 caminhos explícitos sem globs abertos), compatibilidade explícita com `test_all_routers_formato_de_saida_uses_markdown_list_for_header_metadata` em `tests/governance_audit/test_router_agents.py` e preservação do plano no comando de rollback (R-064).
  - **Rodada 2 (`PASS_WITH_NITS` — 3 Nits não-bloqueantes registrados)**:
    1. `NIT-01` (Metadados / `created_at`): Alinhamento explícito da referência temporal no Checklist com `created_at: "2026-04-19"` do frontmatter YAML.
    2. `NIT-02` (Nomenclatura de Etapas do Workflow): Observação cosmética sobre numeração das etapas entre o Gate 1 (`@plan-critic`), Gate 2 HITL (`ask_questions`) e o lote de execução pós-aprovação no `WORKFLOW-GOVERNANCE-MAINTENANCE`.
    3. `NIT-03` (Referência informativa em Q3): Menção informativa a `tests/operational_flow/` na seção 5 (Q3), sendo o alvo real de mutação e asserção estritamente `tests/governance_audit/test_router_agents.py` (já listado em `allowed_files`).

## Checklist

- [x] Frontmatter R-064 completo (`plan_type: "governance"`, `status: DRAFT`, `approved: false`, `created_at: "2026-04-19"`, `review_verdict: PASS_WITH_NITS`, `review_rounds: 2`).
- [x] Persistência por `@governance-maintainer`; auditor (`@agent-auditor`) permanece Read-Only (R-057).
- [x] Conformidade com `docs/plans/governance/` auditada (Smell 2.34) e parecer pré-HITL (`PASS_WITH_NITS`) registrado.
