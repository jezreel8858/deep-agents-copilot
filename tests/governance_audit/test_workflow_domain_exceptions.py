"""
test_workflow_domain_exceptions.py — Validação determinística de exceções de domínio em workflows canônicos.

Quality Gate que garante:
1. As etapas 5 e 6 (red_test_authoring e green_implementation) de WORKFLOW-FEATURE-DEVELOPMENT
   em routing-graph.yaml possuem a anotação excecao_dominio_frontend documentando o desvio Test-Last
   do Angular (R-050).
2. Proteção estrita contra remoção acidental dessa documentação de exceção em refatorações futuras.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_GRAPH_PATH = REPO_ROOT / ".github" / "agents" / "routing-graph.yaml"


@pytest.fixture(scope="session")
def routing_graph_data() -> dict:
    """Carrega o conteúdo parseado de routing-graph.yaml."""
    assert ROUTING_GRAPH_PATH.exists(), f"routing-graph.yaml não encontrado em {ROUTING_GRAPH_PATH}"
    content = ROUTING_GRAPH_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(content) or {}


def test_workflow_feature_development_declares_angular_test_last_exception(routing_graph_data: dict):
    """
    Garante que WORKFLOW-FEATURE-DEVELOPMENT documenta a inversão Test-Last/Implementation-First
    para o angular-router nas etapas 5 (red) e 6 (green).
    """
    workflows = routing_graph_data.get("workflows", [])
    wf_feat = next((wf for wf in workflows if wf.get("id") == "WORKFLOW-FEATURE-DEVELOPMENT"), None)
    assert wf_feat is not None, "WORKFLOW-FEATURE-DEVELOPMENT deve existir em routing-graph.yaml"

    estados = wf_feat.get("estados", [])
    step_red = next((e for e in estados if e.get("nome") == "red_test_authoring"), None)
    step_green = next((e for e in estados if e.get("nome") == "green_implementation"), None)

    assert step_red is not None, "Etapa 'red_test_authoring' deve existir em WORKFLOW-FEATURE-DEVELOPMENT"
    assert step_green is not None, "Etapa 'green_implementation' deve existir em WORKFLOW-FEATURE-DEVELOPMENT"

    # Validação da anotação de exceção na etapa 5 (Red)
    assert "excecao_dominio_frontend" in step_red, (
        "Etapa 5 (red_test_authoring) DEVE possuir o campo 'excecao_dominio_frontend'"
    )
    exc_red_text = str(step_red["excecao_dominio_frontend"])
    assert "angular-router" in exc_red_text, "excecao_dominio_frontend na etapa 5 deve citar 'angular-router'"
    assert "Test-Last" in exc_red_text or "Implementation-First" in exc_red_text, (
        "excecao_dominio_frontend na etapa 5 deve referenciar 'Test-Last' ou 'Implementation-First'"
    )

    # Validação da anotação de exceção na etapa 6 (Green)
    assert "excecao_dominio_frontend" in step_green, (
        "Etapa 6 (green_implementation) DEVE possuir o campo 'excecao_dominio_frontend'"
    )
    exc_green_text = str(step_green["excecao_dominio_frontend"])
    assert "angular-router" in exc_green_text, "excecao_dominio_frontend na etapa 6 deve citar 'angular-router'"
    assert "Test-Last" in exc_green_text or "Implementation-First" in exc_green_text, (
        "excecao_dominio_frontend na etapa 6 deve referenciar 'Test-Last' ou 'Implementation-First'"
    )
