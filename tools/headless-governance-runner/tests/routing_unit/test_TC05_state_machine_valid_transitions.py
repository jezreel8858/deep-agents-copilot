"""TC-05: Transições lícitas cobrindo workflows canônicos na máquina de estados.

Valida o avanço sequencial lícito (etapa n -> etapa n+1) e o ciclo de vida completo
de pelo menos 3 dos 9 workflows canônicos usando a TabelaTransicao real compilada
a partir de .github/agents/routing-graph.yaml.
Subtask 12 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
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


class TestTC05StateMachineValidTransitions:
    """Testes de transições lícitas em workflows canônicos contra o grafo real."""

    def test_deve_transicionar_com_sucesso_ciclo_completo_workflow_bug_fix(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Workflow 1/3: WORKFLOW-BUG-FIX percorre sequencialmente as 5 etapas até conclusão."""
        # 1. Originação a partir do router (R-037)
        sessao_0 = Sessao(fase=Fase.ROUTER, workflow=None, etapa=0, agente_ativo="agent-router")
        ev_1 = Evento(
            origem="usuario",
            tipo=TipoEvento.DECISAO_ROTEAMENTO,
            workflow_solicitado=Workflow.BUG_FIX,
            agente_solicitado="bug-triage",
        )
        s1 = transicionar(sessao_0, ev_1, tabela_real)
        assert s1.fase is Fase.EM_WORKFLOW
        assert s1.workflow is Workflow.BUG_FIX
        assert s1.etapa == 1
        assert s1.agente_ativo == "bug-triage"

        # 2. Avanço para etapa 2 (specialist-unit-test-writer)
        ev_2 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=2,
            agente_solicitado="specialist-unit-test-writer",
        )
        s2 = transicionar(s1, ev_2, tabela_real)
        assert s2.etapa == 2
        assert s2.agente_ativo == "specialist-unit-test-writer"

        # 3. Avanço para etapa 3 (specialist-bug-fixer)
        ev_3 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=3,
            agente_solicitado="specialist-bug-fixer",
        )
        s3 = transicionar(s2, ev_3, tabela_real)
        assert s3.etapa == 3
        assert s3.agente_ativo == "specialist-bug-fixer"

        # 4. Avanço para etapa 4 (runtime-verifier)
        ev_4 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=4,
            agente_solicitado="runtime-verifier",
        )
        s4 = transicionar(s3, ev_4, tabela_real)
        assert s4.etapa == 4
        assert s4.agente_ativo == "runtime-verifier"

        # 5. Avanço para etapa 5 (code-review)
        ev_5 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=5,
            agente_solicitado="code-review",
        )
        s5 = transicionar(s4, ev_5, tabela_real)
        assert s5.etapa == 5
        assert s5.agente_ativo == "code-review"

        # 6. Conclusão da última etapa reseta mandatoriamente para o router (R-052)
        ev_fim = Evento(
            origem="usuario",
            tipo=TipoEvento.CONCLUSAO_WORKFLOW,
            etapa_solicitada=5,
            agente_solicitado="code-review",
        )
        s_fim = transicionar(s5, ev_fim, tabela_real)
        assert s_fim.fase is Fase.ROUTER
        assert s_fim.workflow is None
        assert s_fim.etapa == 0
        assert s_fim.agente_ativo == "agent-router"

    def test_deve_transicionar_com_sucesso_ciclo_completo_workflow_refactoring(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Workflow 2/3: WORKFLOW-REFACTORING percorre sequencialmente as 5 etapas até conclusão."""
        # 1. Originação
        sessao_0 = Sessao(fase=Fase.ROUTER, workflow=None, etapa=0, agente_ativo="agent-router")
        ev_1 = Evento(
            origem="usuario",
            tipo=TipoEvento.DECISAO_ROTEAMENTO,
            workflow_solicitado=Workflow.REFACTORING,
            agente_solicitado="business-rules-extractor",
        )
        s1 = transicionar(sessao_0, ev_1, tabela_real)
        assert s1.workflow is Workflow.REFACTORING
        assert s1.etapa == 1
        assert s1.agente_ativo == "business-rules-extractor"

        # 2. Etapa 2 (codegraph-engine)
        ev_2 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=2,
            agente_solicitado="codegraph-engine",
        )
        s2 = transicionar(s1, ev_2, tabela_real)
        assert s2.etapa == 2

        # 3. Etapa 3 (refactor-planner)
        ev_3 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=3,
            agente_solicitado="refactor-planner",
        )
        s3 = transicionar(s2, ev_3, tabela_real)
        assert s3.etapa == 3

        # 4. Etapa 4 (specialist-feature-developer)
        ev_4 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=4,
            agente_solicitado="specialist-feature-developer",
        )
        s4 = transicionar(s3, ev_4, tabela_real)
        assert s4.etapa == 4

        # 5. Etapa 5 (business-rules-extractor)
        ev_5 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=5,
            agente_solicitado="business-rules-extractor",
        )
        s5 = transicionar(s4, ev_5, tabela_real)
        assert s5.etapa == 5

        # 6. Conclusão
        ev_fim = Evento(
            origem="usuario",
            tipo=TipoEvento.CONCLUSAO_WORKFLOW,
            etapa_solicitada=5,
            agente_solicitado="business-rules-extractor",
        )
        s_fim = transicionar(s5, ev_fim, tabela_real)
        assert s_fim.fase is Fase.ROUTER
        assert s_fim.workflow is None

    def test_deve_transicionar_com_sucesso_ciclo_completo_workflow_release_readiness(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Workflow 3/3: WORKFLOW-RELEASE-READINESS percorre sequencialmente as 5 etapas."""
        # 1. Originação
        sessao_0 = Sessao(fase=Fase.ROUTER, workflow=None, etapa=0, agente_ativo="agent-router")
        ev_1 = Evento(
            origem="usuario",
            tipo=TipoEvento.DECISAO_ROTEAMENTO,
            workflow_solicitado=Workflow.RELEASE_READINESS,
            agente_solicitado="tech-solution-architect",
        )
        s1 = transicionar(sessao_0, ev_1, tabela_real)
        assert s1.workflow is Workflow.RELEASE_READINESS
        assert s1.etapa == 1

        # 2. Etapa 2 (database-specialist)
        ev_2 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=2,
            agente_solicitado="database-specialist",
        )
        s2 = transicionar(s1, ev_2, tabela_real)
        assert s2.etapa == 2

        # 3. Etapa 3 (security-reviewer)
        ev_3 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=3,
            agente_solicitado="security-reviewer",
        )
        s3 = transicionar(s2, ev_3, tabela_real)
        assert s3.etapa == 3

        # 4. Etapa 4 (pr-gatekeeper)
        ev_4 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=4,
            agente_solicitado="pr-gatekeeper",
        )
        s4 = transicionar(s3, ev_4, tabela_real)
        assert s4.etapa == 4

        # 5. Etapa 5 (code-review)
        ev_5 = Evento(
            origem="usuario",
            tipo=TipoEvento.AVANCO_ETAPA,
            etapa_solicitada=5,
            agente_solicitado="code-review",
        )
        s5 = transicionar(s4, ev_5, tabela_real)
        assert s5.etapa == 5

        # 6. Conclusão
        ev_fim = Evento(
            origem="usuario",
            tipo=TipoEvento.CONCLUSAO_WORKFLOW,
            etapa_solicitada=5,
            agente_solicitado="code-review",
        )
        s_fim = transicionar(s5, ev_fim, tabela_real)
        assert s_fim.fase is Fase.ROUTER

    def test_deve_permitir_permanencia_na_mesma_etapa_com_agente_valido(
        self, tabela_real: TabelaTransicao
    ) -> None:
        """Permanecer na mesma etapa (etapa_solicitada == sessao.etapa) é transição lícita (R-050)."""
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
            etapa_solicitada=1,
            agente_solicitado="bug-triage",
        )

        # Act
        nova = transicionar(sessao, evento, tabela_real)

        # Assert
        assert nova.etapa == 1
        assert nova.fase is Fase.EM_WORKFLOW
        assert nova.agente_ativo == "bug-triage"
