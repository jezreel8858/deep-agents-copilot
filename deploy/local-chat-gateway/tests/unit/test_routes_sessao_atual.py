"""Testes unitarios puros de `routes._sessao_atual` (Addendum 7).

Sem FastAPI/SDK/banco real -- apenas a reconstrucao pura de `governance.Sessao`
a partir de um `SessionRecord` (dataclass simples), cobrindo a guarda de
invariante auto-corretiva "Fase.ROUTER implica workflow=None".
"""

from __future__ import annotations

from local_chat_gateway.api.routes import _AGENTE_ROUTER_PADRAO, _sessao_atual
from local_chat_gateway.governance import Fase
from local_chat_gateway.session_store import SessionRecord


def test_record_none_retorna_sessao_router_zerada() -> None:
    """Sem registro persistido (1o turno), a sessao comeca em Fase.ROUTER
    com workflow/etapa/agente_ativo default (comportamento pre-existente)."""
    sessao = _sessao_atual(None)

    assert sessao.fase is Fase.ROUTER
    assert sessao.workflow is None
    assert sessao.etapa == 0
    assert sessao.agente_ativo == _AGENTE_ROUTER_PADRAO


def test_record_fase_em_workflow_com_workflow_valido_e_reconstruido_normalmente() -> None:
    """Registro consistente (fase=em_workflow + workflow preenchido) e
    reconstruido sem nenhuma correcao (caminho feliz, pre-existente)."""
    record = SessionRecord(
        session_id="s1",
        created_at=1000,
        last_seen_at=1000,
        fase="em_workflow",
        workflow="WORKFLOW-TECHNICAL-ANALYSIS",
        etapa=1,
        agente_ativo="tech-solution-architect",
        aprovacoes=None,
    )

    sessao = _sessao_atual(record)

    assert sessao.fase.value == "em_workflow"
    assert sessao.workflow is not None
    assert sessao.workflow.value == "WORKFLOW-TECHNICAL-ANALYSIS"
    assert sessao.etapa == 1
    assert sessao.agente_ativo == "tech-solution-architect"


def test_record_fase_router_com_workflow_residual_e_autocorrigido() -> None:
    """Bug real de producao (2026-10-01, Addendum 7): um registro persistido
    com `fase='router'` mas `workflow`/`etapa`/`agente_ativo` residuais de um
    turno anterior (gravado pelo `create_session` ANTES do fix do Addendum 6,
    ou por qualquer outra via nao antecipada) NUNCA deve propagar o workflow
    residual -- `Fase.ROUTER` sempre implica `workflow=None`/`etapa=0`/
    `agente_ativo` default, independentemente do que estiver no banco.

    Sem esta guarda, `preparar_turno` reaproveita o workflow residual (pois
    so checa `sessao.workflow is None`) e gera `TipoEvento.AVANCO_ETAPA` em
    vez de `DECISAO_ROTEAMENTO`, rejeitado por `TransicaoInvalidaError`
    (R-037: "a partir da Fase.ROUTER so e aceita uma decisao de roteamento
    explicita") -- a sessao fica travada indefinidamente, pois o TTL e
    renovado a cada nova tentativa do usuario (`touch_session`).
    """
    record = SessionRecord(
        session_id="ca967b64f3c18b57",
        created_at=1000,
        last_seen_at=1790875637,
        fase="router",
        workflow="WORKFLOW-TECHNICAL-ANALYSIS",
        etapa=1,
        agente_ativo="tech-solution-architect",
        aprovacoes=None,
    )

    sessao = _sessao_atual(record)

    assert sessao.fase is Fase.ROUTER
    assert sessao.workflow is None
    assert sessao.etapa == 0
    assert sessao.agente_ativo == _AGENTE_ROUTER_PADRAO


def test_record_fase_router_com_aprovacoes_preserva_aprovacoes() -> None:
    """A guarda de invariante zera workflow/etapa/agente_ativo, mas preserva
    `aprovacoes` (checkpoints ja concedidos nao sao descartados por um
    reset de workflow -- apenas o workflow/etapa residual e descartado)."""
    record = SessionRecord(
        session_id="s2",
        created_at=1000,
        last_seen_at=1000,
        fase="router",
        workflow="WORKFLOW-BUG-FIX",
        etapa=2,
        agente_ativo="bug-triage",
        aprovacoes={"1": True},
    )

    sessao = _sessao_atual(record)

    assert sessao.fase is Fase.ROUTER
    assert sessao.workflow is None
    assert "1" in sessao.aprovacoes


def test_record_fase_invalida_cai_para_router_e_tambem_zera_workflow() -> None:
    """Uma `fase` persistida que nao resolve para nenhum `Fase` valido
    (dado corrompido) cai para `Fase.ROUTER` (comportamento pre-existente)
    e, pela mesma guarda, tambem zera workflow/etapa/agente_ativo."""
    record = SessionRecord(
        session_id="s3",
        created_at=1000,
        last_seen_at=1000,
        fase="fase-inexistente-corrompida",
        workflow="WORKFLOW-FEATURE-DEVELOPMENT",
        etapa=3,
        agente_ativo="python-feature-developer",
        aprovacoes=None,
    )

    sessao = _sessao_atual(record)

    assert sessao.fase is Fase.ROUTER
    assert sessao.workflow is None
    assert sessao.etapa == 0
    assert sessao.agente_ativo == _AGENTE_ROUTER_PADRAO

