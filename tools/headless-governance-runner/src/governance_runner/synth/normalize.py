"""
normalize — Normalizacao canonica de texto e sanitizacao anti-override (B1-01).

Implementa a normalizacao deterministica e idempotente usada pelas camadas L1 e L2
de deduplicacao (NFKC, casefold, remocao de diacriticos, remocao de pontuacao e
colapso de espacos) e o filtro de seguranca que rejeita prompts sinteticos contendo
diretivas explicitas de override de rota (CA-03).
"""

from __future__ import annotations

import re
import unicodedata

__all__ = [
    "OVERRIDE_DIRECTIVE_REASON",
    "DIRETIVAS_OVERRIDE",
    "normalizar",
    "normalizar_texto",
    "detectar_override",
    "contem_override",
    "sanitizar_prompt",
]

OVERRIDE_DIRECTIVE_REASON = "override_directive_detected"

DIRETIVAS_OVERRIDE: tuple[str, ...] = (
    "Rota:",
    "Delegado:",
    "Agente Ativo:",
    "expected_agent_route",
)

_REGEX_OVERRIDE = re.compile(
    r"(?:\brota\s*:|\bdelegado\s*:|\bagente\s+ativo\s*:|\bexpected_agent_route\b)",
    re.IGNORECASE,
)

_REGEX_NAO_ALFANUM = re.compile(r"[^\w\s]", re.UNICODE)
_REGEX_ESPACOS = re.compile(r"\s+", re.UNICODE)


def normalizar(texto: str) -> str:
    """Normaliza um texto de forma deterministica e idempotente para deduplicacao."""
    if not texto:
        return ""
    etapa_nfkc = unicodedata.normalize("NFKC", texto).casefold()
    sem_acentos = "".join(
        ch
        for ch in unicodedata.normalize("NFD", etapa_nfkc)
        if unicodedata.category(ch) != "Mn"
    )
    recomposto = unicodedata.normalize("NFKC", sem_acentos)
    sem_pontuacao = _REGEX_NAO_ALFANUM.sub(" ", recomposto).replace("_", " ")
    return _REGEX_ESPACOS.sub(" ", sem_pontuacao).strip()


normalizar_texto = normalizar


def detectar_override(texto: str) -> str | None:
    """Detecta diretivas de override de roteamento no texto candidato.

    Rejeita Rota:, Delegado:, Agente Ativo: e expected_agent_route (case-insensitive),
    retornando override_directive_detected.
    """
    if not texto:
        return None
    if _REGEX_OVERRIDE.search(texto) is not None:
        return OVERRIDE_DIRECTIVE_REASON
    return None


def contem_override(texto: str) -> bool:
    """Retorna True se o texto contiver diretiva de override proibida."""
    return detectar_override(texto) is not None


def sanitizar_prompt(texto: str) -> tuple[bool, str | None]:
    """Valida se o prompt sintetico esta livre de diretivas de override."""
    motivo = detectar_override(texto)
    return (motivo is None, motivo)
