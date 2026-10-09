---
status: approved
date: 2026-10-08
autor: python-arch-advisor
workflow: feature-development
related-planning-doc: docs/implementation-plans/20261008-governance-maintenance-playwright-mcp-frontend-consolidation.md
tier: full
reversibility: T2
plan_ref: docs/implementation-plans/20261008-feature-development-embedded-python-runtime.md
progress: 0
allowed_files:
  - pyproject.toml
  - uv.lock
  - .python-version
  - tests/requirements.txt
  - scripts/dev/py-test.sh
  - scripts/dev/tools.lock
  - .github/skills/embedded-runtime-governance/SKILL.md
  - .github/skills/.index.json
  - .github/agents/backend/python/python-developer.agent.md
  - .github/agents/backend/python/python-test-engineer.agent.md
  - .github/agents/backend/python/python-arch-advisor.agent.md
  - .github/agents/backend/python/python-router.agent.md
  - .github/agents/backend/python/python-catalog.yaml
  - .github/agents/runtime-verifier.agent.md
  - .github/agents/pr-gatekeeper.agent.md
  - .github/agents/catalog.yaml
  - .a2a/agentcards/python-developer.agentcard.json
  - .a2a/agentcards/python-test-engineer.agentcard.json
  - .a2a/agentcards/python-arch-advisor.agentcard.json
  - .a2a/agentcards/python-router.agentcard.json
  - .a2a/agentcards/runtime-verifier.agentcard.json
  - .a2a/agentcards/pr-gatekeeper.agentcard.json
  - tools/agent_source_docs_sync/required_source_docs_rules.json
  - tests/governance_audit/test_embedded_python_runtime_governance.py
approved_by: humano (ask_questions)
approved_date: 2026-10-08
---

Progresso: 0/14 tarefas concluídas

# Plano de Implementação Técnica — Runtime Python Embutido (uv + wrapper `py-test.sh`)

> Modo ADVISORY (Gate 2, R-064, tier `full`): sem código. Executor: `@python-developer` (arquivos de código/config) e `@python-test-engineer` (testes). Aprovação humana via `ask_questions` antes do despacho.
> Plano irmão: `docs/implementation-plans/20261008-feature-development-embedded-maven-runtime.md` (dono de `resolve.sh`, `tools.lock`, skill, `.gitignore`/`.gitattributes`). Entrega no **mesmo commit da consolidação** (decisão humana).

## 1. Contexto e decisões humanas vigentes

- Abordagem: wrappers versionados + `uv` (mise rejeitado).
- Estado atual: não existem `pyproject.toml`, `uv.lock`, `.python-version`, `scripts/`. Existem `tests/requirements.txt` (`pytest>=8.0`, `PyYAML>=6.0`, `jsonschema>=4.20.0`, sem pin exato), `pytest.ini` (`testpaths=tests`, `pythonpath = . tools/otel-langfuse tools/headless-governance-runner/src`, `addopts = -ra -m "not slow"`, marker `slow`) e `.githooks/pre-commit`. `.gitignore` já cobre `.venv/` e `__pycache__/`.
- Workflows CI existentes: `ci-subprojects.yml`, `governance-agent-audit.yml`, `routing-quality-gate.yml` (hoje instalam via `pip install -r tests/requirements.txt`).

## 2. Fronteira, ordem e dependência com o plano Maven

| Artefato | Dono | Regra para este plano |
|---|---|---|
| `scripts/dev/lib/resolve.sh` | Plano Maven | Somente `source`. Usar apenas `dac_log`, `dac_die`, `dac_cache_dir`, `dac_platform`, `dac_download`, `dac_verify_sha256`. **Nenhuma edição** aqui. Necessidade nova → pedir ao plano Maven antes do merge (não alterar). |
| `scripts/dev/tools.lock` | Plano Maven (seção `[mvnd]`) | Este plano **anexa** bloco `[uv]` (chave=valor: versão pinada, URL, SHA-256 por plataforma) **após** o merge Maven. Está na allowlist apenas para esse append. |
| `.gitignore`, `.gitattributes` | Plano Maven | Não editados aqui (`.venv/` já ignorado; `*.sh` LF a cargo do Maven). Gap detectado em T1 → pendência, não edição. |
| Skill `embedded-runtime-governance` | Plano Maven cria; este plano **acrescenta** seção "Python/uv" | Edição somente após o merge da skill Maven; não alterar a tabela de exit codes compartilhada. |
| `skills/.index.json`, `catalog.yaml`, `runtime-verifier`, `pr-gatekeeper` + agentcards | Compartilhados | Editar **depois** do Maven; alterações em linhas/bloco próprio (ponteiro Python), sem reordenar. |
| `pyproject.toml`, `uv.lock`, `.python-version`, `py-test.sh`, agents `python-*`, teste de governança Python | Este plano | Exclusivo. |

Ordem: (1) Maven entrega `resolve.sh`+`tools.lock`+`.gitattributes`+`.gitignore`+skill; (2) este plano consome; (3) tarefas Python em arquivos exclusivos (T1–T4) podem ser desenvolvidas em paralelo ao Maven, mas **T5/T8–T10 só após** os artefatos Maven existirem. Dependência dura: `py-test.sh` falha explicitamente (exit 2 interno de contrato) se `resolve.sh` ausente.

## 3. Mini-ADRs

### ADR-1 — Decisão de Design Pattern (mini-ADR — design-pattern-selection-patterns)
- Contexto: executar pytest de forma reprodutível em Windows/Git Bash/Linux/macOS, com saída enxuta e fallback.
- Decisão: **Nenhum pattern GoF necessário** — Script wrapper com cascata de resolução (Chain of Responsibility implícita, funções de `resolve.sh`); sem camadas adicionais.
- Alternativas: mise (rejeitado pelo humano); Makefile/tox/nox (dependência extra, pior no Windows); venv manual com `pip` (sem lock, sem reprodutibilidade).
- Consequências: + reprodutível via `uv.lock`; + zero dependência nova em CI se uv ausente (fallback); − dois caminhos a manter (uv e pip) → coberto por teste de coerência.

### ADR-2 — `pyproject.toml` e `tests/requirements.txt`: manter ambos
- Decisão: **`pyproject.toml` é a fonte de verdade** do ambiente uv (grupo `dev`); `tests/requirements.txt` **permanece** como fallback e para os workflows CI atuais (não quebrar `pip install -r`). Não gerar um a partir do outro em build (evita passo mágico/diff ruidoso).
- Coerência garantida por **teste** (T10): mesmos pacotes (nome normalizado) e mesmos limites inferiores (`>=`) em ambos. Futura evolução opcional: `uv export --no-hashes` para gerar requirements (fora do escopo; pendência).
- Alternativas: gerar requirements via `uv export` (rejeitado agora: exige uv em CI/pre-commit); remover requirements (quebra CI).
- Consequências: duplicação mínima de 3 linhas, detectada por teste.

### ADR-3 — Configuração do pytest permanece em `pytest.ini`
- Decisão: `pyproject.toml` **não** define `[tool.pytest.ini_options]` (pytest.ini tem precedência; duplicar causaria divergência silenciosa). Projeto uv sem empacotamento: `[tool.uv] package = false` (repo não é distribuível; `pythonpath` do pytest.ini já resolve imports).
- Consequências: `pytest.ini` inalterado (fora da allowlist); testes de governança verificam ausência de `[tool.pytest` no pyproject.

### ADR-4 — Versão Python
- Decisão: `requires-python = ">=3.11"` (alinhado a `python-backend.instructions.md`, mypy `python_version = "3.11"`) e `.python-version` com **3.12** (minor sem patch; ambiente de desenvolvimento atual é 3.12.x, 3.11 permanece suportado). Sugestão a confirmar (pendência P1).
- Consequências: uv baixa/gerencia interpretador conforme `.python-version`; fallback usa python do PATH desde que ≥3.11.

## 4. Especificação técnica (sem código)

### 4.1 `pyproject.toml`
- `[project]`: nome `deep-agents-copilot-dev`, versão `0.0.0`, `requires-python >=3.11`, sem dependências de runtime.
- Grupo `dev` em `[dependency-groups]` (PEP 735): `pytest>=8.0`, `PyYAML>=6.0`, `jsonschema>=4.20.0` (idênticos a `tests/requirements.txt`). `[tool.uv] default-groups = ["dev"]`, `package = false`.
- Sem seções de pytest/mypy/ruff (YAGNI).

### 4.2 `uv.lock` e `.python-version`
- `uv.lock` gerado por `uv lock` (por `@python-developer` com uv disponível; sem uv → bloqueio e pendência P2) e **versionado**. Verificação: `uv lock --check` e uso `--locked` impedem drift.
- `.python-version`: uma linha, `3.12`, LF.

### 4.3 `scripts/dev/py-test.sh [--project <raiz>] [args pytest...]`
- Cabeçalho `#!/usr/bin/env bash`, `set -euo pipefail`, LF, bit executável no índice git (`git update-index --chmod=+x`). `source` de `lib/resolve.sh` (erro explícito se ausente).
- **Resolução do runner** (primeira que satisfizer vence):
  1. `DAC_PYTHON_BIN` (python explícito, usado em modo fallback `-m pytest`) ou `DAC_UV_BIN`/`UV` (binário do uv) — env explícito.
  2. `uv` no `PATH`; senão uv em cache do usuário (`dac_cache_dir`) já instalado; bootstrap do uv com download verificado SHA-256 conforme bloco `[uv]` do `tools.lock` **somente se** `DAC_UV_BOOTSTRAP=1` (default `0`: sem rede implícita).
  3. `python`/`python3` do `PATH` (≥3.11 verificado) → `python -m pytest` com aviso `[FALLBACK]` e verificação de que `pytest`, `yaml`, `jsonschema` importam (senão instruir `python -m pip install -r tests/requirements.txt`).
  4. Erro explícito.
- **Execução com uv** (repo deste projeto): `uv run --locked pytest -q --tb=short <args>` a partir da raiz de `DAC_HOME`.
- **Projeto-alvo externo** `[PROJETO-ALVO]`: `DAC_HOME` = raiz do deep-agents-copilot, **derivada** do local do script (`dirname` do script, nunca hardcode) e exportada; invocar `uv run --locked --project "$DAC_HOME" --directory "<raiz-do-alvo>" pytest -q --tb=short <args>`. **A validar (V1)**: semântica de `--project` vs `--directory` com `--locked` (lock do projeto vs. alvo) e que o `pytest.ini`/`pythonpath` do alvo prevalece sobre o do DAC. Se V1 falhar: fallback documentado `uv run --locked --project "$DAC_HOME" -- python -m pytest --rootdir "<alvo>" -c "<alvo>/pytest.ini|pyproject"`. Plugins/dependências do alvo **não** são instaladas pelo DAC (limitação documentada; alvo com deps próprias deve usar o próprio ambiente).
- **Saída enxuta**: stdout/stderr integrais redirecionados ao log (`<cache>/logs/py-test-<timestamp>.log`, via `dac_cache_dir`, fora do repo); no terminal só: resumo final do pytest (última linha `N passed/failed in Xs`), até as 20 últimas linhas em caso de falha e `log: <caminho-do-log>` (caminho do log pode ser local em runtime, nunca persistido em arquivo versionado). Flag `--verbose` / `DAC_VERBOSE=1` desliga o filtro.
- **Exit codes** (contrato compartilhado da skill; aqui usados):

| Code | Significado no `py-test.sh` |
|---|---|
| 0 | Testes passaram |
| 1 | Falha de testes ou nenhum teste coletado (pytest 1/2/3/4/5 propagados com mensagem) |
| 2 | Uso inválido (raiz do alvo inexistente, sem `pyproject.toml`/`pytest.ini`/`tests/`) |
| 10 | Nenhum runner resolvido (sem uv e sem python) |
| 11 | Falha de download/rede do uv sem cache |
| 12 | Python ausente ou < 3.11 / incompatível com `requires-python` |
| 13 | SHA-256 do uv divergente |
| 14 | Plataforma sem entrada `[uv]` no `tools.lock` |
| 15 | Timeout (`DAC_TEST_TIMEOUT`, default 900 s) |
| 17 (**novo, Python**) | `uv.lock` desatualizado/ausente (`--locked` falhou); orientar `uv lock` |

  Código 17 é registrado na seção Python da skill (sem alterar a tabela comum). Código 16 (política mvnw) não se aplica.
- **Windows/MSYS**: nunca converter caminhos manualmente; usar `cygpath -w` apenas ao passar caminhos a executável nativo quando `dac_platform` = windows; `MSYS_NO_PATHCONV=1` ao invocar uv; escrever scripts em LF (`.gitattributes` do plano Maven); `.venv` do uv cria `Scripts/` no Windows — wrapper não ativa venv, usa `uv run`. `UV_PROJECT_ENVIRONMENT` default (`.venv` na raiz, ignorado pelo git); para o modo alvo, o ambiente permanece no `DAC_HOME`.

### 4.4 Skill compartilhada — seção Python
- Em `.github/skills/embedded-runtime-governance/SKILL.md` (após merge Maven) acrescentar seção "Python/uv": cascata, variáveis (`DAC_PYTHON_BIN`, `DAC_UV_BIN`, `DAC_UV_BOOTSTRAP`, `DAC_HOME`, `DAC_VERBOSE`, `DAC_TEST_TIMEOUT`), exit code 17, uso em `[PROJETO-ALVO]`, fallback pip. Placeholders `<workspace>`/`<HOME>`/`[PROJETO-ALVO]`; sem caminho de máquina.

### 4.5 Agents e artefatos de governança (por ponteiro, sem duplicar conteúdo)
- `python-developer`, `python-test-engineer`: instrução "executar testes via `scripts/dev/py-test.sh` (skill `embedded-runtime-governance`); proibido `pip install` global ad hoc"; adicionar skill ao frontmatter/`source_docs` conforme padrão dos agents Spring (equivalente da tarefa Maven).
- `python-arch-advisor`, `python-router`: ponteiro à skill (validação de plano / roteamento de execução de testes; sem lógica nova).
- `pr-gatekeeper`, `runtime-verifier`: uma linha-ponteiro no bloco Python (verificação de testes por wrapper; saída enxuta + log); sem reescrever o bloco Maven.
- `python-catalog.yaml`, `catalog.yaml`, agentcards (6) e `.index.json` da skill: refletir skill adicionada (skills/capabilities) mantendo hash/ordem existentes; `required_source_docs_rules.json`: incluir a skill nos agents `python-*` (e gatekeeper/verifier se aplicável) — regra de sync é fonte do `source_docs` (rodar o sync em modo check após edição).

### 4.6 CI e pre-commit — impacto
- **CI**: sem alteração obrigatória neste commit (workflows continuam com `pip install -r tests/requirements.txt` + pytest). Opcional posterior: adotar `astral-sh/setup-uv` + `uv run --locked pytest` (pendência P4). Teste de coerência impede divergência enquanto ambos coexistirem.
- **pre-commit** (`.githooks/pre-commit`): **não editado**. Verificar apenas que o hook R-044 (bloqueio de caminho de máquina em `.github/`) não é disparado pelo conteúdo novo (usar placeholders). Scripts novos não são executados pelo hook.

### 4.7 Testes — `tests/governance_audit/test_embedded_python_runtime_governance.py` (`@python-test-engineer`)
- `scripts/dev/py-test.sh` existe, é executável (bit no índice git / `os.access` fora do Windows), shebang bash, LF (sem `\r`), `set -euo pipefail`, referencia `resolve.sh` e `DAC_PYTHON_BIN`.
- Nenhum caminho de máquina (`[A-Za-z]:\\`, `/home/<x>/`, `/Users/<x>/`) nos arquivos novos/alterados (pyproject, scripts, skill, plano).
- `pyproject.toml` parseável (`tomllib`): `requires-python` ≥3.11; grupo `dev` ⊇ pacotes/limites de `tests/requirements.txt` (e vice-versa); ausência de `[tool.pytest`.
- `uv.lock` existe, não vazio, contém os 3 pacotes; `.python-version` válido e compatível com `requires-python`.
- Os 4 agents `python-*`, `pr-gatekeeper` e `runtime-verifier` referenciam `embedded-runtime-governance`; skill existe e consta em `.index.json`; skill contém seção Python e código 17.
- Marcar nenhum teste como `slow`; teste independente de uv instalado (não executa uv).

## 5. Checklist de Execução Técnica (GFM Unificado)

- [ ] T1 — Criar `.python-version` e `pyproject.toml` (grupo dev, `package=false`, sem pytest config) `{paralelizavel: true, responsavel: "@python-developer"}`
- [ ] T2 — Gerar e versionar `uv.lock` (`uv lock`; validar `uv lock --check`); usando o uv obtido pelo bootstrap opt-in (P2/P3); se o bootstrap falhar, bloquear T11 e reportar `{paralelizavel: false, responsavel: "@python-developer"}`
- [ ] T3 — Ajustar cabeçalho de `tests/requirements.txt` (comentário: fonte = `pyproject.toml`, fallback sem uv), sem alterar pacotes/limites `{paralelizavel: true, responsavel: "@python-developer"}`
- [ ] T4 — Validar V1 (`uv run --locked --project ... --directory ...` com projeto-alvo sintético temporário fora do repo) e registrar resultado na skill `{paralelizavel: true, responsavel: "@python-developer"}`
- [ ] T5 — [após T1–T3 do plano Maven `embedded-maven-runtime`] Criar `scripts/dev/py-test.sh` conforme §4.3 + bit executável `{paralelizavel: false, responsavel: "@python-developer"}`
- [ ] T6 — [após T1–T3 do plano Maven `embedded-maven-runtime`] Anexar bloco `[uv]` em `scripts/dev/tools.lock` (versão pinada + SHA-256 por plataforma; valores obtidos de fonte oficial verificada) `{paralelizavel: false, responsavel: "@python-developer"}`
- [ ] T7 — [após T1–T3 do plano Maven `embedded-maven-runtime`] Acrescentar seção "Python/uv" na skill `embedded-runtime-governance` + `.index.json` `{paralelizavel: false, responsavel: "@python-developer"}`
- [ ] T8 — Atualizar 4 agents `python-*` por ponteiro `{paralelizavel: true, responsavel: "@python-developer"}`
- [ ] T9 — Ponteiro Python em `pr-gatekeeper` e `runtime-verifier` `{paralelizavel: true, responsavel: "@python-developer"}`
- [ ] T10 — Atualizar `python-catalog.yaml`, `catalog.yaml`, 6 agentcards e `required_source_docs_rules.json`; rodar sync em modo check `{paralelizavel: false, responsavel: "@python-developer"}`
- [x] T11 — Criar `test_embedded_python_runtime_governance.py` (§4.7) `{paralelizavel: true, responsavel: "@python-test-engineer"}`
- [x] T12 — Validação silenciosa (§6) `{paralelizavel: false, responsavel: "@python-test-engineer"}`
- [x] T13 — Verificação R-044/R-043: varredura de caminho de máquina nos arquivos da allowlist `{paralelizavel: true, responsavel: "@python-test-engineer"}`
- [ ] T14 — Revisão final (`@pr-gatekeeper`) e handoff ao commit único da consolidação `{paralelizavel: false, responsavel: "@pr-gatekeeper"}`

## 6. Validação silenciosa

Executar via wrapper (sem verbose): `scripts/dev/py-test.sh tests/governance_audit` (novo teste + suíte de governança), depois `scripts/dev/py-test.sh` completo (`-m "not slow"` do pytest.ini). Saída esperada: apenas resumo + `log: <caminho>`. Cenários: (a) com uv; (b) `DAC_UV_BIN` inválido → fallback python com `[FALLBACK]`; (c) sem uv e sem python (PATH vazio simulado) → exit 10; (d) `.python-version` incompatível → exit 12; (e) `uv.lock` alterado → exit 17. Rodar também `pip install -r tests/requirements.txt && python -m pytest` para provar que o fallback e CI atuais seguem verdes. Windows: executar no Git Bash.

## 7. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| CRLF em `.sh` (autocrlf) | `bad interpreter` | `.gitattributes` `eol=lf` (Maven) + teste de LF |
| Conversão de caminhos MSYS | `uv`/python não acha caminho | `MSYS_NO_PATHCONV=1`, `cygpath -w` pontual, sem caminhos hardcoded |
| Bit executável perdido no Windows | script não executa em Linux/CI | `git update-index --chmod=+x`; teste no índice |
| `--project`/`--directory` com alvo (V1) | execução externa incorreta | T4 valida; fallback documentado |
| Drift pyproject × requirements | CI e uv divergentes | teste de coerência (ADR-2) |
| `.venv` no repo | sujeira working tree | já em `.gitignore`; teste de presença da regra |
| Bootstrap de uv por rede | supply chain | opt-in, SHA-256 pinado, nunca `curl | sh` |
| Edição concorrente de arquivos compartilhados com plano Maven | conflitos/ordem | §2: Python edita depois e só em bloco próprio |
| uv ausente no ambiente do executor (hoje ausente na máquina de desenvolvimento) | T2 bloqueada | pendência P2; alternativa: executor instala uv por conta própria |
| Alvo com dependências próprias | testes falham no ambiente DAC | limitação documentada; usar ambiente do alvo |

## 8. Rollback (reversibility T2)

Commit único da consolidação: `git revert` do commit restaura estado anterior (nenhum arquivo existente é removido; `tests/requirements.txt` e `pytest.ini` permanecem funcionais). Rollback parcial: remover `pyproject.toml`, `uv.lock`, `.python-version`, `scripts/dev/py-test.sh`, bloco `[uv]`, seção Python da skill e ponteiros nos agents/catálogos/agentcards, e o teste novo. Cache do usuário (uv/logs) fora do repo: limpeza manual opcional. CI não afetado.

## 9. Critérios de pronto

- Todos os itens do checklist marcados e `progress` atualizado; `status: approved` antes da execução.
- `py-test.sh` roda a suíte via uv (`--locked`) e via fallback; exit codes conforme §4.3; saída enxuta com caminho do log.
- Execução em `[PROJETO-ALVO]` usando `DAC_HOME` validada (V1) ou fallback documentado.
- Novo teste de governança verde; suíte completa verde; sync de `source_docs` em check sem divergências; hooks sem bloqueio R-043/R-044.
- Zero caminho de máquina/usuário/projeto local em arquivos versionados.
- `uv.lock` versionado e `uv lock --check` ok.

## 10. Decisões humanas registradas (aprovado por humano em 2026-10-08 via ask_questions)

- P1: `.python-version` = 3.12. **Decidido.**
- P2/P3: uv não está instalado localmente. O bootstrap opt-in (`DAC_UV_BOOTSTRAP`) instala o uv: download verificado por SHA-256, instalação no cache do usuário (`DAC_CACHE_DIR`), versão pinada validada pelo executor via fonte oficial (sem `curl | sh`). `uv.lock` é gerado com esse uv (T2). **Decidido.**
- P4: `setup-uv` nos workflows CI fica fora deste commit (CI segue com `pip install -r tests/requirements.txt`). **Decidido.**
- P5: exit code 17 (`uv.lock` desatualizado) aprovado. **Decidido.**
- Commit: o mesmo da consolidação (commit único). **Decidido.**
- Dependência: T5–T7 aguardam T1–T3 do plano Maven (`embedded-maven-runtime`). **Decidido.**
- P6: aprovação concedida; `status: draft` → `approved`.

### 🔒 Checklist Defensivo Pré-Code-Review
- [ ] Sanitização e validação de inputs em todas as bordas expostas (argumentos do wrapper, raiz do alvo)
- [ ] Ausência de segredos, tokens ou dados sensíveis em hardcode e logging seguro sem PII (logs fora do repo)
- [ ] Tratamento defensivo de exceções e controle de autorização/permissões validado (sem executar código do alvo além de pytest; sem `curl | sh`)
- [ ] Testes unitários/integração defensivos atendendo aos quality gates
