from __future__ import annotations
import pytest
from pathlib import Path
import yaml
import json

REPO_ROOT = Path(__file__).resolve().parents[2]

@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT

@pytest.fixture(scope="session")
def routing_graph(repo_root) -> dict:
    graph_path = repo_root / ".github" / "agents" / "routing-graph.yaml"
    with open(graph_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def casos_roteamento(repo_root) -> dict:
    casos_path = repo_root / ".github" / "agents" / "evals" / "casos-roteamento.yaml"
    with open(casos_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def otel_skill_content(repo_root) -> str:
    skill_path = repo_root / ".github" / "skills" / "agent-observability-otel" / "SKILL.md"
    with open(skill_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="session")
def collector_config_content(repo_root) -> str:
    config_path = repo_root / "tools" / "otel-langfuse" / "otel-collector-config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return f.read()
