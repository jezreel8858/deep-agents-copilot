"""Testes de estabilidade e unicidade do edge_id canônico (B1-03 / CA-03)."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from governance_runner.synth.routing_graph import (
    calcular_edge_id,
    carregar_snapshot_grafo,
)


def _grafo_minimo(arestas: list[dict]) -> dict:
    return {
        "version": "1.0",
        "description": "Grafo sintetico de teste para edge_id",
        "nos": [
            {"id": "agent-router", "tipo": "entry_point", "descricao": "Router"},
            {"id": "python-router", "tipo": "domain_router", "descricao": "Python Router"},
            {"id": "bug-triage", "tipo": "downstream", "descricao": "Bug Triage"},
        ],
        "workflows": [{"id": "WORKFLOW-BUG-FIX", "estados": [{"etapa": 1, "nome": "init", "agent": "bug-triage"}]}],
        "arestas": arestas,
        "politica_cascata": {
            "nivel_1_rule_based": {"threshold": 0.9, "acao": "rule"},
            "nivel_2_semantic": {"threshold": 0.7, "acao": "sem"},
            "nivel_3_llm_based": {"threshold": 0.5, "acao": "llm"},
            "escalonamento_humano": {"threshold": 0.0, "acao": "ask"},
        },
    }


def test_edge_id_invariante_a_reordenacao_do_yaml(tmp_path: Path) -> None:
    """CA-03: Permutar a ordem de arestas e keywords no YAML não altera nenhum edge_id."""
    a1 = {
        "de": "agent-router",
        "para": "python-router",
        "prioridade": 1,
        "threshold_score": 0.7,
        "nivel_routing": "rule-based",
        "condicoes": {
            "tipo": "keyword_based",
            "keywords": ["fastapi", "pydantic", "pytest"],
        },
    }
    a2 = {
        "de": "agent-router",
        "para": "bug-triage",
        "prioridade": 2,
        "threshold_score": 0.6,
        "nivel_routing": "rule-based",
        "condicoes": {
            "tipo": "keyword_based",
            "regra": "erro_producao_critico",
            "keywords": ["incidente", "stacktrace"],
        },
    }
    a1_reord = {
        **a1,
        "condicoes": {
            "tipo": "keyword_based",
            "keywords": ["pytest", "FASTAPI", "pydantic", "fastapi"],
        },
    }

    p_original = tmp_path / "grafo_a.yaml"
    p_permutado = tmp_path / "grafo_b.yaml"
    p_original.write_text(yaml.safe_dump(_grafo_minimo([a1, a2]), sort_keys=False), encoding="utf-8")
    p_permutado.write_text(yaml.safe_dump(_grafo_minimo([a2, a1_reord]), sort_keys=True), encoding="utf-8")

    snap_a = carregar_snapshot_grafo(p_original, repo_root=tmp_path)
    snap_b = carregar_snapshot_grafo(p_permutado, repo_root=tmp_path)

    assert snap_a.sha256 != snap_b.sha256
    assert [r.edge_id for r in snap_a.rotas] == [r.edge_id for r in snap_b.rotas]
    assert len(snap_a.rotas) == 2
    for r in snap_a.rotas:
        assert r.edge_id.startswith("e-") and len(r.edge_id) == 14


def test_colisao_edge_id_falha_explicitamente(tmp_path: Path) -> None:
    """CA-03: Duas arestas com mesmo (de, para, prioridade, tipo, discriminador) geram ValueError."""
    aresta_dup_1 = {
        "de": "agent-router",
        "para": "python-router",
        "prioridade": 1,
        "threshold_score": 0.7,
        "nivel_routing": "rule-based",
        "condicoes": {
            "tipo": "keyword_based",
            "keywords": ["fastapi", "asyncio"],
        },
    }
    aresta_dup_2 = {
        "de": "agent-router",
        "para": "python-router",
        "prioridade": 1,
        "threshold_score": 0.85,
        "nivel_routing": "rule-based",
        "condicoes": {
            "tipo": "keyword_based",
            "keywords": ["ASYNCIO", "fastapi"],
        },
    }
    p = tmp_path / "colisao.yaml"
    p.write_text(yaml.safe_dump(_grafo_minimo([aresta_dup_1, aresta_dup_2])), encoding="utf-8")

    with pytest.raises(ValueError, match="Colisao de edge_id"):
        carregar_snapshot_grafo(p, repo_root=tmp_path)


def test_calcular_edge_id_discriminador_regra_vs_keywords() -> None:
    """Regras distintas ou prioridades distintas produzem edge_ids distintos; normalização estabiliza."""
    id_kw_1 = calcular_edge_id(
        de="agent-router",
        para="python-router",
        prioridade=1,
        tipo="keyword_based",
        keywords=["FastAPI", "SQLAlchemy"],
    )
    id_kw_2 = calcular_edge_id(
        de="agent-router",
        para="python-router",
        prioridade=1.0,
        tipo=None,
        keywords=["sqlalchemy", "fastapi", "FASTAPI"],
    )
    assert id_kw_1 == id_kw_2

    id_prio_diff = calcular_edge_id(
        de="agent-router",
        para="python-router",
        prioridade=2,
        tipo="keyword_based",
        keywords=["FastAPI", "SQLAlchemy"],
    )
    id_regra = calcular_edge_id(
        de="agent-router",
        para="python-router",
        prioridade=1,
        tipo="keyword_based",
        regra="regra_explicita",
        keywords=["FastAPI", "SQLAlchemy"],
    )
    assert id_kw_1 != id_prio_diff
    assert id_kw_1 != id_regra
