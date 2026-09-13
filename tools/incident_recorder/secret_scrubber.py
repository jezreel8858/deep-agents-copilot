"""
secret_scrubber.py — Sanitizador automático de credenciais, tokens e dados sensíveis.

Garante que senhas, tokens Bearer, chaves privadas e API keys sejam
substituídos por [REDACTED] antes de qualquer gravação local ou envio ao Supabase.
"""
from __future__ import annotations

import re
from typing import Any

# Padrões comuns de segredos e tokens
_SECRET_PATTERNS = [
    # Bearer tokens e JWT
    (re.compile(r"(Bearer\s+)[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*", re.IGNORECASE), r"\1[REDACTED_JWT]"),
    # Chaves de API comuns (OpenAI, GitHub, AWS, Google, etc.)
    (re.compile(r"(sk-[a-zA-Z0-9]{20,})", re.IGNORECASE), "[REDACTED_API_KEY]"),
    (re.compile(r"(ghp_[a-zA-Z0-9]{36,})", re.IGNORECASE), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"(AKIA[0-9A-Z]{16})", re.IGNORECASE), "[REDACTED_AWS_KEY]"),
    (re.compile(r"(AIza[0-9A-Za-z-_]{35})", re.IGNORECASE), "[REDACTED_GOOGLE_KEY]"),
    (re.compile(r"(sbp_[a-zA-Z0-9]{40,})", re.IGNORECASE), "[REDACTED_SUPABASE_KEY]"),
    # Parâmetros sensíveis em URLs ou payloads (password=..., token=..., secret=...)
    (re.compile(r'("(?:password|secret|api_key|apiKey|token|access_token|private_key)"\s*:\s*")([^"]+)(")', re.IGNORECASE), r'\1[REDACTED]\3'),
    (re.compile(r"((?:password|secret|api_key|token|access_token)\s*=\s*)([^\s&]+)", re.IGNORECASE), r"\1[REDACTED]"),
]


def scrub_string(text: str) -> str:
    """Aplica substituição de padrões sensíveis em uma string."""
    if not text:
        return text
    result = text
    for pattern, replacement in _SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def scrub_data(data: Any) -> Any:
    """Sanitiza recursivamente dicionários, listas e strings."""
    if isinstance(data, str):
        return scrub_string(data)
    elif isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            # Se a chave indica dado sensível, mascara direto o valor
            if any(s in k.lower() for s in ("password", "secret", "private_key", "token", "apikey", "api_key")):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = scrub_data(v)
        return sanitized
    elif isinstance(data, list):
        return [scrub_data(item) for item in data]
    return data

