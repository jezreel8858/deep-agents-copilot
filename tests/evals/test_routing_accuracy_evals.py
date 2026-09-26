from __future__ import annotations
import pytest
from pathlib import Path

def test_scn_rout_01_canonical_routing_cases_defined(casos_roteamento):
    """SCN-ROUT-01: Garante que o dataset canônico de roteamento cobre os casos essenciais."""
    canonicos = casos_roteamento.get("canonicos", [])
    ambiguos = casos_roteamento.get("ambiguos", [])
    assert len(canonicos) >= 10, f"Deve haver pelo menos 10 casos canônicos (encontrados: {len(canonicos)})."
    assert len(ambiguos) >= 5, f"Deve haver pelo menos 5 casos ambíguos (encontrados: {len(ambiguos)})."
    
    # Valida estrutura de cada caso
    for caso in canonicos:
        assert "id" in caso, "Cada caso canônico deve ter id."
        assert "input" in caso or "entrada" in caso or "prompt" in caso, "Cada caso canônico deve ter input/entrada."
        assert "expected" in caso or "esperado" in caso, "Cada caso deve ter rota/agente esperado."

def test_scn_rout_02_routing_graph_connected(routing_graph):
    """SCN-ROUT-02: Garante integridade topológica do routing-graph.yaml."""
    nos = routing_graph.get("nos", [])
    node_ids = {n.get("id") for n in nos if isinstance(n, dict)}
    assert "agent-router" in node_ids, "agent-router deve ser o nó central do grafo."
    
    arestas = routing_graph.get("arestas", [])
    assert len(arestas) >= 10, "Grafo de roteamento deve conter ao menos 10 arestas mapeadas."
    
    # Origem e destino de cada aresta devem existir nos nós ou ser wildcard (*)
    for aresta in arestas:
        origem = aresta.get("de")
        destino = aresta.get("para")
        for o in [x.strip() for x in origem.split("|")]:
            assert o.startswith("*") or o in node_ids, f"Origem '{o}' inválida."
        for d in [x.strip() for x in destino.split("|")]:
            assert d.startswith("*") or d in node_ids, f"Destino '{d}' inválido."

def test_scn_rout_03_anti_sticky_session_policy(repo_root):
    """SCN-ROUT-03: Garante que o princípio Anti-Sticky Session (R-042 / R-052) está documentado e normatizado."""
    claude_md = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")
    assert "R-042" in claude_md, "CLAUDE.md deve normatizar R-042 (Re-triagem Obrigatória por Turno - Anti Sticky-Session)."
    assert "R-052" in claude_md, "CLAUDE.md deve normatizar R-052 (Reset Mandatório pós-Conclusão de Workflow)."
