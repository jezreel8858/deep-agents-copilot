"""
Modelos de dados e DTOs para traces, spans e generations.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator
from otel_langfuse.exceptions import ValidationException


class TokenUsage(BaseModel):
    """Métricas de uso de tokens em chamadas LLM."""

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)

    @property
    def total_tokens(self) -> int:
        """Calcula a soma de tokens de entrada e saída."""
        return self.input_tokens + self.output_tokens


class SpanMetadata(BaseModel):
    """Metadados e atributos de um Span."""

    name: str
    span_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    status_code: str = "OK"
    status_description: Optional[str] = None


class GenerationData(BaseModel):
    """Representação de uma geração LLM (Observation Generation)."""

    name: str
    model: str
    provider_name: str = "openai"
    input_data: Any = None
    output_data: Any = None
    usage: Optional[TokenUsage] = None
    cost_usd: Optional[float] = None
    finish_reason: Optional[str] = None
    prompt_name: Optional[str] = None
    prompt_version: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "model")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Garante que strings essenciais não estejam vazias."""
        if not v or not v.strip():
            raise ValidationException("O campo não pode ser vazio.")
        return v.strip()


class ScoreData(BaseModel):
    """Avaliação ou métrica de qualidade associada a um trace ou generation."""

    name: str
    value: Union[float, int, str, bool]
    data_type: Literal["numeric", "categorical", "boolean"] = "numeric"
    comment: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_score_name(cls, v: str) -> str:
        """Valida que o nome do score é válido."""
        if not v or not v.strip():
            raise ValidationException("O nome do score não pode ser vazio.")
        return v.strip()
