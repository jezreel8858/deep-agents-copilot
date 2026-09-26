"""
Sanitizador de PII e segredos para telemetria de agentes.

Garante que tokens de API, senhas, chaves privadas e dados pessoais
sejam mascarados antes de serem exportados em traces, spans ou generations.
"""

from __future__ import annotations

import re
from typing import Any

# Padrões regulares de segredos e credenciais sensíveis
_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # GitHub Tokens
    (re.compile(r"(?:ghp_|gho_|github_pat_)[A-Za-z0-9_]+"), "***REDACTED_GH***"),
    # Langfuse Keys (pk-lf-... ou sk-lf-...)
    (re.compile(r"(?:sk|pk)-lf-[A-Za-z0-9-_]+"), "***REDACTED_LF***"),
    # General API Keys (OpenAI sk-..., Anthropic, etc.)
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "***REDACTED_KEY***"),
    # Bearer Tokens e JWTs
    (re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE), "Bearer ***REDACTED***"),
    # AWS Access Keys
    (re.compile(r"AKIA[0-9A-Z]{16}"), "***REDACTED_AWS***"),
    # Google API Keys
    (re.compile(r"AIza[0-9A-Za-z\-_]{20,40}"), "***REDACTED_GOOGLE***"),
    # Supabase Keys
    (re.compile(r"sbp_[a-zA-Z0-9]{40,}"), "***REDACTED_SUPABASE***"),
    # E-mails (PII comum)
    (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "***REDACTED_EMAIL***"),
    # CPF (documento brasileiro)
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "***REDACTED_CPF***"),
]

# Chaves de dicionário consideradas intrinsecamente sensíveis
_SENSITIVE_KEY_NAMES: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "token",
    "apikey",
    "api_key",
    "access_token",
    "authorization",
)


def scrub_string(text: str) -> str:
    """Aplica substituição de padrões sensíveis em uma string.

    Args:
        text: Texto bruto contendo potenciais segredos ou dados pessoais.

    Returns:
        String com dados sensíveis substituídos por placeholders.
    """
    if not text:
        return text

    result = text
    for pattern, replacement in _SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def scrub_data(data: Any) -> Any:
    """Sanitiza recursivamente dicionários, listas e strings.

    Args:
        data: Objeto de dados arbitrário (dict, list, str, etc.).

    Returns:
        Objeto com o mesmo formato estrutural, porém com dados sensíveis mascarados.
    """
    if isinstance(data, str):
        return scrub_string(data)

    if isinstance(data, dict):
        sanitized: dict[str, Any] = {}
        for k, v in data.items():
            key_lower = str(k).lower()
            if any(sens in key_lower for sens in _SENSITIVE_KEY_NAMES):
                sanitized[str(k)] = "***REDACTED***"
            else:
                sanitized[str(k)] = scrub_data(v)
        return sanitized

    if isinstance(data, list):
        return [scrub_data(item) for item in data]

    return data
