"""
state_machine — State machine em código dos 9 workflows canônicos (R-050).

Contrato (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §6.2): dado o estado
atual da `Sessao` e um `Evento` de entrada, calcula o próximo estado
consultando exclusivamente a `TabelaTransicao` compilada por
`graph_loader`. Qualquer transição fora do conjunto permitido (pular
etapa, retroceder sem gate, agente errado) deve levantar
`TransicaoInvalidaError` — nunca falhar silenciosamente.

Guard clauses aplicados, nesta ordem (subtask 3 do
PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md):
    0. R-042 (anti sticky-session / deriva): um evento `DERIVA_DETECTADA`
       sempre reseta a sessão para `Fase.ROUTER`, incondicionalmente,
       independente da fase/etapa atual — avaliado primeiro porque
       sobrepõe qualquer outro guard clause.
    1. R-037 (agent-router first): fora da `Fase.ROUTER` nenhuma transição
       pode originar/trocar de workflow; dentro da `Fase.ROUTER` só uma
       `TipoEvento.DECISAO_ROTEAMENTO` válida (workflow real dentre os 9
       canônicos + agente da etapa 1 correspondente) é aceita.
    2. R-050 (workflows canônicos — sem pular etapa): a única etapa-alvo
       legal é `sessao.etapa` (permanência) ou `sessao.etapa + 1`
       (avanço sequencial); a `EtapaSpec` deve existir na tabela.
    3. Validação de agente permitido: `evento.agente_solicitado` deve
       constar em `EtapaSpec.agent_permitidos` da etapa-alvo.
    4. R-064 (checkpoint humano obrigatório): se a etapa-alvo exige
       aprovação e ela ainda não foi concedida (nem já registrada em
       `sessao.aprovacoes`), a transição é rejeitada.
    5. R-052 (conclusão de workflow): se a etapa-alvo é a última do
       workflow (`EtapaSpec.proxima is None`) e o evento é uma
       `TipoEvento.CONCLUSAO_WORKFLOW`, o novo estado reseta
       mandatoriamente para `Fase.ROUTER` — nunca persiste workflow
       preenchido em fase concluída.
"""

from __future__ import annotations

from governance_runner.routing.model import (
    EtapaSpec,
    Evento,
    Fase,
    Sessao,
    TabelaTransicao,
    TipoEvento,
    Workflow,
)

_AGENTE_ROUTER = "agent-router"


class TransicaoInvalidaError(Exception):
    """Erro de domínio: transição de estado ilegal segundo R-037/R-042/R-050/R-064.

    Levantada quando o evento solicita um avanço de etapa não contíguo,
    um agente fora de `agent_permitidos` da etapa alvo, uma transição
    que ignora um gate de aprovação humana obrigatório, ou uma tentativa
    de originar/trocar de workflow fora da `Fase.ROUTER`.
    """


def _resetar_para_router(aprovacoes: frozenset[str]) -> Sessao:
    """Constrói a `Sessao` de reset mandatório para o router (R-042/R-052)."""
    return Sessao(
        fase=Fase.ROUTER,
        workflow=None,
        etapa=0,
        agente_ativo=_AGENTE_ROUTER,
        aprovacoes=aprovacoes,
    )


def _validar_agente_permitido(
    evento: Evento, etapa_spec: EtapaSpec, *, workflow: Workflow, etapa_alvo: int
) -> str:
    """Guard clause 3: valida `evento.agente_solicitado` contra `agent_permitidos`."""
    agente_solicitado = evento.agente_solicitado
    if agente_solicitado is None or agente_solicitado not in etapa_spec.agent_permitidos:
        raise TransicaoInvalidaError(
            f"Agente solicitado '{agente_solicitado}' não está entre os agentes "
            f"permitidos da etapa {etapa_alvo} de '{workflow}': "
            f"{sorted(etapa_spec.agent_permitidos)}"
        )
    return agente_solicitado


def _validar_checkpoint_humano(
    evento: Evento, sessao: Sessao, etapa_spec: EtapaSpec, *, etapa_alvo: int
) -> frozenset[str]:
    """Guard clause 4 (R-064): valida o checkpoint humano obrigatório da etapa-alvo.

    `Sessao.aprovacoes` é tipado como `frozenset[str]` — identificadores de
    etapas já aprovadas são armazenados como string (`str(etapa_alvo)`).
    """
    etapa_id = str(etapa_alvo)
    if not etapa_spec.requer_aprovacao or etapa_id in sessao.aprovacoes:
        return sessao.aprovacoes

    if not evento.aprovacao_concedida:
        raise TransicaoInvalidaError(
            f"R-064: etapa {etapa_alvo} exige checkpoint humano — aguardando aprovação "
            "explícita antes de avançar (evento sem aprovacao_concedida=True)"
        )
    return sessao.aprovacoes | {etapa_id}


def _transicionar_a_partir_do_router(
    sessao: Sessao, evento: Evento, tabela: TabelaTransicao
) -> Sessao:
    """Guard clause 1 (R-037), ramo `Fase.ROUTER`: única origem legal de workflow."""
    if evento.tipo is not TipoEvento.DECISAO_ROTEAMENTO:
        raise TransicaoInvalidaError(
            "R-037: a partir da Fase.ROUTER só é aceita uma decisão de roteamento "
            f"explícita (TipoEvento.DECISAO_ROTEAMENTO) — evento recebido tem "
            f"tipo={evento.tipo!r}"
        )

    workflow_solicitado = evento.workflow_solicitado
    if workflow_solicitado is None:
        raise TransicaoInvalidaError(
            "R-037: decisão de roteamento deve indicar um workflow_solicitado "
            "válido dentre os 9 workflows canônicos"
        )

    etapa_alvo = 1
    etapa_spec = tabela.etapas.get((workflow_solicitado, etapa_alvo))
    if etapa_spec is None:
        raise TransicaoInvalidaError(
            f"R-037: workflow '{workflow_solicitado}' não possui etapa {etapa_alvo} "
            "na tabela de transição compilada (workflow desconhecido)"
        )

    agente_ativo = _validar_agente_permitido(
        evento, etapa_spec, workflow=workflow_solicitado, etapa_alvo=etapa_alvo
    )
    aprovacoes = _validar_checkpoint_humano(evento, sessao, etapa_spec, etapa_alvo=etapa_alvo)

    return Sessao(
        fase=Fase.EM_WORKFLOW,
        workflow=workflow_solicitado,
        etapa=etapa_alvo,
        agente_ativo=agente_ativo,
        aprovacoes=aprovacoes,
    )


def _transicionar_dentro_do_workflow(
    sessao: Sessao, evento: Evento, tabela: TabelaTransicao
) -> Sessao:
    """Guard clauses 1 (R-037, negativo) a 5 (R-052), fora da `Fase.ROUTER`."""
    workflow_solicitado = evento.workflow_solicitado
    if workflow_solicitado is not None and workflow_solicitado != sessao.workflow:
        raise TransicaoInvalidaError(
            "R-037: não é permitido originar ou trocar de workflow fora da "
            f"Fase.ROUTER (workflow ativo='{sessao.workflow}', "
            f"workflow_solicitado='{workflow_solicitado}')"
        )

    if sessao.workflow is None:
        raise TransicaoInvalidaError(
            "Sessão fora da Fase.ROUTER deve possuir um workflow ativo definido"
        )

    etapa_alvo = evento.etapa_solicitada if evento.etapa_solicitada is not None else sessao.etapa
    if etapa_alvo not in (sessao.etapa, sessao.etapa + 1):
        raise TransicaoInvalidaError(
            f"R-050: etapa solicitada {etapa_alvo} não é uma transição legal a partir "
            f"da etapa atual {sessao.etapa} do workflow '{sessao.workflow}' "
            f"(permitido: permanecer em {sessao.etapa} ou avançar para {sessao.etapa + 1})"
        )

    etapa_spec = tabela.etapas.get((sessao.workflow, etapa_alvo))
    if etapa_spec is None:
        raise TransicaoInvalidaError(
            f"R-050: etapa {etapa_alvo} inexistente para o workflow '{sessao.workflow}' "
            "na tabela de transição (workflow concluído ou etapa fora do grafo)"
        )

    agente_ativo = _validar_agente_permitido(
        evento, etapa_spec, workflow=sessao.workflow, etapa_alvo=etapa_alvo
    )
    aprovacoes = _validar_checkpoint_humano(evento, sessao, etapa_spec, etapa_alvo=etapa_alvo)

    if etapa_spec.proxima is None and evento.tipo is TipoEvento.CONCLUSAO_WORKFLOW:
        # R-052: conclusão da última etapa reseta mandatoriamente para o router.
        return _resetar_para_router(aprovacoes)

    return Sessao(
        fase=Fase.EM_WORKFLOW,
        workflow=sessao.workflow,
        etapa=etapa_alvo,
        agente_ativo=agente_ativo,
        aprovacoes=aprovacoes,
    )


def transicionar(sessao: Sessao, evento: Evento, tabela: TabelaTransicao) -> Sessao:
    """Calcula a próxima `Sessao` a partir do evento, aplicando os guard clauses.

    Args:
        sessao: Estado imutável atual da sessão de governança.
        evento: Evento de entrada (turno do usuário) a ser processado.
        tabela: `TabelaTransicao` imutável compilada por `graph_loader`.

    Returns:
        Sessao: Novo estado imutável da sessão após a transição.

    Raises:
        TransicaoInvalidaError: Se a transição solicitada não constar no
            conjunto de transições permitidas para o workflow/etapa atual,
            se o evento tentar originar um workflow fora da `Fase.ROUTER`,
            se o agente solicitado não for permitido na etapa-alvo, ou se
            um checkpoint humano obrigatório (R-064) não tiver sido
            satisfeito.
    """
    # Guard clause 0 (R-042): deriva de intenção sempre reseta para o router,
    # independentemente da fase/etapa atual — avaliado antes de qualquer
    # outro guard clause por design (nenhuma outra regra pode suprimi-lo).
    if evento.tipo is TipoEvento.DERIVA_DETECTADA:
        return _resetar_para_router(sessao.aprovacoes)

    if sessao.fase is Fase.ROUTER:
        return _transicionar_a_partir_do_router(sessao, evento, tabela)

    return _transicionar_dentro_do_workflow(sessao, evento, tabela)
