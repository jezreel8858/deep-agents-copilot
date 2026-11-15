# `tools/governance_sync`

Utilitário determinístico de sincronização e auditoria de governança documental (R-015 / R-033 / R-055 / R-064).

## Responsabilidades

1. **Derivação Dinâmica de Contagens SSOT**:
   - `total_agent_files` (`.github/agents/**/*.agent.md` = 63: 31 na raiz + 32 em `stacks/`)
   - `catalog_root_entries` (`.github/agents/catalog.yaml` = 39 entradas)
   - `routing_graph_nodes` (`.github/agents/routing-graph.yaml` chave `nos:` = 39 nós)
   - `total_skills` (`.github/skills/.index.json` e `.github/skills/*/SKILL.md` = 81 skills: 15 Tier 1, 65 Tier 2, 1 Tier 3)
   - `total_canonical_workflows` (`.github/agents/workflows/workflow-*.md` = 10 workflows)
   - `generic_instructions` (`.github/instructions/*.instructions.md` = 6 adapters genéricos)
2. **Auditoria e Sincronização de Documentos Vivos**:
   - Monitora `README.md`, `docs/repo-map.md`, `docs/README.md`, `.github/agents/README.md`, `.github/skills/README.md`, `.github/instructions/README.md`, `docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md` e `tests/README.md`.
   - Exclui caminhos históricos imutáveis (`docs/plans/`, `CHANGELOG.md`, `docs/adr/`).
3. **Cobertura Canônica de Agents**:
   - Garante que 100% dos agents de `.github/agents/catalog.yaml` constem em `README.md` e `.github/agents/README.md` e bloqueia agents fantasmas removidos (`refactor-executor`).
4. **Docs & Mermaid Sync Gate (R-064)**:
   - Verifica que os 10 arquivos em `R064_PRE_HITL_WORKFLOW_MERMAID_FILES` incluem `plan-critic` dentro de pelo menos um bloco ` ```mermaid ` com sintaxe balanceada, respeitando `WORKFLOW_MERMAID_EXEMPTIONS`.

## Uso via CLI

```bash
# Modo verificação (CI / Quality Gate — falha com exit code 1 se houver drift)
python -m tools.governance_sync --check

# Modo simulação (exibe desvios sem modificar arquivos)
python -m tools.governance_sync --dry-run

# Modo aplicação (sincroniza padrões de contagem defasados nos documentos vivos)
python -m tools.governance_sync --apply
```
