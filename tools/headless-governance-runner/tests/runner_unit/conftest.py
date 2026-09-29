"""Fixtures compartilhadas para a suite tests/runner_unit (subtask 19)."""

from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner.routing.graph_loader import carregar_grafo
from governance_runner.routing.model import Grafo

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCHEMA_PATH = (
    Path(__file__).parents[2]
    / "src"
    / "governance_runner"
    / "routing"
    / "routing-graph.schema.json"
)


@pytest.fixture(scope="session")
def grafo_agent_audit() -> Grafo:
    """Grafo reduzido contendo o nó `agent-auditor` para os testes do runner (agent-audit)."""
    return carregar_grafo(FIXTURES_DIR / "agent_audit_graph.yaml", SCHEMA_PATH)
