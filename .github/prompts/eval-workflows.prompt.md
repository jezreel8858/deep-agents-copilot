---
name: 'eval-workflows'
description: 'Avalia a conformidade de trajetórias dos workflows canônicos (R-050) com Gemini 3.8 Flash'
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'get_errors', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_search']
argument-hint: '[cenario-id | todos]'
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
source_docs:
  - .github/skills/agent-evals-lab/SKILL.md
  - .github/skills/handoff-governance/SKILL.md
  - .github/skills/harness-eval/SKILL.md
---

# `eval-workflows`

> **Propósito**: Executar avaliação controlada de trajetórias e transições de multi-agentes baseada em micro-cenários isolados (1 cenário por turno), prevenindo decaimento de atenção e alucinação.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Este prompt utiliza as variáveis de contexto nativas do VS Code Copilot:
- Arquivo sob análise: `${file}`
- Workspace root: `${workspaceFolder}`
- Argumento opcional: `${input:param}` para especificar o ID do cenário (ex.: `WF-BUG-001`, `WF-REF-001`, `WF-EDGE-INTENT-DRIFT`).

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ NÃO executar avaliação monolítica misturando múltiplos workflows em uma única chamada aberta.
- ❌ NÃO implementar código da aplicação ou modificar arquivos de produção durante o eval.
- ❌ NÃO aprovar trajetórias que violem as regras de menor privilégio de tooling ou omitam o banner obrigatório.
- ✅ Ler a especificação declarativa em `tests/operational_flow/casos-workflows.yaml`.
- ✅ Avaliar um cenário por vez com foco em:
  1. Identificação correta da etapa inicial e do agente roteado;
  2. Preservação do banner universal `Agente Ativo: <name>` e do `Pipeline de Execução`;
  3. Conformidade das transições de handoff (schema v1.3);
  4. Acionamento do Circuit Breaker em caso de falha de regressão repetida.

---

## 📋 Fluxo de Execução Passo a Passo

### Passo 1 — Coleta de Contexto e Linha de Base
- Carregar o catálogo de cenários em `tests/operational_flow/casos-workflows.yaml`.
- Identificar o cenário selecionado pelo parâmetro ou selecionar o primeiro pendente.

### Passo 2 — Processamento e Transformação
- Mapear a sequência de etapas esperada: `etapa`, `agente`, `invariantes` e `proximos_permitidos`.
- Comparar o comportamento observado na sessão contra os critérios declarados do cenário.

### Passo 3 — Validação e Checagem Imediata
- Validar se os agentes da cadeia mantiveram o isolamento de ferramentas (read-only sem mutação).
- Validar se houve detecção de deriva de intenção caso a solicitação tenha migrado de contexto.

### Passo 4 — Saída Estruturada
- Emitir o relatório de avaliação no formato canônico da governança.

---

## ✅ Checklist Antes de Apresentar

- [ ] Cenário identificado por ID único em `casos-workflows.yaml`.
- [ ] Todas as etapas da trajetória foram auditadas individualmente.
- [ ] Nenhuma ferramenta mutativa executada durante a avaliação.
- [ ] Veredito final (`APROVADO` ou `REPROVADO`) com justificativa fundamentada.

---

## 📊 Formato de Saída

### 🧪 Relatório de Avaliação de Trajetória: <cenario_id> — <cenario_nome>

- **Workflow Canônico**: <WORKFLOW-ID>
- **Tipo de Cenário**: <fast_path | standard | intent_drift | circuit_breaker | fast_chaining>
- **Projeto Alvo**: <projeto_alvo>

#### Trajetória Observada vs. Esperada
| Etapa | Agente Esperado | Banner Válido? | Invariantes Respeitadas? | Transição Permitida? |
|---|---|:---:|:---:|:---:|
| 1 | <agente_1> | ✅/❌ | ✅/❌ | ✅/❌ |
| 2 | <agente_2> | ✅/❌ | ✅/❌ | ✅/❌ |

#### Diagnóstico e Veredito
- **Score de Aderência**: <0.0 a 1.0>
- **Resultado**: <APROVADO | REPROVADO>
- **Desvios / Gaps Observados**: <descrição em ≤ 2 linhas, ou 'Nenhum desvio detectado'>
- **Próximo Passo Mínimo**: <ação sugerida>

---

## 🚨 Regras de Autonomia

- Em caso de inconsistência no grafo de roteamento, pare e aponte a aresta divergente.
- Nunca gere mocks de resposta falsos; avalie estritamente com base nos artefatos reais.

---

## 🔄 Combina Com (Encadeamento)

- `/validate` -> executa validação da suíte pytest completa após a avaliação do cenário.
- `/plan` -> aciona novo planejamento caso desvios de governança sejam detectados.

<execution_protocol>
**Protocolo Plan-Then-Batch (Smell 2.26 / Smell 2.13 / R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
3. **DESPACHAR & VALIDAR**: Aplique todas as mutações ou leituras em processo único no sandbox (all-or-nothing verificado, R-051) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
4. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
5. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
6. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).
8. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".
</execution_protocol>
