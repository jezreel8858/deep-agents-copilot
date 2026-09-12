# Plano de Implementação — Propostas P1–P10 (Orquestração LangChain/LangGraph)

> **Baseado em**: [`proposta-orquestracao-langchain.md`](./proposta-orquestracao-langchain.md)
> **Data de início**: 2026-08-28
> **Data de conclusão**: 2026-08-29
> **Status geral**: ✅ **Concluído — todas as fases + próximos passos mínimos**

---

## 1) Visão Geral

Implementar as 10 propostas da proposta de orquestração em 4 fases, evoluindo as skills de governança existentes e criando dois novos artefatos estruturais (`routing-graph.yaml` e `casos-roteamento.yaml`), seguindo as regras R-026 (sem código inline > 8 linhas), R-038 (genericidade obrigatória) e R-031 (plano auto-implementável).

---

## 2) Estado Atual vs. Desejado

| Artefato | Estado Antes | Estado Após |
|---|---|---|
| `handoff-governance/SKILL.md` | Schema informal, sem guardrails gap | Schema formal tipado + guardrails gap + fan-out/fan-in + identidade do emissor |
| `agent-contracts/SKILL.md` | Contrato de I/O básico (seções 1–5) | + seção 6 (limites de delegação) + seção 7 (context engineering) |
| `context-mode/SKILL.md` | Memory como camada única `ctx_*` | + seção 10 com 6 dimensões short/long-term explícitas |
| `confidence-fallback-policy/SKILL.md` | Score 0–1 com thresholds qualitativos | + seção 6: routing em cascata (rule→semantic→LLM) + logging |
| `agent-router.agent.md` | Sem version, formato sem score numérico | `version: "1.1.0"` + `Confidence Score` + `Nível de Routing` no output |
| `docs/ai-context/routing-graph.yaml` | Não existia | Grafo YAML declarado com nós, arestas e política de cascata |
| `docs/ai-context/evals/casos-roteamento.yaml` | Não existia | Suíte completa: canônicos (10), ambíguos (4), regressão (5), segurança (4) |

---

## 3) O Que NÃO Faz Parte deste Plano

- Instalar qualquer dependência de runtime (LangChain, LangGraph, DeepEval) — R-038
- Criar nova skill `agent-memory-policy` (Fase 4 avançada — roadmap futuro)
- Modificar `CLAUDE.md` com nova regra normativa (escopo separado, requer aprovação explícita)
- Criar arquivos auxiliares além dos 2 novos previstos — R-009
- Alterar qualquer adapter em `.github/instructions/` — fora do escopo de governança de agents

---

## 4) Dependências entre Fases

| Fase | Itens | Depende de | Pode rodar em paralelo com |
|---|---|---|---|
| **Fase 1** | P3, P7, P8 | — | Fase 1 é completamente paralela internamente (3 arquivos distintos) |
| **Fase 2a** | P1, P9 | — | Paralela à Fase 1 |
| **Fase 2b** | P2 | P1 (routing-graph deve existir antes) | — |
| **Fase 3** | P4, P5 | Fase 1 P8 (agent-contracts já modificado) | P4 e P5 são paralelas entre si |
| **Fase 4** | P6, P10 | Fase 1 P3 (handoff já modificado) | P6 e P10 no mesmo arquivo (agrupadas) |

> **Nota de execução**: como cada arquivo é editado em uma única chamada, os itens que tocam o mesmo arquivo são agrupados automaticamente — `handoff-governance` recebe P3+P6+P10 em uma chamada; `agent-contracts` recebe P8+P5 em uma chamada.

---

## 5) Fases e Itens

### Fase 1 — Fundação (baixo risco, aditivo) `[P]`

> Mudanças aditivas em skills já existentes. Sem novo artefato estrutural.

#### - [x] P3 — Schema de estado de handoff versionado + cobertura de guardrails em handoffs

- **Arquivo**: `.github/skills/handoff-governance/SKILL.md`
- **O que fazer**:
  - Adicionar **seção 2.1** — Schema Formal com campos obrigatórios tipados (`versao`, `para`, `emissor`, `contexto`, `proximos_passos_sugeridos`, `nao_retornar_para`)
  - Adicionar **seção 2.2** — Gap de Guardrails em Handoffs (tabela de estratégias compensatórias + regra mínima)
- **Critério de sucesso**: seções 2.1 e 2.2 presentes; seções existentes 1–6 intactas
- **Status**: ✅ Implementado

#### - [x] P7 — Distinção explícita Memory short-term vs long-term + 6 dimensões

- **Arquivo**: `.github/skills/context-mode/SKILL.md`
- **O que fazer**:
  - Adicionar **seção 10** com tabela de 6 dimensões (Duração, Tipo, Escopo, Atualização, Retrieval, Permissão de escrita) e exemplos de `ctx_search` com/sem `source`
- **Critério de sucesso**: seção 10 presente; seções 1–9 intactas
- **Status**: ✅ Implementado

#### - [x] P8 — Limites de delegação e execução declarados nos contratos

- **Arquivo**: `.github/skills/agent-contracts/SKILL.md`
- **O que fazer**:
  - Adicionar **seção 6** com campos `max_delegation_depth`, `max_execution_time_min`, `allow_redelegation`, `circuit_breaker` e tabela de defaults
- **Critério de sucesso**: seção 6 presente com defaults documentados; seções 1–5 intactas
- **Status**: ✅ Implementado

---

### Fase 2 — Roteamento como Dado `[P→S]`

> Muda a fonte de verdade do roteamento sem alterar comportamento observável.

#### - [x] P1 — Formalizar o grafo de roteamento como dado (YAML) `[P]`

- **Arquivo**: `docs/ai-context/routing-graph.yaml` *(novo)*
- **O que fazer**:
  - Criar arquivo YAML com seções `nos` (todos os agents do catálogo), `arestas` (condições de roteamento com keywords, threshold_score, nivel_routing) e `politica_cascata` (rule-based/semantic/llm-based/escalonamento)
- **Critério de sucesso**: arquivo YAML válido com todos os 17 agents como nós; aresta de `binding-initializer` com `prioridade: 0`
- **Status**: ✅ Implementado

#### - [x] P9 — Versionamento semântico de comportamento de agent `[P]`

- **Arquivo**: `.github/agents/agent-router.agent.md`
- **O que fazer**:
  - Adicionar campo `version: "1.1.0"` no frontmatter
- **Critério de sucesso**: `version: "1.1.0"` presente no frontmatter
- **Status**: ✅ Implementado

#### - [x] P2 — Routing em cascata com confidence score explícito no output `[S após P1]`

- **Arquivos**: `.github/skills/confidence-fallback-policy/SKILL.md` + `.github/agents/agent-router.agent.md`
- **O que fazer**:
  - `confidence-fallback-policy`: adicionar **seção 6** com tabela de 4 níveis de cascata, ambiguity zone, logging YAML `routing_log` e regra de output obrigatório
  - `agent-router`: atualizar **Formato de Saída** com `Confidence Score: <0.00–1.00>` e `Nível de Routing`; atualizar Padrão Obrigatório #7
- **Critério de sucesso**: formato de saída do router contém as 2 novas linhas; seção 6 da skill existe com tabela de cascata
- **Status**: ✅ Implementado

---

### Fase 3 — Qualidade Contínua `[P]`

> Fecha o ciclo de regressão de roteamento e custo/latência.

#### - [x] P4 — Suíte de evals versionada como quality gate de CI `[P]`

- **Arquivo**: `docs/ai-context/evals/casos-roteamento.yaml` *(novo)*
- **O que fazer**:
  - Criar suíte YAML com 4 seções: `canonicos` (≥10 casos, threshold 0.90), `ambiguos` (≥4 casos, threshold 0.70), `regressao` (≥5 casos, threshold 1.00), `seguranca` (≥4 casos, threshold 1.00)
  - Incluir seção `execucao` com framework recomendado, integração CI e métricas por categoria de agent
- **Critério de sucesso**: arquivo YAML válido; 4 suítes presentes; 23+ casos totais
- **Status**: ✅ Implementado

#### - [x] P5 — Context Engineering por agent (Anthropic 2025) `[S após P8]`

- **Arquivo**: `.github/skills/agent-contracts/SKILL.md`
- **O que fazer**:
  - Adicionar **seção 7** com estrutura XML canônica de system prompt, política de prompt caching (ordem estático→variável) e tabela de context budget por tier (8K/32K/64K tokens)
- **Critério de sucesso**: seção 7 presente com tabela de context budget; seções 1–6 intactas
- **Status**: ✅ Implementado

---

### Fase 4 — Orquestração Avançada `[P]`

> Mudanças de maior esforço, agrupadas no mesmo arquivo da Fase 1.

#### - [x] P6 — Padrão "Orchestrator-Workers" para análise paralela (fan-out/fan-in) `[S após P3]`

- **Arquivo**: `.github/skills/handoff-governance/SKILL.md`
- **O que fazer**:
  - Adicionar **seção 5.1** com tabela "Quando usar fan-out vs. delegação única", custo LLM por padrão e schema YAML `fan_out` com campos `workers`, `fan_in`, `guardrail_saida`
- **Critério de sucesso**: seção 5.1 presente; tabela de custo (1 call vs 2 calls/domínio) presente
- **Status**: ✅ Implementado (agrupado com P3 na Fase 1)

#### - [x] P10 — Agent Identity nos contratos de handoff `[S após P3]`

- **Arquivo**: `.github/skills/handoff-governance/SKILL.md`
- **O que fazer**:
  - Incluir campos `emissor.nome`, `emissor.versao`, `emissor.modelo_llm`, `emissor.timestamp` no schema formal (seção 2.1)
  - Adicionar nota de correlação com spans OTel (`gen_ai.agent.name`, `gen_ai.request.model`)
- **Critério de sucesso**: schema na seção 2.1 contém bloco `emissor:` com 4 campos
- **Status**: ✅ Implementado (agrupado com P3 na Fase 1)

---

## 6) Checklist de Autonomia (gate pré-implementação — verificado)

- [x] Todos os paths de arquivo verificados (leitura dos 5 arquivos-fonte + `list_dir` de `docs/ai-context/`)
- [x] Zero itens TBD — conteúdo de cada seção nova totalmente especificado
- [x] Critério de sucesso de cada fase verificável (seção 7 — Testes)
- [x] Fases independentes marcadas `[P]`
- [x] Dependências entre fases documentadas na tabela da seção 4
- [x] R-026 respeitado — blocos YAML são schemas/exemplos descritivos (padrão estabelecido nas skills existentes)
- [x] R-038 respeitado — sem referências a LangChain como dependência técnica
- [x] Nenhuma pergunta ao usuário durante a execução

---

## 7) Decisões Tomadas

| Decisão | Alternativa Descartada | Razão |
|---|---|---|
| Agrupar P3+P6+P10 em uma só chamada de `handoff-governance` | Aplicar em PRs separados | R-031 exige execução integral sem interrupção; R-009 proíbe arquivos auxiliares intermediários |
| Agrupar P5+P8 em uma só chamada de `agent-contracts` | Editar em fases | Mesmo arquivo; edição única é obrigatória (Padrões Obrigatórios) |
| Criar `routing-graph.yaml` em `docs/ai-context/` | Criar em `docs/plan/` ou `.github/` | `docs/ai-context/` é o diretório de contexto de binding — alinhado com R-034 |
| Criar `casos-roteamento.yaml` em `docs/ai-context/evals/` | Criar em `tests/evals/` | O repositório não tem diretório `tests/`; `docs/ai-context/` é a localização padrão para artefatos de contexto de IA |
| NÃO criar `agent-memory-policy` skill | Criar nesta iteração | Roadmap futuro — dimensão procedimental exige validação de caso de uso real antes de criar skill |
| NÃO modificar `CLAUDE.md` (R-018 para agents) | Atualizar inline | Requer aprovação explícita de nova regra normativa; documentado como `Próximo passo mínimo` |

---

## 8) Etapas de Validação (Como Testar)

### T1 — `handoff-governance/SKILL.md` (P3 + P6 + P10)

- [ ] Seção **2.1** existe com campos: `versao`, `para`, `emissor` (com `nome`, `versao`, `modelo_llm`, `timestamp`), `contexto`, `proximos_passos_sugeridos`, `nao_retornar_para`
- [ ] Seção **2.2** existe com tabela de estratégias compensatórias e "Regra mínima"
- [ ] Seção **5.1** existe com tabela de custo (1 call vs 2 calls/domínio) e schema YAML `fan_out`
- [ ] Seções 1, 3, 4, 5, 6 originais intactas

### T2 — `agent-contracts/SKILL.md` (P8 + P5)

- [ ] Seção **6** existe com campos `max_delegation_depth`, `max_execution_time_min`, `allow_redelegation`, `circuit_breaker` e tabela de defaults
- [ ] Seção **7** existe com XML canônico (`<instructions>`, `<context>`, `<examples>`, `<input>`), tabela de ordem de prompt caching e tabela de context budget (8K/32K/64K)
- [ ] Seções 1–5 originais intactas

### T3 — `context-mode/SKILL.md` (P7)

- [ ] Seção **10** existe com tabela de 6 dimensões
- [ ] Exemplos de `ctx_search` com e sem `source` presentes
- [ ] Nota sobre "memória procedimental" como skill futura presente
- [ ] Seções 1–9 originais intactas

### T4 — `confidence-fallback-policy/SKILL.md` (P2)

- [ ] Seção **6** existe com tabela de 4 níveis (rule-based → semantic → llm-based → escalonamento)
- [ ] "Ambiguity Zone" (top-2 dentro de 0.05) documentada
- [ ] Schema YAML `routing_log` com `top_3_candidatos` e `score_numerico` presente
- [ ] Regra de output (`Confidence Score: X.XX`) documentada

### T5 — `agent-router.agent.md` (P2 + P9)

- [ ] Frontmatter contém `version: "1.1.0"`
- [ ] Formato de Saída contém `Confidence Score: <0.00–1.00>` e `Nível de Routing: <...>`
- [ ] Padrão Obrigatório #7 menciona "score numérico"

### T6 — `routing-graph.yaml` (P1)

- [ ] Arquivo YAML válido (sem erros de lint)
- [ ] Seção `nos` contém todos os 17 agents do catálogo
- [ ] Aresta para `binding-initializer` com `prioridade: 0` (antes de qualquer triagem)
- [ ] Seção `politica_cascata` com 4 níveis e `ambiguity_zone`
- [ ] **Consistência**: todo `para:` em arestas referencia um `id:` existente nos nós

### T7 — `casos-roteamento.yaml` (P4)

- [ ] Arquivo YAML válido
- [ ] Seção `canonicos`: ≥ 10 casos com `threshold: 0.90` e `critico: true`
- [ ] Seção `ambiguos`: ≥ 4 casos com `comportamento: ask_questions`
- [ ] Seção `regressao`: ≥ 5 casos com `threshold: 1.00` — todos com `nao_deve` documentado
- [ ] Seção `seguranca`: ≥ 4 casos cobrindo injection, commit, instalação e system prompt
- [ ] Seção `execucao` com referência ao DeepEval e gatilho de CI

### T8 — Integração entre artefatos

- [ ] `routing-graph.yaml` ↔ `agent-router.agent.md`: a Decision Tree do router menciona o arquivo como fonte
- [ ] `confidence-fallback-policy/SKILL.md` seção 6 instrui score numérico → Formato de Saída do `agent-router` tem o campo correspondente
- [ ] `handoff-governance/SKILL.md` seção 2.1 menciona correlação OTel → `agent-observability-otel/SKILL.md` é complementar
- [ ] `casos-roteamento.yaml` pode ser referenciado em `agent-evals-lab/SKILL.md` como "arquivo real de casos" (próxima entrega)

---

## 9) Próximos Passos Mínimos (pós-implementação)

1. - [x] **Referenciar `casos-roteamento.yaml` em `agent-evals-lab/SKILL.md`** — seção 9 adicionada, vinculando design ao arquivo real de casos. *(Concluído 2026-08-28)*
2. - [x] **Referenciar `routing-graph.yaml` em `agent-router.agent.md`** — adicionado na seção "Catálogo / Conhecimento Base" como fonte de verdade estrutural. *(Concluído 2026-08-28)*
3. - [x] **Atualizar `docs/ai-context/catalog.yaml`** — versão 1.2, seção `governance_artefacts` com os 2 novos artefatos e campos `consumed_by` + `maintenance_rule`. *(Concluído 2026-08-29)*
4. - [x] **Atualizar `.github/agents/catalog.yaml`** — `source_docs` do `agent-router` com `routing-graph.yaml` + `evals/casos-roteamento.yaml`; `source_docs` do `impact-architect` restaurado corretamente. *(Concluído 2026-08-29)*
5. - [x] **Adicionar R-040 em `CLAUDE.md`** — regra "Grafo de Roteamento como Fonte de Verdade" com 3 obrigações (grafo + Decision Tree + caso de teste). *(Concluído 2026-08-29)*
6. - [x] **Referenciar R-040 em `copilot-instructions.md`** — adicionado na seção de Regras de Autonomia. *(Concluído 2026-08-29)*
7. - [x] **Criar skill `agent-memory-policy`** — Tier 3 (Experimental), categoria `governance`. Cobre memória episódica, semântica e procedimental com guardrails, ciclo controlado de atualização e aprovação humana obrigatória (R-027). *(Concluído 2026-08-29)*

> ✅ **Plano 100% concluído** — todos os 10 itens (P1–P10) implementados e todos os próximos passos mínimos executados.

---

## 10) Referências

- [`proposta-orquestracao-langchain.md`](./proposta-orquestracao-langchain.md) — proposta de origem com análise comparativa e racional por item
- [`/plan`](../../.github/prompts/plan.prompt.md) — prompt de planejamento usado como guia de processo
- `CLAUDE.md` — regras R-026, R-031, R-038 aplicadas nesta execução

