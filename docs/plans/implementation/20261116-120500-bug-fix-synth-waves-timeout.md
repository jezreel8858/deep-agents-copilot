---
status: "APPROVED"
approved: true
author: "@python-arch-advisor"
materialized_by: "@docs-engineer"
plan_type: "implementation"
created_at: "2026-11-16T12:05:00Z"
workflow: WORKFLOW-BUG-FIX
tier: light
plan_ref: docs/plans/implementation/20261116-120500-bug-fix-synth-waves-timeout.md
rollback_plan: "git checkout -- tools/headless-governance-runner/src/governance_runner/synth/storage.py tools/headless-governance-runner/tests/synth_unit/test_storage.py .github/prompts/synth-waves.prompt.md && git clean -f tests/governance_audit/test_synth_waves_prompt.py"
allowed_files:
  - tools/headless-governance-runner/src/governance_runner/synth/storage.py
  - tools/headless-governance-runner/tests/synth_unit/test_storage.py
  - tests/governance_audit/test_synth_waves_prompt.py
  - .github/prompts/synth-waves.prompt.md
progress: 100
lessons_extracted: true
lessons_applied_to: ["plan-conformance-patterns"]
lessons_at: "2026-11-16"
related-planning-doc: "docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md"
session_id: "sess-20261116-120000-bug-fix-synth-waves-timeout"
workflow_id: "WORKFLOW-BUG-FIX"
workflow_trace_id: "wf-trace-20261116-120000-bug-fix-synth-waves-timeout"
parent_plan_ref: "docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PASS"
  author_ref: "@python-arch-advisor"
---

# Plano de Implementação Técnica — Correção de Timeout, Concorrência SQLite e Reconciliação de Runs Órfãos em `/synth-waves`

Progresso: 6/6 tarefas concluídas

## 1. Contexto e Objetivo

Este plano de implementação técnica materializa a correção da causa raiz diagnosticada em `docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md` para o comando `/synth-waves`:

1. **Concorrência SQLite e Resiliência em `SynthRepository` (`storage.py`)**: Observa-se que `storage.py:154-155` (`migrar_conexao`) já define `PRAGMA foreign_keys = ON;` e `PRAGMA journal_mode = WAL;`. O que é **novo** em `storage.py` é:
   - (a) `timeout=30.0` em `sqlite3.connect(str(resolved), timeout=30.0)` em `SynthRepository.__init__` (`storage.py:331`); e
   - (b) `_configurar_conexao(self._conn)` chamado em `SynthRepository.__init__` aplicando `PRAGMA busy_timeout = 30000;` e `PRAGMA journal_mode = WAL;` (além de `PRAGMA foreign_keys = ON;`) em toda abertura de conexão antes de `self.migrar()`.
2. **Reconciliação Idempotente de Runs Órfãos (`storage.py`)**: Implementar `def reconciliar_runs_orfaos(self, run_id: str | None = None) -> int:` na classe `SynthRepository` para reconciliar registros em `synth_runs` que permaneceram com `status = 'running'` após timeout de subprocesso ou encerramento abrupto.
3. **Execução Resiliente e Particionada em `.github/prompts/synth-waves.prompt.md`**: Documentar o particionamento incremental (`--pending` e `--limit 3`, com menção a `background: true`), `cwd` explícito (`[LETRA_DRIVE]:\workspace\deep-agents-copilot` ou `${workspaceFolder}`), resolução de `COPILOT_SDK_TOKEN` via `gh auth token` e invocação de `reconciliar_runs_orfaos` exclusivamente após o término (ou timeout `ETIMEDOUT`) dos subprocessos síncronos de geração/avaliação da Onda e imediatamente antes de `synth-diagnose`.

### Esquema DDL Verificado em `tools/headless-governance-runner/src/governance_runner/synth/storage.py`

- **Tabela `synth_runs`**: colunas `run_id`, `kind`, `status`, `motivo`, `started_at`, `finished_at`, `premium_requests_used`, `n_candidates`, `n_accepted`.
- **Tabela `synth_prompts`**: colunas `prompt_id`, `run_id`.
- **Tabela `synth_evaluations`**: colunas `eval_id`, `run_id`, `prompt_id`, `passed`, `premium_requests`.

---

## 2. Arquivos no Escopo (`allowed_files`)

| Arquivo | Status no Workspace | Papel na Mudança |
| :--- | :--- | :--- |
| `tools/headless-governance-runner/src/governance_runner/synth/storage.py` | Existente (modificar) | Adicionar `timeout=30.0` em `sqlite3.connect`, `_configurar_conexao(self._conn)` aplicando `PRAGMA busy_timeout = 30000;` e `PRAGMA journal_mode = WAL;` em `SynthRepository.__init__`, e método `reconciliar_runs_orfaos(self, run_id: str \| None = None) -> int`. |
| `tools/headless-governance-runner/tests/synth_unit/test_storage.py` | Existente (modificar) | Testes unitários TDD para pragmas WAL/busy_timeout e todos os cenários de `reconciliar_runs_orfaos`. |
| `tests/governance_audit/test_synth_waves_prompt.py` | **Arquivo novo a ser criado** (Passo 1 — TDD) | Teste de auditoria de governança validando as **5 regras determinísticas** de `.github/prompts/synth-waves.prompt.md`. |
| `.github/prompts/synth-waves.prompt.md` | Existente (modificar) | Atualizar protocolo de ondas com particionamento `--pending --limit 3`, `cwd` explícito, resolução de `COPILOT_SDK_TOKEN` via `gh auth token` e reconciliação via `reconciliar_runs_orfaos` antes de `synth-diagnose`. |

---

## 3. Especificação Técnica Detalhada

### Decisão de Design Pattern (mini-ADR)

- **Padrão Selecionado**: **Repository + Idempotent State Reconciliation (Unit of Work Transacional em SQLite WAL)**.
- **Motivação**: Como o worker `governance-runner` grava cada prompt gerado (`inserir_prompt`) e cada avaliação (`inserir_avaliacao`) com `self._conn.commit()` imediato, mas só invoca `finalizar_run()` ao término do lote completo, um kill por timeout deixa `synth_runs.status = 'running'` mesmo com artefatos íntegros já persistidos. Centralizar a reconciliação dentro de `SynthRepository.reconciliar_runs_orfaos` encapsula a regra de consistência no próprio repositório SQLite, enquanto `timeout=30.0` e `PRAGMA busy_timeout = 30000;` evitam `sqlite3.OperationalError: database is locked`.
- **Alternativas Descartadas**:
  - *Heartbeat em arquivo JSON paralelo*: descartado por duplicar estado fora do SQLite e introduzir risco de split-brain.
  - *Nova flag CLI em `cli.py`*: descartada por estar fora de `allowed_files` e porque o script JS de orquestração do prompt pode invocar diretamente `SynthRepository.reconciliar_runs_orfaos` via one-liner Python (`spawnSync(pyBin, ['-c', ...])`).

### 3.1. Conexão SQLite e Pragmas em `SynthRepository` (`storage.py`)

Atualmente, `storage.py:154-155` (`migrar_conexao`) já define `PRAGMA foreign_keys = ON;` e `PRAGMA journal_mode = WAL;`. O que é **novo** em `storage.py` é:

1. **(a) Timeout de conexão em `SynthRepository.__init__` (`storage.py:331`)**:
   - Substituir `self._conn = sqlite3.connect(str(resolved))` por `self._conn = sqlite3.connect(str(resolved), timeout=30.0)`.
   - Manter `self._conn.row_factory = sqlite3.Row`.
2. **(b) Função auxiliar `_configurar_conexao(conn: sqlite3.Connection) -> None` chamada em `SynthRepository.__init__`**:
   - Criar `_configurar_conexao(conn: sqlite3.Connection) -> None` executando `PRAGMA foreign_keys = ON;`, `PRAGMA journal_mode = WAL;` e `PRAGMA busy_timeout = 30000;`.
   - Invocar `_configurar_conexao(self._conn)` em `SynthRepository.__init__` em toda abertura de conexão (imediatamente antes de `self.migrar()`).

### 3.2. Método `reconciliar_runs_orfaos` em `SynthRepository` (`storage.py`) e Proteção contra Condição de Corrida

Assinatura:

```python
def reconciliar_runs_orfaos(self, run_id: str | None = None) -> int:
```

Comportamento determinístico sobre registros de `synth_runs` com `status = 'running'` (filtrando adicionalmente por `run_id = ?` quando `run_id is not None`):

1. Selecionar `run_id`, `kind`, `n_candidates` de `synth_runs WHERE status = 'running'` (e `AND run_id = ?` se informado).
2. Para cada linha em `status = 'running'`:
   - **Caso 1 — `kind == 'generate'`**:
     - Consultar `SELECT COUNT(*) AS total FROM synth_prompts WHERE run_id = ?`.
     - Se `total > 0`: atualizar `synth_runs` definindo `status = 'completed'`, `n_accepted = total`, `n_candidates = CASE WHEN n_candidates < total THEN total ELSE n_candidates END`, `finished_at = COALESCE(finished_at, _utc_now_iso())` para o `run_id`.
     - Se `total == 0`: atualizar `synth_runs` definindo `status = 'failed'`, `motivo = 'interrompido_timeout_orfandade'`, `finished_at = COALESCE(finished_at, _utc_now_iso())` para o `run_id`.
   - **Caso 2 — `kind == 'eval'`**:
     - Consultar `SELECT COUNT(*) AS total, COALESCE(SUM(passed), 0) AS aceitos, COALESCE(SUM(premium_requests), 0) AS reqs FROM synth_evaluations WHERE run_id = ?`.
     - Se `total > 0`: atualizar `synth_runs` definindo `status = 'completed'`, `n_candidates = total`, `n_accepted = aceitos`, `premium_requests_used = reqs`, `finished_at = COALESCE(finished_at, _utc_now_iso())` para o `run_id`.
     - Se `total == 0`: atualizar `synth_runs` definindo `status = 'failed'`, `motivo = 'interrompido_timeout_orfandade'`, `finished_at = COALESCE(finished_at, _utc_now_iso())` para o `run_id`.
   - **Caso 3 — Outros valores de `kind` sem artefatos vinculados (`COUNT(*) == 0`)**:
     - Atualizar `synth_runs` definindo `status = 'failed'`, `motivo = 'interrompido_timeout_orfandade'`, `finished_at = COALESCE(finished_at, _utc_now_iso())`.
3. Realizar `self._conn.commit()` e retornar a contagem inteira (`int`) de runs reconciliados.

#### Proteção contra Condição de Corrida e Ponto de Entrada

- **Sincronismo / Ausência de Condição de Corrida**: No fluxo de `/synth-waves`, a reconciliação é invocada **exclusivamente após o término (ou timeout `ETIMEDOUT`) dos subprocessos síncronos de geração/avaliação da Onda e imediatamente antes de `synth-diagnose`**, passando o `run_id` específico da Onda (ou reconciliando runs órfãos quando não há subprocesso ativo), eliminando qualquer risco de fechar um run em andamento durante polling.
- **Ponto de Entrada Acionado pelo Script JS do Prompt `/synth-waves`**: Chamada one-liner Python via `spawnSync(pyBin, ['-c', 'from governance_runner.synth.storage import SynthRepository, resolver_caminho_db; ...'])` passando o `run_id` antes de `synth-diagnose` (sem necessidade de nova flag em `cli.py`).

### 3.3. Protocolo Resiliente em `.github/prompts/synth-waves.prompt.md` e Contrato de `tests/governance_audit/test_synth_waves_prompt.py`

O arquivo `.github/prompts/synth-waves.prompt.md` será atualizado e validado pelo novo teste `tests/governance_audit/test_synth_waves_prompt.py` quanto às **5 regras determinísticas** alinhadas ao plano pai (`docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md`):

1. **Regra 1**: Frontmatter `tools:` não contém `run_in_terminal`;
2. **Regra 2**: Corpo documenta particionamento incremental com `--pending` e `--limit 3` (e menção a `background: true`);
3. **Regra 3**: Corpo exige `cwd` explícito (`[LETRA_DRIVE]:\workspace\deep-agents-copilot` ou `${workspaceFolder}`);
4. **Regra 4**: Corpo documenta resolução de `COPILOT_SDK_TOKEN` via `gh auth token`;
5. **Regra 5**: Corpo instrui a reconciliação de runs `running` órfãos (`reconciliar_runs_orfaos`) antes de `synth-diagnose`.

---

## 4. Passo a Passo de Execução (TDD Red-Green-Refactor)

### Checklist de Execução Técnica (GFM Unificado)

- [x] **Tarefa 1 (TDD Red — Testes Unitários de Storage)**: Adicionar em `tools/headless-governance-runner/tests/synth_unit/test_storage.py` os testes para: (a) verificação de `journal_mode == 'wal'` e `busy_timeout == 30000` em banco em arquivo temporário (`tmp_path`); (b) `reconciliar_runs_orfaos` para `kind='generate'` com prompts persistidos (`status='completed'`, `n_accepted`, `n_candidates`, `finished_at`); (c) `reconciliar_runs_orfaos` para `kind='eval'` com avaliações persistidas (`status='completed'`, `n_candidates`, `n_accepted`, `premium_requests_used`, `finished_at`); (d) `reconciliar_runs_orfaos` para run `running` com zero registros filhos (`status='failed'`, `motivo='interrompido_timeout_orfandade'`); (e) filtro opcional por `run_id`.
- [x] **Tarefa 2 (TDD Red — Teste de Governança do Prompt com as 5 Regras Determinísticas)**: Criar o **arquivo novo** `tests/governance_audit/test_synth_waves_prompt.py` validando as **5 regras determinísticas** sobre `.github/prompts/synth-waves.prompt.md`: (1) frontmatter `tools:` não contém `run_in_terminal`; (2) corpo documenta particionamento incremental com `--pending` e `--limit 3` (e menção a `background: true`); (3) corpo exige `cwd` explícito (`[LETRA_DRIVE]:\workspace\deep-agents-copilot` ou `${workspaceFolder}`); (4) corpo documenta resolução de `COPILOT_SDK_TOKEN` via `gh auth token`; (5) corpo instrui a reconciliação de runs `running` órfãos (`reconciliar_runs_orfaos`) antes de `synth-diagnose`.
- [x] **Tarefa 3 (TDD Green — Implementação em `storage.py`)**: Implementar `timeout=30.0` em `sqlite3.connect(str(resolved), timeout=30.0)` em `SynthRepository.__init__` (`storage.py:331`), `_configurar_conexao(self._conn)` em `SynthRepository.__init__` aplicando `PRAGMA busy_timeout = 30000;` e `PRAGMA journal_mode = WAL;` em toda abertura de conexão, e o método `def reconciliar_runs_orfaos(self, run_id: str | None = None) -> int:` em `tools/headless-governance-runner/src/governance_runner/synth/storage.py`.
- [x] **Tarefa 4 (TDD Green — Atualização de `.github/prompts/synth-waves.prompt.md`)**: Atualizar `.github/prompts/synth-waves.prompt.md` contemplando as 5 regras determinísticas, incluindo chamada one-liner Python via `spawnSync(pyBin, ['-c', 'from governance_runner.synth.storage import SynthRepository, resolver_caminho_db; ...'])` passando o `run_id` exclusivamente após o término (ou timeout `ETIMEDOUT`) dos subprocessos síncronos de geração/avaliação da Onda e imediatamente antes de `synth-diagnose`.
- [x] **Tarefa 5 (Validação Automatizada em Lote)**: Executar `pytest` nos testes unitários (`tools/headless-governance-runner/tests/synth_unit/test_storage.py`) e nos testes de auditoria de governança (`tests/governance_audit/test_synth_waves_prompt.py` e `tests/governance_audit/test_governance_smells.py`), garantindo 100% de aprovação.
- [x] **Tarefa 6 (Quality Gate Final e Linter)**: Executar explicitamente `tests/governance_audit/test_governance_smells.py` junto com `tests/governance_audit/test_synth_waves_prompt.py` e `tools/headless-governance-runner/tests/synth_unit/test_storage.py` (`pytest tools/headless-governance-runner/tests/synth_unit/test_storage.py tests/governance_audit/test_synth_waves_prompt.py tests/governance_audit/test_governance_smells.py`) e validar zero erros nos arquivos alterados com `get_errors`.

---

### 🔒 Checklist Defensivo Pré-Code-Review

- [x] Nenhuma query SQL utiliza interpolação de strings insegura (100% parâmetros posicionais `?`).
- [x] `timeout=30.0` em `sqlite3.connect(str(resolved), timeout=30.0)` e `_configurar_conexao(self._conn)` (`PRAGMA busy_timeout = 30000;` + `PRAGMA journal_mode = WAL;` + `PRAGMA foreign_keys = ON;`) são aplicados em toda conexão aberta por `SynthRepository.__init__`.
- [x] `reconciliar_runs_orfaos` é 100% idempotente (chamadas subsequentes retornam `0` e não sobrescrevem runs já `completed` ou `failed`) e invocada exclusivamente após o término/timeout dos subprocessos da Onda e antes de `synth-diagnose`.
- [x] `finished_at` preserva timestamp existente via `COALESCE(finished_at, _utc_now_iso())`.
- [x] Nenhum arquivo fora de `allowed_files` foi tocado (conformidade estrita R-043 / R-064).

---

## Estratégia de Rollback

Em caso de regressão detectada durante ou após a implementação:

1. Reverter atomicamente os 3 arquivos modificados e remover o arquivo novo de teste via Git (conforme chave `rollback_plan` do frontmatter):
   - `git checkout -- tools/headless-governance-runner/src/governance_runner/synth/storage.py tools/headless-governance-runner/tests/synth_unit/test_storage.py .github/prompts/synth-waves.prompt.md && git clean -f tests/governance_audit/test_synth_waves_prompt.py`
2. Como `PRAGMA journal_mode = WAL;`, `PRAGMA busy_timeout = 30000;` e `reconciliar_runs_orfaos` não introduzem colunas destrutivas nem alteram a versão de schema (`SCHEMA_VERSION = 1`), o banco SQLite `synth.db` permanece 100% compatível com versões anteriores sem necessidade de migração reversa de dados.

## Parecer do Revisor Cético Pré-HITL (R-064 — Gate 2)

- **review_verdict**: `PASS_WITH_NITS`
- **review_rounds**: `2`
- **reviewer**: `"@plan-critic"`
- **review_tier1**: `PASS`
- **hitl_gate**: Aprovado pelo usuário no Gate HITL (R-064).
