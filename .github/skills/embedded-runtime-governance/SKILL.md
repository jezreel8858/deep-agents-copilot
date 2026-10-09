---
name: embedded-runtime-governance
description: Fonte única do contrato de runtime embutido (Maven via mvnd/mvnw e Python via uv) — scripts/dev/mvn-test.sh e py-test.sh, variáveis DAC_*, exit codes, cascata de resolução, fallback, logs fora do repo e pendências humanas.
tier: 2
category: tooling
triggers:
  - "executar testes maven"
  - "mvn-test.sh"
  - "py-test.sh"
  - "mvnd"
  - "uv run"
  - "runtime embutido"
  - "DAC_MVN_MODE"
  - "bootstrap uv"
  - "tools.lock"
tools: ["run_in_terminal"]
source_docs:
  - .github/skills/terminal-governance/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# Embedded Runtime Governance

> **Progressive Disclosure**: Nível 1 = frontmatter; Nível 2 = este índice; Nível 3 = `references/` (carregar só o necessário via `ctx_search`/`ctx_execute_file`). **SSOT**: agents apenas apontam para esta skill (1–2 linhas) e nunca copiam o conteúdo.

## 1) Quando Usar

- Executar, verificar ou documentar testes/compilação de um `[PROJETO-ALVO]` Maven (Spring Boot, Spring Reactive, EJB, Struts) ou de testes Python.
- Diagnosticar falha de runtime (exit code, cascata, fallback, timeout, daemon, `uv.lock`).
- Revisar instruções de agents que citem `mvn`, `mvnw` ou `pytest` soltos (devem usar os wrappers).

## 2) Contrato dos Wrappers

| Wrapper | Uso | Saída |
| :--- | :--- | :--- |
| `scripts/dev/mvn-test.sh` | `[--dry-run] <raiz-do-projeto> [args-maven...]` (default `test`) · `--stop` · `--help` | Resumo (`resultado`, tempo, módulos, `Tests run`), até 15 linhas `[ERROR]` em falha e `log:` |
| `scripts/dev/mvn-test.cmd` | Shim Windows que delega ao `.sh` via Git Bash (exit 10 se Git Bash ausente) | Idem |
| `scripts/dev/py-test.sh` | `[--project <raiz-alvo>] [--dry-run] [--verbose] [args pytest...]` | Sucesso: 1 linha de resumo; falha: últimas 20 linhas; `log:` |
| `scripts/dev/bootstrap-mvnd.sh` | Instala o mvnd do `tools.lock` no cache do usuário (idempotente, SHA-256) | Caminho do binário em stdout |

- `scripts/dev/lib/resolve.sh` e `scripts/dev/tools.lock` são compartilhados (somente `source`/leitura); versões e SHA-256 vivem apenas no `tools.lock`.
- Logs completos ficam **fora do repo** (`<HOME>/.cache/deep-agents-copilot/logs`, ou `DAC_LOG_DIR` no Maven); mensagens usam `<HOME>`.
- `--dry-run` não faz rede nem bootstrap: serve a verificadores read-only (resolução de runtime, JDK/Python).

## 3) Exit Codes (contrato comum)

| Code | Significado |
| :---: | :--- |
| 0 | Sucesso |
| 1 | Falha de build/teste |
| 2 | Uso inválido (argumento, raiz sem `pom.xml`/`pytest.ini`/`tests`, `DAC_MVN_MODE` inválido) |
| 10 | Runtime ausente (sem Maven/uv/python; `DAC_MAVEN_BIN`/`MVND_HOME` inválido; `curl`/`wget`/`tar`/`unzip` ausente) |
| 11 | Rede (download falhou; timeout aguardando outro bootstrap) |
| 12 | JDK ausente/incompatível/ambíguo no `pom.xml` (Maven) · Python < 3.11 ou dependências ausentes (fallback) |
| 13 | SHA-256 divergente — **nunca** cai em fallback |
| 14 | Plataforma/seção ausente no `tools.lock`, SHA pendente ou host fora da allowlist |
| 15 | Timeout (`DAC_MVN_TIMEOUT` / `DAC_TEST_TIMEOUT`, default 900s) |
| 16 | `mvnw` do alvo bloqueado (modo `daemon` sem `DAC_ALLOW_TARGET_WRAPPER=1`) |
| 17 | `uv.lock` desatualizado/ausente — executar `uv lock` |

## 4) Variáveis

| Variável | Efeito |
| :--- | :--- |
| `DAC_MVN_MODE` | `daemon` (default) \| `wrapper` \| `auto` — política da cascata Maven |
| `DAC_MAVEN_BIN` / `MVND_HOME` | Override do binário Maven / home do mvnd (prioridade máxima, qualquer modo) |
| `DAC_JAVA_HOME` | JDK explícito (exporta `JAVA_HOME`); obrigatório se o `pom.xml` não declara versão Java |
| `DAC_MVN_TIMEOUT` | Segundos (numérico, default 900 — **revisão humana**) |
| `DAC_ALLOW_TARGET_WRAPPER` | `1` permite `./mvnw` do alvo como fallback no modo `daemon` |
| `DAC_MVND_OPTS` · `DAC_MVN_STOP_ON_EXIT` · `DAC_LOG_DIR` | Args extras só do mvnd (ex.: heap) · `1` encerra o daemon ao sair · diretório de logs |
| `DAC_UV_BIN` / `DAC_PYTHON_BIN` | Override do `uv` / do Python (`DAC_UV_BIN` tem precedência; inválido → `[FALLBACK]`) |
| `DAC_BOOTSTRAP_UV` | `1` habilita bootstrap opt-in do uv (alias `DAC_UV_BOOTSTRAP`) |
| `DAC_TEST_TIMEOUT` · `DAC_VERBOSE` | Timeout pytest (default 900s) · `1` imprime o log completo |
| `DAC_HOME` | Raiz do repo (derivada do script; fornece o ambiente `uv`) |
| `XDG_CACHE_HOME` · `DAC_DOWNLOAD_TIMEOUT` · `DAC_LOCK_WAIT` | Base do cache do usuário · timeout de download (900s) · espera por lock de bootstrap (120s) |

## 5) Runtime Maven embutido

- **Cascata** (resumo; detalhe em `references/maven-cascata-daemon.md`): `DAC_MAVEN_BIN`/`MVND_HOME` → conforme o modo — `daemon`: mvnd (PATH) → cache → bootstrap → `[FALLBACK]` mvnw (se permitido)/`mvn`; `wrapper`/`auto`: `./mvnw` do alvo → mvnd → `mvn` → cache → bootstrap.
- **Fallback**: toda degradação emite `[FALLBACK]` em stderr; divergência de SHA (13) aborta sem fallback.
- **Daemon (risco aceito, decisão humana)**: processo residual, RAM e travamento de arquivos no Windows. Mitigações: `mvn-test.sh --stop` (para o mvnd localizado, timeout 60s), stop automático em falha/timeout, `DAC_MVN_STOP_ON_EXIT=1`, sem `clean` implícito, heap via `DAC_MVND_OPTS`, override `DAC_MVN_MODE=wrapper|auto`.
- **mvnw do alvo = execução de código não confiável**: só com `DAC_MVN_MODE=wrapper|auto` ou `DAC_ALLOW_TARGET_WRAPPER=1`.
- **JDK**: `DAC_JAVA_HOME` > `JAVA_HOME` > `java` no PATH; versão mínima lida do `pom.xml` em runtime (sem hardcode).

## 6) Python/uv

- Comando efetivo: `uv run --locked --project "$DAC_HOME" --directory <alvo> pytest -q --tb=short` (alvo = `DAC_HOME` ou `--project <raiz-alvo>`).
- **Cascata**: `DAC_UV_BIN` | `DAC_PYTHON_BIN` → `uv` no PATH → `uv` no cache → bootstrap (`DAC_BOOTSTRAP_UV=1`) → `python`/`python3` ≥ 3.11 → exit 10.
- **Fallback sem uv**: `[FALLBACK] sem uv; usando python -m pytest (sem lock)` — exige `pytest`, `yaml`, `jsonschema` (`pip install -r tests/requirements.txt`, feito pelo humano); senão exit 12. Proibido `pip install` global ad hoc pelo agent.
- **Limitação**: com `--project`, o ambiente é o do `DAC_HOME`; alvo com dependências próprias deve usar o ambiente do alvo.
- Detalhes, bootstrap e validação V1 em `references/python-uv.md`.

## 7) Como Usar

```bash
scripts/dev/mvn-test.sh --dry-run <raiz-do-projeto>   # verifica runtime sem rede
scripts/dev/mvn-test.sh <raiz-do-projeto> test        # testes Maven (default)
scripts/dev/mvn-test.sh --stop                        # encerra o daemon mvnd
scripts/dev/py-test.sh tests/governance_audit         # testes Python do DAC_HOME
scripts/dev/py-test.sh --project [PROJETO-ALVO]       # pytest no alvo externo
```

## 8) Checklist

- [ ] Nenhum `mvn`/`mvnw`/`pytest` solto nas instruções de execução de testes dos agents.
- [ ] Exit code interpretado conforme a tabela da seção 3 (13 nunca vira fallback).
- [ ] Zero caminho de máquina/usuário/projeto local em arquivos versionados (R-038/R-043/R-044): usar `<workspace>`, `<HOME>`, `[PROJETO-ALVO]`.
- [ ] Hashes do `tools.lock` e timeout 900s com revisão humana registrada antes do merge (`references/riscos-e-pendencias.md`).

## 9) Referências

- `references/maven-cascata-daemon.md` · `references/python-uv.md` · `references/riscos-e-pendencias.md`
- `.github/skills/terminal-governance/SKILL.md` (Zero-Noise, watchdog)
