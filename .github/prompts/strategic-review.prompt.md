---
name: strategic-review
description: >-
  Executa revisão estratégica sob demanda do próprio framework de governança
  (deep-agents-copilot) via prompt chaining aprovado item a item (R-033):
  pesquisa de mercado (@deep-search) → diagnóstico read-only de smells
  (@agent-auditor) → plano de simplificação sem execução (@refactor-planner) →
  handoff condicional pós-aprovação humana (@governance-factory /
  @governance-maintainer). NÃO cria agent novo, NÃO fixa model premium
  permanente (R-021) e NÃO executa nenhuma mutação sem aprovação explícita.
agent: 'agent'
router_bypass: slash_workflow
model: "Claude Sonnet 5.5"
tools: ['read_file', 'grep_search', 'file_search', 'list_dir', 'ask_questions', 'run_subagent', 'context-mode/ctx_search', 'context-mode/ctx_batch_execute']
argument-hint: '[tema-de-pesquisa-opcional]'
source_docs:
  - '.github/agents/deep-search.agent.md'
  - '.github/agents/agent-auditor.agent.md'
  - '.github/agents/refactor-planner.agent.md'
  - '.github/agents/governance-maintainer.agent.md'
  - '.github/skills/governance-audit-patterns/SKILL.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
source_docs_lazy:
  - '.github/agents/governance-factory.agent.md'
---

# `/strategic-review`

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/strategic-review` (argumento: `[tema-de-pesquisa-opcional]`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` na triagem inicial — este Slash Prompt possui `router_bypass: slash_workflow` (exceção canônica a R-037/R-063) e seu fluxo já está definido abaixo; o Orquestrador Raiz DEVE executar diretamente as instruções deste `.prompt.md` (ou despachar diretamente para o subagente previsto neste próprio prompt).
- ✅ O uso de `context-mode` (`ctx_batch_execute`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ Revisão estratégica **sob demanda** (não contínua/background) da qualidade,
  simplicidade e evolução do próprio framework de governança
  (`.github/agents`, `.github/skills`, `.github/prompts`).
- ✅ Encadeamento fixo de 4 etapas (**prompt chaining** — Anthropic "Building
  Effective Agents"), cada etapa validada com o usuário antes de avançar
  (R-033 — sem execução blackbox).
- ❌ **NÃO cria nenhum agent novo.** A necessidade de um "arquiteto do
  projeto" persistente foi avaliada e rejeitada por `@agent-auditor` +
  `@deep-search` — é redundante com `deep-search` + `agent-auditor` +
  `refactor-planner` + `governance-factory`/`governance-maintainer`.
  Não reabrir essa discussão.
- ❌ **NÃO fixa `model:` permanente em tier premium (Opus) em nenhum
  catálogo (R-021).** Este prompt roda em tier padrão (Sonnet); qualquer
  necessidade pontual de raciocínio profundo usa o sinal de escalonamento
  🧠 por chamada individual de `run_subagent`, nunca alteração de
  frontmatter/catálogo.
- ❌ **NÃO implementa, corrige ou refatora nada diretamente.** As etapas 1-3
  são estritamente read-only/advisory. Só a etapa 4, e somente após
  aprovação humana explícita via `ask_questions`, delega execução.
- ❌ **NÃO pula etapas nem paraleliza a cadeia.** Cada etapa consome a saída
  da anterior como insumo (dependência sequencial real) — não é um
  orchestrator-workers dinâmico.

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/strategic-review`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## 📐 Justificativa de Design

- **Prompt chaining é o padrão correto para subtarefas fixas e conhecidas em
  tempo de design** (Anthropic "Building Effective Agents"; Vercel "Six Agent
  Orchestration Patterns") — não orchestrator-workers dinâmico, nem criação
  de agent novo, para uma sequência sob demanda de 4 passos já mapeados.
- **Sistemas multi-agent podem consumir até 15x mais tokens** que uma única
  chamada — a arquitetura evita "premature fan-out": cada etapa só dispara
  a próxima delegação após a anterior concluir e (quando aplicável) ser
  aprovada, nunca em paralelo especulativo.
- **Role specialization com capacidade limitada evita agent sprawl** —
  este prompt compõe agents especializados **já existentes** no catálogo
  em vez de criar um novo papel persistente, mantendo o princípio de menor
  privilégio e o catálogo enxuto (R-003).

## 🎯 Uso

```
/strategic-review
/strategic-review multi-agent orchestration patterns 2026
/strategic-review context window management e prompt caching
```

Se `{{tema_pesquisa}}` (argumento livre) não for informado, a etapa 1 usa
como tema padrão: "padrões atuais de governança e arquitetura de agentic
systems, multi-agent frameworks e simplificação de workflows canônicos".

## 📋 Fluxo (prompt chaining sequencial — R-033)

### PASSO 1 — Pesquisa de mercado (`@deep-search`)

Delegar via `run_subagent`:

- **task**: pesquisar na web (Tavily, quando disponível) sobre padrões atuais
  (2025/2026) de governança de agentic systems, multi-agent frameworks,
  prompt chaining vs orchestrator-workers, e o tema informado em
  `{{tema_pesquisa}}` (se houver).
- **Saída esperada**: síntese com citação de fontes, destacando riscos de
  agent sprawl, custo de token em fan-out prematuro, e convenções
  consolidadas de mercado.
- Apresentar a síntese ao usuário antes de prosseguir para o Passo 2.

### PASSO 2 — Diagnóstico read-only (`@agent-auditor`)

Delegar via `run_subagent` **somente após o usuário confirmar prosseguir**:

- **task**: diagnosticar smells/gaps no catálogo atual
  (`.github/agents`, `.github/skills`, `.github/prompts`) aplicando
  `governance-audit-patterns/SKILL.md`, usando **as evidências de mercado
  da etapa 1 como insumo adicional de comparação** (não apenas os smells
  internos padrão).
- **Saída esperada**: lista de smells/gaps priorizados com severidade e
  referência `arquivo:linha`. Nenhuma mutação é executada nesta etapa.

### PASSO 3 — Plano de simplificação (`@refactor-planner`)

Delegar via `run_subagent` **somente após o usuário confirmar prosseguir**:

- **task**: propor plano de simplificação/redução de complexidade (R-050)
  dos workflows canônicos ou de qualquer artefato apontado como smell na
  etapa 2, com fases isoladas, dependências explícitas e estratégia de
  rollback por fase. **Sem implementar.**
- **Saída esperada**: plano faseado, revisável, sem execução.

### PASSO 4 — Gate de aprovação e handoff condicional

- Apresentar o plano completo da etapa 3 ao usuário via `ask_questions`
  perguntando explicitamente: aprovar integralmente, aprovar parcialmente
  (selecionar fases) ou rejeitar.
- **Só em caso de aprovação explícita**, delegar via `run_subagent`:
  - `@governance-factory` — para fases que envolvam criação/revisão de
    artefato de governança (agent, skill, prompt, stack).
  - `@governance-maintainer` — para fases que envolvam execução em lote
    de mudanças já aprovadas via context-mode.
- Se rejeitado ou parcialmente aprovado, registrar o escopo final e encerrar
  sem disparar nenhuma etapa de execução não aprovada.
- **Nunca automático.** Esta etapa nunca dispara sem o gate humano explícito.

## 🚨 Regras de Autonomia

- Nota **R-021**: proibido qualquer etapa deste fluxo fixar `model:`
  permanente em tier premium (Opus) em frontmatter/catálogo. Escalonamento
  é sempre o sinal pontual 🧠 por chamada de `run_subagent`.
- Nota **R-033**: cada etapa é apresentada e validada com o usuário antes de
  avançar para a próxima — proibida execução em cadeia sem checkpoint.
- Nota **R-055**: se o plano da etapa 3 apontar melhoria que se repete em
  múltiplos artefatos análogos, o `@refactor-planner` deve avaliar e
  declarar propagação sistêmica (Q1/Q2/Q3), não correção isolada.
- Este prompt não substitui `/plan`, `/implement` ou `/validate` — a
  etapa 4, quando aprovada, delega para os agents de execução, que seguem
  seus próprios fluxos e gates.

## 🔄 Combina Com

- `/deep-search` → pesquisa avulsa sem o encadeamento completo.
- `/plan` + `/implement` + `/validate` → ciclo de execução após aprovação
  do plano gerado na etapa 3.
- `@governance-factory` → criação/revisão pontual de um único artefato
  (sem necessidade do fluxo estratégico completo).

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/strategic-review` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/strategic-review`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

> **Contrato de UX `ask_questions` (R-027 / CA-03..CA-05)**: 1–4 perguntas/chamada, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais e mutuamente exclusivas (Anti-Strawman), `description` obrigatório (`[Consequência prática / O que faz] + [Trade-off principal ou quando escolher]`) e 1ª opção `(Recomendado)` quando houver melhor prática técnica (exceção: decisão puramente de negócio/produto).

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`. No `ctx_execute`, use obrigatoriamente `language: "javascript"` (`fs`/`path` nativos do Node.js) para I/O, inspeção e mutação de arquivos (proibido `language: "python"` ou `python -c` para I/O, evitando bloqueio do `python.exe` pelo Windows Defender/AMSI); em `ctx_batch_execute`, use apenas comandos shell leves com escopo restrito (proibido `python -c` inline ou varreduras recursivas irrestritas). Em caso de timeout (`ETIMEDOUT`/`timed out`/`taskkill`), aplica-se **Circuit Breaker Fail-Fast**: tolerância zero para repetir a mesma chamada/runtime — máximo de **1 retry** exigindo troca obrigatória de estratégia (migrar para `language: "javascript"` puro com `fs` ou reduzir o lote); no 2º timeout, aborte novos spawns e reporte em formato Compact Error Reporting (R-020).
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions (R-027: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais sem espantalhos, `description` obrigatório com `[Consequência prática + Trade-off/quando escolher]` e 1ª opção `(Recomendado)` para melhor prática técnica), vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).
7. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".

</execution_protocol>
