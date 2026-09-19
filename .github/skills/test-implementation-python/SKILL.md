---
name: test-implementation-python
description: 
  Padrões consolidados para implementação de testes em Python com pytest,
  incluindo unit tests, integration tests e cobertura com coverage.py.
tier: 2
category: testing
triggers:
  - "python testing"
  - "pytest"
  - "python unit test"
  - "python integration test"
  - "coverage.py"
  - "python mock"
  - "pytest fixture"
  - "python test"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/test-implementation-backend/SKILL.md
  - .github/skills/test-coverage-governance/SKILL.md
tools: []
---

# Test Implementation — Python / pytest / coverage.py

> **Escopo**: implementação específica para stack **Python + pytest + coverage.py**.
> Para padrões agnósticos de backend, consulte `test-implementation-backend`.

## Contexto

Stack de referência:
- **pytest** como test runner (não unittest)
- **pytest-mock** / `unittest.mock` para mocking
- **coverage.py** para relatórios de cobertura
- **pytest-cov** para integração de cobertura no pytest
- **httpx** / **respx** para mock de chamadas HTTP
- **conftest.py** para fixtures compartilhadas

## 1) Estrutura de Projeto

```
src/
  modulo/
    service.py
    repository.py

tests/
  unit/
    test_service.py         ← testa service em isolamento
    test_repository.py
  integration/
    test_service_integration.py
  conftest.py               ← fixtures compartilhadas
```

## 2) Unit Tests — pytest + mock

### Padrão Base (Service)

```python
import pytest
from unittest.mock import MagicMock, patch
from modulo.service import [Entidade]Service
from modulo.repository import [Entidade]Repository


@pytest.fixture
def [entidade]_repository():
    return MagicMock(spec=[Entidade]Repository)


@pytest.fixture
def [entidade]_service([entidade]_repository):
    return [Entidade]Service(repository=[entidade]_repository)


class Test[Entidade]Service:
    def test_deve_salvar_quando_dados_validos(
        self, [entidade]_service, [entidade]_repository
    ):
        # Arrange
        dados = {"campo": "valor_valido"}
        [entidade]_repository.save.return_value = {"id": 1, **dados}

        # Act
        resultado = [entidade]_service.salvar(dados)

        # Assert
        assert resultado["id"] == 1
        [entidade]_repository.save.assert_called_once_with(dados)

    def test_deve_lancar_excecao_quando_dados_invalidos(
        self, [entidade]_service
    ):
        # Arrange
        dados = {"campo": None}

        # Act & Assert
        with pytest.raises(ValueError, match="campo obrigatório"):
            [entidade]_service.salvar(dados)
```

### Checklist de Unit Test

- [ ] Todos os métodos públicos testados (happy path + edge cases)
- [ ] Exceções testadas com `pytest.raises`
- [ ] Dependências mockadas com `MagicMock(spec=Classe)`
- [ ] Fixtures em `conftest.py` para estado compartilhado
- [ ] Nomes de teste descritivos em `test_deve_[acao]_quando_[condicao]`
- [ ] Cobertura: ≥ 80% linhas, ≥ 70% branches

### Usando pytest-mock (preferido)

```python
def test_deve_chamar_dependencia(mocker, [entidade]_service):
    # mocker.patch é mais limpo que @patch para pytest
    mock_dep = mocker.patch('modulo.service.[Dependencia]')
    mock_dep.return_value = {"dado": "valor"}

    resultado = [entidade]_service.processar()

    mock_dep.assert_called_once()
    assert resultado["dado"] == "valor"
```

### Parametrize para múltiplos cenários

```python
@pytest.mark.parametrize("entrada,esperado", [
    ({"campo": "valido"}, True),
    ({"campo": None}, False),
    ({"campo": ""}, False),
    ({}, False),
])
def test_deve_validar_entrada(entrada, esperado):
    resultado = validar_entrada(entrada)
    assert resultado == esperado
```

## 3) Fixtures — conftest.py

```python
# tests/conftest.py
import pytest
from modulo.repository import [Entidade]Repository
from modulo.service import [Entidade]Service


@pytest.fixture(scope="session")
def db_connection():
    """Conexão de banco compartilhada na sessão de teste."""
    conn = criar_conexao_teste()
    yield conn
    conn.close()


@pytest.fixture
def [entidade]_repository(db_connection):
    return [Entidade]Repository(db=db_connection)


@pytest.fixture
def [entidade]_service([entidade]_repository):
    return [Entidade]Service(repository=[entidade]_repository)
```

## 4) Integration Tests

```python
import pytest
from httpx import AsyncClient
from app.main import app  # FastAPI / ASGI app


@pytest.mark.asyncio
async def test_deve_retornar_200_ao_buscar([entidade]):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/v1/[entidades]/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
```

### Mock de HTTP Externo — respx

```python
import respx
import httpx


@respx.mock
def test_deve_chamar_api_externa():
    respx.get("https://api.externa.com/dados").mock(
        return_value=httpx.Response(200, json={"resultado": "ok"})
    )

    resultado = chamar_api_externa()
    assert resultado["resultado"] == "ok"
```

## 5) Coverage Targets

| Métrica | Mínimo | Ideal |
|---|---|---|
| Linhas | 70% | 80%+ |
| Branches | 60% | 70%+ |
| Funções | 75% | 85%+ |

## 6) Comandos pytest / coverage.py — Execução com Zero Ruído (R-008 / R-049)

> **ATENÇÃO**: Evite `pytest` sem flags de supressão no terminal. Use `-q` e `--tb=short` combinados com filtros ou Think-in-Code via `ctx_execute` para manter o contexto livre de ruído.

### A) Via `ctx_execute` (Think-in-Code — Recomendado)

```javascript
const { execSync } = require('child_process');
try {
  const out = execSync('pytest -q --tb=short tests/unit/test_[entidade]_service.py', { encoding: 'utf8' });
  console.log(out.trim());
} catch (err) {
  const full = (err.stdout || '') + '\n' + (err.stderr || '');
  console.log(full.split('\n').filter(l => /(FAILED|ERROR|passed in|===)/).slice(0, 30).join('\n'));
}
```

### B) Via Terminal com Filtro Obrigatório

```bash
# Executar arquivo específico (modo silencioso + traceback curto)
pytest -q --tb=short tests/unit/test_[entidade]_service.py 2>&1 | grep -E "FAILED|ERROR|passed in" | head -40

# Apenas um teste
pytest -q --tb=short tests/unit/test_[entidade]_service.py::Test[Entidade]Service::test_deve_salvar_quando_dados_validos

# Com relatório de cobertura conciso
pytest -q --cov=src --cov-report=term-missing --tb=short 2>&1 | grep -E "FAILED|ERROR|TOTAL|passed" | head -40

# Em PowerShell / Windows:
pytest -q --tb=short tests/unit/test_[entidade]_service.py
```

### pyproject.toml (configuração)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/conftest.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## 7) Anti-padrões

- ❌ Usar `unittest.TestCase` quando pytest já está configurado (menos expressivo)
- ❌ Fixtures com `scope="session"` para objetos com estado mutável (vazamento de estado)
- ❌ Mockar módulos internos em vez de injetar dependências (testes frágeis)
- ❌ Testes sem `assert` (passam sempre, inúteis)
- ❌ `time.sleep` em testes (use `freezegun` para tempo)
- ❌ Cobertura <70% sem justificativa de risco

## 8) Typing e MyPy em Testes

```python
from typing import Generator
import pytest


@pytest.fixture
def service() -> Generator[[Entidade]Service, None, None]:
    svc = [Entidade]Service()
    yield svc
    svc.cleanup()
```

## Referências

- pytest: https://docs.pytest.org/
- pytest-mock: https://pytest-mock.readthedocs.io/
- coverage.py: https://coverage.readthedocs.io/
- respx: https://lundberg.github.io/respx/
- freezegun: https://github.com/spulec/freezegun

