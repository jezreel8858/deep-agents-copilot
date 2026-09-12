---
name: visualize-graph
description:
  Gera e abre a visualização interativa do grafo de conhecimento multi-repo em Angular Material 3
  (2D/3D), integrando AST de código, classificação de acoplamento, filtros arquiteturais
  (isolados/órfãos, papéis, camadas, multi-select de repositórios) e pontes de integração REST.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'file_search', 'list_dir', 'run_in_terminal', 'run_subagent', 'context-mode/ctx_execute']
argument-hint: '[--diff <ref> | --bridges <file>]'
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/instructions/README.md
  - tools/codegraph-visualizer/README.md
  - tools/codegraph-visualizer/bridges.json
  - .github/skills/terminal-governance/SKILL.md
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

