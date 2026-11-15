# `tools.plan_lineage_query` — CLI Read-Only de Linhagem OTel e Telemetria R-064 v2

Utilitário CLI **100% Read-Only** para consulta de correlação distribuída (`session_id`, `workflow_id`, `workflow_trace_id`, `parent_plan_ref`) e agregação consultiva da telemetria do `@plan-critic` (`critic_rubric_gaps`, `critic_findings_summary`) sobre os artefatos em `docs/plans/<tipo>/*.md`.

## Segurança e Invariantes (OWASP ASI06 / R-064)
- **Zero Mutação**: nunca altera planos, agents ou skills.
- **YAML Seguro e Limite de Tamanho**: utiliza exclusivamente `yaml.safe_load` com teto de `256 KB` por arquivo.
- **Confinamento de Path Traversal**: rejeita com `exit code 2` qualquer `--root` que escape da raiz do repositório.
- **Proteção Anti-ASI06**: todos os candidatos retornados por `--curation-candidates` incluem `requires_hitl: true`, exigindo aprovação humana via `ask_questions` antes de qualquer ajuste em instruções de agents/skills.

## Exemplos de Uso

```bash
# Consultar planos de uma sessão específica
python -m tools.plan_lineage_query --session-id sess-20261114-200000-r064-otel

# Consultar planos por workflow_trace_id e exportar em Markdown
python -m tools.plan_lineage_query --workflow-trace-id wf-20261114-200000-feat-r064-otel-correlation --format md

# Agregar candidatos de curadoria por (author, gap_code)
python -m tools.plan_lineage_query --curation-candidates
```

## Exit Codes
- `0`: Execução bem-sucedida.
- `1`: Violação de schema v2 detectada quando `--strict` está ativo (ou arquivo acima de 256 KB).
- `2`: Tentativa de Path Traversal ou diretório fora do repositório.
