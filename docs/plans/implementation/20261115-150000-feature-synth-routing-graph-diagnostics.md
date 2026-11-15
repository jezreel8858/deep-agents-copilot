---
status: APPROVED
approved: true
author: "@python-arch-advisor"
plan_type: "implementation"
created_at: "2026-11-15T15:00:00Z"
workflow_id: "WORKFLOW-FEATURE-DEVELOPMENT"
tier: full
related-planning-doc: "docs/plans/architecture/20261115-140000-synth-routing-graph-diagnostics.md"
plan_ref: docs/plans/implementation/20261115-150000-feature-synth-routing-graph-diagnostics.md
allowed_files:
  - "tools/headless-governance-runner/src/governance_runner/synth/**"
  - "tools/headless-governance-runner/src/governance_runner/cli.py"
  - "tools/headless-governance-runner/README.md"
  - "tools/headless-governance-runner/tests/synth_unit/**"
  - "tools/headless-governance-runner/tests/synth_e2e/**"
  - "tools/headless-governance-runner/tests/runner_unit/test_cli.py"
  - ".github/agents/evals/synthetic/**"
read_only_files:
  - ".github/agents/routing-graph.yaml"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/evals/casos-roteamento.yaml"
  - "tools/headless-governance-runner/src/governance_runner/routing/**"
rollback_plan: "git revert por bloco B3→B2→B1, 1 commit por bloco; .cache/routing_synth_history.db descartável; Golden e arquivos read_only intocados"
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: PASS
review_verdict: PASS_WITH_NITS
---

Progresso: 8/11 tarefas concluídas

# Plano de Implementação — synth + routing-graph (geração guiada e diagnóstico)

Base: blueprint delta (parent) sobre 20261115-100000-synth-routing-eval-sqlite.md (plano 20261115-110000 já COMPLETED).

### Decisão de Design Pattern (mini-ADR)
- Contexto: usar campos do routing-graph.yaml sem acoplar synth a routing.model nem duplicar validação.
- Decisão: Anti-Corruption Layer (synth/routing_graph.py sobre routing/graph_loader.py::carregar_grafo) + Strategy para --graph-seeding (off|gaps|all) + Oráculo offline como função pura (Pipes & Filters).
- Alternativas consideradas: parser YAML próprio (duplica validação); estender routing.model (blast radius no audit); diagnóstico dentro de synth-eval (mistura custo SDK e análise offline).
- Consequências: +4 módulos e 1 use-case; dependência unidirecional synth → routing; diagnóstico re-executável de forma idempotente.

### Invariantes e restrições
- --graph-seeding default `off`; Golden (45/5/35/4) intocado; graph-seeding aditivo e opt-in.
- Arestas health_check e mandatory_pre_step excluídas das rotas válidas; security_gate incluída.
- Migração SQLite v1→v2 transacional (BEGIN IMMEDIATE, PRAGMA user_version 1→2), idempotente, ALTER TABLE individuais via conn.execute, índice ix_prompts_graph_edge criado depois das colunas; PROIBIDO executescript. Colunas: prompts.seed_source, graph_edge_id, graph_edge_resolution; synth_runs.routing_graph_sha256. Tabelas: routing_graph_edges, synth_diagnostics.
- Grafo carregado exclusivamente via routing/graph_loader.py::carregar_grafo; caminho_schema fixo do pacote (nunca fornecido pelo usuário).
- PROIBIDA mutação de routing-graph.yaml, agent-router.agent.md, casos-roteamento.yaml (denylist por path resolvido, case-insensitive no Windows, vale mesmo com --allow-root).
- Zero Discovery (R-054) preservado; Blind Evaluation: avaliador recebe só {prompt_text, system_prompt}.
- Artefatos: `diagnostic-<run_id>.yaml` e `.md` determinísticos (`newline="\n"`, `sort_keys=True`), em .github/agents/evals/synthetic/ ou .synth/.
- Testes via scripts/dev/py-test.sh (confirmar sintaxe real --project em B1-03); pytest 100% verde, incluindo suíte existente de routing/agent-audit.
- Prompt injection: keywords/regras do grafo como dados inertes; sanitizar_prompt em todas as seeds graph-seeded.


- B2-03 dividido em B2-03a (código CLI, `@python-developer`) e B2-03b (testes, `@python-test-engineer`) para separar produção e teste.
- Teste E2E offline em `tests/synth_e2e/` (um pipeline com `--graph-seeding gaps` + `synth-diagnose`, sem LLM) sob `@python-test-engineer`, incluído em B3-04.

### Checklist de Execução Técnica (GFM Unificado)
Ordem: B1 → B2 → B3 (um commit por bloco; rollback B3→B2→B1).

**B1 — Fundação (ingestão + schema v2)**
- [x] B1-01 Criar synth/routing_graph.py (ACL sobre carregar_grafo; RotaGrafo, GrafoSnapshot, rotas_validas, edge_id SHA-256 determinístico invariante a reordenação, colisão falha explicitamente, resolver_aresta) `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] B1-02 Evoluir schema.sql + storage.py para v2 (migração atômica idempotente, sem executescript; banco novo nasce em user_version 2) `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] B1-03 Testes test_edge_id.py, test_store_migration.py, criar `tools/headless-governance-runner/tests/synth_unit/test_routing_graph.py` (`test_routing_graph.py::test_carregar_grafo_usa_schema_empacotado_fixo` — caminho_schema fixo do pacote, sem descoberta dinâmica nem parâmetro do usuário); ajustar test_storage.py ao v2 `{paralelizavel: false, responsavel: "@python-test-engineer"}`

**B2 — Geração guiada pelo grafo**
- [x] B2-01 Criar synth/seeds.py (SeedRef, calcular_cobertura_golden, gerar_seeds_grafo; campos opcionais em GoldenSeed) `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] B2-02 Adaptar taxonomy.alocar_estratos, generator.py (propaga seed_source/graph_edge_id/routing_graph_sha256) e use_cases.executar_synth_generate preservando blind eval `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] B2-03a Flags CLI --routing-graph, --graph-seeding, --graph-min-coverage em cli.py `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] B2-03b Testes test_graph_seeding.py e test_blind_eval.py `{paralelizavel: false, responsavel: "@python-test-engineer"}`

**B3 — Oráculo, diagnóstico e guardas**
- [x] B3-01 Criar synth/diagnostics.py (métricas, matriz, órfãs, colisões, divergência router.md, sugestões; offline) `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] B3-02 Criar synth/diagnostic_exporter.py (YAML+MD bit-a-bit, guardas de path, denylist imutável, escape de | ` < e truncamento 240) `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] B3-03 use_cases.executar_synth_diagnose + --use-case synth-diagnose em cli.py (exit codes 3/4/5; zero chamadas LLM) `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] B3-04 Testes test_diagnose.py, test_path_guards.py, E2E offline em tests/synth_e2e/ (um pipeline com --graph-seeding gaps + synth-diagnose, sem LLM); atualizar README.md `{paralelizavel: false, responsavel: "@python-test-engineer"}`

### Rastreio Critérios de Aceite (base: tools/headless-governance-runner/tests/synth_unit/)
- CA-01 seeding off por padrão: test_graph_seeding.py::test_default_seeding_off_gera_zero_prompts_do_grafo, ::test_seeding_gaps_so_cobre_arestas_sem_prompt (B2-01..03b)
- CA-02 exclusão de arestas: test_graph_seeding.py::test_health_check_e_mandatory_pre_step_excluidas, ::test_security_gate_incluida (B1-01, B2-01)
- CA-03 edge_id determinístico: test_edge_id.py::test_edge_id_invariante_a_reordenacao_do_yaml, ::test_colisao_edge_id_falha_explicitamente (B1-01, B1-03)
- CA-04 migração v1→v2: test_store_migration.py::test_migracao_v1_v2_adiciona_colunas_antes_do_indice, ::test_migracao_rollback_em_falha_preserva_v1, ::test_migracao_idempotente, ::test_banco_novo_nasce_em_user_version_2 (B1-02, B1-03)
- CA-05 diagnóstico determinístico/offline: test_diagnose.py::test_diagnostic_yaml_md_bit_a_bit_identicos_em_duas_execucoes, ::test_synth_diagnose_zero_chamadas_llm, ::test_newline_lf_no_windows (B3-01..04)
- CA-06 blind eval: test_blind_eval.py::test_synth_eval_seed_routing_graph_recebe_apenas_prompt_text_e_system_prompt (B2-02, B2-03b)
- CA-07 guardas: test_path_guards.py::test_out_path_traversal_rejeitado, ::test_routing_graph_fora_do_repo_rejeitado, ::test_allow_root_nao_permite_sobrescrever_arquivos_protegidos, test_routing_graph.py::test_carregar_grafo_usa_schema_empacotado_fixo (B1-03, B3-02, B3-04)

### Riscos e Rollback
- RK-G1 contagens Golden: graph-seeding opt-in; verificar com test_golden.py. RK-G2 ALTER/índice SQLite: migração atômica. RK-G3 vazamento do grafo ao avaliador: CA-06. Rollback: git revert B3→B2→B1; .cache/routing_synth_history.db é descartável.

### 🔒 Checklist Defensivo Pré-Code-Review
- [x] Sanitização e validação de inputs em todas as bordas expostas (--out, --routing-graph, keywords do grafo)
- [x] Ausência de segredos, tokens ou dados sensíveis em hardcode e logging seguro sem PII
- [x] Tratamento defensivo de exceções e controle de autorização/permissões validado (denylist imutável)
- [x] Zero Discovery (R-054): schema do grafo carregado via caminho_schema fixo do pacote (`test_routing_graph.py::test_carregar_grafo_usa_schema_empacotado_fixo`), sem descoberta dinâmica nem parâmetro do usuário
- [x] Testes unitários/integração defensivos atendendo aos quality gates (scripts/dev/py-test.sh, pytest 100% verde)
