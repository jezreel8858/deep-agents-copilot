---
name: validate
description: Valida implementação contra plano aprovado, verifica critérios de sucesso e identifica desvios.
agent: 'agent'
router_bypass: slash_workflow
model: "Gemini 4 Argon"
tools: ['read_file', 'grep_search', 'file_search', 'run_in_terminal', 'get_errors', 'run_subagent', 'context-mode/ctx_search', 'context-mode/ctx_batch']
argument-hint: '[caminho-do-plano | escopo-de-validação]'
source_docs:
  - '.github/skills/terminal-governance/SKILL.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/validate`

> **Propósito**: Validar a implementação contra o plano técnico aprovado, checando critérios de aceite e desvios.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/validate` (argumento: `[caminho-do-plano | escopo-de-validação]`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` na triagem inicial — este Slash Prompt possui `router_bypass: slash_workflow` (exceção canônica a R-037/R-063) e seu fluxo já está definido abaixo; o Orquestrador Raiz DEVE executar diretamente as instruções deste `.prompt.md` (ou despachar diretamente para o subagente previsto neste próprio prompt).
- ✅ O uso de `context-mode` (`ctx_batch`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** comparar o código real contra os critérios de sucesso do plano aprovado.
- ✅ **SEMPRE** rodar suíte de testes relevante e checar `get_errors` com relatório de conformidade.
- ❌ **NÃO** modificar arquivos de aplicação durante a validação (perfil estritamente analítico e de auditoria).
- ❌ **NÃO** aprovar validação com falhas de compilação ou testes quebrados pendentes.

---

Você foi encarregado de validar que um plano foi implementado corretamente, verificando critérios e identificando desvios.

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/validate`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## Setup

Ao invocar:

1. **Determine contexto** — sessão existente ou nova?
   - Existente: revise o que foi implementado nesta sessão
   - Nova: descubra via análise do codebase

2. **Localize o plano**:
   - Se path fornecido, use-o
   - Senão, pergunte ao usuário

3. **Colete evidência** via `ctx_search(sort: "timeline")` e `ctx_batch(commands, queries)`

## Processo

### Passo 1: Descoberta de Contexto

Se sessão nova:

1. Leia o plano **integralmente**
2. Identifique o que deveria ter mudado:
   - Todos os arquivos que deveriam ser modificados
   - Critérios (automatizados + manuais)
   - Funcionalidade-chave a verificar

3. **Levante evidências em paralelo** via `ctx_batch`:
   - Verificar mudanças de código vs. plano
   - Verificar cobertura de verificações
   - Verificar artefatos criados/alterados

### Passo 2: Validação Sistemática

Para cada fase:

1. **Status de conclusão**:
   - Cheque checkmarks no plano (`- [x]`)
   - Verifique que código real bate com conclusão alegada
   - Verifique que houve checkpoint da fase via `/ctx-checkpoint`

2. **Verificação automatizada**:
   - Execute cada verificação prevista no plano
   - Documente pass/fail com evidências
   - Investigue falhas

3. **Critérios manuais**:
   - Liste o que precisa de verificação humana
   - Forneça passos claros

4. **Edge cases**:
   - Erros tratados?
   - Validações faltando?
   - Implementação pode quebrar funcionalidade existente?

### Passo 3: Relatório de Validação

```markdown
## Relatório de Validação: <Plano>

### Status de Implementação
✓ Fase 1: <Nome> — Totalmente implementado
✓ Fase 2: <Nome> — Totalmente implementado
⚠️ Fase 3: <Nome> — Parcialmente implementado (ver issues)

### Resultados das Verificações Automatizadas
✓ <verificação 1>: passou
✗ <verificação 2>: falhou — <motivo>

### Achados de Code Review

#### Bate com Plano:
- <item>

#### Desvios do Plano:
- <arquivo:linha> — <descrição do desvio>

#### Issues Potenciais:
- <issue> (apenas reportar, sem julgar)

### Verificação Manual Necessária
1. **Funcionalidade**:
   - [ ] <passo manual 1>
   - [ ] <passo manual 2>

### Recomendações
- N/A — apenas reporte achados objetivos
```

## Diretrizes

1. **Exaustivo mas prático** — foque no que importa
2. **Execute todas as verificações** — não pule
3. **Documente tudo** — sucessos e issues
4. **Pense criticamente** — a implementação resolve o problema?
5. **Token budget** — perguntas em lote no `queries`, `source` quando aplicável, sem saída bruta desnecessária
6. **Leitura integral de código é exceção** — priorize evidência indexada e leitura pontual

## Checklist de Validação

- [ ] Todas as fases marcadas completas estão realmente feitas
- [ ] Cada fase concluída possui registro de checkpoint (`/ctx-checkpoint`)
- [ ] Há checkpoint final de fechamento do plano
- [ ] Critérios verificáveis foram testados
- [ ] Código segue padrões existentes do projeto
- [ ] Sem regressões óbvias
- [ ] Tratamento de erro coberto
- [ ] Passos manuais estão claros e executáveis

## Combina Com

- `/implement` → precede este command
- `/plan` → se validação revela necessidade de ajustar plano

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/validate` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/validate`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch(commands, queries)` OU script iterativo consolidado em `ctx_execute`. No `ctx_execute`, use obrigatoriamente `language: "javascript"` (`fs`/`path` nativos do Node.js) para I/O, inspeção e mutação de arquivos (proibido `language: "python"` ou `python -c` para I/O, evitando bloqueio do `python.exe` pelo Windows Defender/AMSI); em `ctx_batch`, use apenas comandos shell leves com escopo restrito (proibido `python -c` inline ou varreduras recursivas irrestritas). Em caso de timeout (`ETIMEDOUT`/`timed out`/`taskkill`), aplica-se **Circuit Breaker Fail-Fast**: tolerância zero para repetir a mesma chamada/runtime — máximo de **1 retry** exigindo troca obrigatória de estratégia (migrar para `language: "javascript"` puro com `fs` ou reduzir o lote); no 2º timeout, aborte novos spawns e reporte em formato Compact Error Reporting (R-020).
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions (R-027: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais sem espantalhos, `description` obrigatório com `[Consequência prática + Trade-off/quando escolher]` e 1ª opção `(Recomendado)` para melhor prática técnica), vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).

</execution_protocol>
