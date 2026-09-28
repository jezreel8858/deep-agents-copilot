# Plano de Decomposição — Runner Headless Copilot SDK (Governança deep-agents-copilot)

> **Fonte normativa**: [BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md](./BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md)  
> **Autor**: feature-planner · **Status**: PROPOSTO (aguarda aprovação humana para início da Fase PoC)  
> **Escopo impactado**: `tools/headless-governance-runner/{routing,runner,reporters,telemetry}/`, `tests/routing_unit/` (15 arquivos), `.github/workflows/governance-*.yml` (3 workflows), `routing-graph.schema.json`. Consumidores existentes de `routing-graph.yaml`/`catalog.yaml` permanecem intocados — mudança é somente aditiva.

---

## 1. Visão Geral e Estrutura de Execução

Este documento formaliza a quebra operacional em **46 subtasks** para implementação progressiva do Runner Headless Copilot SDK, distribuídas em três fases consecutivas (**PoC**, **Piloto** e **Produção**). Cada fase é protegida por um Quality Gate mandatório.

### Convenções de Paralelismo
- **[S] (Serial)**: Execução estritamente sequencial devido a dependência causal direta.
- **[P] (Paralelo)**: Execução elegível a paralelismo sem compartilhamento de estado mutável ou concorrência de escrita no mesmo arquivo.

---

## 2. Fase PoC (Proof of Concept)

Objetivo: Validar isoladamente o motor de roteamento (`routing/`), cobrir exaustivamente com testes unitários (`tests/routing_unit/`), erguer o runner mínimo read-only com o caso `agent-auditor` e responder empiricamente à questão crítica **Q-01** em CI real.

### 2.1 Bloco A — Eixo 2: Módulo `routing/` (Pré-requisito Fundamental)

| # | Subtask | P/S | Responsável | Depende de | Definition of Done (DoD) | Status |
|---|---------|:---:|-------------|------------|--------------------------|:---:|
| 1 | Scaffolding `tools/headless-governance-runner/{routing,runner,reporters,telemetry}/` + `tests/routing_unit/` | [S] | @python-router → @python-feature-developer | nenhuma | Estrutura de pastas idêntica à §5.2 do Blueprint; `pytest --collect-only` roda sem erro de importação. | ✅ |
| 2 | `graph_loader.py` — parser `routing-graph.yaml` + `routing-graph.schema.json` | [S] | @python-feature-developer | 1 | Carrega os 37 nós e 42 arestas sem exceção; valida contra schema JSON; falha explicitamente em YAML inválido. | ✅ |
| 3 | `state_machine.py` — 9 workflows canônicos + guard clauses (R-050) | [S] | @python-feature-developer | 2 | Todas as transições dos 9 workflows mapeadas; transição ilegal levanta exceção tipada. | ✅ |
| 4 | `drift.py` — detecção de deriva de intenção (R-042) | [P] | @python-feature-developer | 3 | Zero falso-negativo nos fixtures canônicos de sticky-session simulada. | ✅ |
| 5 | `router.py` — roteamento rule-based + política de cascata (0.9/0.7/0.5/0.0) | [P] | @python-feature-developer | 3 | Reproduz fixture canon-001 byte-a-byte; thresholds aplicados corretamente. | ✅ |
| 6 | `handoff.py` — contrato de payload entre agentes | [P] | @python-feature-developer | 3 | Payload validado contra `handoff-governance/SKILL.md`; rejeita payload malformado. | ✅ |
| 7 | Convergência Eixo 2 + smoke test local | [S] | @python-feature-developer | 4, 5, 6 | Pacote `routing/` importável; smoke test end-to-end (sem SDK) passa localmente. | ✅ |

> *Nota de Paralelismo*: As subtasks 4, 5 e 6 operam em paralelo ([P]) por atuarem em arquivos distintos e isolados, sem estado mutável compartilhado.

> ✅ **Bloco A (Eixo 2) concluído**: subtasks 1-7 finalizadas — `routing/` compilado, testado (96 casos verdes em `tests/routing_unit`, incluindo `test_smoke_end_to_end.py`) e com `mypy --strict` limpo. Fachada pública consolidada em `governance_runner/routing/__init__.py` (`__all__` explícito).

### 2.2 Bloco B — Eixo 3: Suíte `tests/routing_unit/` (13 TC + 2 Arquivos Adicionais)

| # | Subtask | P/S | Responsável | Depende de | Nível | Definition of Done (DoD) | Status |
|---|---------|:---:|-------------|------------|:-----:|--------------------------|:------:|
| 8 | `test_TC01_direct_match.py` | [P] | @python-unit-test-writer | 7 | N1 | Cobre caso isolado; `pytest tests/routing_unit -k TC01` verde; zero rede/zero SDK real. | ✅ |
| 9 | `test_TC02_cascade_thresholds.py` | [P] | @python-unit-test-writer | 7 | N1 | Cobre thresholds da cascata; passa isolado; zero rede/zero SDK real. | ✅ |
| 10 | `test_TC03_intent_drift_trigger.py` | [P] | @python-unit-test-writer | 7 | N1 | Valida disparo de deriva de intenção (R-042); passa isolado; zero rede. | ✅ |
| 11 | `test_TC04_fallback_cascade.py` | [P] | @python-unit-test-writer | 7 | N1 | Valida caminho completo de fallback; passa isolado; zero rede. | ✅ |
| 12 | `test_TC05_state_machine_valid_transitions.py` | [P] | @python-unit-test-writer | 7 | N1 | Valida transições lícitas dos 9 workflows; passa isolado. | ✅ |
| 13 | `test_TC06_state_machine_illegal_transition.py` | [P] | @python-unit-test-writer | 7 | N1 | Valida bloqueio estrito de transições ilegais com exceção tipada. | ✅ |
| 14 | `test_TC07_graph_schema_validation.py` | [P] | @python-unit-test-writer | 7, 21 | N1/N2 | Validação contra JSON schema; cobertura estrita de anomalias sintáticas. | ✅ |
| 15 | `test_graph_consistency_cross_ref.py` | [P] | @python-unit-test-writer | 7 | N1 | Valida consistência de nós e referências cruzadas no grafo. | ✅ |
| 16 | `test_state_machine_idempotency.py` | [P] | @python-unit-test-writer | 7 | N1 | Garante idempotência de execução e despacho na máquina de estados. | ✅ |
| 17 | `test_TC08_cache_hit_ratio.py` | [P] | @python-unit-test-writer | 7 | N1 | Valida métricas e taxa de acerto de cache de roteamento. | ✅ |
| 18 | Consolidação N1 — Suíte completa 100% verde | [S] | @python-unit-test-writer (QA) | 8-17 | N1 | Suíte completa 100% verde; zero flakiness comprovado em 10 execuções consecutivas. | ✅ |

> ✅ **Bloco B (Eixo 3) concluído**: subtasks 8-18 finalizadas — suíte canônica de testes unitários N1 consolidada em 10 arquivos (`test_TC01` a `test_TC08` + 2 testes de gap e `test_smoke_end_to_end.py`), 100% verde com zero flakiness validado em 10 execuções consecutivas.

### 2.3 Bloco C — Runner Mínimo + 1 Workflow (`agent-auditor`, Read-Only)

| # | Subtask | P/S | Responsável | Depende de | Nível | Definition of Done (DoD) |
|---|---------|:---:|-------------|------------|:-----:|--------------------------|
| 19 | Runner mínimo `runner/` — caso `agent-auditor` (read-only), invoca `routing/` | [S] | @python-feature-developer | 7 | N2 | Executa localmente contra PR fixture; saída conforme §5.4; conclusão sempre `neutral`. | ✅ |
| 20 | `test_TC09_token_expiration_mock.py` | [P] | @python-integration-test-writer | 19 | N2 | Mock de expiração de token em tempo de execução validado. | ✅ |
| 21 | `test_TC10_exception_exit_code.py` | [P] | @python-integration-test-writer | 19 | N2 | Mapeamento estrito de códigos de saída sob exceção não tratada. | ✅ |
| 22 | `test_TC11_prompt_injection_sanitization.py` | [P] | @python-integration-test-writer | 19 | N2 | Sanitização e neutralização de payloads com injeção de prompt. | ✅ |
| 23 | `test_TC13_otel_collector_unavailable.py` | [P] | @python-integration-test-writer | 19 | N2 | Resiliência e graceful degradation quando o coletor OTel estiver indisponível. | ✅ |
| 24 | `test_TC12_handoff_contract.py` | [S] | @python-integration-test-writer | 6, 19 | N3 | Validação de payload completo de handoff contra `handoff-governance/SKILL.md`. | ✅ |
| 25 | Workflow `governance-agent-audit.yml` (PR, Checks API neutral, sticky comment) | [S] | Orquestrador raiz (edição direta) | 19 | CI | `.github/workflows/governance-agent-audit.yml` criado e validado sintaticamente (YAML parse OK). | ✅ |
| 26 | Validação real de Q-01 em CI (`GITHUB_TOKEN` + `copilot-requests:write` ou BYOK) | [S] | Humano (requer secrets reais + push a PR real) | 25 | CI | Execução real autentica sem erro no GitHub Actions; TC-09 validado fora de mock. | ✅ **CONCLUÍDO** (2026-09-28, PR #55, run `governance-agent-audit.yml` #6/id `36405112477` — auth via PAT dedicado `COPILOT_SDK_TOKEN`, `veredito='neutral'`, custo `{premium_requests:1, turnos:1}`, fail-open OTel confirmado em CI real. Ver Seção 7 de `RUNBOOK_VALIDACAO_Q01_COPILOT_SDK_CI.md`. **Achado adicional corrigido na mesma sessão**: hook `preToolUse` de `.github/hooks/context-mode.json` bloqueava categoricamente todo tool call em ambientes sem o binário `context-mode` — guarda defensiva aplicada nas 12 entradas de hook.) |

### 2.4 Gate de Promoção PoC → Piloto

| # | Subtask / Marco | P/S | Responsável | Depende de | Definition of Done (DoD) |
|---|-----------------|:---:|-------------|------------|--------------------------|
| 27 | **Gate de Qualidade PoC → Piloto** | [S] | requester + QA governança | 18, 20-24, 26 | `tests/routing_unit/` 100% verde · 13 TC + 2 extras aprovados · Q-01 resolvida e comprovada em CI real · zero flakiness em 10 execuções. | ✅ **APROVADO** (2026-09-28) — 161 testes verdes, 0 flakiness, 0 erros estáticos (`mypy --strict`), Q-01 validado empiricamente em CI real (subtask 26). Pendências fechadas na mesma sessão: (a) wiring de `--report checks,pr-comment` em `cli.py::main()` implementado (canais fail-open, nunca alteram o exit code da auditoria); (b) gatilho do workflow restrito a PR `develop→main` com feature-flag opt-in via `vars.GOVERNANCE_AGENT_AUDIT_ENABLED` (custo/credits sob controle explícito). Única pendência remanescente, não bloqueante: confirmação manual do painel de billing/quota da conta (ação humana fora do IDE). |

---

## 3. Fase Piloto

Objetivo: Expandir o runner com o segundo workflow (`code-review`), instrumentar telemetria OTel corporativa (Langfuse), integrar quality gate contínuo e validar soft gate de branch protection com medições de cobertura e mutação.

| # | Subtask | P/S | Responsável | Depende de | Definition of Done (DoD) |
|---|---------|:---:|-------------|------------|--------------------------|
| 28 | Expandir runner com 2º caso de uso: `code-review` | [S] | @python-feature-developer | 27 | Runner suporta simultaneamente `agent-auditor` e `code-review` sem qualquer regressão. |
| 29 | Workflow `governance-code-review.yml` (push) | [S] | @devops-router | 28 | Dispara em eventos de push; gera Checks API equivalente com feedback estruturado. |
| 30 | Testes N2 adicionais (`code-review`) | [P] | @python-integration-test-writer | 28 | Cobre falhas controladas de mock do SDK Copilot e chamadas CLI `gh`. |
| 31 | Testes N3 de contrato de handoff (`code-review`) | [P] | @python-integration-test-writer | 28 | Payload de handoff estritamente validado contra o contrato de governança. |
| 32 | Integrar `tests/routing_unit/` completo (N1+N2+N3) em `routing-quality-gate.yml` | [S] | @devops-router | 30, 31 | Todos os níveis de teste executam no pipeline de CI sem requerer novo toolchain. |
| 33 | Instrumentar spans `deep_agents.*` (OTel) via `telemetry/` | [S] | @python-feature-developer | 27 | Spans OTel exportados com sucesso e verificados no dashboard Langfuse. |
| 34 | Convergência com `workflow_eval_simulator.py` e blast radius | [S] | @python-feature-developer | 28, 33 | Zero regressão comprovada em simuladores e nós consumidores (resultado COMPATIBLE). |
| 35 | Gate soft na branch protection | [S] | @devops-router | 32 | `routing_unit` obrigatório no PR; auditoria semântica LLM não bloqueante. |
| 36 | Medir cobertura ≥95% + taxa de falso-positivo <10% | [S] | QA governança | 34, 35 | Métricas coletadas em regime real e consolidadas em relatório formal. |
| 37 | Mutation testing nos 4 módulos críticos (kill rate ≥80%) | [P] | @python-unit-test-writer | 27 | Relatório de mutação gerado com taxa de eliminação (kill rate) ≥80%. |
| 38 | Execução E2E em sandbox real (≥1 execução completa) | [P] | QA governança | 26 | Execução ponta a ponta concluída com sucesso em ambiente real, com logs auditados. |

### 3.1 Gate de Promoção Piloto → Produção

| # | Subtask / Marco | P/S | Responsável | Depende de | Definition of Done (DoD) |
|---|-----------------|:---:|-------------|------------|--------------------------|
| 39 | **Gate de Qualidade Piloto → Produção** | [S] | requester + QA governança | 36, 37, 38 | Cobertura ≥95% em linhas e 100% em branches · mutation kill rate ≥80% · taxa de falsos-positivos <10% · ≥1 E2E real auditado · 4 semanas contínuas em regime estável. |

---

## 4. Fase Produção

Objetivo: Habilitar o terceiro caso de uso (`repo-hygiene-auditor`), automação semanal, controle financeiro de chamadas premium via alertas em dashboard, enforcement de branch protection para achados críticos e publicação de runbook de rollback.

| # | Subtask | P/S | Responsável | Depende de | Definition of Done (DoD) |
|---|---------|:---:|-------------|------------|--------------------------|
| 40 | Expandir runner com 3º caso de uso: `repo-hygiene-auditor` | [S] | @python-feature-developer | 39 | Runner suporta os 3 casos de uso canônicos de governança sem regressões. |
| 41 | Workflow `governance-hygiene-schedule.yml` (schedule semanal) | [S] | @devops-router | 40 | Disparo semanal automatizado gerando relatório consolidado de higiene. |
| 42 | Dashboard de custo de requisições premium + alerta de teto em 80% | [S] | @python-feature-developer / observability | 33 | Dashboard apresenta total semanal de tokens/custo; alerta dispara ao atingir 80% da quota. |
| 43 | Gate hard na branch protection (bloqueia merge exclusivamente em achados `critical`) | [S] | @devops-router | 41, 42 | Bloqueia efetivamente o merge de PRs que apresentem apontamentos com severidade `critical`. |
| 44 | Runbook de rollback operacional | [S] | @docs-engineer | 43 | Documento técnico `.md` contendo passos de reversão manual testados e validados. |
| 45 | Operação contínua estável por 4 semanas + orçamento sob controle | [S] | QA governança | 43 | Log de 4 semanas sem incidentes de infraestrutura; consumo medido estritamente abaixo do teto orçamentário. |

### 4.1 Gate de Conclusão Produção

| # | Subtask / Marco | P/S | Responsável | Depende de | Definition of Done (DoD) |
|---|-----------------|:---:|-------------|------------|--------------------------|
| 46 | **Gate Final de Conclusão** | [S] | requester | 44, 45 | 4 semanas de estabilidade atestada · orçamento validado dentro do limite estabelecido · runbook de rollback publicado e homologado. |

---

## 5. Grafo de Precedência

O fluxo de dependências causais entre as 46 subtasks é reproduzido a seguir:

```
1 → 2 → 3 → {4,5,6} → 7 → {8..17 [P]} → 18 → 19 → {20,21,22,23,24[dep 6,19]} → 25 → 26 → 27 (GATE)
27 → 28 → {29, 30, 31} → 32 → 35 → 36 ─┐
27 → 33 → 34 (dep 28,33)               ├→ 39 (GATE)
27 → 37 [P] ───────────────────────────┤
26 → 38 [P] ───────────────────────────┘
39 → 40 → 41 → 43 (dep 41,42)
27 → 33 → 42
43 → 44 → 45 → 46 (GATE)
```

---

## 6. Critérios Gerais de Conclusão (DoD Geral)

1. **Aprovação Formal dos 3 Quality Gates**: Os marcos 27 (PoC→Piloto), 39 (Piloto→Produção) e 46 (Conclusão) devem ser explicitamente validados com evidências objetivas arquivadas.
2. **Zero Regressão de Consumidores Legados**: Todos os nós existentes que consom `routing-graph.yaml` e `catalog.yaml` devem permanecer 100% funcionais em todas as fases.
3. **Validação Conclusiva de Q-01 em CI Real**: Nenhuma promoção para a Fase Piloto é autorizada sem que a autenticação de GitHub Actions com permissões de Copilot SDK seja comprovada em ambiente real de pipeline (não apenas mocks locais).
4. **Isolamento Concorrente**: Nenhuma subtask marcada como `[P]` deve competir por escrita ou alterar simultaneamente o mesmo arquivo ou recurso mutável de outra subtask concorrente no mesmo bloco.

---

## 7. Próximo Passo Mínimo

Aguardar aprovação humana explícita para início da **Subtask 1** (Scaffolding), cuja execução será delegada via handoff:
`@agent-router` → `@python-router` → `@python-feature-developer`.
