---
name: <slug-kebab-case>
description: "<Descrição concisa em 3ª pessoa do comando slash, ≤ 200 caracteres, com propósito e gatilho de uso.>"
agent: "<agent-alvo-ou-agent-router>"
# Opcional — router_bypass: utility | slash_workflow (todos os Slash Prompts exceto /agent-router declaram router_bypass para execução direta sem passar por @agent-router)
# router_bypass: utility | slash_workflow
model: "Gemini 3.8 Flash"
tools: ['grep_search', 'file_search', 'list_dir', 'get_errors', 'run_subagent', 'context-mode/ctx_execute', 'context-mode/ctx_batch', 'context-mode/ctx_index', 'context-mode/ctx_search']
argument-hint: "[caminho-ou-escopo] [--opcoes]"
# R-066 (Progressive Disclosure): docs <= 300 linhas em source_docs:; docs > 300 linhas em source_docs_lazy:
source_docs:
  - .github/skills/<skill-relacionada>/SKILL.md
  - .github/skills/context-mode/SKILL.md
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

- ✅ O uso de `context-mode` (`ctx_batch`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).

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
- **Clarificação e UX do `ask_questions` (R-027 / CA-03..CA-05)**: Em ambiguidades ou checkpoints HITL, usar `ask_questions` com 1–4 perguntas/chamada, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais sem espantalhos (Anti-Strawman), `description` obrigatório (`[Consequência prática / O que faz] + [Trade-off principal ou quando escolher]`) e 1ª opção `(Recomendado)` quando houver melhor prática técnica (exceção: decisão puramente de negócio) — SSOT: `structured-intake-patterns`.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch(commands, queries)` OU script iterativo consolidado em `ctx_execute`. No `ctx_execute`, use obrigatoriamente `language: "javascript"` (`fs`/`path` nativos do Node.js) para I/O, inspeção e mutação de arquivos (proibido `language: "python"` ou `python -c` para I/O, evitando bloqueio do `python.exe` pelo Windows Defender/AMSI); em `ctx_batch`, use apenas comandos shell leves com escopo restrito (proibido `python -c` inline ou varreduras recursivas irrestritas). Em caso de timeout (`ETIMEDOUT`/`timed out`/`taskkill`), aplica-se **Circuit Breaker Fail-Fast**: tolerância zero para repetir a mesma chamada/runtime — máximo de **1 retry** exigindo troca obrigatória de estratégia (migrar para `language: "javascript"` puro com `fs` ou reduzir o lote); no 2º timeout, aborte novos spawns e reporte em formato Compact Error Reporting (R-020).
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).

</execution_protocol>
<!-- END:STANDARD -->
