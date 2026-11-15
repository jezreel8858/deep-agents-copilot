---
status: COMPLETED
approved: true
approved_by: "usuario (HITL Gate 2, ask_questions)"
approved_at: "2026-11-15"
author: "@python-arch-advisor"
plan_type: "implementation"
created_at: "2026-11-15"
related-planning-doc: "docs/plans/architecture/20261115-100000-synth-routing-eval-sqlite.md"
parent_plan_ref: "docs/plans/architecture/20261115-100000-synth-routing-eval-sqlite.md"
workflow_id: "WORKFLOW-FEATURE-DEVELOPMENT"
tier: full
plan_ref: "docs/plans/implementation/20261115-110000-feature-synth-routing-eval-sqlite.md"
rollback_plan: "Seção '## Rollback' deste plano: git revert por bloco (B3→B2→B1), 1 commit por bloco; DB .cache descartável; Golden nunca alterado"
review_verdict: PASS_WITH_NITS
review_rounds: 3
review_tier1: PASS
reviewer: "@plan-critic"
allowed_files:
  - .gitignore
  - .github/agents/evals/synthetic/**
  - .github/agents/evals/synthetic/.gitkeep
  - .github/agents/evals/synthetic/promoted-*.yaml
  - scripts/dev/py-test.sh
  - tools/headless-governance-runner/pyproject.toml
  - tools/headless-governance-runner/README.md
  - tools/headless-governance-runner/src/governance_runner/cli.py
  - tools/headless-governance-runner/src/governance_runner/runner/sdk_adapter.py
  - tools/headless-governance-runner/src/governance_runner/synth/**
  - tools/headless-governance-runner/tests/runner_unit/test_cli.py
  - tools/headless-governance-runner/tests/runner_unit/test_sdk_adapter.py
  - tools/headless-governance-runner/tests/synth_e2e/**
  - tools/headless-governance-runner/tests/synth_unit/**
  - docs/plans/architecture/20261115-100000-synth-routing-eval-sqlite.md
  - docs/plans/implementation/20261115-110000-feature-synth-routing-eval-sqlite.md
progress: 100
lessons_extracted: true
lessons_applied_to: ["@python-arch-advisor", "plan-conformance-patterns"]
lessons_at: "2026-11-15"
---

Progresso: 6/26 tarefas concluídas

# Plano de Implementação Técnica — Geração Sintética, Dedup SQLite e Avaliação Cega do `agent-router` ([BACKEND_TASKS])

Raiz: `tools/headless-governance-runner` (abreviado `<R>`; `<S>` = `<R>/src/governance_runner`). Blueprint APPROVED_WITH_NOTES: ver `parent_plan_ref`.

## Invariantes (valem para todas as tarefas)
- `.github/agents/evals/casos-roteamento.yaml` é SOMENTE LEITURA (fora de `allowed_files`). Nenhum código abre-o em modo escrita.
- Somente stdlib para TF-IDF/cosseno/SQLite (`sqlite3`, `hashlib`, `math`, `unicodedata`, `random`); YAML via `yaml.safe_load`/`safe_dump` (dependência já existente no projeto; confirmar em B1-02, sem nova dependência).
- SQL 100% parametrizado (`?`). Python 3.11+, `mypy --strict`, `from __future__ import annotations`.
- Testes sempre via `scripts/dev/py-test.sh --project tools/headless-governance-runner tests/synth_unit/test_golden.py` (ou caminho completo `tools/headless-governance-runner/tests/synth_unit/test_golden.py` caso o `py-test.sh` não suporte `--project`; B1-02 deve confirmar a sintaxe real do script e registrá-la) (skill `embedded-runtime-governance` § Python/uv). Nenhuma execução real de SDK/premium em testes (dublê de `CopilotSDKClient`). Fixtures compartilhadas ficam em `tests/synth_unit/conftest.py` e `tests/synth_e2e/conftest.py` (cobertos pelos globs `tests/synth_unit/**` e `tests/synth_e2e/**`).
- Divergência registrada vs blueprint: o blueprint cita `.github/agents/evals/silver/` para o Silver; ESTE plano segue a instrução do solicitante e usa `.github/agents/evals/synthetic/` como quarentena Silver (arquivo `casos-roteamento-silver-<AAAAMMDD-HHMMSS>.yaml`) e `promoted-<run_id>.yaml` no mesmo diretório. Nomes disjuntos por prefixo; allowlist de caminho única `synthetic/`. Ver seção `## Divergências do Blueprint`.

## Divergências do Blueprint (decisão HITL obrigatória)
- **D1**: Silver em `.github/agents/evals/synthetic/` (blueprint: `silver/`).
- **D2**: `route_source` NULO permitido apenas quando `verdict='unparseable'` (blueprint: `NOT NULL`).
- Ambas exigem emenda no blueprint via `@tech-solution-architect` e decisão explícita no HITL; se o HITL rejeitar D1, usar `silver/` (apenas mudar constante `SILVER_DIR`, plano preserva isso como constante única em `exporter.py`).

### Decisão de Design Pattern (mini-ADR)
- Contexto: três backends de geração (template/sdk), repositório SQLite e SDK acoplado; necessidade de testar offline.
- Decisão: Ports & Adapters — `GeradorSintetico` (Protocol) com `GeradorTemplate`/`GeradorSDK` (Strategy); `SynthRepository` (Repository); funil de dedup como pipeline de funções puras (L1→L2); scorer separado do capturador de rota (Blind Evaluation).
- Alternativas: ORM/SQLAlchemy (descartado: exige dependência nova, stdlib suficiente); scikit-learn TF-IDF (descartado: dependência); edição in-place do Golden (descartado: viola CA-01).
- Consequências: + testabilidade offline e zero deps novas; − TF-IDF próprio exige testes de borda numéricos.

## Blast Radius
- Callers diretos a manter inalterados: `SDKRequest` e `construir_permission_handler_read_only` (usados em `runner/use_cases.py` e `tests/runner_unit/test_runner_agent_audit.py`, handler ~L148–172), `cli.py` (entry point `governance_runner.cli:main`; há também `runner/cli.py` duplicado — B3-04 deve confirmar via `@codegraph-engine` qual é o entry point e que o outro não é afetado), `pyproject.toml` (package-data e testpaths), `.gitignore`.

- [x] **B0-01** Levantar callers dos 4 pontos de extensão e registrar no plano; declara-se que `test_sdk_adapter.py` (`<R>/tests/runner_unit/test_sdk_adapter.py`) e `test_cli.py` (`<R>/tests/runner_unit/test_cli.py`) são alvos de CRIAÇÃO (inexistentes), a confirmar; confirmar existência de `tools/headless-governance-runner/README.md` (edição vs criação). `{paralelizavel: false, responsavel: "@codegraph-engine"}`
  - Aceite: lista de callers + testes existentes que devem permanecer verdes + confirmação de que `test_sdk_adapter.py` e `test_cli.py` são alvos de CRIAÇÃO (inexistentes) + confirmação da existência de `tools/headless-governance-runner/README.md` (edição vs criação, registrado também para B1-02/B3-06).
  - Resultado (`@codegraph-engine`):
    - `SDKRequest`: instanciado apenas em `executar_agent_audit` (`use_cases.py:176`) e re-exportado em `runner/__init__.py`; adicionar campos opcionais com default (`system_prompt: str | None = None`) preserva 100% de compatibilidade;
    - `construir_permission_handler_read_only`: chamado em `use_cases.py:172`; adicionar `strict_empty_scope: bool = False` preserva o comportamento atual de `agent-audit`;
    - `src/governance_runner/cli.py` é o entrypoint canônico (`runner/cli.py` é shim sem importadores);
    - Confirmados `tests/runner_unit/test_sdk_adapter.py` (a criar), `tests/runner_unit/test_cli.py` (a criar) e `tools/headless-governance-runner/README.md` (existente, a editar).
- [x] **B0-02** Emendar blueprint (`docs/plans/architecture/20261115-100000-synth-routing-eval-sqlite.md`) com D1 e D2. `{paralelizavel: true, responsavel: "@tech-solution-architect"}` — concluído (emenda D1 + D2 sincronizada no Blueprint).
## Histórico de Aprovação
- Gate 2 rodada 1: NEEDS_REVISION (10 achados; 5 HIGH) — revisão aplicada
- Gate 2 rodada 2: NEEDS_REVISION (Tier1 FAIL T1-4 rollback_plan; R2-1..R2-4) — corrigido
- Gate 2 @plan-critic: PASS_WITH_NITS (rodada 3/3)
- HITL: APROVADO — D1 e D2 aceitas; emenda do blueprint pendente via @tech-solution-architect (registrar como tarefa B0-02 `{paralelizavel: true, responsavel: "@tech-solution-architect"}`: emendar blueprint com D1 e D2)
## Parecer do Revisor Cético Pré-HITL (R-064)
- review_verdict: PASS_WITH_NITS (rodada 3/3, Tier1 PASS)
- rounds: 3
- review_tier1: PASS
- Status: aprovado com nits na rodada 3/3 (rodadas 1 e 2 endereçadas; aguardando decisão HITL para D1 e D2)
- Nits Rodada 3 (3/3):
  1. Frontmatter e `## Histórico de Aprovação` a atualizar com veredito da rodada 3 [feito].
  2. Tokens de abreviação `<R>` / `<S>` no corpo do plano (manter — legíveis e definidos em Invariantes).
  3. UNKNOWN: confirmar existência de `tools/headless-governance-runner/README.md` (criação vs edição) em B0-01/B1-02.
- Pendências HITL:
  - D1: diretório Silver em `.github/agents/evals/synthetic/` vs `.github/agents/evals/silver/`.
  - D2: `route_source` nulo permitido apenas quando `verdict='unparseable'`.
- Histórico das rodadas anteriores:
  - Rodada 1 (1–10): D1/D2 formalizados para HITL, `allow_root: Path` injetável, `testpaths` em `pyproject.toml`, seção `## Blast Radius` + `B0-01`, `SDKResponse.tool_events` opcional, `validar_orcamento_synth` em B2-05, Rollback detalhado, asserção 45/5/35/4 em `test_golden.py` e rastreio Plano↔Blueprint — endereçado.
  - Rodada 2 (R2-1..R2-4): `rollback_plan` no frontmatter, comando executável `scripts/dev/py-test.sh` explícito, fixtures em `tests/synth_unit/conftest.py` e `tests/synth_e2e/conftest.py`, anotação de cobertura/`py-test.sh` em B1-02 — endereçado.
## B1 — Fundação Offline

- [x] B1-01 `<S>/synth/__init__.py`, `<S>/synth/normalize.py`: `normalizar(texto)` (NFKC, casefold, remoção de acentos, colapso de espaços, pontuação) e `detectar_override(texto)` rejeitando `Rota:`, `Delegado:`, `Agente Ativo:`, `expected_agent_route` (case-insensitive) com motivo `override_directive_detected`. `{paralelizavel: true, responsavel: "@python-developer"}`
  - Aceite: idempotência (`normalizar(normalizar(x)) == normalizar(x)`); "Ação" e "acao" normalizam igual; 4 diretivas rejeitadas.
- [x] B1-02 `<S>/synth/schema.sql`, `<S>/synth/storage.py`, `<R>/pyproject.toml` (package-data `synth/*.sql`, `synth/*.yaml` e ajuste de `testpaths` incluindo `tests/synth_unit` e `tests/synth_e2e`): `SynthRepository` com migração idempotente (`schema_meta`), `PRAGMA foreign_keys=ON; journal_mode=WAL`, tabelas `synth_runs`, `synth_prompts`, `synth_evaluations` (`CHECK (verdict = 'unparseable' OR route_source IN ('tool_hook','text_banner'))`; `verdict` incluindo `unparseable`; `UNIQUE(run_id,prompt_id)`), `synth_exports`; índice por estrato; consulta de cobertura `COUNT(*) GROUP BY agente_alvo, dimensao_perturbacao`; caminho `.cache/routing_synth_history.db` sobrescrevível por `--db`/`GOV_SYNTH_DB`; validação de que `--db` não resolve para dentro de `.github/`; criação de `.cache/` sob demanda. Reconciliar com o DDL do blueprint §4 (ver D2). Confirmar a sintaxe real de `scripts/dev/py-test.sh` (suporte a `--project tools/headless-governance-runner` vs caminho completo `tools/headless-governance-runner/tests/synth_unit/test_golden.py`) e verificar a configuração de cobertura/`py-test.sh`, anotando obrigatoriamente o resultado no plano. `{paralelizavel: false, responsavel: "@python-developer"}`
  - Aceite: migração roda 2x sem erro; FK violada levanta `IntegrityError`; `:memory:` e `tmp_path` funcionam; cobertura por estrato correta; `scripts/dev/py-test.sh` coleta `synth_unit` e `synth_e2e` (teste-sentinela/`--collect-only` confirma); resultado da verificação de cobertura/`py-test.sh` e sintaxe real do script anotados no plano.
- [x] B1-03 `<S>/synth/golden.py`: loader read-only de `casos-roteamento.yaml` (`open(..., "r")`, `yaml.safe_load`), extrai seeds `(suite, id, prompt, expected.agent_route)`, filtro por `--targets`, `seguranca` somente com `--include-security`. `{paralelizavel: true, responsavel: "@python-developer"}`
  - Aceite: nenhuma chamada de escrita no arquivo (teste compara SHA-256 antes/depois); contagens 45/5/35/4 preservadas; `test_golden.py` assere contagens por suíte 45/5/35/4 lidas do loader; teste estático de que `golden.py` não usa modos de escrita (`"w"`, `"a"`, `"x"`, `write_text`, `safe_dump`).
- [x] B1-04 `<S>/synth/taxonomy.py`, `<S>/synth/taxonomy.yaml`: dimensões `parafrase`, `ruido_ortografico`, `code_switching_pt_en`, `omissao_palavra_chave`, `distrator_outro_agente`, `multi_intencao`, `comprimento_extremo` (curto ≤8 / longo ≥80 palavras), `registro_informal`; estrato=`(agente_alvo, dimensao)`; alocação `--per-stratum K` round-robin priorizando estratos de menor cobertura histórica; `random.Random(seed)` determinístico. `{paralelizavel: true, responsavel: "@python-developer"}`
  - Aceite: mesma seed ⇒ mesma alocação; estrato menos coberto alocado primeiro.
- [x] B1-05 `<S>/synth/dedup.py`: funil L1 (`sha256(texto_norm)` vs conjunto Golden+SQLite ⇒ `rejected_hash`) e L2 (TF-IDF esparso `dict[str,float]` word 1–2 + char 3–5 com bordas, `tf=1+log(cnt)`, `idf=log((1+N)/(1+df))+1`, L2-normalizado, índice invertido termo→docs, cosseno) com `--sim-threshold` default 0.85 ⇒ `rejected_similarity`; retorna `max_similarity` e `nearest_ref`. `{paralelizavel: false, responsavel: "@python-developer"}` (depende de B1-01)
  - Aceite: idêntico⇒L1; variação só de acento⇒L1; paráfrase próxima≥limiar⇒L2; distinto<limiar⇒accepted; limiar configurável; determinístico; corpus vazio sem divisão por zero.
- [x] B1-06 `.gitignore`: adicionar `.cache/`. `{paralelizavel: true, responsavel: "@python-developer"}`
  - Aceite: `.cache/routing_synth_history.db` ignorado pelo git.
- [x] B1-07 Testes B1 em `<R>/tests/synth_unit/` (`test_normalize.py`, `test_storage.py`, `test_golden.py`, `test_taxonomy.py`, `test_dedup.py`; fixtures compartilhadas em `tests/synth_unit/conftest.py`). `{paralelizavel: true, responsavel: "@python-test-engineer"}`

## B2 — Integração SDK, Geração e Avaliação Cega

- [x] B2-01 `<S>/runner/sdk_adapter.py` (+ reexport em `runner/__init__.py` se necessário): `SDKRequest.system_prompt: str | None = None`; `_ClienteSDKReal` repassa via `system_message` da sessão se exposto, senão prefixo delimitado determinístico no prompt (fallback documentado); `construir_permission_handler_read_only(..., strict_empty_scope: bool = False)`: com `True` nega leitura quando escopo vazio; default `False` mantém o comportamento `if caminho and escopo and caminho not in escopo`. Exposição do evento de ferramenta (`tool_hook`) — `SDKResponse` ganha campo opcional `tool_events` (default vazio, retrocompatível) populado a partir dos eventos de sessão do SDK quando disponíveis. Confirmar mecanismo do SDK com `@deep-search` ANTES de codificar (ponto de decisão, não bloqueia fallback). `{paralelizavel: false, responsavel: "@python-developer"}`
  - Aceite: chamadas existentes de `agent-audit` sem mudança de assinatura/saída; `strict_empty_scope=True` nega leitura com escopo vazio; teste com dublê emitindo evento de delegação popula `tool_events`; se o SDK real não expuser, `tool_events` vazio e o evaluator cai em `text_banner` (fallback declarado); revisão do `@security-reviewer`.
- [x] B2-02 Criar `<R>/tests/runner_unit/test_sdk_adapter.py` (alvo de criação, inexistente): `system_prompt` (presente/ausente), `strict_empty_scope` True/False, `tool_events`, NÃO REGRESSÃO `agent-audit` (default permite leitura com escopo vazio; `COMPATIBLE`). `{paralelizavel: true, responsavel: "@python-test-engineer"}`
  - Aceite: suíte `test_sdk_adapter.py` e `test_runner_agent_audit.py` 100% verdes.
- [x] B2-03 `<S>/synth/generator.py`: Protocol `GeradorSintetico`; `GeradorTemplate` (offline, determinístico por seed, aplica cada dimensão da taxonomia sem rede); `GeradorSDK` (usa `SDKRequest` com `strict_empty_scope=True`, Budget obrigatório, `--max-attempts` 3, `--generator-mode {sdk,template}` canônico e `--generator` alias). Todo texto gerado passa por `detectar_override` → dedup L1/L2 → persistência (aceitos e rejeitados com motivo). `{paralelizavel: false, responsavel: "@python-developer"}` (depende de B1-*, B2-01)
  - Aceite: modo template roda sem token e sem rede; prompt com override é rejeitado e persistido com motivo; `--dry-run` não grava; SDK sem orçamento nunca é chamado.
- [x] B2-04 `<S>/synth/evaluator.py`: lote retomável (`--run-id`, `--pending`, `--limit`, `--model`); carrega `--router-agent` (default `.github/agents/agent-router.agent.md`, corpo sem frontmatter) como `system_prompt` e grava `router_agent_sha256`; sessão isolada recebendo APENAS `prompt_text` + `system_prompt` (blind: `expected_route` nunca no request); captura de rota na ordem `tool_hook` → `text_banner` (linhas `Delegado:`/`Rota:`/`Agente Ativo:`) → `unparseable` (sem inventar rota); scorer pós-resposta faz join com `expected_route` ⇒ `passed`/`verdict`; `Budget` por item (`registrar_turno`, teto R-060) + `Budget` de lote (`registrar_custo`); estouro ⇒ `status='neutral'`, `motivo='budget_exhausted'`. `{paralelizavel: false, responsavel: "@python-developer"}` (depende de B1-02, B2-01)
  - Aceite: request capturado no dublê não contém `expected`; reexecução não reavalia itens já gravados; 3 caminhos de captura cobertos; `strict_empty_scope=True`.
- [x] B2-05 `<S>/synth/use_cases.py` (`RelatorioSynth`, funções `executar_synth_generate`, `executar_synth_eval`, `validar_orcamento_synth`) e orçamento: validação fail-fast (`validar_orcamento_synth`) ANTES de qualquer chamada SDK — `--max-premium-requests` (ou env `GOV_MAX_PREMIUM_REQUESTS`) inteiro `> 0` obrigatório em `synth-eval` e `synth-generate` com `--generator-mode {sdk,template}` (canônico; `--generator` alias aceito) em modo `sdk`; ausente/≤0/não numérico ⇒ exit/erro de código 2 (integração CLI permanece em B3-04, onde o exit code 2 ponta-a-ponta é verificado). Modo `template` não exige orçamento. `{paralelizavel: false, responsavel: "@python-developer"}`
  - Aceite: `validar_orcamento_synth` executa antes de `criar_cliente_sdk_real`/leitura de token; teste assere zero chamadas ao dublê e exit/erro de código 2 (exit code 2 ponta-a-ponta verificado em B3-04).
- [x] B2-06 Testes B2 em `<R>/tests/synth_unit/` (`test_generator.py`, `test_evaluator.py`, `test_budget_gate.py`) com dublê de `CopilotSDKClient`. `{paralelizavel: true, responsavel: "@python-test-engineer"}`

## B3 — Exportação Silver, Promoção, CLI e Testes

- [x] B3-01 `<S>/synth/exporter.py` — `synth-export`: constante única `SILVER_DIR` e `allow_root: Path` injetável (default `<repo>/.github/agents/evals/synthetic`, testes com `allow_root=tmp_path`); lê avaliações (`--eval-run-id`, `--only-failures` default true, `--include-near-boundary`) e grava Silver `casos-roteamento-silver-<AAAAMMDD-HHMMSS>.yaml` (rejeita prefixo `promoted-*`) validado com `resolve()` (traversal `..` ou symlink fora de `allow_root` ⇒ exit 2); registra em `synth_exports`. `{paralelizavel: false, responsavel: "@python-developer"}` (depende de B1-02)
- [x] B3-02 `<S>/synth/exporter.py` — `synth-promote` (`--silver`, `--run-id`, `--out`, `--stdout`, `--confirm`, `--suite` default `regressao`): exige entrada com prefixo `casos-roteamento-silver-*.yaml` sob `allow_root`; lê itens aprovados com `corrected_route`, re-deduplica read-only contra o Golden e grava apenas `promoted-<run_id>.yaml` sob `allow_root` (ou stdout/diff). Nunca abre `casos-roteamento.yaml` para escrita; caminho fora de `allow_root`/traversal/symlink ⇒ exit 2. `{paralelizavel: false, responsavel: "@python-developer"}` (depende de B3-01, B1-03, B1-05)
  - Aceite: SHA-256 de `casos-roteamento.yaml` idêntico antes/depois; itens duplicados do Golden descartados; sem `--confirm` apenas pré-visualiza.
- [x] **B3-03** `.github/agents/evals/synthetic/README.md`: processo de revisão humana Silver → `promoted-<run_id>.yaml` → PR manual; teste de que nenhum loader/glob existente em `tools/headless-governance-runner` ou `tests/` inclui `synthetic/*.yaml` nas contagens 45/5/35/4. `{paralelizavel: true, responsavel: "@docs-engineer"}`
- [x] B3-04 `<S>/cli.py` (confirmar entry point vs `runner/cli.py` em B0-01): `_USE_CASES_SUPORTADOS` = `("agent-audit","synth-generate","synth-eval","synth-export","synth-promote")`; `--base` validado pós-parse só para `agent-audit` (exit 2 preservado); `--generator-mode {sdk,template}` canônico (`--generator` alias); delega fail-fast a `validar_orcamento_synth`. `{paralelizavel: false, responsavel: "@python-developer"}` (depende de B2-05, B3-01, B3-02)
  - Aceite: exit code 2 ponta-a-ponta verificado em B3-04 para orçamento/caminhos; legados preservados em `test_cli.py` (alvo de criação).
- [x] B3-05 `<R>/README.md`: documentar `synth-*`, `--generator-mode {sdk,template}` (alias `--generator`), orçamento obrigatório, Blind Evaluation e fluxo Silver → `promoted-<run_id>.yaml` → PR manual. `{paralelizavel: true, responsavel: "@docs-engineer"}`
- [x] B3-06 Testes em `<R>/tests/synth_unit/test_exporter.py` (`allow_root=tmp_path`, traversal `..`/symlink ⇒ exit 2 no default, rejeição de `promoted-` no export e exigência de `casos-roteamento-silver-` no promote) e `<R>/tests/runner_unit/test_cli.py` (alvo de criação). `{paralelizavel: true, responsavel: "@python-test-engineer"}`
- [x] B3-07 Teste E2E offline `<R>/tests/synth_e2e/test_pipeline_e2e.py` (fixtures compartilhadas em `tests/synth_unit/conftest.py` e `tests/synth_e2e/conftest.py`): pipeline `generate (template) → eval (dublê) → export → promote` em `tmp_path`, verificando SHA-256 de `casos-roteamento.yaml` idêntico antes/depois. `{paralelizavel: false, responsavel: "@python-test-engineer"}` (depende de B3-04)

## Rastreio Plano↔Blueprint
| Plano | Blueprint | Escopo |
|---|---|---|
| B1-01 | B1-01 | normalize/dedup parte |
| B1-05 | B1-01 | dedup |
| B1-02 | B1-02 | schema/storage/pyproject |
| B1-03 | B1-03 | golden |
| B1-04 | B1-03 | taxonomy |
| B1-06 | B1-04 | .gitignore |
| B2-01 | B2-01 | sdk_adapter |
| B2-03 | B2-02 | generator |
| B2-04 | B2-03 | evaluator |
| B2-05 | B2-04 | use_cases (CLI em B3-04) |
| B3-01/02 | B3-01 | exporter |
| B3-03 | B3-02 | synthetic/README.md |
| B3-07 | B3-03 | E2E offline |
| B3-05 | B3-04 | README.md |

## Critérios de Aceite Globais (rastreio ao blueprint)
- CA-01 Golden imutável (B1-03, B3-02, B3-07). CA-02 captura determinística (B1-02, B2-04). CA-03 blind + sanitização (B2-03, B2-04). CA-04 zero open questions (B2-01 com fallback). CA-05 orçamento fail-fast + `strict_empty_scope` opt-in + não regressão `agent-audit` (B2-01, B2-02, B2-05, B3-04).
- Cobertura mínima nos módulos `synth/*`: ≥85% linhas em `synth/*` se a ferramenta de cobertura estiver configurada (confirmar e anotar o resultado no plano em B1-02); caso contrário, validar por testes dos ramos de captura e fail-fast.

## Estratégia de Testes (pirâmide)
- Unit (maioria): normalize, dedup (casos numéricos), storage `:memory:`, taxonomy/alocação, golden read-only, sdk_adapter, evaluator/generator com dublê, exporter/promote em `tmp_path`.
- Integração leve: CLI via `main([...])` com dublês e exit codes.
- E2E offline: 1 pipeline completo (B3-07). Sem testes que consumam premium requests.
- Execução: `scripts/dev/py-test.sh --project tools/headless-governance-runner tests/synth_unit/test_golden.py` (ou caminho completo `tools/headless-governance-runner/tests/synth_unit/test_golden.py` caso o `py-test.sh` não suporte `--project`; B1-02 deve confirmar a sintaxe real do script e registrá-la). Consulta ao `@test-strategy` somente se o @plan-critic apontar lacuna de pirâmide.

## Riscos
| ID | Risco | Mitigação |
|---|---|---|
| R1 | Mecanismo de `system_message` do SDK incerto | Fallback de prefixo delimitado; `@deep-search` em B2-01 |
| R2 | `strict_empty_scope` quebra `agent-audit` | Default `False`; teste de não regressão B2-02 |
| R3 | Divergência `silver/` vs `synthetic/` | Registrada; confirmação do crítico; allowlist única |
| R4 | `unparseable` vs `CHECK(route_source)` | Esquema permite nulo apenas nesse veredito; teste em B1-07 |
| R5 | Custo premium descontrolado | Orçamento obrigatório, `--limit`, modo template, `--dry-run` |
| R6 | Prompt injection via texto gerado | Sanitizador anti-override antes do dedup; Silver em quarentena |
| R7 | Path traversal em `--out/--silver/--db` | `resolve()` + allowlist; `--db` fora de `.github/` |
| R8 | Glob de loaders pegando `synthetic/*.yaml` | Verificação em B3-03 |
| R9 | Drift de `agent-router.agent.md` | `router_agent_sha256` por run |
| R10 | TF-IDF O(N²) em corpora grandes | Índice invertido; benchmark simples em teste |

## Rollback
- Arquivos exatos: `synth/**`, `sdk_adapter.py`, `runner/__init__.py`, `cli.py`, `pyproject.toml`, `.gitignore`, `README.md`, `synthetic/README.md`, `tests/synth_unit/**` (fixtures compartilhadas em `tests/synth_unit/conftest.py`), `tests/synth_e2e/**` (fixtures compartilhadas em `tests/synth_e2e/conftest.py`), `tests/runner_unit/test_sdk_adapter.py` (alvo de criação), `tests/runner_unit/test_cli.py` (alvo de criação).
- Commits: exigir UM commit por bloco (B1, B2, B3) para `git revert` (B3→B2→B1).
- Dados: `.cache/routing_synth_history.db` descartável (gitignored); artefatos em `synthetic/` removíveis sem efeito sobre o Golden.
- Gate e verificação das contagens: se testes de `agent-audit` ou contagens 45/5/35/4 falharem após B2/B3, reverter o bloco imediatamente; comando de verificação das contagens: `scripts/dev/py-test.sh --project tools/headless-governance-runner tests/synth_unit/test_golden.py` (ou caminho completo `tools/headless-governance-runner/tests/synth_unit/test_golden.py` caso o `py-test.sh` não suporte `--project`; B1-02 deve confirmar a sintaxe real do script e registrá-la) além da suíte existente de routing.

### 🔒 Checklist Defensivo Pré-Code-Review
- [x] Sanitização e validação de inputs em todas as bordas expostas (CLI, YAML, caminhos, texto gerado)
- [x] Ausência de segredos, tokens ou dados sensíveis em hardcode e logging seguro sem PII
- [x] Tratamento defensivo de exceções e controle de autorização/permissões validado
- [x] Testes unitários/integração defensivos atendendo aos quality gates

## Histórico de Aprovação
- Gate 2 rodada 1: NEEDS_REVISION (10 achados; 5 HIGH) — revisão aplicada; rodada 2 pendente
- Gate 2 rodada 2: NEEDS_REVISION (Tier1 FAIL T1-4 rollback_plan; R2-1..R2-4) — corrigido; rodada 3 pendente
- Gate 2 @plan-critic: PENDENTE (rodada 3)
- Aprovação humana (HITL): PENDENTE

## Parecer do Revisor Cético Pré-HITL (R-064)
- review_verdict: NEEDS_REVISION
- rounds: 2
- Status: endereçado na revisão (rodadas 1 e 2)
- Achados Rodada 1 (1–10):
  1. Divergência Silver: D1 (`.github/agents/evals/synthetic/` vs `silver/`, constante única `SILVER_DIR` em `exporter.py`) exige emenda via `@tech-solution-architect` e decisão HITL — endereçado na revisão.
  2. Allowlist vs `tmp_path`: `allow_root: Path` injetável (default `<repo>/.github/agents/evals/synthetic`, testes com `allow_root=tmp_path`), traversal/symlink ⇒ exit 2 e prefixos `promoted-` / `casos-roteamento-silver-` (B3-01, B3-02, B3-06) — endereçado na revisão.
  3. `testpaths` falso verde: ajuste de `testpaths` em `pyproject.toml` (`tests/synth_unit`, `tests/synth_e2e`) e coleta sem argumentos em `scripts/dev/py-test.sh` (B1-02) — endereçado na revisão.
  4. Blast radius: seção `## Blast Radius` e tarefa `B0-01` (`@codegraph-engine`) mapeando callers dos 4 pontos de extensão e `cli.py` vs `runner/cli.py` — endereçado na revisão.
  5. `tool_hook` sem dono: `SDKResponse.tool_events` opcional (default vazio, retrocompatível) em B2-01 com fallback `text_banner` e confirmação via `@deep-search` — endereçado na revisão.
  6. CLI/orçamento em B2: `validar_orcamento_synth` em B2-05 antes de `criar_cliente_sdk_real`/token (zero chamadas ao dublê, exit/erro 2; CLI ponta-a-ponta em B3-04) e `Aceite:` em B2-02/B2-05 — endereçado na revisão.
  7. Rollback: arquivos exatos listados, UM commit por bloco (B1, B2, B3) para `git revert` e comando `scripts/dev/py-test.sh --project tools/headless-governance-runner tests/synth_unit/test_golden.py` (ou caminho completo `tools/headless-governance-runner/tests/synth_unit/test_golden.py` caso o `py-test.sh` não suporte `--project`; B1-02 deve confirmar a sintaxe real do script e registrá-la) — endereçado na revisão.
  8. DDL `route_source`: divergência D2 (`route_source` NULO permitido apenas quando `verdict='unparseable'`) formalizada para emenda e decisão HITL — endereçado na revisão.
  9. Teste de contagens: aceite em B1-03 com asserção 45/5/35/4 em `test_golden.py` e teste estático contra escrita em `golden.py`, mais teste anti-glob de `synthetic/` em B3-03 — endereçado na revisão.
  10. Nits: flag canônica `--generator-mode {sdk,template}` (`--generator` alias), `test_cli.py` criação, fixtures em `tests/synth_unit/conftest.py` e `tests/synth_e2e/conftest.py`, tabela `## Rastreio Plano↔Blueprint` e cobertura condicional — endereçado na revisão.
- Achados Rodada 2 (R2-1..R2-4):
  - R2-1 (BLOCKER/T1-4): `rollback_plan` adicionado ao frontmatter e `review_rounds: 2` — corrigido.
  - R2-2 (MEDIUM): comando executável `scripts/dev/py-test.sh --project tools/headless-governance-runner tests/synth_unit/test_golden.py` (ou caminho completo `tools/headless-governance-runner/tests/synth_unit/test_golden.py` caso o `py-test.sh` não suporte `--project`; B1-02 deve confirmar a sintaxe real do script e registrá-la) explicitado no Rollback e nos comandos de teste — corrigido.
  - R2-3 (MEDIUM): `tools/headless-governance-runner/tests/conftest.py` removido de `allowed_files` e do Rollback (fixtures em `tests/synth_unit/conftest.py` e `tests/synth_e2e/conftest.py` sob os globs `tests/synth_unit/**` e `tests/synth_e2e/**`); declarado em B0-01 que `test_sdk_adapter.py` e `test_cli.py` são alvos de CRIAÇÃO (inexistentes), a confirmar — corrigido.
  - R2-4 (LOW): registrado em B1-02 que o resultado da verificação de cobertura/`py-test.sh` deve ser anotado no plano — corrigido.


<!-- B1 (ETAPA 3a): módulos normalize/storage/golden/taxonomy/dedup validados por smoke import (normalização idempotente, 4 diretivas rejeitadas, API storage/dedup/golden presentes); .gitignore contém .cache/; pyproject com testpaths e package-data OK. Sintaxe py-test.sh: --project <raiz> [args pytest] (exige Git Bash no Windows; /bin/bash do WSL ausente). B1-07 (testes) pendente para @python-test-engineer. Resultado suíte existente: s/routing_unit/test_state_machine_idempotency.py::TestStateMachineIdempotency::test_deve_manter_idempotencia_em_evento_de_conclusao_de_workflow log: <HOME>/.cache/deep-agents-copilot/logs/py-test-20261114-173937-3004.log [dac] [FALLBACK] sem uv; usando python -m pytest (sem lock) [dac] pytest rc=1  -->
