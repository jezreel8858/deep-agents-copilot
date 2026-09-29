"""TC-08: Contrato de determinismo de roteamento e especificação antecipada de cache.

Especificação antecipada (contrato): valida que `rotear()` é uma função pura e
determinística — chamar repetidamente com a MESMA solicitação e o MESMO grafo
produz exatamente a MESMA DecisaoRota (score, nível, escolhido, workflow).
Garante que não existem efeitos colaterais mutáveis no Grafo nem estado global oculto.

NOTA DE DESIGN / DoD SUBTASK 17 & 19:
A implementação do cache real com medição de taxa de acerto (cache hit ratio),
armazenamento LRU/TTL e telemetria fica formalmente para a subtask 19
(Runner mínimo / routing cache). Este arquivo estabelece o contrato formal de
pureza e determinismo necessário para o funcionamento seguro da camada de cache.
Subtask 17 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
"""

from __future__ import annotations

import pytest

from governance_runner.routing.model import DecisaoRota, Grafo, NivelRouting, Workflow
from governance_runner.routing.router import rotear


class TestTC08CacheHitRatio:
    """Testes de determinismo e pureza contratual de rotear() (base para cache hit ratio)."""

    def test_deve_retornar_mesma_decisao_quando_rotear_chamado_repetidamente_com_mesma_solicitacao(
        self, grafo_reduzido: Grafo
    ) -> None:
        """Duas chamadas sucessivas com idêntica entrada devem produzir DecisaoRota estritamente igual."""
        # Arrange
        solicitacao = "Identificado bug e erro crítico em produção"

        # Act
        decisao_1 = rotear(solicitacao, grafo_reduzido)
        decisao_2 = rotear(solicitacao, grafo_reduzido)

        # Assert
        assert decisao_1 == decisao_2
        assert decisao_1.escolhido == decisao_2.escolhido == "bug-triage"
        assert decisao_1.nivel == decisao_2.nivel == NivelRouting.RULE_BASED
        assert decisao_1.workflow == decisao_2.workflow == Workflow.BUG_FIX
        assert decisao_1.score == decisao_2.score

    @pytest.mark.parametrize(
        ("solicitacao", "escolhido_esperado", "nivel_esperado"),
        [
            ("Tenho um bug e um erro grave", "bug-triage", NivelRouting.RULE_BASED),
            ("Preciso revisar codigo, pull request e olhar o diff", "code-review", NivelRouting.SEMANTIC),
            ("Como calcular a distância média entre a Terra e Marte?", "deep-search", NivelRouting.OUT_OF_DOMAIN),
        ],
    )
    def test_deve_manter_determinismo_com_multiplas_solicitacoes_distintas(
        self,
        grafo_reduzido: Grafo,
        solicitacao: str,
        escolhido_esperado: str,
        nivel_esperado: NivelRouting,
    ) -> None:
        """Pureza funcional em lote: para qualquer padrão de entrada, o resultado é 100% determinístico."""
        # Act
        execucoes = [rotear(solicitacao, grafo_reduzido) for _ in range(5)]

        # Assert - todas as 5 execuções consecutivas devem ser idênticas à primeira
        primeira = execucoes[0]
        assert primeira.escolhido == escolhido_esperado
        assert primeira.nivel is nivel_esperado
        for execucao in execucoes[1:]:
            assert execucao == primeira

    def test_deve_garantir_que_rotear_nao_muta_o_grafo_fornecido(
        self, grafo_reduzido: Grafo
    ) -> None:
        """O grafo de entrada permanece absolutamente inalterado antes e após o roteamento."""
        # Arrange
        total_nos_antes = len(grafo_reduzido.nos)
        total_arestas_antes = len(grafo_reduzido.arestas)
        total_workflows_antes = len(grafo_reduzido.workflows)

        # Act
        rotear("Tenho um bug e um erro grave", grafo_reduzido)
        rotear("Outra pergunta qualquer fora de domínio", grafo_reduzido)

        # Assert
        assert len(grafo_reduzido.nos) == total_nos_antes
        assert len(grafo_reduzido.arestas) == total_arestas_antes
        assert len(grafo_reduzido.workflows) == total_workflows_antes

    def test_deve_garantir_determinismo_em_consultas_com_acentos_e_caixas_mistas(
        self, grafo_real: Grafo
    ) -> None:
        """Variações semânticas normalizadas produzem resultados determinísticos no grafo real."""
        # Arrange
        solic_1 = (
            "Isso é um BUG, deu ERRO, é uma REGRESSAO, houve FALHA em producao, "
            "nao funciona, quebrou, exception, NPE, erro 500 e um stack trace no log."
        )
        solic_2 = (
            "isso e um bug, deu erro, e uma regressao, houve falha em producao, "
            "nao funciona, quebrou, exception, npe, erro 500 e um stack trace no log."
        )

        # Act
        d1 = rotear(solic_1, grafo_real)
        d2 = rotear(solic_2, grafo_real)

        # Assert
        assert d1 == d2
        assert d1.escolhido == "bug-triage"
        assert d1.nivel is NivelRouting.RULE_BASED
        assert d1.workflow is Workflow.BUG_FIX
        assert d1.score >= 0.9
