"""
Testes unitários de `graph_loader.py` (subtask 2 do
PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md).

Usa fixtures reduzidas em `tests/routing_unit/fixtures/` para validar o
carregamento e compilação de grafo e invariantes estruturais específicas
(entry_point único, etapas contíguas, ausência de ciclos entre downstream,
flags RG-01/RG-03/RG-04 e tabela de transição).
Validações de schema e referências cruzadas são cobertas canonicamente por
`test_TC07_graph_schema_validation.py` e `test_graph_consistency_cross_ref.py`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner.routing.graph_loader import (
    GraphValidationError,
    carregar_grafo,
    compilar_tabela_transicao,
)
from governance_runner.routing.model import TipoNo, Workflow

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCHEMA_PATH = (
    Path(__file__).parents[2]
    / "src"
    / "governance_runner"
    / "routing"
    / "routing-graph.schema.json"
)


def _fixture(nome: str) -> Path:
    return FIXTURES_DIR / nome


class TestCarregarGrafoCasoFeliz:
    """Carregamento de um grafo válido reduzido."""

    def test_carrega_nos_e_arestas_sem_excecao(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        assert "agent-router" in grafo.nos
        assert "bug-triage" in grafo.nos
        assert len(grafo.nos_por_id) == 7
        assert len(grafo.arestas) == 6

    def test_entry_point_unico_e_identificado(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        entry_points = [n for n in grafo.nos_por_id if n.tipo is TipoNo.ENTRY_POINT]
        assert len(entry_points) == 1
        assert entry_points[0].id == "agent-router"

    def test_workflows_compilados_com_etapas_contiguas(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        bug_fix = next(w for w in grafo.workflows if w.id is Workflow.BUG_FIX)
        assert len(bug_fix.etapas) == 3
        assert bug_fix.etapas[0].proxima == 2
        assert bug_fix.etapas[2].proxima is None

    def test_rg04_agent_pipe_separado_armazenado_sem_resolver(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        bug_fix = next(w for w in grafo.workflows if w.id is Workflow.BUG_FIX)
        etapa_2 = bug_fix.etapas[1]
        assert etapa_2.agent_permitidos == frozenset({"domain-router", "specialist-bug-fixer"})
        assert etapa_2.requer_aprovacao is True

    def test_rg04_agents_permitidos_lista_yaml_suportada(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        analise = next(w for w in grafo.workflows if w.id is Workflow.TECHNICAL_ANALYSIS)
        assert analise.etapas[0].agent_permitidos == frozenset({"code-review", "deep-search"})

    def test_rg01_condicao_tipo_default_keyword_based(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        aresta_sem_tipo = next(a for a in grafo.arestas if a.para == "bug-triage")
        assert aresta_sem_tipo.condicoes.tipo == "keyword_based"

    def test_rg01_condicao_tipo_explicito_preservado(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        aresta_health = next(a for a in grafo.arestas if a.para == "binding-initializer")
        assert aresta_health.condicoes.tipo == "health_check"

    def test_rg03_politica_desvio_default_strict(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        for aresta in grafo.arestas:
            assert aresta.condicoes.politica_desvio == "strict"

    def test_wildcard_de_downstream_nao_quebra_carregamento(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)

        aresta_wildcard = next(a for a in grafo.arestas if a.de == "*downstream")
        assert aresta_wildcard.para == "agent-router"
        assert aresta_wildcard.condicoes.regra == "R-042"


class TestCompilarTabelaTransicao:
    """Compilação de `TabelaTransicao` a partir de um `Grafo` válido."""

    def test_tabela_possui_entrada_por_workflow_e_etapa(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)
        tabela = compilar_tabela_transicao(grafo)

        assert (Workflow.BUG_FIX, 1) in tabela.etapas
        assert (Workflow.BUG_FIX, 2) in tabela.etapas
        assert (Workflow.BUG_FIX, 3) in tabela.etapas
        assert (Workflow.TECHNICAL_ANALYSIS, 1) in tabela.etapas

    def test_tabela_expoe_catalogo_com_nos_do_grafo(self) -> None:
        grafo = carregar_grafo(_fixture("valid_graph.yaml"), SCHEMA_PATH)
        tabela = compilar_tabela_transicao(grafo)

        assert "agent-router" in tabela.catalogo.agentes


class TestInvariantesEstruturaisDoGrafo:
    """Invariantes estruturais obrigatórias — violações levantam `GraphValidationError`."""

    def test_ausencia_de_entry_point_levanta_erro(self) -> None:
        with pytest.raises(GraphValidationError, match="entry_point"):
            carregar_grafo(_fixture("missing_entry_point.yaml"), SCHEMA_PATH)

    def test_entry_point_duplicado_levanta_erro(self) -> None:
        with pytest.raises(GraphValidationError, match="entry_point"):
            carregar_grafo(_fixture("duplicate_entry_point.yaml"), SCHEMA_PATH)

    def test_etapas_nao_contiguas_levanta_erro(self) -> None:
        with pytest.raises(GraphValidationError, match="não contíguas"):
            carregar_grafo(_fixture("etapas_nao_contiguas.yaml"), SCHEMA_PATH)

    def test_ciclo_entre_nos_downstream_levanta_erro(self) -> None:
        with pytest.raises(GraphValidationError, match="Ciclo detectado"):
            carregar_grafo(_fixture("ciclo_entre_downstream.yaml"), SCHEMA_PATH)

    def test_no_downstream_orfao_sem_aresta_de_entrada_nao_e_erro(self) -> None:
        """Invariante 5 é checagem de CICLO, não de cobertura total."""
        grafo = carregar_grafo(_fixture("no_orfao_sem_ciclo.yaml"), SCHEMA_PATH)
        assert "adapter-generator" in grafo.nos


class TestGrafoRealDoRepositorio:
    """Smoke test contra o `routing-graph.yaml` real (~37 nós / ~42 arestas)."""

    def test_carrega_grafo_real_sem_excecao(self) -> None:
        caminho_real = (
            Path(__file__).parents[4] / ".github" / "agents" / "routing-graph.yaml"
        )
        if not caminho_real.exists():
            pytest.skip("routing-graph.yaml real não encontrado neste checkout")

        grafo = carregar_grafo(caminho_real, SCHEMA_PATH)

        assert len(grafo.nos_por_id) >= 30
        assert len(grafo.arestas) >= 30
        entry_points = [n for n in grafo.nos_por_id if n.tipo is TipoNo.ENTRY_POINT]
        assert len(entry_points) == 1
