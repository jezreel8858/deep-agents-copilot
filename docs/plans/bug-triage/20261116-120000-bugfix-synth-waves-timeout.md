---
status: APPROVED
approved: true
author: "@bug-triage"
materialized_by: "@docs-engineer"
plan_type: "bug-triage"
workflow: "WORKFLOW-BUG-FIX"
created_at: "2026-11-16T12:00:00Z"
related-planning-doc: "N/A — plano raiz"
allowed_files:
  - .github/prompts/synth-waves.prompt.md
  - tools/headless-governance-runner/src/governance_runner/synth/storage.py
  - tools/headless-governance-runner/tests/synth_unit/test_storage.py
  - tests/governance_audit/test_synth_waves_prompt.py
lessons_extracted: true
lessons_applied_to: ["plan-conformance-patterns"]
lessons_at: "2026-11-16"
---

# Plano de Triagem e Correção de Bug: Timeout no `/synth-waves` via `ctx_execute`

## 1. Contexto e Sintoma Reportado

Durante a execução do comando `/synth-waves` no ambiente Windows/JetBrains IDE, a Onda 2 (`synth-eval`) sofreu aborto sistemático por timeout e acionou o Circuit Breaker Fail-Fast sob **Compact Error Reporting (R-020)**:

- **Erro Primário**: `MCP tool call mcp_context-mode_ctx_execute timed out after 60000ms` (1º timeout com lote integral de cenários pendentes).
- **Retry / Troca de Estratégia**: 2º timeout consecutivo ao tentar reexecutar `synth-eval` via chamada síncrona em `ctx_execute`, mesmo com `timeoutMs: 300000` informado nos parâmetros da tool.
- **Efeito Colateral no Banco SQLite**: Runs iniciados na Onda 2 permanecem órfãos com `status='running'` em `.synth/results.db` após o kill forçado do subprocesso pelo timeout do cliente MCP, aumentando o risco de contenção (`database is locked`) em retentativas subsequentes.
- **Dúvida/Sugestão do Usuário**: Avaliar a inclusão da tool `run_in_terminal` no prompt `.github/prompts/synth-waves.prompt.md` como alternativa ou fallback ao `ctx_execute` para evitar o timeout.

---

## 2. Análise de Causa Raiz (RCA) e Evidências

A investigação comprovou que o problema decorre da combinação de **três fatores técnicos verificáveis**:

### 2.1. Contrato Declarativo Rígido e Incompleto em `.github/prompts/synth-waves.prompt.md`

- **Evidência (`.github/prompts/synth-waves.prompt.md:44-47` e `:58`)**:
  - As linhas `44-47` impõem a regra de *"1 Onda por turno, máx. 1 tool call `ctx_execute` por turno"* de forma estritamente síncrona, sem orientar o uso de `background: true` (suportado pelo schema do `mcp_context-mode_ctx_execute`) nem particionamento incremental (`--pending --limit <N>`).
  - A linha `58` dispara `governance-runner synth-eval --run-id <RUN_ID>` para avaliar todos os cenários da onda em uma única chamada bloqueante.
  - Adicionalmente, o snippet do prompt não fixa explicitamente o diretório de trabalho (`cwd: 'D:\\workspace\\deep-agents-copilot'` — fazendo `process.cwd()` recair em `[LETRA_DRIVE]:\Users\{username}` no host JetBrains) nem resolve previamente `COPILOT_SDK_TOKEN` via `gh auth token` quando ausente no ambiente do processo MCP.

### 2.2. Hard Timeout do Cliente MCP no Host JetBrains (~60s) vs. Latência Serial do Copilot SDK

- **Evidência (`tools/headless-governance-runner/src/governance_runner/synth/evaluator.py:258-296` e `cli.py:235-247`)**:
  - O cliente MCP embutido no JetBrains IDE aplica um *hard timeout* de transporte JSON-RPC de aproximadamente **60 segundos** por requisição de tool, independentemente do parâmetro `timeoutMs: 300000` aceito internamente pelo servidor `context-mode`.
  - Em `evaluator.py:258-296` (invocado por `cli.py:235-247`), a avaliação de cenários via Copilot SDK ocorre em série com latência média real de **~13,8 segundos por requisição**.
  - Consequentemente, qualquer lote com **mais de 4 avaliações** (`5 × 13,8s = 69,0s > 60s`) ultrapassa deterministicamente a janela de 60s do cliente MCP se executado de forma síncrona em uma única chamada.

### 2.3. Contenção de Lock e Runs Órfãos no SQLite (`storage.py`)

- **Evidência (`tools/headless-governance-runner/src/governance_runner/synth/storage.py:331` e `:155`)**:
  - Na linha `331`, `sqlite3.connect(str(resolved))` utiliza o timeout padrão do Python (`5.0` segundos) e não configura `PRAGMA busy_timeout=30000` em cada conexão aberta.
  - Na linha `155`, `PRAGMA journal_mode=WAL` é executado apenas durante o fluxo inicial de migração, sem garantia de pragmas de concorrência (`busy_timeout=30000`, `synchronous=NORMAL`) em todas as conexões subsequentes.
  - Quando o cliente MCP interrompe a chamada aos 60s, o processo filho pode deixar o registro da execução preso com `status='running'` na tabela `synth_runs` e transações pendentes, sem rotina de reconciliação de runs órfãos antes de retomar `synth-eval --pending`.

---

## 3. Avaliação Técnica da Sugestão do Usuário (`run_in_terminal` como Fallback ao `ctx_execute`)

A proposta de adicionar `run_in_terminal` ao frontmatter/corpo de `.github/prompts/synth-waves.prompt.md` foi avaliada e **rejeitada tecnicamente** pelos 3 motivos abaixo:

| # | Critério | Evidência Verificada | Conclusão |
|---|---|---|---|
| **(a)** | **Indisponibilidade física no Host JetBrains** | No runtime JetBrains desta sessão, a tool nativa `run_in_terminal` não faz parte do conjunto de tools expostas ao agente. Declarar `run_in_terminal` na lista `tools:` do frontmatter de `synth-waves.prompt.md` não instancia nem habilita uma tool inexistente no host IDE. | Ineficaz no ambiente onde o bug ocorre. |
| **(b)** | **Violação direta de Governança (R-008, R-049 e R-056)** | A suíte `tests/governance_audit/test_governance_smells.py:163-224` audita a conformidade com `terminal-governance` e o uso compulsório do sandbox `context-mode`. Além disso, o próprio `.github/prompts/synth-waves.prompt.md:45` proíbe explicitamente o uso de `run_in_terminal`. | Quebraria os testes de auditoria de governança e violaria R-008/R-049/R-056. |
| **(c)** | **Capacidade Nativa Já Existente no `ctx_execute` e no CLI** | O schema da tool `mcp_context-mode_ctx_execute` já possui suporte nativo ao parâmetro `background: true`, e o CLI `governance-runner synth-eval` já implementa `--pending` e `--limit <N>` em `cli.py:78-79` e `evaluator.py:258-296`. | O gargalo síncrono é resolvido nativamente com `--pending --limit 3` e/ou `background: true` dentro do próprio `ctx_execute`. |

---

## 4. Blast Radius e Classificação de Impacto

- **Classificação de Impacto**: **Nível Amarelo** (mini-refactoring controlado e circunscrito a 4 arquivos em 2 domínios).
- **Domínios Afetados e Roteamento Pós-Gate**:
  1. **Domínio de Governança Declarativa (`@governance-maintainer`)**:
     - `.github/prompts/synth-waves.prompt.md` (atualização das instruções da Onda 2 para micro-lotes incrementais `--pending --limit 3` ou execução assíncrona via `background: true`, fixação de `cwd` absoluto do repositório e resolução de `COPILOT_SDK_TOKEN`).
     - `tests/governance_audit/test_synth_waves_prompt.py` (teste de regressão garantindo a presença das diretivas anti-timeout e ausência de `run_in_terminal`).
  2. **Domínio Python / Persistência SQLite (`@python-router` → `@python-arch-advisor` → `@python-developer` / `@python-test-engineer`)**:
     - `tools/headless-governance-runner/src/governance_runner/synth/storage.py` (configuração centralizada de `timeout=30.0`, `PRAGMA journal_mode=WAL` e `PRAGMA busy_timeout=30000` em toda conexão SQLite + helper de reconciliação de runs órfãos com `status='running'`).
     - `tools/headless-governance-runner/tests/synth_unit/test_storage.py` (testes unitários validando pragmas de conexão e recuperação de runs `running` órfãos).

---

## 5. Alternativas Arquiteturais Avaliadas e Solução Recomendada

| Opção | Descrição | Prós | Contras / Trade-offs |
|---|---|---|---|
| **Opção 1 (Recomendada)** | **Particionamento Incremental (`--pending --limit 3`) + `background: true`/Polling em `ctx_execute` + Hardening SQLite (`busy_timeout=30000` + reconciliação de runs órfãos)** | Elimina o timeout de 60s do JetBrains (~41s por micro-lote de 3 cenários ou execução desacoplada em background), fixa `cwd` e `COPILOT_SDK_TOKEN`, elimina locks no SQLite e preserva 100% de conformidade com R-008/R-049/R-056. | Requer coordenação em 2 domínios (`.github/prompts/` + `storage.py` e respectivos testes). |
| **Opção 2** | **Apenas Atualização Declarativa em `synth-waves.prompt.md` (`--pending --limit 3` e `background: true`, sem alterar `storage.py`)** | Mudança restrita a prompt e teste de governança; menor escopo imediato. | Não corrige o timeout default de 5s em `sqlite3.connect` nem reconcilia runs presos em `status='running'` caso ocorra queda abrupta. |
| **Opção 3** | **Apenas Diagnóstico / Execução Manual Externa via CLI fora do MCP** | Zero alteração de código no repositório. | Mantém o comando `/synth-waves` quebrado para lotes > 4 cenários dentro do IDE JetBrains. |

### Solução Recomendada

Adotar a **Opção 1**, combinando:
1. Execução da Onda 2 em micro-lotes idempotentes (`--pending --limit 3`) ou via `background: true` com polling leve no `ctx_execute`, mantendo cada chamada individual abaixo de ~45s (margem segura contra o limite de 60s do cliente MCP JetBrains).
2. Fixação explícita do `cwd` do workspace e injeção segura de `COPILOT_SDK_TOKEN` via `gh auth token` no template do prompt.
3. Hardening da conexão SQLite em `storage.py` (`timeout=30.0`, `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=30000`) e reconciliação de runs órfãos.

---

## 6. Plano Mínimo de Correção Passo a Passo (Safety Net TDD) e Estratégia de Rollback

### Passo 0 — Testes de Regressão (Red Phase / Safety Net TDD)

1. Criar/atualizar `tests/governance_audit/test_synth_waves_prompt.py` verificando que `.github/prompts/synth-waves.prompt.md`:
   - Não referencia nem habilita `run_in_terminal` no frontmatter ou corpo (conformidade R-008/R-049/R-056);
   - Documenta o uso de `--pending --limit 3` (ou `background: true`) na Onda 2 (`synth-eval`) para respeitar o teto de 60s do cliente MCP;
   - Especifica `cwd` explícito do repositório e resolução de `COPILOT_SDK_TOKEN`.
2. Atualizar `tools/headless-governance-runner/tests/synth_unit/test_storage.py` adicionando testes unitários para:
   - Verificar que toda conexão aberta por `storage.py` aplica `PRAGMA busy_timeout = 30000` e `PRAGMA journal_mode = WAL`;
   - Verificar a reconciliação de runs órfãos com `status='running'` ao retomar ou finalizar lotes pendentes.

### Passo 1 — Hardening de Conexão e Reconciliação SQLite (`storage.py`)

1. Em `tools/headless-governance-runner/src/governance_runner/synth/storage.py:331` (e ponto único de abertura de conexão):
   - Configurar `sqlite3.connect(str(resolved), timeout=30.0)`;
   - Aplicar sistematicamente `PRAGMA journal_mode=WAL;` e `PRAGMA busy_timeout=30000;` na abertura da conexão;
   - Garantir que runs interrompidos em estado `running` possam ser retomados por `synth-eval --pending` e reconciliados ao término dos cenários pendentes.

### Passo 2 — Atualização do Contrato Operacional (`.github/prompts/synth-waves.prompt.md`)

1. Atualizar `.github/prompts/synth-waves.prompt.md:44-65`:
   - Preservar a proibição de `run_in_terminal`;
   - Substituir a chamada monolítica síncrona da Onda 2 por execução incremental particionada (`--pending --limit 3`) e/ou `background: true` no `ctx_execute`;
   - Incluir `cwd` explícito para a raiz do workspace e fallback de `COPILOT_SDK_TOKEN` via `gh auth token`.

### Passo 3 — Validação Integrada (Green Phase & Quality Gate)

1. Executar os testes unitários e de governança em lote via `ctx_execute`:
   - `pytest tools/headless-governance-runner/tests/synth_unit/test_storage.py tests/governance_audit/test_synth_waves_prompt.py tests/governance_audit/test_governance_smells.py -q`
2. Executar `get_errors` agrupado (R-051) nos 4 arquivos de `allowed_files`.

### Estratégia de Rollback

Caso qualquer regressão seja detectada durante ou após a aplicação do plano, reverter integralmente e de forma atômica apenas os arquivos autorizados no manifesto:

```bash
git checkout -- .github/prompts/synth-waves.prompt.md tools/headless-governance-runner/src/governance_runner/synth/storage.py tools/headless-governance-runner/tests/synth_unit/test_storage.py tests/governance_audit/test_synth_waves_prompt.py
```

---

## 7. Critérios de Aceitação Verificáveis

- [ ] **CA-01 (Frontmatter & R-064)**: Plano materializado em `docs/plans/bug-triage/20261116-120000-bugfix-synth-waves-timeout.md` com `status: DRAFT`, `approved: false`, `author: "@bug-triage"`, `materialized_by: "@docs-engineer"` e `allowed_files` restrito aos 4 arquivos mapeados.
- [ ] **CA-02 (Governança de Terminal R-008/R-049/R-056)**: `.github/prompts/synth-waves.prompt.md` permanece sem `run_in_terminal` e passa 100% em `tests/governance_audit/test_governance_smells.py` e `tests/governance_audit/test_synth_waves_prompt.py`.
- [ ] **CA-03 (Mitigação do Timeout de 60s do Cliente MCP)**: Onda 2 (`synth-eval`) documentada e configurada para operar com `--pending --limit 3` e/ou `background: true` em `ctx_execute`, com `cwd` explícito e `COPILOT_SDK_TOKEN` resolvido, mantendo cada chamada síncrona abaixo de 60s.
- [ ] **CA-04 (Resiliência SQLite)**: `storage.py` aplica `timeout=30.0`, `PRAGMA journal_mode=WAL` e `PRAGMA busy_timeout=30000` em todas as conexões e reconcilia runs órfãos com `status='running'`, validado por `tools/headless-governance-runner/tests/synth_unit/test_storage.py`.


## Parecer do Revisor Cético Pré-HITL (R-064)

- `review_verdict`: `PASS_WITH_NITS`
- `review_rounds`: `1`
- `reviewer`: `"@plan-critic"`
- `review_tier1`: `PASS`
- **Aprovação Humana (Gate HITL)**: Aprovado pelo usuário (Opção 1) para avanço ao Plano de Implementação Técnica (`WORKFLOW-BUG-FIX`).
