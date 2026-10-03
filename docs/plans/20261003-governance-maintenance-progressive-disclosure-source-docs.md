---
status: concluído
date: 2026-10-03
autor: "@agent-auditor (diagnóstico) + Root Orchestrator (materialização)"
workflow: governance-maintenance
related-plan: docs/plans/20260929-governance-maintenance-harness-bloat-audit.md (escopo irmão/mais amplo, ainda aguardando aprovação — este plano é mais estreito e específico de Progressive Disclosure de `source_docs:`)
---

# Plano de Planejamento — Progressive Disclosure de `source_docs:` (Anti Context Bloat Inicial)

> **Workflow Canônico**: `WORKFLOW-GOVERNANCE-MAINTENANCE` (R-050)
> **Cadeia de autoria**: Análise técnica inicial (Root Orchestrator + pesquisa Tavily) → `@agent-auditor` (diagnóstico formal read-only, Etapa 1)
> **Status**: 🟡 Aguardando aprovação humana explícita via `ask_questions` (nenhuma fase iniciada, nenhum arquivo tocado)

---

## 1) Contexto e Problema

`CLAUDE.md` (353 linhas/~21k tokens), `.github/copilot-instructions.md` (463 linhas/~12k tokens — já auto-injetado nativamente pelo IDE em toda sessão) e `.github/agents/workflows.md` (1.473 linhas/~43k tokens) são declarados em `source_docs:` de forma sistêmica:

- `CLAUDE.md`: **79 ocorrências** em `.github/agents/catalog.yaml`, **100% dos 72 `SKILL.md`**, **100% dos 22 `*.prompt.md`**.
- `.github/copilot-instructions.md`: **75 ocorrências** em `catalog.yaml`, mesma saturação em skills/prompts.
- Campo **duplicado e não-canônico**: `catalog.yaml` possui dois arrays sobrepostos por agent (`prerequisite_docs:` e `source_docs:`), ambos contendo os mesmos dois arquivos em full-load — risco de violação de R-003.

A cláusula **"Pre-fetch automático pelo agent"** (`copilot-instructions.md` § 2) manda carregar esses `source_docs` **integralmente** a cada seleção/spawn de agent. Como cada `run_subagent` abre uma janela de contexto nova, isso se repete a cada handoff em um workflow com múltiplos agents em cadeia (R-050), inflando o contexto inicial em até ~76k tokens por spawn antes de qualquer trabalho útil começar.

Isso contradiz:
- **R-008/R-056** (precedência mandatória de `context-mode`/`ctx_search` sobre leitura bruta de arquivo inteiro).
- O padrão de mercado consolidado de **Progressive Disclosure** (Anthropic Agent Skills spec; Ardalis; Atlan — pesquisa Tavily realizada): metadados sempre carregados (~100 tokens), corpo do skill/agent carregado no acionamento (<5k tokens recomendado), recursos/documentos grandes carregados **sob demanda via busca**, nunca "full-load por garantia".

### Motivação de negócio
Reduzir o custo de tokens/créditos por spawn de agent, mitigar degradação de atenção em "zona burra" (R-061(b), ~100k tokens) e eliminar a contradição normativa já documentada (R-008/R-056 vs. prática real de pre-fetch).

---

## 2) Achados do Diagnóstico Formal (`@agent-auditor`, read-only)

| # | Achado | Evidência | Severidade |
|---|---|---|---|
| 1 | Saturação sistêmica além de agents | `CLAUDE.md` citado em 72/72 `SKILL.md` (100%) e 22/22 `*.prompt.md` (100%), além de 79 hits em `catalog.yaml` | Alto |
| 2 | `agent-contracts/SKILL.md` é instância do próprio smell que corrigiria | `source_docs: [CLAUDE.md, .github/copilot-instructions.md]` no frontmatter da skill que define o banner "Skills Carregadas" | Alto |
| 3 | Campo duplicado e não-canônico em `catalog.yaml` | `prerequisite_docs:` vs. `source_docs:` — arrays sobrepostos, ambos full-load dos mesmos 2 arquivos | Alto |
| 4 | `source_docs:` é campo **gerado**, não editável manualmente | `tools/agent_source_docs_sync/sync_required_source_docs.py` (`--check`/`--apply`) + `tests/governance_audit/test_sync_required_source_docs_invariants.py` (exige drift=0) — edição manual do YAML seria revertida/flagada pelo CI | **Bloqueador** |
| 5 | Colisão de numeração normativa | `CLAUDE.md` contém R-001..R-065 contíguos, sem lacunas; **R-065 já ocupado** ("Guard de Severidade Arquitetural", `workflows.md` § 1.5, coberto por `test_r065_severity_guard.py`) | **Bloqueador** |
| 6 | Gap de teste determinístico | Nenhum teste em `tests/governance_audit/` valida teto de volume/tokens de pre-fetch (`test_sync_required_source_docs_invariants.py` só valida drift=0, não tamanho) | Médio |
| 7 | Templates canônicos não verificados neste ciclo | `.github/agents/templates/*`, `skills/templates/skill-template.md`, `prompts/templates/prompt-template.md` — pendente checar se já preveem o campo `source_docs`/`prerequisite_docs` | Sugestão |
| 8 | Sub-catálogos stack-specific não inspecionados | `spring-boot-catalog.yaml`, `spring-reactive-catalog.yaml`, `ejb-catalog.yaml`, `database-catalog.yaml`, `angular-catalog.yaml`, `struts-catalog.yaml`, `python-catalog.yaml` — pendente confirmar mesmo padrão | Sugestão |

---

## 3) Opções Consideradas e Decisão Técnica

| Opção | Descrição | Decisão |
|---|---|---|
| A — Editar `catalog.yaml` manualmente | Remover `copilot-instructions.md`/substituir por `ctx_search` direto no YAML | ❌ Rejeitada — seria revertida pelo gate de CI (`sync_required_source_docs.py --check`, Achado #4) |
| B — Alterar a lógica do gerador (`sync_required_source_docs.py`) + schema | Fonte de verdade do pre-fetch passa a diferenciar full-load vs. lazy-load na origem; `catalog.yaml` é regenerado via `--apply` | ✅ **Adotada** |
| C — Ignorar duplicação `prerequisite_docs`/`source_docs` nesta rodada | Resolver só o full-load sem resolver a duplicação de campo | ❌ Rejeitada — R-003 (sem duplicação) seria violado persistentemente; correção parcial geraria retrabalho |
| D — Numerar a nova regra como R-065 | Conforme proposta original (pré-diagnóstico) | ❌ Rejeitada — colisão confirmada (Achado #5); **adotado R-066** |
| E — Restringir correção só a `catalog.yaml` de agents | Ignorar saturação em skills/prompts | ❌ Rejeitada — R-055 (Reúso Sistêmico) exige tratar os peers (Achado #1) |

---

## 4) Alternativas Rejeitadas (detalhamento)

- **Confiar em prompt caching do provedor como solução suficiente**: rejeitada porque cada `run_subagent` abre contexto novo (sem cache compartilhado entre spawns no modelo atual de handoff), portanto não mitiga o custo real por handoff em workflows de múltiplos agentes.
- **Aplicar R-066 (teto de orçamento) sem o contrato de 2 camadas (`source_docs:` vs `source_docs_lazy:`)**: rejeitada por ser um teto sem mecanismo de enforcement — precisa da distinção estrutural para ser auditável.
- **Remover `CLAUDE.md`/`copilot-instructions.md` totalmente do pre-fetch sem substituto**: rejeitada — alguns agents genuinamente precisam de contexto normativo mínimo; a substituição correta é por `ctx_search` direcionado, não omissão total.

---

## 5) Escopo Delimitado e Artefatos Impactados

| Frente | Artefatos-alvo | Blast Radius Estimado |
|---|---|---|
| **F1 — Gerador e schema** | `tools/agent_source_docs_sync/sync_required_source_docs.py`, `catalog.yaml` (regenerado via `--apply`, não editado manualmente), resolução de `prerequisite_docs` vs `source_docs` | Alto — toca 35 agents, mas via ferramenta determinística |
| **F2 — Skills e prompts (extensão de escopo R-055)** | 72 `SKILL.md` (incl. `agent-contracts/SKILL.md`), 22 `*.prompt.md` | Alto — mesma saturação 100% |
| **F3 — Fatiamento de `workflows.md`** | `.github/agents/workflows.md` → 9-10 arquivos por workflow (`.github/agents/workflows/<workflow>.md`) + índice leve | Médio — consumido hoje só por 3 agents, mas arquivo monolítico de 174k chars |
| **F4 — Regra normativa R-066** | `CLAUDE.md`, `.github/copilot-instructions.md` (espelhado), `governance-audit-patterns/SKILL.md` § 2 (nova categoria de smell) | Médio |
| **F5 — Teste determinístico** | Novo `tests/governance_audit/test_r066_progressive_disclosure_budget.py` | Pequeno |
| **F6 — Templates canônicos** | `.github/agents/templates/*`, `skills/templates/skill-template.md`, `prompts/templates/prompt-template.md` | Pequeno |
| **F7 — Sub-catálogos stack-specific** | `*-catalog.yaml` de domínio (verificação + correção se aplicável) | A confirmar na Etapa 2 (Plano de Implementação) |

---

## 6) Não-Escopo Explícito

- ❌ Não remove nenhuma regra normativa (R-xxx) existente — apenas adiciona R-066 e corrige o mecanismo de acesso a `CLAUDE.md`/`copilot-instructions.md`.
- ❌ Não altera o conteúdo normativo de `CLAUDE.md` além da nova regra R-066 e espelhamento em `copilot-instructions.md` — não é uma reescrita de regras existentes.
- ❌ Não implementa o ciclo de "governance garbage collection" mais amplo do plano irmão `20260929-governance-maintenance-harness-bloat-audit.md` (escopo distinto, ainda pendente de aprovação própria).
- ❌ Não migra enforcement textual para enforcement mecânico via hooks (fora de escopo deste plano).
- ❌ Não edita `catalog.yaml` manualmente em nenhuma hipótese — toda mudança de `source_docs`/`prerequisite_docs` passa pelo script gerador (`--apply`).

---

## 7) Riscos Técnicos e Blast Radius Inicial

| Risco | Severidade | Mitigação |
|---|---|---|
| Editar `catalog.yaml` manualmente e quebrar o gate de drift do CI | Bloqueador | Toda mudança via `sync_required_source_docs.py --apply`; nunca editar o YAML diretamente |
| Numerar a nova regra incorretamente (colisão com R-xxx futura) | Bloqueador (mitigado) | Confirmado R-066 como próximo número livre nesta auditoria; validar novamente antes de escrever em `CLAUDE.md` |
| Fatiar `workflows.md` e quebrar referências existentes (`agent-router.agent.md`, `runtime-verifier.agent.md`, `codegraph-engine.agent.md` citam `workflows.md` por seção) | Alto | Manter `workflows.md` como índice com links estáveis; atualizar as 3 referências diretas no mesmo commit atômico |
| Resolver duplicação `prerequisite_docs`/`source_docs` sem quebrar consumidores do campo antigo | Alto | Levantar todos os consumidores (`tools/`, testes, outros scripts) antes de alterar o schema |
| Escopo subestimado (sub-catálogos stack-specific não verificados) | Médio | Etapa de Plano de Implementação inclui verificação explícita antes de aplicar F7 |
| `agent-contracts/SKILL.md` corrigir a si mesma gerar inconsistência temporária | Baixo | Incluir no mesmo PR/commit de F2 |

---

## 8) Critério de Aceite e Definition of Done — Status Final: 100% Concluído (com 2 ajustes de escopo documentados)

- [x] `sync_lazy_source_docs.py` (nova ferramenta, complementar a `sync_required_source_docs.py`) diferencia `source_docs` (full-load seguro, <500 linhas) de `source_docs_lazy` (full-load proibido; consumo via `ctx_search`) — allowlist fixa de 3 documentos centrais (CLAUDE.md, copilot-instructions.md, workflows.md); tentativa de generalizar por limiar dinâmico de linhas foi revertida por conflitar com R-042/R-049 (ver implementation-plan § 0.4).
- [x] ~~Duplicação `prerequisite_docs` vs `source_docs` resolvida~~ → **Investigado (INV-01) e registrado como pendência formal**: `catalog.yaml` confirmado manualmente mantido, sem gerador automático (`tools/agent_protocol_sync` cobre apenas `<execution_protocol>`). Resolução da duplicação requer ciclo de planejamento dedicado (ver implementation-plan § 13).
- [x] ~~`catalog.yaml` regenerado via `--apply`~~ → **N/A**: confirmado que nenhuma ferramenta gera `catalog.yaml`; nenhuma edição foi feita neste arquivo nesta rodada (preservação de integridade).
- [x] `agent-contracts/SKILL.md` e demais 71 skills/22 prompts (+ 95 `.agent.md`) migrados para o novo contrato de 2 camadas — 188 artefatos no total, drift=0.
- [x] `workflows.md` fatiado em 10 arquivos (9 workflows + invariantes-e-protocolos) sob `.github/agents/workflows/` + índice leve (199 linhas); **5** referências diretas atualizadas (não 3 — achado de T0); **11** testes de CI corrigidos (não 3 — achado de T0, blast radius real ~4x maior que a estimativa inicial).
- [x] R-066 registrada em `CLAUDE.md` e espelhada em `copilot-instructions.md`; nova categoria de smell (**2.31**, não 2.27 — já ocupado) em `governance-audit-patterns/SKILL.md` § 2.
- [x] `tests/governance_audit/test_r066_progressive_disclosure_budget.py` criado e verde (6 testes).
- [x] Templates canônicos (F6 — 4 templates de agent + skill + prompt) atualizados para já nascerem em conformidade.
- [x] `CHANGELOG.md` recebe entrada registrando a mudança ([2.52.0]).
- [x] Nenhuma edição manual de `catalog.yaml` ocorreu em nenhuma fase (confirmado — arquivo intocado nesta rodada).

**Validação final**: 508/509 testes passando na suíte completa (`governance_audit` + `operational_flow` + `routing_unit` + `evals` + `routing_gate`); 1 falha pré-existente e não-relacionada. Detalhamento completo da execução em `docs/implementation-plans/20261003-governance-maintenance-progressive-disclosure-source-docs.md`.

---

## 9) Adendo Pós-Conclusão — Gap de Discovery Encontrado e Corrigido

Após a conclusão de 100% das 7 frentes (F1-F7), revisão adicional do usuário identificou um **gap crítico não coberto pelo escopo original**: a migração moveu `CLAUDE.md`/`copilot-instructions.md`/`workflows.md` para `source_docs_lazy:` em 188 artefatos, mas **nenhum texto no corpo** desses artefatos instrui o agente sobre o que essa chave significa operacionalmente. A única explicação textual completa (R-066 em `CLAUDE.md`) estava dentro do próprio arquivo classificado como lazy — um problema de bootstrapping circular.

### Solução aplicada
Reaproveitado o mecanismo já existente `tools/agent_protocol_sync/sync_execution_protocol.py` (fonte única `_execution-protocol-fragment.md`) — adicionado o **item 8** ao bloco canônico `<execution_protocol>`, propagado via `--apply` para os **84 agents STANDARD**, garantindo que a instrução viva **no próprio corpo do agente** (sempre lido, nunca dependente de um skill externo opcional).

### Critério de aceite do adendo — 100% atendido
- [x] Item 8 (`source_docs_lazy`/R-066) adicionado ao fragmento canônico.
- [x] Propagado para 84/85 agents mapeados (1 CUSTOM inalterado por design).
- [x] 2 novos testes determinísticos (`test_execution_protocol_fragment_instructs_source_docs_lazy_semantics`, `test_standard_agents_execution_protocol_propagated_with_source_docs_lazy_item`).
- [x] `CHANGELOG.md` [2.52.1] registra a correção.
- [x] Suíte completa revalidada: 539/540 passando.

Detalhamento completo em `docs/implementation-plans/20261003-governance-maintenance-progressive-disclosure-source-docs.md` § 14.

---

## 10) Adendo Pós-Conclusão #2 — Gap Irmão: Prompts Também Precisavam do Bloco

Revisão adicional do usuário sobre `test-strategy.agent.md` levantou a pergunta correta: "os prompts também não deveriam ter `<execution_protocol>`?". Investigação via `context-mode/ctx_execute` confirmou **100% dos 22 `*.prompt.md` com `source_docs_lazy:` mas 0% com o bloco operacional** — o mesmo gap do Adendo #1, nunca propagado para prompts porque o script só varria `.github/agents/`.

### Solução aplicada
`sync_execution_protocol.py` estendido com `get_prompt_files()` + `sync_prompts()` (mesma fonte canônica, inserção ao final do corpo). Aplicado via `--apply` em 22/22 prompts. Corrigido conflito de nomenclatura em `test_prompt_synthesis_output_format_governance.py` (`<execution_protocol>` colidia com uma tag XML residual proibida de conceito histórico não-relacionado). Template `prompts/templates/prompt-template.md` atualizado para já nascer em conformidade.

### Critério de aceite do adendo #2 — 100% atendido
- [x] `sync_execution_protocol.py` estendido para cobrir prompts (mesma fonte canônica, sem duplicar lógica).
- [x] 22/22 prompts corrigidos, drift=0.
- [x] Conflito de nomenclatura com `test_no_residual_xml_prompt_synthesis` resolvido sem perder a proteção original.
- [x] Novo teste `test_all_prompts_contain_execution_protocol_block`.
- [x] Template canônico de prompt atualizado.
- [x] `CHANGELOG.md` [2.52.2] registra a correção.
- [x] Suíte completa revalidada: 540/541 passando.

Detalhamento completo em `docs/implementation-plans/20261003-governance-maintenance-progressive-disclosure-source-docs.md` § 15.

---

## 11) Próximo Passo Mínimo

Nenhum — ciclo 100% concluído, incluindo os 2 adendos de discovery (agents e prompts). Pendências formais remanescentes (duplicação `prerequisite_docs`/`source_docs` em `catalog.yaml`; generalização do teto de linhas além da allowlist fixa) permanecem registradas para um ciclo de governança futuro e separado (ver implementation-plan § 13).

