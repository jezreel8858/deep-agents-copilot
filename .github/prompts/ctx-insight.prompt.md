---
name: ctx-insight
description: Abre o dashboard de analytics do Context Mode com `ctx_insight` para observar uso de ferramentas e sessões.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools:
  - context-mode/ctx_insight
argument-hint: '[port]'
source_docs:
  - .github/skills/context-mode/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/ctx-insight`

Atalho para abrir o painel Insight e revisar métricas da sua rotina no Context Mode.

> **Propósito**: Inicializar o painel analítico local com métricas de consumo de ferramentas e sessões.
> **Workspace**: `${workspaceFolder}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** inicializar e disponibilizar a URL do painel analítico de sessões do Context Mode.
- ✅ **SEMPRE** informar a porta e a URL de acesso local.
- ❌ **NÃO** alterar configurações ou manipular dados da aplicação.
- ❌ **NÃO** iniciar múltiplos servidores em concorrência na mesma porta.

---

## Sintaxe

```
/ctx-insight
```

## Execução obrigatória

### Passo 0 — Diagnóstico rápido antes de abrir (opcional)
Se houver suspeita de problema de conexão, rode `/ctx-doctor` antes de abrir o dashboard.

### Passo 1 — Abrir Dashboard
Execute `ctx_insight` com parâmetros padrão.
2. Informe a URL/porta retornada e se o servidor iniciou corretamente.
3. Se necessário, ofereça nova execução com porta customizada.

## Exemplo de execução

```javascript
ctx_insight({ "port": 4747 })
```

## Resposta esperada

- Porta e URL do dashboard.
- Observação curta de primeiro uso (instalação inicial pode levar ~30s).
- Ação sugerida quando a porta estiver ocupada.

## Regras

- Não usar terminal para abrir o dashboard; use apenas `ctx_insight`.
- Não executar testes/build junto com `/ctx-insight`.
- Em erro, reportar no formato compacto (Causa / Local / Ação).

## Combina Com

- `/ctx-doctor` → diagnostique conectividade antes de abrir o dashboard
- `/ctx-status` → use para revisão rápida sem interface gráfica

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".

</execution_protocol>
