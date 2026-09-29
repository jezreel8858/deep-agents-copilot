"""Validação de referências cruzadas e nós órfãos no grafo.

Gap identificado pelo @test-strategy:
Garante que referências órfãs em arestas (nó de origem ou destino não declarado em 'nos')
ou etapas de workflow com identificadores malformados/órfãos sejam sumariamente rejeitadas
com GraphValidationError explicito, nunca passando silenciosamente.
Subtask 15 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner.routing.graph_loader import GraphValidationError, carregar_grafo
from governance_runner.routing.model import Grafo


class TestGraphConsistencyCrossRef:
    """Testes de consistência referencial cruzada (anti referências órfãs)."""

    def test_deve_rejeitar_quando_aresta_referenciar_destino_inexistente_em_nos(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Aresta com 'para: no-fantasma' inexistente em 'nos' levanta GraphValidationError."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    tipo: entry_point
  - id: node-real
    tipo: downstream
workflows: []
arestas:
  - de: agent-router
    para: no-fantasma
    prioridade: 1
"""
        yaml_path = tmp_path / "aresta_destino_orfao.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="Aresta referencia nó inexistente: 'no-fantasma'"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_rejeitar_quando_aresta_referenciar_origem_inexistente_em_nos(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Aresta com 'de: no-fantasma' inexistente em 'nos' levanta GraphValidationError."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    tipo: entry_point
  - id: node-real
    tipo: downstream
workflows: []
arestas:
  - de: no-fantasma-origem
    para: node-real
    prioridade: 1
"""
        yaml_path = tmp_path / "aresta_origem_orfa.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="Aresta referencia nó inexistente: 'no-fantasma-origem'"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_rejeitar_quando_aresta_usar_wildcard_tipo_no_desconhecido(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Aresta com wildcard inexistente (ex.: '*tipo-desconhecido') levanta GraphValidationError."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    tipo: entry_point
workflows: []
arestas:
  - de: "*tipo-desconhecido"
    para: agent-router
    prioridade: 1
"""
        yaml_path = tmp_path / "wildcard_invalido.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="não corresponde a nenhum TipoNo conhecido"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_rejeitar_quando_etapa_workflow_declarar_agente_vazio(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Workflow com agente vazio na etapa levanta GraphValidationError."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    tipo: entry_point
workflows:
  - id: WORKFLOW-BUG-FIX
    nome: "Bug Fix"
    estados:
      - etapa: 1
        nome: "etapa1"
        agent: ""
arestas: []
"""
        yaml_path = tmp_path / "workflow_agente_vazio.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="declara agente vazio"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_rejeitar_quando_etapa_workflow_declarar_agente_com_token_sintaticamente_invalido(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Workflow com token que viola o padrão sintático kebab-case levanta GraphValidationError."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    tipo: entry_point
workflows:
  - id: WORKFLOW-BUG-FIX
    nome: "Bug Fix"
    estados:
      - etapa: 1
        nome: "etapa1"
        agent: "Agente Inválido! Com Espaço"
arestas: []
"""
        yaml_path = tmp_path / "workflow_agente_invalido.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="não resolvível sintaticamente"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_garantir_consistencia_referencial_completa_no_grafo_real(
        self, grafo_real: Grafo
    ) -> None:
        """Garante que todas as arestas concretas do grafo real referenciam nós existentes em grafo.nos."""
        # Arrange
        nos_validos = grafo_real.nos

        # Act & Assert
        for aresta in grafo_real.arestas:
            for origem in aresta.origens:
                if not origem.startswith("*"):
                    assert origem in nos_validos, f"Aresta com origem órfã no grafo real: '{origem}'"
            for destino in aresta.destinos:
                if not destino.startswith("*"):
                    assert destino in nos_validos, f"Aresta com destino órfão no grafo real: '{destino}'"
