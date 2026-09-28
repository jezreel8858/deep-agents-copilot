"""
telemetry.otel — Instrumentação OTel GenAI do runner headless com fail-open estrito.

Contrato (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §5.2 / §8.1 / TC-13):
A telemetria OTel nunca pode abortar a auditoria de governança. Se o collector
OTel estiver indisponível (ConnectionRefusedError, TimeoutError, etc.), o runner
deve degradar suavemente (fail-open), completando a auditoria normalmente e
definindo o trace_id como sentinela TRACE_ID_INDISPONIVEL ("telemetry_unavailable")
ou None.
"""

from __future__ import annotations

import logging
import os
import urllib.error
import urllib.request
import uuid

__all__ = [
    "TRACE_ID_INDISPONIVEL",
    "OTEL_EXPORTER_OTLP_ENDPOINT_ENV",
    "OTEL_COLLECTOR_TIMEOUT_PADRAO",
    "OTelCollectorUnavailableError",
    "verificar_disponibilidade_collector",
    "obter_trace_id_auditoria",
]

logger = logging.getLogger("governance_runner.telemetry.otel")

TRACE_ID_INDISPONIVEL = "telemetry_unavailable"
OTEL_EXPORTER_OTLP_ENDPOINT_ENV = "OTEL_EXPORTER_OTLP_ENDPOINT"
OTEL_COLLECTOR_TIMEOUT_PADRAO = 2.0


class OTelCollectorUnavailableError(Exception):
    """Levantada quando a conexão com o OTel Collector falha."""


def verificar_disponibilidade_collector(
    endpoint: str | None = None,
    timeout: float = OTEL_COLLECTOR_TIMEOUT_PADRAO,
) -> bool:
    """Verifica se o endpoint do OTel Collector está acessível (fail-open se falso)."""
    endpoint = endpoint or os.environ.get(OTEL_EXPORTER_OTLP_ENDPOINT_ENV)
    if not endpoint:
        return True  # Sem endpoint configurado: telemetria em modo local/noop

    try:
        req = urllib.request.Request(endpoint, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        logger.warning("OTel Collector indisponivel em '%s': %s (fail-open ativado)", endpoint, exc)
        return False


def obter_trace_id_auditoria(
    endpoint: str | None = None,
    timeout: float = OTEL_COLLECTOR_TIMEOUT_PADRAO,
    force_probe: bool = False,
) -> str:
    """Gera um trace_id para a auditoria, aplicando fail-open se o collector estiver indisponível.

    Se OTEL_EXPORTER_OTLP_ENDPOINT estiver configurado (ou `endpoint` fornecido)
    e o coletor não responder, retorna TRACE_ID_INDISPONIVEL em vez de crashar.
    Se o coletor estiver acessível (ou nenhum endpoint exigir probe), gera uuid4.hex.
    """
    url = endpoint or os.environ.get(OTEL_EXPORTER_OTLP_ENDPOINT_ENV)
    if url or force_probe:
        if not verificar_disponibilidade_collector(url, timeout=timeout):
            return TRACE_ID_INDISPONIVEL

    return uuid.uuid4().hex
