"""
otel_langfuse — Cliente de tracing unificado para Langfuse e OpenTelemetry GenAI.

Fornece instrumentação de agents, spans, generations e sanitização de PII
em conformidade com OpenTelemetry GenAI Semantic Conventions v1.41+.
"""

from otel_langfuse.client import LangfuseOtelClient, SpanContextManager
from otel_langfuse.config import TraceConfig
from otel_langfuse.exceptions import (
    DomainException,
    IntegrationException,
    TracingException,
    ValidationException,
)
from otel_langfuse.models import (
    GenerationData,
    ScoreData,
    SpanMetadata,
    TokenUsage,
)
from otel_langfuse.sanitizer import scrub_data, scrub_string

__all__ = [
    "LangfuseOtelClient",
    "SpanContextManager",
    "TraceConfig",
    "DomainException",
    "ValidationException",
    "IntegrationException",
    "TracingException",
    "GenerationData",
    "ScoreData",
    "SpanMetadata",
    "TokenUsage",
    "scrub_string",
    "scrub_data",
]
