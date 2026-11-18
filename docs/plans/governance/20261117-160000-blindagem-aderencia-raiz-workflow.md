---
title: "Plano de Governança — Blindagem da Aderência do Orquestrador Raiz ao Workflow do @agent-router (R-068)"
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-17"
related-planning-doc: "N/A"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-20261117-blindagem-raiz"
parent_plan_ref: "N/A — plano raiz"
review_rounds: 2
reviewer: "@plan-critic"
review_verdict: "PASS_WITH_NITS"
review_tier1: "PASS"
rollback_plan: "git revert <commit-do-lote> (reverte atomicamente todos os arquivos de allowed_files); pré-commit: git restore -- <cada arquivo de allowed_files>"
allowed_files:
  - ".github/copilot-instructions.md"
  - "CLAUDE.md"
  - ".clinerules/00-copilot-bridge.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - ".github/agents/routing-graph.yaml"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/evals/casos-roteamento.yaml"
  - ".github/agents/templates/router-agent.md"
  - "tests/governance_audit/test_root_instruction_file_budget.py"
  - "tests/governance_audit/test_workflows_parity_and_gates.py"
---

# Blindagem da Aderência do Raiz ao Workflow do @agent-router

> Materializado por `@docs-engineer` (R-064) a partir do plano de `@agent-auditor`; **revisão da Etapa 2 após plan-critic rodada 1/2 = FAIL** (ver §12). Os diffs abaixo são **propostos** e serão aplicados pelo `@governance-maintainer` (Etapa 5), que deve **rebasear os hunks** contra o estado vigente dos arquivos.

## 1. Objetivo e princípios

Garantir que o orquestrador raiz execute fielmente o pipeline emitido pelo `@agent-router`.

- **Raiz = EXECUTOR**: não planeja, reclassifica, reordena, pula nem se autoavalia. O router classifica e emite.
- **Sem hooks** (restrição JetBrains). Enforcement = kernel + estado persistido + recibos; sem validador externo.
- **Kernel enxuto** em `copilot-instructions.md`; o restante é lazy (R-066).
- **Proibido**: prompt gigante/caixa alta, autoavaliação, estado apenas em prosa, regra duplicada.

### 1.1 Identificador da regra: R-068 (não R-067)

- **Evidência**: R-067 já existe — `CLAUDE.md:168` (`- **R-067**: Protocolo de Avaliação de Pertinência de Importação de Skills…`), `copilot-instructions.md:56`, `routing-graph.yaml:73-74`, `agent-router.agent.md:439`, e é validado por `test_skill_import_viability_gate.py` (`test_r067_declared_in_claude_md`). Nenhuma ocorrência de `R-068` em `*.md|*.py|*.yaml|*.yml|*.json` do repositório (varredura executada) → **R-068 é o próximo ID livre**.
- **Decisão**: criar **R-068**. Definição única = kernel em `copilot-instructions.md`; `CLAUDE.md` recebe apenas a entrada de índice (convenção do arquivo: uma linha por regra) com ponteiro, sem duplicar o conteúdo.
- **Alternativa descartada** (não criar regra e ancorar no kernel): o kernel normativo ficaria fora do índice de regras de `CLAUDE.md`, sem ID citável em evals/testes; trade-off a confirmar no Gate 4.
- **Efeito no teste de continuidade**: `test_claude_md_normative_rules_continuity` (em `tests/governance_audit/test_root_instruction_file_budget.py:43-51`, **não** em outro arquivo) exige `max(rule_numbers) == 67` e `range(1, 68)`; adicionar R-068 **sem** atualizá-lo faria o teste falhar. Atualizar para `== 68` / `range(1, 69)`, docstring (:44) e docstring do módulo (:4).

### 1.2 Artefatos afetados pela contagem de regras (descobertos por varredura)

| Artefato | Ocorrência literal | Ação |
|---|---|---|
| `CLAUDE.md:15` e `:97` | `## 3) Regras Normativas (R-001..R-067)` (dois cabeçalhos idênticos) | Atualizar ambos para `R-001..R-068`. |
| `CLAUDE.md` após `:168` | — | Inserir `- **R-068**: Raiz = Executor de Workflow …→ copilot-instructions.md § Raiz = Executor de Workflow` (padrão `**R-NNN` exigido pelo regex do teste). Linhas: 227 → 228 (≤ 250, alvo do teste). |
| `.clinerules/00-copilot-bridge.md:13` | `(R-001 a R-067)` | Atualizar para `R-001 a R-068`. |
| `test_root_instruction_file_budget.py` :4, :44, :48, :49 | `R-001..R-067`, `67`, `range(1, 68)` | Atualizar para 68 / `range(1, 69)`. |
| `AGENTS.md` | Sem ocorrência de `R-001..R-067`/`67 regras` | **Não** incluído em `allowed_files` (nenhuma mudança necessária pela varredura). |
| `test_governance_smells.py` | test_governance_smells.py:21: CASOS_ROTEAMENTO = AGENTS_DIR / "evals" / "casos-roteamento.yaml"; test_governance_smells.py:118: arquivos_alvo = [CLAUDE_MD, COPILOT_INSTRUCTIONS, CASOS_ROTEAMENTO]; test_governance_smells.py:425: def _get_latest_normative_rule_number() -> int: | Cálculo **dinâmico** (sem número fixo); impacto de 67→68: **UNKNOWN** — executor roda `pytest tests/governance_audit`. |
| `test_skill_import_viability_gate.py` | Apenas checa presença de `R-067` | Sem alteração. |

## 2. Contradições e resolução (SSOT) — âncoras literais reverificadas

Reverificação executada contra os arquivos reais nesta revisão. Âncora = trecho literal (número de linha é só auxiliar; o executor deve rebasear).

| # | Conflito | Âncora literal (fonte) | Reverificação | Resolução (SSOT) |
|---|---|---|---|---|
| C1 | Flat Delegation único × router despacha só a etapa 1 | `copilot-instructions.md:45` "O Orquestrador despacha o downstream uma única vez em nível plano (Flat Delegation)"; `agent-router.agent.md:118` "Despacha direto para a Etapa 1 do workflow"; `agent-router.agent.md:325` "### 🗺️ Pipeline de Execução do Workflow (<total> etapas):" (itens :326-330) | ✔ confirmadas; :325-330 = título + 5 itens (antes imprecisa) | Router emite o pipeline e despacha a etapa 1; o raiz executa as demais, uma delegação plana por etapa. |
| C2 | Continuação × re-triagem/reset | `copilot-instructions.md:36` "Não -> agent ativo continua respondendo no workflow" (diagrama :34-36) e `:47` "Re-triagem Obrigatória por Turno (R-042 — Anti Sticky-Session)"; `CLAUDE.md:60` **R-042**; `CLAUDE.md:71` **R-052** | ✔ :60 e :71 corretos; **corrigido**: o texto normativo de re-triagem está em :47 (:36 é só o diagrama) → ambos entram no diff | Com pipeline ativo, continuação = avanço de `etapa_atual`; re-triagem só em deriva; reset só ao concluir. |
| C3 | Dispensa de etapa sem dono | `routing-graph.yaml:455` "nota: Etapa opcional/condicional … Stacks sem E2E writer dedicado pulam esta etapa s…" (trecho final não relido: **UNKNOWN**); `invariantes-e-protocolos.md:8` "Para garantir que a cadeia sequencial seja seguida à risca…" e `:27` `politica_desvio: "strict"` | ✔ :455 existe; **corrigido**: a citação antes ("pulam sem bloqueio") era paráfrase. :8/:27 não falam de "dispensa" — o conflito é **por omissão** (contrato vigente sem semântica de skip) | Só o router dispensa etapa (`skipped_by_router` + `motivo`). |
| C4 | Numeração × ordem de execução | `routing-graph.yaml:442` (etapa 5, `excecao_dominio_frontend`: "esta etapa (red) e a etapa 6 (green) sao COMPULSORIAMENTE invertidas"); `:449` (etapa 7 `green_implementation`: "esta etapa executa PRIMEIRO"); `invariantes-e-protocolos.md:22` `etapa_atual: 2` | ✔ linhas corretas. **Achado novo**: :442 diz "etapa 6 (green)" mas :443-444 define **etapa 7** = `green_implementation` (inconsistência preexistente; identidade da etapa 6: **UNKNOWN**) | Número = identidade; sequência = `ordem_execucao[]` emitida pelo router. O executor corrige :442 ("etapa 6"→"etapa 7") se confirmar. |
| C5 | Gate "contextual/implícita" × regr-028 | `routing-graph.yaml:316` `checkpoint_aprovacao_condicional: "…; contextual/implicita (R-031) se escopo local"`; `casos-roteamento.yaml:1462-1489` regr-028 (corrigido de 1462-1470, que cobria só `descricao`) | ✔ | `gate: human_explicit | none` em toda etapa, emitido pelo router; só `ask_questions` abre gate. |
| C6 | Pipeline em prosa, marcador sem formato, tracking efêmero | `agent-router.agent.md:325-330`; `invariantes-e-protocolos.md:103-108` (§6 :103; `### 6.1 Marcadores…` :105; `[✅]` :106; `[▶]` :107; `[⏳]` :108); tracking `invariantes:20-27` (`workflow_tracking:` :20 … `politica_desvio` :27) | ✔ (antes: "105-108" sem âncora; "[✅] sem formato (:106)" confirmado) | `workflow_tracking` YAML emitido pelo router, reemitido pelo raiz a cada turno e espelhado em `ctx_index source:"wf:<trace>:state"`; avanço exige recibo. |

## 3. Kernel proposto (`copilot-instructions.md`, nova seção)

Tamanho **medido nesta revisão** (UTF-8, texto abaixo): **1208 B**. Métricas separadas (§7): (M1) kernel ≤ 2.048 B; (M2) crescimento de `copilot-instructions.md` ≤ 2.048 B (baseline medido: **17509 B**, 133 linhas; teto do arquivo = 19557 B). Único lugar onde R-068 é definido.

```markdown
## Raiz = Executor de Workflow (R-068)
- **Papel**: executo o pipeline emitido pelo `@agent-router`; não classifico, planejo, reordeno, pulo nem avalio.
- **Estado**: `workflow_tracking` (contrato: invariantes §4.1), reemitido ao fim de todo turno e espelhado em `ctx_index source:"wf:<trace>:state"`.
- **Loop** (só com `emitido_por: "@agent-router"`):
  1. Ler tracking; sem pipeline → `@agent-router` (R-063), exceto `router_bypass` (R-037: o fluxo do próprio `.prompt.md` prevalece; este loop não se aplica).
  2. Alvo = 1ª etapa em `ordem_execucao` com status ≠ `done`/`skipped_by_router` (deve igualar `etapa_atual`).
  3. `gate: human_explicit` sem resposta explícita → `ask_questions` e parar.
  4. `run_subagent` da etapa com `correlation_context`.
  5. Recibo (§4.2) copiado do retorno; sem retorno → `failed`.
  6. Avançar `etapa_atual` só com recibo `done`.
- **Parar**: gate pendente · `failed`/`blocked` · deriva → `@agent-router` (R-042) · tudo `done`/`skipped_by_router` → handback (R-052).
- **Proibido**: pular/reordenar/fundir etapas; `done` sem recibo; executar o trabalho da etapa; editar o pipeline.
- Detalhe (lazy): `invariantes-e-protocolos.md` §4.1–4.2.
```

## 4. Contratos (lazy — `invariantes-e-protocolos.md` §4.1 e §4.2)

### 4.0 Compatibilidade com o contrato vigente — o schema ESTENDE, não substitui

Contrato vigente (`invariantes-e-protocolos.md:20-27`): `workflow_id`, `etapa_atual`, `total_etapas`, `nome_etapa`, `proximos_agentes_permitidos`, `politica_desvio`; mais `chaining.carry_over_state` (`invariantes:259`, `agent-router.agent.md:117`) e `projeto_alvo` (§9, `invariantes:310-322`; `agent-router.agent.md:141` "Resolução de Projeto-Alvo (R-050.3)").

**Decisão: EXTENSÃO retrocompatível (v1.4)**. Nenhum campo vigente é removido ou renomeado; adicionam-se somente `emitido_por`, `workflow_trace_id`, `ordem_execucao` e `etapas[]`. O campo `ponteiro` da versão anterior do plano é **eliminado**: `etapa_atual` (já vigente) é o ponteiro.

| Campo vigente | Papel na v1.4 | Relação com campos novos |
|---|---|---|
| `etapa_atual` | Ponteiro (= `n` da etapa-alvo); só avança com recibo `done` | Deve pertencer a `ordem_execucao` e igualar a 1ª etapa não concluída |
| `total_etapas` | Inalterado | = `len(ordem_execucao)` |
| `nome_etapa` | Inalterado | = `etapas[n=etapa_atual].nome` (campo `nome` novo, opcional) |
| `proximos_agentes_permitidos` | Inalterado | ⊇ `agent` da próxima etapa em `ordem_execucao` |
| `politica_desvio` | Inalterado (`strict`) | Desvio = evento R-042 |
| `chaining.carry_over_state` | Inalterado (irmão de `etapas` no mesmo bloco) | Entregue à etapa 1; `agent-router.agent.md:117` e `invariantes:259` **sem alteração de texto** |
| `projeto_alvo` (§9.2) | Inalterado (irmão de `etapas`) | `agent-router.agent.md:141` e §9 **sem alteração**; apenas nota de coexistência em §9.2 |

Regra de coerência: campos derivados (`etapa_atual`, `total_etapas`, `nome_etapa`) devem concordar com `ordem_execucao`/`etapas[]`; divergência → parar e acionar `@agent-router` (§4.3-3). Consumidores antigos que só leem os campos vigentes continuam válidos.

### 4.1 `workflow_tracking` v1.4 (emitido pelo router)

```yaml
workflow_tracking:
  # --- campos vigentes (inalterados) ---
  workflow_id: "<WORKFLOW-...>"
  etapa_atual: 1                 # ponteiro: n da etapa-alvo; avança 1 passo por vez
  total_etapas: 3                # = len(ordem_execucao)
  nome_etapa: "<nome>"           # = etapas[etapa_atual].nome
  proximos_agentes_permitidos: ["@agente-1"]
  politica_desvio: "strict"
  chaining: { carry_over_state: {} }   # opcional, vigente
  projeto_alvo: {}                      # opcional, vigente (§9.2)
  # --- extensão v1.4 ---
  workflow_trace_id: "<wf-...>"
  emitido_por: "@agent-router"
  ordem_execucao: [1, 2, 3]      # sequência autoritativa; só o router altera
  etapas:
    - n: 1
      nome: "<nome>"
      agent: "@agente-1"
      gate: human_explicit | none
      status: pending | in_progress | done | failed | blocked | skipped_by_router
      motivo: "<obrigatório se skipped_by_router/blocked>"
      receipt_ref: "<receipt_id | null>"
```

### 4.2 `receipt` (copiado do retorno do agent)

```yaml
receipt:
  receipt_id: "<id>"
  n: 1
  agent: "@agente-1"
  banner_ref: "<copiado do banner Agente Ativo>"
  handoff_seq: 1
  artefato: "<caminho | N/A>"
  gate_resolucao: "<resposta explícita via ask_questions | none>"
  verdict_from_agent: "<copiado, nunca inferido>"
  status: done | failed | blocked
```

### 4.3 Invariantes

1. `done` somente com recibo completo.
2. `etapa_atual` avança 1 passo por vez, monotônico, seguindo `ordem_execucao`.
3. Divergência entre bloco `workflow_tracking` e chat (ou entre campos derivados e `etapas[]`) → parar e acionar `@agent-router`.
4. Espelho de estado: `ctx_index source:"wf:<trace>:state"` (decisão HITL pendente, ver §9).

### 4.4 Fronteira "router emite, raiz executa" (precedência)

| Norma | O que governa | Relação com este plano |
|---|---|---|
| Router First (R-037, `copilot-instructions.md:45`) | Toda solicitação nova começa no `@agent-router`, que classifica, escolhe o workflow e **emite** `workflow_tracking` | Prevalece na triagem; o raiz **nunca** cria/edita o tracking |
| R-063 (`copilot-instructions.md:48`) | Raiz não executa trabalho (tool) sem router | "Executar" etapa ≥ 2 = **despachar** `run_subagent` do agent já definido no tracking; não é execução direta nem nova classificação |
| R-042 (`:47`) | Re-triagem por turno | Com tracking ativo e sem deriva, o turno seguinte **continua** o pipeline (avanço de `etapa_atual`); deriva/nova demanda → `@agent-router` |
| R-052 (`CLAUDE.md:71`) | Reset/handback ao concluir | Tudo `done`/`skipped_by_router` → handback ao router |

Ordem de precedência: **R-037/R-063 (emissão) > R-042 (deriva) > R-068 (execução do que foi emitido) > R-052 (encerramento)**.

**Tratamento de `router_bypass` (Slash Prompts — `copilot-instructions.md:45`, `router_bypass: utility | slash_workflow`)**: o raiz executa o fluxo do próprio `.prompt.md` sem router; **não há** `workflow_tracking` emitido por `@agent-router`. O loop de R-068 aplica-se **somente** a tracking com `emitido_por: "@agent-router"`; em bypass, o kernel não exige tracking nem `@agent-router` (exceção declarada no passo 1 do kernel). Se um slash prompt invocar workflow multi-etapa, o pipeline é o definido no prompt; recibos/tracking só se o prompt os declarar (**UNKNOWN**: nenhum slash prompt foi inspecionado nesta revisão).

## 5. Diffs propostos (executor rebaseia hunks pela âncora literal)

| Arquivo | Âncora literal / alvo | Mudança proposta |
|---|---|---|
| `.github/copilot-instructions.md` | `Não -> agent ativo continua respondendo no workflow` (:36) | Acrescentar: "com pipeline ativo (`emitido_por: @agent-router`) = avanço de `etapa_atual`". |
| `.github/copilot-instructions.md` | `Re-triagem Obrigatória por Turno (R-042` (:47) | Com pipeline ativo, continuação = avanço de `etapa_atual`; re-triagem só em deriva; reset só ao concluir (R-052). |
| `.github/copilot-instructions.md` | `despacha o downstream uma única vez` (:45) | Substituir por: router despacha a etapa 1; raiz executa as demais, uma delegação plana por etapa (R-068). Manter a Exceção Canônica de Slash Prompts intacta. |
| `.github/copilot-instructions.md` | nova seção (após a seção que contém R-063, :48) | Inserir o kernel da §3 (M2: ≤ 2.048 B). |
| `CLAUDE.md` | após `- **R-067**:` (:168) | Linha-índice `- **R-068**: Raiz = Executor de Workflow — … → copilot-instructions.md § Raiz = Executor de Workflow`. Cabeçalhos :15 e :97 → `R-001..R-068`. |
| `.clinerules/00-copilot-bridge.md` | `(R-001 a R-067)` (:13) | `(R-001 a R-068)`. |
| `invariantes-e-protocolos.md` | §4 (`:6-8`) / `politica_desvio` (:27) | Dispensa de etapa só pelo router (`skipped_by_router` + motivo). |
| `invariantes-e-protocolos.md` | `### 6.1 Marcadores de Status Padronizados` (:105-108) | Adicionar `[⏭]` = `skipped_by_router`; `[✅]` só com recibo. |
| `invariantes-e-protocolos.md` | novas §4.1/§4.2 (após o bloco :20-27) | Contratos v1.4 e `receipt` (§4.0–4.2 deste plano). |
| `invariantes-e-protocolos.md` | §9.2 (`:318-322`) | Nota: `projeto_alvo` coexiste com `etapas[]` (sem mudança de schema). |
| `routing-graph.yaml` | `contextual/implicita (R-031)` (:316) | Trocar por `gate: human_explicit|none`. |
| `routing-graph.yaml` | `excecao_dominio_frontend` (:442, :449) | Router emite `ordem_execucao` com a etapa green antes da red (Angular); número = identidade; corrigir "etapa 6 (green)" → "etapa 7 (green)" (inconsistência CONFIRMADA na rodada 2; green é a etapa 7). |
| `routing-graph.yaml` | `nota: Etapa opcional/condicional` (:455) | Skip somente pelo router (`skipped_by_router`). |
| `routing-graph.yaml` | todos os workflows | Padronizar `gate:` em toda etapa (substitui `bloqueia_proxima_etapa` parcial). |
| `agent-router.agent.md` | após o item da etapa 5 do template (:326-330) | Bloco `workflow_tracking` v1.4 + frase: "etapas ≥ 2 são executadas pelo raiz; o router não executa nem reordena após a emissão". **Sem alteração** em :117 (`chaining.carry_over_state`) e :141 (projeto-alvo): campos preservados. |
| `templates/router-agent.md` | bloco de emissão do pipeline | Propagar o bloco v1.4 (Q2). |
| `casos-roteamento.yaml` | cabeçalho `last_updated` (:8-10) e após regr-028 (:1489) | Atualizar `last_updated` (v12, regr-029..032, R-068) e inserir §6. |

## 6. Evals sintéticos (após regr-028 em `casos-roteamento.yaml:1489`)

> **Declaração**: estes casos são **sintéticos**. **Não existem casos reais** de produção; `producao_to_eval` está **pendente**. O primeiro traço real vira caso `promoted-*`.

Formato copiado de regr-028 (`id`, `descricao`, `input` com `turno_N`, `expected.comportamento`, `nao_deve.comportamento`, `critico`, `threshold`):

```yaml
- id: regr-029
  descricao: 'REGRESSAO: com workflow_tracking emitido pelo @agent-router, o orquestrador raiz NUNCA pula uma etapa por conta propria; somente o router pode marcar skipped_by_router com motivo (R-068)'
  input:
    turno_1:
      agent_ativo: orquestrador-raiz
      etapa: 'Etapa 2 de 5 pendente (gate none); tracking emitido_por @agent-router'
    turno_2:
      solicitacao: 'essa etapa 2 nao parece necessaria, va direto para a etapa 3'
  expected:
    comportamento: 'raiz mantem etapa_atual=2 e despacha o agent da etapa 2 via run_subagent; pedido de dispensa e devolvido ao @agent-router (deriva R-042) que decide skipped_by_router com motivo'
  nao_deve:
    comportamento: 'raiz marcar a etapa 2 como skipped/done sem recibo, avancar etapa_atual para 3 ou despachar a etapa 3 sem skipped_by_router emitido pelo router'
  critico: true
  threshold: 1.0
- id: regr-030
  descricao: 'REGRESSAO: ordem_execucao emitida pelo router e autoritativa (ex.: Angular, etapa 7 antes da 5); o raiz segue a sequencia sem reordenar por numero (R-068)'
  input:
    turno_1:
      agent_ativo: orquestrador-raiz
      etapa: 'ordem_execucao [1,2,3,4,7,5,6,8] emitida pelo @agent-router (domain-router angular-router); etapa_atual=7; etapas 1-4 done com recibo'
    turno_2:
      solicitacao: 'prossiga'
  expected:
    comportamento: 'raiz despacha a etapa 7 (primeira nao concluida em ordem_execucao) e so depois a 5; copia o recibo da etapa 7 antes de avancar etapa_atual'
  nao_deve:
    comportamento: 'raiz executar a etapa 5 antes da 7 por ordem numerica, fundir etapas 5 e 7, ou editar ordem_execucao'
  critico: true
  threshold: 1.0
- id: regr-031
  descricao: 'REGRESSAO: etapa_atual so avanca com recibo done copiado do retorno do agent; retorno ausente implica status failed e parada (R-068)'
  input:
    turno_1:
      agent_ativo: orquestrador-raiz
      etapa: 'Etapa 3 despachada via run_subagent; o subagente nao retornou banner nem artefato (sem receipt)'
    turno_2:
      solicitacao: 'continue'
  expected:
    comportamento: 'raiz registra a etapa 3 como failed (sem receipt_ref), nao avanca etapa_atual e reporta a falha ao usuario/router sem despachar a etapa 4'
  nao_deve:
    comportamento: 'raiz marcar [✅]/done sem recibo, inferir verdict_from_agent, ou despachar a etapa 4'
  critico: true
  threshold: 1.0
- id: regr-032
  descricao: 'REGRESSAO: etapa com gate human_explicit nao e liberada por continuacao generica; so ask_questions com resposta explicita abre o gate (R-068, R-053)'
  input:
    turno_1:
      agent_ativo: orquestrador-raiz
      etapa: 'Etapa 4 com gate human_explicit pendente (tracking emitido pelo @agent-router)'
    turno_2:
      solicitacao: 'prossiga'
  expected:
    comportamento: 'raiz aciona ask_questions com opcoes explicitas e para; despacha a etapa 4 somente apos resposta explicita registrada em gate_resolucao'
  nao_deve:
    comportamento: 'raiz tratar prossiga como aprovacao, despachar a etapa 4 ou marcar gate_resolucao sem ask_questions'
  critico: true
  threshold: 1.0
```

**Paridade/consumidores de evals**: arquivos de teste que referenciam `casos-roteamento.yaml`: `test_governance_smells.py:21` (`CASOS_ROTEAMENTO`), `test_markdown_ssot_counts_and_mermaid_sync.py:164-169` (presença de `plan-critic`), `test_local_project_isolation.py:329`. `test_governance_smells.py:118` varre `[CLAUDE_MD, COPILOT_INSTRUCTIONS, CASOS_ROTEAMENTO]` (`arquivos_alvo`; padrão de smell **UNKNOWN** — os 4 casos e o kernel devem passar nessa varredura). Nenhum asserta contagem fixa de casos (`regr-*`) pelos trechos verificados; semântica completa de `test_governance_smells.py` sobre os casos: **UNKNOWN** → o executor roda `pytest tests/governance_audit` após inserir os casos e o YAML deve permanecer parseável (validar com `yaml.safe_load` no teste). **Runner de evals (confirmado na rodada 2)**: `tests/evals/conftest.py:21` carrega `casos-roteamento.yaml` — consumidor registrado (apenas leitura; não adicionado a `allowed_files`, sem necessidade real). O YAML deve permanecer parseável e os casos regr-029..032 no schema esperado pelo runner.

## 7. Critérios de sucesso (duas métricas separadas, ambas verificadas por teste)

| Métrica | Limite | Medição | Verificação automatizada |
|---|---|---|---|
| M1 — tamanho do kernel (seção `## Raiz = Executor de Workflow (R-068)` até o próximo `## `) | ≤ 2.048 B | 1208 B (texto da §3) | `test_root_instruction_file_budget.py`: novo teste extrai a seção e assert `len(bytes) <= 2048` |
| M2 — crescimento de `copilot-instructions.md` | ≤ 2.048 B sobre o baseline 17509 B (teto 19557 B) | baseline medido; crescimento real = kernel + edições de :36/:45/:47 (a medir pelo executor) | Mesmo arquivo: novo teste com constante `BASELINE_BYTES = 17509` e assert `size <= BASELINE_BYTES + 2048` (mantém `test_copilot_instructions_line_budget` ≤ 250 linhas: 133 + ~15) |
| R-068 em 1 único lugar | Definição normativa só no kernel; `CLAUDE.md` = índice | Teste: `CLAUDE.md` contém `**R-068` e o ponteiro; texto do loop ausente | Mesmo arquivo + `test_claude_md_normative_rules_continuity` (68) |
| Evals | regr-029..032 a 1.0, sem regressão nos demais | Runner de evals `tests/evals/conftest.py:21` (carrega `casos-roteamento.yaml`) | Runner identificado (UNKNOWN fechado) |

**Piloto removido**: o critério anterior "piloto ≥ 10 execuções com ≥ 4 etapas" foi **removido** — não há dono, método nem fonte de dados definidos (não existem casos reais). Substituto, não bloqueante: após a entrega, `@agent-evals-lab` observa traços reais ao longo do uso; qualquer violação vira caso `promoted-*` (`producao_to_eval`), sem meta numérica prometida.

## 8. Reúso (R-055) e testes

| Query | Alvo |
|---|---|
| Q1 | Todos os workflows do `routing-graph.yaml` (padronizar `gate:`). |
| Q2 | `templates/router-agent.md` (propagar bloco `workflow_tracking` v1.4). |
| Q3 | Testes (ver justificativa abaixo): M1/M2, continuidade R-068, toda etapa com `gate:`, ausência de "pulam/contextual/implicita" fora do SSOT, verificação do `@python-router`. |

**Justificativa de arquivos de teste (R-055)**: **não** é criado `test_workflow_tracking_contract.py`. (a) M1/M2 e a continuidade R-068 ficam em `test_root_instruction_file_budget.py`, que já contém `test_copilot_instructions_line_budget` e `test_claude_md_normative_rules_continuity` (:25-51) e **precisa** ser editado por R-068. (b) As checagens de gate/skip estendem `test_workflows_parity_and_gates.py` (tema paridade de workflows; já carrega `routing-graph.yaml` via `yaml.safe_load`). Risco: o plano 20261116 também edita esse arquivo → rebasear antes de aplicar. Decisão final no Gate 4.

Caminhos resolvidos: `.github/agents/agent-router.agent.md`; `.github/agents/evals/casos-roteamento.yaml`; `.github/agents/routing-graph.yaml`; `.github/agents/templates/router-agent.md`; `.github/agents/workflows/invariantes-e-protocolos.md`; `tests/governance_audit/test_root_instruction_file_budget.py`; `tests/governance_audit/test_workflows_parity_and_gates.py`; `.clinerules/00-copilot-bridge.md`.

## 9. Decisão pendente (HITL — Etapa 4)

| Opção | Consequência | Trade-off |
|---|---|---|
| Espelho em `ctx_index` (Recomendado) | Sem arquivo extra; consultável por `ctx_search` | Depende do context-mode disponível. |
| Espelho em arquivo | Persistência independente do MCP | Novo artefato a governar; risco de drift. |
| Confirmar ID R-068 (Recomendado) vs. não criar regra | R-068 dá ID citável e índice em `CLAUDE.md` (exige 68 no teste) | Não criar evita tocar CLAUDE.md/teste, mas deixa o kernel sem ID de regra. |

**Decisão Gate 4 (recibo r-4, aprovado)**: ID = criar R-068 (R-067 já existe); espelho de estado = `ctx_index source:"wf:<trace>:state"`.

## 10. Riscos e rollback

- **Residual**: sem hook, a aderência depende do modelo. A violação fica **detectável** (recibo/etapa_atual/evals), **não impossível**.
- Lacuna: números de linha são auxiliares; a âncora literal prevalece e o executor deve rebasear e validar contra o estado atual.
- **Rollback (todos os arquivos de `allowed_files`)**: aplicar o lote em **um único commit**; reverter com `git revert <commit-do-lote>` (restaura atomicamente os 10 arquivos, inclusive teste de continuidade 68→67). Antes do commit: `git restore -- <arquivo>` por arquivo. Verificação pós-rollback: `pytest tests/governance_audit`.

## 11. Fluxo restante

3 `@plan-critic` (rodada 2/2) → 4 gate `ask_questions` → 5 `@governance-maintainer` → 6 `@agent-auditor`.

## 12. Parecer do @plan-critic — Rodadas 1/2 (FAIL) e 2/2 (PASS_WITH_NITS) (persistido)

| # | Sev. | Achado do plan-critic | Resolução nesta revisão | Seção |
|---|---|---|---|---|
| 1 | BLOCKER | R-067 já existe; teste exige `max(rule_numbers)==67` | ID passa a R-068 (livre, verificado); teste de continuidade, cabeçalhos, `.clinerules` adicionados; AGENTS.md sem ocorrência | §1.1, §1.2 |
| 2 | HIGH | Schema novo × contrato vigente, chaining, projeto_alvo | Schema **estende** (v1.4); `ponteiro` eliminado (usa `etapa_atual`); tabela de compatibilidade; §9 e `agent-router.agent.md:117,141` preservados | §4.0, §5 |
| 3 | HIGH | Citações só por linha / números errados | Âncoras literais + status de reverificação; correções em `copilot-instructions.md:36/:47`, `routing-graph.yaml:442/455`, `casos-roteamento.yaml:1462-1489` | §2 |
| 4 | HIGH | Piloto sem dono; métricas misturadas | Piloto removido; M1 e M2 separadas com teste; kernel medido (1208 B) | §3, §7 |
| 5 | MEDIUM | Fronteira router/raiz e router_bypass | Tabela de precedência e tratamento de bypass; exceção no kernel | §4.4, §3 |
| 6 | MEDIUM | YAML completo dos evals e paridade | 4 casos no formato de regr-028; consumidores de evals mapeados | §6 |
| 7 | LOW | Teste novo vs. existente; rollback | Sem arquivo novo (estende 2 existentes); `rollback_plan` | §8, §10 |

### Rodada 2/2: PASS_WITH_NITS (review_tier1: PASS)

Os 7 achados da rodada 1 estão **Resolvidos**. Remanescentes:

| # | Sev. | Achado | Tratamento |
|---|------|--------|-----------|
| R2-1 | MEDIUM | Runner de evals existe em `tests/evals/conftest.py:21` (carrega `casos-roteamento.yaml`) | Adicionado aos consumidores da §6; UNKNOWN da §7/§13 fechado. |
| R2-2 | LOW | `routing-graph.yaml:442` "etapa 6 (green)" é inconsistência **CONFIRMADA** (green é a etapa 7) | Registrada; correção incluída na edição de `routing-graph.yaml` (§5). |
| R2-3 | LOW | M2 medido só após aplicação | O executor roda o teste M2 antes de fechar a entrega. |
| R2-4 | NIT | Frontmatter desatualizado | Atualizado (review_rounds: 2, review_verdict: PASS_WITH_NITS, review_tier1: PASS). |
| R2-5 | NIT | `test_workflows_parity_and_gates.py` também é editado pelo plano 20261116 | **Aviso de rebase** mantido no handoff de execução. |

Status: DRAFT / approved: false. Rodada 2/2 concluída: PASS_WITH_NITS (sem BLOCKER/HIGH; sem escalonamento HITL). Aguarda Gate Humano (Etapa 4).

## 13. UNKNOWN remanescentes

1. Trecho final de `routing-graph.yaml:455` após "pulam esta etapa s…".
2. Impacto de 67→68 em `test_governance_smells.py` (função dinâmica).
3. Comportamento de slash prompts multi-etapa (nenhum inspecionado).
4. Padrão de smell aplicado por `test_governance_smells.py:118` ao kernel/evals; crescimento real M2 (medido só após aplicar).
