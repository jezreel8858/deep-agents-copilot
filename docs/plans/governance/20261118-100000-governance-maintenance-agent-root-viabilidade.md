---
title: "Plano de Governança — Viabilidade de um agent selecionável @agent-root (Router First, R-037/R-062/R-063/R-068)"
status: DRAFT
approved: false
author: "@agent-auditor"
plan_type: "governance"
tier: "governance"
review_rounds: 2
reviewer: "@plan-critic"
review_verdict: "PASS_WITH_NITS"
review_tier1: "PASS"
created_at: "2026-11-18"
related-planning-doc: "N/A"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-20261118-agent-root-viabilidade"
plan_ref: "docs/plans/governance/20261117-160000-blindagem-aderencia-raiz-workflow.md"
parent_plan_ref: "docs/plans/governance/20261117-160000-blindagem-aderencia-raiz-workflow.md"
rollback_plan: "git revert do commit do lote (reverte atomicamente os arquivos de allowed_files); pré-commit: git restore -- .github/prompts/catalog.yaml .github/prompts/README.md e remover o arquivo novo .github/prompts/workflow-bootstrap.prompt.md; sem aprovação do Gate nenhum arquivo fora de docs/plans/ é alterado"
allowed_files_conditional: "CONDICIONAL à decisão do Gate: só vale se aprovada a opção E+D; nas demais decisões nenhum arquivo de allowed_files é tocado (ver §10). allowed_files cobre só .md/.yaml; os 3 testes .py afetados (test_context_mode_precedence_governance.py, test_template_sections.py, test_utility_slash_prompts_bypass.py) ficam FORA e exigem plano de implementação próprio (R-055 Q3: .py via @python-router), aprovado e aplicado no mesmo lote de commit do prompt (ver §5.1). Se Q6 = (a), exige-se também um plano de governança .md próprio (dono: @governance-maintainer) para ajustar a exceção canônica em .github/copilot-instructions.md (:12/:20/:46) e .github/agents/workflows/invariantes-e-protocolos.md (:525), no mesmo lote de commit; esses 2 arquivos NÃO entram em allowed_files deste plano"
allowed_files:
  - ".github/prompts/workflow-bootstrap.prompt.md"
  - ".github/prompts/catalog.yaml"
  - ".github/prompts/README.md"
---

# Viabilidade de um agent selecionável @agent-root

> Materializado por `@docs-engineer` (R-064) a partir do parecer de `@agent-auditor` (Etapa 1) e da pesquisa de `@deep-search` (Etapa 2). Plano em **DRAFT**: nenhuma alteração fora deste arquivo foi feita. Plano-base já aplicado: [R-068](20261117-160000-blindagem-aderencia-raiz-workflow.md).

## 1. Problema e hipóteses (fato × hipótese)

Pergunta do usuário: faz sentido criar um agent específico (ex.: `@agent-root`) selecionável no chat do Copilot, com todos os guardrails, diretrizes e tools carregados?

### 1.1 Fatos verificados

| # | Fato | Fonte |
|---|---|---|
| F1 | R-063 (Router First) já está no kernel | `.github/copilot-instructions.md:49` (confirmado) |
| F2 | R-062 já está no kernel | `.github/copilot-instructions.md:50` (confirmado) |
| F3 | Kernel R-068 (Raiz = Executor) já aplicado | `.github/copilot-instructions.md:81` (seção "Raiz = Executor de Workflow (R-068)"; confirmado) |
| F4 | O repositório tem 63 agents (`*.agent.md` recursivos em `.github/agents/`); nenhum declara `user-invocable` (varredura 0/63) | `.github/agents/**/*.agent.md` |
| F5 | O `@agent-router` tem 7 tools (`read_file`, `file_search`, `grep_search`, `list_dir`, `ask_questions`, `run_subagent`, `context-mode/ctx_search`) | `.github/agents/agent-router.agent.md` (frontmatter `tools`) |
| F6 | Paridade VS Code/JetBrains não é garantida (nota 9.3 do changelog sobre tabela de modelos × `get_errors`; evidência indireta, trata de nomes de modelo, não de custom agents) | `.github/agents/catalog.yaml:2824` |
| F7 | Exceção `router_bypass: utility \| slash_workflow` já existe (R-037/R-063) | `.github/agents/workflows/invariantes-e-protocolos.md:525` (título) e `:527`; `.github/copilot-instructions.md:12`, `:20`, `:46` |
| F8 | Já existe o prompt `/agent-router` como atalho de entrada; ele **não declara** `router_bypass` no frontmatter (campo ausente). `router_bypass: null` aparece só como entrada em `.github/prompts/catalog.yaml:13` (representação do catálogo, não do frontmatter). O contrato só reconhece `utility` e `slash_workflow`; a ausência cai no grupo "isento" da contagem e é **caso único** (`test_utility_slash_prompts_bypass.py:131`) | `.github/prompts/agent-router.prompt.md` (frontmatter), `.github/prompts/catalog.yaml:9-13`, `.github/copilot-instructions.md:12` |
| F9 | Não há casos reais nem traços de falha pós-R-068 (**lacuna declarada**) | Etapa 1 |

### 1.2 Hipóteses não testadas

| # | Hipótese | Status |
|---|---|---|
| H1 | O `copilot-instructions.md` longo dilui o kernel R-068 | Não testada |
| H2 | O raiz não carrega tools/skills porque instruções sempre ativas não declaram `tools` | Não testada |
| H3 | Sem hooks no JetBrains, não há enforcement determinístico | Parcial (`.github/hooks/README.md:48-66`: hipótese forte de que `preToolUse` não é aplicado a subagents no JetBrains; teste 2026-10-03 confirmado no arquivo) |

## 2. UNKNOWN do host e roteiro de teste empírico

### 2.1 Resultado da pesquisa (JetBrains)

| Capacidade | Confiança | Observação |
|---|---|---|
| Custom agents `.github/agents/*.agent.md` aparecem no dropdown | Alta | Preview pública, sujeita a mudança; agents globais em `~/.copilot/agents/*.agent.md` (changelog 2026-05-13) |
| `model` respeitado | Alta | — |
| `tools` respeitado | Média | — |
| `handoffs` e `user-invocable` | Baixa | Sem confirmação no JetBrains |
| `target` | — | Só `vscode` / `github-copilot` |
| Agent selecionado no dropdown vira o agent principal da sessão | Média | **Ponto central**: um `@agent-root` selecionado É o turno raiz |
| Campo de "agent recomendado/default" por repositório | Baixa | Ausência de evidência |
| Carregamento de `copilot-instructions`/`applyTo` no JetBrains | Declaração do repositório (`.github/instructions/README.md`:107) | Sem fonte oficial; limite de tamanho sem fonte |

Fonte oficial: docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-custom-agents.

### 2.2 Roteiro de teste (5 passos, executado pelo usuário; os agents não rodam comandos)

1. Criar `probe-root.agent.md` com `tools` restritos e marcador `PROBE-ROOT-1`; verificar se aparece no dropdown.
2. Selecionar o agent; verificar marcador, modelo e bloqueio de tool fora do escopo.
3. Criar `probe-hidden` com `user-invocable: false` e `probe-handoff` com `handoffs`; verificar visibilidade e comportamento.
4. Pedir ao `probe-root` que invoque `probe-hidden` via `run_subagent`; confirmar que `probe-root` segue como turno raiz.
5. Criar `probe.instructions.md` com `applyTo: "**/*.md"` e comparar com o agent padrão; inflar `copilot-instructions.md` para detectar truncamento.

Meta: UNKNOWN do host 5 → 0. Os arquivos probe são descartáveis e **fora** de `allowed_files` (criados manualmente pelo usuário).

## 3. Matriz de colisão do `@agent-root`

| Colisão | Severidade |
|---|---|
| Dois cérebros × `@agent-router` | Alto |
| R-037/R-063 ambíguo se o agent selecionado vira o turno raiz | Alto |
| R-062 deixa de se aplicar se o agent assina como agent-root | Alto |
| R-066 "carregar tudo" contradiz progressive disclosure | Alto |
| R-068: duplicação do kernel | Médio |
| R-054: tools amplas | Médio |
| Catálogo: `catalog.yaml`, `routing-graph`, AgentCard em `.a2a/agentcards`, contagens de paridade (`test_a2a_agentcards_parity.py`, `test_agent_count_per_stack_governance.py`) | Médio |

Smells: 2.12 (conflito router × agent-root) e 2.13 (kernel duplicado) — Alto; 2.23 (se tools amplas) — Alto; lacuna de evidência e UNKNOWN de host — Sugestão.

## 4. Opções comparadas (R-055 Q1–Q3)

R-055: Q1 = já existe algo reutilizável? Q2 = dá para estender em vez de criar? Q3 = só então criar.

| Opção | Carrega | Seleção | Catálogo | Custo | Benefício | Risco |
|---|---|---|---|---|---|---|
| A) Novo `@agent-root` com kernel mínimo + ponteiros lazy | Kernel + ponteiros | Dropdown | Toca catalog, routing-graph, AgentCard, paridade | Alto | Entry point explícito | Alto (§3) |
| B) Wrapper fino "modo workflow" (invoca router e executa pipeline) | Kernel via ponteiro | Dropdown | Idem A | Médio | Reduz execução direta | Médio-Alto |
| C) Reforçar só o kernel em `copilot-instructions.md` | Já carregado | N/A | Não | Baixo | Sem novo artefato | Médio (H1: diluição; limite do orçamento de `test_root_instruction_file_budget.py`) |
| D) Slash prompt de bootstrap opt-in | Kernel via ponteiro | `/` | Só catálogo de prompts | Baixo | Opt-in, sem 2º entry point | Baixo |
| E) Nada agora, coletar traços | — | — | Não | Mínimo | Decide com evidência | Baixo (problema pode persistir) |

Q1: o prompt `/agent-router` (F8) já cobre parte de D. Q2: D estende o padrão de prompts existente. Q3: só A/B criariam um agent novo e dependem de §2.

## 5. Recomendação do auditor: E + D

**Não criar `@agent-root` agora.** Executar E (coletar traços) com D (prompt de bootstrap opt-in).

- **D**: `.github/prompts/workflow-bootstrap.prompt.md` (nome provisório) que carrega o kernel R-068 **por ponteiro** (sem copiar texto), manda invocar `@agent-router` na 1ª ação e executar o pipeline emitido.
- **Frontmatter do prompt (decisão Q6 — duas opções com contrato real)**:
  - **(a) Ausência de `router_bypass`** (como `/agent-router`): coerente com a intenção de D (1ª ação = router), pois o prompt não é bypass. Impacto: o prompt vira o 2º "isento" fora de `utility`; exige alterar `test_utility_slash_prompts_bypass.py:131` (caso único) e a exceção canônica (`copilot-instructions.md:12/:20/:46`, `invariantes-e-protocolos.md:525`) para reconhecer a variante, e passa a contagem de isentos de 9 para 10. Trade-off: menor mudança de comportamento, maior mudança de contrato/teste.
  - **(b) `router_bypass: slash_workflow`**: reaproveita valor reconhecido. Impacto: exige `context-mode/ctx_resume`, `ctx_index` e `ctx_search` em `tools` (`test_context_mode_precedence_governance.py:1016-1020`), contagem 15 → 16, e o teste `test_utility_slash_prompts_bypass.py:123-125` exige a menção/diretriz a `@agent-router` e a `router_bypass: slash_workflow`, o que contradiz a 1ª ação de D e reabre R-063. Trade-off: menos mudança de contrato, mas desvirtua o propósito do prompt.
  - **Recomendação: (a)**, porque (b) é incompatível com o objetivo de D (iniciar pelo router) e com o guard de `slash_workflow`; o custo de (a) é localizado (1 teste + texto da exceção) e deve ir no plano de implementação dos testes. Alternativa de menor custo fora de Q6 (R-055 Q2): estender o próprio `agent-router.prompt.md` com a seção de bootstrap, sem prompt novo (não altera contagens), mas muda `allowed_files`; registrada para o Gate.
- **Catálogo de prompts**: registro em `.github/prompts/catalog.yaml` (fonte: frontmatter, R-015) e linha em `.github/prompts/README.md`.

### 5.1 Impacto verificado em testes (resolve o UNKNOWN de contagem de prompts)

Estado real do disco: 24 `.prompt.md` = 15 `slash_workflow` + 8 `utility` + 1 sem campo (`agent-router.prompt.md`).

| Teste | Linha | Asserção afetada por 1 prompt novo | Ajuste necessário |
|---|---|---|---|
| `tests/governance_audit/test_context_mode_precedence_governance.py` | `:1010-1011`, `:1040`, `:1044` | 24 prompts; 15 `slash_workflow`; 9 isentos (8 utility + agent-router) | 24 → 25; isentos 9 → 10 em (a) ou `slash_workflow` 15 → 16 em (b) |
| `tests/governance_audit/test_template_sections.py` | `:451` (docstring `:442`) | `len(prompt_files) == 24` | 24 → 25 |
| `tests/governance_audit/test_utility_slash_prompts_bypass.py` | `:131-141` (docstring `:12`) | `agent-router.prompt.md` é o único sem `router_bypass` | Em (a) relaxar o caso único; em (b) incluir o novo nome na lista `expected_with_bypass` e a menção/diretriz a `@agent-router` e `router_bypass: slash_workflow` (`:123-125`) |

**Decisão de escopo**: os 3 testes (`.py`) **não** entram em `allowed_files` deste plano (escopo `.md`/`.yaml`; Não-Escopo §7; R-055 Q3: `.py` via `@python-router`). Aprovar E+D exige, como **pré-condição**, um plano de implementação próprio para esses testes, aplicado no mesmo lote de commit do prompt; sem isso a suíte `tests/governance_audit` quebra. **Se Q6 = (a)** (recomendada, ausência de `router_bypass`), a pré-condição inclui também um **plano de governança `.md` próprio**, de dono `@governance-maintainer`, para ajustar a exceção canônica em `copilot-instructions.md` (:12/:20/:46) e `invariantes-e-protocolos.md` (:525) — esses 2 arquivos não entram em `allowed_files` deste plano; o plano `.py` e o plano `.md` de governança vão **no mesmo lote de commit** do prompt. Lacuna: o docstring de `test_utility_slash_prompts_bypass.py:115` cita "13 prompts slash_workflow" (diverge dos 15 reais); a forma exata de `expected_with_bypass` não foi lida — o executor deve conferir.

- **Condição de retomada de A/B**: (i) o teste do host confirmar que o agent selecionado carrega `tools`/instruções próprias e (ii) traços mostrarem falha repetida do kernel R-068.

## 6. Análise adicional — variante B' (agent-root = perfil de chat)

Premissa (confiança média): o agent selecionado no dropdown é o turno raiz. **B'** = `@agent-root` é um perfil de chat que (1) carrega o kernel R-068 **por ponteiro**, (2) invoca `@agent-router` via `run_subagent` na 1ª ação e (3) executa o pipeline emitido (Flat Delegation).

### 6.1 O que mudaria em R-062/R-063 (exceção declarada, não regra duplicada)

| Regra | Hoje | Mudança mínima em B' |
|---|---|---|
| R-063 | O turno raiz não executa tarefa técnica sem router; "ausência de agent ativo" não autoriza execução direta | Declarar `@agent-root` como **perfil do turno raiz**: continua sujeito a R-063; sua 1ª ação obrigatória é o router. Não é novo cérebro de roteamento |
| R-062 | Aplicação ao agent ativo que assina | Declarar que o banner/assinatura do `@agent-root` não o torna "agent ativo" para fins de R-062; o agent ativo continua sendo o downstream do pipeline |
| R-037 | Router é o entry point | Acrescentar `@agent-root` à lista de exceções/equivalências com texto curto e ponteiro; o router segue sendo o único classificador |

- O kernel R-068 continua definido **em um só lugar** (`copilot-instructions.md`); o agent traz só um ponteiro, sem copiar texto (evita Smell 2.13).
- Tools: no máximo as do router (7) + `run_subagent`; ampliar gera Smell 2.23 e viola R-054.
- Se aprovada, B' exige plano próprio (novo ciclo) que toque `copilot-instructions.md`, `CLAUDE.md`, `invariantes-e-protocolos.md`, `routing-graph.yaml`, catálogo e AgentCard; **fora** de `allowed_files` deste plano.
- Risco residual: `user-invocable`/`handoffs` sem confirmação no JetBrains (baixa) e preview pública sujeita a mudança.

## 7. Solicitação refinada

**Tarefa**: Decidir, com evidência, se o ecossistema deve ganhar um ponto de entrada selecionável no chat (`@agent-root` / B') ou um prompt opt-in (D), de modo que o turno raiz carregue o kernel R-068 e inicie sempre pelo `@agent-router`.

**Contexto**: R-063, R-062 e R-068 já aplicados; 63 agents sem `user-invocable`; sem traços de falha pós-R-068; host JetBrains com paridade não garantida e sem hooks determinísticos; um agent selecionado tende a virar o turno raiz.

**Restrições e Não-Escopo**:
- Somente `.md`; nenhum código de aplicação alterado.
- Não criar `@agent-root` nesta etapa; não alterar neste plano `copilot-instructions.md` nem `invariantes-e-protocolos.md` (se Q6 = (a), o ajuste da exceção canônica é feito em plano de governança `.md` próprio, dono `@governance-maintainer`, mesmo lote de commit); não alterar `CLAUDE.md`, routing-graph, catalog.yaml dos agents ou AgentCards.
- Não duplicar o kernel R-068; não contradizer R-037/R-062/R-063; progressive disclosure (R-066) preservado.
- Testes do host executados pelo usuário, não pelos agents.
- Fora de escopo: otimização de modelo, mudança de hooks, paridade VS Code/JetBrains além do que o teste revelar.

**Formato de Saída**: este plano (`.md`, PT-BR) com decisão pendente do Gate; se aprovado E+D, um prompt `.prompt.md` novo + registro no catálogo de prompts; os ajustes de testes `.py` (§5.1) seguem em plano de implementação próprio.

**Critério de sucesso**: ver §8.

## 8. Critérios de sucesso

| # | Critério | Medição |
|---|---|---|
| S1 | ≥ 3 traços reais classificados por causa | Planilha/nota de traços |
| S2 | UNKNOWN do host 5 → 0 | Roteiro §2.2 |
| S3 | Queda ≥ 50% de execução direta sem router. **Condicional a S1**: só se aplica com ≥ 3 traços na linha de base; senão marcar N/A | Linha de base = nº de execuções diretas sem router nos traços coletados na janela de 14 dias antes do prompt (fonte: relato do usuário/Q1 e spans `handoff:<workflow_trace_id>:<sequence_index>` via `ctx_search`); medição pós = mesma duração após o prompt |
| S4 | Zero contradição R-037/R-062/R-063 | Revisão do plan-critic + `pytest tests/governance_audit` |
| S5 | Testes de contagem/paridade verdes após o lote | `pytest tests/governance_audit/test_context_mode_precedence_governance.py tests/governance_audit/test_template_sections.py tests/governance_audit/test_utility_slash_prompts_bypass.py` (§5.1); acrescentar `test_a2a_agentcards_parity.py` e `test_agent_count_per_stack_governance.py` somente se um agent for criado |

Nota: F9 declara que hoje não há traços; sem S1, S3 fica N/A e a decisão do Gate se apoia em S2/S4/S5.

## 9. Perguntas abertas para o Gate (ask_questions)

Formato R-027: 1–4 perguntas por chamada (apresentar em 2 chamadas: Q1–Q4 e Q5–Q6), `header` ≤ 25 caracteres, `allowFreeformInput: true`, 2–4 opções reais mutuamente exclusivas, `description` = [consequência + trade-off], 1ª opção `(Recomendado)`.

**Q1 — header `Traços pós-R-068`**: Existem casos reais de falha do raiz pós-R-068 (execução direta sem router)?
- `(Recomendado) Informar ≥ 3 traços agora` — converte F9 em fato e habilita S1/S3; trade-off: exige colar os casos.
- `Não há traços; coletar via E` — mantém E+D e deixa S3 como N/A; trade-off: decisão sem baseline.
- `Decidir sem traços` — avança sem evidência; trade-off: A/B ficam sem justificativa (F9).

**Q2 — header `Teste do host`**: Como proceder com o teste do host (§2.2)?
- `(Recomendado) Executar agora` — roda o roteiro §2.2 e transforma UNKNOWN em fato; trade-off: adia a decisão.
- `Executar depois` — decide agora e testa em seguida; trade-off: UNKNOWN residual e A/B/B' ficam fora até o resultado.
- `Dispensar o teste` — decide agora; trade-off: A/B/B' ficam fora por risco de host.

**Q3 — header `Entry point`**: Aceita um 2º entry point (agent selecionável) ou só opt-in via `/`?
- `(Recomendado) Só opt-in via / (D)` — sem 2º cérebro (Smell 2.12) e catálogo de agents intacto; trade-off: não aparece no dropdown.
- `Agent selecionável (A/B/B')` — entry point explícito; trade-off: matriz de colisão §3 em Alto e novo plano.
- `Adiar até teste do host` — preserva opções; trade-off: sem melhoria imediata.

**Q4 — header `Papel do agent-root`**: Se um agent for criado, qual o papel?
- `(Recomendado) Não criar agent` — alinhada a E+D e a Q3; trade-off: sem entry point selecionável. As demais opções só valem se Q3 escolher criar agent.
- `Wrapper que só aciona o router (B)` — mudança mínima em R-062/R-063; trade-off: o raiz ainda executa o pipeline.
- `Executor do pipeline (B')` — cobre R-068 por completo; trade-off: exceções em R-037/R-062/R-063 e plano próprio.

**Q5 — header `Host alvo`**: Qual o host alvo?
- `(Recomendado) JetBrains e VS Code` — respeita a paridade não garantida (F6); trade-off: dobra o roteiro de teste.
- `Só JetBrains` — foco no host com UNKNOWN; trade-off: sem validação no VS Code.
- `Só VS Code` — menor incerteza de host; trade-off: ignora o host sem hooks.

**Q6 — header `router_bypass do prompt`**: Como o prompt D declara o bypass? (detalhes em §5)
- `(Recomendado) (a) Ausência do campo` — mantém 1ª ação = router; trade-off: altera o teste de caso único (`test_utility_slash_prompts_bypass.py:131`), a exceção canônica e isentos 9 → 10.
- `(b) slash_workflow` — valor reconhecido; trade-off: exige `ctx_resume`/`ctx_index`/`ctx_search`, contagem 16, exige a menção/diretriz a `@agent-router` e `router_bypass: slash_workflow` (`test_utility_slash_prompts_bypass.py:123-125`) e reabre R-063.

## 10. Decisão pendente do Gate (HITL — Etapa 5)

| Opção | Efeito | Arquivos tocados |
|---|---|---|
| Aprovar E+D (Recomendado) | Criar prompt de bootstrap + registro no catálogo de prompts; coletar traços; **pré-condição**: plano de implementação dos 3 testes `.py` (§5.1) e, se Q6 = (a), plano de governança `.md` próprio (`@governance-maintainer`) para a exceção canônica (`copilot-instructions.md` :12/:20/:46; `invariantes-e-protocolos.md` :525), ambos aplicados no mesmo lote de commit do prompt | Os 3 de `allowed_files` (condicional); testes `.py` e ajuste da exceção canônica em planos próprios |
| Executar teste do host antes | Rodar §2.2 e reapresentar ao Gate | Nenhum |
| Avançar com B' | Abrir novo plano para A/B' (§6) | Nenhum neste plano |
| Descartar | Encerrar sem mudanças | Nenhum |

## 11. Riscos e rollback

| Risco | Mitigação |
|---|---|
| Prompt D virar 2º entry point implícito | Frontmatter conforme Q6 (recomendado: ausência do campo) e 1ª ação = router |
| Duplicar o kernel no prompt (Smell 2.13) | Somente ponteiro para `copilot-instructions.md` |
| Testes de contagem de prompts quebrarem (24 → 25; isentos 9 → 10 ou `slash_workflow` 15 → 16; caso único) | Plano de implementação dos testes `.py` (§5.1) no mesmo lote; executor roda os 3 testes citados em S5 e depois `pytest tests/governance_audit` |
| Decidir sem evidência do host | Opção "teste do host antes" |
| Preview pública do host mudar | Reavaliar o roteiro §2.2 periodicamente |

Rollback: ver `rollback_plan` no frontmatter.

## 12. Fluxo restante

1. Etapa 4 — `@plan-critic` (teto R-065: 2 rodadas): rodada 1/2 concluída (NEEDS_REVISION, §14); rodada 2/2 concluída (PASS_WITH_NITS, sem BLOCKER/HIGH, sem escalonamento; §14).
2. Etapa 5 — Gate HITL via `ask_questions` (§9–§10).
3. Etapa 6 — `@governance-factory` **somente se aprovado** (E+D).

## 13. UNKNOWN remanescentes

- Comportamento do host (§2.1): `handoffs`, `user-invocable`, limite de tamanho de instruções.
- Forma exata de `expected_with_bypass` em `test_utility_slash_prompts_bypass.py` e divergência "13" × 15 no docstring `:115` (não lidas integralmente). O impacto nas contagens de prompts **deixou de ser UNKNOWN** (§5.1).
- Plano de implementação dos testes `.py` (a abrir; fora de `allowed_files`).
- Campos de revisão do plan-critic: atualizados na rodada 2 (`review_rounds: 2`, `PASS_WITH_NITS`, `review_tier1: "PASS"`).

## 14. Parecer do plan-critic — rodada 1/2

Veredito: **NEEDS_REVISION** · Tier 1: **PASS** · revisor: `@plan-critic`. Resposta da revisão (`@docs-engineer`), verificada contra o repositório:

| # | Sev. | Achado | Resposta |
|---|---|---|---|
| 1 | HIGH | UNKNOWN de contagem de prompts | Resolvido em §5.1 (24 = 15 + 8 + 1; 3 testes com linhas). Testes ficam fora de `allowed_files`, plano próprio, pré-condição de E+D; §5, §10, §11, §13 e frontmatter ajustados |
| 2 | HIGH | Alegação `router_bypass: null` | Corrigida em F8/§5: campo ausente no frontmatter; `null` só em `.github/prompts/catalog.yaml:13`; Q6 = (a) ausência × (b) `slash_workflow`, com impacto, trade-off e recomendação (a) |
| 3 | MEDIUM | Citações de linha | Revalidadas: `copilot-instructions.md` :12/:20/:46/:49/:50/:81 OK; `invariantes-e-protocolos.md:525` OK (título); `hooks/README.md:48-66` OK; `catalog.yaml:2824` qualificado como `.github/agents/catalog.yaml` (nota de changelog sobre modelos/`get_errors`, evidência indireta) |
| 4 | MEDIUM | Critérios §8 | S3 condicional a S1 com linha de base e método; S5 cita os 3 testes de §5.1 |
| 5 | LOW | `tier` | Justificativa de `standard` removida (ver R2-3): `tier: "governance"` adotado na rodada 2 |

## 14.1 Parecer do plan-critic — rodada 2/2

Veredito: **PASS_WITH_NITS** · Tier 1: **PASS** · sem BLOCKER/HIGH · sem escalonamento (teto R-065 de 2 rodadas atingido sem pendência bloqueante).

| # | Sev. | Achado | Resolução |
|---|---|---|---|
| R2-1 | MEDIUM | Q6 (a) também exige plano de governança `.md` para a exceção canônica | Declarado em §5.1, na pré-condição do Gate (§10), no Não-Escopo (§7) e em `allowed_files_conditional`: dono `@governance-maintainer`, mesmo lote de commit do prompt e do plano `.py` |
| R2-2 | MEDIUM | Q4 com 1ª opção incoerente com E+D/Q3 | "Não criar agent" movida para 1ª opção (Recomendado); demais opções só valem se Q3 escolher criar agent |
| R2-3 | NIT | `tier: "standard"` | Corrigido para `tier: "governance"` (convenção majoritária dos planos governance); justificativa de `standard` removida da §14 (achado 5) |
| R2-4 | NIT | Redação "proíbe invocar @agent-router" | Reescrita para "exige a menção/diretriz a `@agent-router` e `router_bypass: slash_workflow` (`test_utility_slash_prompts_bypass.py:123-125`)" em §5, §5.1 e Q6 |
| R2-5 | NIT | Q2 formulada como pergunta de resultado | Reformulada como "Como proceder com o teste do host?", opções = ações (executar agora / executar depois / dispensar), 1ª (Recomendado) |
