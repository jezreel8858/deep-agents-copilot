"""TC-06: Bloqueio estrito de transições ilegais na máquina de estados.

Valida que qualquer violação das regras R-037, R-050 e R-064 resulte em
TransicaoInvalidaError tipada:
    - Pular etapa (avanço não contíguo: etapa 1 -> etapa 3).
    - Retroceder etapa (etapa 2 -> etapa 1).
    - Agente solicitado fora de agent_permitidos.
    - Falta de aprovação humana quando a etapa exige checkpoint (requer_aprovacao=True).
    - Tentativa de originar ou trocar de workflow fora da Fase.ROUTER.
Subtask 13 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
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
from governance_runner.routing.state_machine import TransicaoInvalidaError, transicionar


class TestTC06StateMachineIllegalTransition:
    """Testes de bloqueio estrito de transições ilegais."""

    def test_deve_bloquear_transicao_quando_pular_etapa_com_transicao_invalida_error(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """R-050: pular etapas (ex.: 1 -> 3) deve levantar TransicaoInvalidaError."""
        # Arrange
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=1,
            agente_ativo="bug-triage",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=3,
            agente_solicitado="specialist-bug-fixer",
        )

        # Act & Assert
        with pytest.raises(TransicaoInvalidaError, match="R-050"):
            transicionar(sessao, evento, tabela_real)

    def test_deve_bloquear_transicao_quando_retroceder_etapa_com_transicao_invalida_error(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """R-050: retroceder etapas (ex.: 2 -> 1) deve levantar TransicaoInvalidaError."""
        # Arrange
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=2,
            agente_ativo="specialist-unit-test-writer",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=1,
            agente_solicitado="bug-triage",
        )

        # Act & Assert
        with pytest.raises(TransicaoInvalidaError, match="R-050"):
            transicionar(sessao, evento, tabela_real)

    def test_deve_bloquear_transicao_quando_agente_solicitado_fora_de_agent_permitidos(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Guard clause 3: agente não autorizado na etapa deve levantar TransicaoInvalidaError."""
        # Arrange
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=1,
            agente_ativo="bug-triage",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=2,
            agente_solicitado="agente-completamente-invalido",
        )

        # Act & Assert
        with pytest.raises(TransicaoInvalidaError, match="não está entre os agentes permitidos"):
            transicionar(sessao, evento, tabela_real)

    def test_deve_bloquear_transicao_quando_falta_aprovacao_humana_em_etapa_com_checkpoint(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """R-064: etapa 3 de FEATURE_DEVELOPMENT exige checkpoint humano; avanço sem aprovação é barrado."""
        # Arrange - etapa 3 do feature development tem checkpoint_humano
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.FEATURE_DEVELOPMENT,
            etapa=2,
            agente_ativo="requirements-analyst",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=3,
            agente_solicitado="tech-solution-architect",
            aprovacao_concedida=False,  # Sem concessão de aprovação
        )

        # Act & Assert
        with pytest.raises(TransicaoInvalidaError, match="R-064"):
            transicionar(sessao, evento, tabela_real)

    def test_deve_permitir_avanco_quando_aprovacao_humana_concedida_em_etapa_com_checkpoint(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """R-064: com aprovacao_concedida=True, o avanço é aceito e registrado em sessao.aprovacoes."""
        # Arrange
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.FEATURE_DEVELOPMENT,
            etapa=2,
            agente_ativo="requirements-analyst",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=3,
            agente_solicitado="tech-solution-architect",
            aprovacao_concedida=True,
        )

        # Act
        nova = transicionar(sessao, evento, tabela_real)

        # Assert
        assert nova.etapa == 3
        assert nova.agente_ativo == "tech-solution-architect"
        assert "3" in nova.aprovacoes

    def test_deve_bloquear_troca_de_workflow_fora_da_fase_router(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """R-037: não é permitido originar ou trocar de workflow enquanto estiver em Fase.EM_WORKFLOW."""
        # Arrange
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=1,
            agente_ativo="bug-triage",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.DECISAO_ROTEAMENTO,
            workflow_solicitado=Workflow.TECHNICAL_ANALYSIS,
            agente_solicitado="code-knowledge-graph",
        )

        # Act & Assert
        with pytest.raises(TransicaoInvalidaError, match="R-037"):
            transicionar(sessao, evento, tabela_real)

    def test_deve_bloquear_quando_etapa_solicitada_inexistente_no_workflow(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Avanço para etapa inexistente na tabela compilada deve ser rejeitado."""
        # Arrange - BUG_FIX só tem 5 etapas
        sessao = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=5,
            agente_ativo="code-review",
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=6,
            agente_solicitado="code-review",
        )

        # Act & Assert
        with pytest.raises(TransicaoInvalidaError, match="R-050"):
            transicionar(sessao, evento, tabela_real)
