"""turn_recorder — acumula dados de UM turno completo (do inicio ao fim de
um prompt, com ou sem workflow/subagents) a partir dos eventos REAIS do SDK
Copilot, para persistencia duravel na tabela `turns` do SQLite local
(`session_store.py`) -- insumo de analise continua de melhoria de
workflow/agent (pedido explicito do usuario, 2026-10-02).

Contexto (levantamento feito na mesma sessao, via introspeccao real de
`copilot.session_events` + pesquisa externa): o gateway ja tinha um
pipeline de telemetria (`telemetry.py`, export OTel/Langfuse) mas ele e
100% best-effort e depende de um OTel Collector externo estar configurado
e rodando -- se nao estiver, os dados sao silenciosamente descartados. Este
modulo persiste LOCALMENTE e SEMPRE, na mesma tabela SQLite que o gateway
ja usa para `sessions`/`checkpoints`/`budget_daily`, servindo como fonte de
verdade DURAVEL e consultavel (ex.: `GET /v1/turns`, `tests/evals`/
`agent-evals-lab`) independente de qualquer observability stack externo.

Eventos do SDK consumidos aqui (confirmados por introspeccao real,
`dataclasses.fields()`, da wheel instalada em `deploy/local-chat-gateway/
.venv`) alem dos ja usados por `sdk_session._on_event` para o protocolo
AG-UI (`AssistantMessageData`/`ToolExecutionStart/CompleteData`/
`SubagentStarted/Completed/FailedData`/`SessionErrorData`):
- `AssistantUsageData`: tokens/custo/latencia REAIS por chamada de modelo.
- `ModelCallFailureData`: falhas de chamada de modelo (antes invisiveis).
- `AssistantTurnRetryData`: contagem e MOTIVO de retries (sinal nº1 de
  workflow/instrucao mal escrita, pedido explicito do usuario).
- `AssistantIntentData`: intencao detectada pelo MODELO -- cruzar com a
  decisao do roteador deterministico detecta desalinhamento de roteamento.
- `SessionCompletionReceiptData`: scorecard pronto de como o turno terminou.
- `SessionTruncationData`/`SessionCompactionCompleteData`: estouro de
  contexto -- sintoma de instrucao/skill mal dimensionada.

Fora de escopo nesta 1a iteracao (simplificacao deliberada, documentada no
levantamento): `SubagentSelectedData`/`SubagentConfiguredData` (nao
carregam `tool_call_id` para correlacionar com precisao a um subagent
especifico) e `PermissionApprovalEvaluation`/`TaskBlocker` (fricção de
aprovacao) -- candidatos a uma 2a iteracao se a analise mostrar
necessidade.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from local_chat_gateway.session_store import SessionStore, TurnRecord

logger = logging.getLogger(__name__)


@dataclass
class AcumuladorDeTurno:
    """Estado mutavel acumulado durante 1 turno -- 1 instancia por chamada
    de `sdk_session.stream_chat_ag_ui`, nunca compartilhada entre
    turnos/sessoes (vive inteiramente na pilha da coroutine do turno)."""

    turn_id: str
    session_id: str
    created_at: int = field(default_factory=lambda: int(time.time()))
    prompt: str = ""
    agent_name: str | None = None
    agent_model: str | None = None
    workflow: str | None = None
    etapa: int | None = None
    score_roteamento: float | None = None
    drift_detectado: bool | None = None
    handoff_origem: str | None = None
    handoff_motivo: str | None = None
    checkpoint_aberto: bool = False
    trace_id: str | None = None

    resposta_partes: list[str] = field(default_factory=list)
    detected_intent: str | None = None
    tools_executados: list[dict[str, Any]] = field(default_factory=list)
    tools_inicio: dict[str, float] = field(default_factory=dict)
    tools_nome: dict[str, str] = field(default_factory=dict)
    subagents_executados: list[dict[str, Any]] = field(default_factory=list)
    subagents_inicio: dict[str, float] = field(default_factory=dict)
    subagents_nome: dict[str, str] = field(default_factory=dict)
    retries_count: int = 0
    retry_reasons: list[str] = field(default_factory=list)
    model_call_failures: list[dict[str, Any]] = field(default_factory=list)
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_reasoning: int = 0
    tokens_cache_read: int = 0
    tokens_cache_write: int = 0
    cost_nano_aiu: float = 0.0
    time_to_first_token_ms: int | None = None
    stop_reason: str | None = None
    successful_tool_count: int | None = None
    failed_tool_count: int | None = None
    context_truncado: bool = False
    tokens_removidos_truncamento: int = 0
    compaction_disparada: bool = False
    error_type: str | None = None
    # Modelo REAL (id tecnico da API, ex.: "claude-sonnet-4-5") reportado
    # pela ULTIMA `AssistantUsageData` do turno -- usado apenas para exibir
    # o badge de creditos no chat (2026-10-03, paridade com o plugin
    # Copilot da IDE, que mostra "<Modelo> · <N> Credits" ao final de cada
    # resposta). Distinto de `agent_model` (nome AMIGAVEL declarado no
    # frontmatter do `.agent.md`, ex.: "Claude Sonnet 5.5") -- `sdk_session.
    # stream_chat_ag_ui` prefere `agent_model` quando disponivel (mais
    # legivel) e cai para este campo tecnico como fallback.
    modelo_usado_real: str | None = None
    # Janela de contexto (context window) REAL da sessao -- capturada do
    # evento nativo `SessionUsageInfoData` (2026-10-03, pedido explicito do
    # usuario: exibir context-window no chat, paridade com o plugin Copilot
    # da IDE). Pode ser emitido MULTIPLAS vezes por turno (a cada mudanca
    # de contagem de tokens da sessao) -- mantemos sempre a ULTIMA ocorrencia
    # (estado mais recente da janela no momento em que o turno termina).
    contexto_tokens_atuais: int | None = None
    contexto_tokens_limite: int | None = None


def adicionar_texto_resposta(turno: AcumuladorDeTurno, texto: str) -> None:
    """Acumula um fragmento de texto REAL do assistente (qualquer bolha,
    badge incluso) na resposta completa do turno."""
    if texto:
        turno.resposta_partes.append(texto)


def registrar_tool_iniciada(turno: AcumuladorDeTurno, tool_call_id: str, nome: str) -> None:
    if not tool_call_id:
        return
    turno.tools_inicio[tool_call_id] = time.time()
    turno.tools_nome[tool_call_id] = nome


def registrar_tool_concluida(turno: AcumuladorDeTurno, tool_call_id: str) -> None:
    if not tool_call_id:
        return
    nome = turno.tools_nome.pop(tool_call_id, "?")
    inicio = turno.tools_inicio.pop(tool_call_id, None)
    duracao_ms = int((time.time() - inicio) * 1000) if inicio is not None else None
    turno.tools_executados.append({"nome": nome, "duracao_ms": duracao_ms})


def registrar_subagent_iniciado(
    turno: AcumuladorDeTurno, tool_call_id: str, nome: str
) -> None:
    if not tool_call_id:
        return
    turno.subagents_inicio[tool_call_id] = time.time()
    turno.subagents_nome[tool_call_id] = nome


def _finalizar_subagent(
    turno: AcumuladorDeTurno,
    tool_call_id: str,
    *,
    outcome: str,
    erro: str | None = None,
) -> None:
    if not tool_call_id:
        return
    nome = turno.subagents_nome.pop(tool_call_id, "?")
    inicio = turno.subagents_inicio.pop(tool_call_id, None)
    duracao_ms = int((time.time() - inicio) * 1000) if inicio is not None else None
    registro: dict[str, Any] = {"nome": nome, "duracao_ms": duracao_ms, "outcome": outcome}
    if erro:
        registro["erro"] = erro
    turno.subagents_executados.append(registro)


def registrar_subagent_concluido(turno: AcumuladorDeTurno, tool_call_id: str) -> None:
    _finalizar_subagent(turno, tool_call_id, outcome="sucesso")


def registrar_subagent_falhou(turno: AcumuladorDeTurno, tool_call_id: str, erro: str) -> None:
    _finalizar_subagent(turno, tool_call_id, outcome="falha", erro=erro)


def registrar_uso_assistente(turno: AcumuladorDeTurno, dado: Any) -> None:
    """`AssistantUsageData` -- pode ser emitido MULTIPLAS vezes por turno
    (1 por chamada de modelo real, incluindo 1 por subagent executado) --
    acumula (soma) tokens/custo do turno INTEIRO; `time_to_first_token_ms`
    usa a PRIMEIRA ocorrencia (latencia ate a 1a reacao percebida pelo
    usuario, nao a de cada subagent interno).

    Custo/creditos (2026-10-03, pedido explicito do usuario -- paridade com
    o badge "<Modelo> · <N> Credits" do plugin Copilot da IDE): a formula
    OFICIAL confirmada em docs.github.com/en/copilot/how-tos/copilot-sdk/
    features/usage-and-billing e' `AI credits = copilot_usage.total_nano_aiu
    / 1e9` -- valor AUTORITATIVO reportado pelo backend real do Copilot
    (CAPI), calculado a partir do token usage e da tabela de precos por
    modelo. Isto e' DISTINTO do campo top-level `dado.cost` (marcado
    "Experimental" na wheel do SDK) -- usado aqui apenas como FALLBACK caso
    `copilot_usage` venha ausente (ex.: versao mais antiga do CLI/SDK sem
    este campo preenchido), nunca como fonte primaria quando o valor
    autoritativo esta disponivel.
    """
    turno.tokens_input += int(getattr(dado, "input_tokens", None) or 0)
    turno.tokens_output += int(getattr(dado, "output_tokens", None) or 0)
    turno.tokens_reasoning += int(getattr(dado, "reasoning_tokens", None) or 0)
    turno.tokens_cache_read += int(getattr(dado, "cache_read_tokens", None) or 0)
    turno.tokens_cache_write += int(getattr(dado, "cache_write_tokens", None) or 0)
    copilot_usage = getattr(dado, "copilot_usage", None)
    nano_aiu_autoritativo = getattr(copilot_usage, "total_nano_aiu", None)
    if nano_aiu_autoritativo is not None:
        turno.cost_nano_aiu += float(nano_aiu_autoritativo)
    else:
        # Fallback (ver docstring acima): ainda em "nano AIU" por convencao
        # de unidade -- `dado.cost` e' um valor experimental/estimado, mas
        # mantido na MESMA escala para que a divisao por 1e9 em
        # `sdk_session.stream_chat_ag_ui` continue correta em ambos os casos.
        turno.cost_nano_aiu += float(getattr(dado, "cost", None) or 0.0)
    modelo_real = getattr(dado, "model", None)
    if modelo_real:
        turno.modelo_usado_real = str(modelo_real)
    if turno.time_to_first_token_ms is None:
        ttft = getattr(dado, "time_to_first_token", None)
        if ttft is not None:
            try:
                turno.time_to_first_token_ms = int(ttft.total_seconds() * 1000)
            except AttributeError:
                logger.debug("turn_recorder_ttft_tipo_inesperado: %r", ttft)


def registrar_info_contexto(turno: AcumuladorDeTurno, dado: Any) -> None:
    """`SessionUsageInfoData` -- estatisticas REAIS de uso da janela de
    contexto (context window) da sessao, campos `currentTokens`/
    `tokenLimit` confirmados por introspeccao da wheel (2026-10-03, pedido
    explicito do usuario: exibir context-window no chat, paridade com o
    plugin Copilot da IDE). Pode ser emitido MULTIPLAS vezes por turno (a
    cada mudanca na contagem de tokens da sessao) -- mantemos sempre a
    ULTIMA ocorrencia (estado mais recente no momento em que o turno
    termina), nunca acumulamos/somamos (ao contrario de tokens/custo em
    `registrar_uso_assistente`): `current_tokens`/`token_limit` ja sao
    valores ABSOLUTOS da sessao inteira, nao incrementos por chamada.
    """
    current_tokens = getattr(dado, "current_tokens", None)
    token_limit = getattr(dado, "token_limit", None)
    if current_tokens is not None:
        turno.contexto_tokens_atuais = int(current_tokens)
    if token_limit is not None:
        turno.contexto_tokens_limite = int(token_limit)


def registrar_falha_model_call(turno: AcumuladorDeTurno, dado: Any) -> None:
    """`ModelCallFailureData` -- falha de chamada de modelo, antes
    totalmente invisivel (o gateway so via `SessionErrorData`, que cobre
    erros de API/cota, nao falhas pontuais de 1 chamada de modelo)."""
    failure_kind = getattr(dado, "failure_kind", None)
    turno.model_call_failures.append(
        {
            "model": getattr(dado, "model", None),
            "error_type": getattr(dado, "error_type", None),
            "failure_kind": str(failure_kind) if failure_kind is not None else None,
            "status_code": getattr(dado, "status_code", None),
        }
    )


def registrar_retry(turno: AcumuladorDeTurno, dado: Any) -> None:
    """`AssistantTurnRetryData` -- sinal nº1 de workflow/instrucao
    problematica (pedido explicito do usuario): quantas vezes e POR QUE o
    SDK precisou tentar novamente a mesma chamada neste turno."""
    turno.retries_count += 1
    motivo = getattr(dado, "reason", None)
    if motivo:
        turno.retry_reasons.append(str(motivo))


def registrar_intencao(turno: AcumuladorDeTurno, dado: Any) -> None:
    """`AssistantIntentData` -- intencao detectada pelo MODELO; cruzar com
    `turno.agent_name`/`turno.workflow` (decisao DETERMINISTICA do
    roteador) na analise posterior revela desalinhamento de roteamento."""
    intent = getattr(dado, "intent", None)
    if intent:
        turno.detected_intent = str(intent)


def registrar_completion_receipt(turno: AcumuladorDeTurno, dado: Any) -> None:
    """`SessionCompletionReceiptData` -- scorecard pronto de como o turno
    terminou (contagem de tools com sucesso/falha, motivo de parada)."""
    sucesso = getattr(dado, "successful_tool_count", None)
    if sucesso is not None:
        turno.successful_tool_count = sucesso
    falha = getattr(dado, "failed_tool_count", None)
    if falha is not None:
        turno.failed_tool_count = falha
    stop_reason = getattr(dado, "stop_reason", None)
    if stop_reason is not None:
        turno.stop_reason = str(stop_reason)


def registrar_truncamento(turno: AcumuladorDeTurno, dado: Any) -> None:
    """`SessionTruncationData` -- contexto estourou e precisou ser cortado
    (sintoma de instrucao/skill mal dimensionada para o workflow)."""
    turno.context_truncado = True
    turno.tokens_removidos_truncamento += int(
        getattr(dado, "tokens_removed_during_truncation", None) or 0
    )


def registrar_compactacao(turno: AcumuladorDeTurno, _dado: Any) -> None:
    """`SessionCompactionCompleteData` -- contexto foi compactado (resumo
    automatico) durante o turno -- mesma familia de sinal que truncamento."""
    turno.compaction_disparada = True


def registrar_erro_sessao(turno: AcumuladorDeTurno, dado: Any) -> None:
    """`SessionErrorData` -- erro real da API do Copilot (cota, rate
    limit, autenticacao); ja tratado por `sdk_session._on_event` para
    visibilidade no chat, aqui so persistimos o codigo para analise."""
    codigo = getattr(dado, "error_code", None)
    if codigo:
        turno.error_type = str(codigo)


def persistir(turno: AcumuladorDeTurno, session_store: SessionStore | None) -> None:
    """Grava 1 linha em `turns` via `SessionStore.record_turn`.

    NUNCA propaga excecao -- uma falha de persistencia de analytics jamais
    deve derrubar o turno de chat real (mesma filosofia best-effort de
    `telemetry.py`/bridges de arquivo). `session_store=None` (chamador nao
    configurou persistencia) e um no-op silencioso.
    """
    if session_store is None:
        return
    ended_at = int(time.time())
    try:
        session_store.record_turn(
            TurnRecord(
                turn_id=turno.turn_id,
                session_id=turno.session_id,
                created_at=turno.created_at,
                ended_at=ended_at,
                duration_ms=max(0, (ended_at - turno.created_at) * 1000),
                prompt=turno.prompt,
                response_text="".join(turno.resposta_partes),
                agent_name=turno.agent_name,
                agent_model=turno.agent_model,
                workflow=turno.workflow,
                etapa=turno.etapa,
                score_roteamento=turno.score_roteamento,
                drift_detectado=turno.drift_detectado,
                handoff_origem=turno.handoff_origem,
                handoff_motivo=turno.handoff_motivo,
                checkpoint_aberto=turno.checkpoint_aberto,
                trace_id=turno.trace_id,
                detected_intent=turno.detected_intent,
                tools_executados=turno.tools_executados or None,
                subagents_executados=turno.subagents_executados or None,
                retries_count=turno.retries_count,
                retry_reasons=turno.retry_reasons or None,
                model_call_failures=turno.model_call_failures or None,
                tokens_input=turno.tokens_input,
                tokens_output=turno.tokens_output,
                tokens_reasoning=turno.tokens_reasoning,
                tokens_cache_read=turno.tokens_cache_read,
                tokens_cache_write=turno.tokens_cache_write,
                cost_nano_aiu=turno.cost_nano_aiu,
                time_to_first_token_ms=turno.time_to_first_token_ms,
                stop_reason=turno.stop_reason,
                successful_tool_count=turno.successful_tool_count,
                failed_tool_count=turno.failed_tool_count,
                context_truncado=turno.context_truncado,
                tokens_removidos_truncamento=turno.tokens_removidos_truncamento,
                compaction_disparada=turno.compaction_disparada,
                error_type=turno.error_type,
            )
        )
    except Exception:  # noqa: BLE001 -- analytics nunca derruba o turno de chat real
        logger.exception("turn_recorder_persistir_falhou turn_id=%s", turno.turn_id)

