---
status: "APPROVED"
approved: true
review_verdict: PASS_WITH_NITS
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: PASS
gate1_status: approved
gate2_status: approved
author: "@governance-factory"
plan_type: "governance"
created_at: "2026-11-15"
related-planning-doc: "docs/guides/synth-routing-eval-copilot-sdk-guide.md"
session_id: "sess-20261115-183000-synth-waves-prompt"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-20261115-183000-synth-waves-prompt"
parent_plan_ref: "N/A — plano raiz"
allowed_files:
  - "tests/governance_audit/test_template_sections.py"
  - "docs/plans/governance/20261115-183000-synth-waves-prompt.md"
  - ".github/prompts/synth-waves.prompt.md"
  - ".github/prompts/catalog.yaml"
  - ".github/prompts/README.md"
  - ".github/prompts/QUICK-START.md"
  - "tests/governance_audit/test_utility_slash_prompts_bypass.py"
---

# Plano de Governança — Slash Prompt /synth-waves (Ciclo Prata em 3 Ondas, Zero-Touch)

> Rodada 2 (pós-crítica @plan-critic, Rodada 1 NEEDS_REVISION): todos os achados BLOCKER/HIGH/MEDIUM/LOW/NIT incorporados.

## 1. Contexto e Motivação
O guia `docs/guides/synth-routing-eval-copilot-sdk-guide.md` (§ 5.3) descreve o ciclo iterativo de calibração do roteamento em 3 Ondas (`synth-generate` → `synth-eval` → `synth-diagnose` → `synth-export` → `synth-promote`) via CLI `governance-runner`, hoje executado manualmente com dezenas de flags. Este plano cria o Slash Prompt `/synth-waves` (`router_bypass: slash_workflow`) que coleta todos os parâmetros em um Intake Único (1 carrossel `ask_questions`, R-027) e executa as 3 ondas sem novas interações (Zero-Touch), incluindo Auto-Curadoria e Promoção Sem Pausa quando autorizada no Intake.

Evidências levantadas (inspeção read-only):
- Nenhum prompt da família `synth-*` existe em `.github/prompts/` (21 `.prompt.md`).
- `.github/prompts/catalog.yaml` NÃO existe; o usuário pediu explicitamente o registro nele, portanto será criado como arquivo NOVO (ver § 7).
- `tests/governance_audit/test_utility_slash_prompts_bypass.py` fixa `ALLOWED_SLASH_WORKFLOW_PROMPTS` (== 13); o teste (c) falha para `.prompt.md` fora das categorias permitidas → atualização obrigatória (Q3).
- CLI: `governance-runner --use-case synth-{generate,eval,diagnose,export,promote}`; `synth-eval` e `synth-generate --generator-mode sdk` exigem `--max-premium-requests` e `COPILOT_SDK_TOKEN`; `synth-promote` exige `--silver`, `--run-id` e `--confirm`.
- Caminho real do golden: `tools/headless-governance-runner/src/governance_runner/synth/golden.py` (contém `CONTAGENS_ESPERADAS_POR_SUITE`). **Não existe** `tests/evals/golden.py`; `tests/evals/` existe como diretório de testes. O alvo de runtime deve ser confirmado na execução do prompt (pré-checagem), sem presumir caminho.
- Suíte de testes do runner: `tools/headless-governance-runner/tests/synth_unit` (`tests/synth_unit` na raiz não existe); `tests/evals` existe na raiz.
- `docs/QUICK-START.md` não existe; o índice de comandos de prompts é `.github/prompts/QUICK-START.md`.
- Allowlist de modelos: `Gemini 4 Argon` é `ga`/`pinnable: true`. Modelos `--model` do CLI (claude-haiku-5.5, claude-sonnet-5.5) são parâmetros do runner SDK, não frontmatter.
- Pesquisa prévia (@deep-search) será delegada pelo @governance-factory na Etapa 3, antes de materializar o prompt; achados incorporados em `source_docs` e guardrails.

## 2. Escopo (Entrega de Governança — Etapa 3)
1. Criar `.github/prompts/synth-waves.prompt.md` (NOVO, `router_bypass: slash_workflow`).
2. Criar `.github/prompts/catalog.yaml` (NOVO) catalogando todos os Slash Prompts de `.github/prompts/`, incluindo `synth-waves`.
3. Atualizar `.github/prompts/README.md` e `.github/prompts/QUICK-START.md` (+1 linha cada, R-015).
4. Atualizar `tests/governance_audit/test_utility_slash_prompts_bypass.py` (13 → 14 prompts slash_workflow).

## 3. Não-Escopo
- ❌ Alterar código do runner (`tools/headless-governance-runner/src/**`), `routing-graph.yaml`, `agent-router.agent.md`, `model-allowlist.yaml` NESTA entrega de governança.
- ❌ Criar agent/skill/workflow novo; ❌ `run_in_terminal` (R-049) ou `run_subagent`.
- ❌ Executar o ciclo `/synth-waves` nesta entrega: a execução é posterior, pelo usuário.
- ❌ Implementar código de aplicação.

## 4. Blast Radius
| Artefato | Impacto | Risco |
|---|---|---|
| `.github/prompts/synth-waves.prompt.md` | Novo arquivo (Etapa 3) | Baixo; consumo premium só mediante Intake |
| `.github/prompts/catalog.yaml` | Novo arquivo (Etapa 3) | Baixo/Médio: nova convenção de catálogo de prompts |
| `README.md` / `QUICK-START.md` de prompts | +1 linha cada | Baixo |
| `test_utility_slash_prompts_bypass.py` | +1 item na allowlist, asserts 13→14 | Baixo |
| Alvos de runtime de `/synth-waves` (fora desta entrega) | `casos-roteamento.yaml` e `golden.py` mutados somente se Q4 = opção 1 | Médio; mitigado por rollback (§ 9) e pytest |

## 5. Allowlist Exata de Arquivos
### 5.1 Arquivos desta entrega de governança (`allowed_files` do frontmatter)
| Arquivo | Ação | Etapa |
|---|---|---|
| `docs/plans/governance/20261115-183000-synth-waves-prompt.md` | Criar/Revisar (este plano) | 1 |
| `.github/prompts/synth-waves.prompt.md` | **NOVO** — criar | 3 |
| `.github/prompts/catalog.yaml` | **NOVO** — criar | 3 |
| `.github/prompts/README.md` | Modificar | 3 |
| `.github/prompts/QUICK-START.md` | Modificar | 3 |
| `tests/governance_audit/test_utility_slash_prompts_bypass.py` | Modificar | 3 |

### 5.2 Artefatos-alvo de runtime do prompt (NÃO editados nesta entrega; fora de `allowed_files`)
Mutados apenas quando o usuário executar `/synth-waves` com a opção 1 da Pergunta 4 (autorização humana concedida no Intake):
| Arquivo | Ação em runtime |
|---|---|
| `.github/agents/evals/casos-roteamento.yaml` | Incorporar casos promovidos |
| `tools/headless-governance-runner/src/governance_runner/synth/golden.py` | Atualizar `CONTAGENS_ESPERADAS_POR_SUITE` (caminho confirmado na pré-checagem; se `tests/evals/golden.py` existir no futuro, usar o encontrado) |
| `.github/agents/evals/synthetic/**` e `.cache/routing_synth_history.db` | Artefatos gerados (descartáveis) |

Rollback de runtime: `git checkout -- .github/agents/evals/casos-roteamento.yaml tools/headless-governance-runner/src/governance_runner/synth/golden.py` (e `tests/evals/golden.py` caso exista).

## 6. Especificação do Prompt `.github/prompts/synth-waves.prompt.md`
### 6.1 Frontmatter
```yaml
name: 'synth-waves'
description: 'Executa o ciclo Prata de calibração do roteamento em 3 ondas (synth-generate/eval/diagnose/export/promote) via governance-runner, com Intake Único e execução Zero-Touch'
agent: 'agent'
router_bypass: slash_workflow
model: "Gemini 4 Argon"
tools: ['read_file', 'get_errors', 'ask_questions', 'context-mode/ctx_execute', 'context-mode/ctx_batch', 'context-mode/ctx_search']
argument-hint: '[smoke|bronze|prata|ouro]'
source_docs:
  - '.github/skills/structured-intake-patterns/SKILL.md'
  - '.github/skills/agent-evals-lab/SKILL.md'
  - '.github/skills/harness-eval/SKILL.md'
  - '.github/skills/context-mode/SKILL.md'
  - '.github/skills/efficient-batch-code-modification/SKILL.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
source_docs_lazy:
  - 'docs/guides/synth-routing-eval-copilot-sdk-guide.md'
```
Sem `run_in_terminal` (CLI via `ctx_execute` `language: "javascript"` com `child_process`); sem `run_subagent`. `model:` validado por `get_errors` e allowlist.

### 6.2 Estrutura do corpo
H1 com o comando → Propósito/Invocação → CRÍTICO (Escopo/Não-Escopo) → Intake Único → Execução Zero-Touch das 3 Ondas → Regras Críticas → Formato de Saída (CommonMark-safe) → Combina Com.

### 6.3 Bloco CRÍTICO (obrigatório)
- ❌ NÃO invocar `@agent-router` na triagem (`router_bypass: slash_workflow`).
- ✅ `context-mode` 100% obrigatório (R-056); ferramentas nativas só como fallback comprovado.
- ❌ NÃO editar agents/skills/prompts/routing-graph; escrita permitida apenas em `.cache/routing_synth_history.db`, `.github/agents/evals/synthetic/` e — somente com Q4 = opção 1 — nos alvos de § 5.2.
- ❌ NÃO encadear `ctx_execute` unitário (Smell 2.26): **1 chamada `ctx_execute` (`language: "javascript"`) por Onda, 1 tool call por turno**, sobre `--db-path .cache/routing_synth_history.db`.
- ❌ NÃO expor `COPILOT_SDK_TOKEN` em saída/logs; ausente → erro compacto e parada.
- ✅ Teto de tool turns ≤ 5 (R-060); Circuit Breaker: 1 retry com troca de estratégia; 2º timeout → relatório compacto (R-020).

### 6.4 Intake Único — 1 carrossel `ask_questions` (R-027)
Chamada única com 4 perguntas (`header` ≤ 25 chars, `allowFreeformInput: true`, `description` com [Consequência + Trade-off], 1ª opção `(Recomendado)`):
| # | header | Opções (literais) |
|---|---|---|
| 1 | `Perfil e Volume` | `Meta Prata — Equilibrado (Recomendado)` · `Smoke Test — Rápido / Baixo Custo` · `Meta Bronze — Triagem Rápida` · `Meta Ouro — Exaustivo (Certificação)` |
| 2 | `Escopo de Seeding` | `Cobertura Total: Arestas + Workflows (--graph-seeding all --workflow-seeds all) (Recomendado)` · `All na Onda 1 + Gaps nas Ondas 2 e 3` · `Apenas Workflows Canônicos (--workflow-seeds all)` · `Apenas Arestas (--graph-seeding all)` |
| 3 | `Modo e Modelo SDK` | `Híbrido: Onda 1 Template + Ondas 2/3 SDK com claude-sonnet-5.5 (Recomendado)` · `Full SDK nas 3 Ondas com claude-sonnet-5.5` · `Geração Econômica (claude-haiku-5.5) + Avaliação Sonnet (claude-sonnet-5.5)` · `100% Template na Geração + claude-sonnet-5.5 na Avaliação` |
| 4 | `Politica Auto-Promocao` | `Auto-Promover Completo: Silver -> promoted -> casos-roteamento.yaml + golden.py (Recomendado)` · `Auto-Promover até Staging (promoted-<run_id>.yaml)` · `Apenas Diagnóstico e Exportação Silver` |
Após o carrossel nenhuma nova pergunta é permitida (Zero-Touch); ambiguidade residual → defaults das opções Recomendadas, registrados no relatório. Teto `--max-premium-requests` derivado do Perfil (Bronze ≈205, Prata ≈656, Ouro ≈1.312, Smoke reduzido), dividido entre ondas.

### 6.5 Execução Zero-Touch das 3 Ondas
Cada Onda = **1 chamada `ctx_execute` (`language: "javascript"`)**, 1 tool call por turno, `--db-path .cache/routing_synth_history.db`. A pré-checagem (token presente, `governance-runner` disponível, `routing-graph.yaml` existente, caminho de `golden.py` resolvido, teto válido; e, quando Q4 = opção 1, working tree limpo nos alvos `casos-roteamento.yaml` e `golden.py` — `git status --porcelain` vazio para esses caminhos — ou backup prévio (cópia `.bak`) antes de qualquer mutação) fica embutida no início do script JS da Onda 1; falha → relatório compacto e parada.

| Onda | Pipeline (um script JS consolidado) | Gate |
|---|---|---|
| 1 — Baseline Estrutural | `synth-generate --dimensions parafrase,ruido_ortografico,comprimento_extremo,registro_informal` → `synth-eval` → `synth-diagnose --format both` | exit code 0; diagnóstico emitido |
| 2 — Hardening Semântico e Adversarial | `synth-generate --dimensions omissao_palavra_chave,distrator_outro_agente` → `synth-eval` → `synth-diagnose --format both` | exit code 0; Quality Gates § 5.4 do guia avaliados |
| 3 — Consolidação Cross-Dimensão + Exportação Silver + Auto-Promoção Zero-Touch | (1) `synth-generate --dimensions code_switching_pt_en,multi_intencao` → `synth-eval` → `synth-diagnose --format both`; (2) `synth-export` sobre os runs avaliados; (3) Auto-Curadoria e Promoção Sem Pausa conforme Pergunta 4 | exit code 0; política de Q4 aplicada |

Modo de geração por onda (template/SDK) e `--graph-seeding`/`--workflow-seeds` seguem as Perguntas 2 e 3 (opção 2 da Pergunta 2: `all` na Onda 1 e apenas gaps nas Ondas 2 e 3). Parâmetros do Perfil (`--min-support`) conforme Pergunta 1.

**Política da Pergunta 4 (Onda 3, passo 3):**
- **Opção 1 — Auto-Promover Completo (Recomendado):** a autorização humana prévia já foi concedida no Intake Único da Pergunta 4; portanto o agente, sem pausa: (a) cura programaticamente os arquivos `casos-roteamento-silver-*.yaml` (`review_status: approved`, `corrected_route` igual a `expected.agent_route`); (b) executa `synth-promote --confirm`; (c) incorpora os casos promovidos em `.github/agents/evals/casos-roteamento.yaml`; (d) atualiza `CONTAGENS_ESPERADAS_POR_SUITE` no `golden.py` (caminho resolvido na pré-checagem; atualmente `tools/headless-governance-runner/src/governance_runner/synth/golden.py`); (e) valida com `pytest` na suíte `synth_unit` (`tools/headless-governance-runner/tests/synth_unit`) e em `tests/evals`. Falha de pytest → rollback automático (§ 9) e relatório compacto.
- **Opção 2 — Staging:** curadoria + `synth-promote --confirm` até `promoted-<run_id>.yaml`; sem tocar `casos-roteamento.yaml`/`golden.py`.
- **Opção 3 — Somente Diagnóstico e Exportação Silver:** encerra após `synth-export`; sem curadoria nem promote.

O prompt não aplica remediações em `agent-router.agent.md`/`routing-graph.yaml`: apenas lista `SUG-*` e recomenda `/plan`.

### 6.6 Formato de Saída (CommonMark-safe)
Banner `Agente Ativo: synth-waves` seguido de linha em branco; lista `- ` com: Perfil, Seeding, Modo/Modelo, run_ids, reqs premium consumidas/teto, recall e IC de Wilson por onda, Quality Gates (PASS/FAIL), `SUG-*`, artefatos, status de promoção e resultado do pytest.

## 7. Especificação do Registro em `.github/prompts/catalog.yaml` (arquivo NOVO)
Criar catálogo dos Slash Prompts de `.github/prompts/` (todos os `.prompt.md`, incluindo `synth-waves`), schema `version` + `prompts[]`. Entrada do novo prompt:
```yaml
- name: synth-waves
  file: .github/prompts/synth-waves.prompt.md
  command: /synth-waves
  router_bypass: slash_workflow
  model: "Gemini 4 Argon"
  description: "Ciclo Prata de calibração do roteamento em 3 ondas (synth-*) com Intake Único, execução Zero-Touch e Auto-Promoção"
  skills: [structured-intake-patterns, agent-evals-lab, harness-eval, context-mode]
```
Os demais prompts são catalogados a partir de seus frontmatters (`name`, `router_bypass`, `model`, `description`), sem inventar campos.

## 8. Plano de Verificação
- [ ] Delegar @deep-search (diretrizes/skills) e incorporar achados.
- [x] `get_errors` agrupado em todos os arquivos alterados (`model:` sem `Unknown model`).
- [x] `pytest tests/governance_audit/test_utility_slash_prompts_bypass.py` (14 slash_workflow; teste (c) verde).
- [ ] `pytest tests/governance_audit/test_model_allowlist_governance.py`.
- [ ] Suítes de prompts/README em `tests/governance_audit/` (paridade README ↔ arquivos ↔ catalog.yaml).
- [ ] `tools/headless-governance-runner/tests/synth_unit` e `tests/evals` verdes (regressão).
- [ ] Dry-run manual: `governance-runner --use-case synth-generate --generator-mode template --dry-run` (0 reqs premium).

## 9. Rollback
- Entrega de governança: remover `synth-waves.prompt.md` e `catalog.yaml` (ambos novos); reverter `README.md`, `QUICK-START.md` e o teste (13 itens) via `git checkout -- <arquivo>`.
- Runtime do prompt (Q4 opção 1): ver rollback em § 5.2 (working tree limpo/backup validado na pré-checagem da Onda 1). Artefatos `synthetic/` e SQLite são descartáveis.

## 10. Portão de Reúso Sistêmico (R-055)
- **Q1**: slash_workflow e utility existentes não afetados; sem skill nova, logo sem retrofit de `source_docs` em agents.
- **Q2**: `.github/prompts/templates/prompt-template.md` já documenta `router_bypass`; sem alteração (padrão Intake Único + Zero-Touch é proposta futura).
- **Q3**: SIM — atualizar `test_utility_slash_prompts_bypass.py` (allowlist 14) e, opcionalmente, asserir que `synth-waves` declara `ask_questions` e não declara `run_in_terminal`/`run_subagent`; paridade com `catalog.yaml`.

## 11. Checklist de Execução (pós-aprovação R-064)
- [x] T1: @deep-search (diretrizes/skills) → @governance-factory cria `synth-waves.prompt.md`.
- [x] T2: Criar `.github/prompts/catalog.yaml`.
- [x] T3: Atualizar README/QUICK-START de prompts.
- [x] T4: Atualizar teste de bypass (13 → 14).
- [x] T5: `get_errors` + suítes do § 8; validar conformidade R-064 (allowed_files).

## Parecer do Revisor Cético Pré-HITL (R-064)
- Revisor: @plan-critic
- Rodada 1: NEEDS_REVISION (achados incorporados)
- Rodada 2: PASS_WITH_NITS — 0 BLOCKER, 0 HIGH
- Tier 1: PASS | Gate 1: approved
- Nits aplicados: (1) linha duplicada de rollback removida do § 9 (referência ao § 5.2); (2) pré-check da Onda 1 (§ 6.5) agora exige working tree limpo/backup antes de mutar `casos-roteamento.yaml` e `golden.py`.
- Estado: `status: DRAFT`, `approved: false` — aguardando checkpoint HITL (R-064).
