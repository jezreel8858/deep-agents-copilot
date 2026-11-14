# Test Implementation — Python (Fixtures, Integration e Config)

## 3–4) Fixtures (`conftest.py`) e Integration Tests (`AsyncClient` / `respx`)

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
