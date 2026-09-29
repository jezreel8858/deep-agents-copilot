"""TC-02: Os 4 níveis da política de cascata de roteamento.

Valida os 4 thresholds contratuais (§7.2 do blueprint):
    - RULE_BASED: score >= 0.9
    - SEMANTIC: 0.7 <= score < 0.9
    - LLM_ASSISTED: 0.5 <= score < 0.7
    - OUT_OF_DOMAIN: score < 0.5
Inclui também a resolução determinística da zona de ambiguidade (Δ <= 0.05).
Subtask 9 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
"""

from __future__ import annotations

import pytest

from governance_runner.routing.model import Grafo, NivelRouting
from governance_runner.routing.router import rotear


class TestTC02CascadeThresholds:
    """Testes dos 4 níveis de cascata e thresholds contratuais."""

    def test_deve_classificar_como_rule_based_quando_score_maior_ou_igual_noventa_porcento(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Score >= 0.9 (ex.: 2 de 2 keywords = 1.0) classifica como RULE_BASED."""
        # Arrange - 2/2 keywords de bug-triage: "bug", "erro"
        solicitacao = "Detectamos um bug e um erro fatal"

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.nivel is NivelRouting.RULE_BASED
        assert decisao.score >= 0.9
        assert decisao.escolhido == "bug-triage"

    def test_deve_classificar_como_semantic_quando_score_entre_setenta_e_noventa_porcento(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Score >= 0.7 e < 0.9 (ex.: 3 de 4 keywords = 0.75) classifica como SEMANTIC."""
        # Arrange - 3/4 keywords de code-review: "revisar codigo", "pull request", "diff" (sem "merge")
        solicitacao = "Preciso revisar codigo, olhar o pull request e analisar o diff deste branch"

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.nivel is NivelRouting.SEMANTIC
        assert 0.7 <= decisao.score < 0.9
        assert decisao.escolhido == "code-review"
        assert decisao.score == pytest.approx(0.75)

    def test_deve_classificar_como_llm_assisted_quando_score_entre_cinquenta_e_setenta_porcento(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Score >= 0.5 e < 0.7 (ex.: 2 de 4 keywords = 0.5) classifica como LLM_ASSISTED."""
        # Arrange - 2/4 keywords de code-review: "revisar codigo", "diff"
        solicitacao = "Vou apenas revisar codigo observando o diff gerado"

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.nivel is NivelRouting.LLM_ASSISTED
        assert 0.5 <= decisao.score < 0.7
        assert decisao.escolhido == "code-review"
        assert decisao.score == pytest.approx(0.50)

    def test_deve_classificar_como_out_of_domain_quando_score_menor_que_cinquenta_porcento(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Score < 0.5 (ex.: 1 de 4 keywords = 0.25) cai na cascata para OUT_OF_DOMAIN."""
        # Arrange - apenas 1/4 keywords de code-review: "diff"
        solicitacao = "Exiba apenas o diff para eu ver o que mudou"

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.nivel is NivelRouting.OUT_OF_DOMAIN
        assert decisao.score == pytest.approx(0.25)
        # OUT_OF_DOMAIN ativa o nó de fallback primário (deep-search)
        assert decisao.escolhido == "deep-search"

    def test_deve_desempatar_por_prioridade_na_zona_de_ambiguidade_quando_delta_menor_ou_igual_cinco_centesimos(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Quando dois candidatos têm Δ <= 0.05 e scores > 0.5, a prioridade mais alta desempata."""
        # Arrange:
        # code-review: 3/4 keywords = 0.75 (prioridade 1.0)
        # security-review: 7/10 keywords = 0.70 (prioridade 2.0)
        # Δ = 0.05 -> zona de ambiguidade -> security-review vence pela prioridade 2.0 > 1.0.
        solicitacao = (
            "Preciso revisar codigo, revisar pull request e olhar o diff. "
            "Tambem e importante revisar seguranca, checar vulnerabilidade, "
            "autenticacao, token, senha e possivel vazamento por exploit."
        )

        # Act
        decisao = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao.escolhido == "security-review"
        assert decisao.score == pytest.approx(0.70)
        assert decisao.nivel is NivelRouting.SEMANTIC
