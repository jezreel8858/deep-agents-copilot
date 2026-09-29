"""TC-04: Caminho completo de fallback sob OUT_OF_DOMAIN.

Valida que quando uma solicitação não possui match de keyword (score 0.0) ou não atinge
o piso mínimo (score < 0.5), o roteador ativa o nível OUT_OF_DOMAIN e seleciona
o nó de tipo 'fallback' com maior prioridade declarada no grafo.
Subtask 11 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
"""

from __future__ import annotations

import dataclasses

import pytest

from governance_runner.routing.model import Grafo, NivelRouting
from governance_runner.routing.router import RoteamentoError, rotear


class TestTC04FallbackCascade:
    """Testes do caminho canônico TC-04: fallback sob OUT_OF_DOMAIN."""

    def test_deve_rotear_para_fallback_quando_nenhuma_keyword_corresponder(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Solicitação completamente fora de domínio sem keywords ativa OUT_OF_DOMAIN e fallback."""
        # Arrange
        solicitacao = "Qual é a previsão do tempo para amanhã em Lisboa?"

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.nivel is NivelRouting.OUT_OF_DOMAIN
        assert decisao.score == pytest.approx(0.0)
        # deep-search (prioridade 9) vence tech-solution-architect (prioridade 8)
        assert decisao.escolhido == "deep-search"
        assert decisao.workflow is None

    def test_deve_escolher_fallback_de_maior_prioridade_quando_houver_multiplos(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Entre múltiplos nós fallback disponíveis, prevalece o nó com maior prioridade de aresta."""
        # Arrange
        solicitacao = "Receita de bolo de chocolate tradicional"

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.escolhido == "deep-search"

    def test_deve_rotear_para_fallback_secundario_quando_primario_for_removido(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Se o fallback primário não existir, o próximo nó fallback elegível é selecionado."""
        # Arrange - grafo sem deep-search, mantendo tech-solution-architect
        grafo_sem_deep_search = dataclasses.replace(
            grafo_reduzido,
            nos_por_id=tuple(n for n in grafo_reduzido.nos_por_id if n.id != "deep-search"),
        )
        solicitacao = "Consulta culinária aleatória"

        # Act
        decisao = rotear(solicitacao, grafo_sem_deep_search)

        # Assert
        assert decisao.nivel is NivelRouting.OUT_OF_DOMAIN
        assert decisao.escolhido == "tech-solution-architect"

    def test_deve_lancar_roteamento_error_quando_grafo_nao_possuir_nenhum_fallback(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Grafo sem nenhum nó do tipo fallback deve falhar de forma fechada com RoteamentoError."""
        # Arrange - remove ambos os nós de fallback
        grafo_sem_fallback = dataclasses.replace(
            grafo_reduzido,
            nos_por_id=tuple(
                n for n in grafo_reduzido.nos_por_id
                if n.id not in {"deep-search", "tech-solution-architect"}
            ),
        )

        # Act & Assert
        with pytest.raises(RoteamentoError, match="não possui nó 'fallback'"):
            rotear("Qualquer pergunta fora de domínio", grafo_sem_fallback)

    def test_deve_rotear_para_fallback_no_grafo_real_quando_solicitacao_desconhecida(
        self, grafo_real: Grafo
    ) -> None:
        """No grafo real de produção, solicitações desconhecidas ativam o fallback oficial."""
        # Arrange
        solicitacao = "Quantos satélites naturais orbitam o planeta Saturno?"

        # Act
        decisao = rotear(solicitacao, grafo_real)

        # Assert
        assert decisao.nivel is NivelRouting.OUT_OF_DOMAIN
        assert decisao.escolhido in {"deep-search", "tech-solution-architect"}
