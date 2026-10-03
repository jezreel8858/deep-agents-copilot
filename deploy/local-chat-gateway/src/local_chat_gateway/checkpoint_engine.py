"""checkpoint_engine — parsing puro da resposta de checkpoint humano (R-027/R-064).

Gramatica (BLUEPRINT_LOCAL_CHAT_GATEWAY.md Secao 5):
    ^\\s*(cp-[0-9a-f]{4}\\s+)?([0-9]+)(\\s*:\\s*(.+))?\\s*$

Invariante 11 (obrigatoria): respostas vagas ("prossiga", "continue", "ok",
"sim", ...) ou fora da gramatica NAO resolvem o checkpoint — a pergunta e
reemitida sem mudanca de estado, a custo zero (nenhuma chamada de
rede/LLM: apenas comparacao lexical local e regex).

Funcao pura, sem I/O — testavel isoladamente.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_CHECKPOINT_PATTERN = re.compile(r"^\s*(cp-[0-9a-f]{4}\s+)?([0-9]+)(\s*:\s*(.+))?\s*$")

# Invariante 11: respostas vagas conhecidas — comparadas apos strip+lower,
# nunca resolvem o checkpoint (custo zero, resposta 100% local).
VAGUE_RESPONSES: frozenset[str] = frozenset(
    {
        "prossiga",
        "prosseguir",
        "continue",
        "continuar",
        "ok",
        "okay",
        "sim",
        "yes",
        "segue",
        "vai",
        "beleza",
        "certo",
    }
)


@dataclass(frozen=True)
class CheckpointResolution:
    """Resultado da tentativa de resolver um checkpoint a partir de uma resposta.

    Attributes:
        resolved: `True` somente quando a resposta casa a gramatica valida
            e (se `checkpoint_id_aberto` for informado) o ID do checkpoint
            bate com o aberto.
        checkpoint_id: ID `cp-xxxx` extraido da resposta, se presente.
        option: Numero da opcao escolhida (grupo 2 da gramatica).
        free_text: Texto livre apos ":" (opcao "0: <texto>"), se presente.
        reason: Motivo de nao-resolucao (`"vague_response"`,
            `"invalid_grammar"`, `"checkpoint_id_mismatch"`) ou `None`
            quando `resolved is True`.
    """

    resolved: bool
    checkpoint_id: str | None = None
    option: int | None = None
    free_text: str | None = None
    reason: str | None = None


def parse_checkpoint_response(
    resposta: str, *, checkpoint_id_aberto: str | None = None
) -> CheckpointResolution:
    """Interpreta a resposta humana a um checkpoint segundo a gramatica R-027/R-064.

    Args:
        resposta: Texto bruto digitado pelo usuario.
        checkpoint_id_aberto: ID do (unico) checkpoint atualmente aberto,
            usado para validar/(des)ambiguar o ID opcional da gramatica.

    Returns:
        CheckpointResolution: `resolved=False` com `reason` preenchido
        sempre que a Invariante 11 se aplica (resposta vaga ou fora da
        gramatica) ou o ID do checkpoint nao corresponder ao aberto.
    """
    normalizado = resposta.strip().lower()
    if normalizado in VAGUE_RESPONSES:
        return CheckpointResolution(resolved=False, reason="vague_response")

    match = _CHECKPOINT_PATTERN.match(resposta)
    if match is None:
        return CheckpointResolution(resolved=False, reason="invalid_grammar")

    checkpoint_id_bruto = match.group(1)
    checkpoint_id = (
        checkpoint_id_bruto.strip() if checkpoint_id_bruto is not None else None
    )
    option = int(match.group(2))
    free_text = match.group(4)

    if (
        checkpoint_id is not None
        and checkpoint_id_aberto is not None
        and checkpoint_id != checkpoint_id_aberto
    ):
        return CheckpointResolution(
            resolved=False,
            checkpoint_id=checkpoint_id,
            option=option,
            free_text=free_text,
            reason="checkpoint_id_mismatch",
        )

    return CheckpointResolution(
        resolved=True,
        checkpoint_id=checkpoint_id or checkpoint_id_aberto,
        option=option,
        free_text=free_text,
        reason=None,
    )
