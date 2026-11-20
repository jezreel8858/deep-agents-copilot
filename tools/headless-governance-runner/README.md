# headless-governance-runner

Pacote Python `governance_runner` — motor determinístico de roteamento/governança
(`routing/`), pipeline sintético de avaliação de roteamento e utilidade A/B de skills (`synth/`),
e runner headless de auditoria/governança para GitHub Actions (`runner/`, `reporters/`, `telemetry/`).

> **Escopo e contratos completos**: ver
> [`docs/architecture/BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md`](../../docs/architecture/BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md)
> (arquitetura, §5.2 estrutura de diretórios, §6 contratos de classes/funções, §7 testes determinísticos).
>
> **Plano de execução e status das subtasks**: ver
> [`docs/architecture/PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md`](../../docs/architecture/PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md)
> (Bloco A — Eixo 2 `routing/`, Bloco B — Eixo 3 `tests/routing_unit/`).

## Estrutura de Módulos

- `routing/`: validação canônica de `routing-graph.yaml` (`graph_loader.py`), máquina de estados e detecção de drift.
- `synth/`: pipeline sintético de geração, avaliação cega, avaliação A/B de utilidade de skills (P5), curadoria Silver e diagnóstico offline guiado pelo grafo (`routing_graph.py`, `seeds.py`, `taxonomy.py`, `generator.py`, `evaluator.py`, `diagnostics.py`, `diagnostic_exporter.py`, `storage.py`).
- `runner/`, `reporters/`, `telemetry/`: adaptador Copilot SDK headless, controle de orçamento e telemetria OTel fail-open.

## Instalação (modo editável, para desenvolvimento e uso com GitHub Copilot SDK)

> **Nota**: No PyPI, o pacote oficial `github-copilot-sdk` encontra-se na série `0.x` (*Technical Preview*). Instale o pacote local com o extra `[dev]` e, em seguida, instale `github-copilot-sdk`:

**PowerShell:**
```powershell
python -m pip install -e "tools/headless-governance-runner[dev]"
python -m pip install github-copilot-sdk
```

**Windows `cmd.exe`:**
```cmd
python -m pip install -e "tools/headless-governance-runner[dev]"
python -m pip install github-copilot-sdk
```

**Linux / macOS (`bash`):**
```bash
python -m pip install -e "tools/headless-governance-runner[dev]"
python -m pip install github-copilot-sdk
```

## Modos `synth-*` (geração, avaliação, utilidade A/B de skills e diagnóstico sintético)

- `synth-generate`:
  - `--generator-mode {sdk,template}` (alias `--generator`)
  - `--graph-seeding {off,gaps,all}` (default `off`), `--routing-graph PATH`, `--graph-min-coverage INT` (default `3`)
  - `--skill-seeding {off,gaps,all}` (default `off`), `--skills <s1,s2,...>`, `--skill-cases PATH` (default `tests/evals/skill_ab_cases.yaml`), `--include-skill-gaps`
- `synth-eval`, `synth-export`, `synth-promote`, `synth-diagnose`.
- `synth-skill-ab` (Avaliação A/B de Utilidade de Skills — Treatment vs. Baseline — P5):
  - Flags: `--generator-mode {template,sdk}` (default `template` para avaliação determinística por rubrica), `--skill-cases PATH` (default `tests/evals/skill_ab_cases.yaml`), `--skills <s1,s2,...>`, `--include-skill-gaps`, `--max-premium-requests INT` (exigido apenas em `--generator-mode sdk`).
  - Modo `template` (100% offline e determinístico por rubrica, 0 premium requests): avalia `baseline_output` vs. `baseline_output + SKILL.md (+ references/*)` contra `required_clauses` e `forbidden_antipatterns`, calculando `delta_utility = treatment_score - baseline_score`, sinalizando skills redundantes (`delta_utility <= 0.0`) e persistindo na tabela `synth_skill_ab_evals` (SQLite schema `v4`).
  - Modo `sdk`: executa pares Baseline (sem skill) e Treatment (com skill injetada) via Copilot SDK respeitando o teto de `--max-premium-requests` (2 requests por caso) e `COPILOT_SDK_TOKEN`.
- `--base` é obrigatório apenas em `agent-audit`.
- Orçamento (`--max-premium-requests` ou `GOV_MAX_PREMIUM_REQUESTS`, inteiro `> 0`) é obrigatório em `synth-eval`, `synth-generate --generator-mode sdk` e `synth-skill-ab --generator-mode sdk`; validado antes de qualquer token/chamada SDK (exit code `2`).
- Autenticação via variável de ambiente `COPILOT_SDK_TOKEN` (exigida em `synth-eval`, `synth-generate --generator-mode sdk`, `synth-skill-ab --generator-mode sdk` e `agent-audit`).
- Blind Evaluation: `expected_route`, `graph_edge_id`, `seed_source` e metadados do `routing-graph.yaml` nunca são enviados ao modelo avaliado; o avaliador recebe apenas `{prompt_text, system_prompt}` e compara após a resposta (`matched`, `mismatched`, `unparseable`, `error`).
- Diagnóstico offline (`--use-case synth-diagnose --eval-run-id <RUN_ID>`):
  - 100% determinístico e offline (0 chamadas LLM / 0 premium requests).
  - Cruza `synth_evaluations`, `synth_prompts`, `routing-graph.yaml`, `.github/agents/agent-router.agent.md`, os resultados de `synth_skill_ab_evals` (`--skill-ab-run-id <RUN_ID>` ou automaticamente o último `skill_ab` run concluído) e a cobertura de `.github/skills/*/SKILL.md` frente a `tests/evals/skill_ab_cases.yaml`.
  - Emite sugestões automáticas `SKILL_REDUNDANTE` (para poda/refatoração) e `LACUNA_COBERTURA_SKILL` (skills sem caso A/B cadastrado), gerando `diagnostic-<eval_run_id>.yaml` e `diagnostic-<eval_run_id>.md` em `.github/agents/evals/synthetic/` (ou `.synth/`).
  - Exit codes: `0` sucesso, `3` `eval_run_id` inexistente/não-eval, `4` `routing-graph` inválido, `5` violação de guarda de path/denylist.
- Fluxo de curadoria: `synth-export` → Silver em `.github/agents/evals/synthetic/casos-roteamento-silver-*.yaml` → revisão humana em cada item de `casos` (`silver.review_status: approved` + `silver.corrected_route`) → `synth-promote --confirm` gera `.github/agents/evals/synthetic/promoted-<run_id>.yaml` → Pull Request manual. Os arquivos protegidos (`.github/agents/routing-graph.yaml`, `.github/agents/agent-router.agent.md` e `.github/agents/evals/casos-roteamento.yaml`) estão em denylist imutável e nunca são alterados pelo pipeline.

### Exemplos rápidos (`synth-skill-ab` + `synth-diagnose`)

```bash
# 1. Executar Eval A/B determinístico (rubric, 0 premium requests) e persistir no SQLite
python -m governance_runner.cli --use-case synth-skill-ab --generator-mode template --db .cache/synth.db

# 2. Gerar seeds sintéticos cobrindo lacunas de skills ainda sem caso A/B
python -m governance_runner.cli --use-case synth-generate --generator-mode template --skill-seeding gaps --db .cache/synth.db

# 3. Rodar diagnóstico unificado (roteamento + última rodada synth-skill-ab + cobertura de skills)
python -m governance_runner.cli --use-case synth-diagnose --eval-run-id <EVAL_RUN_ID> --db .cache/synth.db
```

> **Guia Completo do Usuário (`synth-*` + GitHub Copilot SDK + SQLite)**: consulte [`docs/guides/synth-routing-eval-copilot-sdk-guide.md`](../../docs/guides/synth-routing-eval-copilot-sdk-guide.md) para instruções detalhadas de instalação, configuração de `COPILOT_SDK_TOKEN`, valores válidos de `--targets` e `--dimensions`, receitas em PowerShell, Windows `cmd.exe` e `bash`, queries SQLite reais e troubleshooting.
