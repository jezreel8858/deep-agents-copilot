# Checkpoint — Runner Headless Copilot SDK (Governança deep-agents-copilot)

> **Documento de retomada**: registra o estado exato em que o trabalho foi pausado, para que a sessão seguinte (humana ou de IA) possa continuar sem precisar reconstruir o contexto do zero.
>
> **Data do checkpoint**: 2026-09-28
> **Documentos normativos relacionados** (ler nesta ordem ao retomar):
> 1. [`BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md`](./BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md) — arquitetura, C4, decisão MADR.
> 2. [`PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md`](./PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md) — as 46 subtasks, DAG de precedência, gates.
> 3. [`RUNBOOK_VALIDACAO_Q01_COPILOT_SDK_CI.md`](./RUNBOOK_VALIDACAO_Q01_COPILOT_SDK_CI.md) — evidências reais da validação de autenticação em CI (Seção 7 preenchida).
> 4. Este documento — snapshot do estado + próximo passo mínimo.

---

## 1. Estado Geral

| Fase | Status |
|---|---|
| **PoC (subtasks 1-27)** | ✅ **100% concluída** — Gate 27 (PoC → Piloto) **APROVADO** em 2026-09-28 |
| **Piloto (subtasks 28-39)** | 🔲 Não iniciada |
| **Produção (subtasks 40-46)** | 🔲 Não iniciada |

**Decisão de continuidade tomada nesta sessão**: aguardar um período de observação de custo/comportamento real do `agent-audit` em PRs `develop→main` reais antes de decidir se/quando avançar para a Fase Piloto (que adiciona um 2º workflow + telemetria real, aumentando a superfície de consumo de créditos). **Nenhuma subtask da Fase Piloto foi iniciada.**

---

## 2. O Que Foi Implementado e Validado (Fase PoC)

### 2.1 Motor determinístico de roteamento (`tools/headless-governance-runner/src/governance_runner/routing/`)
- `model.py`, `graph_loader.py`, `state_machine.py`, `drift.py`, `router.py`, `handoff.py` — 100% implementados e testados.
- Codifica em Python puro as regras R-037/R-042/R-050/R-052/R-064 como state machine real (antes só existiam em Markdown/prompt).

### 2.2 Runner headless (`tools/headless-governance-runner/src/governance_runner/runner/`)
- `sdk_adapter.py` — **integração REAL** com o Copilot SDK (pacote PyPI `github-copilot-sdk`, módulo `copilot`), classe `_ClienteSDKReal` com ponte síncrona sobre a API assíncrona, timeout de segurança (120s), detecção heurística de erro de autenticação.
- `budget.py` — teto de premium requests (`GOV_MAX_PREMIUM_REQUESTS`) + teto de 5 turnos (R-060).
- `use_cases.py` — caso de uso `agent-audit` (read-only), sempre conclui `neutral` na fase PoC.
- `cli.py` — entrypoint `governance-runner`, **wiring de reporters fechado nesta sessão** (`--report checks,pr-comment` agora publica de verdade, fail-open).

### 2.3 Reporters (`tools/headless-governance-runner/src/governance_runner/reporters/`)
- `checks.py` (Checks API) e `pr_comment.py` (comentário sticky) — implementados e **agora invocados** por `cli.py::main()`.
- `artifact.py` — ainda placeholder, não usado no caso de uso atual.

### 2.4 Telemetria (`tools/headless-governance-runner/src/governance_runner/telemetry/otel.py`)
- Fail-open confirmado **em CI real** (não só em mock): OTel Collector retornou 404 e a execução continuou normalmente com `trace_id='telemetry_unavailable'`.

### 2.5 Suíte de testes
- **161 testes** (110 `tests/routing_unit/` + 51 `tests/runner_unit/`), 100% verdes, **zero flakiness** (10 execuções consecutivas), `mypy --strict` limpo em 21 arquivos-fonte.

### 2.6 CI/CD (`.github/workflows/governance-agent-audit.yml`)
- Dispara **exclusivamente** em PR `develop → main` tocando `.github/{agents,skills,prompts}/**` (filtro duplo: `branches: [main]` + `head.ref == 'develop'`).
- **Feature-flag opt-in**: variável de repositório `vars.GOVERNANCE_AGENT_AUDIT_ENABLED` — ausente/`false` = job nem inicia (zero custo). Ativar em *Settings → Secrets and variables → Actions → Variables*.
- Passo `python -m copilot download-runtime` (exigido pelo SDK real).
- `permissions.copilot-requests: write` (não `write-all` — valor inválido por-escopo).

### 2.7 Correção crítica de governança descoberta pela própria execução real
- `.github/hooks/context-mode.json`: os 12 hooks agora têm guarda defensiva (`command -v context-mode || exit 0` / `Get-Command`) — antes, qualquer ambiente sem o binário `context-mode` instalado (como o runner de CI) tinha **todo tool call bloqueado** pelo hook `preToolUse` com erro.

### 2.8 Validação empírica do Q-01 (autenticação Copilot SDK em CI)
- PR de teste #55 (`test/poc-q01-copilot-auth`), run `governance-agent-audit.yml` #6 / run id `36405112477`.
- Opção testada: **B** — PAT dedicado (`COPILOT_SDK_TOKEN`), escopo "Copilot Requests: Read-only".
- Resultado: ✅ autenticação bem-sucedida, `veredito='neutral'`, custo `{premium_requests:1, turnos:1}` (dentro do teto de 15).
- Evidência completa registrada na Seção 7 de `RUNBOOK_VALIDACAO_Q01_COPILOT_SDK_CI.md`.

---

## 3. Arquivos Alterados Nesta Sessão (Ainda Não Commitados)

Por governança R-031, nenhum commit/push foi executado autonomamente. **Ação pendente do usuário**: aplicar os commits abaixo (em blocos, na ordem em que foram gerados) antes de prosseguir.

| Bloco | Arquivos | Mensagem de commit sugerida |
|---|---|---|
| 1 | `.github/workflows/governance-agent-audit.yml` (fix `write-all`→`write`) | `fix(ci): corrigir valor invalido de permissao copilot-requests` |
| 2 | `tools/headless-governance-runner/src/governance_runner/cli.py` (fix path `parents[3]`→`parents[4]`) | `fix(runner): corrige resolucao de path do routing-graph.yaml` |
| 3 | `.github/workflows/governance-agent-audit.yml` + `tools/headless-governance-runner/{pyproject.toml,src/governance_runner/runner/sdk_adapter.py}` (integração real do SDK) | `fix(runner): implementa integracao real com Copilot SDK` |
| 4 | `.github/hooks/context-mode.json` + `CHANGELOG.md` + `docs/architecture/{PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md,RUNBOOK_VALIDACAO_Q01_COPILOT_SDK_CI.md}` (fechamento Q-01 + fix hook) | `fix(hooks): guarda defensiva contra binario ausente + docs(governance): registra resolucao do Q-01` |
| 5 | `.github/workflows/governance-agent-audit.yml` + `tools/headless-governance-runner/src/governance_runner/cli.py` + `CHANGELOG.md` + `docs/architecture/PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md` (restrição develop→main + feature-flag + wiring reporters) | `feat(ci): restringe governance-agent-audit a PR develop->main + feature-flag opt-in + wiring de reporters` |

> **Nota**: alguns arquivos aparecem em mais de um bloco porque foram editados incrementalmente ao longo da sessão. Se preferir, pode consolidar tudo em um único commit — o importante é que o estado final em disco já reflete todas as correções acima.

**Verificar antes de commitar**:
```bash
git --no-pager status --short
git --no-pager diff --stat
```

---

## 4. Gaps Conhecidos (Não Bloqueantes)

1. **Confirmação manual do painel de billing/quota** da conta associada ao PAT `COPILOT_SDK_TOKEN` — ação humana fora do escopo de automação, não fechada ainda.
2. **PR de teste #55** (`test/poc-q01-copilot-auth`) segue aberto — decidir entre: (a) fechar sem merge (procedimento de rollback na Seção 8 do runbook), ou (b) mergear como parte do histórico de validação. Como o workflow agora exige `head.ref == 'develop'`, esse PR específico pode não satisfazer mais o gatilho dependendo de qual era sua branch base real — revisar antes de decidir.
3. **Reporters `artifact.py`** — ainda placeholder, não usado.

---

## 5. Próximo Passo Mínimo Para Retomar

1. Aplicar os commits pendentes da Seção 3 (ou consolidar em um só) e dar push.
2. Decidir o destino do PR #55 (fechar ou mergear).
3. Rodar ao menos 1-2 ciclos reais de `agent-audit` em PRs `develop→main` genuínos (com a feature-flag ligada manualmente) para observar custo e comportamento antes de decidir avançar.
4. Quando pronto para avançar, retomar pela **subtask 28** (`PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md` §3) — expandir o runner com o 2º caso de uso `code-review`, delegando via `@agent-router` → `@python-router` → `@python-feature-developer`.

---

## 6. Referências Rápidas

- **Repositório**: `jezreel8858/deep-agents-copilot`
- **Branch de trabalho principal**: `develop`
- **Branch produtiva**: `main`
- **PR de teste do Q-01**: #55
- **Run de validação**: `governance-agent-audit.yml` #6 (run id `36405112477`)
- **Pacote real do SDK**: PyPI `github-copilot-sdk` (módulo `copilot`), confirmado disponível (v1.0.14 no momento da pesquisa)

