---
applyTo: ["**/*.py", "**/requirements*.txt", "**/pyproject.toml", "**/setup.py", "**/Pipfile"]
---

# Convenções de Código — Python Backend

> Resumo consolidado das convenções de backend para projetos Python. Use este documento como referência principal para padrões Python; consulte `CLAUDE.md` e `.github/copilot-instructions.md` apenas para governança geral.
>
> **Instruções genéricas**: este arquivo é reutilizável por qualquer projeto Python backend. Customizações específicas de projeto (frameworks web, ORMs, estruturas de diretório) devem ser adicionadas via adapter próprio em `.github/instructions/<projeto>-python-backend.instructions.md`.

### Padrões Gerais

- Todo código, comentários e logs do domínio devem ser escritos em Português do Brasil.
- Nomenclatura Python seguindo PEP 8: `snake_case` para funções/variáveis, `PascalCase` para classes.
- Preferir explícito a implícito (PEP 20 — Zen of Python).

### Tipagem e Qualidade

- Usar **type hints** em todas as funções e métodos públicos (PEP 484).
- Configurar **mypy** (target Python 3.11+) com `strict = true` ou `disallow_untyped_defs = true`.
- Usar **dataclasses** ou **Pydantic** para modelos de dados com validação.
- Usar **TypedDict** para dicionários estruturados.

### Formatação e Linting

- **Black** (88 colunas) como formatter padrão — sem configuração customizada de line length.
- **isort** com perfil `"black"` para organização de imports.
- **flake8** ou **ruff** para linting.
- Executar em CI: `black --check . && isort --check-only . && flake8 src`

### Organização de Imports

```python
# 1. Standard library
import os
from typing import Optional, List

# 2. Third-party
import httpx
from pydantic import BaseModel

# 3. Internal
from modulo.service import MinhaService
```

### Classes e Funções

- Injeção de dependência via construtor (não via variáveis globais nem `import`).
- Preferir funções puras e testáveis; evitar estado global mutável.
- Métodos de classe não devem exceder 20 linhas; extrair para funções privadas bem nomeadas.
- Documentar comportamento (não a implementação) em docstrings Google style para APIs públicas.

```python
def processar(dados: dict[str, str]) -> ResultadoDTO:
    """Processa os dados e retorna o resultado.

    Args:
        dados: Dicionário com campos obrigatórios.

    Returns:
        DTO com resultado processado.

    Raises:
        ValueError: Se campo obrigatório ausente.
    """
```

### Exceções

- Criar exceções customizadas derivadas de `Exception` para erros de domínio.
- Não capturar `Exception` genérica; preferir exceções específicas.
- Registrar logs antes de re-raise com contexto suficiente.

```python
class DomainException(Exception):
    """Exceção base de domínio."""

class ValidationException(DomainException):
    """Falha de validação de dados."""

class IntegrationException(DomainException):
    """Falha de integração com sistema externo."""
```

### Logging

- Usar `logging` padrão (não `print`).
- Configurar via `logging.getLogger(__name__)` por módulo.
- Nível de log com f-strings apenas se necessário; preferir `%s` lazy para performance.

```python
import logging

logger = logging.getLogger(__name__)

def salvar(dados: dict) -> None:
    logger.info("Iniciando salvamento: campo=%s", dados.get("campo"))
    # ...
    logger.info("Salvamento concluído com sucesso")
```

### Testes & Execução com Zero Ruído (R-008 / R-049)

- Base: **pytest** com `pytest-mock` e `pytest-cov`.
- Fixtures em `conftest.py` — reutilizáveis por escopo de sessão/módulo/função.
- Padrão de nome: `test_deve_[acao]_quando_[condicao]`.
- Mock de dependências com `MagicMock(spec=Classe)` — nunca mock parcial sem spec.
- Cobertura mínima: 80% de linhas, 70% de branches.
- **Higiene de Execução (Zero-Noise)**: Priorizar execução via `ctx_execute` (Think in Code). Se usar terminal, aplicar compulsoriamente `-q --tb=short` e filtro pipe:
  `pytest -q --tb=short tests/unit/test_arquivo.py 2>&1 | grep -E "FAILED|ERROR|passed in" | head -40`

Para padrões detalhados de testes, consulte `test-implementation-python`.

### Configuração do Projeto

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Guardrail de Manutenção

- Manter este adapter genérico — sem referências a frameworks específicos (FastAPI, Django, Flask) ou projetos.
- Customizações de framework → adapter próprio: `.github/instructions/<projeto>-python-backend.instructions.md`.

### Referências da convenção consolidada

- `CLAUDE.md` e `.github/copilot-instructions.md` para governança global.
- Este documento para as convenções genéricas de backend Python.
- `test-implementation-python` para padrões detalhados de testes.
- Adapter específico do projeto (ex.: `.github/instructions/<projeto>-python-backend.instructions.md`) para customizações de framework e estrutura de projeto.

