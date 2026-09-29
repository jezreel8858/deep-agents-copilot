"""TC-01: Roteamento com match direto e óbvio de keyword (score alto, único candidato claro).

Cobre o caso isolado onde a solicitação do usuário contém keywords óbvias e
específicas, resultando em score >= 0.9 e roteamento determinístico RULE_BASED.
Subtask 8 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
"""

from __future__ import annotations

import pytest

from governance_runner.routing.model import Grafo, NivelRouting, Workflow
from governance_runner.routing.router import rotear


class TestTC01DirectMatch:
    """Testes de caso canônico TC-01: match direto rule-based."""

    def test_deve_rotear_rule_based_quando_match_direto_obvio_palavras_chave(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Match completo de todas as keywords de bug-triage resulta em RULE_BASED e score 1.0."""
        # Arrange
        solicitacao = "Tenho um bug e também um erro no sistema"

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.escolhido == "bug-triage"
        assert decisao.nivel is NivelRouting.RULE_BASED
        assert decisao.score == pytest.approx(1.0)

    def test_deve_associar_workflow_quando_candidato_escolhido_for_etapa_inicial(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Quando o agente escolhido for a etapa 1 de um workflow, o workflow deve ser preenchido."""
        # Arrange
        solicitacao = "Apareceu um bug e um erro grave no checkout"

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.workflow is Workflow.BUG_FIX

    def test_deve_rotear_rule_based_no_grafo_real_quando_solicitacao_tiver_keywords_criticas(
        self, grafo_real: Grafo
    ) -> None:
        """No grafo real de produção, match direto leva ao bug-triage com workflow associado."""
        # Arrange
        solicitacao = (
            "Isso é um bug, deu erro, é uma regressao, houve falha em producao, "
            "nao funciona, nao consigo acessar, quebrou, apareceu exception, NPE, "
            "erro 500 e um stack trace no log."
        )

        # Act
        decisao = rotear(solicitacao, grafo_real)

        # Assert
        assert decisao.escolhido == "bug-triage"
        assert decisao.nivel is NivelRouting.RULE_BASED
        assert decisao.workflow is Workflow.BUG_FIX
        assert decisao.score >= 0.9

    def test_deve_rotear_rule_based_para_code_review_no_grafo_real(
        self, grafo_real: Grafo
    ) -> None:
        """Match direto com keywords de code review no grafo real de produção."""
        # Arrange
        solicitacao = (
            "Preciso revisar codigo, fazer code review, essa e uma revisao antes "
            "do merge, vou analisar pull request, revisar diff e revisar pr."
        )

        # Act
        decisao = rotear(solicitacao, grafo_real)

        # Assert
        assert decisao.escolhido == "code-review"
        assert decisao.nivel is NivelRouting.RULE_BASED
        assert decisao.score >= 0.9

    def test_deve_lancar_value_error_quando_solicitacao_estiver_vazia_ou_apenas_espacos(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Solicitação vazia ou composta exclusivamente por espaços deve ser rejeitada."""
        # Act & Assert
        with pytest.raises(ValueError, match="não pode ser vazia"):
            rotear("", grafo_reduzido)

        with pytest.raises(ValueError, match="não pode ser vazia"):
            rotear("   \t\n  ", grafo_reduzido)
