"""Re-export do módulo de telemetria sob namespace runner."""

from governance_runner.telemetry.otel import (
    OTEL_COLLECTOR_TIMEOUT_PADRAO,
    OTEL_EXPORTER_OTLP_ENDPOINT_ENV,
    TRACE_ID_INDISPONIVEL,
    OTelCollectorUnavailableError,
    obter_trace_id_auditoria,
    verificar_disponibilidade_collector,
)

__all__ = [
    "TRACE_ID_INDISPONIVEL",
    "OTEL_EXPORTER_OTLP_ENDPOINT_ENV",
    "OTEL_COLLECTOR_TIMEOUT_PADRAO",
    "OTelCollectorUnavailableError",
    "verificar_disponibilidade_collector",
    "obter_trace_id_auditoria",
]
