---
name: visualize-graph
description:
  Gera e abre a visualização interativa do grafo de conhecimento multi-repo em Angular Material 3
  (2D/3D), integrando AST de código, classificação de acoplamento, filtros arquiteturais
  (isolados/órfãos, papéis, camadas, multi-select de repositórios) e pontes de integração REST.
agent: 'agent'
router_bypass: slash_workflow
model: "Gemini 3.8 Flash"
tools: ['read_file', 'file_search', 'list_dir', 'run_in_terminal', 'run_subagent', 'context-mode/ctx_execute', 'context-mode/ctx_batch', 'context-mode/ctx_search']
argument-hint: '[--diff <ref> | --bridges <file>]'
source_docs:
  - '.github/instructions/README.md'
  - 'tools/codegraph-visualizer/README.md'
  - 'tools/codegraph-visualizer/bridges.json'
  - '.github/skills/terminal-governance/SKILL.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/visualize-graph`

> **Propósito**: Compilar e abrir a visualização interativa unificada do Grafo de Conhecimento Multi-Repo
> com interface Angular Material 3, alternância 2D/3D e análise de blast radius.
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/visualize-graph` (argumento: `[--diff <ref> | --bridges <file>]`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` na triagem inicial — este Slash Prompt possui `router_bypass: slash_workflow` (exceção canônica a R-037/R-063) e seu fluxo já está definido abaixo; o Orquestrador Raiz DEVE executar diretamente as instruções deste `.prompt.md` (ou despachar diretamente para o subagente previsto neste próprio prompt).
- ✅ O uso de `context-mode` (`ctx_batch`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** compilar e abrir a visualização interativa do grafo local.
- ✅ **SEMPRE** utilizar dados reais dos bancos SQLite `.codegraph/graph.db`.
- ❌ **NÃO** alterar a estrutura de arquivos da aplicação ou do repositório durante a visualização.
- ❌ **NÃO** executar rebuild de grafos desnecessariamente quando já indexados.

---

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/visualize-graph`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## 🎯 Uso

```bash
/visualize-graph                                      → Gera grafo unificado em tools/codegraph-visualizer/dist/index.html e abre no navegador
/visualize-graph --diff HEAD~1                        → Destaca nós modificados e calcula blast radius de PR
/visualize-graph --bridges custom-bridges.json        → Utiliza mapeamento de pontes customizado
```

---

## 📋 Fluxo de Execução

1. **Localizar Bancos de Dados SQLite do Grafo**:
   - Verificar a existência dos arquivos `.codegraph/graph.db` nos repositórios registrados no catálogo (`projects.local.yaml` / `catalog.yaml`).
   - Se algum projeto não possuir grafo construído, alertar e sugerir rodar `codegraph build` no repositório correspondente.

2. **Carregar Pontes REST Cross-Repo**:
   - Carregar o registro central de pontes em `tools/codegraph-visualizer/bridges.json`.

3. **Executar Generator Multi-Repo**:
   - Executar o script Python de build no local único centralizado:
   ```bash
   python tools/codegraph-visualizer/generator/generate-graph.py --output "tools/codegraph-visualizer/dist/index.html" --open
   ```

4. **Confirmar e Entregar Evidência**:
   - Reportar ao usuário o total de nós, arestas, pontes mapeadas e o caminho do arquivo HTML gerado.

---

## 🚨 Regras de Autonomia

- ✅ SEMPRE utilizar o template standalone em `tools/codegraph-visualizer/template/index.html`.
- ✅ SEMPRE verificar se o arquivo HTML gerado é auto-contido e executável offline.
- ❌ NÃO recriar bancos SQLite do zero se o `graph.db` já existir e estiver atualizado.
- ❌ NÃO expor credenciais ou dados sensíveis nos títulos dos nós.

---

*v1.0 — visualize-graph prompt — 2026-09-04*

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/visualize-graph` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/visualize-graph`
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
