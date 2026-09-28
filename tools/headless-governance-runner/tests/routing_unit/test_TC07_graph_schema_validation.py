"""TC-07: Validação de routing-graph.yaml contra routing-graph.schema.json.

Cobre pelo menos 3 anomalias sintáticas distintas:
    1. Campo obrigatório ausente em nó ('id' ou 'tipo').
    2. Campo obrigatório ausente em aresta ('de' ou 'para').
    3. Campo obrigatório ausente em workflow ('id' ou 'estados').
    4. Tipo de dado incorreto (ex.: 'nos' não sendo lista).
    5. YAML malformado sintaticamente.
Todas devem levantar GraphValidationError explícito, nunca exceções genéricas.
Subtask 14 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner.routing.graph_loader import GraphValidationError, carregar_grafo


class TestTC07GraphSchemaValidation:
    """Testes de schema JSON e integridade sintática do grafo."""

    def test_deve_lancar_graph_validation_error_quando_campo_obrigatorio_ausente_em_no(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Anomalia 1: nó sem o campo obrigatório 'tipo' deve levantar GraphValidationError."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    # 'tipo' ausente
workflows: []
arestas: []
"""
        yaml_path = tmp_path / "missing_tipo_no.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="routing-graph.yaml falhou na validação de schema"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_lancar_graph_validation_error_quando_campo_obrigatorio_ausente_em_aresta(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Anomalia 2: aresta sem o campo obrigatório 'para' deve levantar GraphValidationError."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    tipo: entry_point
workflows: []
arestas:
  - de: agent-router
    # 'para' ausente
"""
        yaml_path = tmp_path / "missing_para_aresta.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="routing-graph.yaml falhou na validação de schema"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_lancar_graph_validation_error_quando_campo_obrigatorio_ausente_em_workflow(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Anomalia 3: workflow sem 'estados' obrigatório deve levantar GraphValidationError."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    tipo: entry_point
workflows:
  - id: WORKFLOW-BUG-FIX
    nome: "Bug Fix"
    # 'estados' ausente
arestas: []
"""
        yaml_path = tmp_path / "missing_estados_workflow.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="routing-graph.yaml falhou na validação de schema"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_lancar_graph_validation_error_quando_tipo_de_dado_invalido(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Anomalia 4: 'nos' fornecido como string em vez de lista deve ser rejeitado."""
        # Arrange
        conteudo = """
version: "1.0"
nos: "isso-deveria-ser-uma-lista"
workflows: []
arestas: []
"""
        yaml_path = tmp_path / "wrong_type.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="routing-graph.yaml falhou na validação de schema"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_lancar_graph_validation_error_quando_yaml_malformado(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Anomalia 5: sintaxe YAML inválida (dois pontos soltos/indentação corrompida)."""
        # Arrange
        conteudo = """
version: "1.0"
nos:
  - id: agent-router
    tipo: entry_point
  corrompido: : : : [invalido
"""
        yaml_path = tmp_path / "invalid_syntax.yaml"
        yaml_path.write_text(conteudo, encoding="utf-8")

        # Act & Assert
        with pytest.raises(GraphValidationError, match="YAML malformado"):
            carregar_grafo(yaml_path, caminho_schema)

    def test_deve_lancar_graph_validation_error_quando_arquivo_yaml_inexistente(
        self, caminho_schema: Path, tmp_path: Path
    ) -> None:
        """Arquivo inexistente deve levantar GraphValidationError com indicação clara."""
        # Arrange
        yaml_fantasma = tmp_path / "arquivo_que_nao_existe.yaml"

        # Act & Assert
        with pytest.raises(GraphValidationError, match="Não foi possível ler"):
            carregar_grafo(yaml_fantasma, caminho_schema)
