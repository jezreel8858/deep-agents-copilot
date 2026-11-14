# Python/uv — Cascata, Bootstrap e Validação V1

Origem: `scripts/dev/py-test.sh` e bloco `[uv]` do `tools.lock`.

## Cascata do runner

1. `DAC_UV_BIN` válido → uv. Inválido → `[FALLBACK] DAC_UV_BIN invalido`.
2. Senão `DAC_PYTHON_BIN` válido → python. Inválido → `[FALLBACK]`.
3. `uv` no PATH → `uv` no cache (`<HOME>/.cache/deep-agents-copilot/uv/<versão>/<plataforma>`).
4. `DAC_BOOTSTRAP_UV=1` (alias `DAC_UV_BOOTSTRAP`) → bootstrap opt-in: download do release oficial do uv, SHA-256 do `tools.lock`, cópia para o cache; host permitido `github.com/astral-sh/uv/releases/download/`; nunca `curl | sh`.
5. `python`/`python3` → exige ≥ 3.11 e `pytest`, `yaml`, `jsonschema` (senão exit 12) e emite `[FALLBACK] sem uv; usando python -m pytest (sem lock)`.
6. Nada disponível → exit 10.

## Execução

- uv: `uv run --locked --project "$DAC_HOME" --directory <alvo> pytest -q --tb=short <args>`.
- Alvo: `DAC_HOME` por padrão; `--project <raiz>` exige `pytest.ini`, `pyproject.toml` ou `tests/` (senão exit 2); args pytest relativos ao alvo.
- `PYTEST_DEBUG_TEMPROOT` aponta para o cache do usuário (evita symlink em TEMP restrito); `MSYS_NO_PATHCONV=1` e `cygpath -w` no Windows.
- Timeout `DAC_TEST_TIMEOUT` (default 900s) → exit 15. `uv.lock` desatualizado/ausente → exit 17 (`uv lock`).
- Saída: sucesso = linha de resumo do pytest; falha = últimas 20 linhas; `DAC_VERBOSE=1`/`--verbose` = log inteiro. Log `py-test-<data>-<pid>.log` fora do repo.

## Validação V1 (execução contra `[PROJETO-ALVO]` externo)

Objetivo: provar que o ambiente do `DAC_HOME` executa pytest com `--directory` apontando para um projeto fora do repo.

1. Criar projeto sintético temporário **fora do repo** (`[PROJETO-ALVO]` com `tests/test_smoke.py` trivial).
2. Executar `uv run --locked --project "$DAC_HOME" --directory [PROJETO-ALVO] pytest -q` (ou `py-test.sh --project [PROJETO-ALVO]`).
3. Esperado: exit 0 e 1 teste passando; remover o diretório temporário.

Status: procedimento documentado; **o resultado da execução é registrado pela tarefa T4 do plano Python** (depende de uv disponível/bootstrap) — pendência até o registro.
