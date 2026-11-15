"""
normalize — Normalizacao de texto e guarda anti-override para prompts sinteticos (B1 / B2 / §3.4).
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
    "Workflow:",
    "Etapa do Workflow:",
    "expected_agent_route",
)
_REGEX_OVERRIDE = re.compile(
    r"(?:\brota\s*:|\bdelegado\s*:|\bagente\s+ativo\s*:|\bworkflow\s*:|\betapa\s+do\s+workflow\s*:|\bexpected_agent_route\b)",
    re.IGNORECASE,
)
_REGEX_NAO_ALFANUM = re.compile(r"[^\w\s]", re.UNICODE)
_REGEX_ESPACOS = re.compile(r"\s+", re.UNICODE)


def normalizar(texto: str) -> str:
    """Normaliza texto aplicando NFKC, casefold, remocao de acentos e colapso de espacos."""
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
    """Retorna motivo se o texto contiver diretivas de override de rota ou workflow."""
    if not texto:
        return None
    if _REGEX_OVERRIDE.search(texto) is not None:
        return OVERRIDE_DIRECTIVE_REASON
    return None


def contem_override(texto: str) -> bool:
    """Retorna True se o texto contiver diretiva de override."""
    return detectar_override(texto) is not None


def sanitizar_prompt(texto: str) -> tuple[bool, str | None]:
    """Valida se o prompt esta livre de diretivas de override."""
    motivo = detectar_override(texto)
    return (motivo is None, motivo)
