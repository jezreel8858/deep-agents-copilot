"""Testes da ACL read-only routing_graph.py (B1-03 / CA-02 / CA-07 / R-054)."""
from __future__ import annotations

import hashlib
import time
from unittest.mock import patch

from governance_runner.synth import routing_graph
from governance_runner.synth.routing_graph import (
    DEFAULT_ROUTING_GRAPH_REL_PATH,
    TIPOS_ARESTA_EXCLUIDOS,
    GrafoSnapshot,
    RotaGrafo,
    carregar_snapshot_grafo,
    resolver_aresta,
    rotas_validas,
)


def test_carregar_snapshot_grafo_real_exclui_pre_steps_e_inclui_security_gate() -> None:
    """CA-02: Carrega .github/agents/routing-graph.yaml real, exclui health_check/mandatory_pre_step e inclui security_gate."""
    snap = carregar_snapshot_grafo()
    assert len(snap.sha256) == 64
    assert snap.rotas
    assert snap.todas_rotas
    assert len(snap.todas_rotas) >= len(snap.rotas)

    tipos_validas = {r.tipo for r in snap.rotas}
    assert tipos_validas.isdisjoint(TIPOS_ARESTA_EXCLUIDOS)
    assert "security_gate" in tipos_validas
    assert "keyword_based" in tipos_validas
    assert all(r.de == "agent-router" and r.para != "agent-router" for r in snap.rotas)
    assert all(r.para in snap.nos for r in snap.rotas)

    caminho_real = routing_graph.resolver_caminho_routing_graph()
    assert caminho_real.as_posix().endswith(DEFAULT_ROUTING_GRAPH_REL_PATH.as_posix())
    assert hashlib.sha256(caminho_real.read_bytes()).hexdigest() == snap.sha256


def test_carregar_grafo_usa_schema_empacotado_fixo() -> None:
    """CA-07 / R-054 Zero Discovery: carregar_snapshot_grafo invoca carregar_grafo sempre com _SCHEMA_FIXO_PACOTE."""
    with patch.object(
        routing_graph, "carregar_grafo", wraps=routing_graph.carregar_grafo
    ) as spy_loader:
        snap = carregar_snapshot_grafo()
        assert snap.rotas
        assert spy_loader.call_count == 1
        args, _ = spy_loader.call_args
        assert args[1] == routing_graph._SCHEMA_FIXO_PACOTE
        assert routing_graph._SCHEMA_FIXO_PACOTE.name == "routing-graph.schema.json"
        assert routing_graph._SCHEMA_FIXO_PACOTE.exists()


def test_resolver_aresta_precedencia_e_matching_literal_sem_redos() -> None:
    """Testa resolução keyword, unique_target, priority, orphan e matching literal anti-ReDoS."""
    r_py_1 = RotaGrafo(
        edge_id="e-000000000001",
        de="agent-router",
        para="python-developer",
        tipo="keyword_based",
        regra=None,
        prioridade=2.0,
        threshold_score=0.7,
        nivel_routing="L1",
        keywords=("fastapi", "(z+)+$"),
    )
    r_py_2 = RotaGrafo(
        edge_id="e-000000000002",
        de="agent-router",
        para="python-developer",
        tipo="keyword_based",
        regra="fallback_py",
        prioridade=1.0,
        threshold_score=0.7,
        nivel_routing="L1",
        keywords=("pytest", "fixture"),
    )
    r_sec = RotaGrafo(
        edge_id="e-000000000003",
        de="agent-router",
        para="cybersecurity-advisor",
        tipo="security_gate",
        regra="owasp",
        prioridade=0.0,
        threshold_score=0.8,
        nivel_routing="L0",
        keywords=("owasp",),
    )
    snap = GrafoSnapshot(
        sha256="a" * 64,
        rotas=(r_py_1, r_py_2, r_sec),
        nos=frozenset({"agent-router", "python-developer", "cybersecurity-advisor"}),
        todas_rotas=(r_py_1, r_py_2, r_sec),
    )

    assert resolver_aresta("python-developer", "preciso configurar fastapi agora", snap) == (
        "e-000000000001",
        "keyword",
    )
    assert resolver_aresta("python-developer", "demanda generica de backend", snap) == (
        "e-000000000002",
        "priority",
    )
    assert resolver_aresta("cybersecurity-advisor", "revisao de ameacas", snap) == (
        "e-000000000003",
        "unique_target",
    )
    assert resolver_aresta("agente-inexistente", "qualquer texto", snap) == (None, "orphan")

    inicio = time.perf_counter()
    entrada_patologica = "y" * 5000 + "!"
    eid, kind = resolver_aresta("python-developer", entrada_patologica, snap)
    duracao = time.perf_counter() - inicio
    assert duracao < 0.1
    assert (eid, kind) == ("e-000000000002", "priority")

    apenas_sec = rotas_validas(snap, incluir_tipos={"security_gate"})
    assert [r.edge_id for r in apenas_sec] == ["e-000000000003"]
