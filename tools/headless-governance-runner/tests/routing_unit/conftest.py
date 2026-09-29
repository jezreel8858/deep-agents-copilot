"""Fixtures compartilhadas para a suíte de testes unitários de routing (routing_unit).

Todas as fixtures que realizam leitura de disco ou compilação de grafo são
configuradas com escopo 'session' para garantir máxima performance, pureza
e determinismo na execução dos testes N1.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner.routing.graph_loader import carregar_grafo, compilar_tabela_transicao
from governance_runner.routing.model import Grafo, TabelaTransicao

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCHEMA_PATH = (
    Path(__file__).parents[2]
    / "src"
    / "governance_runner"
    / "routing"
    / "routing-graph.schema.json"
)
REAL_GRAPH_PATH = Path(__file__).parents[4] / ".github" / "agents" / "routing-graph.yaml"


@pytest.fixture(scope="session")
def caminho_schema() -> Path:
    """Caminho absoluto para o schema JSON do grafo."""
    return SCHEMA_PATH


@pytest.fixture(scope="session")
def caminho_grafo_real() -> Path:
    """Caminho absoluto para o routing-graph.yaml real de produção."""
    return REAL_GRAPH_PATH


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Diretório de fixtures reduzidas da suíte routing_unit."""
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def grafo_reduzido(caminho_schema: Path) -> Grafo:
    """Grafo reduzido para testes de scoring e thresholds de cascata."""
    return carregar_grafo(FIXTURES_DIR / "router_scoring.yaml", caminho_schema)


@pytest.fixture(scope="session")
def grafo_valido(caminho_schema: Path) -> Grafo:
    """Grafo reduzido para testes de máquina de estados e carregador."""
    return carregar_grafo(FIXTURES_DIR / "valid_graph.yaml", caminho_schema)


@pytest.fixture(scope="session")
def tabela_valida(grafo_valido: Grafo) -> TabelaTransicao:
    """Tabela de transição compilada a partir da fixture valid_graph.yaml."""
    return compilar_tabela_transicao(grafo_valido)


@pytest.fixture(scope="session")
def grafo_real(caminho_grafo_real: Path, caminho_schema: Path) -> Grafo:
    """Grafo real de produção compilado a partir de .github/agents/routing-graph.yaml."""
    if not caminho_grafo_real.exists():
        pytest.skip("routing-graph.yaml real não encontrado neste checkout")
    return carregar_grafo(caminho_grafo_real, caminho_schema)


@pytest.fixture(scope="session")
def tabela_real(grafo_real: Grafo) -> TabelaTransicao:
    """Tabela de transição compilada a partir do grafo real de produção."""
    return compilar_tabela_transicao(grafo_real)
