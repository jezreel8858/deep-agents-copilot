"""Idempotência e determinismo da máquina de estados.

Gap identificado pelo @test-strategy:
Garante que aplicar o MESMO evento de transição duas vezes seguidas sobre a mesma
Sessão de entrada produz o MESMO resultado idêntico, comprovando a pureza funcional
e a ausência de mutação colateral em state_machine.transicionar.
Subtask 16 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
"""

from __future__ import annotations

import pytest

from governance_runner.routing.model import (
    Evento,
    Fase,
    Sessao,
    TabelaTransicao,
    TipoEvento,
    Workflow,
)
from governance_runner.routing.state_machine import transicionar


class TestStateMachineIdempotency:
    """Testes de pureza funcional e idempotência de transições."""

    def test_deve_produzir_mesmo_resultado_quando_aplicar_mesmo_evento_duas_vezes_sobre_mesma_sessao(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Duas chamadas independentes com a mesma Sessao e o mesmo Evento geram Sessoes iguais."""
        # Arrange
        sessao_inicial = Sessao(
            fase=Fase.ROUTER,
            workflow=None,
            etapa=0,
            agente_ativo="agent-router",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.DECISAO_ROTEAMENTO,
            workflow_solicitado=Workflow.BUG_FIX,
            agente_solicitado="bug-triage",
        )

        # Act
        resultado_1 = transicionar(sessao_inicial, evento, tabela_real)
        resultado_2 = transicionar(sessao_inicial, evento, tabela_real)

        # Assert
        assert resultado_1 == resultado_2
        assert resultado_1.fase is Fase.EM_WORKFLOW
        assert resultado_1.workflow is Workflow.BUG_FIX
        assert resultado_1.etapa == 1
        assert resultado_1.agente_ativo == "bug-triage"

    def test_deve_garantir_imutabilidade_da_sessao_de_entrada_apos_transicao(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """A Sessao de entrada não deve ter nenhum de seus campos alterados após a chamada."""
        # Arrange
        sessao_inicial = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=1,
            agente_ativo="bug-triage",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=2,
            agente_solicitado="specialist-unit-test-writer",
        )

        # Act
        nova_sessao = transicionar(sessao_inicial, evento, tabela_real)

        # Assert
        assert sessao_inicial.fase is Fase.EM_WORKFLOW
        assert sessao_inicial.workflow is Workflow.BUG_FIX
        assert sessao_inicial.etapa == 1
        assert sessao_inicial.agente_ativo == "bug-triage"
        assert nova_sessao.etapa == 2

    def test_deve_manter_idempotencia_em_evento_de_deriva_detectada(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Evento de deriva aplicado repetidamente sobre a mesma sessão produz o mesmo reset."""
        # Arrange
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=3,
            agente_ativo="specialist-bug-fixer",
            aprovacoes=frozenset({"2"}),
        )
        evento_deriva = Evento(origem="drift-detector", tipo=TipoEvento.DERIVA_DETECTADA)

        # Act
        res_1 = transicionar(sessao, evento_deriva, tabela_real)
        res_2 = transicionar(sessao, evento_deriva, tabela_real)

        # Assert
        assert res_1 == res_2
        assert res_1.fase is Fase.ROUTER
        assert res_1.workflow is None
        assert res_1.etapa == 0
        assert res_1.agente_ativo == "agent-router"
        assert res_1.aprovacoes == frozenset({"2"})

    def test_deve_manter_idempotencia_em_evento_de_conclusao_de_workflow(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Evento de conclusão aplicado repetidamente produz idêntica transição para router."""
        # Arrange - etapa 5 é a última do BUG_FIX
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=5,
            agente_ativo="code-review",
        )
        evento_conclusao = Evento(
            origem="usuario",
            tipo=TipoEvento.CONCLUSAO_WORKFLOW,
            etapa_solicitada=5,
            agente_solicitado="code-review",
        )

        # Act
        res_1 = transicionar(sessao, evento_conclusao, tabela_real)
        res_2 = transicionar(sessao, evento_conclusao, tabela_real)

        # Assert
        assert res_1 == res_2
        assert res_1.fase is Fase.ROUTER
        assert res_1.workflow is None
        assert res_1.etapa == 0
