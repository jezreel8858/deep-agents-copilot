---
name: '<verbo>-<objeto>'
description: >-
    <Ação imperativa em 1 linha — ex.: Analisa e refatora o arquivo ativo aplicando padrões de Clean Architecture>
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'get_errors', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_search']
# Se run_in_terminal for declarado em tools, é OBRIGATÓRIO incluir .github/skills/terminal-governance/SKILL.md em source_docs (R-049).
# O uso de context-mode (ctx_execute, ctx_batch_execute, ctx_search) é 100% OBRIGATÓRIO para leituras e escritas quando disponível, aplicando compulsoriamente Single-Turn MCP Batching (R-008, R-046, R-056, Smell 2.24, Smell 2.26).
argument-hint: '[caminho-do-arquivo | contexto-opcional]'
# SSOT de Dependências de Prompt (VS Code Copilot Prompt Files Spec):
# 100% das dependências documentais e skills do prompt DEVEM residir exclusivamente em source_docs:/source_docs_lazy: no frontmatter.
# É TERMINANTEMENTE PROIBIDO criar seções de pré-carregamento documental no corpo markdown
# (ex.: seções de catálogo, herança ou pré-carregamento documental no corpo).
# PREVENÇÃO DE SMELL 2.12 (SSOT Invertido): Prompts NUNCA devem se autodeclarar "SSOT Normativa".
# A fonte única da verdade técnica reside compulsoriamente na SKILL.md referenciada em source_docs.
# R-066 (Progressive Disclosure Compulsória): CLAUDE.md e .github/copilot-instructions.md são documentos de alto
# fan-in (>300 linhas) — NUNCA em source_docs: (full-load); sempre em source_docs_lazy:, consultados
# exclusivamente via context-mode/ctx_search sob demanda (nunca read_file integral).
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/<verbo>-<objeto>`

> **Propósito**: Descreva o que este prompt executa em 1-2 frases diretas e imperativas.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Este prompt utiliza as variáveis de contexto nativas do VS Code Copilot:

```bash
# Execução direta com base no arquivo ativo no editor:
/<verbo>-<objeto>

# Execução passando argumento explícito ou filtro:
/<verbo>-<objeto> <argumento>
```

### Variáveis Disponíveis no Template
- `${file}`: Caminho absoluto do arquivo aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto atualmente selecionado pelo usuário.
- `${workspaceFolder}`: Diretório raiz do workspace ativo.
- `${input:nomeDoParametro}`: Parâmetro dinâmico solicitado ao usuário no momento da invocação.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** processar o arquivo alvo `${file}` ou a seleção `${selection}`.
- ✅ **SEMPRE** verificar erros via `get_errors` antes e após alterações.
- ❌ **NÃO** inferir requisitos ou refatorar além da intenção declarada ("Never infer intent").
- ❌ **NÃO** executar operações destrutivas ou irreversíveis sem confirmação prévia explícita.
- ❌ **NÃO** modificar arquivos fora do escopo sem instrução direta.

---

## 📋 Fluxo de Execução Passo a Passo

### Passo 1 — Coleta de Contexto e Linha de Base
- Avalie se o usuário forneceu `${selection}` ou se o alvo é o arquivo completo `${file}`.
- Se necessário um parâmetro complementar em runtime, interaja via `${input:nomeDoParametro}`.
- Leia o arquivo alvo usando `read_file` e colete o estado atual de integridade via `get_errors`.

### Passo 2 — Processamento e Transformação
- Aplique a transformação técnica planejada respeitando convenções e menor privilégio.
- Preserve estilo existente, tipagem estrita e regras de linting do projeto.

### Passo 3 — Validação e Checagem Imediata
- Execute novamente `get_errors` sobre o arquivo alterado.
- Caso novos erros ou avisos apareçam, corrija-os antes de apresentar a conclusão.

### Passo 4 — Saída Estruturada
- Apresente um resumo enxuto e rastreável do resultado obtido.

---

## ✅ Checklist Antes de Apresentar

- [ ] Arquivo alvo (`${file}` ou argumento) verificado antes da intervenção.
- [ ] Transformação aplicada de forma atômica e pontual.
- [ ] `get_errors` rodado com 0 novos erros introduzidos.
- [ ] Limites de Não-Escopo respeitados.
- [ ] Nenhuma alteração não autorizada fora do arquivo alvo.

---

## 📊 Formato de Saída

```markdown
### Execução de `/<verbo>-<objeto>`

- **Arquivo Processado**: `${file}`
- **Status de Integridade**: ✅ Sem erros (`get_errors` validado)

### Alterações Realizadas
- <Item 1 das alterações executadas>
- <Item 2 das alterações executadas>

### Próximo Passo Sugerido
- <Próxima ação recomendada, ex.: rodar testes ou comando encadeado>
```

---

## 🚨 Regras de Autonomia

- ❌ **NUNCA** executar comandos de exclusão, git push, migrações de banco ou reescrita massiva sem confirmação humana.
- ❌ **NÃO** encapsular a resposta inteira em bloco global de código markdown nem aninhar cercas de mesma quantidade de backticks quando gerar múltiplos artefatos copiáveis.
- ✅ **SEMPRE** expor evidências com referências de linhas e arquivos tocados.

---

## 🔄 Combina Com (Encadeamento)

```text
/<prompt-anterior> → /<verbo>-<objeto> → /<prompt-seguinte>
```

- `/<prompt-anterior>`: Gera o insumo ou contexto preliminar.
- `/<prompt-seguinte>`: Consome o artefato produzido (ex.: `/review` ou `/commit`).

---

<!-- Bloco sincronizado por tools/agent_protocol_sync/sync_execution_protocol.py (fonte
     única: _execution-protocol-fragment.md). NÃO editar manualmente — editar o fragmento
     e rodar --apply para propagar a todos os *.prompt.md reais. -->
## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).
8. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".

</execution_protocol>

