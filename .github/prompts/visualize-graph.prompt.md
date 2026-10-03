---
name: visualize-graph
description:
  Gera e abre a visualização interativa do grafo de conhecimento multi-repo em Angular Material 3
  (2D/3D), integrando AST de código, classificação de acoplamento, filtros arquiteturais
  (isolados/órfãos, papéis, camadas, multi-select de repositórios) e pontes de integração REST.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'file_search', 'list_dir', 'run_in_terminal', 'run_subagent', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_search']
argument-hint: '[--diff <ref> | --bridges <file>]'
source_docs:
  - .github/instructions/README.md
  - tools/codegraph-visualizer/README.md
  - tools/codegraph-visualizer/bridges.json
  - .github/skills/terminal-governance/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/visualize-graph`

> **Propósito**: Compilar e abrir a visualização interativa unificada do Grafo de Conhecimento Multi-Repo
> com interface Angular Material 3, alternância 2D/3D e análise de blast radius.
> **Workspace**: `${workspaceFolder}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** compilar e abrir a visualização interativa do grafo local.
- ✅ **SEMPRE** utilizar dados reais dos bancos SQLite `.codegraph/graph.db`.
- ❌ **NÃO** alterar a estrutura de arquivos da aplicação ou do repositório durante a visualização.
- ❌ **NÃO** executar rebuild de grafos desnecessariamente quando já indexados.

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
