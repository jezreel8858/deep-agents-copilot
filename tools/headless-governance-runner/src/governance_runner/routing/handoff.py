"""
handoff — Contrato de payload de handoff entre agentes.

Contrato (`.github/skills/handoff-governance/SKILL.md`): valida a
estrutura mínima do payload trocado entre agentes em uma cadeia de
handoffs (contexto recebido, entradas consideradas válidas, ausência de
dados sensíveis não sanitizados), rejeitando payloads malformados antes
da delegação.

Implementação — subtask 6 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.

Regras de validação (schema v1.3, `.github/skills/handoff-governance/SKILL.md` §2.1):
    1. Campos obrigatórios: `versao`, `para`, `motivo`, `emissor.nome`,
       `contexto.solicitacao_original`, `contexto.trabalho_realizado`.
    2. Retrocompatibilidade v1.0: blocos aditivos (`roteamento_grafo`,
       `origem_contexto`, `workflow_tracking`) são inteiramente opcionais.
    3. Consistência `roteamento_grafo.next_node == para`, quando presente.
    4. `workflow_tracking.workflow_id` deve pertencer ao enum `Workflow`.
    5. `workflow_tracking.politica_desvio` deve ser `strict` ou `adaptive`.
    6. `origem_contexto.call_type` deve ser `subroutine` ou `permanent_transfer`.
    7. Sanitização fail-closed de segredos não mascarados (não tenta mascarar,
       apenas rejeita).
    8. `para` não pode ser vazio nem idêntico a `emissor.nome` (evita handoff
       trivial A→A).

Este módulo não contém I/O nem chamadas de rede — validação pura e
determinística sobre a estrutura em memória do payload.
"""

from __future__ import annotations

import re
from typing import Any, Final

from governance_runner.routing.model import HandoffPayload, Workflow

__all__ = ["HandoffPayloadInvalidoError", "validar_handoff"]


class HandoffPayloadInvalidoError(Exception):
    """Erro de domínio: payload de handoff não atende ao schema `handoff-governance/SKILL.md`.

    Levantada quando campos obrigatórios estão ausentes, quando dados
    sensíveis (PII/credenciais) não foram sanitizados, ou quando o agente
    de destino não está habilitado a receber o tipo de handoff solicitado.
    """


# ---------------------------------------------------------------------------
# Constantes de validação (enums do schema §2.1).
# ---------------------------------------------------------------------------

_WORKFLOW_VALUES: Final[frozenset[str]] = frozenset(w.value for w in Workflow)
_POLITICAS_DESVIO_VALIDAS: Final[frozenset[str]] = frozenset({"strict", "adaptive"})
_CALL_TYPES_VALIDOS: Final[frozenset[str]] = frozenset({"subroutine", "permanent_transfer"})

# Marcador que indica que um valor já foi sanitizado por camada anterior
# (ex.: agent-observability-otel / redator de logs) — não deve ser re-rejeitado.
_MARCADOR_SANITIZADO: Final[str] = "***REDACTED"

# Padrões óbvios de segredo não sanitizado (adaptado de práticas comuns de
# scanning de credenciais — GitHub tokens, OpenAI-style keys, Bearer tokens,
# AWS access keys e chaves privadas PEM).
_PADROES_SEGREDO: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"gh[po]_[A-Za-z0-9]{10,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{10,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"Bearer\s+\S+"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----"),
)


def _contem_segredo_nao_sanitizado(texto: str) -> bool:
    """Retorna `True` se `texto` contém um padrão de segredo não mascarado."""
    if _MARCADOR_SANITIZADO in texto:
        return False
    return any(padrao.search(texto) for padrao in _PADROES_SEGREDO)


def _verificar_payload_sem_segredos(valor: Any) -> None:
    """Varre recursivamente `valor` (dict/list/tuple/str) por segredos não sanitizados.

    Fail-closed: rejeita o payload inteiro assim que o primeiro segredo não
    mascarado é encontrado, em qualquer profundidade de aninhamento.
    """
    if isinstance(valor, dict):
        for item in valor.values():
            _verificar_payload_sem_segredos(item)
    elif isinstance(valor, (list, tuple)):
        for item in valor:
            _verificar_payload_sem_segredos(item)
    elif isinstance(valor, str):
        if _contem_segredo_nao_sanitizado(valor):
            raise HandoffPayloadInvalidoError(
                "Dado sensível não sanitizado detectado no payload de handoff "
                "(credencial/token em texto plano). Mascare o valor "
                f"(ex.: '{_MARCADOR_SANITIZADO}') antes de emitir o handoff."
            )


def _exigir_string_nao_vazia(valor: Any, nome_campo: str) -> str:
    """Valida que `valor` é uma string não vazia; caso contrário, rejeita o payload."""
    if not isinstance(valor, str) or not valor.strip():
        raise HandoffPayloadInvalidoError(
            f"Campo obrigatório ausente ou vazio no payload de handoff: '{nome_campo}'."
        )
    return valor


def validar_handoff(payload: dict[str, Any]) -> HandoffPayload:
    """Valida um payload bruto de handoff contra o schema `handoff-governance/SKILL.md`.

    Args:
        payload: Dicionário bruto recebido do agente de origem, contendo
            ao menos o resumo de contexto e as entradas consideradas válidas.

    Returns:
        HandoffPayload: Payload validado e pronto para consumo pelo agente
        de destino.

    Raises:
        HandoffPayloadInvalidoError: Se o payload for malformado, omitir
            campos obrigatórios, apresentar inconsistência estrutural entre
            blocos aditivos, usar valores fora dos enums do schema, conter
            dados sensíveis não sanitizados, ou apontar handoff para o
            próprio emissor.
    """
    if not isinstance(payload, dict):
        raise HandoffPayloadInvalidoError("Payload de handoff deve ser um dicionário (dict).")

    # Regra 1 — campos obrigatórios (estritos, independem de versão/blocos aditivos).
    _exigir_string_nao_vazia(payload.get("versao"), "versao")
    para = _exigir_string_nao_vazia(payload.get("para"), "para")
    _exigir_string_nao_vazia(payload.get("motivo"), "motivo")

    emissor = payload.get("emissor")
    if not isinstance(emissor, dict):
        raise HandoffPayloadInvalidoError("Campo obrigatório ausente no payload de handoff: 'emissor'.")
    emissor_nome = _exigir_string_nao_vazia(emissor.get("nome"), "emissor.nome")

    contexto = payload.get("contexto")
    if not isinstance(contexto, dict):
        raise HandoffPayloadInvalidoError("Campo obrigatório ausente no payload de handoff: 'contexto'.")
    _exigir_string_nao_vazia(contexto.get("solicitacao_original"), "contexto.solicitacao_original")
    _exigir_string_nao_vazia(contexto.get("trabalho_realizado"), "contexto.trabalho_realizado")

    # Regra 8 — 'para' não pode ser idêntico a 'emissor.nome' (evita loop trivial A→A).
    if para == emissor_nome:
        raise HandoffPayloadInvalidoError(
            f"Handoff inválido: 'para' ({para!r}) não pode ser idêntico a "
            "'emissor.nome' — handoff para o próprio agente emissor não é permitido."
        )

    # Regra 3 — consistência 'roteamento_grafo.next_node' == 'para' (bloco aditivo opcional, v1.1+).
    roteamento_grafo = payload.get("roteamento_grafo")
    if isinstance(roteamento_grafo, dict):
        next_node = roteamento_grafo.get("next_node")
        if next_node is not None and next_node != para:
            raise HandoffPayloadInvalidoError(
                f"Inconsistência estrutural: 'roteamento_grafo.next_node' ({next_node!r}) "
                f"difere de 'para' ({para!r}) — os dois campos devem ser idênticos quando presentes."
            )

    # Regras 4/5 — enums de 'workflow_tracking' (bloco aditivo opcional, v1.2/v1.3).
    workflow_tracking = payload.get("workflow_tracking")
    if isinstance(workflow_tracking, dict):
        workflow_id = workflow_tracking.get("workflow_id")
        if workflow_id is not None and workflow_id not in _WORKFLOW_VALUES:
            raise HandoffPayloadInvalidoError(
                f"'workflow_tracking.workflow_id' inválido: {workflow_id!r}. "
                f"Valores permitidos: {sorted(_WORKFLOW_VALUES)}."
            )

        politica_desvio = workflow_tracking.get("politica_desvio")
        if politica_desvio is not None and politica_desvio not in _POLITICAS_DESVIO_VALIDAS:
            raise HandoffPayloadInvalidoError(
                f"'workflow_tracking.politica_desvio' inválido: {politica_desvio!r}. "
                f"Valores permitidos: {sorted(_POLITICAS_DESVIO_VALIDAS)}."
            )

    # Regra 6 — enum de 'origem_contexto.call_type' (bloco aditivo opcional).
    origem_contexto = payload.get("origem_contexto")
    if isinstance(origem_contexto, dict):
        call_type = origem_contexto.get("call_type")
        if call_type is not None and call_type not in _CALL_TYPES_VALIDOS:
            raise HandoffPayloadInvalidoError(
                f"'origem_contexto.call_type' inválido: {call_type!r}. "
                f"Valores permitidos: {sorted(_CALL_TYPES_VALIDOS)}."
            )

    # Regra 7 — sanitização fail-closed de dados sensíveis, em todo o payload (aninhado).
    _verificar_payload_sem_segredos(payload)

    return HandoffPayload(payload)
